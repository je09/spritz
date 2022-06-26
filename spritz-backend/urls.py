from django.contrib import admin
from django.urls import path, include


api_v1_urls = [
    path('users/', include('users.urls')),
    path('library/', include('library.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_urls)),
]
