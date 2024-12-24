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
    

class EmployeeDepartmentViewSet(CustomViewSet):
    queryset = Department.objects.all()
    lookup_field = 'pk'
    serializer_class = EmployeeDepartmentSerializer
    permission_classes = [CheckCustomPermission]
    
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeDepartmentFilter

    @log_activity
    def create(self, request, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        name = request.data.get('name')
        qs = Department.objects.filter(name=name).last()
        if qs:
            return ResponseWrapper(error_msg='Department Name Must Be Unique', error_code=400)
        if serializer.is_valid():
            employee_division = serializer.validated_data.pop('employee_division', None)
            department_head = serializer.validated_data.pop('department_head', None)
            
            if department_head:
                employee_qs = EmployeeInformation.objects.filter(
                    slug = department_head
                ).last()
                if not employee_qs:
                    return ResponseWrapper(error_msg='Division Head Information is NOt Found', error_code=404)
                
            if employee_division:
                employee_division_qs = EmployeeDivision.objects.filter(
                    slug = employee_division
                ).last()
                if not employee_division_qs:
                    return ResponseWrapper(error_msg='Division Information is Not Found', error_code=404)
                
            serializer.validated_data['created_by'] = self.request.user
            qs = serializer.save()
            qs.employee_division= employee_division_qs
            qs.department_head= employee_qs.user
            qs.save()
        
            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    @log_activity
    def update(self, request,slug, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        
        qs = Department.objects.filter(slug=slug).last()
        if not qs:
            return ResponseWrapper(error_msg='Department is not Found', error_code=404)

        name = request.data.get('name')
        employee_division_qs = EmployeeDivision.objects.exclude(slug = slug).filter(name=name).last()
        
        if employee_division_qs:
            return ResponseWrapper(error_msg='Employee Division Name Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            employee_division = serializer.validated_data.pop('employee_division', None)
            department_head = serializer.validated_data.pop('department_head', None)
            
            if department_head:
                employee_qs = EmployeeInformation.objects.filter(
                    slug = department_head
                ).last()
                if not employee_qs:
                    return ResponseWrapper(error_msg='Division Head Information is NOt Found', error_code=404)
                
            if employee_division:
                employee_division_qs = EmployeeDivision.objects.filter(
                    slug = employee_division
                ).last()
                if not employee_division_qs:
                    return ResponseWrapper(error_msg='Division Information is Not Found', error_code=404)
                
           
            serializer.validated_data['updated_by'] = self.request.user
            qs = serializer.update(instance=qs, validated_data=serializer.validated_data)
            
            if employee_division:
                qs.employee_division= employee_division_qs
                
            if department_head:
                qs.department_head= employee_qs.user
                
            qs.save()
            serializer = EmployeeDepartmentSerializer(qs)

            return ResponseWrapper(data=serializer.data, msg='Updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
   
 
class EmployeeDesignationViewSet(CustomViewSet):
    queryset = Designation.objects.all()
    lookup_field = ('id', 'slug')
    serializer_class = EmployeeDesignationSerializer
    permission_classes = [CheckCustomPermission]
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeDesignationFilter

    @log_activity
    def create(self, request, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        name = request.data.get('name')
        qs = Designation.objects.filter(name=name).last()
        if qs:
            return ResponseWrapper(error_msg='Employee Division Name Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            departments = serializer.validated_data.pop('departments', None)
            if departments:
                department_qs = Department.objects.filter(
                    slug = departments
                ).last()
                if not department_qs:
                    return ResponseWrapper(error_msg='Department Information is Not Found', error_code=404)
                
            serializer.validated_data['created_by'] = self.request.user
            qs = serializer.save()
            if department_qs:
                
                try:
                    qs.division_head= department_qs.user
                except:
                    pass
            qs.save()

            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    @log_activity
    def update(self, request,slug, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        
        qs = Designation.objects.filter(slug=slug).last()
        if not qs:
            return ResponseWrapper(error_msg='Employee Designation not Found', error_code=404)

        name = request.data.get('name') or qs.name
        
        employee_division_qs = Designation.objects.exclude(slug = slug).filter(name=name).last()
        
        if employee_division_qs:
            return ResponseWrapper(error_msg='Employee Designation Name Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            departments = serializer.validated_data.pop('departments', None)
            
            if departments:
                departments_qs = Department.objects.filter(
                    slug = departments
                ).last()
                if not departments_qs:
                    return ResponseWrapper(error_msg='Employee Department is Not Found', error_code=404)

            serializer.validated_data['updated_by'] = self.request.user
            qs = serializer.update(instance=qs, validated_data=serializer.validated_data)
            
            if departments:
                qs.division_head= departments_qs
                qs.save()
                
            serializer = EmployeeDesignationSerializer(qs)

            return ResponseWrapper(data=serializer.data, msg='Updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

class EmployeeRankingViewSet(CustomViewSet):
    queryset = Ranking.objects.all()
    lookup_field = 'pk'
    serializer_class = EmployeeRankingSerializer
    permission_classes = [CheckCustomPermission]
    
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeRankingFilter

    @log_activity
    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        name = request.data.get('name')
        employee_ranking_qs = Ranking.objects.filter(name =  name).last()
        if employee_ranking_qs:
            return ResponseWrapper(error_msg='Employee Ranking Name Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            grade = serializer.validated_data.pop('grade', None)
            
            if grade:
                grade_qs = Grading.objects.filter(
                    slug = grade
                ).last()
                if not grade_qs:
                    return ResponseWrapper(error_msg='Employee Grading is Not Found', error_code=404)
                
            try:
                qs = serializer.save( 
                    created_by=self.request.user
                )
            except:
                qs = serializer.save()
                
            if grade:
                qs.grade = grade_qs
                qs.save()

            # Save Logger for Tracking 

            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
    
    @log_activity
    def update(self, request,slug, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True) 
        
        qs = Ranking.objects.filter(slug=slug).last()
        if not qs:
            return ResponseWrapper(error_msg='Employee Ranking not Found', error_code=404)

        name = request.data.get('name') or qs.name
        
        employee_ranking_qs = Ranking.objects.exclude(slug = slug).filter(name=name).last()
        
        if employee_ranking_qs:
            return ResponseWrapper(error_msg='Employee Ranking Name Must Be Unique', error_code=400) 
        
        if serializer.is_valid():
            grade = serializer.validated_data.pop('grade', None)
            
            if grade:
                grade_qs = Grading.objects.filter(
                    slug = grade
                ).last()
                if not grade_qs:
                    return ResponseWrapper(error_msg='Employee Grading is Not Found', error_code=404)
                
            
            serializer.validated_data['updated_by'] = self.request.user
            qs = serializer.update(instance=qs, validated_data=serializer.validated_data)
            
            if grade:
                qs.grade = grade_qs
                qs.save()
            
            serializer = EmployeeRankingSerializer(qs)

            return ResponseWrapper(data=serializer.data, msg='Updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)


class EmployeeGradeViewSet(CustomViewSet):
    queryset = Grading.objects.all()
    lookup_field = 'pk'
    serializer_class = EmployeeGradeSerializer
    permission_classes = [CheckCustomPermission]
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeGradingFilter
    
    @log_activity
    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        name = request.data.get('name')
        employee_grade_qs = Grading.objects.filter(name =  name).last()
        if employee_grade_qs:
            return ResponseWrapper(error_msg='Employee Grade Name Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            try:
                qs = serializer.save( 
                    created_by=self.request.user
                )
            except:
                qs = serializer.save()

            # Save Logger for Tracking 

            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    @log_activity
    def update(self, request,slug, *args, **kwargs): 
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True) 
        
        qs = Grading.objects.filter(slug=slug).last()
        if not qs:
            return ResponseWrapper(error_msg='Employee Grading not Found', error_code=404)

        name = request.data.get('name') or qs.name
        
        employee_grading_qs = Grading.objects.exclude(slug = slug).filter(name=name).last()
        
        if employee_grading_qs:
            return ResponseWrapper(error_msg='Employee Grading Name Must Be Unique', error_code=400) 
        
        if serializer.is_valid():
            
            serializer.validated_data['updated_by'] = self.request.user
            qs = serializer.update(instance=qs, validated_data=serializer.validated_data)
            
            serializer = EmployeeGradeSerializer(qs)

            return ResponseWrapper(data=serializer.data, msg='Updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

class EmployeeTypeViewSet(CustomViewSet):
    queryset = EmployeeType.objects.all()
    lookup_field = 'pk'
    serializer_class = EmployeeTypeSerializer
    permission_classes = [CheckCustomPermission]
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeTypeFilter
        
 
class ExamTypeViewSet(CustomViewSet):
    queryset = ExamType.objects.all()
    lookup_field = 'pk'
    serializer_class = ExamTypeSerializer
    permission_classes = [CheckCustomPermission]
    # filter_backends = (
    #     DjangoFilterBackend,
    #     filters.OrderingFilter,
    # )
    # filterset_class = ExamTypeFilter
    
class EmployeeInformationViewSet(CustomViewSet):
    # queryset = EmployeeInformation.objects.exclude()
    queryset = EmployeeInformation.objects.exclude()
    lookup_field = 'slug'
    serializer_class = EmployeeInformationListSerializer
    permission_classes = [CheckCustomPermission]
    
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = EmployeeInformationFilter
    
    def get_serializer_class(self):
        if self.action in ['create', "update"]:
            self.serializer_class = EmployeeInformationCreateUpdateSerializer
        elif self.action in ['list']:
            self.serializer_class = EmployeeInformationListSerializer
        else:
            self.serializer_class = EmployeeInformationDetailsSerializer

        return self.serializer_class

    
    @log_activity
    def employee_overview_list(self, request, *args, **kwargs):
        context = [
            {
                'msg': "Active Employee",
                'quantity': random.randint(333, 7342),
                'ratio': f"{random.randint(21, 99)}%",
            },
            {
                'msg': "Full Time Employee",
                'quantity': random.randint(333, 7342),
                'ratio': f"{random.randint(21, 99)}%",
            },
            {
                'msg': "Part Time Employee",
                'quantity': random.randint(333, 7342),
                'ratio': f"{random.randint(21, 99)}%",
            },
            {
                'msg': "Upcoming Joining Employee",
                'quantity': random.randint(333, 7342),
                'ratio': f"{random.randint(21, 99)}%",
            }
        ]
        return ResponseWrapper(data= context, msg="Success", status=200)
    
    @log_activity
    def office_wise_employee_list(self, request, *args, **kwargs):
        qs = OfficeLocation.objects.filter(office_type__in = ['HEAD_OFFICE', 'WAREHOUSE'])
        # qs = self.filter_queryset(qs)
        
        page_qs = self.paginate_queryset(qs)
        serializer = OfficeWiseEmployeeInformationListSerializer(instance=page_qs, many=True)

        paginated_data = self.get_paginated_response(serializer.data)
        
        return ResponseWrapper(data=paginated_data.data, msg="Success", status=200)
    
    
    @log_activity
    def employee_information_summary(self, request, *args, **kwargs):
        total_employee = 0.0
        total_full_time_employee = 0.0
        total_part_time_employee = 0.0
        total_probation_employee = 0.0
        
        total_employee_rating = 0.0
        total_full_time_employee_rating = 0.0
        total_part_time_employee_rating = 0.0
        total_probation_employee_rating = 0.0
        
        employee_qs = self.queryset
        full_time_employee_qs = self.queryset.filter(employee_type__name = "Full Time")
        part_time_employee_qs = self.queryset.filter(employee_type__name = "Part Time")
        probation_employee_qs = self.queryset.filter(employee_type__name = "Probation")
        
        total_employee = employee_qs.count()
        total_full_time_employee = full_time_employee_qs.count()
        total_part_time_employee = part_time_employee_qs.count()
        total_probation_employee = probation_employee_qs.count()
        
        total_employee_rating = (total_employee*100/total_employee)
        total_full_time_employee_rating = (total_full_time_employee*100/total_employee)
        total_part_time_employee_rating = (total_part_time_employee*100/total_employee)
        total_probation_employee_rating = (total_probation_employee*100/total_employee)
        
        all_employee = {
            'message': "Total Employee",
            'total_employee': total_employee,
            'rating': round(total_employee_rating, 2)
        }
        full_time_employee = {
            'message': "Total Full Time Employee",
            'total_employee': total_full_time_employee,
            'rating': round(total_full_time_employee_rating, 2)
        }
        part_time_employee = {
            'message': "Total Part Time Employee",
            'total_employee': total_part_time_employee,
            'rating': round(total_part_time_employee_rating, 2)
        }
        
        probation_employee = {
            'message': "Total Probation Employee",
            'total_employee': total_probation_employee,
            'rating': round(total_probation_employee_rating, 2)
        }
        
        context = {
            'all_employee':all_employee,
            'full_time_employee':full_time_employee,
            'part_time_employee':part_time_employee,
            'probation_employee':probation_employee,
        }
        
        return ResponseWrapper(data = context, msg="success", status=200)
    
    @log_activity
    def create(self, request, user_id, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial = True)
        
        user_qs = UserAccount.objects.filter(id = user_id).last()
        
        if not user_qs:
            return ResponseWrapper(error_msg='User Information is Not Found', error_code=404)
        
        
        name = f"{user_qs.first_name} {user_qs.last_name}"
        phone_number = user_qs.phone
        designations_qs = None
        pos_area_qs = None
        company_qs = None
        employee_type_qs = None
        reporting_person_qs= None
        work_station_qs = None
        rank_qs = None

        employee_user_qs = EmployeeInformation.objects.filter(user__id = user_id).last()
        if employee_user_qs:
            return ResponseWrapper(error_msg=f'For {name} Employee Information is Already Found', error_code=404)
        
        employee_id = request.data.get('employee_id')
        
        employee_information_qs = EmployeeInformation.objects.filter(employee_id =  employee_id).last()
        
        if employee_information_qs:
            return ResponseWrapper(error_msg='Employee ID Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            employee_type = serializer.validated_data.pop('employee_type', None)
            designations = serializer.validated_data.pop('designations', None)
            work_station = serializer.validated_data.pop('work_station', None)
            reporting_person = serializer.validated_data.pop('reporting_person', None)
            pos_reason = serializer.validated_data.pop('pos_reason', None)
            pos_area = serializer.validated_data.pop('pos_area', None)
            rank = serializer.validated_data.pop('rank', None)
            
            if employee_type:
                employee_type_qs = EmployeeType.objects.filter(slug = employee_type).last()
                if not employee_type_qs:
                    return ResponseWrapper( error_msg='Employee Type is Not Found', status=404)
                
            if designations:
                designations_qs = Designation.objects.filter(slug = designations).last()
                if not designations_qs:
                    return ResponseWrapper( error_msg='Designations is Not Found', status=404)
                
            if work_station:
                work_station_qs = OfficeLocation.objects.filter(slug = work_station).last()
                if not work_station_qs:
                    return ResponseWrapper( error_msg='Office Location is Not Found', status=404)


            if reporting_person:
                reporting_person_qs = EmployeeInformation.objects.filter(slug = reporting_person).last()
                if not reporting_person_qs:
                    return ResponseWrapper( error_msg='Reporting Person is Not Found', status=404)

            if pos_reason:
                pos_reason_qs = EmployeeInformation.objects.filter(slug = pos_reason).last()
                if not pos_reason_qs:
                    return ResponseWrapper( error_msg='POS Resion is Not Found', status=404)
                
            if rank:
                rank_qs = Ranking.objects.filter(slug = rank).last()
                if not rank_qs:
                    return ResponseWrapper( error_msg='Ranking is Not Found', status=404)
            
            slug = unique_slug_generator(name = name)
            
            company_qs = EmployeeInformation.objects.filter(user = request.user).last().employee_company
            
            qs = serializer.save(
                created_by=self.request.user,
                name = name,
                slug = slug,
                employee_company = company_qs,
                phone_number = phone_number,
                employee_type = employee_type_qs,
                designations = designations_qs,
                work_station = work_station_qs,
                reporting_person = reporting_person_qs,
                pos_area = pos_area_qs,
                rank = rank_qs,
                user = user_qs
            )
            serializer = EmployeeInformationDetailsSerializer(qs)
            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
    
    @log_activity
    def update(self, request, slug, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        
        employee_qs = EmployeeInformation.objects.filter(slug = slug).last()
        
        if not employee_qs:
            return ResponseWrapper(error_msg=f'Employee Information is Not Found', error_code=404)
        
        if request.data.get('employee_id'):
            employee_id = request.data.pop('employee_id')
        # else:
        #     employee_id = employee_qs.employee_id if employee_qs else None
        
        
        employee_type_qs = None
        designations_qs = None
        work_station_qs = None
        reporting_person_qs = None
        pos_reason_qs = None
        pos_area_qs = None
        rank_qs = None

        
        employee_information_qs = EmployeeInformation.objects.exclude(slug = slug).filter(employee_id =  employee_id).last()
        
        if employee_information_qs:
            return ResponseWrapper(error_msg='Employee ID Must Be Unique', error_code=400)
        
        if serializer.is_valid():
            # employee_id = serializer.validated_data.pop('employee_id')
            name = serializer.validated_data.pop('name', employee_qs.name)
            employee_type_slug = serializer.validated_data.pop('employee_type', employee_qs.employee_type.slug if employee_qs.employee_type else request.data.get('employee_type'))
            designations_slug = serializer.validated_data.pop('designation', employee_qs.designations.slug if employee_qs.designations else request.data.get('designation'))
            work_station_slug = serializer.validated_data.pop('work_station', employee_qs.work_station.slug if employee_qs.work_station else request.data.get('work_station'))
            rank_slug = serializer.validated_data.pop('rank', employee_qs.rank.slug if employee_qs.rank else request.data.get('rank'))
            reporting_person_slug = serializer.validated_data.pop('rank', employee_qs.reporting_person.slug if employee_qs.reporting_person else request.data.get('reporting_person'))
            pos_reason_slug = serializer.validated_data.pop('rank', employee_qs.pos_reason.slug if employee_qs.pos_reason else request.data.get('pos_reason'))
            pos_area_slug = serializer.validated_data.pop('rank', employee_qs.pos_area.slug if employee_qs.pos_area else request.data.get('pos_area'))

            if employee_type_slug:
                employee_type_qs = EmployeeType.objects.filter(slug = employee_type_slug).last()
                if not employee_type_qs:
                    return ResponseWrapper( error_msg='Employee Type is Not Found', status=404)
            
            if designations_slug:
                designations_qs = Designation.objects.filter(slug = designations_slug).last()
                
                if not designations_qs:
                    return ResponseWrapper( error_msg='Designations is Not Found', status=404)
                
            if work_station_slug:
                work_station_qs = OfficeLocation.objects.filter(slug = work_station_slug).last()
                if not work_station_qs:
                    return ResponseWrapper( error_msg='Office Location is Not Found', status=404)
                
            if rank_slug:
                rank_qs = Ranking.objects.filter(slug = rank_slug).last()
                if not rank_qs:
                    return ResponseWrapper( error_msg='Ranking is Not Found', status=404)

            if pos_area_slug:
                pos_area_qs = POSArea.objects.filter(slug = pos_area_slug).last()
                if not pos_area_qs:
                    return ResponseWrapper( error_msg='POS Area is Not Found', status=404)

            if reporting_person_slug:
                reporting_person_qs = EmployeeInformation.objects.filter(slug = reporting_person_slug).last()
                if not reporting_person_qs:
                    return ResponseWrapper( error_msg='Reporting Person is Not Found', status=404)

            if pos_reason_slug:
                pos_reason_qs = POSRegion.objects.filter(slug = pos_reason_slug).last()
                if not pos_reason_qs:
                    return ResponseWrapper( error_msg='POS Resion is Not Found', status=404)

            company_qs = EmployeeInformation.objects.filter(user = request.user).last().employee_company
            
            qs = serializer.update(instance=employee_qs, 
                validated_data=serializer.validated_data
            )
            employee_qs.name = name
            # qs.employee_company = company_qs,
            employee_qs.phone_number = employee_qs.phone_number
            employee_qs.employee_type = employee_type_qs
            employee_qs.designations = designations_qs
            employee_qs.work_station = work_station_qs
            employee_qs.pos_area = pos_area_qs
            employee_qs.reporting_person = reporting_person_qs
            employee_qs.pos_reason = pos_reason_qs
            employee_qs.rank = rank_qs
            employee_qs.updated_by_id = self.request.user.id
            employee_qs.save()
            
            serializer = EmployeeInformationDetailsSerializer(employee_qs)
            return ResponseWrapper(data=serializer.data, msg='Updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)


class GuardianInformationViewSet(CustomViewSet):
    queryset = EmployeeGuardianInformation.objects.all()
    lookup_field = 'id'

    serializer_class = EmployeeGuardianInformationCreateSerializer
    permission_classes = [CheckCustomPermission]

    @log_activity
    def retrieve(self, request, slug, *args, **kwargs):
        employee_qs = EmployeeInformation.objects.filter(slug = slug).last()
        if not employee_qs:
            return ResponseWrapper(error_msg='Employee Information is Not Found', error_code=404)
        
        serializer = EmployeeGuardianInformationSerializer(employee_qs.guardian_information, many = True)

        return ResponseWrapper(data=serializer.data, msg='created', status=200)
    
    @log_activity
    def update(self, request, employee_slug, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)

        if not serializer.is_valid():
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
        
        employee_qs = EmployeeInformation.objects.filter(slug = employee_slug).last()
        if not employee_qs:
            return ResponseWrapper(error_msg='Employee Information is Not Found', error_code=404)
        
        data = request.data

        if not isinstance(data, list):
            data = [data]  
        results = []
        try:
            with transaction.atomic():
                for item_data in data:
                    serializer = serializer_class(data=item_data)

                    if serializer.is_valid():
                        name = item_data.get('name')
                        relationship_type = item_data.get('relationship_type')
                        guardian_information_qs = self.queryset.filter(relationship_type = relationship_type, employee_informations = employee_qs).last()
                        
                        if not guardian_information_qs:
                            slug = unique_slug_generator(name)
                            
                            qs = serializer.save(
                                created_by=self.request.user,
                                slug = slug
                                )
                        else:
                            qs = serializer.update(instance = guardian_information_qs,
                                    validated_data=serializer.validated_data
                                )
                            
                        employee_qs.guardian_information.add(qs)
                        
                    else:
                        results.append({
                            "error_msg": serializer.errors,
                            "error_code": 400
                        })

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400)
        
        serializer = EmployeeInformationDetailsSerializer(employee_qs)

        return ResponseWrapper(data=serializer.data, msg='created', status=200)


class EmployeeAddressInformationViewSet(CustomViewSet):
    queryset = EmployeeAddressInformation.objects.all()
    serializer_class = EmployeeAddressInformationCreateSerializer
    permission_classes = [CheckCustomPermission]
    lookup_field = 'pk'

    @log_activity
    def update(self, request, employee_slug, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)
        
        if not serializer.is_valid():
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
        
        employee_qs = EmployeeInformation.objects.filter(slug = employee_slug).last()
        if not employee_qs:
            return ResponseWrapper(error_msg='Employee Information is Not Found', error_code=404)
        
        data = request.data
        
        district_name = '-'
        division_name = '-'
        country_name = '-'
        
        try:
            with transaction.atomic():
                for item_data in data:
                    serializer = serializer_class(data=item_data)
                    if serializer.is_valid():
                        area_name = item_data.pop('area_name', None)
                        
                        address_type = item_data.get('address_type')
                        
                        address_qs = self.queryset.filter(address_type = address_type, employee_informations = employee_qs)
                        
                        area_qs = Area.objects.filter(slug= area_name).last()
                        
                        if not area_qs:
                            return ResponseWrapper(error_msg='Area is Not Found', error_code=404)
                        
                        if area_qs.district:
                            district_name = area_qs.district.name
                            
                            if area_qs.district.division:
                                division_name = area_qs.district.division.name
                                
                            if area_qs.district.division.country:
                                country_name = area_qs.district.division.country.name
                            
                        if not address_qs:
                            qs = serializer.save(
                                created_by=self.request.user,
                                area_name = area_qs,
                                district_name = district_name,
                                division_name =division_name,
                                country_name = country_name
                                )
                        else:
                            full_address = item_data.get('full_address') or address_qs.last().full_address
                            city = item_data.get('city') or address_qs.last().city
                            remarks = item_data.get('remarks') or address_qs.last().remarks
                            is_active = item_data.get('is_active') or address_qs.last().is_active
                            
                            qs = address_qs.update(
                                full_address = full_address,
                                city = city,
                                address_type = address_type,
                                area_name = area_qs,
                                district_name = district_name,
                                division_name = division_name,
                                country_name = country_name,
                                remarks = remarks,
                                is_active = is_active,
                                )
                        
                        employee_qs.employee_address_information.add(qs)
                        

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400)

        serializer = EmployeeInformationDetailsSerializer(employee_qs)

        return ResponseWrapper(data=serializer.data, msg='created', status=200)
    
    
class EmployeeEducationInformationViewSet(CustomViewSet):
    queryset = EmployeeEducationInformation.objects.all()
    lookup_field = 'id'

    serializer_class = EmployeeEducationInformationSerializer
    permission_classes = [CheckCustomPermission]
    
    @log_activity
    def update(self, request, employee_slug, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)

        if not serializer.is_valid():
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
        
        employee_qs = EmployeeInformation.objects.filter(slug = employee_slug).last()
        if not employee_qs:
            return ResponseWrapper(error_msg='Employee Information is Not Found', error_code=404)
        
        data = request.data

        if not isinstance(data, list):
            data = [data]  
        results = []
        try:
            with transaction.atomic():
                for item_data in data:
                    serializer = serializer_class(data=item_data)

                    if serializer.is_valid():
                        exam_type = serializer.validated_data.pop('exam_type')
                        
                        if serializer.validated_data.get('file'):
                            file = serializer.validated_data.pop('file')
                        else:
                            file = None
                            
                        institution_name = item_data.get('institution_name')
                        
                        exam_type_qs= ExamType.objects.filter(slug = exam_type).last()
                        
                        if not exam_type_qs:
                            return ResponseWrapper(
                                error_msg='Exam Type is Not Found', error_code=404
                            )
                        
                        employee_education_information_qs = self.queryset.filter(exam_type__slug = exam_type, employee_informations = employee_qs).last() 
                        
                        if not employee_education_information_qs:
                            slug = unique_slug_generator(name=institution_name)
                            
                            qs = serializer.save(
                                created_by=self.request.user,
                                slug = slug,
                                exam_type = exam_type_qs
                                )
                        else:
                            qs = serializer.update(
                                instance = employee_education_information_qs,
                                validated_data=serializer.validated_data
                                )
                            
                            qs.exam_type = exam_type_qs
                            qs.save()
                            
                            
                        employee_qs.employee_education_information.add(qs)
                        
                    else:
                        results.append({
                            "error_msg": serializer.errors,
                            "error_code": 400
                        })

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400)
        
        serializer = EmployeeInformationDetailsSerializer(employee_qs)

        return ResponseWrapper(data=serializer.data, msg='created', status=200)
    

class JobExperienceInformationViewSet(CustomViewSet):
    queryset = JobExperienceInformation.objects.all()
    lookup_field = 'slug'

    serializer_class = JobExperienceInformationSerializer
    permission_classes = [CheckCustomPermission]
    
    @log_activity
    def update(self, request, employee_slug, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)

        if not serializer.is_valid():
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
        
        employee_qs = EmployeeInformation.objects.filter(slug = employee_slug).last()
        if not employee_qs:
            return ResponseWrapper(error_msg='Employee Information is Not Found', error_code=404)
        
        data = request.data

        if not isinstance(data, list):
            data = [data]  
        results = []
        try:
            with transaction.atomic():
                for item_data in data:
                    serializer = serializer_class(data=item_data)

                    if serializer.is_valid():
                        company_name = serializer.validated_data.get('company_name')
                        
                        
                        employee_job_experience_information_qs = self.queryset.filter(company_name = company_name, employee_informations = employee_qs).last() 
                        
                        if not employee_job_experience_information_qs:
                            slug = unique_slug_generator(name=company_name)
                            
                            qs = serializer.save(
                                created_by=self.request.user,
                                slug = slug,
                                )
                        else:
                            qs = serializer.update(
                                instance = employee_job_experience_information_qs,
                                validated_data=serializer.validated_data
                                )
                            
                        employee_qs.job_experience_information.add(qs)
                        
                    else:
                        results.append({
                            "error_msg": serializer.errors,
                            "error_code": 400
                        })

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400)
        
        serializer = EmployeeInformationDetailsSerializer(employee_qs)

        return ResponseWrapper(data=serializer.data, msg='created', status=200)
    

class BankInformationViewSet(CustomViewSet):
    queryset = BankInformation.objects.all()
    lookup_field = 'slug'

    serializer_class = BankInformationSerializer
    permission_classes = [CheckCustomPermission]
    
    @log_activity
    def update(self, request, employee_slug, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)

        if not serializer.is_valid():
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
        
        employee_qs = EmployeeInformation.objects.filter(slug = employee_slug).last()
        if not employee_qs:
            return ResponseWrapper(error_msg='Employee Information is Not Found', error_code=404)
        
        data = request.data

        if not isinstance(data, list):
            data = [data]  
        results = []
        try:
            with transaction.atomic():
                for item_data in data:
                    serializer = serializer_class(data=item_data)

                    if serializer.is_valid():
                        account_name = serializer.validated_data.get('account_name')
                        account_number = serializer.validated_data.get('account_number')
                        
                        
                        employee_bank_information_qs = self.queryset.filter(account_number = account_number, employee_informations = employee_qs).last() 
                        
                        if not employee_bank_information_qs:
                            slug = unique_slug_generator(name=account_name)
                            
                            qs = serializer.save(
                                created_by=self.request.user,
                                slug = slug,
                                )
                        else:
                            qs = serializer.update(
                                instance = employee_bank_information_qs,
                                validated_data=serializer.validated_data
                                )
                            
                        employee_qs.bank_information.add(qs)
                        
                    else:
                        results.append({
                            "error_msg": serializer.errors,
                            "error_code": 400
                        })

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400)
        
        serializer = EmployeeInformationDetailsSerializer(employee_qs)

        return ResponseWrapper(data=serializer.data, msg='created', status=200)
