from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminOrReadOnly
from .models import Game, Cart
from .serializers import gamesSerializer, cartSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

# Microservice for Search
def search(request):
    if request.user and request.user.is_authenticated:
        if request.user.is_staff:
            greeting = f"admin user {request.user.get_username()}"
        else:
            greeting = f"user {request.user.get_username()}"
    else:
        greeting = "guest user"
    
    try:
        profile_picture = request.user.get_profilePicture()
    except:
        profile_picture = 'NA'

    if request.query_params.get('name') is not None:
        gameObjs = Game.objects.filter(name__icontains = request.query_params.get('name'))
        gamesSerial = gamesSerializer(gameObjs, many=True)
        return Response({"message": f"Hi {greeting}","Catalogue":gamesSerial.data,"Profile_Picture": profile_picture}, status=status.HTTP_200_OK)
    gameObjs    = Game.objects.all()
    gamesSerial = gamesSerializer(gameObjs, many=True)
    return Response({"message": f"Hi {greeting}","Catalogue":gamesSerial.data,"Profile_Picture":profile_picture}, status=status.HTTP_200_OK)
    

@api_view(["GET"])
def Home(request):
    return search(request)
    

@api_view(["GET", "POST", "PATCH"])
@permission_classes([IsAdminOrReadOnly])
def gamesAdmin(request):
    if request.method == "GET":
        return search(request)
    
    if request.method == "POST":
        if isinstance(request.data, dict):
            if Game.objects.filter(name = request.data.get('name')).exists():
                return Response({"message":f"game {request.data.get('name')} already present use PATCH for update"}, status=status.HTTP_400_BAD_REQUEST)
            data = [request.data]
        else:
            data = request.data
            ########### FIX DUPLICATE GAMES ISSUE!!!!!!##############
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
    

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def userCart(request):
    if request.method == "GET":
        cartObj        = Cart.objects.get(user = request.user)
        cartSerialData = cartSerializer(cartObj)
        return Response({"message":f"Cart for user {request.user.get_username()}", "Cart":cartSerialData.data}, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        if Cart.objects.filter(user = request.user).exists():
            return Response({"message":f"Cart already exists for {request.user.get_username()} use PATCH method"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("id") is not None:
            try:
                gamesObjList = []
                for g in eval(request.data.get("id")):
                    if Game.objects.filter(id = g).exists():
                        gamesObjList.append(Game.objects.get(id = g))
                cart = Cart.objects.create(user = request.user)
                cart.games.set(gamesObjList)
                cart.save()
                return Response({"message":"games added to cart successfully!"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)