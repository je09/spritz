from rest_framework import serializers
from library.models import Book
from library.services import parse_book


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
        return 1

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

    def update(self, instance, validated_data):
        # TODO: Parse ebook
        pass

    class Meta:
        model = Book
        fields = ('vk_id', 'file')


class LibraryProgressModelSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ()
