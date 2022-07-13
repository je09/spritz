from rest_framework import serializers
from users.models import User
from library.serializers import BookViewSerializer


class UserSerializer(serializers.ModelSerializer):
    vk_id = serializers.IntegerField()
    books = BookViewSerializer(many=True, read_only=True)

    # TODO: Return forbidden status code if vk_id is not set.

    class Meta:
        model = User
        fields = ('vk_id', 'books')
