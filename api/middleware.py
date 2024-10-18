from django.http import JsonResponse
from rest_framework import status


class CatchAppendSlashErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.get_full_path()
        print(path)

        if path[-1] != '/':
            return JsonResponse({"message": "POST request missing trailing slash. Ensure URL ends with a '/'"},
                                status=status.HTTP_400_BAD_REQUEST)
        # Returning the response
        return response
