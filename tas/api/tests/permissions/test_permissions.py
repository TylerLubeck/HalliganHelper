import mock
import pytest
from django_dynamic_fixture import G

from rest_framework import permissions

UNSAFE_METHODS = ('PUT', 'PATCH', 'POST', 'DELETE',)


@pytest.fixture
def not_my_school():
    from tas.models import School
    from tas.custom_user import CustomUser
    admin = CustomUser.objects.create_user(email='asd@asd.com')

    school = School.objects.create(name='Test School',
                                   administrator=admin,
                                   max_course_count=5)

    return school


class TestOwnSchoolPermission:

    def test_is_own_school(self, test_school, test_user):
        from tas.api.permissions import OwnSchoolPermission
        permission = OwnSchoolPermission()

        permission._is_own_school(test_user.student, test_school)

    def test_is_not_own_school(self, test_user, not_my_school):
        from tas.api.permissions import OwnSchoolPermission

        permission = OwnSchoolPermission()

        permission._is_own_school(test_user.student, not_my_school)

    def test_not_has_permission_no_course_pk(self):
        from tas.api.permissions import OwnSchoolPermission
        view = mock.Mock()
        view.kwargs = {}

        permission = OwnSchoolPermission()
        assert not permission.has_permission(mock.Mock(), view)

    @mock.patch('tas.api.permissions.Course')
    def test_not_has_permission_no_course_found(self, Course):
        from tas.api.permissions import OwnSchoolPermission
        Course.DoesNotExist = Exception
        Course.objects.get.side_effect = Course.DoesNotExist

        view = mock.Mock()
        view.kwargs = {
            'course_pk': 11,
        }

        permission = OwnSchoolPermission()
        assert not permission.has_permission(mock.Mock(), view)

    @mock.patch('tas.api.permissions.Course')
    def test_has_permission_success(self, Course, test_user):
        from tas.api.permissions import OwnSchoolPermission

        course = mock.Mock()
        course.school = test_user.student.school
        request = mock.Mock()
        request.user = test_user
        view = mock.Mock()
        view.kwargs = {
            'course_pk': 11,
        }

        Course.objects.get.return_value = course

        permission = OwnSchoolPermission()

        assert permission.has_permission(request, view)

    def test_has_object_permission_with_request_my_school(self,
                                                          test_user,
                                                          test_school):
        from tas.models import Request
        from tas.api.permissions import OwnSchoolPermission

        obj = mock.Mock(spec=Request)
        obj.requestor.school = test_school
        request = mock.Mock()
        request.user = test_user

        permission = OwnSchoolPermission()

        assert permission.has_object_permission(request, mock.Mock(), obj)

    def test_has_object_permission_with_request_not_my_school(self,
                                                              test_user,
                                                              not_my_school):
        from tas.models import Request
        from tas.api.permissions import OwnSchoolPermission

        obj = mock.Mock(spec=Request)
        obj.requestor.school = not_my_school
        request = mock.Mock()
        request.user = test_user

        permission = OwnSchoolPermission()

        assert not permission.has_object_permission(request, mock.Mock(), obj)

    def test_has_object_permission_with_officehour_my_school(self,
                                                             test_user,
                                                             test_school):
        from tas.models import OfficeHour
        from tas.api.permissions import OwnSchoolPermission

        obj = mock.Mock(spec=OfficeHour)
        obj.ta.school = test_school
        request = mock.Mock()
        request.user = test_user

        permission = OwnSchoolPermission()

        assert permission.has_object_permission(request, mock.Mock(), obj)

    def test_has_object_permission_with_officehour_not_my_school(self,
                                                                 test_user,
                                                                 not_my_school):
        from tas.models import OfficeHour
        from tas.api.permissions import OwnSchoolPermission

        obj = mock.Mock(spec=OfficeHour)
        obj.ta.school = not_my_school
        request = mock.Mock()
        request.user = test_user

        permission = OwnSchoolPermission()

        assert not permission.has_object_permission(request, mock.Mock(), obj)

    def test_has_object_permission_with_student_my_school(self,
                                                          test_user,
                                                          test_school):
        from tas.models import Student
        from tas.api.permissions import OwnSchoolPermission

        obj = mock.Mock(spec=Student)
        obj.school = test_school
        request = mock.Mock()
        request.user = test_user

        permission = OwnSchoolPermission()

        assert permission.has_object_permission(request, mock.Mock(), obj)

    def test_has_object_permission_with_student_not_my_school(self,
                                                              test_user,
                                                              not_my_school):
        from tas.models import Student
        from tas.api.permissions import OwnSchoolPermission

        obj = mock.Mock(spec=Student)
        obj.school = not_my_school
        request = mock.Mock()
        request.user = test_user

        permission = OwnSchoolPermission()

        assert not permission.has_object_permission(request, mock.Mock(), obj)

    def test_has_object_permission_not_registered_object(self):
        from tas.models import (
            SchoolEmailDomain,
            Course,
            TA,
        )
        from tas.api.permissions import OwnSchoolPermission

        permission = OwnSchoolPermission()

        for model in [SchoolEmailDomain, Course, TA]:
            obj = mock.Mock(spec=model)

            assert not permission.has_object_permission(mock.Mock(),
                                                        mock.Mock(),
                                                        obj)


