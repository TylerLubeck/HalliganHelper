import logging
import hashlib

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

from .custom_user import CustomUser
from .utils import get_school_admin_group_name

logger = logging.getLogger(__name__)


def not_empty_string(value):
    """ Validate that a string is not empty.
    Raises a ValidationError if a string is empty, returns None otherwise.
    """
    if len(value) == 0:
        raise ValidationError("No value for field")


class School(models.Model):
    # TODO: Make a custom Manager method to get all administrators
    #       This direct one, plus all from the group
    name = models.CharField(max_length=255, unique=True)
    administrator = models.OneToOneField(settings.AUTH_USER_MODEL)
    date_created = models.DateTimeField(auto_now_add=True)
    max_course_count = models.IntegerField()

    def __str__(self):
        return self.name


@receiver(post_save, sender=School)
def create_school_admin_group(instance, created, **kwargs):
    if created:
        group_name = get_school_admin_group_name(instance.name)
        Group.objects.get_or_create(name=group_name)


class SchoolEmailDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    school = models.ForeignKey(School, related_name='valid_domains')

    def __str__(self):
        return '{} - {}'.format(self.school.name, self.domain)


class Course(models.Model):
    """ A Course is the representation of an academic course.
        Requests and TAs are associated with courses.
    """
    class Meta:
        ordering = ['department', 'number']

    school = models.ForeignKey(School, related_name='courses')
    name = models.CharField(max_length=100,
                            help_text='The name of the course')
    department = models.CharField(max_length=50,
                                  help_text='The department the course '
                                            'belongs to')
    number = models.IntegerField(help_text='The identifying course number')

    postfix = models.CharField(max_length=20,
                               blank=True,
                               default='',
                               help_text='The CP of COMP 150CP')
    date_created = models.DateTimeField(auto_now_add=True)
    request_time_to_live = models.IntegerField(
        default=3,
        help_text='The time until a request for a course times out'
    )

    def get_identifier(self):
        return '{} {}{}'.format(self.department.title(),
                                self.number,
                                self.postfix)

    def __str__(self):
        return '{}: {}'.format(self.school.name, self.name)


def determine_headshot_name(student, filename):
    data = {
        'email': student.user.email,
        'user_pk': student.user.pk
    }
    hash_string = '{email}-{user_pk}-headshot'.format(**data)

    return 'headshots/{}'.format(hashlib.sha224(hash_string).hexdigest())


class Student(models.Model):
    """ A Student is the base user class for the application.
        Every User object has a Student associated with it, and these Students
        are created when the user is registered.
    """
    default_image = 'blank/blank.jpg'
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    school = models.ForeignKey(School)

    # TODO: Make sure these are process properly. Size, naming, etc
    headshot = ProcessedImageField(upload_to=determine_headshot_name,
                                   default=default_image,
                                   help_text='A headshot of the user',
                                   processors=[ResizeToFit(width=100,
                                                           height=100)]
                                   )

    # Both of these will have to be limited to only allow Courses within the
    # same school
    courses = models.ManyToManyField(Course,
                                     related_name='students',
                                     blank=True,
                                     help_text='The courses a student is '
                                               'registered for.')

    ta_jobs = models.ManyToManyField(Course,
                                     through='TA',
                                     related_name='tas',
                                     help_text='The courses a '
                                               'student TAs for.')

    blurb = models.CharField(max_length=255,
                             help_text="A field for TA bios")

    def __str__(self):
        return self.user.get_full_name()

    def __repr__(self):
        return '<Student ({}) at {}>'.format(self.user.get_full_name(),
                                             id(self))


@receiver(post_save, sender=CustomUser)
def create_student_profile_for_user(instance, created, **kwargs):
    if created:
        domain = instance.email.split('@')[-1]
        try:
            sed = SchoolEmailDomain.objects.get(domain=domain)
            Student.objects.get_or_create(user=instance, school=sed.school)

        except SchoolEmailDomain.DoesNotExist:
            logger.error('Tried to create a student for the '
                         'non existent email domain: %s', domain)


class TA(models.Model):
    """ A representation of TA.
        TAs have the ability to resolve requests and are
        associated with a specific User
    """
    class Meta:
        verbose_name = "Teacher's Assistant"
        verbose_name_plural = "Teacher's Assistants"

    student = models.ForeignKey(Student)
    course = models.ForeignKey(Course)
    active = models.BooleanField(default=True,
                                 help_text='Whether or not the TA '
                                           'is currently active')

    def __str__(self):
        return 'TA: {}'.format(self.student.user.get_full_name())

    def __repr__(self):
        return '<TA ({}) at 0x{}>'.format(self.student.user.get_full_name(),
                                          id(self))


class Request(models.Model):
    """ Requests are the corner stone of this whole shebang.
        They keep track of when a Student requests a TA for a course
    """
    # Required Relations
    course = models.ForeignKey(Course,
                               help_text='The course the request is for')
    requestor = models.ForeignKey(Student,
                                  related_name='requests',
                                  help_text='The student who made the request')

    # Request Information
    when_asked = models.DateTimeField(auto_now_add=True,
                                      help_text='When the request was made')
    question = models.CharField(max_length=51,
                                validators=[not_empty_string],
                                help_text='The question associated '
                                          'with the request')
    where_located = models.CharField(max_length=50,
                                     validators=[not_empty_string],
                                     help_text='Where the user is located')

    # Information about being solved
    cancelled = models.BooleanField(default=False,
                                    help_text='Did the student '
                                              'cancel the request?')
    checked_out = models.BooleanField(default=False,
                                      help_text='Has a TA started working '
                                                'on the request?')
    solved = models.BooleanField(default=False,
                                 help_text='Has the request been resolved?')
    when_solved = models.DateTimeField(blank=True, null=True,
                                       help_text='When the request '
                                                 'was resolved')
    who_solved = models.ForeignKey(Student,
                                   related_name='requests_solved',
                                   null=True,
                                   blank=True,
                                   help_text='The TA who resolved the request')
    expired = models.BooleanField(default=False,
                                  help_text='If the request expired')
    expired_at = models.DateTimeField(blank=True, null=True,
                                      help_text='When the request was marked '
                                      'as expired')

    def __str__(self):
        return '{0} - Comp {1}'.format(self.requestor.user.get_full_name(),
                                       self.course.number)


class OfficeHour(models.Model):
    """The representation of an office hour.
    It's associated with a course and a TA
    """
    start_time = models.DateTimeField(auto_now_add=True,
                                      help_text='When the TA went on duty')
    end_time = models.DateTimeField(help_text='When the TA goes off duty')
    course = models.ForeignKey(Course,
                               help_text='The course this OfficeHour '
                                         'is associated with')
    ta = models.ForeignKey(Student,
                           help_text='The TA on duty')
    location = models.CharField(max_length=255,
                                help_text='The home base of the TA')
