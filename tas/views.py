import logging
import requests
import json

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.shortcuts import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from registration.backends.default.views import RegistrationView
from registration.signals import user_registered, user_activated
from socketio import socketio_manage
from socketio.namespace import BaseNamespace

from .forms import TAPhotoChangeForm, ForgotUsernameForm
from .models import Student, Request, TA, Course, OfficeHour
from .custom_user_forms import EmailUserCreationForm, EmailAuthenticationForm


logger = logging.getLogger(__name__)
socket_logger = logging.getLogger('sockets')


def notify(user, courses, adding_ta=True):
    subject = 'TA Activation'
    from_email = 'halliganhelper@tylerlubeck.com'
    to_email = user.email
    if adding_ta:
        plaintext = get_template('tas/ta_activation.txt')
        htmly = get_template('tas/ta_activation.html')
    else:
        plaintext = get_template('tas/remove_ta.txt')
        htmly = get_template('tas/remove_ta.html')

    d = Context({'user': user, 'courses': courses})
    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(subject, text_content,
                                 from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def check_ta(user):
    # Because apparently having an '@' in the email gives a 403 back from Tufts
    email = user.email.replace('@', ':')
    url = "http://www.cs.tufts.edu/~molay/compta/isata.cgi/{0}"
    r = requests.get(url.format(email))
    is_ta = r.text.strip() != 'NONE'
    if is_ta:
        course_nums = r.text.strip().split(' ')
        courses = Course.objects.filter(number__in=course_nums)

        logger.debug("{0} has been added as a ta".format(user))
        ta, created = TA.objects.get_or_create(user=user)
        ta.active = True
        ta.course = courses
        ta.save()
        notify(user, courses, adding_ta=True)
    else:
        if TA.objects.filter(user__email=email).exists():
            ta = TA.objects.get(user__email=email)
            ta.active = False
            ta.courses = []
            ta.save()
            notify(user, None, adding_ta=False)


def user_confirmed(sender, user, request, **kwargs):
    check_ta(user)
    logger.debug("User {0} confirmed".format(user))


def user_created(sender, user, request, **kwargs):
    form = EmailUserCreationForm(request.POST)
    stu, created = Student.objects.get_or_create(user=user)
    stu.save()
    user.first_name = form.data['first_name']
    user.last_name = form.data['last_name']
    user.save()
    logger.debug("User {0} created".format(user))

user_registered.connect(user_created)
user_activated.connect(user_confirmed)


def ta_test(user):
    if user.is_authenticated():
        try:
            return user.ta.active
        except TA.DoesNotExist:
            return False
    else:
        return False


class TuftsRegistrationView(RegistrationView):
    form_class = EmailUserCreationForm


def send_forgotten_username_email(user):
    subject = 'Forgotten HalliganHelper Username'
    from_email = 'halliganhelper@tylerlubeck.com'
    to_email = user.email
    plaintext = get_template('registration/forgotten_username_email.txt')
    htmly = get_template('registration/forgotten_username_email.html')

    d = Context({'user': user})
    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(subject, text_content,
                                 from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def forgot_username(request):
    if request.method == 'POST':
        form = ForgotUsernameForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_forgotten_username_email(user)
            except User.DoesNotExist:
                # This means that the email does not exist
                pass
            return HttpResponseRedirect(reverse('sent_username'))
    else:
        form = ForgotUsernameForm()

    return render(request,
                  'registration/forgot_username_form.html',
                  {'form': form})


def sent_username(request):
    return render(request,
                  'registration/forgot_username_complete.html',
                  {})


def is_ta(user):
    try:
        return user.ta.active
    except TA.DoesNotExist:
        return False


def login_or_register(request):
    if request.method == 'POST':
        register_form = EmailUserCreationForm(request.POST)
        login_form = EmailAuthenticationForm(request.POST)
    else:
        register_form = EmailUserCreationForm()
        login_form = EmailAuthenticationForm()
    template_vars = {
        'register': register_form,
        'login': login_form
    }
    return render(request,
                  'tas/login_or_register.html',
                  template_vars)


@login_required()
@user_passes_test(is_ta)
def update_photo(request):
    if request.method == 'POST':
        image_form = TAPhotoChangeForm(request.POST, request.FILES)
        if image_form.is_valid():
            ta = TA.objects.get(pk=request.user.ta.pk)
            if ta.has_updated_headshot:
                ta.headshot.delete()
            else:
                ta.has_updated_headshot = True
            ta.headshot = image_form.cleaned_data['image']
            ta.save()
            return HttpResponseRedirect(reverse('ModularHomePage'))
    else:
        image_form = TAPhotoChangeForm()

    template_params = {'form': image_form}
    return render(request,
                  'tas/update_photo.html',
                  template_params)

############################################################################
#             Socketio Stuff
############################################################################


class QueueNamespace(BaseNamespace):
    _connections = {}

    def recv_connect(self, *args, **kwargs):
        self._connections[id(self)] = {
            'socket': self,
            'user': self.request.user,
            'request': self.request
        }
        return super(QueueNamespace, self).recv_connect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        del self._connections[id(self)]
        socket_logger.debug("Deleting socket with ID {}".format(id(self)))
        super(QueueNamespace, self).disconnect(*args, **kwargs)

    @staticmethod
    def notify_request(request_id, course_number, change_type):
        obj = Request.objects.get(pk=request_id)
        message = {
            'type': change_type,
            'course': course_number,
            'id': request_id,
            'remove': obj.cancelled or obj.solved
        }

        for _, connection in QueueNamespace._connections.items():
            connection['socket'].send(message, True)

    @staticmethod
    def notify_office_hour(office_hour_id, course_number, change_type):
        from .api import OfficeHourResource

        resource = OfficeHourResource()

        message = {
            'type': change_type,
            'course': course_number
        }

        office_hour = OfficeHour.objects.get(pk=office_hour_id)

        QueueNamespace.send_message(resource, office_hour, message)

    @staticmethod
    def send_message(br, item, message):
        for _, connection in QueueNamespace._connections.items():
            resource = br.build_bundle(obj=item, request=connection['request'])
            dehydrated_data = br.full_dehydrate(resource)
            serialized_data = br.serialize(None,
                                           dehydrated_data,
                                           'application/json')
            message['data'] = json.loads(serialized_data)
            connection['socket'].send(message, True)


class AnnouncementNamespace(BaseNamespace):

    _connections = {}

    def recv_connect(self, *args, **kwargs):
        self._connections[id(self)] = {
            'socket': self,
            'user': self.request.user,
        }
        return super(AnnouncementNamespace, self).recv_connect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        del self._connections[id(self)]
        super(AnnouncementNamespace, self).disconnect(*args, **kwargs)

    @staticmethod
    def send_request_update(course_num, json=True):
        num_requests = Request.objects.still_open()
        num_requests = num_requests.filter(course__number=course_num).count()
        msg = {
            'type': 'request_update',
            'course_number': course_num,
            'num_requests': num_requests
        }
        for _, connection in AnnouncementNamespace._connections.items():
            connection['socket'].send(msg, json)

    @staticmethod
    def cancel_office_hours(hour_id, class_number, json_parse=True):
        msg = {
            'type': 'cancel_hours',
            'course_number': class_number,
            'office_hour_id': hour_id
        }
        for _, connection in AnnouncementNamespace._connections.items():
            connection['socket'].send(msg, json_parse)

    @staticmethod
    def notify_ta(user_name, course_number, json_parse=True):
        # Hot fix for ta objects not existing on the socket. Weird but oh well.
        # This code will be removed with the redis update anyway.
        pass
        # msg = {
        #     'type': 'notifyta',
        #     'name': user_name
        # }
        #
        # for _, connection in AnnouncementNamespace._connections.items():
        #     # If the connectoin isn't a ta, then bail out
        #     try:
        #         ta = connection['user'].ta
        #     except TA.DoesNotExist:
        #         continue

        #     course_office_hours = OfficeHour.objects.on_duty_for_course(
        #         course_number)

        #     active_for_course = ta.course.filter(number=course_number).exists()
        #     on_duty = course_office_hours.filter(ta__pk=ta.pk).exists()
        #     if ta.active and active_for_course and on_duty:
        #         connection['socket'].send(msg, json_parse)

    @staticmethod
    def notify_user(which_user, ta_name, json_parse=True):
        msg = {
            'type': 'notifystudent',
            'name': ta_name
        }

        logger.debug("NOTIFY USER")
        for _, connection in AnnouncementNamespace._connections.items():
            logger.debug(
                "Looking for user {} with user {}".format(
                    connection['user'].pk,
                    which_user))
            if connection['user'].pk == which_user:
                logger.debug("SENDING NOTIFICATION")
                connection['socket'].send(msg, json_parse)


def socketio(request):
    try:
        socketio_manage(request.environ, {
            '/taqueue': QueueNamespace,
            '/announcements': AnnouncementNamespace
        }, request=request)
    except:
        logger.error("Exception while handling sockets")

    return HttpResponse()
