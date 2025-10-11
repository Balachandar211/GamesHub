from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User, OTP
from .serializers import userSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
import random
import time


# Create your views here.

@api_view(["POST"])
def SignUp(request):
    userObject     = userSerializer(data = request.data)

    if User.objects.filter(userName = request.data.get("userName")).exists():
        return Response({"message": "UserName already Exists"}, status=status.HTTP_400_BAD_REQUEST)

    if userObject.is_valid():
        userObject = userObject.save()
        refresh = RefreshToken.for_user(userObject)
        return Response({"message": f"User {request.data.get('userName')} added successfully and your token is {str(refresh.access_token)}"}, status=status.HTTP_201_CREATED)
    
    return Response({"errors":userObject.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def Login(request):
    try:
        userObj = User.objects.get(userName = request.data.get("userName"))
        if check_password(request.data.get("passWord"), userObj.get_passWord()):
            refresh = RefreshToken.for_user(userObj)
            return Response({"message": f"User {userObj.get_userName()} logged in and you token is {str(refresh.access_token)}"}, status=status.HTTP_200_OK)
        else:
            return Response({"message":f"Incorrect password for user {userObj.get_userName()}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message":"userName not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(["POST"])
def Forgot_Password(request):
    if "OTP" in request.data:
        otp      = request.data.get("OTP")
        try:
            userObj  = User.objects.get(userName = request.data.get("userName"))
            otpObj   = OTP.objects.get(account = request.data.get("userName"))
            gen_otp, time_gen = otpObj.get_details()

            if int(otp) == gen_otp and (time_gen + 60 >= int(time.time())):
                userObj.set_password(request.data.get("password"))
                userObj.save()
                otpObj.delete()
                return Response({"message": f"Password change successfull for account {request.data.get("userName")}"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "OTP either expired or incorrect"}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            print(e)
            return Response({"message": "Incorrect userName entered or OTP not generated for this user"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        userObj  = User.objects.get(userName = request.data.get("userName"))
        email_id = userObj.get_email()
        otp_num  = random.randint(1000, 9999)

        if OTP.objects.filter(account = request.data.get("userName")).exists():
            otpObj   = OTP.objects.get(account = request.data.get("userName"))
            otpObj.set_details(otp_num, time.time())
        else:    
            otpObj   = OTP(otp=otp_num, account = request.data.get("userName"))
        otpObj.save()

        send_mail(
        subject='GamesHub Account Recovery',
        message=f'Your otp to reset password {otp_num}',
        from_email='gameshub.test@gmail.com',
        recipient_list=[email_id],
        fail_silently=False,
        )
        return Response({"message":f"otp sent to {email_id}"})


