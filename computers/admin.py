from django.conf.urls import patterns
from django.contrib import admin
from django.http import HttpResponse
from .models import Lab, Computer, RoomInfo, CourseUsageInfo

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    pass

admin.site.register(Computer)
admin.site.register(RoomInfo)
admin.site.register(CourseUsageInfo)
