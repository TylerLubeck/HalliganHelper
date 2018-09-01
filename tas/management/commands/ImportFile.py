__author__ = 'tom'
import argparse
import csv

from django.core.management.base import BaseCommand
from django.template.loader import get_template
from tas.custom_user import CustomUser
from tas.models import Course, Student, TA
from tas.utils import notify


class Command(BaseCommand):
    help = 'Ensure that all accounts in a file exist and are TAs for a course'

    def notify_account(self, user, course):
        subject = 'Your Halligan Helper Account'

        plaintext = get_template('tas/email/new_account.txt')
        htmly = get_template('tas/email/new_account.html')

        d = {'user': user, 'course': course}
        text_content = plaintext.render(d)
        html_content = htmly.render(d)

        user.email_user(subject, text_content, html_message=html_content)

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', type=argparse.FileType('r'),
            help="a CSV file with an email address and a name on each line"
        )

        parser.add_argument(
            'course_id', type=int,
            help="the ID of the course to add TAs to"
        )

    def handle(self, *args, **options):
        course = Course.objects.get(pk=options['course_id'])
        school = course.school

        for row in csv.reader(options['csv_file']):
            try:
                names = row[0].split()
                email = row[1]
            except IndexError:
                self.stderr.write("Malformed row. Skipping")

            try:
                user = CustomUser.objects.get(
                    email__iexact=CustomUser.objects.normalize_email(email)
                )
                student = user.student
            except CustomUser.DoesNotExist:
                self.stdout.write("Could not find student {}".format(email))
                new_user = True
                password = CustomUser.objects.make_random_password()
                user = CustomUser.objects.create_user(email, password)
                user.first_name = names[0]
                user.last_name = names[-1]
                user.save()
                try:
                    student = Student.objects.get(user=user)
                except Student.DoesNotExist:
                    student = Student.objects.create(user=user, school=school)
                else:
                    student.school = school
                    student.save()

                try:
                    self.notify_account(user, course)
                except Exception:
                    self.stderr.write("Failed to send email")
            else:
                self.stdout.write("Found student {}".format(email))
                new_user = False

            ta_job, changed = TA.objects.get_or_create(student=student, course=course)
            ta_job.active = True
            ta_job.save()

            if changed and not new_user:
                notify(student.user, student.ta_jobs.all())
