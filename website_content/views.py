# website_content/views.py

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import WebsiteContent, Menu
from .serializers import WebsiteContentSerializer, MenuSerializer
from .filters import WebsiteContentFilter
from sbshe_student_portal.permissions import IsAdminUser


class WebsiteContentViewSet(viewsets.ModelViewSet):
    """ViewSet for Website Content"""
    queryset = WebsiteContent.objects.select_related('menu')
    serializer_class = WebsiteContentSerializer
    filterset_class = WebsiteContentFilter
    search_fields = ['name', 'short_name', 'short_intro', 'intro', 'description', 'menu__name']
    ordering_fields = ['name', 'date', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name','slug']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]