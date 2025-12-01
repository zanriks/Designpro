from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    agreement = models.BooleanField(default=False, verbose_name='Согласие на обработку персональных данных')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.full_name} ({self.username})"

# class Order(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
#     image = models.ImageField(upload_to='catalog/images/')
#
#
#     def __str__(self):
#         return self.name
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(
#         Order, related_name='items', on_delete=models.CASCADE)

