# sbshe_student_portal/serializers.py

from rest_framework import serializers
from .models import Department, Branch, Course


class DepartmentSerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source='courses.count', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'slug', 'description', 'introduction', 
            'file', 'file_url', 'file_type', 'file_name',
            'is_active', 'course_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None
    
    def get_file_type(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return 'image'
            elif ext == 'pdf':
                return 'pdf'
        return None
    
    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None


class BranchSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'slug', 'description', 'location', 
            'file', 'file_url', 'file_type', 'file_name',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None
    
    def get_file_type(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return 'image'
            elif ext == 'pdf':
                return 'pdf'
        return None
    
    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None


class CourseListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_file = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'name', 'slug', 'department', 'department_name',
            'department_file', 'introduction', 'file', 'file_url', 'file_type',
            'duration', 'course_type', 'course_type_display', 
            'is_top_course', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None
    
    def get_file_type(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return 'image'
            elif ext == 'pdf':
                return 'pdf'
        return None
    
    def get_department_file(self, obj):
        if obj.department and obj.department.file:
            return {
                'url': obj.department.file.url,
                'type': 'image' if obj.department.file.name.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'] else 'pdf',
                'name': obj.department.file.name.split('/')[-1]
            }
        return None


class CourseDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'course_code', 'slug', 'department', 'introduction', 
            'full_description', 'file', 'file_url', 'file_type', 'duration',
            'eligibility', 'course_type', 'course_type_display',
            'is_top_course', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None
    
    def get_file_type(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return 'image'
            elif ext == 'pdf':
                return 'pdf'
        return None