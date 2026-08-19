# student_form/filters.py

import django_filters
from django.db import models
from .models import StudentForm


class StudentFormFilter(django_filters.FilterSet):
    course = django_filters.CharFilter(field_name='course__slug', lookup_expr='exact')
    course_id = django_filters.NumberFilter(field_name='course_id')
    course_code = django_filters.CharFilter(field_name='course_code', lookup_expr='icontains')
    copy_type = django_filters.CharFilter(field_name='copy_type', lookup_expr='exact')
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = StudentForm
        fields = ['course', 'course_id', 'course_code', 'copy_type', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(father_name__icontains=value) |
            models.Q(email__icontains=value) |
            models.Q(phone__icontains=value) |
            models.Q(address__icontains=value) |
            models.Q(course__name__icontains=value)
        )