from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views
from .views import SignUpView

urlpatterns = [
    # TODO: Django already provides some mechanism for account management in /accounts. Maybe its possible to reuse it.
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", views.profile, name='profile'),
    path("profile/update_email/", views.update_email, name='update_email'),
    path("profile/delete_account/", views.delete_account, name='delete_account'),
    path("change-password/", auth_views.PasswordChangeView.as_view(), name='change_password'),
    path("profile/leaderboard/", views.delete_account, name='leaderboard_personal'),
]
