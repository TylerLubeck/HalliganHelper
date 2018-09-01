import mock
import pytest
from django_dynamic_fixture import G

class TestSchoolAdminSerializerIsHeadAdmin(object):

    @pytest.mark.django_db
    def test_is_not_head_admin(self):
        from tas.api.serializers import SchoolAdminSerializer
        from tas.models import CustomUser
        user = G(CustomUser)

        sas = SchoolAdminSerializer()

        assert not sas.get_is_head_admin(user)

    @pytest.mark.django_db
    def test_is_head_admin(self):
        from tas.api.serializers import SchoolAdminSerializer
        from tas.models import CustomUser, School
        user = G(CustomUser)
        G(School, administrator=user)

        sas = SchoolAdminSerializer()

        assert sas.get_is_head_admin(user)
