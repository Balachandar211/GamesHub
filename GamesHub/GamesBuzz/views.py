from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from Store.models import Game
from Store.serializers import gamesSerializerSimplified
from django.urls import reverse


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