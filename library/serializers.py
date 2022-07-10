from rest_framework import serializers
from library.models import Book
from library.services import EpubParser


class BookViewSerializer(serializers.ModelSerializer):
    """
    Serializer for EPUB-Books representation from ORM
    """
    text = serializers.SerializerMethodField('get_text', read_only=True)
    page = serializers.SerializerMethodField('get_page', read_only=True)

    def get_text(self, obj) -> str:
        """Get book text by page from EPUB file"""
        # There should be caching and file reading running under Celery
        return "mockup"

    def get_page(self, obj) -> int:
        """Get page from request"""
        return obj.pk

    class Meta:
        model = Book
        fields = ('vk_id', 'unique_id', 'author', 'title', 'page', 'text')
        extra_kwargs = {
            'vk_id': {'read_only': True},
            'text': {'read_only': True},
            'page': {'read_only': True},
            'author': {'read_only': True},
            'title': {'read_only': True},
        }


class BookCreateSerializer(serializers.ModelSerializer):
    """
    Deserializer for user requested EPUB-book

    Get requested vk_id and file, parse the file to fill:
    • title
    • author
    Set unique_id automatically.
    """

    file = serializers.FileField(required=True)
    title = serializers.CharField(max_length=256)
    author = serializers.CharField(max_length=256)

    def to_internal_value(self, data):
        if 'file' not in data:
            return super().to_internal_value(data)

        if data['file'].content_type == 'application/epub+zip':
            path = data['file'].temporary_file_path()
            book = EpubParser(path, parse_text=False)
            data['title'] = book.title
            data['author'] = book.author

        return super().to_internal_value(data)

    class Meta:
        model = Book
        fields = ('unique_id', 'vk_id', 'file', 'title', 'author')
        extra_kwargs = {
            'file': {'write_only': True},
            'vk_id': {'write_only': True},
            'unique_id': {'read_only': True},
            'title': {'read_only': True},
            'author': {'read_only': True},
        }

class LibraryProgressModelSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ()
