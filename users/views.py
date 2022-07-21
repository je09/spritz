from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import exceptions
from users.serializers import UserSerializer
from users.models import User


class UserListAPIView(RetrieveAPIView):
    """
    Returns books ID of user with given vk_id

    * If user didn't upload any books result will be empty
    """
    authentication_classes = []
    permission_classes = []

    allowed_methods = ['GET']
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `vk_id` query parameter in the URL.
        """

        vk_id = request.META.get('vk_user_id')
        self.queryset.filter(vk_id=vk_id)
        if not self.queryset.filter(vk_id=vk_id).exists():
            raise exceptions.NotFound

        serializer = UserSerializer(self.queryset.filter(vk_id=vk_id).first())
        return Response(serializer.data)
