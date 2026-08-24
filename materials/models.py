# materials/models.py

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import os

# ==================== VALIDATORS ====================

def validate_file_size(value):
    """Validate file size (max 10MB)"""
    filesize = value.size
    if filesize > 10 * 1024 * 1024:
        raise ValidationError("Maximum file size is 10MB")

def validate_file_extension(value):
    """Validate file extension"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file type. Allowed: {', '.join(valid_extensions)}")
    return value

# ==================== UPLOAD PATHS ====================

def subject_material_file_path(instance, filename):
    """Upload path for subject materials"""
    return f"materials/{instance.subject.course.department.slug}/{instance.subject.course.slug}/{instance.subject.slug}/{instance.material_type}/{filename}"

# ==================== MODELS ====================

class Subject(models.Model):
    """Subject model - belongs to Course"""
    
    ACADEMIC_YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]
    
    SEMESTER_CHOICES = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
    ]
    
    course = models.ForeignKey(
        'sbshe_student_portal.Course',
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    subject_code = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    academic_year = models.CharField(max_length=20, choices=ACADEMIC_YEAR_CHOICES)
    semester = models.CharField(max_length=20, blank=True, null=True, choices=SEMESTER_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['academic_year', 'semester', 'subject_code']
        unique_together = ['course', 'subject_code']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.course.slug}-{self.subject_code}-{self.subject_name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class SubjectMaterial(models.Model):
    """Subject Material model - Simple: Subject + Type + File only"""
    
    MATERIAL_TYPE_CHOICES = [
        ('syllabus', 'Syllabus'),
        ('study_material', 'Study Material'),
        ('question_paper', 'Question Paper'),
        ('assignment', 'Assignment'),
        ('assessment', 'Assessment'),
    ]
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    material_type = models.CharField(
        max_length=50,
        choices=MATERIAL_TYPE_CHOICES
    )
    file = models.FileField(
        upload_to=subject_material_file_path,
          max_length=500,
        validators=[validate_file_extension, validate_file_size]
    )
    
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        # Ensure only one file per type per subject
     

    def __str__(self):
        return f"{self.subject.subject_code} - {self.get_material_type_display()}"

    def delete(self, *args, **kwargs):
        """Delete file when material is deleted"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)