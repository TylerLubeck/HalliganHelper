import mock
import pytest
from django_dynamic_fixture import G
from django.utils.timezone import now
from datetime import timedelta


class TestCourseSerializerAmATA(object):

    @pytest.mark.django_db
    def test_is_a_ta(self):
        from tas.models import Student, Course, TA
        from tas.api.serializers import CourseSerializer

        student = G(Student)
        course = G(Course, school=student.school)
        G(TA, student=student, course=course, active=True)

        request = mock.Mock()
        request.user = student.user

        cs = CourseSerializer()
        cs.context = {'request': request}

        assert cs.get_am_a_ta(course)

    @pytest.mark.django_db
    def test_is_a_ta_no_request_object(self):
        from tas.models import Student, Course, TA
        from tas.api.serializers import CourseSerializer

        student = G(Student)
        course = G(Course, school=student.school)
        G(TA, student=student, course=course, active=True)

        cs = CourseSerializer()
        cs.context = {'request': None}

        assert not cs.get_am_a_ta(course)

    @pytest.mark.django_db
    def test_is_not_a_ta(self):
        from tas.models import Student, Course
        from tas.api.serializers import CourseSerializer

        student = G(Student)
        course = G(Course, school=student.school)

        request = mock.Mock()
        request.user = student.user

        cs = CourseSerializer()
        cs.context = {'request': request}

        assert not cs.get_am_a_ta(course)

    @pytest.mark.django_db
    def test_is_an_inactive_ta(self):
        from tas.models import Student, Course, TA
        from tas.api.serializers import CourseSerializer

        student = G(Student)
        course = G(Course, school=student.school)
        G(TA, student=student, course=course, active=False)

        request = mock.Mock()
        request.user = student.user

        cs = CourseSerializer()
        cs.context = {'request': request}

        assert not cs.get_am_a_ta(course)


class TestCourseSerializerActiveTACount(object):

    @pytest.mark.django_db
    def test_no_office_hours(self):
        from tas.models import Course
        from tas.api.serializers import CourseSerializer

        course = G(Course)

        cs = CourseSerializer()

        assert cs.get_active_ta_count(course) == 0

    @pytest.mark.django_db
    def test_no_office_hours_for_course(self):
        from tas.models import Course, OfficeHour
        from tas.api.serializers import CourseSerializer

        course = G(Course)
        other_course = G(Course, school=course.school)

        G(
            OfficeHour,
            course=other_course,
            end_time=(now() + timedelta(hours=1))
        )

        cs = CourseSerializer()

        assert cs.get_active_ta_count(course) == 0

    @pytest.mark.django_db
    def test_no_current_office_hours_for_course(self):
        from tas.models import Course, OfficeHour
        from tas.api.serializers import CourseSerializer

        course = G(Course)

        G(
            OfficeHour,
            course=course,
            end_time=(now() - timedelta(hours=1))
        )

        cs = CourseSerializer()

        assert cs.get_active_ta_count(course) == 0

    @pytest.mark.django_db
    def test_office_hours_for_course(self):
        from tas.models import Course, OfficeHour
        from tas.api.serializers import CourseSerializer

        course = G(Course)

        G(
            OfficeHour,
            course=course,
            end_time=(now() + timedelta(hours=1))
        )

        cs = CourseSerializer()

        assert cs.get_active_ta_count(course) == 1


class TestCourseSerializerCurrentRequestCount(object):

    @pytest.mark.django_db
    def test_all_expired_requests(self):
        from tas.models import Course, Request
        from tas.api.serializers import CourseSerializer

        course = G(Course, request_time_to_live=1)
        G(
            Request,
            course=course,
            when_asked=(now() - timedelta(hours=2))
        )

        cs = CourseSerializer()

        assert cs.get_current_request_count(course) == 0

    @pytest.mark.django_db
    def test_all_solved_expired_requests(self):
        from tas.models import Course, Request
        from tas.api.serializers import CourseSerializer

        course = G(Course, request_time_to_live=1)
        G(
            Request,
            course=course,
            solved=True
        )

        cs = CourseSerializer()

        assert cs.get_current_request_count(course) == 0

    @pytest.mark.django_db
    def test_all_cancelled_expired_requests(self):
        from tas.models import Course, Request
        from tas.api.serializers import CourseSerializer

        course = G(Course, request_time_to_live=1)
        G(
            Request,
            course=course,
            cancelled=True
        )

        cs = CourseSerializer()

        assert cs.get_current_request_count(course) == 0

    @pytest.mark.django_db
    def test_requests_for_another_course(self):
        from tas.models import Course, Request
        from tas.api.serializers import CourseSerializer

        course = G(Course, request_time_to_live=1)
        other_course = G(Course, request_time_to_live=1)
        G(
            Request,
            course=other_course
        )

        cs = CourseSerializer()

        assert cs.get_current_request_count(course) == 0

    @pytest.mark.django_db
    def test_has_requests(self):
        from tas.models import Course, Request
        from tas.api.serializers import CourseSerializer

        course = G(Course, request_time_to_live=1)
        G(
            Request,
            course=course
        )

        cs = CourseSerializer()

        assert cs.get_current_request_count(course) == 1

    @pytest.mark.django_db
    def test_no_time_to_live(self):
        from tas.models import Course, Request
        from tas.api.serializers import CourseSerializer

        course = G(Course, request_time_to_live=0)
        G(
            Request,
            course=course,
            when_asked=(now() - timedelta(days=1))
        )

        cs = CourseSerializer()

        assert cs.get_current_request_count(course) == 1
