from django.shortcuts import render

from rest_framework.authtoken.serializers import AuthTokenSerializer

from employee.filters import *
from utils.decorators import log_activity
from utils.permissions import CheckCustomPermission
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
    queryset = EmployeeDivision.objects.all()
    lookup_field = 'pk'
    serializer_class = EmployeeDivisionSerializer
    permission_classes = [CheckCustomPermission]
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeDivisionFilter
    
    @log_activity
    def create(self, request, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        name = request.data.get('name')
        employee_division_qs = EmployeeDivision.objects.filter(name=name).last()
        if employee_division_qs:
            return ResponseWrapper(error_msg='Employee Division Name Must Be Unique', error_code=400)
        if serializer.is_valid():
            division_head = serializer.validated_data.pop('division_head', None)
            if division_head:
                employee_qs = EmployeeInformation.objects.filter(
                    slug = division_head
                ).last()
                if not employee_qs:
                    return ResponseWrapper(error_msg='Division Head Information is NOt Found', error_code=404)
                
            serializer.validated_data['created_by'] = self.request.user
            qs = serializer.save()
            qs.division_head= employee_qs.user
            qs.save()

            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    @log_activity
    def update(self, request, slug, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        
        qs = EmployeeDivision.objects.filter(slug=slug).last()
        if not qs:
            return ResponseWrapper(error_msg='Employee Division not Found', error_code=404)

        name = request.data.get('name')
        employee_division_qs = EmployeeDivision.objects.exclude(slug = slug).filter(name=name).last()
        
        if employee_division_qs:
            return ResponseWrapper(error_msg='Employee Division Name Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            division_head = serializer.validated_data.pop('division_head', None)
            
            if division_head:
                employee_qs = EmployeeInformation.objects.filter(
                    slug = division_head
                ).last()
                if not employee_qs:
                    return ResponseWrapper(error_msg='Employee Information is Not Found', error_code=404)
                
           
            serializer.validated_data['updated_by'] = self.request.user
            qs = serializer.update(instance=qs, validated_data=serializer.validated_data)
            
            if division_head:
                qs.division_head= employee_qs.user
                qs.save()
                
            serializer = EmployeeDivisionSerializer(qs)

            return ResponseWrapper(data=serializer.data, msg='Updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
    

class DepartmentViewSet(CustomViewSet):
    queryset = Department.objects.all().order_by('name')
    lookup_field = 'slug'
    serializer_class = EmployeeDepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

 