from django.db import models


class User(models.Model):
    vk_id = models.IntegerField(primary_key=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.vk_id}'

    class Meta:
        ordering = ['created']
