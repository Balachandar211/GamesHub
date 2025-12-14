from rest_framework.pagination import LimitOffsetPagination
from Store.models import Game
from Store.serializers import gamesSerializer
import requests
import os
from django.core.cache import cache
from django.db.models import Q, F
from .models import UpvoteDownvoteControl
from GamesHub.settings import CACHE_ENV

redis_client = cache.client.get_client()

def delete_cache_key(base_key):
    keys = list(redis_client.scan_iter(f":1:{base_key}*"))

    if keys:
        redis_client.delete(*keys)
    
    if base_key == "comment":
        delete_cache_key("post")
        delete_cache_key("ticket")


# Microservice for Search
def search(request, game_ids):
    path_key = request.path

    paginator = LimitOffsetPagination()
    cache_key   = CACHE_ENV + "game" + path_key + "CACHED_GAMES"
    cached_vals = cache.get(cache_key)

    if not request.GET and cached_vals and not game_ids:
        cache_vals = cached_vals
    elif not request.GET and not cached_vals:
        if game_ids is None:
            gameObjs = Game.objects.all().order_by('id')
        else:
            gameObjs = Game.objects.filter(id__in = game_ids).order_by('id')
        paginated_games = paginator.paginate_queryset(gameObjs, request)
        gamesSerial = gamesSerializer(paginated_games, many=True)
        gamesSerial = gamesSerial.data
        cache_vals  = gamesSerial, paginator.get_next_link(), paginator.get_previous_link(), paginator.count
        if not game_ids:
            cache.set(cache_key, cache_vals, timeout=2592000)
    else:
        query_params = request.GET.dict()
        sorted_pairs = str(sorted(tuple(query_params.items()), key=lambda x: x[1].lower()))
        cache_key    = CACHE_ENV + "game" + path_key + sorted_pairs
        cached_vals = cache.get(cache_key)

        if cached_vals:
            cache_vals = cached_vals
        else:
            filters = Q()

            if game_ids:
                filter &= Q(id__in = game_ids)

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
            cache_vals  = gamesSerial, paginator.get_next_link(), paginator.get_previous_link(), paginator.count
            if not game_ids:
                cache.set(cache_key, cache_vals, timeout=2592000)

    return cache_vals


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
            

def validate_vote_value(attrs, model):
    upvote = attrs.get(f"upvote_{model}")
    downvote = attrs.get(f"downvote_{model}")

    truthy = ['1', 1, True, "true"]

    if upvote in truthy and downvote in truthy:
        return True

    return False


def update_voting_field(instance, validated_data, content_type, model, request_user, model_obj):

    upvote_downvote, created  = UpvoteDownvoteControl.objects.get_or_create(user=request_user,content_type=content_type,object_id=instance.id)

    if created:
        if validated_data.get(f"upvote_{model}") in ['1', 1, True, "true"]:
            upvote_downvote.set_vote_type(True)
            upvote_downvote.save()
            model_obj.update(upvote=F('upvote') + 1)
        if validated_data.get(f"downvote_{model}") in ['1', 1, True, "true"]:
            upvote_downvote.set_vote_type(False)
            upvote_downvote.save()
            model_obj.update(downvote=F('downvote') + 1)
    else:
        vote_type   = upvote_downvote.get_vote_type()

        if validated_data.get(f"upvote_{model}") in ['1', 1, True, "true"] and not vote_type:
            upvote_downvote.set_vote_type(True)
            upvote_downvote.save()
            model_obj.update(upvote=F('upvote') + 1, downvote=F('downvote') - 1)
        if validated_data.get(f"downvote_{model}") in ['1', 1, True, "true"] and vote_type:
            upvote_downvote.set_vote_type(False)
            upvote_downvote.save()
            model_obj.update(upvote=F('upvote') - 1, downvote=F('downvote') + 1)
        
        if validated_data.get(f"upvote_{model}") in ['1', 1, True, "true"] and vote_type:
            upvote_downvote.delete()
            model_obj.update(upvote=F('upvote') - 1)
        
        if validated_data.get(f"downvote_{model}") in ['1', 1, True, "true"] and not vote_type:
            upvote_downvote.delete()
            model_obj.update(downvote=F('downvote') - 1)


    instance.refresh_from_db(fields=['upvote', 'downvote'])
    return instance
    

