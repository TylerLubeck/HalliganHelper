import pytest
from django_dynamic_fixture import G
from django_dynamic_fixture.ddf import BadDataError


class TestRequest(object):

    @pytest.mark.django_db
    def test_request_string(self):
        from tas.models import Request
        request = G(Request)

        assert str(request) == '{} - Comp {}'.format(
            request.requestor.user.get_full_name(),
            request.course.number
        )

    @pytest.mark.django_db
    def test_question_max_length(self):
        from tas.models import Request
        QUESTION_MAX_LENGTH = 51
        question = 'x' * (QUESTION_MAX_LENGTH + 1)

        # ddf wraps the ValidationError with a BadDataError. It's either do
        # this or manually construct the Request object, and that seems
        # more fragile
        with pytest.raises(BadDataError):
            G(Request, question=question)

    @pytest.mark.django_db
    def test_where_located_max_length(self):
        from tas.models import Request
        WHERE_LOCATED_MAX_LENGTH = 50
        location = 'x' * (WHERE_LOCATED_MAX_LENGTH + 1)

        # ddf wraps the ValidationError with a BadDataError. It's either do
        # this or manually construct the Request object, and that seems
        # more fragile
        with pytest.raises(BadDataError):
            G(Request, where_located=location)
