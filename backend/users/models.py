from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True
    )
    name = models.CharField(
        max_length=16
    )
    surname = models.CharField(
        max_length=16
    )
    image = models.ImageField(
        upload_to='users/images/',
        verbose_name='Фото',
        help_text='Загрузите картинку профиля',
        blank=True,
        null=True
    )
    background_image = models.ImageField(
        upload_to='users/background_images/',
        verbose_name='Фото',
        help_text='Загрузите фоновую картинку профиля',
        blank=True,
        null=True
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
