import mock
import pytest
from django_dynamic_fixture import G

from rest_framework import serializers

from django.utils.timezone import now
from datetime import timedelta


class TestOfficeHourSerializerEndTime(object):

    def test_end_time_before_now(self):
        from tas.api.serializers import OfficeHourSerializer
        ohs = OfficeHourSerializer()
        with pytest.raises(serializers.ValidationError):
            ohs.validate_end_time(now() - timedelta(hours=1))

    def test_end_time_after_now(self):
        from tas.api.serializers import OfficeHourSerializer
        ohs = OfficeHourSerializer()
        ohs.validate_end_time(now() + timedelta(hours=1))


class TestOfficeHourSerializerIsMe(object):

    @pytest.mark.django_db
    def test_is_not_me(self):
        from tas.api.serializers import OfficeHourSerializer
        from tas.models import OfficeHour, Student
        student = G(Student)
        student_two = G(Student)
        office_hour = G(OfficeHour, ta=student_two)

        request = mock.Mock()
        request.user = student.user

        ohs = OfficeHourSerializer()
        ohs.context = {'request': request}

        assert not ohs.get_is_me(office_hour)

    @pytest.mark.django_db
    def test_is_me(self):
        from tas.api.serializers import OfficeHourSerializer
        from tas.models import OfficeHour, Student
        student = G(Student)
        office_hour = G(OfficeHour, ta=student)

        request = mock.Mock()
        request.user = student.user

        ohs = OfficeHourSerializer()
        ohs.context = {'request': request}

        assert ohs.get_is_me(office_hour)

    def test_no_request(self):
        from tas.api.serializers import OfficeHourSerializer

        ohs = OfficeHourSerializer()
        ohs.context = {'request': None}

        assert not ohs.get_is_me(mock.Mock())


class TestOfficeHourSerializerValidate(object):

    @pytest.mark.django_db
    def test_already_on_duty(self):
        from tas.api.serializers import OfficeHourSerializer
        from tas.models import OfficeHour, Student
        student = G(Student)
        G(OfficeHour, ta=student, end_time=(now() + timedelta(hours=1)))

        request = mock.Mock()
        request.user = student.user

        ohs = OfficeHourSerializer()
        ohs.context = {'request': request}

        with pytest.raises(serializers.ValidationError):
            ohs.validate({})

    @pytest.mark.django_db
    def test_never_on_duty(self):
        from tas.api.serializers import OfficeHourSerializer
        from tas.models import Student
        student = G(Student)

        request = mock.Mock()
        request.user = student.user

        ohs = OfficeHourSerializer()
        ohs.context = {'request': request}

        ohs.validate({})

    @pytest.mark.django_db
    def test_not_on_duty(self):
        from tas.api.serializers import OfficeHourSerializer
        from tas.models import OfficeHour, Student
        student = G(Student)
        G(OfficeHour, ta=student, end_time=(now() - timedelta(hours=1)))

        request = mock.Mock()
        request.user = student.user

        ohs = OfficeHourSerializer()
        ohs.context = {'request': request}

        ohs.validate({})

    def test_no_request(self):
        from tas.api.serializers import OfficeHourSerializer

        with mock.patch('tas.api.serializers.OfficeHour') as OfficeHour:
            ohs = OfficeHourSerializer()
            ohs.context = {'request': None}

            ohs.validate({})

            assert not OfficeHour.objects.filter.called
