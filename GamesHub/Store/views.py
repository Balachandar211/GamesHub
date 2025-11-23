from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Game, Cart, Wishlist
from .serializers import CartSerializer, WishlistSerializer, gamesSerializerSimplified
from django.contrib.auth import get_user_model
from utills.microservices import search
from .documentation import cart_delete_schema, cart_get_schema, cart_patch_schema, cart_post_schema, whishlist_delete_schema, whishlist_get_schema, whishlist_patch_schema, whishlist_post_schema
from GamesHub.settings import REDIS_CLIENT
from GamesBuzz.models import GameInteraction
from GamesBuzz.serializers import GameInteractionSerializerSimplified
from django.db.models import Q
import redis
User = get_user_model()


@api_view(["GET"])
def Home(request):
    gamesSerial, get_next_link, get_previous_link, count = search(request)
    return Response({"message": "user catalogue", "count":count,  "next": get_next_link, "previous": get_previous_link, "catalogue":gamesSerial}, status=status.HTTP_200_OK)


@cart_post_schema
@cart_patch_schema
@cart_get_schema
@cart_delete_schema
@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def userCart(request):
    if request.method == "GET":
        try:
            cartObj        = Cart.objects.get(user = request.user)
            cartSerialData = CartSerializer(cartObj)
            return Response({"message":"cart for user", "cart":cartSerialData.data}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message":"cart for user does not exist", "cart":[]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":{"code":"cart_get_error", "message":"internal server error"}, "cart":[]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "POST":
        if Cart.objects.filter(user = request.user).exists():
            return Response({"message":f"Cart already exists for user use PATCH method"}, status=status.HTTP_400_BAD_REQUEST)
        
        game_ids = request.data.get("games")

        if game_ids is None or game_ids == '':
            return Response({"error":{"code":"not_null_constraint", "message":"cart cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(game_ids, list):
            return Response({"error": {"code":"incorrect_datatype", "message":"games should be passed as a list"}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cartSerialData = CartSerializer(data = request.data, context={'request':request})
            if cartSerialData.is_valid():
                cartSerialData.save()
                return Response({"message":"cart saved successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error":{"code":"new_cart_error", "details":cartSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error":{"code":"cart_post_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "PATCH":
        game_ids = request.data.get("games")

        if game_ids is None or game_ids == '':
            return Response({"error":{"code":"not_null_constraint", "message":"cart cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(game_ids, list):
            return Response({"error": {"code":"incorrect_datatype", "message":"ids should be passed as list"}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart = Cart.objects.get(user = request.user)
                
            cartSerialData = CartSerializer(cart, data = request.data, partial = True)
            if cartSerialData.is_valid():
                cartSerialData.save()
                return Response({"message": "cart updated successfully"}, status= status.HTTP_202_ACCEPTED)
            else:
                return Response({"error":{"code":"update_cart_error", "details":cartSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"cart for user not created yet"}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":{"code":"cart_patch_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "DELETE":
        try:
            cart = Cart.objects.get(user = request.user)
            cart.delete()
            return Response({"message":f"cart for user deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"cart for user do not exist"}}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error":{"code":"cart_delete_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@whishlist_post_schema
@whishlist_patch_schema
@whishlist_get_schema
@whishlist_delete_schema
@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def WishlistUser(request):
    if request.method == "GET":
        try:
            wishlistObj        = Wishlist.objects.get(user = request.user)
            wishlistSerialData = WishlistSerializer(wishlistObj)
            return Response({"message":"wishlist for user", "wishlist":wishlistSerialData.data}, status=status.HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response({"message":"wishlist for user does not exist", "wishlist":[]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":{"code":"wishlist_get_error", "message":"internal server error"}, "wishlist":[]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "POST":
        if Wishlist.objects.filter(user = request.user).exists():
            return Response({"message":f"wishlist already exists for user use PATCH method"}, status=status.HTTP_400_BAD_REQUEST)
        
        game_ids = request.data.get("games")

        if game_ids is None or game_ids == '':
            return Response({"error":{"code":"not_null_constraint", "message":"cart cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(game_ids, list):
            return Response({"error": {"code":"incorrect_datatype", "message":"games should be passed as a list"}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlistSerialData = WishlistSerializer(data = request.data, context={'request':request})
            if wishlistSerialData.is_valid():
                wishlistSerialData.save()
                return Response({"message":"wishlist saved successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error":{"code":"new_wishlist_error", "details":wishlistSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":{"code":"wishlist_post_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "PATCH":
        game_ids = request.data.get("games")

        if game_ids is None or game_ids == '':
            return Response({"error":{"code":"not_null_constraint", "message":"cart cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(game_ids, list):
            return Response({"error": {"code":"incorrect_datatype", "message":"ids should be passed as list"}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wishlist           = Wishlist.objects.get(user = request.user)
                
            wishlistSerialData = WishlistSerializer(wishlist, data = request.data, partial = True)
            if wishlistSerialData.is_valid():
                wishlistSerialData.save()
                return Response({"message": "wishlist updated successfully"}, status= status.HTTP_202_ACCEPTED)
            else:
                return Response({"error":{"code":"update_wishlist_error", "details":wishlistSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": {"wishlist":"do_not_exist", "message":"cart for user not created yet"}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":{"code":"wishlist_patch_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "DELETE":
        try:
            wishlist  = Wishlist.objects.get(user = request.user)
            wishlist.delete()
            return Response({"message":f"wishlist for user deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":"wishlist for user do not exist"}}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error":{"code":"wishlist_delete_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#Possible bug have to clear out later
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def featuredPage(request):
    try:
        user_featured  = REDIS_CLIENT.hgetall(request.user.get_username())

        if not user_featured:
            return Response({"message": "featured games for user", "games":{}}, status=status.HTTP_200_OK)

        user_featured  = list(map(lambda kv : (kv[0], kv[1]), user_featured.items()))
        user_featured  = sorted(user_featured, key = lambda kv : kv[1], reverse=True)[:min(len(user_featured), 5)]
        user_featured  = list(map(lambda v : v[0], user_featured))    
        gameObjs       = Game.objects.filter(id__in = user_featured)
        gameObjsSerial = gamesSerializerSimplified(gameObjs, many=True).data
    except redis.ConnectionError:
        return Response({"error": {"code":"not_available", "message":"featured temporarily unavailable please try back later"}, "games": []}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    except Exception as e:
        return Response({"error": {"code":"not_available", "message":"featured temporarily unavailable please try back later"}, "games": []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message": "featured games for user", "games":gameObjsSerial}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def library(request):
    gameInteractions       = GameInteraction.objects.filter(Q(user = request.user) & Q(in_library = True)).select_related('game').order_by('-purchase_date')
    gameInteractionsSerial = GameInteractionSerializerSimplified(gameInteractions, many = True)
    return Response({"message": "library contents", "library": gameInteractionsSerial.data}, status=status.HTTP_200_OK)