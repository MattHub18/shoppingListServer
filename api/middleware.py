from django.http import JsonResponse
from rest_framework import status


class CatchAppendSlashErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Preparation ops

        # Retrieving the response
        response = self.get_response(request)

        # Updating the response
        if request.method == "POST" and (response.status_code == 404 or response.status_code == 500):
            return JsonResponse({"status": status.HTTP_400_BAD_REQUEST,
                                 "message": "POST request missing trailing slash. Ensure URL ends with a '/'"})
        # Returning the response
        return response
