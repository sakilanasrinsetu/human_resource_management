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
     # Exam Type

     path('exam_type/',
               ExamTypeViewSet.as_view({'post': 'create', 'get': 'list'},  name='exam_type')),
     path('exam_type/<slug>/',
               ExamTypeViewSet.as_view({'patch': 'update', 'get': 'retrieve'},  name='exam_type')),

     # Employee Information

     path('employee_information/',
               EmployeeInformationViewSet.as_view({'get': 'list'},  name='employee_information')),
     path('employee_overview_list/',
               EmployeeInformationViewSet.as_view({'get': 'employee_overview_list'},  name='employee_overview_list')),

     path('employee_information_create/<user_id>/',
               EmployeeInformationViewSet.as_view({'post': 'create'},  name='employee_information_create')),
     path('employee_information/<slug>/',
               EmployeeInformationViewSet.as_view({'patch': 'update', 'get': 'retrieve', 'delete':'destroy'},  name='employee_information')),
     path('employee_information_summary/',
               EmployeeInformationViewSet.as_view({'get': 'employee_information_summary'},  name='employee_information_summary')),
     path('office_wise_employee_list/',
               EmployeeInformationViewSet.as_view({'get': 'office_wise_employee_list'},  name='office_wise_employee_list')),

     # Employee Guardian Information


     path('guardian_information_create/<employee_slug>/',
               GuardianInformationViewSet.as_view({'patch': 'update'}, name='guardian_information_create')),
     
     path('employee_guardian_information/<slug>/',
               GuardianInformationViewSet.as_view({'get': 'retrieve'},  name='employee_guardian_information')),

     path('employee_address_information/<employee_slug>/',
               EmployeeAddressInformationViewSet.as_view({'patch': 'update'}, name='employee_address_information')),
     
     # path('employee_address_information/<employee_param>/',
     #         EmployeeAddressInformationViewSet.as_view({'post': 'create', 'get': 'retriveEmployee'}, name='employee_address_information-detail')),

     path('employee_education_information/<employee_slug>/',
               EmployeeEducationInformationViewSet.as_view({'patch': 'update'}, name='employee_education_information')),

     path('employee_job_experience_information/<employee_slug>/',
               JobExperienceInformationViewSet.as_view({'patch': 'update'}, name='employee_job_experience_information')),

     path('employee_bank_information/<employee_slug>/',
               BankInformationViewSet.as_view({'patch': 'update'}, name='employee_bank_information')),

]
  