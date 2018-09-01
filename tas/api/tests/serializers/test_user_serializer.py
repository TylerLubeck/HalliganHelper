import pytest
from django_dynamic_fixture import G


class TestUserSerializer(object):

    @pytest.mark.django_db
    def test_get_ta_jobs(self):
        from tas.api.serializers import UserSerializer
        from tas.models import Student, Course, TA
        student = G(Student)
        course = G(Course, school=student.school)
        G(TA, student=student, course=course, active=True)

        # second course, not assigned to student
        G(Course, school=student.school)

        us = UserSerializer()
        assert len(us.get_ta_jobs(student.user)) == 1
