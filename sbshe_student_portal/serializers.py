# sbshe_student_portal/serializers.py

from rest_framework import serializers
from .models import Department, Branch, Course, CourseMaterial


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


# ============ COURSE MATERIAL SERIALIZERS ============

class CourseMaterialSerializer(serializers.ModelSerializer):
    """Serializer for reading course materials"""
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code_display = serializers.CharField(source='course_code', read_only=True)
    material_type_display = serializers.CharField(source='get_material_type_display', read_only=True)
    academic_year_display = serializers.SerializerMethodField()
    deadline_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseMaterial
        fields = [
            'id',
            'course',
            'course_name',
            'course_code',
            'course_code_display',
            'material_type',
            'material_type_display',
            'subject_code',
            'academic_year',
            'academic_year_display',
            'title',
            'description',
            'instructions',
            'file',
            'file_url',
            'file_type',
            'deadline',
            'deadline_display',
            'semester',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'course_code']
    
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
    
    def get_academic_year_display(self, obj):
        year_map = {
            '1': 'First Year',
            '2': 'Second Year',
            '3': 'Third Year',
            '4': 'Fourth Year'
        }
        return year_map.get(obj.academic_year, obj.academic_year)
    
    def get_deadline_display(self, obj):
        if obj.deadline:
            return obj.deadline.strftime('%Y-%m-%d')
        return None


class CourseMaterialCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating course materials"""
    
    class Meta:
        model = CourseMaterial
        fields = [
            'id',
            'course',
            'material_type',
            'subject_code',
            'academic_year',
            'title',
            'description',
            'instructions',
            'file',
            'deadline',
            'semester',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_course(self, value):
        if not Course.objects.filter(id=value.id, is_active=True).exists():
            raise serializers.ValidationError("Course does not exist or is not active")
        return value
    
    def validate_file(self, value):
        ext = value.name.split('.')[-1].lower()
        allowed = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        if ext not in allowed:
            raise serializers.ValidationError(f"Unsupported file type. Allowed: {', '.join(allowed)}")
        return value
    
    def validate_academic_year(self, value):
        valid_years = ['1', '2', '3', '4']
        if value and value not in valid_years:
            raise serializers.ValidationError(f"Invalid academic year. Choices: {', '.join(valid_years)}")
        return value
    
    def create(self, validated_data):
        try:
            course = validated_data.get('course')
            if not course:
                raise serializers.ValidationError({"course": "Course is required"})
            
            validated_data['course_code'] = course.course_code
            material = CourseMaterial.objects.create(**validated_data)
            return material
        except Exception as e:
            raise serializers.ValidationError(f"Error creating material: {str(e)}")
    
    def update(self, instance, validated_data):
        if 'course' in validated_data:
            course = validated_data['course']
            validated_data['course_code'] = course.course_code
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ============ COURSE SERIALIZERS ============

class CourseListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_file = serializers.SerializerMethodField()
    material_count = serializers.IntegerField(source='materials.count', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'name', 'slug', 'department', 'department_name',
            'department_file', 'introduction', 'file', 'file_url', 'file_type',
            'duration', 'course_type', 'course_type_display', 
            'is_top_course', 'is_active', 'material_count', 'created_at'
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
    materials = CourseMaterialSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'name', 'course_code', 'slug', 'department', 'introduction', 
            'full_description', 'file', 'file_url', 'file_type', 'duration',
            'eligibility', 'course_type', 'course_type_display',
            'is_top_course', 'is_active', 'materials',
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