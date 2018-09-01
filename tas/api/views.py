import logging
from datetime import timedelta

from django.contrib.auth import logout
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import (
    viewsets,
    mixins,
    status,
    generics,
    permissions,
)
from rest_framework.exceptions import NotAuthenticated, ParseError
from rest_framework.response import Response
from rest_framework.decorators import list_route
from djoser.views import PasswordResetView as DjoserPasswordResetView

from registration.models import RegistrationProfile

from ws4redis.publisher import RedisPublisher


from ..models import (School, Course, Request,
                      Student, OfficeHour, CustomUser)

from ..utils import publish_message

from .serializers import (
    SchoolSerializer,
    CourseSerializer,
    RequestSerializer,
    OfficeHourSerializer,
    UserSerializer,
    RegistrationSerializer,
    LoginSerializer,
    TASerializer,

)

from .permissions import (
    RequestPermission,
    OwnSchoolPermission,
    OfficeHourPermission
)

logger = logging.getLogger(__name__)


class PasswordResetView(DjoserPasswordResetView):
    subject_template_name = 'registration/password_reset_subject.txt'
    plain_body_template_name = 'registration/password_reset_email.txt'
    html_body_template_name = 'registration/password_reset_email.html'


class CreateModelWithRequestMixin(mixins.CreateModelMixin):

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create_with_request(serializer, request)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create_with_request(self, serializer, request):
        serializer.save()


