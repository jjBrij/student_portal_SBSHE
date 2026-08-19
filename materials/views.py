
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Subject, SubjectMaterial
from .serializers import (
    SubjectListSerializer,
    SubjectDetailSerializer,
    SubjectMaterialSerializer,
    SubjectMaterialCreateSerializer
)
from .filters import SubjectFilter, SubjectMaterialFilter
from sbshe_student_portal.permissions import IsAdminUser


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related('course__department').prefetch_related('materials')
    filterset_class = SubjectFilter
    search_fields = ['subject_code', 'subject_name', 'description', 'course__name']
    ordering_fields = ['subject_code', 'subject_name', 'academic_year', 'semester', 'created_at']
    ordering = ['academic_year', 'semester', 'subject_code']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'materials']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        # ✅ Use SubjectListSerializer for both list and retrieve
        return SubjectListSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
    
    @action(detail=True, methods=['get'], url_path='materials')
    def materials(self, request, pk=None):
        """Get all materials for a specific subject"""
        subject = self.get_object()
        materials = subject.materials.filter(is_active=True)
        
        material_type = request.query_params.get('material_type')
        if material_type:
            materials = materials.filter(material_type=material_type)
        
        serializer = SubjectMaterialSerializer(materials, many=True, context={'request': request})
        return Response(serializer.data)


class SubjectMaterialViewSet(viewsets.ModelViewSet):
    """ViewSet for Subject Material"""
    queryset = SubjectMaterial.objects.select_related('subject__course__department')
    filterset_class = SubjectMaterialFilter
    search_fields = ['subject__subject_code', 'subject__subject_name']
    ordering_fields = ['uploaded_at', 'updated_at']
    ordering = ['-uploaded_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'types']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubjectMaterialCreateSerializer
        return SubjectMaterialSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get all available material types"""
        types = [
            {'value': choice[0], 'label': choice[1]}
            for choice in SubjectMaterial.MATERIAL_TYPE_CHOICES
        ]
        return Response(types)