from django.utils.timezone import now
from django.utils.html import conditional_escape
from tastypie import fields
from tastypie.http import HttpUnauthorized
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import DjangoAuthorization, ReadOnlyAuthorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL_WITH_RELATIONS
import logging
import datetime
from .authorizations import RequestAuthorization, OfficeHourAuthorization
from .validations import RequestValidation, OfficeHourValidation
from .models import Course, TA, OfficeHour, Request, Student
from .views import QueueNamespace, AnnouncementNamespace
from HalliganAvailability.authentication import OAuth20Authentication
logger = logging.getLogger('api')


class CommonMeta(object):
    authorization = DjangoAuthorization()
#     authentication = MultiAuthentication(OAuth20Authentication(),
#                                          SessionAuthentication())
    authentication = MultiAuthentication(SessionAuthentication(),
                                         OAuth20Authentication())
    limit = 0
    always_return_data = True


class CourseResource(ModelResource):
    class Meta(CommonMeta):
        queryset = Course.objects.all()
        authorization = ReadOnlyAuthorization()
        filtering = {
            'name': ['exact', 'iexact', 'startswith', ],
            'number': ['exact', 'lte', 'lt', 'gte', 'gt', ],
            'department': ['exact', 'iexact', 'startswith', ],
        }
        fields = ['name', 'number', 'department', 'students', 'id']
        allowed_methods = ['get']


class TAResource(ModelResource):
    class Meta(CommonMeta):
        authorization = ReadOnlyAuthorization()
        queryset = TA.objects.active()
        fields = ['headshot', 'active']
        allowed_methods = ['get']

    def get_object_list(self, request):
        if 'get_all' in request.GET:
            return TA.objects.all()
        else:
            return TA.objects.active()

    def dehydrate(self, bundle):
        bundle.data['full_name'] = bundle.obj.user.get_full_name()
        return bundle


class OfficeHourResource(ModelResource):
    ta = fields.ForeignKey(TAResource, 'ta', full=True)
    course = fields.ForeignKey(CourseResource, 'course', full=False)

    class Meta(CommonMeta):
        queryset = OfficeHour.objects.all()
        authorization = OfficeHourAuthorization()
        allowed_list_methods = ['get', 'post']
        allowed_detail_methods = ['get', 'patch']
        validation = OfficeHourValidation()
        fields = ['id', 'start_time', 'end_time', 'location',
                  'ta']

        filtering = {
            'course': ALL_WITH_RELATIONS
        }

    def get_object_list(self, request):
        query_set = super(OfficeHourResource, self).get_object_list(request)
        return query_set.filter(end_time__gte=now())

    def dehydrate(self, bundle):
        bundle.data['location'] = conditional_escape(bundle.data['location'])
        bundle.data['is_me'] = bundle.request.user.pk == bundle.obj.ta.user.pk
        return bundle

    def alter_list_data_to_serialize(self, request, data):
        try:
            data['meta']['is_ta'] = request.user.ta.active
        except TA.DoesNotExist:
            data['meta']['is_ta'] = False

        return data

    def obj_create(self, bundle, **kwargs):
        kwargs['ta'] = bundle.request.user.ta
        kwargs['start_time'] = now()
        kwargs['end_time'] = bundle.data['end_time'].replace('T', ' ')

        return_val = super(OfficeHourResource, self).obj_create(bundle, **kwargs)
        QueueNamespace.notify_office_hour(bundle.obj.pk,
                                          bundle.obj.course.number,
                                          'office_hour_create')
        return return_val

    def obj_update(self, bundle, **kwargs):
        return_val = super(OfficeHourResource, self).obj_create(bundle, **kwargs)
        QueueNamespace.notify_office_hour(bundle.obj.pk,
                                          bundle.obj.course.number,
                                          'office_hour_update')
        return return_val


class RequestResource(ModelResource):
    course = fields.ForeignKey(CourseResource, 'course', full=False)

    class Meta(CommonMeta):
        queryset = Request.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'patch']
        authorization = RequestAuthorization()
        validation = RequestValidation()

        fields = ['when_asked', 'first_name', 'last_name', 'course',
                  'where_located', 'question', 'checked_out', 'id',
                  'solved', 'cancelled']
        filtering = {
            'course': ALL_WITH_RELATIONS
        }

    def get_object_list(self, request):
        query_set = super(RequestResource, self).get_object_list(request)
        five_hours = datetime.timedelta(hours=5)
        return query_set.filter(when_asked__gte=now() - five_hours,
                                cancelled=False,
                                solved=False)

    def _can_student_update(self, user, new_keys, item_id):
        student_allowed_updates = set(['where_located',
                                       'question',
                                       'cancelled'])
        item_to_update = Request.objects.get(pk=item_id)

        is_owner = item_to_update.student.user.pk == user.pk

        changes_allowed = new_keys.issubset(student_allowed_updates)

        if (not is_owner) or (is_owner and not changes_allowed):
            return False

        return True

    def _can_ta_update(self, user, new_keys):
        ta_allowed_updates = set(['solved', 'checked_out'])

        try:
            is_ta = user.ta.active
        except TA.DoesNotExist:
            is_ta = False

        changes_allowed = new_keys.issubset(ta_allowed_updates)
        if (not is_ta) or (is_ta and not changes_allowed):
            return False
        return True

    def obj_update(self, bundle, **kwargs):
        request = bundle.request
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))
        new_keys = set(data.keys())
        ta_update = self._can_ta_update(request.user, new_keys)

        if ta_update and 'solved' in new_keys and bundle.obj.when_solved is None:
            bundle.obj.when_solved = now()
            bundle.obj.who_solved = request.user.ta

        return_val = super(RequestResource, self).obj_update(bundle, **kwargs)

        websocket_data = {
            'type': 'request_update',
            'id': bundle.obj.pk,
            'course_id': bundle.obj.course.pk,
            'remove': bundle.obj.cancelled or bundle.obj.solved
        }
        publish_ta_message(websocket_data)

        return return_val

    def obj_create(self, bundle, **kwargs):
        student = Student.objects.get(user__pk=bundle.request.user.pk)
        kwargs['student'] = student
        kwargs['when_asked'] = now()

        return_val = super(RequestResource, self).obj_create(bundle, **kwargs)
        QueueNamespace.notify_request(bundle.obj.pk,
                                      bundle.obj.course.number,
                                      'request_create')
        AnnouncementNamespace.notify_ta(bundle.request.user.get_full_name(),
                                        bundle.obj.course.number)

        return return_val

    def patch_detail(self, request, **kwargs):
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))
        new_keys = set(data.keys())

        student_update = self._can_student_update(request.user, new_keys,
                                                  kwargs['pk'])
        ta_update = self._can_ta_update(request.user, new_keys)

        if (not student_update) and (not ta_update):
            return HttpUnauthorized("You are not authorized")
        return super(RequestResource, self).patch_detail(request, **kwargs)

    def dehydrate(self, bundle):
        user = bundle.request.user

        # Html escape vulnerable properties
        bundle.data['where_located'] = conditional_escape(bundle.data['where_located'])
        bundle.data['question'] = conditional_escape(bundle.data['question'])

        try:
            bundle.data['allow_resolve'] = user.ta.active
        except TA.DoesNotExist:
            bundle.data['allow_resolve'] = False

        if bundle.obj.student.user.pk == user.pk:
            bundle.data['allow_edit'] = True
        else:
            bundle.data['allow_edit'] = False

        bundle.data['first_name'] = bundle.obj.student.user.first_name
        bundle.data['last_name'] = bundle.obj.student.user.last_name
        return bundle
