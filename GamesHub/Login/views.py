from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import User
from .serializers import userSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

@api_view(["GET", "POST"])
def Users(request):
    if request.method == "GET":
        userObjects     = User.objects.all()
        userObjectsData = userSerializer(userObjects, many= True)
        return Response(userObjectsData.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        userObject     = userSerializer(data = request.data)
        if userObject.is_valid():
            userObject.save()
            return Response({"message": f"User {request.data.get('userName')} added successfully"}, status=status.HTTP_201_CREATED)
        return Response({"errors":userObject.errors}, status=status.HTTP_400_BAD_REQUEST)
