import logging
from datetime import timedelta

from django.utils.timezone import now
from django.contrib.auth import authenticate, login

from rest_framework import serializers, validators

from ..models import (School,
                      Course,
                      CustomUser,
                      SchoolEmailDomain,
                      Student,
                      Request,
                      OfficeHour,
                      TA)

from ..utils import get_administrators_for_school

logger = logging.getLogger(__name__)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, email):
        # TODO: Base this off of the django settings module
        if not CustomUser.objects.filter(email__iexact=email).exists():
            msg = 'There is no account for the email address {}'
            raise serializers.ValidationError(msg.format(email))

        return email

    def validate_password(self, password):
        email = self.initial_data.get('email')

        # If the email isn't valid, we don't want to bother attempting to
        # to validate the password. But we don't want to bubble the
        # ValidationError for the email inside the password validation,
        # so abort password validation if email validation fails.
        try:
            self.validate_email(email)
        except serializers.ValidationError:
            return

        # Get the case-sensitive version of the email that the user used.
        email = CustomUser.objects.get(email__iexact=email).email
        user = authenticate(email=email, password=password)

        if user is None or not user.is_active:
            msg = 'The email/password combo is invalid'
            raise serializers.ValidationError(msg)

        request = self.context.get('request')
        if request:
            login(request, user)

        return password


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[
            validators.UniqueValidator(
                queryset=CustomUser.objects.all(),
                message='An account with this email already exists'
            )
        ]
    )
    password = serializers.CharField(min_length=7, max_length=255)
    password_confirm = serializers.CharField(min_length=7, max_length=255)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)

    def validate_email(self, email):
        domain = email.split('@')[-1]
        if not SchoolEmailDomain.objects.filter(domain=domain).exists():

            msg = 'There is no school associated with \'{}\'. Please use your '
            msg += 'school email address'

            raise serializers.ValidationError(msg.format(domain))

        if CustomUser.objects.filter(email__iexact=email).filter():
            msg = 'An account with this email already exists'
            raise serializers.ValidationError(msg)

        return email

    def validate_password_confirm(self, password_confirm):
        password = self.initial_data.get('password')
        if password_confirm != password:
            raise serializers.ValidationError('Your password does not match')

        return password_confirm


class UserSerializer(serializers.ModelSerializer):
    headshot_url = serializers.ImageField(source='student.headshot',
                                          read_only=True)
    blurb = serializers.CharField(source='student.blurb')
    ta_jobs = serializers.SerializerMethodField()

    def get_ta_jobs(self, user):
        jobs = TA.objects.filter(student=user.student, active=True)
        return jobs.values_list('pk', flat=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'headshot_url',
            'ta_jobs',
            'blurb',
        )

        read_only_fields = (
            'id',
            'first_name',
            'last_name',
            'headshot_url',
            'ta_jobs',
        )


class CourseSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(source='get_identifier')
    active_ta_count = serializers.SerializerMethodField()
    current_request_count = serializers.SerializerMethodField()
    am_a_ta = serializers.SerializerMethodField()

    def get_am_a_ta(self, course):
        request = self.context.get('request', None)
        if request is None:
            return False

        return TA.objects.filter(active=True,
                                 course=course,
                                 student=request.user.student).exists()

    def get_active_ta_count(self, course):
        return OfficeHour.objects.filter(course=course,
                                         end_time__gte=now()).count()

    def get_current_request_count(self, course):
        requests = Request.objects.filter(
            course=course,
            solved=False,
            cancelled=False
        )

        # If there's a TTL, filter by it.
        if course.request_time_to_live > 0:
            when_asked_cutoff = timedelta(hours=course.request_time_to_live)
            requests = requests.filter(
                when_asked__gte=(now() - when_asked_cutoff)
            )

        return requests.count()

    class Meta:
        model = Course
        fields = (
            'id',
            'name',
            'identifier',
            'request_time_to_live',
            'am_a_ta',
            'active_ta_count',
            'current_request_count',
        )


class RequestorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    headshot_url = serializers.ImageField(source='headshot',
                                          read_only=True)

    class Meta:
        model = Student
        fields = (
            'id',
            'headshot_url',
            'first_name',
            'last_name',
        )


class TASerializer(serializers.ModelSerializer):
    headshot_url = serializers.ImageField(source='headshot',
                                          read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    is_me = serializers.SerializerMethodField()

    on_duty = serializers.SerializerMethodField()

    def get_is_me(self, student):
        request = self.context.get('request', None)
        if request is None:
            logger.error('Null context passed to RequestoSerializer')
            return False

        return request.user.pk == student.user.pk

    def get_on_duty(self, student):
        return OfficeHour.objects.filter(
            ta=student,
            end_time__gt=now()
        ).exists()

    class Meta:
        model = Student
        fields = (
            'id',
            'headshot_url',
            'first_name',
            'last_name',
            'is_me',
            'on_duty',
            'blurb',
        )


class OfficeHourSerializer(serializers.ModelSerializer):
    ta = RequestorSerializer(read_only=True)

    is_me = serializers.SerializerMethodField()

    def validate(self, data):
        request = self.context.get('request', None)
        if request is None:
            logger.warning('No request provided to validator')
            return data

        current_hours = OfficeHour.objects.filter(end_time__gte=now(),
                                                  ta=request.user.student)
        if current_hours.exists():
            course = current_hours.first().course.get_identifier()
            msg = "You're already on duty for {}".format(course)
            raise serializers.ValidationError(msg)

        return data

    def validate_end_time(self, end_time):
        if end_time <= now():
            raise serializers.ValidationError('This needs to be in the future')

        return end_time

    def get_is_me(self, officehour):
        request = self.context.get('request', None)
        if request is None:
            logger.warning("No request in context for officehour")
            return False

        return officehour.ta == request.user.student

    class Meta:
        model = OfficeHour
        fields = (
            'id',
            'location',
            'start_time',
            'end_time',
            'ta',
            'is_me',
        )


class RequestSerializer(serializers.ModelSerializer):
    requestor = RequestorSerializer(read_only=True)
    owned_by_me = serializers.SerializerMethodField()
    can_ta_for = serializers.SerializerMethodField()

    def get_owned_by_me(self, help_request):
        web_request = self.context.get('request', None)
        if web_request is None:
            return False

        return web_request.user.student == help_request.requestor

    def get_can_ta_for(self, help_request):
        web_request = self.context.get('request', None)
        if web_request is None:
            return False

        course = help_request.course
        student = web_request.user.student

        return TA.objects.filter(student=student,
                                 course=course,
                                 active=True).exists()

    class Meta:
        model = Request
        fields = ('id', 'question', 'where_located', 'when_asked',
                  'cancelled', 'checked_out', 'solved', 'requestor',
                  'expired', 'owned_by_me', 'can_ta_for',)


class SchoolAdminSerializer(serializers.ModelSerializer):
    headshot_url = serializers.ImageField(source='student.headshot',
                                          read_only=True)
    full_name = serializers.CharField(source='get_full_name',
                                      read_only=True)
    is_head_admin = serializers.SerializerMethodField()

    def get_is_head_admin(self, user):
        return hasattr(user, 'school')

    class Meta:
        model = CustomUser
        fields = ('email', 'headshot_url', 'is_head_admin', 'full_name')


class SchoolSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    administrators = serializers.SerializerMethodField()

    def get_administrators(self, school):
        admins = get_administrators_for_school(school)
        return SchoolAdminSerializer(admins, many=True).data

    class Meta:
        model = School
        fields = ('name', 'administrators', 'courses',)
