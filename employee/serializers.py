from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from employee.models import *
from user.serializers import UserDetailsSerializer
from utils.generates import unique_slug_generator



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
    
    class Meta:
        model = EmployeeDivision
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["division_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeDivisionSerializer, self).to_representation(instance)
    
class EmployeeDepartmentSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    class Meta:
        model = Department
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeDepartmentSerializer, self).to_representation(instance)

class EmployeeDesignationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    class Meta:
        model = Designation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeDesignationSerializer, self).to_representation(instance)
    
class EmployeeGradeSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    
    class Meta:
        model = Grading
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeGradeSerializer, self).to_representation(instance)
    
class EmployeeRankingSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    slug = serializers.CharField(read_only = True)
    
    class Meta:
        model = Ranking
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeRankingSerializer, self).to_representation(instance)

class EmployeeTypeSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    
    class Meta:
        model = EmployeeType
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeTypeSerializer, self).to_representation(instance)

class EmployeeAddressInformationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    
    class Meta:
        model = EmployeeAddressInformation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeAddressInformationSerializer, self).to_representation(instance)
    
class EmployeeGuardianInformationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    
    class Meta:
        model = EmployeeGuardianInformation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeGuardianInformationSerializer, self).to_representation(instance)

class EmployeeEducationInformationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    
    class Meta:
        model = EmployeeEducationInformation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(EmployeeEducationInformationSerializer, self).to_representation(instance)

class BankInformationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only = True)
    updated_by = serializers.CharField(read_only = True)
    
    class Meta:
        model = BankInformation
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields["department_head"] = UserDetailsSerializer(read_only=True)
        return super(BankInformationSerializer, self).to_representation(instance)

class EmployeeInformationSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only=True)
    updated_by = serializers.CharField(read_only=True)
    guardians = EmployeeGuardianInformationSerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeInformation
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(EmployeeInformationSerializer, self).to_representation(instance)
        
        representation['user'] = UserDetailsSerializer(instance.user).data

        return representation


class EmployeeInformationLiteSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(read_only=True)
    updated_by = serializers.CharField(read_only=True)
    guardians = EmployeeGuardianInformationSerializer(many=True, read_only=True)
    class Meta:
        model = EmployeeInformation
        exclude = ['guardian_information', 'employee_address_information','employee_education_information','bank_information'] 

    def to_representation(self, instance):
        representation = super(EmployeeInformationLiteSerializer, self).to_representation(instance)
        
        representation['user'] = UserDetailsSerializer(instance.user).data

        return representation
        
