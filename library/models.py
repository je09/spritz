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
    """Describes Book in our DB"""

    vk_id = models.ForeignKey(User, related_name='books_id', on_delete=models.CASCADE)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    file = models.FileField(upload_to=upload_to)
    edited = models.DateTimeField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # To make sure to remember time of every update.
        self.edited = timezone.now()
        return super().save()

    def __str__(self):
        return f'{self.unique_id}'

    class Meta:
        ordering = ['edited']
        unique_together = ('title', 'author', 'vk_id')


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
