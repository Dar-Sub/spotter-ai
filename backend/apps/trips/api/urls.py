from django.urls import path

from .views import HealthView, TripDetailView, TripPlanView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("trips/plan/", TripPlanView.as_view(), name="trip-plan"),
    path("trips/<int:trip_id>/", TripDetailView.as_view(), name="trip-detail"),
]
