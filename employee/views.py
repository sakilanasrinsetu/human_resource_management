from django.shortcuts import render

from rest_framework.authtoken.serializers import AuthTokenSerializer
from .serializers import *
from utils.custom_veinlet import CustomViewSet
from employee.models import *
from rest_framework import permissions

from django.db.models import Q

from employee.serializers import *
from utils.response_wrapper import ResponseWrapper

# Create your views here.

class CompanyViewSet(CustomViewSet):
    queryset = Company.objects.all()
    lookup_field = 'slug'
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    

class OfficeLocationViewSet(CustomViewSet):
    queryset = OfficeLocation.objects.all()
    lookup_field = 'slug'
    serializer_class = OfficeLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    

class EmployeeDivisionViewSet(CustomViewSet):
    queryset = EmployeeDivision.objects.all()
    lookup_field = 'slug'
    serializer_class = EmployeeDivisionSerializer
    permission_classes = [permissions.IsAuthenticated]

 