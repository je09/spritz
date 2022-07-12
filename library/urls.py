from django.urls import path, include
from library.views import (
    LibraryRetrieveViewSet,
    StatisticsViewSet,
)

app_name = 'api_library'
urlpatterns = [
    path('', LibraryRetrieveViewSet.as_view(), name='library_list_control'),
    path('progress/', StatisticsViewSet.as_view(), name='library_stat_control'),
]
