from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import *

urlpatterns = [
    path('register/', ShoppingRegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('shopping/create/', ShoppingListCreateView.as_view(), name='shopping_create'),
    path('shopping/get/', ShoppingListListView.as_view(), name='shopping_get'),
    path('shopping/delete/<str:pk>/', ShoppingListDestroyView.as_view(), name='shopping_delete'),
    path('shopping/retrieve/<str:id>/', ShoppingListRetrieveView.as_view(), name='shopping_retrieve'),
    path('item/create/', ItemCreateView.as_view(), name='item_create'),
    path('item/delete/<str:pk>/', ItemDestroyView.as_view(), name='item_delete'),
    path('notify/', NotifyView.as_view(), name='notify'),
]
