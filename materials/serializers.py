# materials/serializers.py

from rest_framework import serializers
from .models import Subject, SubjectMaterial


class SubjectListSerializer(serializers.ModelSerializer):
    """Serializer for Subject list with materials in same response"""
    
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    department_name = serializers.CharField(source='course.department.name', read_only=True)
    academic_year_display = serializers.CharField(source='get_academic_year_display', read_only=True)
    semester_display = serializers.CharField(source='get_semester_display', read_only=True)
    
    # Material fields
    syllabus = serializers.SerializerMethodField()
    question_paper = serializers.SerializerMethodField()
    study_material = serializers.SerializerMethodField()
    assignment = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    
    materials_count = serializers.IntegerField(source='materials.count', read_only=True)
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'subject_code',
            'subject_name',
            'slug',
            'course',
            'course_name',
            'course_code',
            'department_name',
            'academic_year',
            'academic_year_display',
            'semester',
            'semester_display',
            'description',
            'syllabus',
            'question_paper',
            'study_material',
            'assignment',
            'assessment',
            'materials_count',
            'is_active',
            'created_at',
            'updated_at'
        ]
    
    def get_material_data(self, obj, material_type):
        """Helper method to get material data by type"""
        try:
            material = obj.materials.get(material_type=material_type, is_active=True)
            request = self.context.get('request')
            if material.file:
                return {
                    "material_type": material_type,
                    "material_type_display": material.get_material_type_display(),
                    "file": request.build_absolute_uri(material.file.url) if request else material.file.url
                }
        except SubjectMaterial.DoesNotExist:
            pass
        return None
    
    def get_syllabus(self, obj):
        return self.get_material_data(obj, 'syllabus')
    
    def get_question_paper(self, obj):
        return self.get_material_data(obj, 'question_paper')
    
    def get_study_material(self, obj):
        return self.get_material_data(obj, 'study_material')
    
    def get_assignment(self, obj):
        return self.get_material_data(obj, 'assignment')
    
    def get_assessment(self, obj):
        return self.get_material_data(obj, 'assessment')


class SubjectDetailSerializer(SubjectListSerializer):
    """Same as list serializer but can add extra fields if needed"""
    pass


class SubjectMaterialSerializer(serializers.ModelSerializer):
    """Serializer for Subject Material"""
    material_type_display = serializers.CharField(source='get_material_type_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SubjectMaterial
        fields = [
            'id',
            'subject',
            'material_type',
            'material_type_display',
            'file',
            'file_url',
            'is_active',
            'uploaded_at',
            'updated_at'
        ]
        read_only_fields = ['uploaded_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class SubjectMaterialCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Subject Material"""
    
    class Meta:
        model = SubjectMaterial
        fields = [
            'id',
            'subject',
            'material_type',
            'file',
            'is_active',
        ]
    
    def validate_file(self, value):
        """Validate file extension and size"""
        import os
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"Unsupported file type. Allowed: {', '.join(valid_extensions)}")
        
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        return value