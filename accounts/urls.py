from django.urls import path

from . import views


urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path("profile/delete/", views.delete_account_confirm, name="delete_account_confirm"),
    path("profile/delete/final/", views.delete_account_final, name="delete_account_final"),
]
