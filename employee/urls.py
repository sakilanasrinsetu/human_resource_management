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
]