import pytest
import mock
from django_dynamic_fixture import N, G

from django.db import IntegrityError


class TestSchool(object):

    def test_name_method(self):
        from tas.models import School
        school_name = 'my_school'
        school = School(name=school_name)

        assert str(school) == school_name

    @pytest.mark.django_db
    def test_group_created_on_save(self):
        school_name = 'my_school'

        with mock.patch('tas.models.create_school_admin_group') as create_group_signal:
            with mock.patch('tas.models.Group') as Group:
                from tas.models import School
                from tas.utils import get_school_admin_group_name

                school = N(School, name=school_name)
                school.save()

                assert create_group_signal.called_once
                assert Group.objects.get_or_create.called_once_with(
                    name=get_school_admin_group_name(school_name)
                )

    @pytest.mark.django_db
    def test_unique_by_name(self):
        from tas.models import School
        school = G(School)
        duplicate_school = N(School, name=school.name)

        with pytest.raises(IntegrityError):
            duplicate_school.save()
