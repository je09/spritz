from django.urls import path, include
from rest_framework import routers
from users.views import UserListAPIView

app_name = 'api_user'
urlpatterns = [
    path('', UserListAPIView.as_view(), name='user info'),
]
