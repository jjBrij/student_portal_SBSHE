# student_form/serializers.py

from rest_framework import serializers
from .models import StudentForm
from sbshe_student_portal.models import Course


class StudentFormSerializer(serializers.ModelSerializer):
    """Serializer for reading student forms"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_details = serializers.SerializerMethodField()
    copy_type_display = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='course.department.name', read_only=True)
    
    class Meta:
        model = StudentForm
        fields = [
            'id',
            'name',
            'father_name',
            'email',
            'phone_number',
            'address',
            'pincode',
            'copy_type',
            'copy_type_display',
            'course',
            'course_name',
            'course_code',
            'department_name',
            'course_details',
            'is_active',
            'is_submitted',
            'submitted_at',
            'can_edit',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'is_submitted', 
            'submitted_at', 'can_edit', 'course_details',
            'department_name'
        ]
    
    def get_copy_type_display(self, obj):
        """Get human-readable copy type"""
        return dict(obj.COPY_TYPE_CHOICES).get(obj.copy_type, '')
    
    def get_can_edit(self, obj):
        """Check if form can be edited"""
        return not obj.is_submitted
    
    def get_course_details(self, obj):
        """Get detailed course information"""
        if obj.course:
            return {
                'id': obj.course.id,
                'name': obj.course.name,
                'course_code': obj.course.course_code,
                'slug': obj.course.slug,
                'department': obj.course.department.id if obj.course.department else None,
                'department_name': obj.course.department.name if obj.course.department else None,
                'duration': obj.course.duration,
                'course_type': obj.course.course_type,
                'course_type_display': obj.course.get_course_type_display(),
                'is_active': obj.course.is_active
            }
        return None


class StudentFormCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating student forms - User accessible"""
    course_name = serializers.CharField(write_only=True, required=True)
    course_id = serializers.IntegerField(read_only=True)
    department_name = serializers.CharField(source='course.department.name', read_only=True)
    
    class Meta:
        model = StudentForm
        fields = [
            'id',
            'name',
            'father_name',
            'email',
            'phone_number',
            'address',
            'pincode',
            'copy_type',
            'course_name',  # User provides this
            'course_id',    # Auto-populated
            'department_name',  # Read-only
            'is_active',
            'is_submitted',
            'submitted_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'is_submitted', 
            'submitted_at', 'course_id', 'department_name'
        ]
    
    def validate_course_name(self, value):
        """Validate and fetch course by name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Course name is required")
        
        try:
            # Try to find course by name (case-insensitive)
            course = Course.objects.filter(
                name__iexact=value.strip(),
                is_active=True
            ).first()
            
            if not course:
                # Try to find by course code
                course = Course.objects.filter(
                    course_code__iexact=value.strip(),
                    is_active=True
                ).first()
            
            if not course:
                # Try partial match
                course = Course.objects.filter(
                    name__icontains=value.strip(),
                    is_active=True
                ).first()
            
            if not course:
                raise serializers.ValidationError(
                    f"Course '{value}' not found. Please enter a valid course name or code."
                )
            
            # Store the course in the context for later use
            self.context['course'] = course
            return value
            
        except Exception as e:
            raise serializers.ValidationError(f"Error validating course: {str(e)}")
    
    def validate_phone_number(self, value):
        """Validate phone number"""
        import re
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError(
                "Phone number must be 10-15 digits. Optional + and country code allowed."
            )
        return value
    
    def validate_pincode(self, value):
        """Validate pincode"""
        if value:
            import re
            if not re.match(r'^\d{5,10}$', value):
                raise serializers.ValidationError("Pincode must be 5-10 digits")
        return value
    
    def validate_email(self, value):
        """Validate email is unique"""
        if StudentForm.objects.filter(email=value).exists():
            raise serializers.ValidationError("A student with this email already exists")
        return value
    
    def create(self, validated_data):
        """Create student form with auto-populated course"""
        # Get course from context
        course = self.context.get('course')
        if not course:
            raise serializers.ValidationError({"course_name": "Course not found"})
        
        # Remove course_name from validated_data (not a model field)
        validated_data.pop('course_name', None)
        
        # Set the course
        validated_data['course'] = course
        
        # Create the form
        return StudentForm.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update student form - Only if not submitted"""
        if instance.is_submitted:
            raise serializers.ValidationError(
                "This form has already been submitted and cannot be edited."
            )
        
        # Handle course update if provided
        course_name = validated_data.pop('course_name', None)
        if course_name:
            course = self.context.get('course')
            if course:
                validated_data['course'] = course
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StudentFormSubmitSerializer(serializers.ModelSerializer):
    """Serializer for submitting the form - Marks as submitted"""
    
    class Meta:
        model = StudentForm
        fields = ['id', 'is_submitted', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']
    
    def update(self, instance, validated_data):
        """Submit the form - Cannot be undone"""
        if instance.is_submitted:
            raise serializers.ValidationError("This form has already been submitted.")
        
        instance.is_submitted = True
        from django.utils import timezone
        instance.submitted_at = timezone.now()
        instance.save()
        return instance