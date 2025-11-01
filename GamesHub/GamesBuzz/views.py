from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Store.models import Game
from Store.serializers import gamesSerializerSimplified, gamesSerializer
from django.urls import reverse
from utills.microservices import requested_user, transaction_id_generator
from .models import GameInteraction
from datetime import datetime


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase(request):
    to_buy  = {}
    na_list = {}
    total_price = 0
    for id in eval(request.data.get("id")):
        try:
            gameObj      = Game.objects.get(id = id)
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
    for id in eval(request.data.get("id")):
        gameObj               = Game.objects.get(id = id)
        gameBoughtObj         = GameInteraction.objects.create(user = request.user, game = gameObj, purchase_date = datetime.now(), purchase_price = gameObj.get_price())
        gameBoughtObj.save()
        transaction_ids[id]   = transaction_id_generator()
    
    return Response({"message":"Games requested bought successfully!", "Transaction_IDs":transaction_ids}, status=status.HTTP_200_OK)
        

@api_view(["GET"])
def games_detail(request, pk):
    try:
        game           = Game.objects.get(pk = pk)
        gameSerialData = gamesSerializer(game)
        gameData       = gameSerialData.data
    except:
        gameData       = {}

    greeting, profile_picture = requested_user(request)

    return Response({"message": f"Hi {greeting}", "game":gameData, "Profile_Picture":profile_picture}, status=status.HTTP_200_OK)