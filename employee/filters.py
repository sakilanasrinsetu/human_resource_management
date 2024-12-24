import django_filters
from employee.models import *
from django_filters.rest_framework import FilterSet
from django.db.models import Count, Min, Q
from datetime import date, datetime, timedelta
from django.utils import timezone
from datetime import datetime


class EmployeeDivisionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    division_head = django_filters.CharFilter(label="division_head",
                                         method="filter_model")
    is_active = django_filters.CharFilter(label="is_active",
                                         method="filter_model")

    class Meta:
        model = EmployeeDivision
        fields = (
            'search',
            'division_head',
            'is_active',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        division_head = self.data.get('division_head')
        is_active = self.data.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if division_head:
            queryset = queryset.filter(
                Q(division_head__employee_informations__name__icontains = division_head)
                | Q(division_head__employee_informations__slug__icontains = division_head)
            )
            
        if is_active:
            if is_active.lower() == 'true' :
                queryset = queryset.filter(
                    is_active = True 
                )
            else:
                queryset = queryset.filter(
                    is_active = False 
                )

            
        return queryset

class EmployeeAttendenceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search", method="filter_model")
    start_date = django_filters.CharFilter(label="start_date", method="filter_model")
    end_date = django_filters.CharFilter(label="end_date", method="filter_model")
    employee_id = django_filters.CharFilter(label="employee_id", method="filter_model")
    check_in = django_filters.CharFilter(label="check_in", method="filter_model")
    check_out = django_filters.CharFilter(label="check_out", method="filter_model")
    attendance_type = django_filters.CharFilter(label="attendance_type", method="filter_model")

    class Meta:
        model = EmployeeAttendance
        fields = (
            
        )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        is_active = self.data.get('is_active')
        start_date = self.data.get('start_date')
        end_date = self.data.get('end_date')
        employee_id = self.data.get('employee_id')
        check_in = self.data.get('check_in')
        check_out = self.data.get('check_out')
        attendance_type = self.data.get('attendance_type')




    
class EmployeeDepartmentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    employee_division = django_filters.CharFilter(label="employee_division",
                                         method="filter_model")
    department_head = django_filters.CharFilter(label="department_head",
                                         method="filter_model")
    is_active = django_filters.CharFilter(label="is_active",
                                         method="filter_model")

    class Meta:
        model = Department
        fields = (
            'search',
            'employee_division',
            'department_head',
            'is_active',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        employee_division = self.data.get('employee_division')
        department_head = self.data.get('department_head')
        is_active = self.data.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if employee_division:
            queryset = queryset.filter(
                Q(employee_division__name__icontains = employee_division)
                | Q(employee_division__slug__icontains = employee_division)
            )
            
        if department_head:
            queryset = queryset.filter(
                Q(division_head__employee_informations__user__name__icontains = department_head)
                | Q(division_head__employee_informations__user__slug__icontains = department_head)
            )
            
        if is_active:
            if is_active.lower() == 'true' :
                queryset = queryset.filter(
                    is_active = True 
                )
            else:
                queryset = queryset.filter(
                    is_active = False 
                )

            
        return queryset
   
    
class EmployeeDesignationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    departments = django_filters.CharFilter(label="departments",
                                         method="filter_model")
    is_active = django_filters.CharFilter(label="is_active",
                                         method="filter_model")

    class Meta:
        model = Designation
        fields = (
            'search',
            'departments',
            'is_active',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        departments = self.data.get('departments')
        is_active = self.data.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if departments:
            queryset = queryset.filter(
                Q(departments__name__icontains = departments)
                | Q(departments__slug__icontains = departments)
            )
            
        if is_active:
            if is_active.lower() == 'true' :
                queryset = queryset.filter(
                    is_active = True 
                )
            else:
                queryset = queryset.filter(
                    is_active = False 
                )

            
        return queryset
   

class EmployeeGradingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    is_active = django_filters.CharFilter(label="is_active",
                                         method="filter_model")

    class Meta:
        model = Grading
        fields = (
            'search',
            'is_active',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        is_active = self.data.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if is_active:
            if is_active.lower() == 'true' :
                queryset = queryset.filter(
                    is_active = True 
                )
            else:
                queryset = queryset.filter(
                    is_active = False 
                )

            
        return queryset
   

class EmployeeRankingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    grade = django_filters.CharFilter(label="grade",
                                         method="filter_model")
    is_active = django_filters.CharFilter(label="is_active",
                                         method="filter_model")

    class Meta:
        model = Ranking
        fields = (
            'search',
            'grade',
            'is_active',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        grade = self.data.get('grade')
        is_active = self.data.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if grade:
            queryset = queryset.filter(
                Q(grade__name__icontains = grade)
                | Q(grade__slug__icontains = grade)
            )
            
        if is_active:
            if is_active.lower() == 'true' :
                queryset = queryset.filter(
                    is_active = True 
                )
            else:
                queryset = queryset.filter(
                    is_active = False 
                )

            
        return queryset
   
    
class EmployeeTypeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    is_active = django_filters.CharFilter(label="is_active",
                                         method="filter_model")

    class Meta:
        model = EmployeeType
        fields = (
            'search',
            'is_active',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        is_active = self.data.get('is_active')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if is_active:
            if is_active.lower() == 'true' :
                queryset = queryset.filter(
                    is_active = True 
                )
            else:
                queryset = queryset.filter(
                    is_active = False 
                )

            
        return queryset
   

class EmployeeInformationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    employee_type = django_filters.CharFilter(label="employee_type",
                                         method="filter_model")
    designations = django_filters.CharFilter(label="designations",
                                         method="filter_model")
    is_active = django_filters.CharFilter(label="is_active",
                                         method="filter_model")
    office_location = django_filters.CharFilter(label="office_location",
                                         method="filter_model")

    class Meta:
        model = EmployeeInformation
        fields = (
            'search',
            'employee_type',
            'designations',
            'office_location',
            'is_active',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        employee_type = self.data.get('employee_type')
        designations = self.data.get('designations')
        is_active = self.data.get('is_active')
        office_location = self.data.get('office_location')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
                | Q(user__email__icontains = search)
                | Q(user__phone__icontains = search)
                | Q(employee_id__icontains = search)
                | Q(bank_information__account_name__icontains = search)
                | Q(designations__name__icontains = search)
                | Q(work_station__name__icontains = search)
                | Q(designations__departments__name__icontains = search)
            )
            
        if employee_type:
            queryset = queryset.filter(
                Q(employee_type__name__icontains = employee_type)
                | Q(employee_type__slug__icontains = employee_type)
            )
            
        print(f"Before ={queryset.count()}")
        if office_location:
            queryset = queryset.filter(
                Q(work_station__name__icontains = office_location)
                | Q(work_station__slug__icontains = office_location)
            )
            
        print(f"After ={queryset.count()}, office_location = {office_location}")
            
        if designations:
            queryset = queryset.filter(
                Q(designations__name__icontains = designations)
                | Q(designations__slug__icontains = designations)
            )
            
        if is_active:
            if is_active.lower() == 'true' :
                queryset = queryset.filter(
                    is_active = True 
                )
            else:
                queryset = queryset.filter(
                    is_active = False 
                )

            
        return queryset
   
  
class EmployeeOfficeHourFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    start_time = django_filters.CharFilter(label="start_time",
                                         method="filter_model")
    end_time = django_filters.CharFilter(label="end_time",
                                         method="filter_model")

    class Meta:
        model = EmployeeOfficeHour
        fields = (
            'search',
            'start_time',
            'end_time',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        start_time = self.data.get('start_time')
        end_time = self.data.get('end_time')
        
        if search:
            queryset = queryset.filter(
                Q(employee_information__name__icontains = search)
                | Q(employee_information__slug__icontains = search)
            )
            
        if start_time and end_time:
            queryset = queryset.filter(
                Q(start_time = start_time)
                | Q(end_time = end_time)
            )

            
        return queryset
    
    
class EmployeeAttendanceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    status = django_filters.CharFilter(label="status",
                                         method="filter_model")
    attendance_type = django_filters.CharFilter(label="attendance_type",
                                         method="filter_model")
    start_date = django_filters.CharFilter(label="start_date",
                                         method="filter_model")
    end_date = django_filters.CharFilter(label="end_date",
                                         method="filter_model")

    class Meta:
        model = EmployeeAttendance
        fields = (
            'search',
            'status',
            'attendance_type',
            'start_date',
            'end_date',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        status = self.data.get('status')
        attendance_type = self.data.get('attendance_type')
        start_date = self.data.get('start_date')
        end_date = self.data.get('end_date')
        
        if search:
            queryset = queryset.filter(
                Q(employee_office_hour__employee_information__name__icontains = search)
                | Q(employee_office_hour__employee_information__slug__icontains = search)
            )
            
        if status:
            queryset = queryset.filter(
                status = status
            )
            
        if attendance_type:
            queryset = queryset.filter(
                attendance_type = attendance_type
            )
            
        if start_date and end_date:
            queryset = queryset.filter(
                working_date__range=(start_date, end_date)
            )

            
        return queryset
    
    
class EventOrNoticeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    start_date = django_filters.CharFilter(label="start_time",
                                         method="filter_model")
    end_date = django_filters.CharFilter(label="end_date",
                                         method="filter_model")
    type = django_filters.CharFilter(label="type",
                                         method="filter_model")

    class Meta:
        model = EventOrNotice
        fields = (
            'search',
            'start_date',
            'end_date',
            'type',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        start_date = self.data.get('start_date')
        end_date = self.data.get('end_date')
        type = self.data.get('type')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if start_date and end_date:
            queryset = queryset.filter(
                Q(start_date = start_date)
                | Q(end_date = end_date)
            )

        if type:
            queryset = queryset.filter(
                type__icontains = type
            )

            
        return queryset
    
    
class EmployeeTaskFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(label="search",
                                         method="filter_model")
    status = django_filters.CharFilter(label="status",
                                         method="filter_model")

    class Meta:
        model = EmployeeTask
        fields = (
            'search',
            'status',
            )

    def filter_model(self, queryset, name, value):
        search = self.data.get('search')
        status = self.data.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains = search)
                | Q(slug__icontains = search)
            )
            
        if status:
            queryset = queryset.filter(
                Q(status = status)
            )
            
        # if is_active:
        #     if is_active.lower() == 'true' :
        #         queryset = queryset.filter(
        #             is_active = True 
        #         )
        #     else:
        #         queryset = queryset.filter(
        #             is_active = False 
        #         )

            
        return queryset