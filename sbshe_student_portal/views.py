# sbshe_student_portal/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.core.cache import cache
from django.db.models import Q, Count
from .models import Department, Branch, Course
from .serializers import (
    DepartmentSerializer, BranchSerializer, CourseListSerializer,
    CourseDetailSerializer
)
from .filters import CourseFilter, DepartmentFilter
from .tasks import log_admin_action_task
from .permissions import IsAdminUser


class DepartmentViewSet(viewsets.ModelViewSet):
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
    queryset = Course.objects.select_related('department')
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


# sbshe_student_portal/views.py

class RootView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        base_url = f"{request.scheme}://{request.get_host()}"
        
        return Response({
            "message": "Student Portal API",
            "version": "v1",
            "base_url": base_url,
            "endpoints": {
                "departments": f"{base_url}/api/departments/",
                "branches": f"{base_url}/api/branches/",
                "courses": f"{base_url}/api/courses/",
                "subjects": f"{base_url}/api/materials/subjects/",
                "materials": f"{base_url}/api/materials/materials/",
                "subject_material_types": f"{base_url}/api/materials/materials/types/",
                "subject_materials_by_type": f"{base_url}/api/materials/materials/by_type/",
                "website_content": f"{base_url}/api/website-content/",  # ADD THIS
                "student_forms": f"{base_url}/api/student-forms/",
                "student_forms_stats": f"{base_url}/api/student-forms/stats/",
                "student_forms_types": f"{base_url}/api/student-forms/copy_types/",
                "top_courses": f"{base_url}/api/courses/top_courses/",
                "filters": f"{base_url}/api/courses/filters/",
                "auth": {
                    "login": f"{base_url}/auth/login/",
                    "register": f"{base_url}/auth/register/",
                    "refresh": f"{base_url}/auth/refresh/",
                    "logout": f"{base_url}/auth/logout/",
                    "me": f"{base_url}/auth/me/"
                },
                "admin": f"{base_url}/admin/"
            }
        })