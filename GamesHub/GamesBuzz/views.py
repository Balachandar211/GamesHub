from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Store.models import Game, GamesMedia, Cart, Wishlist, WalletTransaction, Wallet
from Store.serializers import gamesSerializerSimplified, gamesSerializer, GameMediaSerializer
from django.urls import reverse
from utills.microservices import mail_service, delete_cache_key
from .models import GameInteraction
from datetime import datetime
from django.core.cache import cache
from .serializers import GameInteractionSerializerSimplified
from django.db.models import Q
from utills.email_helper import game_bought_details
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from rest_framework.exceptions import UnsupportedMediaType
from decimal import Decimal

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase(request):
    game_ids = request.data.get("id")

    if game_ids is None or game_ids == '':
        return Response({"error":{"code":"not_null_constraint", "message":"buying ids cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(game_ids, list):
        return Response({"error": {"code":"incorrect_datatype", "message":"games should be passed as a list"}}, status=status.HTTP_400_BAD_REQUEST)
    
    to_buy        = {}
    na_list       = {}
    total_price   = 0

    for id in request.data.get("id"):
        try:
            gameObj      = Game.objects.get(id = id)
            try:
                GameInteraction.objects.get(game = gameObj, user = request.user)
                na_list[id]  = "Game already available in library"
            except GameInteraction.DoesNotExist:
                to_buy[id]   = gamesSerializerSimplified(gameObj).data
                total_price += gameObj.get_price()
            except Exception:
                return Response({"error":{"code":"purchase_section_fail", "message":"errors in purchase section"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Game.DoesNotExist:
            na_list[id]  = "Game not available enter valid id"
        except (ValueError, ValidationError):
            na_list[id]  = "Game not available enter valid id with correct format"
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception:
            return Response({"error":{"code":"purchase_section_fail", "message":"errors in purchase section"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
    endpoint = reverse('buy')

    full_url = request.build_absolute_uri(endpoint)
    
    return Response({"message": "redirect to endpoint with this payload except 'invalid_or_owned_games'", "url":full_url, "Games_to_be_baught":to_buy, "invalid_or_owned_games":na_list, "total_price": round(total_price, 2)}, status=status.HTTP_200_OK)


@transaction.atomic
def buy_atomic(request, use_wallet, wallet):
    transaction_ids  = {}
    na_list          = {}
    total            = 0
    games_bought     = []
    
    balance    = wallet.get_balance()
    
    for id in request.data.get("id"):
        try:
            gameObj      = Game.objects.get(id = id)
            try:
                GameInteraction.objects.get(game = gameObj, user = request.user)
                na_list[id]  = "Game already available in library"
            except GameInteraction.DoesNotExist:
                try:
                    price                 = Decimal(str(gameObj.get_price()))
                    total                += price
                    gameBoughtObj         = GameInteraction.objects.create(user = request.user, game = gameObj, purchase_date = datetime.now(), purchase_price = price)
                    games_bought.append(gameBoughtObj)
                    transaction_ids[id]   = gameBoughtObj.get_transaction_id()
                    if use_wallet:
                        if balance - price >= 0:
                            balance -= price
                            WalletTransaction.objects.create(wallet= wallet, amount=price, payment_type = 3)
                        else:
                            raise ValueError(f"not enough fund in wallet, need Rs {abs(balance - price)} please reacharge and continue")

                except IntegrityError as e:
                    raise Exception("model integrity error")

                try:
                    cart         = Cart.objects.get(user = request.user)
                    cart.games.remove(gameObj)
                except Cart.DoesNotExist:
                    pass #nothing needed to be done as there is no cart

                try:
                    wishlist     = Wishlist.objects.get(user = request.user)
                    wishlist.games.remove(gameObj)
                except Wishlist.DoesNotExist:
                    pass #nothing needed to be done as there is no wishlist


        except Game.DoesNotExist:
            na_list[id]  = "Game not available enter valid id"
        except ValidationError:
            na_list[id]  = "Game not available enter valid id with correct format"
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    
    response_message = f"Games requested bought successfully!" if len(transaction_ids) > 0 else "Nothing to buy"

    return transaction_ids, games_bought, total, response_message, na_list


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def buy(request):
    game_ids      = request.data.get("id")
    use_wallet    = True if request.data.get("use_wallet") in [1, '1', "true", True] else False
    wallet        = Wallet.objects.get(user=request.user)

    if game_ids is None or game_ids == '':
        return Response({"error":{"code":"not_null_constraint", "message":"buying ids cannot be empty"}}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(game_ids, list):
        return Response({"error": {"code":"incorrect_datatype", "message":"games should be passed as a list"}}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        transaction_ids, games_bought, total, response_message, na_list = buy_atomic(request, use_wallet, wallet)
    except ValueError as e:
        return Response({"error": {"code": "insufficient_funds", "message": str(e)}},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":{"code":"internal_buying_point_error", "message":"internal server error"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if len(transaction_ids) > 0:
        username   = request.user.get_username()
        Subject    = f'Game{'s' if len(transaction_ids) > 1 else ''} Purchase Confirmation'
        message    = game_bought_details({"username":username, "gamesInteractions":games_bought, "total":total, "use_wallet":use_wallet, "wallet_balance":wallet.get_balance()})
        
        recepients = [request.user.get_email()]

        mail_result, _ = mail_service(Subject, message, recepients)
        delete_cache_key("transaction" + username)
        
        if not mail_result:
            return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed but games bought added successfully"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    return Response({"message":response_message, "important_note":"these are not actual purchases", "transaction_ids":transaction_ids, "errors":na_list}, status=status.HTTP_200_OK)
       

@api_view(["GET"])
def games_detail(request, pk):
    if request.user.is_authenticated:
        key = "game" + request.user.get_username() + str(pk)
    else:
        key = "game" + "anonymous_user" + str(pk)

    cached_game = cache.get(key)
    if cached_game:
        return Response(cached_game, status=status.HTTP_200_OK)
            
    try:
        game  = Game.objects.get(pk = pk) 
        
        gameMedia       = GamesMedia.objects.filter(game = game)
        gameMediaSerial = GameMediaSerializer(gameMedia, many = True)

        if request.user.is_authenticated:
            gameInteractionUser           = GameInteraction.objects.filter(Q(game = game) & Q(user = request.user))
            gameInteractionSerialUser     = GameInteractionSerializerSimplified(gameInteractionUser, many = True)
            gameInteractionSerialDataUser = gameInteractionSerialUser.data
            library_flag                  = gameInteractionUser.exists()

            gameInteraction               = GameInteraction.objects.filter(Q(game = game) & ~Q(user = request.user))
            gameInteractionSerial         = GameInteractionSerializerSimplified(gameInteraction, many = True)
            gameInteractionSerialData     = gameInteractionSerial.data

            key = "game" + request.user.get_username() + str(pk)
        else:
            gameInteractionSerialDataUser = {}
            library_flag                  = False

            gameInteraction               = GameInteraction.objects.filter(Q(game = game))
            gameInteractionSerial         = GameInteractionSerializerSimplified(gameInteraction, many = True)
            gameInteractionSerialData     = gameInteractionSerial.data

            key = "game" + "anonymous_user" + str(pk)

        gameSerialData = gamesSerializer(game)
        gameData       = gameSerialData.data
    except Game.DoesNotExist:
        return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)
    except UnsupportedMediaType as e:
        return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    except Exception as e:
        return Response({"error":{"code":"game_detail_failed", "message":"please try back later"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    response = Response({"message": f"game detail for pk {pk}", "in_library":library_flag, "game":gameData, "game_media":gameMediaSerial.data, "user_comment": gameInteractionSerialDataUser, "comments":gameInteractionSerialData }, status=status.HTTP_200_OK)
    
    cache.set(key, response.data, timeout=3600)

    return Response({"message": f"game detail for pk {pk}", "in_library":library_flag, "game":gameData, "game_media":gameMediaSerial.data, "user_comment": gameInteractionSerialDataUser, "comments":gameInteractionSerialData }, status=status.HTTP_200_OK)
    


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def comment(request, pk):
    try:
        gameObj        = Game.objects.get(id = pk)
    except Game.DoesNotExist:
        return Response({"error":{"code":"do_not_exist", "message":f"no game with id {pk} exist"}}, status= status.HTTP_404_NOT_FOUND)
    
    try:
        gameInteration = GameInteraction.objects.get(game = gameObj, user = request.user)
    except GameInteraction.DoesNotExist:
        return Response({"error":{"code":"do_not_exist", "message":f"game is not present in library"}}, status= status.HTTP_404_NOT_FOUND)
    try:
        gameInterationSerial = GameInteractionSerializerSimplified(gameInteration, data = request.data, partial = True)

        if gameInterationSerial.is_valid():
            gameInterationSerial.save()
            return Response({"message":"Comment saved successfully!"}, status=status.HTTP_202_ACCEPTED)
        return Response({"errors":{"code":"validation_error", "details":gameInterationSerial.errors}}, status=status.HTTP_400_BAD_REQUEST)
    except UnsupportedMediaType as e:
        return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    except Exception:
        return Response({"error":{"code":"comment_section_fail", "message":"errors in comment section"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       