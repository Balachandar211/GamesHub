from rest_framework.pagination import LimitOffsetPagination
from Store.models import Game
from Store.serializers import gamesSerializer
from .models import Constants
import requests
import os
from django.core.cache import cache
from django.db.models import Q
from django.db import transaction


# Microservice for Search
def search(request):
    paginator = LimitOffsetPagination()
    
    cached_vals = cache.get("CACHED_GAMES")
    
    if not request.GET and cached_vals:
        cache_vals = cached_vals
    elif not request.GET and not cached_vals:
        gameObjs = Game.objects.all().order_by('id')
        paginated_games = paginator.paginate_queryset(gameObjs, request)
        gamesSerial = gamesSerializer(paginated_games, many=True)
        gamesSerial = gamesSerial.data
        cache_vals  = gamesSerial, paginator.get_next_link(), paginator.get_previous_link(), paginator.count
        cache.set("CACHED_GAMES", cache_vals, timeout=3600)
    else:
        query_params = request.GET.dict()
        sorted_pairs = sorted(tuple(query_params.items()), key=lambda x: x[1].lower())
        cached_vals = cache.get(sorted_pairs)

        if cached_vals:
            cache_vals = cached_vals
        else:
            filters = Q()

            if name := request.query_params.get('name'):
                filters &= Q(name__icontains = name.strip())
            if published_date := request.query_params.get('publishedDate'):
                filters &= Q(publishedDate__lte = published_date.strip())
            if price:= request.query_params.get('price'):
                try:
                    filters &= Q(price__lte = float(price.strip()))
                except:
                    pass # not needed as invalid data item
            if developer := request.query_params.get('developer'):
                filters &= Q(developer__icontains = developer.strip())
            if discount := request.query_params.get('discount'):
                try:
                    filters &= Q(discount__gte= float(discount.strip()))
                except:
                    pass # not needed as invalid data item
            if rating := request.query_params.get('rating'):
                try:
                    filters &= Q(rating__gte = float(rating.strip()))
                except:
                    pass # not needed as invalid data item
            if len(request.GET.getlist('platforms')) != 0:
                for p in request.GET.getlist('platforms'):
                    filters &= Q(platforms__icontains=p.strip())
            if len(request.GET.getlist('genre')) != 0:
                for g in request.GET.getlist('genre'):
                    filters &= Q(genre__icontains=g.strip())

            gameObjs = Game.objects.filter(filters).order_by('id')
            paginated_games = paginator.paginate_queryset(gameObjs, request)
            gamesSerial = gamesSerializer(paginated_games, many=True)
            gamesSerial = gamesSerial.data
            sorted_pairs = sorted(tuple(query_params.items()), key=lambda x: x[1].lower())
            cache_vals  = gamesSerial, paginator.get_next_link(), paginator.get_previous_link(), paginator.count
            cache.set(sorted_pairs, cache_vals, timeout=3600)

    return cache_vals

# Microservice for transaction ID generator
def transaction_id_generator():
    with transaction.atomic():
        constants = Constants.objects.select_for_update().get(variable="TRANSACTION_ID")
        current_id = int(constants.get_value())
        next_id = current_id + 1
        constants.set_value(str(next_id))
        constants.save()
        return next_id

# Microservice for transaction ID decrementor
def transaction_id_decrementor():
    with transaction.atomic():
        constants = Constants.objects.select_for_update().get(variable="TRANSACTION_ID")
        current_id = int(constants.get_value())
        next_id = current_id - 1
        constants.set_value(str(next_id))
        constants.save()
        return next_id

FLASK_MAILER_API_KEY = os.getenv("FLASK_MAILER_API_KEY")

# Microservice for Email servive
def mail_service(Subject, message, recepients):
    if False: #Logic to use django method if web service hosting platfors allow SMTP traffic
        try:
            send_mail(
                subject=Subject,
                message='',
                html_message= message,
                from_email='GamesHub <gameshub.test@gmail.com>',
                recipient_list=[recepients],
                fail_silently=False,
                )
            
            return True, "Email sent successfully"
        except:
            return False, "Email sending failed"
    else:

            url = "https://gameshubmailer.pythonanywhere.com/mailer"
            headers = {
                "Content-Type": "application/json",
                "API-Key": FLASK_MAILER_API_KEY
            }
            payload = {
                "Subject": Subject,
                "Recepient": recepients,
                "Body": message
            }

            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                return True, "Email sent successfully"
            else:
                return False, "Email sending failed"