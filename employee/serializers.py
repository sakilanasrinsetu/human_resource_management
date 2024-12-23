from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from employee.models import *


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ['slug', 'created_by', 'updated_by', 'company_owner']
        
class OfficeLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfficeLocation
        fields = "__all__"

class EmployeeDivisionSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeDivision
        fields = "__all__"
        
