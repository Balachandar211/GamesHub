from rest_framework.pagination import LimitOffsetPagination
from Store.models import Game
from Store.serializers import gamesSerializer
from .models import Constants
import requests
import os
from django.core.cache import cache

# Microservice to get User and User Type
def requested_user(request):    
    if request.user and request.user.is_authenticated:
        if request.user.is_staff:
            greeting = f"admin user {request.user.get_username()}"
        else:
            greeting = f"user {request.user.get_username()}"
    else:
        greeting = "guest user"
        
    return greeting

# Microservice for Search
def search(request):
    paginator = LimitOffsetPagination()

    greeting = requested_user(request)
    
    cached_vals = cache.get("CACHED_GAMES")
    
    if not request.GET and cached_vals:
        gameObjs = cached_vals
    elif not request.GET and not cached_vals:
        gameObjs = Game.objects.all()
        cache.set("CACHED_GAMES", gameObjs, timeout=600)
    else:
        filters = {}

        if request.query_params.get('name') is not None:
            filters["name__icontains"] = request.query_params.get('name')
        if request.query_params.get('publishedDate') is not None:
            filters["publishedDate__lte"] = request.query_params.get('publishedDate')
        if request.query_params.get('price') is not None:
            filters["price__lte"] = request.query_params.get('price')
        if request.query_params.get('developer') is not None:
            filters["developer__icontains"] = request.query_params.get('developer')
        if request.query_params.get('discount') is not None:
            filters["discount__gte"] = request.query_params.get('discount')
        if request.query_params.get('rating') is not None:
            filters["rating__gte"] = request.query_params.get('rating')
        if len(request.GET.getlist('platforms')) != 0:
            filters["platforms__in"] = request.GET.getlist('platforms')
        if len(request.GET.getlist('genre')) != 0:
            filters["genre__in"] = request.GET.getlist('genre')

        cached_vals = cache.get(tuple(filters.keys()))

        if cached_vals:
            gameObjs = cached_vals
        else:
            gameObjs = Game.objects.filter(**filters)
            cache.set(tuple(filters.keys()), gameObjs, timeout=600)

    paginated_games = paginator.paginate_queryset(gameObjs, request)
    gamesSerial = gamesSerializer(paginated_games, many=True)
    return greeting, paginator, gamesSerial

# Microservice for transaction ID generator
def transaction_id_generator():
    transaction_obj = Constants.objects.get(variable="TRANSACTION_ID")
    transaction_id  = int(transaction_obj.get_value())
    transaction_id  += 1
    transaction_obj.set_value(str(transaction_id))
    transaction_obj.save()
    return int(transaction_id)

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