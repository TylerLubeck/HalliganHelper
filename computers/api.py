from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from computers.models import RoomInfo, CourseUsageInfo
from computers.models import Lab, Computer
from HalliganAvailability.authentication import OAuth20Authentication
from django.utils.timezone import now
from .authorizations import AdminWriteAuthorization


class CommonMeta:
    authorization = DjangoAuthorization()
    authentication = MultiAuthentication(OAuth20Authentication(),
                                         SessionAuthentication())
    limit = 0


class ComputerResource(ModelResource):
    class Meta(CommonMeta):
        authorization = AdminWriteAuthorization()
        queryset = Computer.objects.all()
        limit = 100
        filtering = {
            'number': ['exact', ],
            'room_number': ['exact', ],
            'status': ['exact', 'iexact', ],
            'used_for': ['exact', 'iexact'],
        }
        resource_name = 'computer'
        fields = ['number', 'room_number', 'status', 'used_for',
                  'last_update']
        allowed_methods = ['get', 'post', 'put']

    def obj_create(self, bundle, **kwargs):
        bundle.data['last_update'] = now()
        return super(ComputerResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, **kwargs):
        bundle.data['last_update'] = now()
        return super(ComputerResource, self).obj_update(bundle, **kwargs)


class RoomInfoResource(ModelResource):
    cuis = fields.ToManyField(
        'computers.api.CourseUsageInfoResource',
        'cuis', full=True
        )

    class Meta(CommonMeta):
        queryset = RoomInfo.objects.all().order_by('-last_updated')
        filtering = {
            'lab': ['exact', ],
        }
        resource_name = 'roominfo'
        fields = ['lab', 'num_reporting', 'num_available', 'num_unavailable',
                  'num_error', 'last_updated']
        allowed_methods = ['get']
        limit = 100
        ordering = ['last_updated']


class CourseUsageInfoResource(ModelResource):
    room = fields.ToOneField(RoomInfoResource, 'room')

    class Meta(CommonMeta):
        queryset = CourseUsageInfo.objects.all()
        allowed_methods = ['get']


class LabResource(ModelResource):

    day_of_week_str = fields.CharField(attribute='day_of_week_name')
    in_session = fields.BooleanField(attribute='is_lab_in_session')
    coming_up = fields.BooleanField(attribute='is_lab_coming_up')

    class Meta(CommonMeta):
        queryset = Lab.objects.all().order_by('day_of_week', 'start_time')
        allowed_methods = ['get']
        filtering = {
            'room_number': ['exact', ],
            'course_name': ['exact', ],
            'start_date': ['lt', 'lte', 'gt', 'gte', ],
            'end_date': ['lt', 'lte', 'gt', 'gte', ],
            'start_time': ['lt', 'lte', 'gt', 'gte', ],
            'end_time': ['lt', 'lte', 'gt', 'gte', ],
            # 'in_session': ['exact', ],
            # 'coming_up': ['exact', ],
        }

        resource_name = 'lab'
        fields = ['course_name', 'room_number', 'start_time', 'end_time',
                  'start_date', 'end_date', 'day_of_week', 'is_lab_in_session',
                  'id']
        allowed_methods = ['get']
