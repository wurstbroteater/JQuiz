"""
URL configuration for JQuiz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from quiz import views

app_name = "quiz"

user_mgmt_patterns = [
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("change-password/", auth_views.PasswordChangeView.as_view()),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

quiz_patterns = [
    path('quiz/', views.quiz_overview, name='quiz_overview'),
    path('quiz/<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    path('quiz/<int:turn_id>/question/<int:question_id>/', views.question_view, name='question'),
    path('quiz/<int:turn_id>/results/', views.results_view, name='results'),
    path('quiz/leaderboard/', views.leaderboard_overall_view, name='leaderboard'),
    path('quiz/<int:quiz_id>/leaderboard/', views.leaderboard_quiz_view, name='leaderboard_quiz'),
]
urlpatterns = user_mgmt_patterns + quiz_patterns + [
    path('admin/', admin.site.urls),
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path('report_problem/', views.report_problem, name='report_problem'),
]
