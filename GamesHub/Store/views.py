from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utills.permissions import IsAdminOrReadOnly
from rest_framework import status
from .models import Game, Cart, Wishlist, Wallet, WalletTransaction, Sale
from .serializers import CartSerializer, WishlistSerializer, gamesSerializerSimplified, WalletSerializer, WalletTransactionSerializer, SaleSerializer, SaleSerializerDetail
from django.contrib.auth import get_user_model
from utills.microservices import search, mail_service, delete_cache_key
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
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.views import exception_handler
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
import copy
from GamesHub.settings import CACHE_ENV
User = get_user_model()


def get_cache_key(request):
    query_params = request.GET.dict()
    sorted_pairs = str(sorted(tuple(query_params.items()), key=lambda x: x[1].lower()))
    username   = request.user.get_username()

    return CACHE_ENV + username + sorted_pairs

def get_paginated(request, objects, serializer):
    paginator              = LimitOffsetPagination()
    paginated_transactions = paginator.paginate_queryset(objects, request)
    objectSerial           = serializer(paginated_transactions, many=True).data
    return objectSerial, paginator.get_next_link(), paginator.get_previous_link(), paginator.count

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
    
    def handle_exception(self, exc):
        model_name = self.model.__name__.lower()

        if isinstance(exc, self.model.DoesNotExist):
            return Response({"error": {"code": "do_not_exist","message": f"{model_name} for user not created yet use POST to create it"},model_name: []}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exc, UnsupportedMediaType):
            return Response({"error": {"code": "unsupported_media_type", "message": str(exc)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        response = exception_handler(exc, {"view": self, "request": self.request})
        if response is not None:
            return response

        method = self.request.method.lower()
        return Response({"error": {"code": f"{model_name}_{method}_error","message": "internal server error"},model_name: []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def check_games(self, request, model_name):
        game_ids  = request.data.get("games")
        valid_ids = copy.deepcopy(game_ids)
        if game_ids is None or game_ids == '':
            return Response({"error":{"code":"not_null_constraint", "message":f"{model_name} cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(game_ids, list):
            return Response({"error": {"code":"incorrect_datatype", "message":"games should be passed as a list"}}, status=status.HTTP_400_BAD_REQUEST)

        for ids in valid_ids:
            try:
                int(ids)
            except:
                request.data.get("games").remove(ids)
                continue 

            if GameInteraction.objects.filter(game__id = ids).exists():
                request.data.get("games").remove(ids)
            

    def get_object(self, request):
        return self.model.objects.get(user = request.user)

    def get(self, request):
        model_name  = self.model.__name__.lower()
        cache_key   = CACHE_ENV + model_name + get_cache_key(request)
        model_name  = self.model.__name__.lower()
        cache_val   = cache.get(cache_key)

        if cache_val:
            return Response(cache_val)
        
        modelObj     = self.get_object(request)
        gameObjs     = modelObj.games.all()
        cache_vals   = get_paginated(request, gameObjs, self.paginate_serializer)
        response = Response({"message":f"{model_name} for user", "next":cache_vals[1], "previous":cache_vals[2], "count":cache_vals[3], model_name:cache_vals[0]}, status=status.HTTP_200_OK)
        cache.set(cache_key, response.data, timeout=3600)
        return response
        
    def post(self, request):
        model_name     = self.model.__name__.lower()
        cache_base_key = model_name + request.user.get_username()
        if self.model.objects.filter(user = request.user).exists():
            return Response({"message":f"{model_name} already exists for user use PATCH method"}, status=status.HTTP_400_BAD_REQUEST)
        
        check_response = self.check_games(request, model_name)
        if check_response is not None:
            return check_response  

        modelSerialData = self.serializer_class(data = request.data)
        if modelSerialData.is_valid():
            modelSerialData.save(user = request.user)
            delete_cache_key(cache_base_key)
            return Response({"message":f"{model_name} saved successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error":{"code":f"new_{model_name}_error", "details":modelSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        model_name  = self.model.__name__.lower()
        cache_base_key = model_name + request.user.get_username()

        check_response = self.check_games(request, model_name)
        if check_response is not None:
            return check_response  
        
        modelObj = self.get_object(request)
            
        modelSerialData = self.serializer_class(modelObj, data = request.data, partial = True)
        if modelSerialData.is_valid():
            modelSerialData.save()
            delete_cache_key(cache_base_key)
            return Response({"message": f"{model_name} updated successfully"}, status= status.HTTP_202_ACCEPTED)
        else:
            return Response({"error":{"code":f"update_{model_name}_error", "details":modelSerialData.errors}}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        cache_base_key = model_name + request.user.get_username()
        model_name  = self.model.__name__.lower()
        modelObj = self.get_object(request)
        modelObj.delete()
        delete_cache_key(cache_base_key)
        return Response({"message":f"{model_name} for user deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class UserCart(BaseStoreObjectsView):
    model               = Cart
    serializer_class    = CartSerializer
    paginate_serializer = gamesSerializerSimplified

class UserWishlist(BaseStoreObjectsView):
    model               = Wishlist
    serializer_class    = WishlistSerializer
    paginate_serializer = gamesSerializerSimplified


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
    cache_key              = get_cache_key(request)
    cache_vals             = cache.get("library" + cache_key)
    if cache_vals:
        return Response(cache_vals, status=status.HTTP_200_OK)
    gameInteractions       = GameInteraction.objects.filter(Q(user = request.user) & Q(in_library = True)).select_related('game').order_by('-purchase_date')
    cache_vals             = get_paginated(request, gameInteractions, GameInteractionSerializerSimplified)
    response = Response({"message": "library contents", "next":cache_vals[1], "previous":cache_vals[2], "count":cache_vals[3], "library":cache_vals[0]}, status=status.HTTP_200_OK)
    cache.set("library" + cache_key, response.data, timeout=2592000)
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
        
        delete_cache_key("transaction" + username)
        Subject    = f'Wallet recharge confirmation for {username}'
        message    = wallet_recharge_successful_email({"username":username, "recharge_amount":amount, "transaction_id":walletTransaction.get_transaction_id(), "wallet_balance":wallet.get_balance()})
            
        recipients = [request.user.get_email()]

        mail_result, _ = mail_service(Subject, message, recipients)

        if not mail_result:
            return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        walletSerial = WalletSerializer(wallet).data

        return Response({"message":"wallet recharged successfully", "wallet":walletSerial}, status=status.HTTP_200_OK)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet_transaction(request):
    cache_key  = get_cache_key(request)
    cache_vals = cache.get("transaction" + cache_key)
    if cache_vals:
        return Response({"message":"wallet transaction details for user", "next":cache_vals[1], "previous":cache_vals[2], "count":cache_vals[3], "transactions":cache_vals[0]}, status=status.HTTP_200_OK)
    
    wallet, _              = Wallet.objects.get_or_create(user = request.user)
    wallet_transactions    = WalletTransaction.objects.filter(wallet= wallet).order_by('-created_at')
    cache_vals             = get_paginated(request, wallet_transactions, WalletTransactionSerializer)
    cache.set("transaction" + cache_key, cache_vals, timeout=3600)
    return Response({"message":"wallet transaction details for user", "next":cache_vals[1], "previous":cache_vals[2], "count":cache_vals[3], "transactions":cache_vals[0]}, status=status.HTTP_200_OK)
    

@api_view(["GET", "POST"])
@permission_classes([IsAdminOrReadOnly])
@parser_classes([MultiPartParser])
def sale_view(request):
    if request.method == "GET":
        sales        = Sale.objects.all()
        sales_serial = SaleSerializer(sales, many=True)
        return Response({"message":"GamesHub sales details", "sales":sales_serial.data}, status=status.HTTP_200_OK)

    if request.method == "POST":
        try:
            serial_data  = SaleSerializer(data=request.data)
            if serial_data.is_valid():
                serial_data.save()
                return Response({"message":"sale data saved successfully", "sale":serial_data.data}, status=status.HTTP_201_CREATED)
            return Response({"error":{"code":"validation_error", "details":serial_data.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except Exception as e:
            return Response({"error":{"code": f"sale_endpoint_error","message": "internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
@parser_classes([MultiPartParser])
def sale_detail_view(request, pk):
    if request.method == "GET":
        try:
            sale        = Sale.objects.get(pk = pk)
            sale_serial = SaleSerializerDetail(sale)
            return Response({"message":"sale detail", "sale":sale_serial.data}, status=status.HTTP_200_OK)
        except Sale.DoesNotExist:
            return Response({"error": {"code": "do_not_exist","message": f"sale object do not exist"}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": {"code":"manage_sale_failed", "message":"errors in sale manage get endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    if request.method == "PATCH":
        try:
            sale        = Sale.objects.get(pk = pk)
            sale_serial = SaleSerializerDetail(sale, data = request.data, partial=True)
            if sale_serial.is_valid():
                sale_serial.save()
                return Response({"message":"sale data saved successfully", "sale":sale_serial.data}, status=status.HTTP_201_CREATED)
            return Response({"error":{"code":"validation_error", "details":sale_serial.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Sale.DoesNotExist:
            return Response({"error": {"code": "do_not_exist","message": f"sale object do not exist"}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": {"code":"manage_sale_failed", "message":"errors in sale manage patch endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    if request.method == "DELETE":
        try:
            Sale.objects.get(pk = pk).delete()
            return Response({"message":"sale object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Sale.DoesNotExist:
            return Response({"error": {"code": "do_not_exist","message": f"sale object do not exist"}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": {"code":"manage_sale_failed", "message":"errors in sale manage delete endpoint"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
