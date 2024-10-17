import json
import os
import sys

import firebase_admin
from dj_rest_auth.registration.views import RegisterView
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
from rest_framework.exceptions import NotFound
from rest_framework.generics import DestroyAPIView, CreateAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import requests

# Create your views here.


from .serializers import *
from .models import ShoppingList, Item


class ShoppingRegisterView(RegisterView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.save(request)

            user.notificationId = request.data.get('notificationId')
            user.save()

            return JsonResponse({'message': 'User created successfully', 'status': status.HTTP_201_CREATED})
        except json.JSONDecodeError:
            return JsonResponse({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid JSON format"})

        except Exception as e:
            return JsonResponse(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": f"Failed to create object, {e}"})


class ShoppingListListView(ListAPIView):
    serializer_class = ShoppingListSerializer
    permission_classes = (IsAuthenticated,)
    queryset = ShoppingList.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            data = self.get_queryset().all()
            serializer = self.get_serializer(data, many=True)
            return JsonResponse(
                {"status": status.HTTP_200_OK, "message": "List retrieved successfully", "data": serializer.data})

        except ObjectDoesNotExist:
            return JsonResponse({"status": status.HTTP_404_NOT_FOUND, "message": "List not found"})

        except Exception as e:
            return JsonResponse(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": f"Something went wrong: {e}"})


class ShoppingListDestroyView(DestroyAPIView):
    serializer_class = ShoppingListSerializer
    permission_classes = (IsAuthenticated,)
    queryset = ShoppingList.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, args, kwargs)
            return JsonResponse({
                'message': 'List deleted successfully', 'status': status.HTTP_200_OK})

        except NotFound:
            return JsonResponse({'message': 'List not found', 'status': status.HTTP_404_NOT_FOUND})


class ShoppingListCreateView(CreateAPIView):
    serializer_class = ShoppingListSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, args, kwargs)
            return JsonResponse({"status": status.HTTP_200_OK, "message": "List created successfully"})

        except json.JSONDecodeError:
            return JsonResponse({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid JSON format"})

        except Exception as e:
            return JsonResponse(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": f"Failed to create list: {e}"})


class ShoppingListRetrieveView(ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Item.objects.filter(shoppingListId=self.request.parser_context['kwargs']['id'])

    def get(self, request, *args, **kwargs):
        try:
            data = self.get_queryset().all()
            serializer = self.get_serializer(data, many=True)
            return JsonResponse(
                {"status": status.HTTP_200_OK, "message": "Items retrieved successfully", "data": serializer.data})
        except ObjectDoesNotExist:
            return JsonResponse({"status": status.HTTP_404_NOT_FOUND, "message": "List not found"})

        except Exception as e:
            return JsonResponse(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": f"Something went wrong: {e}"})


class ItemDestroyView(DestroyAPIView):
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Item.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, args, kwargs)
            return JsonResponse({
                'message': 'Item deleted successfully', 'status': status.HTTP_200_OK})

        except NotFound:
            return JsonResponse({'message': 'Item not found', 'status': status.HTTP_404_NOT_FOUND})


class ItemCreateView(CreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            users = ShoppingUser.objects.all()
            user = request.user
            for u in users:
                if u.notificationId != '' and u.notificationId != user.notificationId:
                    notify_url = request.build_absolute_uri(reverse('notify'))
                    lst = ShoppingList.objects.get(id=request.POST['shoppingListId'])
                    requests.post(notify_url,
                                  data={'notification_id': u.notificationId, "username": request.user.username,
                                        'item_name': request.POST['name'], 'list': lst.createdAt},
                                  headers={'Authorization': f'Bearer {request.auth}'})

            return JsonResponse({"status": status.HTTP_200_OK, "message": "Item created successfully"})
        except json.JSONDecodeError:
            return JsonResponse({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid JSON format"})

        except Exception as e:
            return JsonResponse(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": f"Failed to create list: {e}"})


class NotifyView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    # read firebase credentials
    try:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ.get("FIREBASE_PROJECT_ID", ""),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID", ""),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
            "client_email": "firebase-adminsdk-9expx@" + os.environ.get("FIREBASE_PROJECT_ID",
                                                                        "") + ".iam.gserviceaccount.com",
            "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-9expx%40" +
                                    os.environ.get("FIREBASE_PROJECT_ID", "") + ".iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        })
        firebase_admin.initialize_app(cred)
    except IOError as e:
        sys.exit(f"Something went wrong with firebase certificate: {e}")
    except ValueError as e:
        sys.exit(e)

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST

            # check the body of user's call
            topic = data['notification_id']
            if topic == '':
                return JsonResponse({'message': 'Notification id is empty', 'status': status.HTTP_400_BAD_REQUEST})
            username = data['username']
            if username == '':
                return JsonResponse({'message': 'username is empty', 'status': status.HTTP_400_BAD_REQUEST})

            item_name = data['item_name']
            if item_name == '':
                return JsonResponse({'message': 'item is empty', 'status': status.HTTP_400_BAD_REQUEST})
            lst = data['list']
            if lst == '':
                return JsonResponse({'message': 'list is empty', 'status': status.HTTP_400_BAD_REQUEST})

            # build notification

            notification = messaging.Notification("List della spesa", f'{username} ha aggiunto {item_name} a {lst}')
            message = messaging.Message(notification=notification, topic=topic)
            # try notification
            try:
                messaging.send(message)
            except FirebaseError as f_e:
                return JsonResponse(
                    {'message': f'Firebase FCM error occurred: {f_e}', 'status': status.HTTP_502_BAD_GATEWAY})
            except ValueError as v_e:
                return JsonResponse(
                    {'message': f'Some values are wrong: {v_e}', 'status': status.HTTP_406_NOT_ACCEPTABLE})

            return JsonResponse({'message': 'Notified', 'status': status.HTTP_200_OK})
        except json.JSONDecodeError:
            return JsonResponse({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid JSON format"})

        except Exception as e:
            return JsonResponse(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": f"Failed to create list: {e}"})
