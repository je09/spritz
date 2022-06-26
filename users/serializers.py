from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    vk_id = serializers.IntegerField()
    books_id = serializers.StringRelatedField(many=True)

    # TODO: Return forbidden status code if vk_id is not set.

    class Meta:
        model = User
        fields = ('vk_id', 'books_id')
