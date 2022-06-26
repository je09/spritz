from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
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

    def get(self, request, *args, **kwargs):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `vk_id` query parameter in the URL.
        """
        vk_id = self.request.query_params.get('vk_id')
        # Prevent request to the ORM
        if not vk_id:
            return Response(UserSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        queryset = User.objects.get(vk_id=vk_id)
        return Response(UserSerializer(queryset).data)
