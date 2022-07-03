from django.contrib import admin
from library.models import (
    Book,
    Statistics
)


@admin.register(Book)
class LibraryBookAdmin(admin.ModelAdmin):
    readonly_fields = (
        'unique_id',
    )

    list_display = (
        'unique_id',
        'title',
        'author',
        'file',
        'edited'
    )


@admin.register(Statistics)
class LibraryStatisticsAdmin(admin.ModelAdmin):
    readonly_fields = (
        'book_id',
    )

    list_display = (
        'percentage',
        'pages_read',
        'words_read',
        'average_speed',
        'edited',
    )
