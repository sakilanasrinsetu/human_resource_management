from django.db import models

from django.utils.translation import gettext_lazy as _
from user.models import UserAccount
from django.utils.timezone import timedelta

from django.utils.translation import gettext_lazy as _
from utils.helpers import (
    time_str_mix_slug)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save, pre_save
from django.utils.text import slugify
from utils.generates import unique_slug_generator

# Create your models here.


CALENDER_TYPE = [
    ("BUSY", 'Busy'),
    ("FREE", 'Free'),
]

TASK_STATUS = [
    ("PENDING", 'Pending'),
    ("IN_PROGRESS", 'In Progress'),
    ("FEEDBACK", 'Feedback'),
    ("REJECT", 'Reject'),
    ("PAUSED", 'Paused'),
    ("DONE", 'Done'),
]

DAYS = [
        ("SATURDAY", "Saturday"),
        ("SUNDAY", "Sunday"),
        ("MONDAY", "Monday"),
        ("TUESDAY", "Tuesday"),
        ("WEDNESDAY", "Wednesday"),
        ("THURSDAY", "Thursday"),
        ("FRIDAY", "Friday"),
    ]


class Company(models.Model):
    COMPANY_STATUS = [
        ("ACTIVE", "Active"),
        ("SUSPENDED", "Suspended"),
        ("INACTIVE", "Inactive"),
        ("OTHERS", "Others"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    logo = models.TextField(null=True, blank=True)
    primary_phone = models.CharField(max_length=30)
    secondary_phone = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    website_url = models.URLField(max_length=255, null=True, blank=True)
    vat_registration_no = models.CharField(max_length=30, blank=True, null=True)
    registration_number = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=255)
    starting_date = models.DateField(null=True,blank=True)
    company_owner = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='companys')
    currency = models.CharField(max_length=20, null=True, blank=True) # Ex: BDT, DOLLAR
    status = models.CharField(max_length=10, choices=COMPANY_STATUS, default='ACTIVE')
    remaining_days_subscription_ends = models.CharField(max_length=50, null=True, blank=True) # Auto Generate
    subscription_ends = models.DateField()
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='company_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='company_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.id)
        
    class Meta:
        ordering = ["name"]
        


class OfficeLocation(models.Model):
    OFFICE_TYPE = [
        ('HEAD_OFFICE', "Head Office"),
        ('WAREHOUSE', "Warehouse"),
        ('BRANCH', "Branch"),
        ('STORE', "Store"),
        ('OTHERS', "Others"),
    ]
    name = models.CharField(max_length=550)
    slug = models.SlugField(max_length=255,unique=True)
    store_no = models.CharField(max_length=10, blank=True, null=True)
    bn_name = models.CharField(max_length=100,null=True)
    address = models.TextField(null=False)
    primary_phone = models.CharField(max_length=17)
    email = models.CharField(max_length=50, blank=True, null=True)
    map_link = models.URLField()
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='office_location_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='office_location_updated_bys',
        null=True, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        return str(self.id)
    
    class Meta:
        ordering = ['-name']
        
