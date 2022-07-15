import uuid
from django.db import models
from django.utils import timezone
from users.models import User


def upload_to(instance, filename) -> str:
    """
    Generate path to upload book to.

    Lambda cannot be serialized in Django Models. That is why we need this function.
    """
    return f'books/{str(instance)}-{filename}'


class Book(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    pages = models.IntegerField()
    words = models.IntegerField()
    file = models.FileField(upload_to=upload_to)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.unique_id}: {self.author} - {self.title}'

    class Meta:
        abstract = True
        ordering = ['edited']
        unique_together = ('title', 'author')


"""
Public books

Those books are free to use for every user.
Bookshelf -> PublicBook
"""


class PublicBookCategory(models.Model):
    shelf = models.ManyToManyField('Bookshelf')
    name = models.CharField(primary_key=True, max_length=256)
    title = models.CharField(max_length=256)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class PublicBook(Book):
    """Book which can be accessed by any user"""
    category = models.ForeignKey(PublicBookCategory, on_delete=models.CASCADE)


"""
Private books are the ones User uploaded, they're allowed to use for this user only.

PrivateBook -> Bookshelf
"""


class PrivateBook(Book):
    """Book which can be accessed by user uploaded it only"""
    shelf = models.ForeignKey('Bookshelf', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('title', 'author', 'shelf')


class Bookshelf(models.Model):
    """Entity where user stores his private and public books"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public_book = models.ManyToManyField(PublicBook)


class Statistics(models.Model):
    """Describes Statistics of book reading"""

    book_id = models.OneToOneField(Book, on_delete=models.CASCADE, primary_key=True)
    percentage = models.FloatField(max_length=4)
    pages_read = models.IntegerField()
    words_read = models.IntegerField()
    average_speed = models.FloatField(max_length=6)
    edited = models.DateTimeField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # To make sure to remember time of every update.
        self.edited = timezone.now()
        return super().save()

    def __str__(self):
        return f'{self.book_id} - {self.percentage}%'

    class Meta:
        ordering = ['edited']
