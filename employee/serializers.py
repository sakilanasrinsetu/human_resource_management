from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from employee.models import *
from human_resource_management import settings
from user.models import UserInformation
from user.serializers import UserDetailsSerializer
from utils.generates import unique_slug_generator
import base64
from drf_extra_fields.fields import Base64FileField, Base64ImageField

class Base64PDFField(serializers.Field):
    def to_internal_value(self, data):
        try:
            # Decoding base64 string to bytes
            decoded_data = base64.b64decode(data)
            return decoded_data
        except TypeError:
            raise serializers.ValidationError("Invalid base64 data")

    def to_representation(self, value):
        # Not needed for write operations, just returning the value as is
        return value
    
class BaseSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = UserAccount
        fields = [
            'id',
            'email',
            'phone',
            'is_active',
            'user_details'
        ]
        
    def get_user_details(self, obj):
        name = '-'
        profile_pic = settings.NOT_FOUND_IMAGE
        
        user_information_qs = UserInformation.objects.filter(user = obj).last()
        if user_information_qs:
            name = user_information_qs.name
            if user_information_qs.image:
                profile_pic = user_information_qs.image
        
        context = {
            'name':name,
            'profile_pic':profile_pic,
        }
        
        return context
    
    
class OfficeLocationListSerializer(serializers.ModelSerializer): 
    slug = serializers.CharField(read_only = True)

    class Meta:
        model = OfficeLocation
        fields = [
            'id',
            'name',
            'slug',
            'primary_phone',
            'store_no',
            'email',
                  ]
        
class UserInformationBaseSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField(read_only = True)
    user_type = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = UserAccount
        fields = [
                    'id',  
                    'email',  
                    'phone',  
                    'employee_info',  
                    'user_type',  
                ]
        
    def get_employee_info(self, obj):
        employee_id = None
        name = None
        image = None
        slug = None
        employee_qs = EmployeeInformation.objects.filter(user= obj).last()
        
        if employee_qs:
            employee_id = employee_qs.employee_id
            name = employee_qs.name
            image = employee_qs.image
            slug = employee_qs.slug
            
        context = {
            'employee_id': employee_id,
            'name': name,
            'image': image,
            'slug': slug,
        }
        return context
        
    def get_user_type(self, obj):
        name = None
        slug = None
        qs = UserInformation.objects.filter(user= obj).last()
        
        if qs.user_type:
            name = qs.user_type.name
            slug = qs.user_type.slug
            
        context = {
            'name': name,
            'slug': slug,
        }
        return context
    
class CompanySerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ['slug', 'created_by', 'updated_by', 'company_owner']
        
class OfficeLocationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)

    class Meta:
        model = OfficeLocation
        fields = "__all__"
        read_only_fields = ['slug', 'created_by', 'updated_by', 'company_owner']


class EmployeeDivisionSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    division_head = serializers.CharField()
    
    class Meta:
        model = EmployeeDivision
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["division_head"] = UserInformationBaseSerializer(read_only=True)
        return super(EmployeeDivisionSerializer, self).to_representation(instance)
    
    
class EmployeeDivisionListSerializer(serializers.ModelSerializer):
    division_head = UserInformationBaseSerializer(read_only = True)
    class Meta:
        model = EmployeeDivision
        fields = [
                  'id',
                  'name',
                  'slug',
                  'division_head',
                  ]
    
class EmployeeDepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
                    'id',  
                    'name',  
                    'slug',  
                ]
        
class EmployeeDepartmentSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    employee_need = serializers.CharField(read_only = True)
    employee_division = serializers.CharField()
    department_head = serializers.CharField()
    class Meta:
        model = Department
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["employee_division"] = EmployeeDivisionListSerializer(read_only=True)
        self.fields["department_head"] = UserInformationBaseSerializer(read_only=True)
        return super(EmployeeDepartmentSerializer, self).to_representation(instance)

class EmployeeDesignationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    departments = serializers.CharField()
    class Meta:
        model = Designation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["departments"] = EmployeeDepartmentListSerializer(read_only=True)
        return super(EmployeeDesignationSerializer, self).to_representation(instance)
    
class EmployeeGradeSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    
    class Meta:
        model = Grading
        fields = '__all__'
    
class EmployeeRankingSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    grade = serializers.CharField()
    
    class Meta:
        model = Ranking
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["grade"] = EmployeeGradeSerializer(read_only=True)
        return super(EmployeeRankingSerializer, self).to_representation(instance)

class EmployeeTypeSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    
    class Meta:
        model = EmployeeType
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserSerializer(read_only=True)
        return super(EmployeeTypeSerializer, self).to_representation(instance)

class EmployeeAddressInformationSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    address_type_display = serializers.CharField(source='get_address_type_display')
    # area_name = AreaSerializer(read_only = True)
    district_name = serializers.CharField(read_only=True)
    division_name = serializers.CharField(read_only=True)
    country_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = EmployeeAddressInformation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["area_name"] = AreaSerializer(read_only=True)
        return super(EmployeeAddressInformationSerializer, self).to_representation(instance)

        
class EmployeeAddressInformationCreateSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    area_name = serializers.CharField(write_only = True)
    
    class Meta:
        model = EmployeeAddressInformation
        fields = '__all__'
        
    
class EmployeeGuardianInformationCreateSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    slug = serializers.CharField(read_only = True) 
    
    class Meta:
        model = EmployeeGuardianInformation
        fields = '__all__'
        
    
class ExamTypeSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    slug = serializers.CharField(read_only = True) 
    
    class Meta:
        model = ExamType
        fields = '__all__'
        
class EmployeeGuardianInformationSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    slug = serializers.CharField(read_only = True) 
    relationship_type_display = serializers.CharField(source='get_relationship_type_display')
    
    class Meta:
        model = EmployeeGuardianInformation
        fields = '__all__'
        
        
class Base64PDFField(serializers.Field):
    def to_internal_value(self, data):
        try:
            # Decoding base64 string to bytes
            decoded_data = base64.b64decode(data)
            return decoded_data
        except TypeError:
            raise serializers.ValidationError("Invalid base64 data")

    def to_representation(self, value):
        # Not needed for write operations, just returning the value as is
        return value
class EmployeeEducationInformationSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    slug = serializers.CharField(read_only = True)
    exam_type = serializers.CharField(write_only = True)
    file = Base64PDFField(required=False)
    
    class Meta:
        model = EmployeeEducationInformation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["exam_type"] = ExamTypeSerializer(read_only=True)
        return super(EmployeeEducationInformationSerializer, self).to_representation(instance)
        
    def create(self, validated_data):
        image_file = validated_data.get('file', None)
        file = validated_data.pop('file', None)
        
        path = 'employee_certificate'
        if image_file:
            filename = "certificate.pdf"
            
            # Decode base64 data
            pdf_data = base64.b64decode(image_file)
            
            # Write binary data to a PDF file
            with open(filename, 'wb') as f:
                f.write(pdf_data)
            
            # Pass the file path to the image_upload function
            image = image_upload(file=open(filename, 'rb'), path=path)
            
            if image:
                # Create the EmployeeEducationInformation instance
                qs = EmployeeEducationInformation.objects.create(**validated_data)
                qs.file = image
                qs.save()
                
                return True
                
        return EmployeeEducationInformation.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        image_file = validated_data.get('file', None)
        file = validated_data.pop('file', None)
        
        if image_file:
            # If a new file is provided, handle it similar to the create method
            path = 'employee_certificate'
            filename = "certificate.pdf"
            
            # Decode base64 data
            pdf_data = base64.b64decode(image_file)
            
            # Write binary data to a PDF file
            with open(filename, 'wb') as f:
                f.write(pdf_data)
            
            # Upload the file and assign it to the instance
            file = image_upload(file=open(filename, 'rb'), path=path)
            instance.file = file
        
        # Update other fields if provided
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Save the instance
        instance.file = file
        instance.save()
    
        return instance


class JobExperienceInformationSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    slug = serializers.CharField(read_only = True)
    total_job_experience = serializers.SerializerMethodField(read_only = True)
    
    joining_date = serializers.DateField(format="%m/%d/%Y")
    resign_date = serializers.DateField(format="%m/%d/%Y")
    
    class Meta:
        model = JobExperienceInformation
        fields = '__all__'
        
    def get_total_job_experience(self, obj):
        total_job_experience = None
        
        if obj.joining_date and obj.resign_date:
            # today = today + timedelta(days=65)
            remaining_time = obj.resign_date - obj.joining_date
            
            if remaining_time > timedelta(days=0):
                total_days = remaining_time.days
                # Calculate years
                years, days_remainder = divmod(total_days, 365)
                # Calculate months
                months, days_remainder = divmod(days_remainder, 30)
                # Calculate remaining days
                days = days_remainder

                # Print the result
                total_job_experience = f"{years} Years, {months} Months, {days} Days"
                
                obj.total_job_experience = total_job_experience
                obj.save()
        
        return total_job_experience
        
