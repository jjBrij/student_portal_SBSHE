# sbshe_student_portal/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.core.cache import cache
from django.db.models import Prefetch
from .models import Department, Branch, Course, CourseMaterial
from .serializers import (
    DepartmentSerializer, BranchSerializer, CourseListSerializer,
    CourseDetailSerializer, CourseMaterialSerializer, CourseMaterialCreateSerializer
)
from .filters import CourseFilter, DepartmentFilter, CourseMaterialFilter
from .tasks import log_admin_action_task, cleanup_orphan_files_task
from .permissions import IsAdminUser


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department model"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filterset_class = DepartmentFilter
    search_fields = ['name', 'description', 'introduction']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete('departments_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='create',
            model='Department',
            object_id=instance.id
        )
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete('departments_queryset')
        cache.delete(f'department_{instance.id}')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='update',
            model='Department',
            object_id=instance.id
        )
    
    def perform_destroy(self, instance):
        cache.delete('departments_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='delete',
            model='Department',
            object_id=instance.id
        )
        instance.delete()


class BranchViewSet(viewsets.ModelViewSet):
    """ViewSet for Branch model"""
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete('branches_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='create',
            model='Branch',
            object_id=instance.id
        )
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete('branches_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='update',
            model='Branch',
            object_id=instance.id
        )
    
    def perform_destroy(self, instance):
        cache.delete('branches_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='delete',
            model='Branch',
            object_id=instance.id
        )
        instance.delete()


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model"""
    queryset = Course.objects.select_related('department').prefetch_related('materials')
    filterset_class = CourseFilter
    search_fields = ['name', 'introduction', 'course_code', 'full_description', 'department__name']
    ordering_fields = ['name', 'course_code', 'created_at', 'updated_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'top_courses', 'filters']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseDetailSerializer
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete('courses_queryset_*')
        cache.delete('filters_data')
        cache.delete('top_courses')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='create',
            model='Course',
            object_id=instance.id
        )
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete('courses_queryset_*')
        cache.delete(f'course_{instance.id}')
        cache.delete('filters_data')
        cache.delete('top_courses')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='update',
            model='Course',
            object_id=instance.id
        )
    
    def perform_destroy(self, instance):
        cache.delete('courses_queryset_*')
        cache.delete('filters_data')
        cache.delete('top_courses')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='delete',
            model='Course',
            object_id=instance.id
        )
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def top_courses(self, request):
        """Get top courses - Public access"""
        cache_key = 'top_courses'
        data = cache.get(cache_key)
        
        if not data:
            top_courses = Course.objects.filter(
                is_active=True, 
                is_top_course=True
            ).select_related('department')[:10]
            serializer = CourseListSerializer(top_courses, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60 * 15)
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Get dynamic filter options - Public access"""
        cache_key = 'filters_data'
        data = cache.get(cache_key)
        
        if not data:
            departments = Department.objects.filter(is_active=True)
            branches = Branch.objects.filter(is_active=True)
            courses = Course.objects.filter(is_active=True)
            
            data = {
                'departments': [
                    {
                        'id': d.id, 
                        'name': d.name, 
                        'slug': d.slug,
                        'image_url': d.file.url if d.file else None
                    } 
                    for d in departments
                ],
                'branches': [
                    {
                        'id': b.id, 
                        'name': b.name, 
                        'slug': b.slug,
                        'image_url': b.file.url if b.file else None
                    } 
                    for b in branches
                ],
                'courses': [
                    {
                        'id': c.id, 
                        'name': c.name, 
                        'slug': c.slug,
                        'image_url': c.file.url if c.file else None
                    } 
                    for c in courses
                ],
                'course_types': [
                    {'value': 'online', 'label': 'Online'},
                    {'value': 'offline', 'label': 'Offline'},
                    {'value': 'hybrid', 'label': 'Hybrid (Online + Offline)'},
                ]
            }
            cache.set(cache_key, data, 60 * 30)
        
        return Response(data)


class CourseMaterialViewSet(viewsets.ModelViewSet):
    """
    Course Material ViewSet - Handles Assignments, Question Papers, Syllabus
    """
    # Simplified queryset without complex prefetch
    queryset = CourseMaterial.objects.select_related('course').all()
    filterset_class = CourseMaterialFilter
    search_fields = [
        'title', 'description', 'instructions', 
        'course__name', 'course_code', 'subject_code'
    ]
    ordering_fields = ['title', 'deadline', 'created_at', 'updated_at', 'material_type']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'types', 'by_type']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseMaterialCreateSerializer
        return CourseMaterialSerializer
    
    def get_queryset(self):
        """Override to ensure proper filtering"""
        queryset = super().get_queryset()
        # Apply filters if needed
        return queryset
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available material types for dropdown"""
        types = [
            {'value': 'assignment', 'label': 'Assignment'},
            {'value': 'question_paper', 'label': 'Question Paper'},
            {'value': 'syllabus', 'label': 'Syllabus'},
        ]
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Filter materials by type"""
        material_type = request.query_params.get('type')
        if material_type:
            queryset = self.get_queryset().filter(
                material_type=material_type, 
                is_active=True
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Type parameter required. Valid types: assignment, question_paper, syllabus'}, 
            status=400
        )
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete('materials_queryset')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='create',
            model='CourseMaterial',
            object_id=instance.id
        )
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete('materials_queryset')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='update',
            model='CourseMaterial',
            object_id=instance.id
        )
    
    def perform_destroy(self, instance):
        if instance.file:
            cleanup_orphan_files_task.delay(instance.file.path)
        cache.delete('materials_queryset')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='delete',
            model='CourseMaterial',
            object_id=instance.id
        )
        instance.delete()


class RootView(APIView):
    """
    Root API endpoint showing available endpoints
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "message": "Student Portal API",
            "version": "v1",
            "endpoints": {
                "departments": "/api/departments/",
                "branches": "/api/branches/",
                "courses": "/api/courses/",
                "materials": "/api/materials/",
                "materials_types": "/api/materials/types/",
                "materials_by_type": "/api/materials/by_type/",
                "top_courses": "/api/courses/top_courses/",
                "filters": "/api/courses/filters/",
                "auth": {
                    "login": "/api/auth/login/",
                    "register": "/api/auth/register/",
                    "refresh": "/api/auth/refresh/",
                    "logout": "/api/auth/logout/",
                    "me": "/api/auth/me/"
                },
                "swagger_ui": "/swagger/",
                "redoc": "/redoc/",
                "admin": "/admin/"
            }
        })