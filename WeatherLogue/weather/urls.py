from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path("location/", views.location, name="location"),
    path("find-location", views.find_location, name="find-location"),
    path("forecast/", views.forecast, name="forecast"),
    path("history/", views.history, name="history"),
    path("location-history/<int:location_id>/", views.location_history, name="location_history")
]