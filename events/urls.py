from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.events_list_view, name="events_list"),
    path("<slug:slug>/duplicate/", views.duplicate_event_view, name="duplicate_event"),
    path("<slug:slug>/", views.registration_view, name="register"),
    path("<slug:slug>/dashboard/", views.dashboard_view, name="dashboard"),
    path("<slug:slug>/dashboard/export.csv", views.export_csv_view, name="export_csv"),
]
