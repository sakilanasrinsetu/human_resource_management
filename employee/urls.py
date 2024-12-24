from django.urls import path

from .views import *

urlpatterns =[
     path('company/',
         CompanyViewSet.as_view({'get': 'list', 'post': 'create'}, name='company')),
     path('company/<slug>/',
         CompanyViewSet.as_view({'delete': 'destroy',
                              "patch":"update", "get":"retrieve"},
                              name='company')),
     path('office_location/',
         OfficeLocationViewSet.as_view({'get': 'list', 'post': 'create'}, name='office_location')),
     path('office_location/<slug>/',
         OfficeLocationViewSet.as_view({'delete': 'destroy',
                              "patch":"update", "get":"retrieve"},
                              name='office_location')),
     path('employee_division/',
         EmployeeDivisionViewSet.as_view({'get': 'list', 'post': 'create'}, name='employee_division')),
     path('employee_division/<slug>/',
         EmployeeDivisionViewSet.as_view({'delete': 'destroy',
                              "patch":"update", "get":"retrieve"},
                              name='employee_division')),
     path('employee_department/',
         EmployeeDepartmentViewSet.as_view({'get': 'list', 'post': 'create'}, name='employee_department')),
     path('employee_department/<slug>/',
         EmployeeDepartmentViewSet.as_view({'delete': 'destroy',
                              "patch":"update", "get":"retrieve"},
                              name='employee_department')),
    
     # Employee Designation

     path('employee_designation/',
               EmployeeDesignationViewSet.as_view({'post': 'create', 'get': 'list'},  name='employee_designation')),
     path('employee_designation/<slug>/',
               EmployeeDesignationViewSet.as_view({'patch': 'update', 'get': 'retrieve'},  name='employee_designation')),

     # Employee Grade

     path('employee_grade/',
               EmployeeGradeViewSet.as_view({'post': 'create', 'get': 'list'},  name='employee_grade')),     
     path('employee_grade/<slug>/',
               EmployeeGradeViewSet.as_view({'patch': 'update', 'get': 'retrieve'},  name='employee_grade')),

     # Employee Rank

     path('employee_rank/',
               EmployeeRankingViewSet.as_view({'post': 'create', 'get': 'list'},  name='employee_rank')),   
     path('employee_rank/<slug>/',
               EmployeeRankingViewSet.as_view({'patch': 'update', 'get': 'retrieve' },  name='employee_rank')),

     # Employee Type

     path('employee_type/',
               EmployeeTypeViewSet.as_view({'post': 'create', 'get': 'list'},  name='employee_type')),
     path('employee_type/<id>/',
               EmployeeTypeViewSet.as_view({'patch': 'update', 'get': 'retrieve', 'delete':'destroy'},  name='employee_type')),

]