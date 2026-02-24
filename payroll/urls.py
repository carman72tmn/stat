from django.urls import path

from .views import dashboard_view, register_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("register/", register_view, name="register"),
]
