import pytest
import mock


class TestEmptyStringValidator(object):
    def test_with_empty_string(self):
        from tas.models import not_empty_string
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            not_empty_string('')

    def test_with_nonempty_string(self):
        from tas.models import not_empty_string

        not_empty_string('not_empty')


class TestDetermineHeadshotName(object):

    def test_places_in_headshots_folder(self):
        from tas.models import determine_headshot_name, Student

        student = mock.Mock(spec=Student)
        student.user.email = 'a@a.com'
        student.user.pk = 4

        path_name = determine_headshot_name(student, 'file')
        assert path_name.startswith('headshots/')

    def test_hashes_with_email_and_pk(self):
        with mock.patch('tas.models.hashlib') as hashlib:
            from tas.models import determine_headshot_name, Student

            student = mock.Mock(spec=Student)
            student.user.email = 'a@a.com'
            student.user.pk = 4

            hash_string = '{}-{}-headshot'.format(
                student.user.email,
                student.user.pk
            )

            determine_headshot_name(student, 'file')
            assert hashlib.sha224.called_once_with(hash_string)
            assert hashlib.sha224.hexdigest.called_once
