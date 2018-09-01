import json

import pytest
from django_dynamic_fixture import G
from rest_framework.test import (
    force_authenticate,
    APIClient
)

from rest_framework.exceptions import (
    PermissionDenied,
    MethodNotAllowed,
    NotFound,
)


class TestRequestView(object):

    @pytest.mark.django_db
    def test_(self):
        from tas.models import Course, Student, School

        student = G(Student)
        other_school = G(School)
        course = G(Course, school=other_school)

        client = APIClient()
        client.force_authenticate(user=student.user)
        response = client.get('/api/v3/school/courses/')
        response_data = json.loads(response.content)