class BankInformationSerializer(serializers.ModelSerializer):
    created_by = BaseSerializer(read_only = True)
    updated_by = BaseSerializer(read_only = True)
    slug = serializers.CharField(read_only = True)
    
    class Meta:
        model = BankInformation
        fields = '__all__'
        
class OfficeWiseEmployeeInformationListSerializer(serializers.ModelSerializer):
    employee_list = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = OfficeLocation
        fields = [
                'id',  
                'name',  
                'slug',  
                'employee_list',  
                ]
        
    def get_employee_list(self, obj):
        employee_list = []
        employee_qs = EmployeeInformation.objects.filter(work_station__slug = obj.slug)
        employee_list = employee_qs.values_list('id', 'name', 'slug')
        
        return employee_list
        
class EmployeeInformationListSerializer(serializers.ModelSerializer):
    designations = serializers.SerializerMethodField(read_only=True)
    departments = serializers.SerializerMethodField(read_only=True)
    # employee_type = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    office_location = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = EmployeeInformation
        fields = [
                    'id',  
                    'employee_id',
                    'name',
                    'slug',
                    'departments',
                    'designations',
                    'employee_type',
                    'image',
                    'email',
                    'phone',
                    'office_location',
                ]
        
    def get_image(self, obj):
        image = settings.NOT_FOUND_IMAGE
        if obj.image:
            image = obj.image
        return image

    def get_office_location(self, obj):
        office_location = "N/A"
        if obj.work_station:
            office_location = obj.work_station.name
        return office_location

    def get_email(self, obj):
        email = "N/A"
        if obj.user:
            email = obj.user.email
        return email
    
    def get_work_station(self, obj):
        work_station = "N/A"
        if obj.work_station:
            work_station = obj.work_station.name
        return work_station
    
    def get_designations(self, obj):
        designations = "N/A"
        if obj.designations:
            designations = obj.designations.name
        return designations

    def get_departments(self, obj):
        departments = "N/A"
        if obj.designations:
            if obj.designations.departments:
                departments = obj.designations.departments.name
        return departments

    def get_phone(self, obj):
        phone = "N/A"
        if obj.user:
            phone = obj.user.phone
        return phone

        
# class EmployeeInformationListSerializer(serializers.ModelSerializer):
#     designations = serializers.SerializerMethodField(read_only=True)
#     departments = serializers.SerializerMethodField(read_only=True)
#     employee_type = serializers.SerializerMethodField(read_only=True)
#     image = serializers.SerializerMethodField(read_only=True)
#     email = serializers.SerializerMethodField(read_only=True)
#     phone = serializers.SerializerMethodField(read_only=True)
#     office_location = serializers.SerializerMethodField(read_only=True)
#     employee_address_information = serializers.SerializerMethodField(read_only=True)
#     employee_education_information = serializers.SerializerMethodField(read_only=True)
#     job_experience_information = serializers.SerializerMethodField(read_only=True)
#     bank_information = serializers.SerializerMethodField(read_only=True)
#     guardian_information = serializers.SerializerMethodField(read_only=True)
#     pos_area = serializers.SerializerMethodField(read_only=True)
#     pos_reason = serializers.SerializerMethodField(read_only=True)
#     work_station = serializers.SerializerMethodField(read_only=True)
#     rank = serializers.SerializerMethodField(read_only=True)
#     employee_company = serializers.SerializerMethodField(read_only=True)
#     reporting_person = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = EmployeeInformation
#         fields = [
#             'id',
#             'employee_id',
#             'name',
#             'slug',
#             'email',
#             'phone',
#             'image',
#             'designations',
#             'departments',
#             'office_location',
#             'employee_type',
#             'reporting_person',
#             'employee_company',
#             'employee_type',
#             'designations',
#             'pos_area',
#             'pos_reason',
#             'work_station',
#             'rank',
#             'guardian_information',
#             'employee_address_information',
#             'employee_education_information',
#             'job_experience_information',
#             'bank_information',
#             'nid_number',
#             'passport_number',
#             'joining_date',
#             'next_confirmation_date',
#             'date_of_birth',
#             'resign_date',
#         ]

#     def get_image(self, obj):
#         image = settings.NOT_FOUND_IMAGE
#         if obj.image:
#             image = obj.image
#         return image

