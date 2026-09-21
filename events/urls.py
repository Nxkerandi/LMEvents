from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.events_list_view, name="events_list"),
    path("preparing-the-home-for-home/", views.initial_page_view, name="initial_page"),
    path("preparing-the-home-for-home/dashboard/", views.combined_dashboard_view, name="combined_dashboard"),
    path("registrations/<int:registration_id>/edit/", views.edit_registration_view, name="edit_registration"),
    path("registrations/<int:registration_id>/cancel/", views.cancel_registration_view, name="cancel_registration"),
    path("registrations/<int:registration_id>/restore/", views.restore_registration_view, name="restore_registration"),
    path("<slug:slug>/", views.registration_view, name="register"),
]
