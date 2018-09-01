import pytest
from django_dynamic_fixture import N, G

from django.db import IntegrityError


class TestCourse(object):

    @pytest.mark.django_db
    def test_str_method(self):
        from tas.models import Course

        course = N(Course)

        assert str(course) == '{}: {}'.format(course.school.name, course.name)

    @pytest.mark.django_db
    def test_get_identifier(self):
        from tas.models import Course

        course = N(Course)

        assert course.get_identifier() == '{} {}{}'.format(
                course.department.title(),
                course.number,
                course.postfix
        )

    @pytest.mark.django_db
    def test_that_postfix_can_be_blank(self):
        from tas.models import Course

        # If this throws an exception, this test fails.
        course = G(Course, postfix='')
        course.save()

    @pytest.mark.django_db
    def test_ordering(self):
        from tas.models import Course, SchoolEmailDomain

        sed = G(SchoolEmailDomain)
        for course_num in range(5):
            email = '{}@{}'.format(course_num, sed.domain)
            G(Course, number=course_num, school__administrator__email=email)

        courses = Course.objects.all()
        implicit_sort = courses.values_list('pk', flat=True)
        explicit_sort = courses.order_by('department', 'number').values_list('pk', flat=True)

        assert len(implicit_sort) == len(explicit_sort)

        for a, b in zip(implicit_sort, explicit_sort):
            assert a == b
