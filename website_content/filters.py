# website_content/filters.py

import django_filters
from django.db import models
from .models import WebsiteContent

class WebsiteContentFilter(django_filters.FilterSet):
    """Filter for Website Content"""
    menu = django_filters.NumberFilter(field_name='menu_id')
    menu_name = django_filters.CharFilter(field_name='menu__name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    class Meta:
        model = WebsiteContent
        fields = ['menu', 'menu_name', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(short_name__icontains=value) |
            models.Q(short_intro__icontains=value) |
            models.Q(intro__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(menu__name__icontains=value)
        )