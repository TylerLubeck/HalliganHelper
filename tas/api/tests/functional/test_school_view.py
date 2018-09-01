import json

import pytest
from django_dynamic_fixture import G
from rest_framework.test import (
    force_authenticate,
    APIRequestFactory,
    APIClient,
)

from rest_framework.exceptions import (
    PermissionDenied,
    MethodNotAllowed,
    NotFound,
)


class TestSchoolView(object):
    def test_permission_denied_if_not_authenticated(self):
        from tas.api.views import SchoolView
        factory = APIRequestFactory()
        request = factory.get('/api/v3/school')
        view = SchoolView.as_view()
        response = view(request)

        assert response.status_code == PermissionDenied.status_code

    @pytest.mark.django_db
    def test_permission_granted_if_authenticated(self):
        from tas.api.views import SchoolView
        from tas.models import Student

        student = G(Student)

        factory = APIRequestFactory()
        request = factory.get('/api/v3/school')
        view = SchoolView.as_view()

        force_authenticate(request, user=student.user)
        response = view(request)

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_does_not_have_an_individual_getter(self):
        from tas.models import Student

        student = G(Student)

        client = APIClient()
        client.force_authenticate(user=student.user)
        response = client.get('/api/v3/school/{}/'.format(student.school.pk))

        assert response.status_code == NotFound.status_code

    @pytest.mark.django_db
    def test_returns_the_users_school(self):
        from tas.api.views import SchoolView
        from tas.models import Student, School

        real_name = 'Real Name'
        fake_name = 'Fake Name'
        student = G(Student, school__name=real_name)

        # make a decoy school
        G(School, name=fake_name)

        factory = APIRequestFactory()
        request = factory.get('/api/v3/school')
        view = SchoolView.as_view()

        force_authenticate(request, user=student.user)
        response = view(request)
        response.render()
        data = json.loads(response.content)

        assert data['name'] == real_name

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'method,status_code',
        (
            ('GET', 200,),
            ('OPTIONS', 200,),
            ('HEAD', 200,),
            ('POST', MethodNotAllowed.status_code,),
            ('PUT', MethodNotAllowed.status_code,),
            ('PATCH', MethodNotAllowed.status_code,),
        )
    )
    def test_only_responds_to_safe_methods(self, method, status_code):
        from tas.api.views import SchoolView
        from tas.models import Student

        student = G(Student)

        factory = APIRequestFactory()
        request_method = getattr(factory, method.lower())
        request = request_method('/api/v3/school')
        view = SchoolView.as_view()

        force_authenticate(request, user=student.user)
        response = view(request)

        assert response.status_code == status_code
