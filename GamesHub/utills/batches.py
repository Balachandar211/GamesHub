from  .microservices import mail_service
from GamesHub.celery import app
from .models import BlacklistedAccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.utils import timezone
from datetime import timedelta
from Store.models import Game
from django.contrib.auth import get_user_model
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
            message = f"<b>Hey {user_name} 👋</b><br><br>Your wishlist just got hotter! 🔥 Check out these epic deals:<br><br>" + message + "<br>Don’t miss out — these prices won’t last forever!<br><br>Cheers<br>Team GamesHub 🎮"
            
            result, _ = mail_service(Subject="Items from your wishlist on Sale!", message=message, recepients=[email])
            
    return "Promotional mails sent"

@app.task(name='delete_expired_access_tokens')
def delete_expired_access_tokens():
    BlacklistedAccessToken.objects.filter(blacklisted_time__lte = timezone.localtime() - timedelta(minutes=30)).delete()
    return "Expired access tokens deleted"

@app.task(name='delete_expired_refresh_token')
def delete_expired_refresh_token():
    one_day_ago = timezone.localtime() - timedelta(days=1)
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt=one_day_ago)
    BlacklistedToken.objects.filter(token__in=expired_tokens).delete()
    expired_tokens.delete()
    return "Expired refresh tokens deleted"