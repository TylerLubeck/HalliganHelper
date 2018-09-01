import pytest
from django_dynamic_fixture import G

from rest_framework import serializers


class TestRegistrationSerializerEmail(object):

    @pytest.mark.django_db
    def test_no_school_for_domain(self):
        from tas.api.serializers import RegistrationSerializer

        rs = RegistrationSerializer()

        with pytest.raises(serializers.ValidationError):
            rs.validate_email('nope@noschool.edu')

    @pytest.mark.django_db
    def test_email_already_exists(self):
        from tas.api.serializers import RegistrationSerializer
        from tas.models import SchoolEmailDomain, CustomUser

        domain = 'school.edu'
        email = 'not_unique@{}'.format(domain)
        G(SchoolEmailDomain, domain=domain)
        G(CustomUser, email=email)

        rs = RegistrationSerializer()

        with pytest.raises(serializers.ValidationError):
            rs.validate_email(email)

    @pytest.mark.django_db
    def test_returns_email(self):
        from tas.api.serializers import RegistrationSerializer
        from tas.models import SchoolEmailDomain

        domain = 'school.edu'
        email = 'not_unique@{}'.format(domain)
        G(SchoolEmailDomain, domain=domain)

        rs = RegistrationSerializer()

        assert rs.validate_email(email) == email


class TestRegistrationSerializerPassword(object):

    def test_returns_password(self):
        from tas.api.serializers import RegistrationSerializer

        password = 'password'

        rs = RegistrationSerializer()
        rs.initial_data = {'password': password}

        assert rs.validate_password_confirm(password) == password

    def test_wrong_password_raises_error(self):
        from tas.api.serializers import RegistrationSerializer

        rs = RegistrationSerializer()
        rs.initial_data = {'password': 'password'}

        with pytest.raises(serializers.ValidationError):
            rs.validate_password_confirm('wrong_password')


class TestRegistrationSerializer(object):

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'email,password,password_confirm,fname,lname,is_valid',
        (
            ('f@f.com', 'perfect', 'perfect', 'jim', 'beam', True),
            ('f@f.com', 'short', 'short', 'jim', 'beam', False),
            ('f@f.com', 'l' * 256, 'l' * 256, 'jim', 'beam', False),
            ('f@f.com', 'perfect', 'perfect', 'j' * 101, 'beam', False),
            ('f@f.com', 'perfect', 'perfect', 'jim', 'b' * 101, False),
            ('f@f.com', 'nomatch', 'forreal', 'jim', 'b' * 101, False),
        )
    )
    def test_validation(
        self,
        email,
        password,
        password_confirm,
        fname,
        lname,
        is_valid
    ):
        from tas.api.serializers import RegistrationSerializer
        from tas.models import SchoolEmailDomain
        G(SchoolEmailDomain, domain='f.com')
        rs = RegistrationSerializer(
            data={
                'email': email,
                'password': password,
                'password_confirm': password_confirm,
                'first_name': fname,
                'last_name': lname,
            }
        )

        assert rs.is_valid() == is_valid
