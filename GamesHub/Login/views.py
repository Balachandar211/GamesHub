from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import OTP
from .serializers import userSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
import random
import time
from django.contrib.auth import get_user_model
from django.http import HttpResponse
User = get_user_model()


# Create your views here.

def api_redirect(request):
    return HttpResponse("<h1> Incorrect endpoint please access /login for further</h1>")

@api_view(["POST"])
def SignUp(request):
    userObject     = userSerializer(data = request.data)

    if User.objects.filter(username = request.data.get("username")).exists():
        return Response({"message": "Username already Exists"}, status=status.HTTP_400_BAD_REQUEST)

    if userObject.is_valid():
        userObject = userObject.save()
        refresh = RefreshToken.for_user(userObject)
        send_mail(
            subject='Welcome to GamesHub!',
            message='',
            html_message= f'Hi <b>{request.data.get('username')}</b> welcome to GamesHub an exclusive videogames marketplace!',
            from_email='GamesHub <gameshub.test@gmail.com>',
            recipient_list=[request.data.get('email')],
            fail_silently=False,
            )
        return Response({"message": f"User {request.data.get('username')} added successfully", "Access_Token":str(refresh.access_token), "Refresh_Token":str(refresh)}, status=status.HTTP_201_CREATED)
    
    return Response({"errors":userObject.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def Login(request):
    try:
        userObj = User.objects.get(username = request.data.get("username"))
        if userObj.check_password(request.data.get("password")):
            refresh = RefreshToken.for_user(userObj)
            return Response({"message": f"User {userObj.get_username()} logged in", "Access_Token":str(refresh.access_token), "Refresh_Token":str(refresh)}, status=status.HTTP_200_OK)
        else:
            return Response({"message":f"Incorrect password for user {userObj.get_username()}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message":"userName not found"}, status=status.HTTP_404_NOT_FOUND)
    

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
                return Response({"message": f"Password change successfull for account {request.data.get("username")}"}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"message": "OTP either expired or incorrect"}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            print(e)
            return Response({"message": "Incorrect userName entered or OTP not generated for this user"}, status=status.HTTP_400_BAD_REQUEST)

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

            send_mail(
            subject='GamesHub Account Recovery',
            message='',
            html_message= f'Your otp to reset password <b>{otp_num}</b>',
            from_email='GamesHub <gameshub.test@gmail.com>',
            recipient_list=[email_id],
            fail_silently=False,
            )
            return Response({"message":f"otp sent to {email_id} for password reset for user account {request.data.get("username")}"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"message":f"Incorrect Username {request.data.get("username")}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def extendSession(request):
    refresh   = request.data.get("Refresh_Token")
    if not refresh:
        return Response({"message":"Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        refresh_token = RefreshToken(refresh)
        return Response({"message":"Access Token generated successfully", "Access_Token":str(refresh_token.access_token)}, status=status.HTTP_200_OK)
    except:
        return Response({"message":"Refresh token incorrect or expired"}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh   = request.data.get("Refresh_Token")
    if refresh is None:
        return Response({"message":"Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_name     = request.user.get_username()
        refresh_token = RefreshToken(refresh)
        refresh_token.blacklist()
        return Response({"message":f"user {user_name} logged out successfully!"}, status=status.HTTP_205_RESET_CONTENT)
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

        send_mail(
        subject='GamesHub Account Deletion',
        message='',
        html_message= f'Your otp to delete account is <b>{otp_num}</b>',
        from_email='GamesHub <gameshub.test@gmail.com>',
        recipient_list=[email_id],
        fail_silently=False,
        )

        return Response({"message": f"OTP created successfully for account deletion for user {username}"}, status=status.HTTP_201_CREATED)

    else:
        otp      = request.data.get("OTP")
        try:
            otpObj   = OTP.objects.get(account = username)
            gen_otp, time_gen = otpObj.get_details()
            
            if int(otp) == gen_otp and (time_gen + 300 >= int(time.time())):
                userObj.delete()
                otpObj.delete()
                send_mail(
                subject='GamesHub Account Deletion Confirmation',
                message='',
                html_message= f'Your user account <b>{username}</b> deleted successfully',
                from_email='GamesHub <gameshub.test@gmail.com>',
                recipient_list=[email_id],
                fail_silently=False,
                )
                return Response({"message": f"user account {username} deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
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
