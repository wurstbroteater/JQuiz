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
from django.urls import path
from django.contrib.auth import views as auth_views

from quiz import views

app_name = "quiz"

quiz_patterns = [
    path('quiz/<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    path('quiz/<int:turn_id>/question/<int:question_id>/', views.question_view, name='question'),
    path('quiz/<int:turn_id>/results/', views.results_view, name='results'),
]
urlpatterns = quiz_patterns + [
    path('admin/', admin.site.urls),
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path('quiz/<int:quiz_id>/leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('quiz/', views.quiz_overview, name='quiz_overview'),

    path('login/', auth_views.LoginView.as_view(template_name='quiz/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('report_problem/<int:question_id>/', views.report_problem, name='report_problem'),
    path('problem_reported/', views.problem_reported, name='problem_reported'),
]
