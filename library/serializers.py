import os.path
from django.db.models import (
    Avg,
    Q
)
from rest_framework import serializers
from library.models import (
    Book,
    Statistics
)
from library.services import EpubParser


EPUB_EXTENSION = 'application/epub+zip'


class BookViewSerializer(serializers.ModelSerializer):
    """
    Serializer for EPUB-Books representation from ORM
    """

    # TODO: make an error on to large page.
    text = serializers.CharField()
    page = serializers.IntegerField()
    pages = serializers.IntegerField()
    words = serializers.IntegerField()

    def to_representation(self, instance):
        # dirty hack! requires because book info should be operated from one place.
        # that is why serializers.SerializerMethodField can't be used in this case.
        # there is ma be a much better way of handling this task, if it is - rewrite this part in the future.
        instance.text, instance.page, instance.pages, instance.words = self.get_book_info(instance)

        return super().to_representation(instance)

    def get_book_info(self, data) -> (str, int, int, int):
        """Return text, page, pages, words"""
        text, page, pages, words = '', 0, 0, 0
        if not data.file:
            return text, page, pages, words

        _, extension = self._extension(data.file.path)
        page = int(self.context['page'])
        if extension == '.epub':
            book = EpubParser(data.file.path)
            text, words = book.get_page(page)
            pages = len(book)

        return text, page, pages, words


    def _extension(self, file_name):
        return os.path.splitext(file_name)

    class Meta:
        model = Book
        fields = ('vk_id', 'unique_id', 'author', 'title', 'page', 'pages', 'words', 'text')
        extra_kwargs = {
            'vk_id': {'read_only': True},
            'text': {'read_only': True},
            'page': {'read_only': True},
            'pages': {'read_only': True},
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

    file = serializers.FileField(required=True, write_only=True)
    title = serializers.CharField(max_length=256)
    author = serializers.CharField(max_length=256)

    def to_internal_value(self, data):
        if 'file' not in data or not data['file']:
            return super().to_internal_value(data)

        if data['file'].content_type == EPUB_EXTENSION:
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
    book_id = serializers.SlugRelatedField(slug_field='unique_id', queryset=Book.objects.all())

    class Meta:
        model = Statistics
        fields = ('book_id', 'pages_read', 'words_read', 'percentage', 'average_speed')


class LibraryAvgProgressBaseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        books = Book.objects.all().filter(vk_id=instance['vk_id']).all()
        stat = Statistics.objects.all().filter(book_id__in=books).aggregate(
            Avg('percentage'),
            Avg('pages_read'),
            Avg('words_read'),
            Avg('average_speed')
        )

        return {
            'pages_read': stat['pages_read__avg'],
            'words_read': stat['words_read__avg'],
            'percentage': stat['percentage__avg'],
            'average_speed': stat['average_speed__avg'],
        }
