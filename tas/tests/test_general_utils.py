import json

import mock
import pytest
import requests_mock
from django_dynamic_fixture import G


class TestInvalidCourseStringError(object):

    def test_string(self):
        from tas.utils import InvalidCourseStringError
        icse = InvalidCourseStringError('course')
        msg = 'Course Strings must contain a number. You gave course'
        assert str(icse) == msg

    def test_is_value_error(self):
        from tas.utils import InvalidCourseStringError
        icse = InvalidCourseStringError('course')
        assert isinstance(icse, ValueError)


class TestNotify(object):

    @pytest.mark.django_db
    def test_no_courses(self):
        from tas.utils import notify
        from tas.models import Course, CustomUser
        user = G(CustomUser)

        with mock.patch('tas.utils.get_template') as get_template:
            notify(user, Course.objects.none())

            calls = [
                mock.call('tas/email/remove_ta.txt'),
                mock.call('tas/email/remove_ta.html'),
            ]
            assert get_template.call_count == len(calls)
            get_template.assert_has_calls(calls)

    @pytest.mark.django_db
    def test_with_courses(self):
        from tas.utils import notify
        from tas.models import Course, CustomUser
        user = G(CustomUser)

        with mock.patch('tas.utils.get_template') as get_template:
            G(Course)  # make a course
            notify(user, Course.objects.all())

            calls = [
                mock.call('tas/email/ta_activation.txt'),
                mock.call('tas/email/ta_activation.html'),
            ]
            assert get_template.call_count == len(calls)
            get_template.assert_has_calls(calls)


# Mocking the notify function so we don't send emails wile testing
@mock.patch('tas.utils.notify', lambda x, y: None)
class TestConfirmATA(object):
    pass


# Mocking the notify function so we don't send emails wile testing
@mock.patch('tas.utils.notify', lambda x, y: None)
@pytest.mark.django_db
class TestCheckTA(object):

    def test_http_exception(self):
        from tas.utils import check_ta
        user = mock.Mock()
        user.email = 'test_email@test.com'

        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=404)
            assert not check_ta(user)

    @pytest.mark.django_db
    @mock.patch('tas.utils._get_ta_courses')
    def test_no_longer_a_ta(self, get_ta_courses):
        from tas.utils import check_ta
        from tas.models import Course, Student, TA
        student = G(Student)
        course = G(Course, school=student.school)
        G(TA, student=student, course=course, active=True)
        get_ta_courses.return_value = Course.objects.none()

        ta_jobs = TA.objects.filter(student=student, active=True)
        assert not check_ta(student.user)
        assert not ta_jobs.exists()

    @pytest.mark.django_db
    @mock.patch('tas.utils.notify')
    @mock.patch('tas.utils._get_ta_courses')
    def test_first_time_ta(self, get_ta_courses, notify):
        from tas.utils import check_ta
        from tas.models import Course, Student, TA

        student = G(Student)
        G(Course, school=student.school)
        get_ta_courses.return_value = Course.objects.all()

        assert not TA.objects.filter(student=student, active=True)
        assert check_ta(student.user)
        assert TA.objects.filter(student=student, active=True)
        assert notify.called_once

    @pytest.mark.django_db
    @mock.patch('tas.utils.notify')
    @mock.patch('tas.utils._get_ta_courses')
    def test_new_courses(self, get_ta_courses, notify):
        from tas.utils import check_ta
        from tas.models import Course, Student, TA

        student = G(Student)
        old_course = G(Course, school=student.school)

        G(Course, school=student.school)  # Make a new course to be assigned
        G(TA, student=student, course=old_course, active=True)
        get_ta_courses.return_value = Course.objects.all()

        assert TA.objects.filter(student=student, active=True).count() == 1
        assert check_ta(student.user)
        assert TA.objects.filter(student=student, active=True).count() == 2
        assert notify.called_once

    @pytest.mark.django_db
    @mock.patch('tas.utils.notify')
    @mock.patch('tas.utils._get_ta_courses')
    def test_courses_changed(self, get_ta_courses, notify):
        from tas.utils import check_ta
        from tas.models import Course, Student, TA

        student = G(Student)
        old_course = G(Course, school=student.school)

        new_course = G(Course, school=student.school)
        G(TA, student=student, course=old_course, active=True)
        get_ta_courses.return_value = Course.objects.filter(pk=new_course.pk)

        assert TA.objects.filter(student=student, active=True).count() == 1
        assert check_ta(student.user)
        assert TA.objects.filter(student=student, active=True).count() == 1
        assert TA.objects.filter(student=student, active=False).count() == 1
        assert notify.called_once

    @pytest.mark.django_db
    @mock.patch('tas.utils.notify')
    @mock.patch('tas.utils._get_ta_courses')
    def test_has_same_courses(self, get_ta_courses, notify):
        from tas.utils import check_ta
        from tas.models import Course, Student, TA

        student = G(Student)
        old_course = G(Course, school=student.school)
        G(TA, student=student, course=old_course, active=True)
        get_ta_courses.return_value = Course.objects.filter(pk=old_course.pk)

        not_my_course = G(Course, school=student.school)

        assert TA.objects.filter(student=student, active=True).count() == 1
        assert check_ta(student.user)
        assert TA.objects.filter(student=student, active=True).count() == 1
        assert not TA.objects.filter(
            student=student,
            course__pk=not_my_course.pk
        ).exists()
        assert not notify.called


