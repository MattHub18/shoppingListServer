from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(ShoppingList)
admin.site.register(Item)
admin.site.register(ShoppingUser)
