# sbshe_student_portal/filters.py

import django_filters
from django.db import models
from .models import Department, Branch, Course


class CourseFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(method='filter_department')
    department_id = django_filters.NumberFilter(field_name='department_id')
    department_slug = django_filters.CharFilter(field_name='department__slug')
    branch = django_filters.CharFilter(field_name='branch__slug', lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = Course
        fields = ['department', 'department_id', 'department_slug', 'branch', 'is_active']
    
    def filter_department(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(department_id=int(value))
        return queryset.filter(department__slug=value)
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(introduction__icontains=value) |
            models.Q(full_description__icontains=value) |
            models.Q(department__name__icontains=value)
        )


class DepartmentFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = Department
        fields = ['is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(introduction__icontains=value)
        )