# sbshe_student_portal/views.py - Complete file without swagger decorators
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Department, Branch, Course, Assignment
from .serializers import (
    DepartmentSerializer, BranchSerializer, CourseListSerializer,
    CourseDetailSerializer, AssignmentSerializer, AssignmentCreateSerializer
)
from .filters import CourseFilter, DepartmentFilter, AssignmentFilter
from .tasks import log_admin_action_task, cleanup_orphan_files_task
from .permissions import IsAdminUser, IsAdminOrReadOnly


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Department ViewSet
    Provides CRUD operations for departments
    
    ## Permissions:
    - GET: Anyone can view
    - POST/PUT/PATCH/DELETE: Admin only
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'description', 'introduction']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
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
    """
    Branch ViewSet
    Provides CRUD operations for branches
    
    ## Permissions:
    - GET: Anyone can view
    - POST/PUT/PATCH/DELETE: Admin only
    """
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
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


class CourseViewSet(viewsets.ModelViewSet):
    """
    Course ViewSet
    Provides CRUD operations for courses with dynamic filters
    
    ## Permissions:
    - GET: Anyone can view
    - POST/PUT/PATCH/DELETE: Admin only
    
    ## Filtering Options:
    - `?search=keyword` - Search in name, introduction, description
    - `?department=slug` - Filter by department
    - `?course_type=online` - Filter by course type
    - `?is_active=true` - Filter active courses
    - `?is_top_course=true` - Filter top courses
    - `?ordering=name` - Order by name
    - `?ordering=-created_at` - Order by newest first
    - `?page=1&page_size=20` - Pagination
    """
    queryset = Course.objects.select_related('department').prefetch_related('assignments')
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = CourseFilter
    search_fields = ['name', 'introduction', 'full_description', 'department__name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseDetailSerializer
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
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
    
    @action(detail=False, methods=['get'])
    def top_courses(self, request):
        """Get top courses with caching"""
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
        """Get dynamic filter options with caching"""
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
                        'image_url': d.image.url if d.image else None
                    } 
                    for d in departments
                ],
                'branches': [
                    {
                        'id': b.id, 
                        'name': b.name, 
                        'slug': b.slug,
                        'image_url': b.image.url if b.image else None
                    } 
                    for b in branches
                ],
                'courses': [
                    {
                        'id': c.id, 
                        'name': c.name, 
                        'slug': c.slug,
                        'image_url': c.image.url if c.image else None
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


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    Assignment ViewSet
    Provides CRUD operations for assignments
    
    ## Permissions:
    - GET: Anyone can view
    - POST/PUT/PATCH/DELETE: Admin only
    
    ## Filtering Options:
    - `?course=slug` - Filter by course
    - `?is_active=true` - Filter active assignments
    - `?deadline_after=2026-01-01T00:00:00Z` - Filter after date
    - `?deadline_before=2026-12-31T23:59:59Z` - Filter before date
    """
    queryset = Assignment.objects.select_related('course').all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = AssignmentFilter
    search_fields = ['title', 'description', 'instructions', 'course__name']
    ordering_fields = ['title', 'deadline', 'created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AssignmentCreateSerializer
        return AssignmentSerializer
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete('assignments_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='create',
            model='Assignment',
            object_id=instance.id
        )
    
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete('assignments_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='update',
            model='Assignment',
            object_id=instance.id
        )
    
    def perform_destroy(self, instance):
        if instance.file:
            cleanup_orphan_files_task.delay(instance.file.path)
        cache.delete('assignments_queryset')
        cache.delete('filters_data')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='delete',
            model='Assignment',
            object_id=instance.id
        )
        instance.delete()


# Root View for API
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
                "assignments": "/api/assignments/",
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