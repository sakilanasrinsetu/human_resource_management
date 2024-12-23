from django.contrib import admin
from employee.models import *

# Register your models here.


class EmployeeDivisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = EmployeeDivision
admin.site.register(EmployeeDivision, EmployeeDivisionAdmin)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = Department
        
admin.site.register(Department, DepartmentAdmin)

class GradingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','slug', 'created_at']

    class Meta:
        model = Grading
        
admin.site.register(Grading, GradingAdmin)


class RankingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = Ranking
        
admin.site.register(Ranking, RankingAdmin)


class DesignationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','slug', 'created_at']

    class Meta:
        model = Designation
        
admin.site.register(Designation, DesignationAdmin)


class EmployeeTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = EmployeeType
        
admin.site.register(EmployeeType, EmployeeTypeAdmin)


class EmployeeGuardianInformationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = EmployeeGuardianInformation
        
admin.site.register(EmployeeGuardianInformation, EmployeeGuardianInformationAdmin)


class EmployeeAddressInformationAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_address', 'created_at']

    class Meta:
        model = EmployeeAddressInformation
        
admin.site.register(EmployeeAddressInformation, EmployeeAddressInformationAdmin)


class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = ExamType
        
admin.site.register(ExamType, ExamTypeAdmin)


class EmployeeEducationInformationAdmin(admin.ModelAdmin):
    list_display = ['id', 'institution_name', 'created_at']

    class Meta:
        model = EmployeeEducationInformation
        
admin.site.register(EmployeeEducationInformation, EmployeeEducationInformationAdmin)


class BankInformationAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_name', 'created_at']

    class Meta:
        model = BankInformation
        
admin.site.register(BankInformation, BankInformationAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = Company
        
admin.site.register(Company, CompanyAdmin)

class EmployeeInformationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'slug', 'employee_id', 'work_station','employee_type','created_at']
    list_filter = ['work_station__name']

    class Meta:
        model = EmployeeInformation
        
admin.site.register(EmployeeInformation, EmployeeInformationAdmin)


class EmployeeInformationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_information', 'created_at']

    class Meta:
        model = EmployeeInformationLog
        
admin.site.register(EmployeeInformationLog, EmployeeInformationLogAdmin)

class EmployeeOfficeHourAdmin(admin.ModelAdmin):
    list_display = ['id', 'type','day', 'created_at']

    class Meta:
        model = EmployeeOfficeHour
        
admin.site.register(EmployeeOfficeHour, EmployeeOfficeHourAdmin)


class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_office_hour','created_by','check_in', 'check_out', 'working_description','status', 'attendance_type','total_office_hour', 'created_at']
    list_filter = ['employee_information__name', 'attendance_type', 'status']

    class Meta:
        model = EmployeeAttendance        
admin.site.register(EmployeeAttendance, EmployeeAttendanceAdmin)


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = EventType
admin.site.register(EventType, EventTypeAdmin)

class EventOrNoticeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = EventOrNotice
admin.site.register(EventOrNotice, EventOrNoticeAdmin)

class EmployeeCalendarAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = EmployeeCalendar
admin.site.register(EmployeeCalendar, EmployeeCalendarAdmin)

class EmployeeTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug','created_at']

    class Meta:
        model = EmployeeTask
admin.site.register(EmployeeTask, EmployeeTaskAdmin)

class EmployeeTaskStatusLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee_task', 'status','created_at']

    class Meta:
        model = EmployeeTaskStatusLog
admin.site.register(EmployeeTaskStatusLog, EmployeeTaskStatusLogAdmin)
