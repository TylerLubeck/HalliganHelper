import pytest
from django_dynamic_fixture import G
from rest_framework.test import (
    APIRequestFactory,
    APIClient
)

from rest_framework.exceptions import (
    PermissionDenied,
    MethodNotAllowed
)


class TestUserViewSet(object):
    def test_unauthed_list_method_raises_exception(self):
        from tas.api.views import UserViewSet
        factory = APIRequestFactory()
        request = factory.get('/api/v3/user')
        view = UserViewSet.as_view(actions={'get': 'list'})
        response = view(request)

        assert response.status_code == PermissionDenied.status_code

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'method,response_code',
        (
            ('GET', MethodNotAllowed.status_code,),
            ('HEAD', MethodNotAllowed.status_code,),
            ('OPTIONS', 200,),
            ('PUT', MethodNotAllowed.status_code,),
            # ('PATCH', MethodNotAllowed.status_code,),
            ('POST', 200,),
            ('DELETE', MethodNotAllowed.status_code,),
        )
    )
    def test_login_only_responds_to_post(self, method, response_code):
        from tas.models import Student

        student = G(Student)
        student.user.set_password('password')
        student.user.save()

        client = APIClient()
        request_method = getattr(client, method.lower())
        response = request_method(
            '/api/v3/user/login/',
            {'email': student.user.email, 'password': 'password'}
        )

        print(response)

        assert response.status_code == response_code
