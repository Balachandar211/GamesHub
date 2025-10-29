from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
@api_view(["GET"])
def health_check(request):
    return Response({"message":"up and running"}, status=status.HTTP_200_OK)

@api_view(["GET"])
def api_redirect(request):
    return Response({"message": "requested end point not found"}, status=status.HTTP_404_NOT_FOUND)

def monitor_1(request):
    return HttpResponse("Monitor 1 good")

def monitor_2(request):
    return HttpResponse("Monitor 2 good")
