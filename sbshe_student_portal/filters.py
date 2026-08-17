
import django_filters
from django.db import models
from .models import Department, Branch, Course, CourseMaterial


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


class CourseMaterialFilter(django_filters.FilterSet):
    course = django_filters.CharFilter(field_name='course__slug', lookup_expr='exact')
    course_id = django_filters.NumberFilter(field_name='course_id')
    course_code = django_filters.CharFilter(field_name='course_code', lookup_expr='icontains')
    material_type = django_filters.CharFilter(field_name='material_type', lookup_expr='exact')
    subject_code = django_filters.CharFilter(field_name='subject_code', lookup_expr='icontains')
    academic_year = django_filters.CharFilter(field_name='academic_year', lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    deadline_after = django_filters.DateFilter(field_name='deadline', lookup_expr='gte')
    deadline_before = django_filters.DateFilter(field_name='deadline', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = CourseMaterial
        fields = [
            'course', 'course_id', 'course_code', 'material_type',
            'subject_code', 'academic_year', 'is_active',
            'deadline_after', 'deadline_before'
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(instructions__icontains=value) |
            models.Q(course__name__icontains=value) |
            models.Q(subject_code__icontains=value)
        )