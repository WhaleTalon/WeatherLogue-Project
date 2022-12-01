from django.contrib import admin

from .models import Location, WeatherLog

admin.site.register(Location)
admin.site.register(WeatherLog)
