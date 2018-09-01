import pytest
import random
import string

def random_string(length=10):
    return ''.join(random.sample(string.ascii_letters, length))


def random_email(length=10):
    return '{}@sample.com'.format(random_string(length))


@pytest.fixture
def test_user(django_user_model, test_school):
    from tas.models import Student
    user, _ = django_user_model.objects.get_or_create(first_name='first_name',
                                                      last_name='last_name',
                                                      email=random_email(),
                                                      password='password')
    # Student.objects.create(user=user, school=test_school)

    return user


@pytest.fixture
def test_school(django_user_model):
    from tas.models import School, SchoolEmailDomain
    user = django_user_model.objects.create(first_name='school admin',
                                            last_name='school_admin',
                                            email=random_email(),
                                            password='password')

    school, _ = School.objects.get_or_create(name=random_string(),
                                             administrator=user,
                                             max_course_count=5)

    SchoolEmailDomain.objects.create(domain="sample.com", school=school)

    return school


@pytest.fixture
def test_course(test_school):
    from tas.models import Course
    course, _ = Course.objects.get_or_create(school=test_school,
                                             department='TESTS',
                                             number=1)

    return course


@pytest.fixture
def test_user_ta(django_user_model, test_school, test_course):
    from tas.models import Student, TA
    user = django_user_model.objects.create(first_name='first_name',
                                            last_name='last_name',
                                            email=random_email(),
                                            password='password')

    TA.objects.create(student=user.student,
                      course=test_course,
                      active=True)
    return user