#     def get_office_location(self, obj):
#         office_location = "N/A"
#         if obj.work_station:
#             office_location = obj.work_station.name
#         return office_location

#     def get_email(self, obj):
#         email = "N/A"
#         if obj.user:
#             email = obj.user.email
#         return email

#     def get_pos_area(self, obj):
#         pos_area = "N/A"
#         if obj.pos_area:
#             pos_area = obj.pos_area.name
#         return pos_area

#     def get_pos_reason(self, obj):
#         pos_reason = "N/A"
#         if obj.pos_reason:
#             pos_reason = obj.pos_reason.name
#         return pos_reason

#     def get_employee_company(self, obj):
#         employee_company = "N/A"
#         if obj.employee_company:
#             employee_company = obj.employee_company.name
#         return employee_company

#     def get_work_station(self, obj):
#         work_station = "N/A"
#         if obj.work_station:
#             work_station = obj.work_station.name
#         return work_station

#     def get_rank(self, obj):
#         rank = "N/A"
#         if obj.rank:
#             rank = obj.rank.name
#         return rank

#     def get_phone(self, obj):
#         phone = "N/A"
#         if obj.user:
#             phone = obj.user.phone
#         return phone

#     def get_reporting_person(self, obj):
#         reporting_person = "N/A"
#         if obj.reporting_person:
#             reporting_person = obj.reporting_person
#         return reporting_person

#     def get_designations(self, obj):
#         designations = "N/A"
#         if obj.designations:
#             designations = obj.designations.name
#         return designations

#     def get_departments(self, obj):
#         departments = "N/A"
#         if obj.designations:
#             if obj.designations.departments:
#                 departments = obj.designations.departments.name
#         return departments

#     def get_employee_type(self, obj):
#         employee_type = "N/A"
#         if obj.designations:
#             employee_type = obj.employee_type.name
#         return employee_type

#     def get_employee_address_information(self, obj):
#         employee_address_infos = obj.employee_address_information.all()
#         if not employee_address_infos:
#             return "N/A"

#         address_info_list = []
#         for info in employee_address_infos:
#             formatted_info = {
#                 'city': info.city,
#                 'district_name': info.district_name,
#                 'division_name': info.division_name,
#                 'full_address': info.full_address,
#                 'country_name': info.country_name,
#                 'address_type': info.address_type,
#                 'remarks': info.remarks,
#             }
#             address_info_list.append(formatted_info)
#         return address_info_list

#     def get_employee_education_information(self, obj):
#         employee_education_infos = obj.employee_education_information.all()
#         if not employee_education_infos:
#             return "N/A"

#         education_info_list = []
#         for info in employee_education_infos:
#             formatted_info = {
#                 'exam_type': info.exam_type.name,
#                 'institute_name': info.institution_name,
#                 'board_name': info.board_name,
#                 'grade': info.grade,
#                 'remarks': info.remarks,
#             }
#             education_info_list.append(formatted_info)
#         return education_info_list

#     def get_job_experience_information(self, obj):
#         employee_job_experience_infos = obj.job_experience_information.all()
#         if not employee_job_experience_infos:
#             return "N/A"

#         job_experience_info_list = []
#         for info in employee_job_experience_infos:
#             formatted_info = {
#                 'company_name': info.company_name,
#                 'address': info.address,
#                 'joining_date': info.joining_date,
#                 'resign_date': info.resign_date,
#                 'job_experience': info.total_job_experience,
#             }
#             job_experience_info_list.append(formatted_info)
#         return job_experience_info_list

#     def get_bank_information(self, obj):
#         employee_bank_infos = obj.bank_information.all()
#         if not employee_bank_infos:
#             return "N/A"

#         job_bank_info_list = []
#         for info in employee_bank_infos:
#             formatted_info = {
#                 'bank_account_name': info.account_name,
#                 'account_number': info.account_number,
#                 'bank_name': info.bank_name,
#                 'branch_name': info.branch_name,
#                 'expire_date': info.expire_date,
#             }
#             job_bank_info_list.append(formatted_info)
#         return job_bank_info_list

#     def get_guardian_information(self, obj):
#         employee_gurdian_infos = obj.guardian_information.all()
#         if not employee_gurdian_infos:
#             return "N/A"

