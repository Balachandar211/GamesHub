from  .microservices import mail_service
from GamesHub.celery import app
from .models import BlacklistedAccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.utils import timezone
from Store.models import Game
from django.contrib.auth import get_user_model
from GamesHub import settings
User = get_user_model()

@app.task(name='send_daily_promotional_email')
def send_daily_promotional_email():
    userObjs = User.objects.all()
    for inv_user in userObjs:
        user_name = inv_user.get_username()
        email     = inv_user.get_email()
        message   = ""
        gameObjs = Game.objects.filter(wishlist__user=inv_user)
        for game in gameObjs:
            if game.get_discount() != 0:
                message += "&#x2022; <b>" + game.get_name() + "</b> - now at Rs <b>" + str(game.get_actual_price()) + "</b> (Save " + str(game.get_discount()) + "%)" + "<br>"
        
        if message != "":
            message = f"<b>Hey {user_name} &#128075;</b><br><br>Your wishlist just got hotter! &#128293; Check out these epic deals:<br><br>" + message + "<br>Don’t miss out — these prices won’t last forever!<br><br>Cheers<br>Team GamesHub &#127918;"
            
            result, _ = mail_service(Subject="Items from your wishlist on Sale!", message=message, recepients=[email])
            
    return "Promotional mails sent"

@app.task(name='delete_expired_access_tokens')
def delete_expired_access_tokens():
    BlacklistedAccessToken.objects.filter(blacklisted_time__lte = timezone.localtime() - settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")).delete()
    return "Expired access tokens deleted"

@app.task(name='delete_expired_refresh_token')
def delete_expired_refresh_token():
    one_day_ago = timezone.localtime() - settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt=one_day_ago)
    BlacklistedToken.objects.filter(token__in=expired_tokens).delete()
    expired_tokens.delete()
    return "Expired refresh tokens deleted"

@app.task(name="delete_deleted_users")
def delete_deleted_users():
    inactiveUsers = User.objects.filter(is_active = False)
    timeLine      = timezone.localtime() - settings.USER_RECOVERABLE_TIME
    for inactiveUser in inactiveUsers:
        if inactiveUser.last_login and inactiveUser.last_login <= timeLine:
            inactiveUser.delete()
    
    return "Deleted deleted users of more than 30 days"