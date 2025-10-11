from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import userSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password


# Create your views here.

@api_view(["POST"])
def SignUp(request):
    userObject     = userSerializer(data = request.data)
    if userObject.is_valid():
        userObject = userObject.save()
        refresh = RefreshToken.for_user(userObject)
        return Response({"message": f"User {request.data.get('userName')} added successfully and your token is {str(refresh.access_token)}"}, status=status.HTTP_201_CREATED)
    
    return Response({"errors":userObject.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def Login(request):
    try:
        userObj = User.objects.get(userName = request.data.get("userName"))
        if check_password(request.data.get("passWord"), userObj.get_passWord()):
            refresh = RefreshToken.for_user(userObj)
            return Response({"message": f"User {userObj.get_userName()} logged in and you token is {str(refresh.access_token)}"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":f"Incorrect password for user {userObj.get_userName()}"}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"message":"userName not found"}, status=status.HTTP_404_NOT_FOUND)
    




