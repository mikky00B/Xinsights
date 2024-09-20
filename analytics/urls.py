from django.urls import path
from . import views

urlpatterns = [
    path("testing/<str:username>/", views.fetch_twitter_data, name="trigger_task"),
    path(
        "check-task-status/<str:task_id>/",
        views.check_task_status_view,
        name="check_task_status",
    ),
    path("", views.home),
]
