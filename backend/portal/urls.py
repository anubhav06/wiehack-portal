from django.urls import path

from . import views 

urlpatterns = [
    path('', views.index, name="index"),
    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("submission", views.submission, name="submission"),
    path("judge-dashboard", views.judge_index, name="judge_index")
]