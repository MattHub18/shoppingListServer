from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from .models import *


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class UserSerializer(RegisterSerializer):
    notificationId = serializers.CharField()

    class Meta:
        model = ShoppingUser
        fields = ['username', 'email', 'notificationId']
