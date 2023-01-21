from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True
    )
    first_name = models.CharField(
        max_length=16
    )
    last_name = models.CharField(
        max_length=16
    )

    class Meta:
        ordering = ['-date_joined']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follow')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
