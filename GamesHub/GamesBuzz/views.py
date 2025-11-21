from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Store.models import Game, GamesMedia, Cart, Wishlist
from Store.serializers import gamesSerializerSimplified, gamesSerializer, GameMediaSerializer
from django.urls import reverse
from utills.microservices import transaction_id_generator
from .models import GameInteraction
from datetime import datetime
from django.core.cache import cache
from .serializers import GameInteractionSerializerSimplified, GameInteractionSerializer
from django.db.models import Q
from utills.microservices import mail_service


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase(request):
    to_buy  = {}
    na_list = {}
    total_price = 0
    for id in request.data.get("id"):
        gameObj      = Game.objects.get(id = id)
        try:
            GameInteraction.objects.get(game = gameObj, user = request.user)
            na_list[id]  = "Game already available in library"
        except:
            try:            
                to_buy[id]   = gamesSerializerSimplified(gameObj).data
                total_price += gameObj.get_price()
            except:
                na_list[id]  = "Game not available enter valid list"
        
    endpoint = reverse('buy')

    full_url = request.build_absolute_uri(endpoint)
    
    return Response({"message": "redirect to endpoint with this payload except 'games_not_available'", "url":full_url, "Games_to_be_baught":to_buy, "games_not_available":na_list, "total_price": total_price}, status=status.HTTP_307_TEMPORARY_REDIRECT)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def buy(request):
    transaction_ids = {}
    na_list         = {}
    html_data       = ''
    total           = 0

    for id in request.data.get("id"):
        gameObj      = Game.objects.get(id = id)
        cart         = Cart.objects.get(user = request.user)
        wishlist     = Wishlist.objects.get(user = request.user)
        try:
            GameInteraction.objects.get(game = gameObj, user = request.user)
            na_list[id]  = "Game already available in library"
        except:
            cart.games.remove(gameObj)
            wishlist.games.remove(gameObj)
            transaction_id        = transaction_id_generator()
            transaction_ids[id]   = transaction_id
            price                 = gameObj.get_price()
            total                += price
            html_data += f"<tr><td>{gameObj.get_name()}</td><td>{transaction_id}</td><td>{price}</td></tr>"
            gameBoughtObj         = GameInteraction.objects.create(user = request.user, game = gameObj, purchase_date = datetime.now(), purchase_price = price, transaction_id = transaction_id)
            gameBoughtObj.save()
        
            respone_message = f"Games requested bought successfully!" if len(transaction_ids) > 0 else "Nothing to buy"

            if len(transaction_ids) > 0:

                Subject    = f'Game{'s' if len(transaction_ids) > 1 else ''} Purchase Confirmation'
                message    = f"""Hi <b>{request.user.get_username()},</b><br><br>
                                Thanks for your Purchase &#127918;, your transaction details are as below,<br><br>
                                <table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;'>
                                    <tr>
                                        <th>Game</th>
                                        <th>Transaction ID</th>
                                        <th>Price</th>
                                    <tr>
                                    {html_data}
                                </table><br>
                                Total : {total}<br><br>
                                <b>Game on,<br> — The GamesHub Team</b>"""
                
                recepients = [request.user.get_email()]

                mail_result, message_response = mail_service(Subject, message, recepients)
        
    return Response({"message":respone_message, "Transaction_IDs":transaction_ids, "errors":na_list}, status=status.HTTP_200_OK)
        

@api_view(["GET"])
def games_detail(request, pk):
    if request.method == "GET":
        try:
            cached_game = cache.get(pk)
            if cached_game:
                game = cached_game
            else:
                game  = Game.objects.get(pk = pk) 
                cache.set(pk, game, timeout=600)
            
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
            else:
                gameInteractionSerialDataUser = {}
                library_flag                  = False

                gameInteraction               = GameInteraction.objects.filter(Q(game = game))
                gameInteractionSerial         = GameInteractionSerializerSimplified(gameInteraction, many = True)
                gameInteractionSerialData     = gameInteractionSerial.data

            gameSerialData = gamesSerializer(game)
            gameData       = gameSerialData.data
        except Exception as e:
            gameData                      = {}
            gameInteractionSerialData     = {}
            gameInteractionSerialDataUser = {}
            library_flag                  = False

        return Response({"message": f"game detail for pk {pk}", "in_library":library_flag, "game":gameData, "game_media":gameMediaSerial.data, "user_comment": gameInteractionSerialDataUser, "comments":gameInteractionSerialData }, status=status.HTTP_200_OK)
    


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def comment(request, pk):
    try:
        gameObj        = Game.objects.get(id = pk)
    except:
        return Response({"error":f"no game with id {pk} exist"}, status= status.HTTP_404_NOT_FOUND)
    
    try:
        gameInteration = GameInteraction.objects.get(game = gameObj, user = request.user)
    except:
        return Response({"error":f"no game with id {pk} exist in library"}, status= status.HTTP_404_NOT_FOUND)

    gameInterationSerial = GameInteractionSerializer(gameInteration, data = request.data, partial = True)

    if gameInterationSerial.is_valid():
        gameInterationSerial.save()
        return Response({"message":"Comment saved successfully!"}, status=status.HTTP_202_ACCEPTED)
    return Response({"errors":gameInterationSerial.errors}, status=status.HTTP_400_BAD_REQUEST)
