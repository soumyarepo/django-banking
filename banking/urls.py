from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "transfer/",
        views.transfer_money,
        name="transfer",
    ),
    path(
        "health/",
        views.health_check,
        name="health",
    ),
]