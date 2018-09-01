__author__ = 'tyler'
from django.core.management.base import BaseCommand
from tas.models import Student
from tas.utils import check_ta

# Don't mess with anyone from other schools
SCHOOL = 'Tufts University'


class Command(BaseCommand):
    help = 'Update TAs from Bruce Molays list of TA emails'

    def handle(self, *args, **options):
        for student in Student.objects.filter(school__name=SCHOOL):
            self.stdout.write('Processing {}...'.format(student.user.email))
            check_ta(student.user)
