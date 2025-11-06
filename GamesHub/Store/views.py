from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Game, Cart, Wishlist
from .serializers import cartSerializer, wishlistSerializer
from django.contrib.auth import get_user_model
from utills.microservices import search
User = get_user_model()


@api_view(["GET"])
def Home(request):
    greeting, paginator, gamesSerial = search(request)
    return Response({"message": f"Hi {greeting}", 'next': paginator.get_next_link(), 'previous': paginator.get_previous_link(), "Catalogue":gamesSerial.data}, status=status.HTTP_200_OK)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def userCart(request):
    if request.method == "GET":
        if  Cart.objects.filter(user = request.user).exists():
            cartObj        = Cart.objects.get(user = request.user)
            cartSerialData = cartSerializer(cartObj)
            return Response({"message":f"Cart for user {request.user.get_username()}", "Cart":cartSerialData.data}, status=status.HTTP_200_OK)
        return Response({"message":f"Cart for user {request.user.get_username()}", "Cart":[]}, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        if Cart.objects.filter(user = request.user).exists():
            return Response({"message":f"Cart already exists for {request.user.get_username()} use PATCH method"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("id") is not None:
            try:
                success_dict = {}
                failure_dict = {}
                gamesObjList = []
                for g in request.data.get("id"):
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
        if request.data.get("id") is not None:
            try:
                success_dict = {}
                failure_dict = {}
                for g in request.data.get("id"):
                    if Game.objects.filter(id = g).exists():
                        gamesObj = Game.objects.get(id = g)
                        cart.games.add(gamesObj)
                        success_dict[gamesObj.get_name()] = "Added Successfully"
                    else:
                        failure_dict[g] = "Incorrect ID"
                cart.save()
                return Response({"message":"games added to cart successfully!", "Success_Status": success_dict, "Failure_Status":failure_dict}, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                return Response({"message": "Data Should be passed as list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    if request.method == "DELETE":
        try:
            cart = Cart.objects.get(user = request.user)
            cart.delete()
            return Response({"message":f"cart for user {request.user.get_username()} deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"message":f"No cart exist for user {request.user.get_username()}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def WishlistUser(request): 
    if request.method == "GET":
        if  Wishlist.objects.filter(user = request.user).exists():
            WishlistObj        = Wishlist.objects.get(user = request.user)
            WishlistSerialData = wishlistSerializer(WishlistObj)
            return Response({"message":f"Wishlist for user {request.user.get_username()}", "Wishlist":WishlistSerialData.data}, status=status.HTTP_200_OK)
        return Response({"message":f"Wishlist for user {request.user.get_username()}", "Wishlist":[]}, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        if Wishlist.objects.filter(user = request.user).exists():
            return Response({"message":f"Wishlist already exists for {request.user.get_username()} use PATCH method"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("id") is not None:
            try:
                success_dict = {}
                failure_dict = {}
                gamesObjList = []
                for g in request.data.get("id"):
                    if Game.objects.filter(id = g).exists():
                        gamesObj = Game.objects.get(id = g)
                        gamesObjList.append(gamesObj)
                        success_dict[gamesObj.get_name()] = "Added Successfully"
                    else:
                        failure_dict[g] = "Incorrect ID"
                WishlistObj = Wishlist.objects.create(user = request.user)
                WishlistObj.games.set(gamesObjList)
                WishlistObj.save()
                return Response({"message":"games added to Wishlist successfully!", "Success_Status": success_dict, "Failure_Status":failure_dict}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message": "Data Should be passed as list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == "PATCH":
        WishlistObj = Wishlist.objects.get(user = request.user)
        if request.data.get("id") is not None:
            try:
                success_dict = {}
                failure_dict = {}
                for g in request.data.get("id"):
                    if Game.objects.filter(id = g).exists():
                        gamesObj = Game.objects.get(id = g)
                        WishlistObj.games.add(gamesObj)
                        success_dict[gamesObj.get_name()] = "Added Successfully"
                    else:
                        failure_dict[g] = "Incorrect ID"
                WishlistObj.save()
                return Response({"message":"games added to Wishlist successfully!", "Success_Status": success_dict, "Failure_Status":failure_dict}, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                return Response({"message": "Data Should be passed as list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "DELETE":
        try:
            wishlist = Wishlist.objects.get(user = request.user)
            wishlist.delete()
            return Response({"message":f"wishlist for user {request.user.get_username()} deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"message":f"No wishlist exist for user {request.user.get_username()}"}, status=status.HTTP_400_BAD_REQUEST)
