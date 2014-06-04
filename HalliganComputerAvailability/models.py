from django.db import models
from datetime import datetime
import datetime as dt
from django.contrib import admin
import pytz
from django.conf import settings

# Create your models here.


def _now():
    tz = pytz.timezone(settings.TIME_ZONE)
    now = dt.datetime.now(tz=tz)
    return now


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
    ComputerNumber = models.CharField(max_length=7,
                                      primary_key=True)
    RoomNumber = models.IntegerField()
    Status = models.CharField(max_length=9,
                              choices=STATUS_CHOICES,
                              default=AVAILABLE)
    used_for = models.CharField(max_length=40, null=True)
    LastUpdate = models.DateTimeField(auto_now=True)

    # TODO: Foreign Key to computers in TA System?
admin.site.register(Computer)


class RoomInfo(models.Model):
    lab = models.CharField(max_length=10)
    numReporting = models.IntegerField()
    num_available = models.IntegerField()
    num_unavailable = models.IntegerField()
    num_error = models.IntegerField()

    updateTime = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.updateTime = _now()
        return super(RoomInfo, self).save(*args, **kwargs)

    def __str__(self):
        format_str = '{5}: {0} has {1} machine(s) reporting: '
        format_str += '{2} available {3} unavailable and {4} broken'
        return format_str.format(self.lab, self.numReporting,
                                 self.num_available,
                                 self.num_unavailable,
                                 self.num_error, self.updateTime)
admin.site.register(RoomInfo)


class CourseUsageInfo(models.Model):
    room = models.ForeignKey(RoomInfo, related_name='cuis')
    course = models.CharField(max_length=20)
    num_machines = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.course is None:
            self.course = 'Other'
        return super(CourseUsageInfo, self).save(*args, **kwargs)

    def __str__(self):
        format_str = '{0} has {1} machine(s) in room {2}'
        return format_str.format(self.course, self.num_machines,
                                 self.room.lab)


class ComputerInfo(models.Model):
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

    def __init__(self, *args, **kwargs):
        super(models.Model, self).__init__(*args, **kwargs)
        print "\n\nDON'T ACTUALLY USE THIS MODEL: ComputerInfo\n\n"

    RoomNumber = models.IntegerField()
    ComputerNumber = models.CharField(max_length=7)
    Updated = models.DateTimeField(auto_now=True)
    ComputerStatus = models.CharField(max_length=10,
                                      choices=STATUS_CHOICES,
                                      default=AVAILABLE)


class Server(models.Model):
    OFF = 'OFF'
    ON = 'ON'
    ERROR = 'ERROR'

    CHOICES = [OFF, ON, ERROR]

    STATUS_CHOICES = (
        (OFF, 'Off'),
        (ON, 'On'),
        (ERROR, 'Error')
    )

    ComputerName = models.CharField(max_length=20,
                                    primary_key=True)
    NumUsers = models.IntegerField()

    Status = models.CharField(max_length=40,
                              choices=STATUS_CHOICES,
                              default=ON)

    LastUpdated = models.DateTimeField(auto_now=True)

admin.site.register(Server)


class ServerInfo(models.Model):
    ComputerName = models.CharField(max_length=20)
    Updated = models.DateTimeField(auto_now=True)
    NumUsers = models.IntegerField()


class Lab(models.Model):
    ClassName = models.CharField(max_length=30)
    RoomNumber = models.IntegerField()
    StartTime = models.TimeField()
    EndTime = models.TimeField()
    StartDate = models.DateField()
    EndDate = models.DateField()
    DayOfWeek = models.IntegerField(max_length=1)

    def for_response(self):
        response = {
            'ClassName': self.ClassName,
            'RoomNumber': self.RoomNumber,
            'StartTime': self.StartTime.strftime('%I:%M %p'),
            'EndTime': self.EndTime.strftime('%I:%M %p'),
            'DayOfWeek': self.day_of_week(),
            'InSession': self.is_lab_in_session(),
            'ComingUp': self.is_lab_coming_up(),
            'DayOfWeek_AsNum': self.DayOfWeek
        }
        return response

    def day_of_week(self, short_name=False):
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
            return long(self.DayOfWeek)[0:3]
        else:
            return long(self.DayOfWeek)

    def is_lab_in_session(self):
        """
        Returns whether a lab is currently in session
        """
        CurrTime = datetime.now().time()
        CurrDate = datetime.now().date()
        CurrDay = datetime.now().weekday()

        if(self.StartDate < CurrDate < self.EndDate
           and self.StartTime < CurrTime < self.EndTime
           and self.DayOfWeek == CurrDay):
            return True

        return False

    def is_lab_coming_up(self):
        """
         Returns whether the lab occurs within the next 3 hours
        """

        CurrTime = datetime.now().time()
        CurrDate = datetime.now().date()
        CurrDay = datetime.now().weekday()
        delta = dt.timedelta(hours=3)
        start_time = dt.date(10, 10, 10)
        combined = datetime.combine(start_time, self.StartTime)

        ModdedStartTime = (combined - delta).time()

        if(self.StartDate < CurrDate < self.EndDate
            and self.DayOfWeek == CurrDay
            and self.EndTime > CurrTime > ModdedStartTime
                and not self.is_lab_in_session()):

                return True

        return False

admin.site.register(Lab)
