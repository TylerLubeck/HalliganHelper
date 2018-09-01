import pytest
from django_dynamic_fixture import G


class TestTA(object):

    @pytest.mark.django_db
    def test_ta_string(self):
        from tas.models import TA
        ta = G(TA)
        assert str(ta) == 'TA: {}'.format(ta.student.user.get_full_name())

    @pytest.mark.django_db
    def test_ta_rep(self):
        from tas.models import TA
        ta = G(TA)
        assert repr(ta) == '<TA ({}) at 0x{}>'.format(
            ta.student.user.get_full_name(),
            id(ta)
        )
