from rest_framework.generics import (
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView
)
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from library.serializers import (
    BookViewSerializer,
    LibraryProgressModelSerializer
)
from library.models import Book


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

    allowed_methods = ('GET', 'POST', 'DELETE')

    def get(self, request: Request, *args, **kwargs):
        """Get book details and text by submitting book_id and page"""
        # Can't use values() or items() because params might not be in request.
        # TODO: UUID error
        book_id, page = request.query_params.get('book_id'), request.query_params.get('page')
        if not book_id or not page:
            return Response(BookViewSerializer(None).data, status=status.HTTP_400_BAD_REQUEST)

        queryset = Book.objects.all().filter(unique_id=book_id)
        if not queryset.exists():
            return Response(BookViewSerializer(None).data, status=status.HTTP_204_NO_CONTENT)

        # TODO: Pagination and async magic in serializer.
        serializer = BookViewSerializer(queryset.first(), partial=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass
