from django.urls import path, include
from library.views import (
    LibraryRetrieveViewSet,
)

app_name = 'api_library'
urlpatterns = [
    path('', LibraryRetrieveViewSet.as_view(), name='library_list_control'),
]