class EmployeeDivision(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    division_head = models.ForeignKey(
        UserAccount, on_delete=models.SET_NULL,  related_name='employee_divisions',
        null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_division_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_division_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-id"]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self.name)
        super().save(*args, **kwargs)

class Department(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    is_active = models.BooleanField(default=True)
    employee_division = models.ForeignKey(
        EmployeeDivision, on_delete=models.SET_NULL,  related_name='departments',
        null=True, blank=True)
    department_head = models.ForeignKey(
        UserAccount, on_delete=models.SET_NULL,  related_name='departments',
        null=True, blank=True)
    employee_need = models.PositiveBigIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='department_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='department_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self.name)
        super().save(*args, **kwargs)

class Grading(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    is_active = models.BooleanField(default=True)  
    remarks = models.TextField(null=True, blank=True) 
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='grading_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='grading_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self.name)
        super().save(*args, **kwargs)     
        
class Ranking(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    grade = models.ForeignKey(
        Grading, on_delete=models.SET_NULL,  related_name='rankings',
        null=True, blank=True)
    is_active = models.BooleanField(default=True) 
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='ranking_created_s')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='ranking_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-id"]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self.name)
        super().save(*args, **kwargs)     
        
class Designation(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)
    departments = models.ForeignKey(
        Department, on_delete=models.SET_NULL,  related_name='designations',
        null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='designation_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='designation_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self.name)
        super().save(*args, **kwargs)    
             
class EmployeeType(models.Model):
    name = models.CharField(max_length=255) # Full Time, Part-Time, Probation
    slug = models.SlugField(max_length=555, unique=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_type_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_type_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-id"]
    
class EmployeeGuardianInformation(models.Model):
    RELATIONSHIP_TYPE = [
        ('FATHER', 'Father'),
        ('MOTHER', 'Mother'),
        ('SISTER', 'Sister'),
        ('BROTHER', 'Brother'),
        ('HUSBAND', 'Husband'),
        ('WIFE', 'Wife'),
        ('OTHERS', 'Others'),
    ]
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=255,unique=True)
    occupation = models.CharField(max_length=250, blank=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    nid_number = models.CharField(max_length=150, blank=True, null=True)
    passport_number = models.CharField(max_length=150, blank=True, null=True)
    relationship_type = models.CharField(
        choices=RELATIONSHIP_TYPE, max_length=50, default="FATHER"
        )
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_guardian_information_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_guardian_information_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-id"]
    
class EmployeeAddressInformation(models.Model):
    ADDRESS_TYPE = [
        ('PERMANENT', 'Permanent'),
        ('PRESENT', 'Present'),
        ('OTHERS', 'Others'),
    ]
    full_address = models.CharField(max_length=550)
    city = models.CharField(max_length=250, blank=True)
    district_name = models.CharField(max_length=250, null = True, blank=True)
    division_name = models.CharField(max_length=250, null = True, blank=True)
    country_name = models.CharField(max_length=250, null = True, blank=True)
    address_type = models.CharField(
        choices=ADDRESS_TYPE, max_length=50, default="PERMANENT")
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_address_information_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_address_information_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return f"{(self.full_address)} and {str(self.id)}"
    
    class Meta:
        ordering = ["-id"]
    
class ExamType(models.Model):
    name = models.CharField(max_length=550)
    slug = models.SlugField(max_length=255,unique=True)
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='exam_type_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='exam_type_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ["-id"]
    
class EmployeeEducationInformation(models.Model):
    exam_type = models.ForeignKey(
        ExamType, on_delete=models.SET_NULL,
        related_name='employee_education_informations',
        null=True, blank=True)
    institution_name = models.CharField(max_length=355)
    slug = models.SlugField(max_length=255,unique=True)
    board_name = models.CharField(max_length=355, null=True, blank=None)
    grade = models.CharField(max_length=355, null=True, blank=None)
    file = models.TextField(blank=True, null=True)
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_education_information_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_education_information_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return f"Institution Name = {self.institution_name} and Exam Type = {self.exam_type.name}"
    
    class Meta:
        ordering = ["-id"]
    
class JobExperienceInformation(models.Model):
    company_name = models.CharField(max_length=355)
    slug = models.SlugField(max_length=255,unique=True)
    address = models.TextField(null=True, blank=None)
    website_url = models.URLField(null=True, blank=None)
    joining_date = models.DateField(null = True, blank = True)
    resign_date = models.DateField(null = True, blank = True)
    total_job_experience = models.CharField(max_length=355,null = True, blank = True)
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='job_experience_information_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='job_experience_information_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return str(self.company_name)
    
    class Meta:
        ordering = ["-id"]
    
class BankInformation(models.Model):
    account_name = models.CharField(max_length=355)
    slug = models.SlugField(max_length=255,unique=True)
    account_number = models.CharField(max_length=355, null=True, blank=None)
    bank_name = models.CharField(max_length=355, null=True, blank=None)
    branch_name = models.CharField(max_length=355, null=True, blank=None)
    routing_number = models.CharField(max_length=355, null=True, blank=None)
    expire_date = models.CharField(max_length=355, null=True, blank=None)
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='bank_information_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='bank_information_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return str(self.account_name)
    
    class Meta:
        ordering = ["-id"]
    
    
class EmployeeInformation(models.Model):
    user = models.OneToOneField(
        UserAccount, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="employee_informations"
    )
    employee_id = models.CharField(max_length=355,unique=True)
    image = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=355,blank=True, null=True)
    slug = models.SlugField(max_length=555, unique=True)
    nid_number = models.CharField(max_length=355,blank=True, null=True)
    passport_number = models.CharField(max_length=355,blank=True, null=True)
    phone_number = models.CharField(max_length=355,blank=True, null=True)
    reporting_person = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        related_name='employee_informations',
        null=True, blank=True)
    employee_company = models.ForeignKey(
        Company, on_delete=models.SET_NULL,
        related_name='employee_informations',
        null=True, blank=True)
    employee_type = models.ForeignKey(
        EmployeeType, on_delete=models.SET_NULL,
        related_name='employee_informations',
        null=True, blank=True)
    designations = models.ForeignKey(
        Designation, on_delete=models.SET_NULL,
        related_name='employee_informations',
        null=True, blank=True)
    work_station = models.ForeignKey(
        OfficeLocation, on_delete=models.SET_NULL,
        related_name='employee_informations',
        null=True, blank=True)
    rank = models.ForeignKey(
        Ranking, on_delete=models.SET_NULL,
        related_name='employee_informations',
        null=True, blank=True)
    guardian_information = models.ManyToManyField(
        to=EmployeeGuardianInformation,blank=True,
        related_name='employee_informations'
        )
    employee_address_information = models.ManyToManyField(
        to=EmployeeAddressInformation,blank=True,
        related_name='employee_informations'
        )
    employee_education_information = models.ManyToManyField(
        to=EmployeeEducationInformation,blank=True,
        related_name='employee_informations'
        )
    job_experience_information = models.ManyToManyField(
        to=JobExperienceInformation,blank=True,
        related_name='employee_informations'
        )
    bank_information = models.ManyToManyField(
        to=BankInformation,blank=True,
        related_name='employee_informations'
        )
    
    joining_date = models.DateField(blank=True, null=True)
    next_confirmation_date = models.DateField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    resign_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_information_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_information_updated_bys',
        null=True, blank=True)
    
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ["-id"]

    
class EmployeeInformationLog(models.Model):
    employee_information = models.ForeignKey(
        EmployeeInformation, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_information_logs')
    employee_type = models.ForeignKey(
        EmployeeType, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_information_logs',)
    employee_designation = models.ForeignKey(
        Designation, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_information_logs',)
    employee_rank = models.ForeignKey(
        Ranking, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_information_logs',)
    confirmation_date = models.DateTimeField(blank=True, null=True)
    employee_info = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_information_log_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_information_log_bys',
        null=True, blank=True)
    
    def __str__(self):
        if self.employee_information:
            return str(self.employee_information.name)
        else:
            return str(self.id)

class EmployeeOfficeHour(models.Model):
    TYPE = [
        ("REGULAR","Regular"),
        ("EXTRA","Extra"),
        ("SPECIAL","SPECIAL")
    ]
    employee_information = models.ManyToManyField(
        to=EmployeeInformation, blank=True, related_name='employee_office_hours')
    slug = models.CharField(max_length=250, blank=True, null=True)
    day = models.CharField(choices = DAYS, max_length=50,
                          blank=True, null = True)
    type = models.CharField(max_length=20, choices=TYPE, default="REGULAR")
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    grace_time = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_office_hour_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_office_hour_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        if self.employee_information:
            return f"Employee Name = {self.employee_information.name} and {self.get_day_display()}, Office Hour = {self.start_time} - {self.end_time}"
        return str(self.id)
                
class EmployeeAttendance(models.Model):
    ATTENDANCE_STATUS = [
        ("INITIALIZED", "Initialized"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]
    ATTENDANCE_TYPE = [
        ('ON_TIME', 'On Time'),
        ('OVER_TIME', 'Over Time'),
        ('LATE', 'Late'),
        ('ABSENT', 'Absent'),
        ('CASUAL_LEAVE', 'Casual Leave'),
        ('SICK_LEAVE', 'Sick Leave'),
        ('SPECIAL_LEAVE', 'Special Leave'),
        ('PATERNITY_LEAVE', 'Paternity Leave'),
        ('MATERNITY_LEAVE', 'Maternity Leave'),
        ('EXTRA_OFFICE_DAY', 'Extra Office Day'),
    ]
    employee_information = models.ForeignKey(
        EmployeeInformation, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_attendances')
    employee_office_hour = models.ForeignKey(
        EmployeeOfficeHour, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_attendances')
    slug = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default="APPROVED")
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE, default="ON_TIME")
    working_description = models.TextField(blank=True, null=True)
    total_office_hour = models.CharField(max_length=20, blank=True, null=True)
    
    working_date = models.DateTimeField(blank=True, null=True)
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    office_hour_type = models.CharField(max_length=50,blank=True, null=True)
    approved_by = models.ForeignKey(
        EmployeeInformation, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_attendance_approved_bys')
    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default = False)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_attendance_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_attendance_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        if self.employee_office_hour:
            return str(self.employee_office_hour.employee_information.name)
        return str(self.id)
    
class EmployeeAttendanceLog(models.Model):
    employee_attendance = models.ForeignKey(
        EmployeeAttendance, on_delete=models.SET_NULL, blank=True, null=True,  related_name='employee_attendance_logs')
    working_description = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=50,blank=True, null=True)
    status_display = models.CharField(max_length=50,blank=True, null=True)
    working_date = models.DateTimeField(blank=True, null=True)
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    status_change_by_info = models.JSONField(blank=True, null=True)
    approved_by_info = models.JSONField(blank=True, null=True)
    reason = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default = False)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_attendance_log_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_attendance_log_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return str(self.employee_attendance)
    

class EventType(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='event_type_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='event_type_updated_bys',
        null=True, blank=True)

    def __str__(self):
        return self.name 
    
class EventOrNotice(models.Model):
    TYPE = [
        ("NOTICE", 'Notice'),
        ("EVENT", 'Event'),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    event_url = models.TextField(blank=True, null=True)
    employee = models.ManyToManyField(
        to=EmployeeInformation,blank=True,
        related_name='event_or_notices'
        )
    office_location = models.ManyToManyField(
        to=OfficeLocation,blank=True,
        related_name='event_or_notices'
        )
    event_type = models.ForeignKey(
        EventType, on_delete=models.SET_NULL,blank=True, null = True,
        related_name='event_or_notices')
    
    type = models.CharField(max_length=50, 
                            choices=TYPE, default="EVENT")
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='event_or_notice_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='event_or_notice_updated_bys',
        null=True, blank=True)

    def __str__(self):
        return self.name 

class EmployeeTask(models.Model):
    task_no = models.CharField(max_length=150, unique = True)
    employee = models.ForeignKey(
        EmployeeInformation, on_delete=models.SET_NULL,blank=True, null = True,
        related_name='employee_tasks')
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, 
                            choices=TASK_STATUS, default="PENDING")
    approved_by = models.ForeignKey(
        EmployeeInformation, on_delete=models.SET_NULL,blank=True, null = True,
        related_name='approved_by_employee_tasks')
    
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_task_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_task_updated_bys',
        null=True, blank=True)

    def __str__(self):
        return self.name
    
class EmployeeTaskStatusLog(models.Model):
    employee_task = models.ForeignKey(
        EmployeeTask, on_delete=models.SET_NULL ,null=True, blank=True,related_name='employee_task_status_logs')
    status = models.CharField(max_length=150)
    status_display = models.CharField(max_length=150)
    status_reason = models.TextField(null=True, blank=True)
    status_change_by = models.JSONField(blank=True, null=True)
    status_change_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_task_status_log_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_task_status_log_updated_bys',
        null=True, blank=True)
    
    def __str__(self):
        return str(self.employee_task.task_no)
    
class EmployeeCalendar(models.Model):
    employee = models.ForeignKey(
        EmployeeInformation, on_delete=models.SET_NULL,blank=True, null = True,
        related_name='employee_calendars')
    event_type = models.ForeignKey(
        EventType, on_delete=models.SET_NULL,blank=True, null = True,
        related_name='employee_calendars')
    calender_type = models.CharField(max_length=50, 
                            choices=CALENDER_TYPE, default="FREE")
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,unique=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE ,related_name='employee_calendar_created_bys')
    updated_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE,  related_name='employee_calendar_updated_bys',
        null=True, blank=True)

    def __str__(self):
        return self.name