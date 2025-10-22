from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminOrReadOnly
from .models import Game, Cart
from .serializers import gamesSerializer, cartSerializer
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
User = get_user_model()

# Microservice for Search
def search(request):
    paginator = LimitOffsetPagination()
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
        paginated_games = paginator.paginate_queryset(gameObjs, request)
        gamesSerial = gamesSerializer(paginated_games, many=True)
        return Response({"message": f"Hi {greeting}", 'next': paginator.get_next_link(), 'previous': paginator.get_previous_link(), "Catalogue":gamesSerial.data,"Profile_Picture": profile_picture}, status=status.HTTP_200_OK)
    
    gameObjs    = Game.objects.all()
    paginated_games = paginator.paginate_queryset(gameObjs, request)
    gamesSerial = gamesSerializer(paginated_games, many=True)
    return Response({"message": f"Hi {greeting}", 'next': paginator.get_next_link(), 'previous': paginator.get_previous_link(), "Catalogue":gamesSerial.data,"Profile_Picture":profile_picture}, status=status.HTTP_200_OK)
    

@api_view(["GET"])
def Home(request):
    return search(request)
    

@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
def gamesAdmin(request):
    if request.method == "GET":
        return search(request)
    
    if request.method == "POST":
        if isinstance(request.data, dict):
            if not request.data.get('name'):
                return Response({"message": "Data without name field exist"}, status=status.HTTP_400_BAD_REQUEST)
            if Game.objects.filter(name = request.data.get('name')).exists():
                return Response({"message":f"game {request.data.get('name')} already present use PATCH for update"}, status=status.HTTP_400_BAD_REQUEST)
            data = [request.data]
            gameObjs    = gamesSerializer(data = data)
            if gameObjs.is_valid():
                gameObjs.save()
                return Response({"message":f"game(s) added successfully!"}, status=status.HTTP_201_CREATED)
            return Response({"error": gameObjs.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            success_dict = {}
            error_dict   = {}
            for data in request.data:
                if not data.get('name'):
                    error_dict["Incorrect Json"] = "Entry without name field exist"
                elif Game.objects.filter(name = data.get('name')).exists():
                    error_dict[data.get('name')] = "Game with the name already exists use PATCH to update"
                else:
                    gameObjs    = gamesSerializer(data = data)
                    if gameObjs.is_valid():
                        gameObjs.save()
                        success_dict[data.get('name')] = "Game added Successfully!"
                    else:
                        error_dict[data.get('name')] =  gameObjs.errors
                
            return Response({"message":f"game(s) added successfully!", "Success_Status":success_dict, "Error_Status":error_dict}, status=status.HTTP_201_CREATED)
    
    if request.method == "PATCH":
        gameObj     = Game.objects.get(name = request.data.get("name"))
        gamesSerial = gamesSerializer(gameObj, data = request.data, partial=True)
        if gamesSerial.is_valid():
            gamesSerial.save()
            return Response({"message":f"game {request.data.get("name")} updated successfully!"}, status=status.HTTP_202_ACCEPTED)
        return Response({"message": gamesSerial.errors})
    
    if request.method == "DELETE":
        success_dict = {}
        failure_dict = {}
        try:
            if request.data.get('id') is not None:
                for id in eval(request.data.get('id')):
                    if Game.objects.filter(id = id).exists():
                        gameObj   = Game.objects.get(id = id)
                        game_name = gameObj.get_name()
                        gameObj.delete()
                        success_dict[id] = f"game {game_name} deleted successfully"
                    else:
                        failure_dict[id] = "game does not exist for this id"
                
                return Response({"message": f"Games deleted successfully!", "Success_Status":success_dict, "Failure_Status": failure_dict}, status=status.HTTP_204_NO_CONTENT)
            
            if request.data.get('name') is not None:
                for name in eval(request.data.get('name')):
                    if Game.objects.filter(name = name).exists():
                        gameObj   = Game.objects.get(name = name)
                        game_name = gameObj.get_name()
                        gameObj.delete()
                        success_dict[name] = f"game {game_name} deleted successfully"
                    else:
                        failure_dict[name] = "game does not exist for this id"
                
                return Response({"message": f"Games deleted successfully!", "Success_Status":success_dict, "Failure_Status": failure_dict}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error":f"use id or exact name as list of values"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error":f"use id or exact name to request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST", "PATCH"])
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
                success_dict = {}
                failure_dict = {}
                gamesObjList = []
                for g in eval(request.data.get("id")):
                    if Game.objects.filter(id = g).exists():
                        gamesObj = Game.objects.get(id = g)
                        gamesObjList.append(gamesObj)
                        success_dict[gamesObj.get_name()] = "Added Successfully"
                    else:
                        failure_dict[g] = "Incorrect ID"
                cart = Cart.objects.create(user = request.user)
                cart.games.set(gamesObjList)
                cart.save()
                return Response({"message":"games added to cart successfully!", "Success_Status": success_dict, "Failure_Status":failure_dict}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message": "Data Should be passed as list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == "PATCH":
        cart = Cart.objects.get(user = request.user)
        #to implement


    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase(request):
    if request.method == "POST":
        pass