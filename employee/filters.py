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