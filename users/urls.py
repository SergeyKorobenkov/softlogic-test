from .views import UserCreate, LoginView
from django.urls import path, include

app_name = 'users'


urlpatterns = [
    path("signup/", UserCreate.as_view(), name="user_create"),
    path("login/", LoginView.as_view(), name="login"),
]