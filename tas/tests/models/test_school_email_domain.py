import pytest
from django_dynamic_fixture import N, G

from django.db import IntegrityError


class TestSchoolEmailDomain(object):

    @pytest.mark.django_db
    def test_str_method(self):
        from tas.models import SchoolEmailDomain

        sed = N(SchoolEmailDomain)

        assert str(sed) == '{} - {}'.format(sed.school.name, sed.domain)

    @pytest.mark.django_db
    def test_has_school_object(self):
        from tas.models import SchoolEmailDomain, School

        sed = N(SchoolEmailDomain)

        assert isinstance(sed.school, School)

    @pytest.mark.django_db
    def test_unique_by_name(self):
        from tas.models import SchoolEmailDomain

        sed = G(SchoolEmailDomain)

        duplicate_sed = N(SchoolEmailDomain, domain=sed.domain)

        with pytest.raises(IntegrityError):
            duplicate_sed.save()
