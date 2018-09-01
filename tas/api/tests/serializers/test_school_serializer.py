import pytest
from django_dynamic_fixture import G


class TestSchoolAdminSerializerIsHeadAdmin(object):

    @pytest.mark.django_db
    def test_has_an_administrator(self):
        from tas.api.serializers import SchoolSerializer
        from tas.models import School

        school = G(School)

        ss = SchoolSerializer()

        administrators = ss.get_administrators(school)
        assert len(administrators) == 1
        assert 'email' in administrators[0]
        assert 'headshot_url' in administrators[0]
        assert 'full_name' in administrators[0]
        assert 'is_head_admin' in administrators[0]

    @pytest.mark.django_db
    def test_has_multiple_administrator(self):
        from tas.api.serializers import SchoolSerializer
        from tas.models import School, CustomUser
        from django.contrib.auth.models import Group

        school = G(School)
        user = G(CustomUser)
        group = Group.objects.get(name='{} Admins'.format(school.name))
        user.groups.add(group)

        ss = SchoolSerializer()

        administrators = ss.get_administrators(school)
        assert len(administrators) == 2
