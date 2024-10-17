from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class ShoppingList(models.Model):
    createdAt = models.DateTimeField(auto_now_add=False)

    class Meta:
        ordering = ['createdAt']

    def __str__(self):
        return str(self.createdAt)


class Item(models.Model):
    shoppingListId = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    name = models.TextField()
    isle = models.IntegerField()

    class Meta:
        ordering = ["isle"]

    def __str__(self):
        return self.name


class ShoppingUser(AbstractUser):
    notificationId = models.TextField()
