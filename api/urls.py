from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )
from rest_framework.routers import DefaultRouter


from . import views


app_name = 'api'

urlpatterns = [
    path('api/v1/persons/', views.GetAll.as_view()),
    path('api/v1/persons/compare/', views.CompareVectors.as_view()),
    path('api/v1/persons/<person_id>/', views.GetInfoOrDelete.as_view()),
    
]