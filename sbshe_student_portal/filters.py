# sbshe_student_portal/filters.py
import django_filters
from django.db import models
from .models import Department, Branch, Course, Assignment


class CourseFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(field_name='department__slug', lookup_expr='exact')
    branch = django_filters.CharFilter(field_name='branch__slug', lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = Course
        fields = ['department', 'branch', 'is_active']
    
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


class AssignmentFilter(django_filters.FilterSet):
    course = django_filters.CharFilter(field_name='course__slug', lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    deadline_after = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='gte')
    deadline_before = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='lte')
    
    class Meta:
        model = Assignment
        fields = ['course', 'is_active', 'deadline_after', 'deadline_before']