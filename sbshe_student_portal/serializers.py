# sbshe_student_portal/serializers.py - Add AssignmentCreateSerializer

from rest_framework import serializers
from .models import Department, Branch, Course, Assignment


class DepartmentSerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source='courses.count', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'slug', 'description', 'introduction', 
                 'image', 'image_url', 'is_active', 'course_count', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class BranchSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'slug', 'description', 'location', 
                 'image', 'image_url', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class AssignmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'instructions', 'file', 
                 'file_url', 'deadline', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'course', 'title', 'description', 'instructions', 
                 'file', 'deadline', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_course(self, value):
        """Validate that the course exists and is active"""
        if not Course.objects.filter(id=value.id, is_active=True).exists():
            raise serializers.ValidationError("Course does not exist or is not active")
        return value
    
    def create(self, validated_data):
        """Create assignment with proper course relationship"""
        try:
            course = validated_data.get('course')
            if not course:
                raise serializers.ValidationError({"course": "Course is required"})
            
            # Create the assignment
            assignment = Assignment.objects.create(**validated_data)
            return assignment
        except Exception as e:
            raise serializers.ValidationError(f"Error creating assignment: {str(e)}")


class CourseListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_image = serializers.SerializerMethodField()
    assignment_count = serializers.IntegerField(source='assignments.count', read_only=True)
    image_url = serializers.SerializerMethodField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'slug', 'department', 'department_name',
            'department_image', 'introduction', 'image', 'image_url', 
            'duration', 'course_type', 'course_type_display', 
            'is_top_course', 'is_active', 'assignment_count', 'created_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_department_image(self, obj):
        if obj.department and obj.department.image:
            return obj.department.image.url
        return None


class CourseDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'slug', 'department', 'introduction', 
            'full_description', 'image', 'image_url', 'duration',
            'eligibility', 'course_type', 'course_type_display',
            'is_top_course', 'is_active', 'assignments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id', 'department', 'name', 'introduction', 'full_description',
            'image', 'duration', 'eligibility', 'course_type',
            'is_top_course', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_department(self, value):
        if not Department.objects.filter(id=value.id, is_active=True).exists():
            raise serializers.ValidationError("Department does not exist or is not active")
        return value