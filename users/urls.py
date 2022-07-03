from django.urls import path
from users.views import UserListAPIView

app_name = 'api_user'
urlpatterns = [
    path('', UserListAPIView.as_view(), name='user_info'),
]
