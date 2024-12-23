from django.shortcuts import render

from rest_framework.authtoken.serializers import AuthTokenSerializer
from .serializers import *
from utils.custom_veinlet import CustomViewSet
from user.models import UserAccount
from rest_framework import permissions

from django.db.models import Q

from user.serializers import *
from utils.response_wrapper import ResponseWrapper

from django.contrib.auth.hashers import make_password
from utils.actions import send_action

# Create your views here.

class UserViewSet(CustomViewSet):
    queryset = UserAccount.objects.all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'login':
            self.serializer_class = AuthTokenSerializer

        elif self.action == 'register':
            self.serializer_class = RegisterSerializer

        elif self.action == 'update':
            self.serializer_class = UserProfileUpdateSerializer

        else:
            self.serializer_class = UserDetailsSerializer

        return self.serializer_class 
    

    def get_permissions(self):
        permission_classes = []
        if self.action in ["update", "user_details", 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["list", "destroy"]:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


    def register(self, request, *args, **kwargs):
        password = request.data.pop("password")
        email = request.data["email"]
        username = request.data["username"]

        email_exist = UserAccount.objects.filter(email=email).exists()

        if email_exist:
            return ResponseWrapper(
                error_msg="Email is Already Found", status=400
            )

        username_exist = UserAccount.objects.filter(username=username).exists()

        if username_exist:
            return ResponseWrapper(
                error_msg="Username is Already Found", status=400
            )
        
        password = make_password(password=password)
        user = UserAccount.objects.create(
            password=password,
            **request.data
        )

        serializer = UserDetailsSerializer(instance=user)
        return ResponseWrapper(data=serializer.data, status=200)


    def login(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username:
            return ResponseWrapper(error_msg='User Name is Not Given', status=400)

        if not password:
            return ResponseWrapper(error_msg='Password is Not Given', status=400)

        qs = UserAccount.objects.filter(Q(username=username)| Q(email=username)
                                        ).last()

        if not qs:
            return ResponseWrapper(error_msg='User Not Found', status=400)

        elif qs.check_password(password):
            serializer = LoginSerializer(instance=qs)

            return ResponseWrapper(data=serializer.data, status=200)

        return ResponseWrapper(error_msg="Password Doesn't Match", status=400)


    def user_details(self, request, *args, **kwargs):
        qs = UserAccount.objects.filter(Q(phone=self.request.user.phone)
                                 | Q(email=self.request.user.email)).last()

        if not qs:
            return ResponseWrapper(error_msg='User Not Found',
                                   error_code=400)

        serializer = UserDetailsSerializer(instance=qs)
        return ResponseWrapper(data=serializer.data, status=200)
    
    def update(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        if not serializer.is_valid():
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

        user_qs = UserAccount.objects.filter(pk = kwargs["pk"]).last()
        if not user_qs:
            return ResponseWrapper(error_msg='User Not Found',
                                   error_code=400)
        
        password = serializer.validated_data.pop('password')

        request_data = serializer.validated_data
        
        if password:
           password = make_password(password=password)

        qs = serializer.update(instance=user_qs,
                               validated_data=serializer.validated_data)
        
        user_qs.password = password
        user_qs.save()
        
        serializer = UserDetailsSerializer(instance=qs)

        request_method = request.method
        request_url = request.build_absolute_uri()
        
        response_data = serializer.data

        try:
            send_action(qs, request_method, request_url,request_data, response_data)
        except:
            pass

        return ResponseWrapper(data=serializer.data, status=200)