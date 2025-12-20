from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Store.models import Game, GamesMedia, Cart, Wishlist, WalletTransaction, Wallet
from Store.serializers import gamesSerializerSimplified, gamesSerializer, GameMediaSerializer
from django.urls import reverse
from utills.microservices import mail_service, delete_cache_key
from .models import GameInteraction, Review
from datetime import datetime
from django.core.cache import cache
from .serializers import ReviewSerializer
from django.db.models import Q
from utills.email_helper import game_bought_details
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from rest_framework.exceptions import UnsupportedMediaType
from decimal import Decimal
from utills.baseviews import BaseRetrieveUpdateDestroyView, BaseListCreateView
from Support.models import Ticket
from Support.serializers import UserTicketSerializer
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.parsers import MultiPartParser
from django.utils import timezone
from datetime import timedelta
from GamesHub.settings import CACHE_ENV
import logging
from .documentation import purchase_schema, buy_schema, games_detail_schema, review_create_schema, review_list_schema, review_delete_schema, review_retrieve_schema, review_update_schema, game_ticket_create_schema

logger = logging.getLogger("gameshub") 

@purchase_schema
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
            except Exception as e:
                logger.error(f"purchase endpoint failure: {str(e)}", exc_info=True)
                return Response({"error":{"code":"purchase_section_fail", "message":"errors in purchase section"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Game.DoesNotExist:
            na_list[id]  = "Game not available enter valid id"
        except (ValueError, ValidationError):
            na_list[id]  = "Game not available enter valid id with correct format"
        except UnsupportedMediaType as e:
            return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        except Exception as e:
            logger.error(f"purchase endpoint failure: {str(e)}", exc_info=True)
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
                GameInteraction.objects.get(game = gameObj, user = request.user, in_library = True)
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

@buy_schema
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
        username = request.user.get_username()
        delete_cache_key("library" + username)
        if use_wallet:
            delete_cache_key("transaction" + username)
    except ValueError as e:
        return Response({"error": {"code": "insufficient_funds", "message": str(e)}},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"buy endpoint failure: {str(e)}", exc_info=True)
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
       
@games_detail_schema
@api_view(["GET"])
def games_detail(request, pk):
    if request.user.is_authenticated:
        key = f"{CACHE_ENV}:game:{request.user.get_username()}:{str(pk)}"
    else:
        key = f"{CACHE_ENV}:game:anonymous_user:{str(pk)}"

    cached_game = cache.get(key)
    if cached_game:
        return Response(cached_game, status=status.HTTP_200_OK)
            
    try:
        game  = Game.objects.get(pk = pk) 
        
        gameMedia       = GamesMedia.objects.filter(game = game)
        gameMediaSerial = GameMediaSerializer(gameMedia, many = True)

        if request.user.is_authenticated:
            gameInteractionUser           = GameInteraction.objects.filter(Q(game = game) & Q(user = request.user))
            library_flag                  = gameInteractionUser.exists()

        else:
            library_flag                  = False


        gameSerialData = gamesSerializer(game)
        gameData       = gameSerialData.data
    except Game.DoesNotExist:
        return Response({"error": {"code":"do_not_exist", "message":"game object doesn't exist"}}, status=status.HTTP_404_NOT_FOUND)
    except UnsupportedMediaType as e:
        return Response({"error": {"code": "unsupported_media_type", "message": str(e)}}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    except Exception as e:
        logger.error(f"game detail endpoint failure: {str(e)}", exc_info=True)
        return Response({"error":{"code":"game_detail_failed", "message":"please try back later"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    response = Response({"message": f"game detail for pk {pk}", "in_library":library_flag, "game":gameData, "game_media":gameMediaSerial.data}, status=status.HTTP_200_OK)
    
    cache.set(key, response.data, timeout=600)

    return Response({"message": f"game detail for pk {pk}", "in_library":library_flag, "game":gameData, "game_media":gameMediaSerial.data}, status=status.HTTP_200_OK)

@review_list_schema
@review_create_schema
class ReviewListCreateView(BaseListCreateView):
    model            = Review
    serializer_class = ReviewSerializer
        
    def get_queryset(self):
        try:
            gameobj         = Game.objects.get(pk = self.kwargs.get("pk"))
        except Game.DoesNotExist:
            raise NotFound(f"requested game with pk {self.kwargs.get("pk")} not found")
        
        return Review.objects.filter(game = gameobj).order_by("-created_at")

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        try:
            gameobj = Game.objects.get(pk = self.kwargs.get("pk"))
        except Game.DoesNotExist:
            raise NotFound(f"requested game with pk {self.kwargs.get("pk")} not found")

        if request.method == "POST":
            if not GameInteraction.objects.filter(user=request.user, game=gameobj).exists():
                raise NotFound("user don't have game in his library so can't provide a review")
            
            if Review.objects.filter(user=request.user, game=gameobj).exists():
                raise RestValidationError("user already provided review for this game use patch to update")
            
        return {"game": gameobj}
    
@review_retrieve_schema
@review_update_schema
@review_delete_schema
class ReviewRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    model            = Review
    serializer_class = ReviewSerializer

    def get_object(self):
        object_id = self.kwargs.get("object_id")
        pk        = self.kwargs.get("pk")
        try:
            gameObj = Game.objects.get(id=object_id) 
            obj     = Review.objects.get(pk=pk, game=gameObj)
        except Game.DoesNotExist:
            raise NotFound(f"requested game with pk {pk} not found")
        except Review.DoesNotExist:
            raise NotFound(f"requested review with pk {pk} not linked to game {object_id}")
        self.check_object_permissions(self.request, obj)
        return obj

@game_ticket_create_schema
class GameTicketCreateView(BaseListCreateView):
    model             = Ticket
    serializer_class  = UserTicketSerializer
    http_method_names = ["post"]
    parser_classes    = [MultiPartParser]

    def get_extra_save_kwargs(self, request, *args, **kwargs):
        try:
            parent_object   = Game.objects.get(pk = kwargs.get("pk"))
            game_interation = GameInteraction.objects.get(user = request.user, game = parent_object, in_library = True)
        except Game.DoesNotExist:
            raise NotFound(f"requested Game with pk {kwargs.get("pk")} not found")
        except GameInteraction.DoesNotExist:
            raise RestValidationError("user doesn't have this game in his library")
        
        return {"game": parent_object, "library_object":game_interation}
    
    def create(self, request, *args, **kwargs):     
        issue_type = request.data.get("issue_type")

        try:
            issue_type = int(issue_type)
        except:
            return Response({"error": {"code": "validation_errors", "details": "issue type should be passed as 1 or 2 when raising an issue on a game"}},status=status.HTTP_400_BAD_REQUEST)
        
        if issue_type is None or issue_type not in [1, 2]:
            return Response({"error": {"code": "validation_errors", "details": "issue type should be passed as 1 or 2 when raising an issue on a game"}},status=status.HTTP_400_BAD_REQUEST)
           
        extra_kwargs = self.get_extra_save_kwargs(request, *args, **kwargs)

        if GameInteraction.objects.filter(user= request.user, game = extra_kwargs["game"]).count() > 1 and issue_type == 1:
            return Response({"error": {"code":"duplicate_transaction", "message":"user already returned this game in a previous ticket and got a refund can't process a refund again"}},status=status.HTTP_400_BAD_REQUEST)

        base_key = self.model.__name__.lower()

        serializer = self.serializer_class(data=request.data)

        game_interation = extra_kwargs.pop("library_object")
        
        if game_interation.purchase_date + timedelta(days = 14) < timezone.now():
            return Response({"error":{"code":"warranty_ended", "message":"requested game cannot be returned as ticket is raised after 14 days of buying game"}}, status=status.HTTP_404_NOT_FOUND)
                    
        if not serializer.is_valid():
            return Response({"error": {"code": "validation_errors", "details": serializer.errors}},status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(user=request.user, **extra_kwargs)
        delete_cache_key(base_key)
        return Response({"message": f"{self.model.__name__} has been saved successfully", self.model.__name__: serializer.data}, status=status.HTTP_201_CREATED)
