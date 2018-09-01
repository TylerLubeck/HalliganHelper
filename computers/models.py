from django.db import models
import datetime as dt
from django.contrib import admin
from django.utils.timezone import now


class Computer(models.Model):
    OFF = 'OFF'
    INUSE = 'INUSE'
    AVAILABLE = 'AVAILABLE'
    ERROR = 'ERROR'

    CHOICES = [OFF, INUSE, AVAILABLE, ERROR]

    STATUS_CHOICES = (
        (OFF, 'Off'),
        (INUSE, 'In Use'),
        (AVAILABLE, 'Available'),
        (ERROR, 'Error')
    )
    number = models.CharField(max_length=7,
                              primary_key=True)
    room_number = models.IntegerField()
    status = models.CharField(max_length=9,
                              choices=STATUS_CHOICES,
                              default=AVAILABLE)
    used_for = models.CharField(max_length=40, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.number)

    def __repr__(self):
        return self.__str__()


class RoomInfo(models.Model):
    lab = models.CharField(max_length=10)
    num_reporting = models.IntegerField()
    num_available = models.IntegerField()
    num_unavailable = models.IntegerField()
    num_error = models.IntegerField()

    last_updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.last_updated = now()
        return super(RoomInfo, self).save(*args, **kwargs)

    def __str__(self):
        format_str = '{5}: {0} has {1} machine(s) reporting: '
        format_str += '{2} available {3} unavailable and {4} broken'
        return format_str.format(self.lab, self.num_reporting,
                                 self.num_available,
                                 self.num_unavailable,
                                 self.num_error, self.last_updated)


class CourseUsageInfo(models.Model):
    room = models.ForeignKey(RoomInfo, related_name='cuis')
    course = models.CharField(max_length=20)
    num_machines = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.pk is None and self.course == '':
            self.course = 'other'
        return super(CourseUsageInfo, self).save(*args, **kwargs)

    def __str__(self):
        format_str = '{0} has {1} machine(s) in room {2}'
        return format_str.format(self.course, self.num_machines,
                                 self.room.lab)

    def __repr__(self):
        return self.__str__()


class Lab(models.Model):
    course_name = models.CharField(max_length=30)
    room_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    day_of_week = models.IntegerField(max_length=1)

    def __str__(self):
        return '{}: {} {:%I:%M%p}'.format(self.course_name,
                                          self.day_of_week_name(),
                                          self.start_time)


    def day_of_week_name(self, short_name=False):
        def long(x):
            return {
                0: 'Monday',
                1: 'Tuesday',
                2: 'Wednesday',
                3: 'Thursday',
                4: 'Friday',
                5: 'Saturday',
                6: 'Sunday'
            }[x]

        if short_name:
            return long(self.day_of_week)[0:3]
        else:
            return long(self.day_of_week)

    def is_lab_in_session(self):
        """
        Returns whether a lab is currently in session
        """
        # now = dt.datetime.now()
        _now = now()
        weekday_same = _now.weekday() == self.day_of_week
        time_within = self.start_time <= _now.time() <= self.end_time
        day_within = self.start_date <= _now.date() <= self.end_date

        if weekday_same and time_within and day_within:
            return True
        return False

    def is_lab_coming_up(self, within_hours=3):
        """
         Returns whether the lab occurs within the next 'within_hours' hours
        """

        _now = now()
        within_hours_delta = dt.timedelta(hours=within_hours)
        within_datetime = _now + within_hours_delta

        weekday_within = within_datetime.weekday() == self.day_of_week
        date_within = self.start_date <= within_datetime.date() <= self.end_date
        time_within = self.start_time <= within_datetime.time() <= self.end_time
        if date_within and time_within and weekday_within:
            return True

        return False
