import logging
import requests
import json

from django.template.loader import get_template
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
redis_broadcast_publisher = RedisPublisher(facility='ta', broadcast=True)

logger = logging.getLogger(__name__)


class InvalidCourseStringError(ValueError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        msg = 'Course Strings must contain a number. You gave {}'
        return msg.format(self.value)


def notify(user, courses):
    subject = 'Halligan Helper TA Status'

    if courses:
        plaintext = get_template('tas/email/ta_activation.txt')
        htmly = get_template('tas/email/ta_activation.html')
    else:
        plaintext = get_template('tas/email/remove_ta.txt')
        htmly = get_template('tas/email/remove_ta.html')

    d = {'user': user, 'courses': courses}
    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    user.email_user(subject, text_content, html_message=html_content)


def _get_ta_courses(user):
    """Returns a QuerySet of Course objects representing which courses a user
    is a TA for.
    """
    from tas.models import Course

    # Because apparently having an '@' in the email gives a 403 back from Tufts
    email = user.email.replace('@', ':')
    url = "http://www.cs.tufts.edu/~molay/compta/isata.cgi/{0}"
    r = requests.get(url.format(email))

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception(
            'Failed to get courses from %s for user %s',
            url.format(email),
            user.email
        )
        return Course.objects.none()

    course_strings = r.text.strip()

    logger.info(
        'Got TA status for user. user="%s" courses="%s"',
        user.email,
        course_strings
    )

    if course_strings == 'NONE':
        return Course.objects.none()

    # Create query objects. Basically means create a bunch of objects that
    # say "number=number AND postfix=postfix"
    #
    # Q objects:
    # https://docs.djangoproject.com/es/1.9/topics/db/queries/#complex-lookups-with-q-objects
    #
    # OR all of the created Q objects together
    # (number=11 AND postfix='') OR (number=150 AND postfix='IDS')
    course_query = Q()
    course_strings = course_strings.split(' ')
    for course_string in course_strings:
        number, postfix = _split_course_string(course_string)
        q_obj = Q(number=number) & Q(postfix__iexact=postfix)
        course_query |= q_obj

    # Run the query to get the courses
    courses = Course.objects.filter(course_query)

    if courses.count() != len(course_strings):
        logger.warning(
            'User %s is TA for courses not in our database. '
            'their_courses="%s" our_courses="%s"',
            user.email,
            course_strings,
            ' '.join(
                map(lambda x: '{}{}'.format(x.number, x.postfix), courses)
            )
        )

    return courses


def check_ta(user):
    """
        Get the users current TA jobs
        If the user is marked as a TA for a course not in that list, remove the mark
        If the user is not marked as a TA for a course in that list, add the mark

        return true if a ta, false otherwise
    """
    from tas.models import TA

    student = user.student

    courses = _get_ta_courses(user)
    new_course_list = map(str, courses)

    try:
        old_course_list = map(str, student.ta_jobs.filter(ta__active=True))

        TA.objects.filter(student=student).update(active=False)
        for course in courses:
            ta_job, _ = TA.objects.get_or_create(
                student=student,
                course=course
            )
            ta_job.active = True
            ta_job.save()

        # Get any existing TA jobs that we didn't just add and deactivate them
        remove_jobs = (
            TA.objects.filter(student=student).exclude(course__in=courses)
        )
        remove_jobs.update(active=False)

        # Don't notify students whose course lists haven't changed.
        if old_course_list != new_course_list:
            notify(user, courses)
    except Exception:
        # Intentionally catch everything. If it failed, log and continue.
        logger.exception('Failed to set TA status for %s. Courses: %s',
                         user.email, new_course_list)
        return False

    return TA.objects.filter(student=student, active=True).exists()


def get_administrators_for_school(school):
    group_name = get_school_admin_group_name(school.name)
    user_model = get_user_model()
    group_admins = Group.objects\
        .prefetch_related('user_set').get(name=group_name).user_set.all()
    return group_admins | user_model.objects.filter(pk=school.administrator.pk)


def get_school_admin_group_name(school_name):
    return '{} Admins'.format(school_name)


def _split_course_string(course_string):
    """ Split the course string in to a course number and a course postfix
    Expects all strings to be in the format numpostfix. For instance,
    '50CP' and '150IDS' are valid. The postfix is allowed to be empty: '11' is
    a valid course string. The number, however, must be present: 'IDS' is not
    a valid course string. Only the first numbers are parsed as the course
    number: '11A7B12' will be parsed as course_num = 11, postfix = 'A7B12'

    :param str course_string: The course string to parse

    :returns: `(course_num, course_postfix)`

    :raises: InvalidCourseStringError
    """
    number = ''
    postfix = ''

    for index, char in enumerate(course_string):
        try:
            int(char)
            number += char
        except ValueError:
            postfix = course_string[index:]
            break

    if not number:
        logger.exception('Got an invalid course string: %s', course_string)
        raise InvalidCourseStringError(course_string)

    return number, postfix


def publish_message(message_type, data=None, publisher=None):
    redis_publisher = publisher
    if redis_publisher is None:
        redis_publisher = redis_broadcast_publisher

    packet = {
        'type': message_type
    }

    if data is not None:
        packet['data'] = data

    logger.debug('Publishing redis message. message="%s" '
                 'default_publisher="%s"',
                 packet, publisher is None)

    message = RedisMessage(json.dumps(packet))
    redis_publisher.publish_message(message)
