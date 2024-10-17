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
    class Meta:
        model = ShoppingUser
        fields = '__all__'

    def create(self, validated_data):
        # Create a new user instance with validated data
        user = ShoppingUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            password=validated_data['password'],
        )
        # Set the notificationId and save the user
        n_id = validated_data['notificationId']
        print(n_id)
        user.notificationId = n_id
        user.save()
        return user
