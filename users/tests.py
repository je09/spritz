from django.test import (
    TestCase,
    Client
)
from django.urls import reverse
from rest_framework import status
from users.models import User
from users.serializers import UserSerializer
from library.models import Book

client = Client()


class TestUserListApiView(TestCase):
    """
    Testing GET of /api/v1/users/
    """

    def setUp(self) -> None:
        # Create two users with unique vk_id
        User.objects.create(vk_id=371449298)
        User.objects.create(vk_id=489302347)

        # Create user with an empty list of books
        User.objects.create(vk_id=123123123)

        # Create few books linked to the first user
        Book.objects.create(vk_id=User.objects.get(vk_id=371449298),
                            title="Kafka on the Shore", author="Haruki Murakami",
                            pages=500, words=229000, )
        Book.objects.create(vk_id=User.objects.get(vk_id=371449298),
                            title="The Old Man and the Sea", author="Ernest Hemingway",
                            pages=500, words=229000, )
        Book.objects.create(vk_id=User.objects.get(vk_id=371449298),
                            title="The Trial", author="Kafka Franz",
                            pages=500, words=229000, )

        # Create few book linked to the second user
        Book.objects.create(vk_id=User.objects.get(vk_id=489302347), title="Hyperion", author="Dan Simons",
                            pages=500, words=229000, )
        Book.objects.create(vk_id=User.objects.get(vk_id=489302347), title="Ubik", author="Philip K. Dick",
                            pages=500, words=229000, )
        Book.objects.create(vk_id=User.objects.get(vk_id=489302347),
                            title="Revelation Space", author="Reynolds Alastair",
                            pages=500, words=229000, )

    def test_get_users(self):
        # get data from API response with vk_id=371449298
        response = client.get(reverse('api_user:user_info'), data={'vk_id': 371449298})

        # get data from ORM
        clients = User.objects.get(vk_id=371449298)
        clients_serialized = UserSerializer(clients)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, clients_serialized.data)

    def test_get_empty_user(self):
        # get data from API response with vk_id=123123123
        response = client.get(reverse('api_user:user_info'), data={'vk_id': 123123123})

        # get data from ORM
        clients = User.objects.get(vk_id=123123123)
        clients_serialized = UserSerializer(clients)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, clients_serialized.data)

    def test_empty_args(self):
        response = client.get(reverse('api_user:user_info'))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
