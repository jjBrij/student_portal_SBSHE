# materials/filters.py

import django_filters
from django.db import models
from .models import Subject, SubjectMaterial


class SubjectFilter(django_filters.FilterSet):
    """Filter for Subject model"""
    course = django_filters.CharFilter(field_name='course__slug', lookup_expr='exact')
    course_id = django_filters.NumberFilter(field_name='course_id')
    department = django_filters.CharFilter(field_name='course__department__slug', lookup_expr='exact')
    academic_year = django_filters.CharFilter(field_name='academic_year', lookup_expr='exact')
    semester = django_filters.CharFilter(field_name='semester', lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = Subject
        fields = ['course', 'course_id', 'department', 'academic_year', 'semester', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(subject_code__icontains=value) |
            models.Q(subject_name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(course__name__icontains=value) |
            models.Q(course__course_code__icontains=value)
        )


class SubjectMaterialFilter(django_filters.FilterSet):
    """Filter for Subject Material model"""
    subject = django_filters.CharFilter(field_name='subject__slug', lookup_expr='exact')
    subject_id = django_filters.NumberFilter(field_name='subject_id')
    material_type = django_filters.CharFilter(field_name='material_type', lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = SubjectMaterial
        fields = ['subject', 'subject_id', 'material_type', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(subject__subject_code__icontains=value) |
            models.Q(subject__subject_name__icontains=value)
        )