class SchoolView(generics.ListAPIView):
    """Returns information about the users school.

    Only responds to safe methods (GET, HEAD, OPTIONS)

    Returns information based on who is authenticated, so user A
        can not see the school of user B (unless they have the same school)
    """
    serializer_class = SchoolSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = School.objects.none()

    def get(self, request):
        school = request.user.student.school
        return Response(SchoolSerializer(school).data)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns information about a course or list of courses.

    Only responds to safe methods (GET, HEAD, OPTIONS)

    Based off of a users school, so a user will only be allowed to see
    a course that belongs to their school.
    """
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_queryset(self):
        qs = super(CourseViewSet, self).get_queryset()

        user_school = self.request.user.student.school
        return qs.filter(school=user_school)


class RequestViewSet(CreateModelWithRequestMixin,
                     mixins.UpdateModelMixin,
                     viewsets.ReadOnlyModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    permission_classes = (OwnSchoolPermission, RequestPermission,)

    def get_serializer_context(self):
        context = super(RequestViewSet, self).get_serializer_context()
        context.update({
            'request': self.request
        })
        return context

    def perform_create_with_request(self, serializer, request):
        course = request.data['course']
        requestor = self.request.user.student
        serializer.save(course=course, requestor=requestor)

    def get_queryset(self):
        queryset = super(RequestViewSet, self).get_queryset()
        queryset = queryset.filter(cancelled=False, solved=False)
        queryset.order_by('-when_asked')
        return queryset

    def list(self, request, course_pk=None):
        course = Course.objects.get(pk=course_pk)
        queryset = self.get_queryset().filter(course=course_pk)

        # If there's a TTL, filter by it.
        if course.request_time_to_live > 0:
            when_asked_cutoff = timedelta(hours=course.request_time_to_live)
            queryset = queryset.filter(
                when_asked__gte=(timezone.now() - when_asked_cutoff)
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, course_pk=None):
        help_request = get_object_or_404(self.get_queryset(),
                                         pk=pk,
                                         course=course_pk)

        serializer = self.get_serializer(help_request)
        return Response(serializer.data)

    def create(self, request, course_pk=None):
        course = get_object_or_404(Course, pk=course_pk)
        request.data['course'] = course

        created = super(RequestViewSet, self).create(request, course_pk)

        publish_message('request_created', {
            'course': course.pk,
            'id': created.data['id']
        })

        return created

    def update(self, *args, **kwargs):
        updated = super(RequestViewSet, self).update(*args, **kwargs)

        course_pk = kwargs.get('course_pk')
        try:
            course_pk = int(course_pk)
        except (ValueError, TypeError):
            logger.exception('Could not get course_pk on request update')
            raise ParseError

        packet_type = 'request_updated'
        if updated.data['cancelled'] or updated.data['solved']:
            packet_type = 'request_removed'

        publish_message(packet_type, {
            'course': course_pk,
            'id': updated.data['id'],
        })

        # Commented out to see if the user-specific sockets are the
        # sockets that are blocking

        # If the request was checked out, tell the student
        # solved = updated.data['solved']
        # checked_out = updated.data['checked_out']
        # cancelled = updated.data['cancelled']
        # if checked_out and not (cancelled or solved):
        #     student = Student.objects.get(pk=updated.data['requestor']['id'])
        #     student_username = student.user.email
        #     checked_out_by = self.request.user
        #     publish_message('checked_out', {
        #         'checked_out_by': checked_out_by.get_full_name(),
        #         'headshot': checked_out_by.student.headshot.url,
        #     }, RedisPublisher(facility='ta', users=[student_username]))

        return updated


class OfficeHourViewSet(CreateModelWithRequestMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.ReadOnlyModelViewSet):
    serializer_class = OfficeHourSerializer
    queryset = OfficeHour.objects.all()
    permission_classes = (
        OwnSchoolPermission,
        OfficeHourPermission,
    )

    def get_queryset(self):
        queryset = super(OfficeHourViewSet, self).get_queryset()
        return queryset.filter(end_time__gt=timezone.now())

    def perform_create_with_request(self, serializer, request):
        course = request.data['course']
        ta = request.user.student
        serializer.save(course=course, ta=ta)

    def list(self, request, course_pk=None):
        queryset = self.get_queryset().filter(course=course_pk)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None, course_pk=None):
        office_hour = get_object_or_404(self.get_queryset(),
                                        pk=pk,
                                        course=course_pk)
        serializer = self.get_serializer(office_hour)

        return Response(serializer.data)

    def create(self, request, course_pk=None):
        school = request.user.student.school

        course = get_object_or_404(Course, pk=course_pk, school=school)
        request.data['course'] = course

        created = super(OfficeHourViewSet, self).create(request, course_pk)
        publish_message('on_duty', {
            'course': course_pk,
            'id': created.data['id'],
        })

        return created

    def destroy(self, request, pk=None, course_pk=None, **kwargs):
        office_hour = get_object_or_404(OfficeHour.objects.all(), pk=pk)

        now = timezone.now()
        if office_hour.end_time >= now:
            office_hour.end_time = now
            office_hour.save()

        publish_message('off_duty', {
            'course': course_pk,
            'id': office_hour.pk,
        })

        return Response(status=status.HTTP_204_NO_CONTENT)


class TAViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TASerializer
    queryset = Student.objects.none()
    permission_classes = (OwnSchoolPermission,)

    def list(self, request, course_pk=None):
        queryset = Course.objects.get(pk=course_pk).tas.filter(ta__active=True)
        queryset = queryset.order_by('ta__active',
                                     'user__last_name',
                                     'user__first_name')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, course_pk=None):
        queryset = Course.objects.get(pk=course_pk).tas.filter(ta__active=True)
        ta = get_object_or_404(queryset, pk=pk)

        serializer = self.get_serializer(ta)
        return Response(serializer.data)


class UserViewSet(viewsets.ViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.none()
    SEND_ACTIVATION_EMAIL = getattr(settings, 'SEND_ACTIVATION_EMAIL', True)

    def get_queryset(self):
        return CustomUser.objects.none()

    def get_serializer(self, *args, **kwargs):
        context = {
            'request': self.request
        }

        kwargs['context'] = context

        return UserViewSet.serializer_class(*args, **kwargs)

    def list(self, request):
        user = request.user
        if not user.is_authenticated() or not user.is_active:
            raise NotAuthenticated
        return Response(UserSerializer(user).data)

    def patch(self, request):
        logger.debug('about to patch for user %s', request.user.pk)
        user = CustomUser.objects.get(pk=request.user.pk)

        user.student.blurb = request.data.get('blurb', user.student.blurb)
        serializer = self.get_serializer(user,
                                         data={'blurb': user.student.blurb})
        serializer.is_valid(raise_exception=True)

        user.student.save()
        user.save()
        user.student.refresh_from_db()
        user.refresh_from_db()

        return Response(self.get_serializer(user).data)

    @list_route(methods=['post'])
    def login(self, request):
        logger.debug('about to login')
        serializer = LoginSerializer(data=request.data,
                                     context={'request': request})

        serializer.is_valid(raise_exception=True)

        return Response(self.get_serializer(request.user).data)

    @list_route(methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({}, status=200)

    @list_route(methods=['post'])
    def upload_photo(self, request):
        photo = request.data.get('photo')

        if photo is None:
            raise ParseError

        if not isinstance(photo, UploadedFile):
            logger.warning('Attempt to upload a non-file: %s user:%s',
                           photo, request.user.pk)
            raise ParseError

        request.user.student.headshot = photo
        request.user.student.save()
        return Response(self.get_serializer(request.user).data)

    @list_route(methods=['post'])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = dict(serializer.data)
        password = serializer.data.pop('password')
        del user_data['password_confirm']

        user = CustomUser(**user_data)
        user.set_password(password)
        user.is_active = False
        user.save()

        RegistrationProfile.objects.create_inactive_user(
            new_user=user,
            site=get_current_site(request),
            send_email=self.SEND_ACTIVATION_EMAIL,
            request=request
        )

        return Response({})
