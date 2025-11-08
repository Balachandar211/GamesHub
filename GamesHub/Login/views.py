from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from .models import OTP
from .serializers import userSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import random
import time
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from utills.microservices import mail_service
import requests
import os
from utills.models import BlacklistedAccessToken
from django.utils import timezone
from .documentation import signup_schema, login_schema
User = get_user_model()

EMAIL_CHECKER_API_KEY = os.getenv("EMAIL_CHECKER_API_KEY")

@signup_schema
@api_view(["POST"])
@parser_classes([MultiPartParser])
def SignUp(request):
    if User.objects.filter(username = request.data.get("username")).exists():
        return Response({"message": "Username already Exists"}, status=status.HTTP_400_BAD_REQUEST)

    # API to check if email ID provided is valid
    email_check_response = requests.get(f"https://emailreputation.abstractapi.com/v1/?api_key={EMAIL_CHECKER_API_KEY}&email={request.data.get('email')}")
    
    email_check_response = email_check_response.json()

    if not email_check_response["email_deliverability"]["is_smtp_valid"]:
        return  Response({"error":"Incorrect email ID provided"}, status=status.HTTP_400_BAD_REQUEST)

    userObject     = userSerializer(data = request.data)

    if userObject.is_valid():
        userObject = userObject.save()
        refresh = RefreshToken.for_user(userObject)

        Subject    = f'&#127918; Welcome to GamesHub, {request.data.get('username')}!'
        message    = f'''Hi <b>{request.data.get('username')},</b><br><br>
                         Welcome to GamesHub — where epic adventures, legendary loot, and exclusive titles await!<br><br>
                        &#128377; Whether you're into pixel-perfect indies or blockbuster AAA hits,
                        we've got something for every kind of gamer.<br><br>
                        &#128293; Discover trending releases, hidden gems, and curated collections tailored to your playstyle.<br><br>
                        &#127873; Plus, enjoy early access deals, wishlist alerts, and community-powered reviews — all in one sleek hub.
                        Your next favorite game is just a click away. Let the quest begin!<br><br>
                        <b>Game on,<br> — The GamesHub Team</b>'''
        
        recepients = [request.data.get('email')]

        mail_result, message_response = mail_service(Subject, message, recepients)

        if not mail_result:
            Response({"error":"Mailer job failed!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = Response({"message": f"User {request.data.get('username')} added successfully", "username":userObject.get_username(), "profile_picture":userObject.get_profilePicture(), "Access_Token":str(refresh.access_token)}, status=status.HTTP_201_CREATED)
    
        response.set_cookie(
                key='Refresh_Token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age= 24 * 60 * 60,
                path="/user/session/"
            )
        
        return response
    
    return Response({"error":userObject.errors}, status=status.HTTP_400_BAD_REQUEST)

@login_schema
@api_view(["POST"])
def Login(request):
    try:
        userObj = User.objects.get(username = request.data.get("username"))
        if userObj.check_password(request.data.get("password")):
            refresh = RefreshToken.for_user(userObj)

            response = Response({"message": f"User {userObj.get_username()} logged in", "username":userObj.get_username(), "profile_picture":userObj.get_profilePicture(), "Access_Token":str(refresh.access_token)}, status=status.HTTP_200_OK)

            response.set_cookie(
                key='Refresh_Token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age= 24 * 60 * 60,
                path="/user/session/"
            )

            return response
        else:
            return Response({"message":f"Incorrect password for user {userObj.get_username()}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message":"username not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(["POST"])
def Forgot_Password(request):
    if "OTP" in request.data:
        otp      = request.data.get("OTP")
        try:
            userObj  = User.objects.get(username = request.data.get("username"))
            otpObj   = OTP.objects.get(account = request.data.get("username"))
            gen_otp, time_gen = otpObj.get_details()

            if int(otp) == gen_otp and (time_gen + 300 >= int(time.time())):
                userObj.set_password(request.data.get("password"))
                userObj.save()
                otpObj.delete()
                return Response({"message": f"Password change successfull for account {request.data.get("username")} please continue login"}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"message": "OTP either expired or incorrect"}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            print(e)
            return Response({"message": "Incorrect username entered or OTP not generated for this user"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        try:
            userObj  = User.objects.get(username = request.data.get("username"))
            email_id = userObj.get_email()
            otp_num  = random.randint(1000, 9999)

            if OTP.objects.filter(account = request.data.get("username")).exists():
                otpObj   = OTP.objects.get(account = request.data.get("username"))
                otpObj.set_details(otp_num, time.time())
            else:    
                otpObj   = OTP(otp=otp_num, account = request.data.get("username"), time = time.time())
            otpObj.save()

            Subject    = 'GamesHub Account Recovery'
            message    = f'Your otp to reset password for account <b>{request.data.get("username")}</b> is <b>{otp_num}</b>'
            recepients = [email_id]

            mail_result, message_response = mail_service(Subject, message, recepients)

            if not mail_result:
                Response({"errors":"Mailer job failed!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message":f"otp sent to {email_id} for password reset for account {request.data.get("username")}"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"message":f"Incorrect Username {request.data.get("username")}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def extendSession(request):
    refresh   = request.COOKIES.get('Refresh_Token')
    if not refresh:
        return Response({"message":"Refresh token cookie not found"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh_token    = RefreshToken(refresh)
        blacklist_access = BlacklistedAccessToken(access_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1], blacklisted_time =  timezone.now())
        blacklist_access.save()

        refresh_token.blacklist()

        refresh = RefreshToken.for_user(request.user)

        response = Response({"message":"Access Token generated successfully", "Access_Token":str(refresh.access_token)}, status=status.HTTP_200_OK)

        response.set_cookie(
                key='Refresh_Token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age= 24 * 60 * 60,
                path="/user/session/"
            )

        return response
    except:
        return Response({"message":"Refresh token incorrect or expired"}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh   = request.COOKIES.get('Refresh_Token')
    if refresh is None:
        return Response({"message":"Refresh token cookie not found"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_name     = request.user.get_username()
        refresh_token = RefreshToken(refresh)
        blacklist_access = BlacklistedAccessToken(access_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1], blacklisted_time =  timezone.now())
        blacklist_access.save()
        refresh_token.blacklist()
        response = Response({"message":f"user {user_name} logged out successfully!"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('Refresh_Token', path='/user/session/')

        return response
    except Exception as e:
        print(e)
        return Response({"message":"Refresh token incorrect or expired"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    userObj  = request.user
    email_id = userObj.get_email()
    username = request.user.get_username()

    if request.data.get("OTP") is None:
        otp_num  = random.randint(1000, 9999)

        if OTP.objects.filter(account = username).exists():
            otpObj   = OTP.objects.get(account = username)
            otpObj.set_details(otp_num, time.time())
        else:    
            otpObj   = OTP(otp=otp_num, account = username, time = time.time())
        otpObj.save()

        
        Subject    = 'GamesHub Account Deletion'
        message    = f'Your otp to delete account is <b>{otp_num}</b>'
        recepients = [email_id]

        mail_result, message_response = mail_service(Subject, message, recepients)

        if not mail_result:
            Response({"errors":"Mailer job failed!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"OTP created successfully for account deletion for user {username}"}, status=status.HTTP_201_CREATED)

    else:
        otp      = request.data.get("OTP")

        if int(request.data.get("delete_permanently")) == 1:
            
            try:
                otpObj   = OTP.objects.get(account = username)
                gen_otp, time_gen = otpObj.get_details()
                
                if int(otp) == gen_otp and (time_gen + 300 >= int(time.time())):
                    if check_password(request.data.get("password"), userObj.get_password()):
                        userObj.delete()
                        otpObj.delete()

                        Subject    = 'GamesHub Account Deletion Confirmation'
                        message    = f'Your user account <b>{username}</b> deleted permanently'
                        recepients = [email_id]

                        mail_result, message_response = mail_service(Subject, message, recepients)

                        if not mail_result:
                            Response({"errors":"Mailer job failed!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                        return Response({"message": f"user account {username} deleted permanently"}, status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({"message": f"incorrect password for user account {username}"}, status=status.HTTP_400_BAD_REQUEST)
                                   
                else:
                    return Response({"message": "OTP either expired or incorrect"}, status=status.HTTP_400_BAD_REQUEST)


            except Exception as e:
                return Response({"message": "Incorrect username entered or OTP not generated for this user"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                otpObj   = OTP.objects.get(account = username)
                gen_otp, time_gen = otpObj.get_details()
                
                if int(otp) == gen_otp and (time_gen + 300 >= int(time.time())):
                    userObj.change_status()
                    userObj.save()

                    Subject    = 'GamesHub Account Deletion Confirmation'
                    message    = f'Your user account <b>{username}</b> deleted successfully and can be recovered within 30 days'
                    recepients = [email_id]

                    mail_result, message_response = mail_service(Subject, message, recepients)

                    if not mail_result:
                        Response({"errors":"Mailer job failed!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    return Response({"message": f"user account {username} deleted successfully and can be recovered within 30 days"}, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({"message": "OTP either expired or incorrect"}, status=status.HTTP_400_BAD_REQUEST)


            except Exception as e:
                return Response({"message": "Incorrect username entered or OTP not generated for this user"}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_user(request):
    userObj            = request.user
    if request.data.get("password") is not None:
        return Response({"error": "use forgot_password endpoint to update password"}, status=status.HTTP_400_BAD_REQUEST)
    allowed_keys = ['first_name', 'last_name', 'profilePicture', 'email', 'phoneNumber']
    if not set(request.data.keys()).issubset(allowed_keys):
        unexpected = set(request.data.keys()) - set(allowed_keys)
        return Response({"error": f"unexpected keys {unexpected}"}, status=status.HTTP_400_BAD_REQUEST)

    userObjectSerial   = userSerializer(userObj, data = request.data, partial=True)
    if userObjectSerial.is_valid():
        userObjectSerial.save()
        return Response({"message": f"user {request.user.get_username()} updated successfully!"}, status=status.HTTP_202_ACCEPTED)
    return Response({"error": userObjectSerial.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def recover_user(request):
    if "OTP" in request.data:
        otp      = request.data.get("OTP")
        try:
            userObj  = User.objects.get(username = request.data.get("username"))
            otpObj   = OTP.objects.get(account = request.data.get("username"))
            gen_otp, time_gen = otpObj.get_details()

            if int(otp) == gen_otp and (time_gen + 300 >= int(time.time())):
                if check_password(request.data.get("password"), userObj.get_password()):
                    userObj.change_status()
                    userObj.save()
                    otpObj.delete()

                    Subject    = 'GamesHub Account Recovery'
                    message    = f'Your account <b>{request.data.get("username")}</b> recovered successfully!'
                    recepients = [email_id]

                    mail_result, message_response = mail_service(Subject, message, recepients)

                    if not mail_result:
                        Response({"errors":"Mailer job failed!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    return Response({"message": f"account recovery successfull for {request.data.get("username")}"}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({"message": f"Incorrect password for account {request.data.get("username")}"}, status=status.HTTP_400_BAD_REQUEST)            
            else:
                return Response({"message": "OTP either expired or incorrect"}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            print(e)
            return Response({"message": "Incorrect username entered or OTP not generated for this user"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        try:
            userObj  = User.objects.get(username = request.data.get("username"))
            email_id = userObj.get_email()
            otp_num  = random.randint(1000, 9999)

            if OTP.objects.filter(account = request.data.get("username")).exists():
                otpObj   = OTP.objects.get(account = request.data.get("username"))
                otpObj.set_details(otp_num, time.time())
            else:    
                otpObj   = OTP(otp=otp_num, account = request.data.get("username"), time = time.time())
            otpObj.save()

            Subject    = 'GamesHub Account Recovery'
            message    = f'Your otp to recover account <b>{request.data.get("username")}</b> is <b>{otp_num}</b>'
            recepients = [email_id]

            mail_result, message_response = mail_service(Subject, message, recepients)

            if not mail_result:
                Response({"errors":"Mailer job failed!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message":f"otp sent to {email_id} for account recovery for user account {request.data.get("username")}"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"message":f"Incorrect Username {request.data.get("username")}"}, status=status.HTTP_400_BAD_REQUEST)

