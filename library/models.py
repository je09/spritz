import uuid
from itertools import chain
from django.db import models
from users.models import User


def upload_to(instance, filename) -> str:
    """
    Generate path to upload book to.

    Lambda cannot be serialized in Django Models. That is why we need this function.
    """
    return f'books/{str(instance)}-{filename}'


class Bookshelf(models.Model):
    """
    An entity to store books in to.

    There are two types of bookshelf: user's private bookshelf and
    library bookshelf. The last one is used to store public books in.
    If user "borrows" book from this shelf, "Librarian" sets a
    record in the LibraryJournal with a set of book_unique_id and
    shelf_unique_id.
    Note that there is no actual "Librarian" model here it's just a user
    with a vk_id=0.
    """

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    public = models.BooleanField(null=False, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # TODO: Check to have only one model with public=true
        super().save()

    def create_public_shelf(self):
        if not User.objects.filter(vk_id=0).exists():
            librarian = User.objects.create(vk_id=0)
            librarian.save()

        librarian = User.objects.filter(vk_id=0).first()
        self.objects.create(public=True, user=librarian)
        self.save()

    def get_all(self):
        if self.public:
            return Book.objects.filter(public=True).all()

        private = Book.objects.filter(shelf=self).all()
        borrowed_books = LibrarianJournal.objects.filter(user_shelf=self).all().values_list('borrowed_book__unique_id', flat=True)
        public = Book.objects.filter(unique_id__in=borrowed_books)

        return list(chain(private, public))

    def __str__(self):
        if str(self.user) == 'Librarian':
            return 'Public Bookshelf'

        return f'Private Bookshelf: {self.user}'


class LibrarianJournal(models.Model):
    """
    An entity to store records of "borrowed" by user books.
    """

    user_shelf = models.ForeignKey(Bookshelf, on_delete=models.CASCADE)
    borrowed_book = models.ForeignKey('Book', on_delete=models.CASCADE)


class Book(models.Model):
    """
    An entity to store information about a book.

    This model describes two types of books, which basically aren't that
    different from each other.
    Private Books – are books user uploaded. Those books assigned to
    user's bookshelf and can't be accessed by another user.
    Public Books – are books Librarian uploaded. Those books assigned to
    "Librarian" public bookshelf
    """

    # TODO: add image, image-256.
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    shelf = models.ForeignKey('Bookshelf', on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    category = models.ForeignKey('BookCategory', on_delete=models.CASCADE, null=True)
    pages = models.IntegerField()
    words = models.IntegerField()
    file = models.FileField(upload_to=upload_to)
    public = models.BooleanField(null=False, default=False)
    edited = models.DateTimeField(auto_now=True)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # TODO: Check category for public or not book. If it's the public, there should be a category, not – otherwise.
        super().save()

    def __str__(self):
        return f'{self.unique_id}: {self.author} - {self.title}'

    def borrow(self, shelf):
        if (not self.public or
                LibrarianJournal.objects.filter(user_shelf=shelf, borrowed_book=self).exists()):
            return

        lib = LibrarianJournal.objects.create(user_shelf=shelf, borrowed_book=self)
        lib.save()

    def give_back(self, shelf):
        if (not self.public or
                not LibrarianJournal.objects.filter(user_shelf=shelf, borrowed_book=self).exists()):
            return

        LibrarianJournal.objects.filter(user_shelf=shelf, borrowed_book=self).delete()

    class Meta:
        ordering = ['edited']
        unique_together = ('title', 'author', 'shelf')


class BookCategory(models.Model):
    """
    Describes categories of public books.
    """

    name = models.CharField(primary_key=True, max_length=256)
    title = models.CharField(max_length=256)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Statistics(models.Model):
    """Describes Statistics of book reading"""

    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    shelve = models.ForeignKey(Bookshelf, on_delete=models.CASCADE)
    percentage = models.FloatField(max_length=4)
    pages_read = models.IntegerField()
    words_read = models.IntegerField()
    average_speed = models.FloatField(max_length=6)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.book_id} - {self.percentage}%'

    def get_book_stat(self, user: User):
        return

    class Meta:
        ordering = ['edited']
        unique_together = ('book_id', 'shelve')
