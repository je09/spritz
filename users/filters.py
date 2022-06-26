from django_filters import FilterSet
from users.models import User


class UserFilter(FilterSet):
    strict = True

    class Meta:
        model = User
        fields = ('vk_id', 'books_id',)
