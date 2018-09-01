import mock
import pytest
from django_dynamic_fixture import G

from django.db import DataError


class TestCustomUser(object):

    @pytest.mark.django_db
    def test_first_name_length_too_long(self):
        from tas.models import CustomUser
        user = CustomUser(first_name='l' * 101)
        with pytest.raises(DataError):
            user.save()

    @pytest.mark.django_db
    def test_first_name_length_fits(self):
        from tas.models import CustomUser
        user = CustomUser(first_name='l' * 100)
        user.save()

    @pytest.mark.django_db
    def test_last_name_length_too_long(self):
        from tas.models import CustomUser
        user = CustomUser(last_name='l' * 101)
        with pytest.raises(DataError):
            user.save()

    @pytest.mark.django_db
    def test_last_name_length_fits(self):
        from tas.models import CustomUser
        user = CustomUser(last_name='l' * 100)
        user.save()

    @pytest.mark.django_db
    def test_is_staff_defaults_to_false(self):
        from tas.models import CustomUser
        user = CustomUser()
        user.save()

        assert not user.is_staff

    @pytest.mark.django_db
    def test_is_active_defaults_to_true(self):
        from tas.models import CustomUser
        user = CustomUser()
        user.save()

        assert user.is_active

    @pytest.mark.django_db
    def test_objects_is_a_custom_user_manager(self):
        from tas.models import CustomUser
        from tas.custom_user import CustomUserManager

        assert isinstance(CustomUser.objects, CustomUserManager)

    def test_get_full_name(self):
        from tas.models import CustomUser

        first_name = 'jim'
        last_name = 'beam'

        user = CustomUser(first_name=first_name, last_name=last_name)

        assert user.get_full_name() == '{} {}'.format(first_name, last_name)

    def test_get_short_name(self):
        from tas.models import CustomUser

        first_name = 'jim'
        last_name = 'beam'

        user = CustomUser(first_name=first_name, last_name=last_name)

        assert user.get_short_name() == '{} {}.'.format(
            first_name.title(),
            last_name[0].upper()
        )

    def test_string_method(self):
        from tas.models import CustomUser

        data = {
            'first_name': 'jim',
            'last_name': 'beam',
            'email': 'email@email.com',
        }

        user = CustomUser(**data)

        assert str(user) == '{} ({})'.format(
            user.get_full_name(),
            data['email']
        )

    @pytest.mark.django_db
    def test_email_user(self):
        from tas.models import CustomUser

        subject = 'test'
        message = 'test'
        from_email = 'support@halliganhelper.com'

        user = G(CustomUser, email='support@halliganhelper.com')

        with mock.patch('django.core.mail.send_mail') as send_mail:
            user.email_user(subject, message, from_email=from_email)

            assert send_mail.called_once_with(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[user.email]
            )

    @pytest.mark.django_db
    def test_email_user_html_message(self):
        from tas.models import CustomUser

        subject = 'test'
        message = 'test'
        from_email = 'support@halliganhelper.com'
        html_message = '<span>hello</span>'

        user = G(CustomUser, email='support@halliganhelper.com')

        with mock.patch('django.core.mail.send_mail') as send_mail:
            user.email_user(subject, message, html_message, from_email)

            assert send_mail.called_once_with(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[user.email],
                html_message=html_message
            )

    @pytest.mark.django_db
    def test_email_user_default_from_email(self):
        from tas.models import CustomUser

        subject = 'test'
        message = 'test'
        from_email = 'support@halliganhelper.com'

        user = G(CustomUser, email='support@halliganhelper.com')

        with mock.patch('django.core.mail.send_mail') as send_mail:
            with mock.patch('django.conf.settings') as settings:
                settings.DEFAULT_FROM_EMAIL = from_email
                user.email_user(subject, message)

                assert send_mail.called_once_with(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=[user.email]
                )


class TestCustomUserManager(object):

    def test_create_basic_user(self):
        email = 'support@halliganhelper.com'
        password = 'password'
        with mock.patch('tas.custom_user.CustomUserManager._create_user') as raw_create:
            from tas.custom_user import CustomUserManager
            manager = CustomUserManager()
            manager.create_user(email, password)

            assert raw_create.called_once_with(
                email,
                password,
                is_staff=False,
                is_superuser=False
            )

    def test_create_basic_user_passes_kwargs(self):
        email = 'support@halliganhelper.com'
        password = 'password'
        with mock.patch('tas.custom_user.CustomUserManager._create_user') as raw_create:
            from tas.custom_user import CustomUserManager
            manager = CustomUserManager()
            manager.create_user(email, password, some_thing='blah')

            assert raw_create.called_once_with(
                email,
                password,
                is_staff=False,
                is_superuser=False,
                some_thing='blah'
            )

    def test_create_super_user(self):
        email = 'support@halliganhelper.com'
        password = 'password'
        with mock.patch('tas.custom_user.CustomUserManager._create_user') as raw_create:
            from tas.custom_user import CustomUserManager
            manager = CustomUserManager()
            manager.create_superuser(email, password)

            assert raw_create.called_once_with(
                email,
                password,
                is_staff=True,
                is_superuser=True,
            )

    def test_create_super_user_passes_kwargs(self):
        email = 'support@halliganhelper.com'
        password = 'password'
        with mock.patch('tas.custom_user.CustomUserManager._create_user') as raw_create:
            from tas.custom_user import CustomUserManager
            manager = CustomUserManager()
            manager.create_superuser(email, password, some_thing='blah')

            assert raw_create.called_once_with(
                email,
                password,
                is_staff=True,
                is_superuser=True,
                some_thing='blah'
            )

    def test_raw_create_user_requires_email(self):
        from tas.custom_user import CustomUserManager
        manager = CustomUserManager()

        with pytest.raises(ValueError):
            manager._create_user(
                email=None,
                password='',
                is_staff=False,
                is_superuser=False
            )

    def test_create_user_normalizes_email(self):
        from tas.custom_user import CustomUserManager
        manager = CustomUserManager()
        manager.model = mock.Mock()

        email = 'support@halliganhelper.com'
        with mock.patch('tas.custom_user.CustomUserManager.normalize_email') as normalize:
            manager._create_user(
                email=email,
                password='',
                is_staff=False,
                is_superuser=False
            )

            assert normalize.called_once_with(email)

    def test_create_user_sets_password(self):
        from tas.custom_user import CustomUserManager
        user = mock.Mock()
        model = mock.Mock()
        model.return_value = user

        manager = CustomUserManager()
        manager.model = model

        email = 'support@halliganhelper.com'
        password = 'password'
        manager._create_user(
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False
        )

        assert user.set_password.called_once_with(password)

    def test_create_user_saves_the_user(self):
        from tas.custom_user import CustomUserManager
        user = mock.Mock()
        model = mock.Mock()
        model.return_value = user

        manager = CustomUserManager()
        manager.model = model

        email = 'support@halliganhelper.com'
        password = 'password'
        manager._create_user(
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False
        )

        assert user.save.called
