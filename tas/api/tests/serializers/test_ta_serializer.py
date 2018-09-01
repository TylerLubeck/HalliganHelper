import mock
import pytest
from django_dynamic_fixture import G

from django.utils.timezone import now
from datetime import timedelta


class TestTASerializerIsMe(object):

    @pytest.mark.django_db
    def test_is_not_me(self):
        from tas.models import Student
        from tas.api.serializers import TASerializer

        student_one = G(Student)
        student_two = G(Student)

        request = mock.Mock()
        request.user = student_one.user

        ta_serializer = TASerializer()
        ta_serializer.context = {'request': request}

        assert not ta_serializer.get_is_me(student_two)

    @pytest.mark.django_db
    def test_is_me(self):
        from tas.models import Student
        from tas.api.serializers import TASerializer

        student_one = G(Student)

        request = mock.Mock()
        request.user = student_one.user

        ta_serializer = TASerializer()
        ta_serializer.context = {'request': request}

        assert ta_serializer.get_is_me(student_one)

    @pytest.mark.django_db
    def test_not_request(self):
        from tas.api.serializers import TASerializer

        ta_serializer = TASerializer()
        ta_serializer.context = {'request': None}

        assert not ta_serializer.get_is_me(mock.Mock())


class TestTASerializerGetOnDuty(object):

    @pytest.mark.django_db
    def test_no_office_hours(self):
        from tas.models import Student
        from tas.api.serializers import TASerializer

        student = G(Student)

        ta_serializer = TASerializer()

        assert not ta_serializer.get_on_duty(student)

    @pytest.mark.django_db
    def test_not_on_duty(self):
        from tas.models import Student, OfficeHour
        from tas.api.serializers import TASerializer

        student = G(Student)
        G(OfficeHour, ta=student, end_time=(now() - timedelta(hours=1)))

        ta_serializer = TASerializer()

        assert not ta_serializer.get_on_duty(student)

    @pytest.mark.django_db
    def test_on_duty(self):
        from tas.models import Student, OfficeHour
        from tas.api.serializers import TASerializer

        student = G(Student)
        G(OfficeHour, ta=student, end_time=(now() + timedelta(hours=1)))

        ta_serializer = TASerializer()

        assert ta_serializer.get_on_duty(student)
