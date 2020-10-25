from .serializers import UserSerializer
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response


class UserCreate(generics.CreateAPIView):
    '''
    Регистрация пользователя в сервисе на основе POST-запроса.
    Необходимые данные в теле запроса: username и password.
    '''
    
    serializer_class = UserSerializer


class LoginView(APIView):
    '''
    Авторизация пользователя в сервисе на основе POST-запроса.
    Необходимые данные в теле запроса: username и password.
    '''
    permission_classes = ()

    def post(self, request,):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)