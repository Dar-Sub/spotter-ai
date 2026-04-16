from django.contrib import admin

from apps.trips.models import DailyLog, DutySegment, RouteLeg, Stop, Trip

admin.site.register(Trip)
admin.site.register(RouteLeg)
admin.site.register(Stop)
admin.site.register(DutySegment)
admin.site.register(DailyLog)

# Register your models here.
