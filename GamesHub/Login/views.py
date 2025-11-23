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
from .documentation import signup_schema, login_schema, extend_session_schema, update_user_schema, logout_session_schema, recover_user_schema, delete_user_schema, forgot_password_schema
from GamesHub.settings import COOKIE_LIFETIME
from utills.email_helper import signup_email, forgot_password_email, password_change_success_email, account_recovery_success_email, recover_account_email, user_deletion_email, user_deletion_confirmation, recoverable_deletion_confirmation
from rest_framework_simplejwt.exceptions import TokenError
import secrets
from utills.storage_supabase import delete_from_supabase
User = get_user_model()

EMAIL_CHECKER_API_KEY = os.getenv("EMAIL_CHECKER_API_KEY")


@signup_schema
@api_view(["POST"])
@parser_classes([MultiPartParser])
def SignUp(request):
    if request.data.get("username") is None or request.data.get("username") == '':
        return Response({"error": {"code":"not_null_constraint", "message":"username cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

    if request.data.get("email") is None or request.data.get("email") == '':
        return Response({"error": {"code":"not_null_constraint", "message":"email id cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

    if request.data.get("password") is None or request.data.get("password") == '':
        return Response({"error": {"code":"not_null_constraint", "message":"password cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

    # API to check if email ID provided is valid
    try:
        email_check_response = requests.get(f"https://emailreputation.abstractapi.com/v1/?api_key={EMAIL_CHECKER_API_KEY}&email={request.data.get('email')}", timeout=5)
        
        email_check_response = email_check_response.json()
        if not email_check_response["email_deliverability"]["is_smtp_valid"]:
            return  Response({"error":{"code": "invalid_email", "message":"incorrect email id provided"}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except (requests.RequestException, ValueError):
        return  Response({"error":{"code":"mail_reputation_server_not_reachable", "message":"email validation service unavailable"}}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    
    if User.objects.filter(username__iexact = request.data.get("username")).exists():
        return Response({"error":{"code":"username_integrity_error", "message":"username already exists"}}, status=status.HTTP_409_CONFLICT)

    userObject     = userSerializer(data = request.data)

    if userObject.is_valid():
        user = userObject.save()
        refresh = RefreshToken.for_user(user)

        Subject    = f'Welcome to GamesHub, {user.get_username()}!'
        message    = signup_email({"username": user.get_username()})
        
        recipients = [user.get_email()]

        mail_result, _ = mail_service(Subject, message, recipients)

        if not mail_result:
            return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = Response({"message": f"User {user.get_username()} added successfully", "user":{ "username":user.get_username(), "profile_picture":user.get_profilePicture()}, "access_token":str(refresh.access_token)}, status=status.HTTP_201_CREATED)
    
        response.set_cookie(
                key='Refresh_Token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age= COOKIE_LIFETIME,
                path="/user/session/"
            )
        
        return response
    
    return Response({"error":{"code": "validation_error", "message": "invalid input data", "details": userObject.errors}}, status=status.HTTP_400_BAD_REQUEST)

@login_schema
@api_view(["POST"])
def Login(request):
    if request.data.get("username") is None:
        return Response({"error": {"code":"not_null_constraint", "message":"username cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

    if request.data.get("password") is None:
        return Response({"error": {"code":"not_null_constraint", "message":"password cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

    try:
        userObj = User.objects.get(username__iexact = request.data.get("username"))

        if not userObj.is_active:
            return Response({"error": {"code":"recovery_needed", "message":"requested user is inactive please send a recovery request"}}, status=status.HTTP_400_BAD_REQUEST)

        if userObj.check_password(request.data.get("password")):
            refresh = RefreshToken.for_user(userObj)
            userObj.set_last_login()
            userObj.save()
            response = Response({"message": f"User {userObj.get_username()} logged in", 
                                 "user": {
                                    "username": userObj.get_username(),
                                    "profile_picture": userObj.get_profilePicture()
                                 },
                                 "access_token": str(refresh.access_token)
                                }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='Refresh_Token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age= COOKIE_LIFETIME,
                path="/user/session/"
            )

            return response
        else:
            return Response({"error":{"code":"invalid_credentials", "message":"incorrect password for user"}}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error":{"code":"username_not_found", "message":"requested username not found"}}, status=status.HTTP_404_NOT_FOUND)
    
@forgot_password_schema
@api_view(["POST"])
def Forgot_Password(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or username == '':
        return Response({"error": {"code":"not_null_constraint", "message":"username cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)


    if "OTP" in request.data:
        otp      = request.data.get("OTP")
        try:
            userObj  = User.objects.get(username__iexact = username)
            try:
                otpObj   = OTP.objects.get(account = username)
            except OTP.DoesNotExist:
                return Response({"error":{"code":"otp_not_found", "message":"OTP not generated for this user"}}, status=status.HTTP_404_NOT_FOUND)
    
            gen_otp, time_gen = otpObj.get_details()

            if password is None or password == '':
                return Response({"error": {"code":"not_null_constraint", "message":"password cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

            if secrets.compare_digest(str(otp), str(gen_otp)) and (time_gen + 300 >= int(time.time())):
                if password is None or password == '':
                    return Response({"error": {"code":"not_null_constraint", "message":"password cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

                userObj.set_password(password)
                userObj.save()
                otpObj.delete()
                email_id = userObj.get_email()

                Subject    = 'GamesHub Password Reset Successfull'
                message    = password_change_success_email({"username":userObj.get_username()})
                recepients = [email_id]

                mail_result, _ = mail_service(Subject, message, recepients)

                if not mail_result:
                    return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

                return Response({"message": f"password change successful, please continue login"}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"error":{"code":"otp_invalid_or_expired","message":"OTP either expired or incorrect"}}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error":{"code":"username_not_found", "message":"requested username not found"}}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        try:
            userObj  = User.objects.get(username__iexact = username)
            email_id = userObj.get_email()
            otp_num  = secrets.randbelow(900000) + 100000

            otpObj, _ = OTP.objects.get_or_create(account=username)
            otpObj.set_details(otp_num, time.time())
            otpObj.save()

            Subject    = 'GamesHub Password Reset'
            message    = forgot_password_email({"username":userObj.get_username(), "otp_num":otp_num})
            recepients = [email_id]

            mail_result, _ = mail_service(Subject, message, recepients)

            if not mail_result:
                return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message":f"otp sent successfully"}, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({"error":{"code":"username_not_found", "message":"requested username not found"}}, status=status.HTTP_404_NOT_FOUND)
    

@extend_session_schema
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def extendSession(request):
    refresh   = request.COOKIES.get('Refresh_Token')

    if not refresh:
        return Response({"error":{"code":"refresh_token_not_found", "message":"refresh token cookie not found"}}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh_token    = RefreshToken(refresh)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        try:
            access_token = auth_header.split()[1]
        except IndexError:
            return Response({"error":{"code":"invalid_authorization_header","message":"authorization header malformed"}}, status=status.HTTP_400_BAD_REQUEST)
        
        blacklist_access = BlacklistedAccessToken(access_token = access_token, blacklisted_time =  timezone.now())
        blacklist_access.save()

        refresh_token.blacklist()

        refresh = RefreshToken.for_user(request.user)
        request.user.set_last_login()
        request.user.save()

        response = Response({"message":"access Token generated successfully", "access_token":str(refresh.access_token)}, status=status.HTTP_200_OK)

        response.set_cookie(
                key='Refresh_Token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age= COOKIE_LIFETIME,
                path="/user/session/"
            )

        return response
    except TokenError:
        return Response({"error":{"code":"invalid_refresh_token","message":"refresh token incorrect or expired"}}, status=status.HTTP_401_UNAUTHORIZED)

@logout_session_schema    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh   = request.COOKIES.get('Refresh_Token')
    if not refresh:
        return Response({"error":{"code":"refresh_token_not_found", "message":"refresh token cookie not found"}}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_name     = request.user.get_username()
        refresh_token = RefreshToken(refresh)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        try:
            access_token = auth_header.split()[1]
        except IndexError:
            return Response({"error":{"code":"invalid_authorization_header","message":"authorization header malformed"}}, status=status.HTTP_400_BAD_REQUEST)
        
        blacklist_access = BlacklistedAccessToken(access_token = access_token, blacklisted_time =  timezone.now())
        blacklist_access.save()
        refresh_token.blacklist()

        response = Response({"message":f"user {user_name} logged out successfully!"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('Refresh_Token', path='/user/session/')

        return response
    except TokenError:
        return Response({"error":{"code":"invalid_refresh_token","message":"refresh token incorrect or expired"}}, status=status.HTTP_401_UNAUTHORIZED)


@delete_user_schema
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    userObj  = request.user
    email_id = userObj.get_email()
    username = request.user.get_username()

    if request.data.get("OTP") is None:
        otp_num  = secrets.randbelow(900000) + 100000

        otpObj, _ = OTP.objects.get_or_create(account=username)
        otpObj.set_details(otp_num, time.time())
        otpObj.save()
        
        Subject    = 'GamesHub Account Deletion'
        message    = user_deletion_email({"username":username, "otp_num":otp_num})
        recepients = [email_id]

        mail_result, _ = mail_service(Subject, message, recepients)

        if not mail_result:
            return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message":f"otp sent successfully"}, status=status.HTTP_201_CREATED)

    else:
        otp      = request.data.get("OTP")
            
        try:
            otpObj   = OTP.objects.get(account = username)
        except OTP.DoesNotExist:
            return Response({"error":{"code":"otp_not_found", "message":"OTP not generated for this user"}}, status=status.HTTP_404_NOT_FOUND)

        gen_otp, time_gen = otpObj.get_details()

        if secrets.compare_digest(str(otp), str(gen_otp)) and (time_gen + 300 >= int(time.time())):
            if request.data.get("delete_permanently")  and (request.data.get("delete_permanently") in (True, "true", "1", 1)):
                if check_password(request.data.get("password"), userObj.get_password()):
                    userObj.delete()
                    otpObj.delete()

                    Subject      = 'GamesHub Account Deletion Permanently'
                    message      = user_deletion_confirmation({"username":username})
                    response_msg = "user account deleted permanently"
                else:
                    return Response({"error":{"code":"invalid_credentials", "message":"incorrect password for user account"}}, status=status.HTTP_400_BAD_REQUEST)
       
            else:
                userObj.change_status()
                userObj.save()

                Subject      = 'GamesHub Account Deletion Confirmation'
                message      = recoverable_deletion_confirmation({"username":username})
                response_msg = "user account deleted and can be recovered within 30 days"

            recepients     = [email_id]
            mail_result, _ = mail_service(Subject, message, recepients)

            if not mail_result:
                return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": response_msg}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error":{"code":"otp_invalid_or_expired","message":"OTP either expired or incorrect"}}, status=status.HTTP_400_BAD_REQUEST)


        

@update_user_schema
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def update_user(request):
    userObj            = request.user
    if request.data.get("password") is not None:
        return Response({"error": {"code":"incorrect_end_point", "message": "use forgot_password endpoint to update password"}}, status=status.HTTP_400_BAD_REQUEST)
    
    allowed_keys = ['first_name', 'last_name', 'profilePicture', 'email', 'phoneNumber']

    if not set(request.data.keys()).issubset(allowed_keys):
        unexpected = set(request.data.keys()) - set(allowed_keys)
        return Response({"error": {"code":"forbidden_keys", "message":f"unexpected keys {unexpected}"}}, status=status.HTTP_400_BAD_REQUEST)
    
    if "profilePicture" in request.data:
        profile_picture_url = userObj.get_profilePicture_url()
    else:
        profile_picture_url = ''

    # API to check if email ID provided is valid
    if "email" in request.data:
        try:
            email_check_response = requests.get(f"https://emailreputation.abstractapi.com/v1/?api_key={EMAIL_CHECKER_API_KEY}&email={request.data.get('email')}", timeout=5)
            
            email_check_response = email_check_response.json()

            if not email_check_response["email_deliverability"]["is_smtp_valid"]:
                return  Response({"error":{"code": "invalid_email", "message":"incorrect email id provided"}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except (requests.RequestException, ValueError):
            return  Response({"error":{"code":"mail_reputation_server_not_reachable", "message":"email validation service unavailable"}}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    userObjectSerial   = userSerializer(userObj, data = request.data, partial=True)
    if userObjectSerial.is_valid():
        userObjectSerial.save()
        if not (profile_picture_url is None or profile_picture_url == ''):
            object_key = profile_picture_url.split("GamesHubMedia/")[-1]
            delete_from_supabase(object_key)

        return Response({"message": "user updated successfully!"}, status=status.HTTP_202_ACCEPTED)
    
    return Response({"error":{"code": "validation_error", "message": "invalid input data", "details": userObjectSerial.errors}}, status=status.HTTP_400_BAD_REQUEST)


@recover_user_schema
@api_view(["POST"])
def recover_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or username == '':
        return Response({"error": {"code":"not_null_constraint", "message":"username cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)


    if "OTP" in request.data:
        otp      = request.data.get("OTP")
        try:
            userObj  = User.objects.get(username__iexact = username)

            try:
                otpObj   = OTP.objects.get(account = username)
            except OTP.DoesNotExist:
                return Response({"error":{"code":"otp_not_found", "message":"OTP not generated for this user"}}, status=status.HTTP_404_NOT_FOUND)
    
            gen_otp, time_gen = otpObj.get_details()

            if secrets.compare_digest(str(otp), str(gen_otp)) and (time_gen + 300 >= int(time.time())):
                if password is None or password == '':
                    return Response({"error": {"code":"not_null_constraint", "message":"password cannot be none"}}, status=status.HTTP_400_BAD_REQUEST)

                if check_password(password, userObj.get_password()):
                    userObj.change_status()
                    userObj.save()
                    otpObj.delete()
                    email_id = userObj.get_email()

                    Subject    = 'GamesHub Account Recovery Confirmation'
                    message    = account_recovery_success_email({"username":userObj.get_username()})
                    recepients = [email_id]

                    mail_result, _ = mail_service(Subject, message, recepients)

                    if not mail_result:
                        return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    return Response({"message": f"account recovery successful"}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({"error":{"code":"invalid_credentials", "message":"incorrect password provided"}}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":{"code":"otp_invalid_or_expired","message":"OTP either expired or incorrect"}}, status=status.HTTP_400_BAD_REQUEST)


        except User.DoesNotExist:
            return Response({"error":{"code":"username_not_found", "message":"requested username not found"}}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        try:
            userObj  = User.objects.get(username__iexact = username)
            email_id = userObj.get_email()

            otp_num  = secrets.randbelow(900000) + 100000

            otpObj, _ = OTP.objects.get_or_create(account=username)
            otpObj.set_details(otp_num, time.time())
            otpObj.save()

            Subject    = 'GamesHub Account Recovery'
            message    = recover_account_email({"username":userObj.get_username(), "otp_num":otp_num})
            recepients = [email_id]

            mail_result, _ = mail_service(Subject, message, recepients)

            if not mail_result:
                return Response({"error":{"code":"mailer_api_failed", "message":"mailer service failed"}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message":f"OTP sent successfully"}, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({"error":{"code":"username_not_found", "message":"requested username not found"}}, status=status.HTTP_404_NOT_FOUND)