import mock
import pytest
from django_dynamic_fixture import G


class TestRequestSerializerOwnedByMe(object):

    @pytest.mark.django_db
    def test_not_owned_by_me(self):
        from tas.api.serializers import RequestSerializer
        from tas.models import Student, Request

        student = G(Student)
        other_student = G(Student)
        help_request = G(Request, requestor=other_student)

        web_request = mock.Mock()
        web_request.user = student.user

        rs = RequestSerializer()
        rs.context = {'request': web_request}

        assert not rs.get_owned_by_me(help_request)

    @pytest.mark.django_db
    def test_owned_by_me(self):
        from tas.api.serializers import RequestSerializer
        from tas.models import Student, Request

        student = G(Student)
        help_request = G(Request, requestor=student)

        web_request = mock.Mock()
        web_request.user = student.user

        rs = RequestSerializer()
        rs.context = {'request': web_request}

        assert rs.get_owned_by_me(help_request)

    def test_owned_by_me_no_request(self):
        from tas.api.serializers import RequestSerializer

        rs = RequestSerializer()
        rs.context = {'request': None}

        assert not rs.get_owned_by_me(mock.Mock())


class TestRequestSerializerCanTAFor(object):

    @pytest.mark.django_db
    def test_can_not_ta_for(self):
        from tas.api.serializers import RequestSerializer
        from tas.models import Student, Request, TA, Course

        student = G(Student)
        other_student = G(Student, school=student.school)
        course = G(Course, school=student.school)
        other_course = G(Course, school=student.school)
        help_request = G(Request, requestor=other_student, course=other_course)
        G(TA, student=student, course=course)

        web_request = mock.Mock()
        web_request.user = student.user

        rs = RequestSerializer()
        rs.context = {'request': web_request}

        assert not rs.get_can_ta_for(help_request)

    @pytest.mark.django_db
    def test_can_ta_for(self):
        from tas.api.serializers import RequestSerializer
        from tas.models import Student, Request, TA, Course

        student = G(Student)
        other_student = G(Student, school=student.school)
        course = G(Course, school=student.school)
        help_request = G(Request, requestor=other_student, course=course)
        G(TA, student=student, course=course)

        web_request = mock.Mock()
        web_request.user = student.user

        rs = RequestSerializer()
        rs.context = {'request': web_request}

        assert rs.get_can_ta_for(help_request)

    def test_can_ta_for_no_request(self):
        from tas.api.serializers import RequestSerializer

        rs = RequestSerializer()
        rs.context = {'request': None}

        assert not rs.get_can_ta_for(mock.Mock())
