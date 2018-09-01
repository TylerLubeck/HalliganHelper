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


class TestCourseView(object):

    @pytest.mark.django_db
    def test_does_not_get_course_from_other_school(self):
        from tas.models import Course, Student, School

        student = G(Student)
        other_school = G(School)
        course = G(Course, school=other_school)

        client = APIClient()
        client.force_authenticate(user=student.user)
        response = client.get('/api/v3/school/courses/')
        response_data = json.loads(response.content)

        # List method should show nothing
        assert response.status_code == 200
        assert len(response_data) == 0

        # Detail method for other school's course should 404
        response = client.get('/api/v3/school/courses/{}/'.format(course.pk))
        assert response.status_code == NotFound.status_code

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'method,response_code',
        (
            ('GET', 200,),
            ('HEAD', 200,),
            ('OPTIONS', 200,),
            ('PUT', MethodNotAllowed.status_code,),
            ('PATCH', MethodNotAllowed.status_code,),
            ('POST', MethodNotAllowed.status_code,),
            ('DELETE', MethodNotAllowed.status_code,),
        )
    )
    def test_does_not_respond_to_unsafe_methods(self, method, response_code):
        from tas.models import Student

        student = G(Student)

        client = APIClient()
        client.force_authenticate(user=student.user)
        request_method = getattr(client, method.lower())
        response = request_method('/api/v3/school/courses/')

        assert response.status_code == response_code