class TestRequestPermission:

    def test_student_can_not_solve(self, test_user, test_course):
        from tas.models import Request
        from tas.api.permissions import RequestPermission

        permission = RequestPermission()

        obj = mock.Mock(spec=Request)
        obj.solved = False
        obj.course = test_course

        mock_request = mock.Mock()
        mock_request.user = test_user
        mock_request.data = {
            'solved': True,
        }

        assert not permission.has_object_permission(mock_request,
                                                    mock.Mock(),
                                                    obj)

    def test_ta_can_solve(self, test_user_ta, test_course):
        from tas.models import Request
        from tas.api.permissions import RequestPermission

        permission = RequestPermission()

        obj = mock.Mock(spec=Request)
        obj.solved = False
        obj.course = test_course

        mock_request = mock.Mock()
        mock_request.user = test_user_ta
        mock_request.data = {
            'solved': True,
        }

        assert permission.has_object_permission(mock_request,
                                                mock.Mock(),
                                                obj)

    def test_ta_can_not_cancel(self, test_user_ta, test_user, test_course):
        from tas.models import Request
        from tas.api.permissions import RequestPermission

        permission = RequestPermission()

        obj = mock.Mock(spec=Request)
        obj.cancelled = False
        obj.course = test_course
        obj.requestor = test_user

        mock_request = mock.Mock()
        mock_request.user = test_user_ta
        mock_request.data = {
            'cancelled': True,
        }

        assert not permission.has_object_permission(mock_request,
                                                    mock.Mock(),
                                                    obj)

    def test_student_can_cancel(self, test_user, test_course):
        from tas.models import Request
        from tas.api.permissions import RequestPermission

        permission = RequestPermission()

        obj = mock.Mock(spec=Request)
        obj.cancelled = False
        obj.course = test_course

        mock_request = mock.Mock()
        mock_request.user = test_user
        mock_request.data = {
            'cancelled': True,
        }

        assert not permission.has_object_permission(mock_request,
                                                    mock.Mock(),
                                                    obj)


class TestOfficeHourPermissionsSingleObject(object):

    def test_no_course_pk(self):
        from tas.api.permissions import OfficeHourPermission

        view = mock.Mock()
        view.kwargs = {'course_pk': None}

        ohp = OfficeHourPermission()

        assert not ohp.has_permission(mock.Mock(), view)

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', permissions.SAFE_METHODS)
    def test_always_granted_for_safe_methods_with_same_school(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student
        course = G(Course)
        student = G(Student, school=course.school)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert ohp.has_permission(request, view)

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', permissions.SAFE_METHODS)
    def test_never_granted_for_different_schools(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student, School
        school_one = G(School)
        school_two = G(School)

        course = G(Course, school=school_one)
        student = G(Student, school=school_two)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert not ohp.has_permission(request, view)

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', UNSAFE_METHODS)
    def test_must_be_ta_for_unsafe_methods(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student
        course = G(Course)
        student = G(Student, school=course.school)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert not ohp.has_permission(request, view)

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', UNSAFE_METHODS)
    def test_is_ta_for_course(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student, TA
        course = G(Course)
        student = G(Student, school=course.school)
        G(TA, course=course, student=student, active=True)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert ohp.has_permission(request, view)

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', UNSAFE_METHODS)
    def test_is_not_ta_for_course(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student, TA
        course = G(Course)
        other_course = G(Course)
        student = G(Student, school=course.school)
        G(TA, course=other_course, student=student, active=True)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert not ohp.has_permission(request, view)

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', UNSAFE_METHODS)
    def test_is_not_active_ta_for_course(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student, TA
        course = G(Course)
        student = G(Student, school=course.school)
        G(TA, course=course, student=student, active=False)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert not ohp.has_permission(request, view)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'method',
        permissions.SAFE_METHODS + UNSAFE_METHODS
    )
    def test_course_must_exist(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student, TA
        course = G(Course)
        student = G(Student, school=course.school)
        G(TA, course=course, student=student, active=False)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk + 1}

        ohp = OfficeHourPermission()

        assert not ohp.has_permission(request, view)


class TestOfficeHourPermissionsList(object):

    @pytest.mark.xfail(reason='See comment in code')
    @pytest.mark.parametrize(
        'method',
        permissions.SAFE_METHODS + UNSAFE_METHODS
    )
    def test_no_course_pk(self, method):
        from tas.api.permissions import OfficeHourPermission

        # We shouldn't need to look at the user for this one.
        request = mock.Mock()
        request.user = AttributeError
        request.method = method

        view = mock.Mock()
        view.kwargs = {'course_pk': None}

        ohp = OfficeHourPermission()

        assert not ohp.has_object_permission(request, view, mock.Mock())

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', permissions.SAFE_METHODS)
    def test_always_granted_for_safe_methods_with_same_school(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student, OfficeHour
        course = G(Course)
        student = G(Student, school=course.school)
        office_hour = G(OfficeHour, ta=student, course=course)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert ohp.has_object_permission(request, view, office_hour)

    @pytest.mark.django_db
    @pytest.mark.parametrize('method', UNSAFE_METHODS)
    def test_not_my_office_hour(self, method):
        from tas.api.permissions import OfficeHourPermission
        from tas.models import Course, Student, OfficeHour
        course = G(Course)
        student = G(Student, school=course.school)
        other_student = G(Student, school=course.school)
        office_hour = G(OfficeHour, ta=other_student, course=course)

        request = mock.Mock()
        request.method = method
        request.user.student = student

        view = mock.Mock()
        view.kwargs = {'course_pk': course.pk}

        ohp = OfficeHourPermission()

        assert not ohp.has_object_permission(request, view, office_hour)
