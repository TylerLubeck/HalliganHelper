import mock
import pytest
from django_dynamic_fixture import G

from rest_framework import serializers


class TestLoginSerializerEmail(object):

    @pytest.mark.django_db
    def test_email_must_exist(self):
        from tas.api.serializers import LoginSerializer
        from tas.models import CustomUser

        G(CustomUser, email='real_email@email.com')
        ls = LoginSerializer()
        with pytest.raises(serializers.ValidationError):
            ls.validate_email('not_real_email@email.com')

    @pytest.mark.django_db
    def test_email_does_exist(self):
        from tas.api.serializers import LoginSerializer
        from tas.models import CustomUser

        user = G(CustomUser)
        ls = LoginSerializer()
        ls.validate_email(user.email)

    @pytest.mark.django_db
    def test_email_is_not_case_sensitive(self):
        from tas.api.serializers import LoginSerializer
        from tas.models import CustomUser

        email = 'real_email@email.com'
        G(CustomUser, email=email)

        ls = LoginSerializer()
        ls.validate_email(email.upper())


class TestLoginSerializerPassword(object):

    @pytest.mark.django_db
    def test_with_invalid_email(self):
        from tas.api.serializers import LoginSerializer
        from tas.models import CustomUser

        user = G(CustomUser, email='fake_email@email.com')
        ls = LoginSerializer()
        ls.initial_data = {'email': 'real_email@email.com'}
        assert ls.validate_password(user.password) is None

    @pytest.mark.django_db
    def test_with_wrong_password(self):
        from tas.api.serializers import LoginSerializer
        from tas.models import CustomUser

        user = G(CustomUser, password='password')
        ls = LoginSerializer()
        ls.initial_data = {'email': user.email}
        with pytest.raises(serializers.ValidationError):
            ls.validate_password('wrong_password')

    @pytest.mark.django_db
    def test_returns_password(self):
        with mock.patch('tas.api.serializers.authenticate') as authenticate:
            from tas.api.serializers import LoginSerializer
            from tas.models import Student

            student = G(Student)
            user = student.user
            authenticate.return_value = user

            ls = LoginSerializer()
            ls.initial_data = {'email': user.email}
            assert ls.validate_password(user.password) == user.password

    @pytest.mark.django_db
    def test_wrong_password_for_user(self):
        with mock.patch('tas.api.serializers.authenticate') as authenticate:
            from tas.api.serializers import LoginSerializer
            from tas.models import Student

            student = G(Student)
            user = student.user
            authenticate.return_value = None

            ls = LoginSerializer()
            ls.initial_data = {'email': user.email}
            with pytest.raises(serializers.ValidationError):
                ls.validate_password(user.password)

    @pytest.mark.django_db
    def test_inactive_user(self):
        with mock.patch('tas.api.serializers.authenticate') as authenticate:
            from tas.api.serializers import LoginSerializer
            from tas.models import Student

            student = G(Student)
            user = student.user
            user.is_active = False
            authenticate.return_value = user

            ls = LoginSerializer()
            ls.initial_data = {'email': user.email}
            with pytest.raises(serializers.ValidationError):
                ls.validate_password(user.password)

    @pytest.mark.django_db
    def test_calls_login(self):
        with mock.patch('tas.api.serializers.authenticate') as authenticate:
            with mock.patch('tas.api.serializers.login') as login:
                from tas.api.serializers import LoginSerializer
                from tas.models import Student

                student = G(Student)
                user = student.user
                authenticate.return_value = user

                ls = LoginSerializer()
                ls.initial_data = {'email': user.email}
                ls.context = {'request': mock.Mock()}

                ls.validate_password(user.password)

                assert login.called_once
