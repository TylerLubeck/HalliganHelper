__author__ = 'tyler'
from django.core.management.base import BaseCommand, CommandError
import requests
import csv
import datetime
from dateutil.parser import parse as date_parser
from computers.models import Lab


class Command(BaseCommand):
    args = 'none'
    help = 'Add semesters labs from Bruce Molay\'s online log'

    update_url = 'http://www.cs.tufts.edu/~molay/labs/times.cgi'

    time_ranges = {
        '8:30-10:20': (datetime.time(8, 30), datetime.time(10, 20)),
        '10:30-11:45': (datetime.time(10, 30), datetime.time(11, 45)),
        '12:00-1:15': (datetime.time(12, 00), datetime.time(13, 15)),
        '1:30-2:45': (datetime.time(13, 30), datetime.time(14, 45)),
        '3:00-4:15': (datetime.time(15, 00), datetime.time(16, 15)),
        '4:30-5:45': (datetime.time(16, 30), datetime.time(17, 45)),
        '6:00-7:15': (datetime.time(18, 00), datetime.time(19, 15)),
        '7:30-8:45': (datetime.time(19, 30), datetime.time(20, 45)),
        '9:00-10:15': (datetime.time(21, 00), datetime.time(22, 15))
    }

    def day_to_int(self, x):
        return {
            'Mon': 0,
            'Tue': 1,
            'Wed': 2,
            'Thu': 3,
            'Fri': 4,
            'Sat': 5,
            'Sun': 6,
        }.get(x, 0)

    def handle(self, *args, **options):
        start_msg = "Enter Start Date of Labs in format mm/dd/yyyy: "
        end_msg = "Enter End Date of Labs in format mm/dd/yyyy: "
        start_date_str = raw_input(start_msg)
        end_date_str = raw_input(end_msg)
        try:
            start_date = date_parser(start_date_str).date()
            end_date = date_parser(end_date_str).date()
        except ValueError:
            raise CommandError("Unable to parse date")

        msg = "Update labs between {} and {}: y/N? ".format(start_date,
                                                            end_date)
        confirm = raw_input(msg)

        if confirm.lower() not in ['y', 'yes']:
            raise CommandError("Didn't get 'yes', aborting")

        Lab.objects.filter(start_date=start_date, end_date=end_date).delete()

        data = requests.get(self.update_url)
        reader = csv.reader(data.content.split('\n'), delimiter='\t')

        for row in reader:
            # print row
            if len(row) != 3:
                continue
            course_name = row[2].split('|')[0]
            lab_info = row[0].split()
            room_num = int(lab_info[0])
            day_of_week = self.day_to_int(lab_info[1])
            time_range = self.time_ranges.get(lab_info[2], None)
            if time_range is None:
                msg = "Unable to parse time range {}".format(lab_info[2])
                raise CommandError(msg)

            Lab.objects.create(room_number=room_num,
                               course_name=course_name,
                               start_time=time_range[0],
                               end_time=time_range[1],
                               start_date=start_date,
                               end_date=end_date,
                               day_of_week=day_of_week)
