from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import os


class User(AbstractUser):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    agreement = models.BooleanField(default=False, verbose_name='Согласие на обработку персональных данных')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.full_name} ({self.username})"


def validate_image_file(value):
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError('Разрешены только файлы: jpg, jpeg, png, bmp.')
    if value.size > 2 * 1024 * 1024:  # 2 МБ
        raise ValidationError('Размер файла не должен превышать 2 МБ.')


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_COMPLETED, 'Выполнена'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='orders'
    )

    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='catalog/images/',
        validators=[validate_image_file],
        verbose_name='Фото помещения или план',
    )
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='Статус'
    )

    def __str__(self):
        return self.name