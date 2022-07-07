from django.test import (
    TestCase,
    Client
)
from django.urls import reverse
from rest_framework import status
from library.models import (
    Book,
    Statistics
)
from library.serializers import (
    BookViewSerializer,
    LibraryProgressModelSerializer
)
from users.models import User

CONTENT_TYPE_JSON_APPLICATION = 'application/json'
# Random book unique id
RANDOM_UUID = 'f0653e13-aa84-4632-8f59-cc47141ea8cd'

client = Client()


class TestLibraryModelViewSet(TestCase):
    """
    Testing POST   /api/v1/library
            GET    /api/v1/library?book_id&page
            DELETE /api/v1/library?book_id
    """

    def setUp(self) -> None:
        # Create two users with unique vk_id
        User.objects.create(vk_id=123123213)
        User.objects.create(vk_id=901283092)

        # Create few books linked to the first user
        Book.objects.create(vk_id=User.objects.get(vk_id=123123213),
                            title="Kafka on the Shore", author="Haruki Murakami", )
        Book.objects.create(vk_id=User.objects.get(vk_id=123123213),
                            title="The Old Man and the Sea", author="Ernest Hemingway", )
        Book.objects.create(vk_id=User.objects.get(vk_id=123123213),
                            title="The Trial", author="Kafka Franz", )

    def test_get(self):
        """Get book correctly"""

        book = Book.objects.all().first()
        book_serialization = BookViewSerializer(book)
        response = client.get(reverse('api_library:library_list_control'), data={'book_id': book.unique_id, 'page': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, book_serialization.data)

    def test_get_wrong_book_id(self):
        """Get book with non-existing book_id param"""

        response = client.get(reverse('api_library:library_list_control'), data={'book_id': RANDOM_UUID, 'page': 1})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_wrong_page(self):
        """Get book with either too-small or too-big page number."""

        response = client.get(reverse('api_library:library_list_control'), data={'book_id': RANDOM_UUID, 'page': -1})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_enough_params(self):
        """Send request without one of the params: book_id/page"""

        book = Book.objects.all().first()
        response = client.get(reverse('api_library:library_list_control'), data={'book_id': book.unique_id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = client.get(reverse('api_library:library_list_control'), data={'page': 1})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post(self):
        """Send book correctly"""

        with open('library/test/test_files/accessible_epub_3.epub', 'rb') as file:
            request = client.post(reverse('api_library:library_list_control'), data={'vk_id': 123123213, 'file': file})

        # Get the book we just uploaded
        book = Book.objects.all().filter(vk_id=User.objects.get(vk_id=123123213)).last()

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.vk_id, User.objects.get(vk_id=123123213))
        self.assertTrue(book.file)

    def test_post_wrong_vk_id(self):
        """Send book with non-existing vk_id param"""

        with open('library/test/test_files/accessible_epub_3.epub', 'rb') as file:
            request = client.post(reverse('api_library:library_list_control'), data={'vk_id': 123, 'file': file})

        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_empty_file(self):
        """Send book with an empty file"""

        request = client.post(reverse('api_library:library_list_control'), data={'vk_id': 123, 'file': ''})
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete(self):
        """Delete book correctly"""

        book = Book.objects.all().last()
        book_id = book.unique_id

        request = client.delete(reverse('api_library:library_list_control'),
                                content_type=CONTENT_TYPE_JSON_APPLICATION,
                                data={'book_id': book_id})

        self.assertEqual(request.status_code, status.HTTP_200_OK)

        response = client.get(reverse('api_library:library_list_control'), data={'book_id': book_id, 'page': 1})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_wrong_book_id(self):
        """Delete book with wrong book_id"""

        request = client.delete(reverse('api_library:library_list_control'),
                                content_type=CONTENT_TYPE_JSON_APPLICATION,
                                data={'book_id': RANDOM_UUID})

        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)


class TestStatisticsModelViewSet(TestCase):
    def setUp(self) -> None:
        # Create two users with unique vk_id
        User.objects.create(vk_id=123123213)
        User.objects.create(vk_id=901283092)

        # Create few books linked to the first user
        Book.objects.create(vk_id=User.objects.get(vk_id=123123213),
                            title="Kafka on the Shore", author="Haruki Murakami", )
        Book.objects.create(vk_id=User.objects.get(vk_id=123123213),
                            title="The Old Man and the Sea", author="Ernest Hemingway", )
        Book.objects.create(vk_id=User.objects.get(vk_id=123123213),
                            title="The Trial", author="Kafka Franz", )

        Statistics.objects.create(book_id=Book.objects.all().last(),
                                  percentage=1, pages_read=1, words_read=1,
                                  average_speed=1)

    def test_update_clean_stat(self):
        """Update book stat, when stat is unset"""
        book = Book.objects.all().last()
        data = {
            'book_id': book.unique_id,
            'vk_id': book.vk_id_id,
            'pages': 1,
            'words': 1,
            'average_speed': 1
        }
        request = client.put(reverse('api_library:library_stat_control'),
                             content_type=CONTENT_TYPE_JSON_APPLICATION,
                             data=data)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_update_stat(self):
        """Update book stat"""
        book = Book.objects.all().last()
        data = {
            'book_id': book.unique_id,
            'vk_id': book.vk_id_id,
            'pages': 1,
            'words': 1,
            'average_speed': 1
        }
        request = client.put(reverse('api_library:library_stat_control'),
                             content_type=CONTENT_TYPE_JSON_APPLICATION,
                             data=data)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_update_wrong_book_id(self):
        """Update book stat with a wrong book_id"""
        data = {
            'book_id': RANDOM_UUID,
            'vk_id': 901283092,  # VK_ID may be random here as well
            'pages': 1,
            'words': 1,
            'average_speed': 1
        }
        request = client.put(reverse('api_library:library_stat_control'),
                             content_type=CONTENT_TYPE_JSON_APPLICATION,
                             data=data)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_get_stat(self):
        """Get all the user stat"""
        user_stat = Statistics.objects.all().first()
        vk_id = Book.objects.all().filter(unique_id=user_stat.book_id.unique_id).first().vk_id_id
        user_stat_serialized = LibraryProgressModelSerializer(user_stat)

        request = client.get(reverse('api_library:library_stat_control'),
                             content_type=CONTENT_TYPE_JSON_APPLICATION,
                             data={'vk_id': vk_id})
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, user_stat_serialized.data)

    def test_get_specific_stat(self):
        """Get book stat by book_id"""
        user_stat = Statistics.objects.all().first()
        vk_id = Book.objects.all().filter(unique_id=user_stat.book_id.unique_id).first().vk_id_id
        book_id = user_stat.book_id.unique_id
        user_stat_serialized = LibraryProgressModelSerializer(user_stat)

        request = client.get(reverse('api_library:library_stat_control'),
                             content_type=CONTENT_TYPE_JSON_APPLICATION,
                             data={'vk_id': vk_id, 'book_id': book_id})
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.data, user_stat_serialized.data)

    def test_get_wrong_stat(self):
        """Get book stat with wrong book_id"""
        user_stat = Statistics.objects.all().first()
        vk_id = Book.objects.all().filter(unique_id=user_stat.book_id.unique_id).first().vk_id_id
        user_stat_serialized = LibraryProgressModelSerializer(user_stat)

        request = client.get(reverse('api_library:library_stat_control'),
                             content_type=CONTENT_TYPE_JSON_APPLICATION,
                             data={'vk_id': vk_id, 'book_id': RANDOM_UUID})
        self.assertEqual(request.status_code, status.HTTP_204_NO_CONTENT)
