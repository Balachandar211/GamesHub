from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminOrReadOnly
from .models import Game
from .serializers import gamesSerializer

# Create your views here.

@api_view(["GET"])
def Home(request):
    if request.user and request.user.is_authenticated:
        gameObjs    = Game.objects.all()
        gamesSerial = gamesSerializer(gameObjs, many=True)
        return Response({"message": f"Hi {request.user.get_username()}","Catalogue":gamesSerial.data,"Profile_Picture":request.user.get_profilePicture()}, status=status.HTTP_200_OK)
    else:
        gameObjs    = Game.objects.all()
        gamesSerial = gamesSerializer(gameObjs, many=True)
        return Response({"message": f"Hi guest user", "Catalogue":gamesSerial.data}, status=status.HTTP_200_OK)
    

@api_view(["GET", "POST", "PATCH"])
@permission_classes([IsAdminOrReadOnly])
def gamesAdmin(request):
    if request.method == "GET":
        if request.query_params.get('name') is not None:
            gameObjs = Game.objects.filter(name__icontains = request.query_params.get('name'))
            gamesSerial = gamesSerializer(gameObjs, many=True)
            return Response({"message": f"Hi admin user {request.user.get_username()}","Catalogue":gamesSerial.data,"Profile_Picture":request.user.get_profilePicture()}, status=status.HTTP_200_OK)
        gameObjs    = Game.objects.all()
        gamesSerial = gamesSerializer(gameObjs, many=True)
        return Response({"message": f"Hi admin user {request.user.get_username()}","Catalogue":gamesSerial.data,"Profile_Picture":request.user.get_profilePicture()}, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        if Game.objects.filter(name = request.data.get('name')).exists():
            return Response({"message":f"game {request.data.get('name')} already present use PATCH for update"}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.data, dict):
            data = [request.data]
        gameObjs    = gamesSerializer(data = data, many=True)
        if gameObjs.is_valid():
            gameObjs.save()
            return Response({"message":f"game(s) added successfully!"}, status=status.HTTP_201_CREATED)
        return Response({"message": gameObjs.errors})
    
    if request.method == "PATCH":
        gameObj     = Game.objects.get(name = request.data.get("name"))
        gamesSerial = gamesSerializer(gameObj, data = request.data, partial=True)
        if gamesSerial.is_valid():
            gamesSerial.save()
            return Response({"message":f"game {request.data.get("name")} updated successfully!"}, status=status.HTTP_202_ACCEPTED)
        return Response({"message": gamesSerial.errors})
    

