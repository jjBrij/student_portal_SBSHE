# student_form/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.core.cache import cache
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import StudentForm
from .serializers import (
    StudentFormSerializer, 
    StudentFormCreateSerializer,
    StudentFormSubmitSerializer
)
from sbshe_student_portal.models import Course
from sbshe_student_portal.tasks import log_admin_action_task


class StudentFormViewSet(viewsets.ModelViewSet):
    """
    Student Form ViewSet
    - POST (create/submit): Public
    - GET (list/retrieve): Public (view submitted forms)
    - All other operations: Admin only
    """
    queryset = StudentForm.objects.select_related('course__department').all()
    search_fields = [
        'name', 'father_name', 'email', 'phone_number', 
        'address', 'course__name', 'course__course_code'
    ]
    ordering_fields = ['name', 'created_at', 'updated_at', 'email']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Set permissions based on action:
        - create, submit, list, retrieve, copy_types: Public access (AllowAny)
        - All other actions: Admin only (IsAdminUser)
        """
        if self.action in ['create', 'submit', 'list', 'retrieve', 'copy_types']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentFormCreateSerializer
        elif self.action == 'submit':
            return StudentFormSubmitSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentFormCreateSerializer
        return StudentFormSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by course (using course ID)
        course = self.request.query_params.get('course')
        if course and course.isdigit():
            queryset = queryset.filter(course_id=int(course))
        
        # Filter by course name
        course_name = self.request.query_params.get('course_name')
        if course_name:
            queryset = queryset.filter(course__name__icontains=course_name)
        
        # Filter by copy_type
        copy_type = self.request.query_params.get('copy_type')
        if copy_type:
            queryset = queryset.filter(copy_type=copy_type)
        
        # Filter by submission status
        is_submitted = self.request.query_params.get('is_submitted')
        if is_submitted is not None:
            if is_submitted.lower() == 'true':
                queryset = queryset.filter(is_submitted=True)
            elif is_submitted.lower() == 'false':
                queryset = queryset.filter(is_submitted=False)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'true':
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == 'false':
                queryset = queryset.filter(is_active=False)
        
        # Only show submitted forms to public (non-admin)
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_submitted=True)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List forms - Public (only submitted forms)"""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve single form - Public (only if submitted)"""
        instance = self.get_object()
        if not instance.is_submitted and not request.user.is_staff:
            return Response(
                {'error': 'This form has not been submitted yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create new form - Public
        Accepts course_name and auto-fetches course ID
        """
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit the form - Public endpoint
        """
        instance = self.get_object()
        
        if instance.is_submitted:
            return Response(
                {'error': 'This form has already been submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = StudentFormSubmitSerializer(
            instance, 
            data={'is_submitted': True},
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Form submitted successfully!',
                'data': StudentFormSerializer(instance).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def by_course(self, request):
        """Get student forms for a specific course - Admin only"""
        course_id = request.query_params.get('course_id')
        
        if not course_id:
            return Response(
                {'error': 'course_id parameter is required'},
                status=400
            )
        
        if not course_id.isdigit():
            return Response(
                {'error': 'course_id must be a number'},
                status=400
            )
        
        queryset = self.get_queryset().filter(course_id=int(course_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """Get statistics about student forms - Admin only"""
        total = StudentForm.objects.count()
        submitted = StudentForm.objects.filter(is_submitted=True).count()
        pending = StudentForm.objects.filter(is_submitted=False).count()
        active_count = StudentForm.objects.filter(is_active=True).count()
        inactive_count = StudentForm.objects.filter(is_active=False).count()
        
        by_copy_type = StudentForm.objects.values('copy_type').annotate(
            count=Count('id'),
            submitted=Count('id', filter=Q(is_submitted=True)),
            pending=Count('id', filter=Q(is_submitted=False))
        )
        
        by_course = StudentForm.objects.values('course__id', 'course__name', 'course__course_code').annotate(
            count=Count('id'),
            submitted=Count('id', filter=Q(is_submitted=True)),
            pending=Count('id', filter=Q(is_submitted=False))
        ).order_by('-count')[:10]
        
        copy_type_map = {
            '1': 'Soft Copy',
            '2': 'Hard Copy'
        }
        
        return Response({
            'total': total,
            'submitted': submitted,
            'pending': pending,
            'active': active_count,
            'inactive': inactive_count,
            'by_copy_type': [
                {
                    'type': item['copy_type'],
                    'label': copy_type_map.get(item['copy_type'], 'Unknown'),
                    'total': item['count'],
                    'submitted': item['submitted'],
                    'pending': item['pending']
                }
                for item in by_copy_type
            ],
            'top_courses': [
                {
                    'course_id': item['course__id'],
                    'course_name': item['course__name'],
                    'course_code': item['course__course_code'],
                    'total': item['count'],
                    'submitted': item['submitted'],
                    'pending': item['pending']
                }
                for item in by_course if item['course__id']
            ]
        })
    
    @action(detail=False, methods=['get'])
    def copy_types(self, request):
        """Get available copy types - Public"""
        types = [
            {'value': '1', 'label': 'Soft Copy'},
            {'value': '2', 'label': 'Hard Copy'},
        ]
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def course_list(self, request):
        """Get list of active courses for dropdown - Public"""
        courses = Course.objects.filter(is_active=True).select_related('department')
        data = [
            {
                'id': course.id,
                'name': course.name,
                'course_code': course.course_code,
                'department_name': course.department.name if course.department else None,
                'full_name': f"{course.name} ({course.course_code})"
            }
            for course in courses
        ]
        return Response(data)
    
    def perform_create(self, serializer):
        """Create new form - Users can create"""
        instance = serializer.save()
        cache.delete('student_forms_queryset')
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
        else:
            user_id = None
        log_admin_action_task.delay(
            user_id=user_id,
            action='create',
            model='StudentForm',
            object_id=instance.id
        )
    
    def perform_update(self, serializer):
        """Update form - Admin only"""
        instance = self.get_object()
        if instance.is_submitted:
            raise serializers.ValidationError(
                "This form has been submitted and cannot be modified."
            )
        instance = serializer.save()
        cache.delete('student_forms_queryset')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='update',
            model='StudentForm',
            object_id=instance.id
        )
    
    def perform_destroy(self, instance):
        """Delete form - Admin only"""
        cache.delete('student_forms_queryset')
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        log_admin_action_task.delay(
            user_id=user_id,
            action='delete',
            model='StudentForm',
            object_id=instance.id
        )
        instance.delete()