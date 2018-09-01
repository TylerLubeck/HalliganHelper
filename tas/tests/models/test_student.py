import pytest
import mock
from django_dynamic_fixture import N, G


class TestStudent(object):

    @pytest.mark.django_db
    def test_student_name(self):
        from tas.models import Student
        student = N(Student)

        assert str(student) == student.user.get_full_name()

    @pytest.mark.django_db
    def test_student_repr(self):
        from tas.models import Student
        student = N(Student)

        assert repr(student) == '<Student ({}) at {}>'.format(
            student.user.get_full_name(),
            id(student)
        )

    @pytest.mark.django_db
    def test_student_starts_with_no_courses(self):
        from tas.models import Student
        student = G(Student)
        assert len(student.courses.all()) == 0

    @pytest.mark.django_db
    def test_student_starts_with_no_ta_jobs(self):
        from tas.models import Student
        student = G(Student)
        assert len(student.ta_jobs.all()) == 0

    @pytest.mark.django_db
    def test_profile_signal_fired_when_user_created(self):
        with mock.patch('tas.models.create_student_profile_for_user') as cspu:
            from tas.models import CustomUser
            G(CustomUser)
            assert cspu.called_once

    @pytest.mark.django_db
    def test_student_created_when_user_created(self):
        from tas.models import CustomUser, SchoolEmailDomain, Student
        sed = G(SchoolEmailDomain)
        user = G(CustomUser, email='email@{}'.format(sed.domain))

        assert Student.objects.filter(user=user).exists()

    @pytest.mark.django_db
    def test_student_not_created_for_bad_email(self):
        from tas.models import CustomUser, Student
        user = G(CustomUser, email='does_not_exist')

        assert not Student.objects.filter(user=user).exists()
