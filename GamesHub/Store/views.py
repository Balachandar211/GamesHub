from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Game, Cart, Wishlist, Wallet, WalletTransaction
from .serializers import CartSerializer, WishlistSerializer, gamesSerializerSimplified, WalletSerializer, WalletTransactionSerializer
from django.contrib.auth import get_user_model
from utills.microservices import search, mail_service
from .documentation import cart_delete_schema, cart_get_schema, cart_patch_schema, cart_post_schema, whishlist_delete_schema, whishlist_get_schema, whishlist_patch_schema, whishlist_post_schema
from GamesHub.settings import REDIS_CLIENT
from GamesBuzz.models import GameInteraction
from GamesBuzz.serializers import GameInteractionSerializerSimplified
from django.db.models import Q
import redis
from django.core.cache import cache
from rest_framework.exceptions import UnsupportedMediaType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from decimal import Decimal
from utills.email_helper import wallet_recharge_successful_email
User = get_user_model()


@api_view(["GET"])
def Home(request):
    try:
        gamesSerial, get_next_link, get_previous_link, count = search(request, None)
        return Response({"message": "user catalogue", "count":count,  "next": get_next_link, "previous": get_previous_link, "catalogue":gamesSerial}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error":{"code":"game_fetch_error", "message":"internal server error"}, "game":[]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BaseStoreObjectsView(APIView):

    permission_classes = [IsAuthenticated]
    http_method_names  = ['get', 'post', 'patch', 'delete']

    def check_games(self, request, model_name):
        game_ids = request.data.get("games")
        if game_ids is None or game_ids == '':
            return Response({"error":{"code":"not_null_constraint", "message":f"{model_name} cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(game_ids, list):
            return Response({"error": {"code":"incorrect_datatype", "message":"games should be passed as a list"}}, status=status.HTTP_400_BAD_REQUEST)
        

    def get(self, request):
        model_name  = self.model.__name__.lower()
        cache_val   = cache.get(model_name + request.user.get_username())

        if cache_val:
            return Response(cache_val)
        
        try:
            modelObj     = self.model.objects.get(user = request.user)
            modelObjData = self.serializer_class(modelObj).data
            response = Response({"message":f"{model_name} for user", model_name:modelObjData}, status=status.HTTP_200_OK)
            cache.set(model_name + request.user.get_username(), response.data, timeout=3600)
            return response
        
        except self.model.DoesNotExist:
            return Response({"message":f"{model_name} for user does not exist", model_name:[]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":{"code":f"{model_name}_get_error", "message":"internal server error"}, model_name:[]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        model_name  = self.model.__name__.lower()
        if self.model.objects.filter(user = request.user).exists():
            return Response({"message":f"{model_name} already exists for user use PATCH method"}, status=status.HTTP_400_BAD_REQUEST)
        
        check_response = self.check_games(request, model_name)
        if check_response is not None:
            return check_response  

        try:
            modelSerialData = self.serializer_class(data = request.data)
            if modelSerialData.is_valid():
                modelSerialData.save(user = request.user)
                cache.delete(model_name + request.user.get_username())
                return Response({"message":f"{model_name} saved successfully", model_name:modelSerialData.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error":{"code":f"new_{model_name}_error", "details":modelSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error":{"code":f"{model_name}_post_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
    def patch(self, request):
        model_name  = self.model.__name__.lower()

        check_response = self.check_games(request, model_name)
        if check_response is not None:
            return check_response  
        try:
            modelObj = self.model.objects.get(user = request.user)
                
            modelSerialData = self.serializer_class(modelObj, data = request.data, partial = True)
            if modelSerialData.is_valid():
                modelSerialData.save()
                cache.delete(model_name + request.user.get_username())
                return Response({"message": f"{model_name} updated successfully", model_name:modelSerialData.data}, status= status.HTTP_202_ACCEPTED)
            else:
                return Response({"error":{"code":f"update_{model_name}_error", "details":modelSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except self.model.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":f"{model_name} for user not created yet"}}, status=status.HTTP_404_NOT_FOUND)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            return Response({"error":{"code":f"{model_name}_patch_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        model_name  = self.model.__name__.lower()

        try:
            modelObj = self.model.objects.get(user = request.user)
            modelObj.delete()
            cache.delete(model_name + request.user.get_username())
            return Response({"message":f"{model_name} for user deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except self.model.DoesNotExist:
            return Response({"error": {"code":"do_not_exist", "message":f"{model_name} for user does not exist"}}, status=status.HTTP_404_NOT_FOUND)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception:
            return Response({"error":{model_name:f"{model_name}_delete_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

class UserCart(BaseStoreObjectsView):
    model            = Cart
    serializer_class = CartSerializer

class UserWishlist(BaseStoreObjectsView):
    model            = Wishlist
    serializer_class = WishlistSerializer


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
    except UnsupportedMediaType as e:
        return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    except Exception as e:
        return Response({"error": {"code":"not_available", "message":"featured temporarily unavailable please try back later"}, "games": []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({"message": "featured games for user", "games":gameObjsSerial}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def library(request):
    cache_vals             = cache.get("library" + request.user.get_username())
    if cache_vals:
        return Response(cache_vals)
    gameInteractions       = GameInteraction.objects.filter(Q(user = request.user) & Q(in_library = True)).select_related('game').order_by('-purchase_date')
    gameInteractionsSerial = GameInteractionSerializerSimplified(gameInteractions, many = True)
    response = Response({"message": "library contents", "library": gameInteractionsSerial.data}, status=status.HTTP_200_OK)
    cache.set("library" + request.user.get_username(), response.data, timeout=3600)
    return response


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def wallet(request):
    if request.method == "GET":
        wallet, _ = Wallet.objects.get_or_create(user = request.user)
        walletSerial = WalletSerializer(wallet).data
        return Response({"message":f"wallet for user {request.user.get_username()}", "wallet":walletSerial}, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        username = request.user.get_username()
        # an external payment portal needs to be added here to make api calls currently not needed as we are mocking the payment
        amount = request.data.get("amount")
        if amount is None:
            return Response({"error":{"code":"not_null_constraint", "message":"amount cannot be null"}}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = Decimal(str(amount))
        except:
            return Response({"error":{"code":"incorrect_data_type", "message":"amount should be a valid decimal"}}, status=status.HTTP_400_BAD_REQUEST)
        
        if amount <= Decimal(str(0.00)):
            return Response({"error":"invalid_amount", "message":"for wallet recharge amount should be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            try:
                wallet    = Wallet.objects.select_for_update().get(user = request.user)
            except Wallet.DoesNotExist:
                wallet, _ = Wallet.objects.get_or_create(user = request.user)
                wallet    = Wallet.objects.select_for_update().get(user = request.user)

            try:
                walletTransaction = WalletTransaction.objects.create(wallet= wallet, amount=amount, payment_type = 1)
            except IntegrityError as e:
                raise
            except ValidationError as e:
                return Response({"error":{"code":"validation_error", "message":str(e.message)}}, status=status.HTTP_400_BAD_REQUEST)
        

        Subject    = f'Wallet recharge confirmation for {username}'
        message    = wallet_recharge_successful_email({"username":username, "recharge_amount":amount, "transaction_id":walletTransaction.get_transaction_id(), "wallet_balance":wallet.get_balance()})
            
        recipients = [request.user.get_email()]

        mail_result, _ = mail_service(Subject, message, recipients)

        if not mail_result:
            return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        walletSerial = WalletSerializer(wallet).data

        return Response({"message":"wallet recharged successfully", "wallet":walletSerial}, status=status.HTTP_200_OK)

