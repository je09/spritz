from django.db import models


class User(models.Model):
    vk_id = models.IntegerField(primary_key=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Librarian
        if self.vk_id == 0:
            return 'Librarian'

        return f'User: {self.vk_id}'

    class Meta:
        ordering = ['created']
