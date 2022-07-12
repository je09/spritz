from django.db.models import (
    Q
)
from rest_framework.generics import (
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from library.serializers import (
    BookViewSerializer,
    BookCreateSerializer,
    LibraryProgressModelSerializer,
    LibraryAvgProgressBaseSerializer
)
from users.models import User
from library.models import (
    Book,
    Statistics
)


class LibraryRetrieveViewSet(
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView
):
    """
    View to control user book-library

    GET book details by book_id and text by page
    POST user_id and file
    DELETE by book_id
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = BookViewSerializer

    allowed_methods = ('GET', 'POST', 'DELETE')

    def get(self, request: Request, *args, **kwargs):
        """Get book details and text by submitting book_id and page"""
        # Can't use values() or items() because params might not be in request.
        # TODO: add vk_id to make sure the right params are sent
        # TODO: Check for valid type
        # TODO: move logic to serializer. use BaseSerializer if required.
        book_id, page = request.query_params.get('book_id'), request.query_params.get('page')
        if not book_id or not page:
            return Response(BookViewSerializer(None).data, status=status.HTTP_400_BAD_REQUEST)

        queryset = Book.objects.all().filter(unique_id=book_id)
        if not queryset.exists():
            return Response(BookViewSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        serializer = BookViewSerializer(queryset.first(), partial=True, context={'page': page})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Send user vk_id and book file"""
        vk_id = request.data.get('vk_id')
        user = User.objects.filter(vk_id=vk_id)

        if not user.exists():
            user = User.objects.create(vk_id=vk_id)
            user.save()

        book_serialized = BookCreateSerializer(data=request.data)
        if not book_serialized.is_valid():
            return Response(BookViewSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        book_serialized.save()

        return Response(book_serialized.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, *args, **kwargs):
        """Delete book by book_id"""
        # TODO: add vk_id to make sure the right params are sent
        book_id = request.data.get('book_id')
        if not book_id:
            return Response(BookViewSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        book = Book.objects.all().filter(unique_id=book_id)
        if not book:
            return Response(BookViewSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        book.delete()
        return Response(BookViewSerializer(None).data, status=status.HTTP_200_OK)


class StatisticsViewSet(
    RetrieveAPIView,
    UpdateAPIView
):
    """
    User statistics

    GET – get all the user stat: pages read, words read, average speed reed
    GET with book_id param – get stat about specific book
    PUT with book_id - update stat about specific book
    """
    def get(self, request: Request, *args, **kwargs):
        vk_id = request.query_params.get('vk_id')
        if not vk_id:
            return Response(LibraryProgressModelSerializer(None).data,
                            status=status.HTTP_204_NO_CONTENT)

        book_id = request.query_params.get('book_id')
        if not book_id:
            # return average stat of user reading
            return Response(LibraryAvgProgressBaseSerializer(request.query_params).data)

        # TODO: serializer validation. error during invalid token.
        # check if the book really belongs to the user
        book = Book.objects.all().filter(Q(vk_id=vk_id) & Q(unique_id=book_id))
        if not book.exists():
            return Response(LibraryProgressModelSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        stat = Statistics.objects.all().filter(book_id=book.first()).first()

        return Response(LibraryProgressModelSerializer(stat).data)

    def put(self, request, *args, **kwargs):
        # TODO: Doesn't work, fix late. Update tests.
        vk_id, book_id = request.data.get('vk_id'), request.data.get('book_id')
        if not vk_id or not book_id:
            return Response(LibraryProgressModelSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        stat_serialized = LibraryProgressModelSerializer(data=request.data)
        if not stat_serialized.is_valid():
            return Response(LibraryProgressModelSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        stat_serialized.save()

        return Response(stat_serialized.data, status=status.HTTP_200_OK)
