
from datetime import timedelta, datetime
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .serializers import SignUpSerializer, Userserializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from django.utils.timezone import datetime
from django.core.mail import send_mail
from utils.helper import get_current_host

# Create your views here.


@api_view(['POST'])
def register(request):
    data = request.data
    user = SignUpSerializer(data=data)
    if user.is_valid():
        if not User.objects.filter(username=data['email']).exists():
            user = User.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                username=data['email'],
                password=make_password(data['password']),
            )

            return Response({'details': 'User sucessful registered'}, status=status.HTTP_201_CREATED)

        else:
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def curent_user(request):
    user = Userserializer(request.user, many=False)

    return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.email = data['email']
    user.username = data['email']

    if data['password'] != "":
        user.password = make_password(data['password'])

    user.save()

    serializer = Userserializer(user, many=False)
    return Response(serializer.data)
# funtion to get the reset-link


@api_view(['POST'])
def forgot_password(request):
    data = request.data

    user = get_object_or_404(User, email=data['email'])

    token = get_random_string(40)
    expired_time = datetime.now() + timedelta(minutes=30)

    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expired_time
    user.profile.save()
    host = get_current_host(request)
    link = "{host}api/reset_password/{token}".format(host=host, token=token)
    body = "Developed by Sarinke John Sarijore (+255)0748048065: Your passowrd reset email is {link}".format(
        link=link)

    send_mail(
        "Password Reset For StoreFront:",
        body,
        "noreply@storefront.shop",
        [data['email']]
    )
    return Response({'details': 'Email has been sent to: {email}'.format(email=data['email'])})


@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(User, profile__reset_password_token=token)

    # checking if the token has expired first
    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'error': 'Token is expired!'}, status=status.HTTP_400_BAD_REQUEST)

    # password if they are the same
    if data['password'] != data['confirmpassword']:
        return Response({'error': 'passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None
    user.profile.save()
    user.save()
    return Response({'details': 'Passwords reset successfully'})