class TestSchoolAdministratorTools(object):
    @pytest.mark.django_db
    def test_get_administrators_for_school_no_extra_admins(self):
        from tas.utils import get_administrators_for_school
        from tas.models import School

        school = G(School)

        assert get_administrators_for_school(school).count() == 1

    @pytest.mark.django_db
    def test_get_administrators_for_school_with_extra_admins(self):
        from django.contrib.auth.models import Group
        from tas.utils import (
            get_administrators_for_school,
            get_school_admin_group_name
        )
        from tas.models import School, Student

        school = G(School)
        student = G(Student, school=school)

        group_name = get_school_admin_group_name(school.name)
        group = Group.objects.get(name=group_name)
        student.user.groups.add(group)

        assert get_administrators_for_school(school).count() == 2

    def test_school_admin_group_name(self):
        from tas.utils import get_school_admin_group_name as gsagn
        assert gsagn('Test School') == 'Test School Admins'


class TestSplitCourseString(object):

    def test_all_numbers(self):
        from tas.utils import _split_course_string

        num, postfix = _split_course_string('12345')
        assert num == '12345'
        assert postfix == ''

    def test_all_characters(self):
        from tas.utils import _split_course_string
        from tas.utils import InvalidCourseStringError

        with pytest.raises(InvalidCourseStringError):
            num, postfix = _split_course_string('abcdefgh')

    def test_mix_characters_numbers(self):
        from tas.utils import _split_course_string

        num, postfix = _split_course_string('11A7B12')
        assert num == '11'
        assert postfix == 'A7B12'

    def test_valid_course_string(self):
        from tas.utils import _split_course_string

        num, postfix = _split_course_string('150IDS')

        assert num == '150'
        assert postfix == 'IDS'


class TestPublishMessage(object):
    @mock.patch('tas.utils.redis_broadcast_publisher')
    def test_no_publisher(self, publisher):
        from tas.utils import publish_message
        publish_message('message_type')
        assert publisher.publish_message.called

    def test_no_data_packet(self):
        from tas.utils import publish_message
        publisher = mock.Mock()
        publish_message('message_type', publisher=publisher)

        assert publisher.publish_message.called

        msg = publisher.publish_message.call_args[0][0]
        msg = json.loads(msg)

        assert 'type' in msg
        assert msg['type'] == 'message_type'

        assert 'data' not in msg

    def test_with_data_packet(self):
        from tas.utils import publish_message
        publisher = mock.Mock()

        publish_message('message_type',
                        data='this is data',
                        publisher=publisher)

        assert publisher.publish_message.called

        msg = publisher.publish_message.call_args[0][0]
        msg = json.loads(msg)

        assert 'type' in msg
        assert msg['type'] == 'message_type'

        assert 'data' in msg
        assert msg['data'] == 'this is data'


class TestGetTACourses(object):
    def test_http_error(self):
        from tas.utils import _get_ta_courses
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=404)
            assert _get_ta_courses(mock.Mock()).count() == 0

    def test_no_courses(self):
        from tas.utils import _get_ta_courses
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=200, text='NONE')
            assert _get_ta_courses(mock.Mock()).count() == 0

    @pytest.mark.django_db
    def test_two_courses(self):
        from tas.utils import _get_ta_courses
        from tas.models import Course
        G(Course, number=11)
        G(Course, number=150, postfix='IDS')
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=200, text='11 150IDS')
            assert _get_ta_courses(mock.Mock()).count() == 2

    @pytest.mark.django_db
    def test_course_does_not_exist(self):
        from tas.utils import _get_ta_courses
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=200, text='99Nope')
            assert _get_ta_courses(mock.Mock()).count() == 0

    @pytest.mark.django_db
    def test_course_is_not_case_sensitive(self):
        from tas.utils import _get_ta_courses
        from tas.models import Course
        G(Course, number=150, postfix='IDS')

        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, status_code=200, text='150ids')
            assert _get_ta_courses(mock.Mock()).count() == 1
