from django.shortcuts import render

from rest_framework.authtoken.serializers import AuthTokenSerializer

from employee.filters import *
from .serializers import *
from utils.custom_veinlet import CustomViewSet
from employee.models import *
from rest_framework import permissions

from django.db.models import Q

from employee.serializers import *
from utils.response_wrapper import ResponseWrapper
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, filters

# Create your views here.

class CompanyViewSet(CustomViewSet):
    queryset = Company.objects.all().order_by('name')
    lookup_field = 'slug'
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    

class OfficeLocationViewSet(CustomViewSet):
    queryset = OfficeLocation.objects.all().order_by('name')
    lookup_field = 'slug'
    serializer_class = OfficeLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    

class EmployeeDivisionViewSet(CustomViewSet):
    queryset = EmployeeDivision.objects.all().order_by('name')
    lookup_field = 'slug'
    serializer_class = EmployeeDivisionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeDivisionFilter
    

class DepartmentViewSet(CustomViewSet):
    queryset = Department.objects.all().order_by('name')
    lookup_field = 'slug'
    serializer_class = EmployeeDepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

 