#         gurdian_info_list = []
#         for info in employee_gurdian_infos:
#             formatted_info = {
#                 'name': info.name,
#                 'occupation': info.occupation,
#                 'phone_number': info.phone_number,
#                 'nid_number': info.nid_number,
#                 'passport_number': info.passport_number,
#                 'relation_type': info.relationship_type,
#             }
#             gurdian_info_list.append(formatted_info)
#         return gurdian_info_list


class EmployeeInformationCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    employee_type = serializers.CharField()
    designations = serializers.CharField()
    work_station = serializers.CharField()
    rank = serializers.CharField()
    pos_area = serializers.CharField()
    reporting_person = serializers.CharField()
    pos_reason = serializers.CharField()

    
    class Meta:
        model = EmployeeInformation
        fields = [
                    'id',  
                    'employee_id',  
                    'image',  
                    'name',  
                    'nid_number',  
                    'passport_number',  
                    'employee_type',  
                    'designations',  
                    'work_station',
                    'reporting_person',
                    'rank',
                    'pos_area',
                    'pos_reason',
                    'joining_date',
                    'date_of_birth',
                    'next_confirmation_date',
                ]
        
    def create(self, validated_data):
        image_file = validated_data.pop('image', None)
        if image_file:
            path ='employee'
            image = image_upload(file=image_file, path=path)
            if image:
                return EmployeeInformation.objects.create(image=image, **validated_data)
        return EmployeeInformation.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        image = validated_data.get('image')
        if image:
            image_file = validated_data.pop('image', None)
            path = 'employee'
            image = image_upload(file=image_file, path=path)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            if image:
                instance.image = image
            
            instance.save()
        return instance

class EmployeeInformationLiteSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only=True)
    updated_by = serializers.CharField(read_only=True)
    guardians = EmployeeGuardianInformationSerializer(many=True, read_only=True)
    class Meta:
        model = EmployeeInformation
        exclude = [
            'guardian_information',
            'employee_address_information',
            'employee_education_information',
            'bank_information'
            ] 

    def to_representation(self, instance):
        representation = super(EmployeeInformationLiteSerializer, self).to_representation(instance)
        
        representation['user'] = UserSerializer(instance.user).data

        return representation
    

class EmployeeUserSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = UserAccount
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'is_active',
            'user_type'
        ]
        
    def get_user_type(self, obj):
        name = None
        slug = None
        qs = UserInformation.objects.filter(user= obj).last()
        
        if qs.user_type:
            name = qs.user_type.name
            slug = qs.user_type.slug
            
        context = {
            'name': name,
            'slug': slug,
        }
        return context
        
from datetime import datetime
class EmployeeInformationDetailsSerializer(serializers.ModelSerializer):
    user = EmployeeUserSerializer(read_only = True)
    created_by = BaseSerializer(read_only=True)
    updated_by = BaseSerializer(read_only=True)
    employee_type = EmployeeTypeSerializer(read_only=True)
    designations = EmployeeDesignationSerializer(read_only=True)
    work_station = OfficeLocationListSerializer(read_only=True)
    rank = EmployeeRankingSerializer(read_only=True)
    guardian_information = EmployeeGuardianInformationSerializer(many=True, read_only=True)
    employee_address_information = EmployeeAddressInformationSerializer(many=True, read_only=True)
    employee_education_information = EmployeeEducationInformationSerializer(many=True, read_only=True)
    job_experience_information = JobExperienceInformationSerializer(many=True, read_only=True)
    bank_information = BankInformationSerializer(many=True, read_only=True)
    joining_date = serializers.SerializerMethodField(read_only = True)
    date_of_birth = serializers.SerializerMethodField(read_only = True)
    next_confirmation_date = serializers.SerializerMethodField(read_only = True)
    resign_date = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = EmployeeInformation
        fields = '__all__'
    
    def get_next_confirmation_date(self, obj):
        default_date = "-"

        if obj.next_confirmation_date:
            confirmation_date = obj.next_confirmation_date
            return confirmation_date.strftime("%d/%m/%Y")
        else:
            return default_date


    def get_resign_date(self, obj):
        default_date = "-"

        if obj.resign_date:
            return obj.resign_date.strftime("%d/%m/%Y")
        else:
            return default_date


    def get_joining_date(self, obj):
        default_date = "-"

        if obj.joining_date:
            return obj.joining_date.strftime("%d/%m/%Y")
        else:
            return default_date


    def get_date_of_birth(self, obj):
        default_date = "-"

        if obj.date_of_birth:
            return obj.date_of_birth.strftime("%d/%m/%Y")
        else:
            return default_date