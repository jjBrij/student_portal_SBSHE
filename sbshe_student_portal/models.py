# sbshe_student_portal/models.py

from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import os

# ==================== VALIDATORS ====================
def validate_image_or_pdf_size(value):
    """Validate file size (max 10MB)"""
    filesize = value.size
    if filesize > 10 * 1024 * 1024:
        raise ValidationError("Maximum file size is 10MB")

def validate_image_or_pdf(value):
    """Validate that file is an image or PDF"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.pdf']
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file type. Allowed: {', '.join(valid_extensions)}")
    return value

# ==================== UPLOAD PATHS ====================
def department_file_path(instance, filename):
    """Upload path for department files"""
    ext = filename.split('.')[-1]
    filename = f"department_{instance.id}_{filename}"
    return f"departments/{instance.slug}/{filename}"

def branch_file_path(instance, filename):
    """Upload path for branch files"""
    ext = filename.split('.')[-1]
    filename = f"branch_{instance.id}_{filename}"
    return f"branches/{instance.slug}/{filename}"

def course_file_path(instance, filename):
    """Upload path for course files"""
    ext = filename.split('.')[-1]
    filename = f"course_{instance.id}_{filename}"
    return f"courses/{instance.department.slug}/{filename}"

# ==================== MODELS ====================

class Department(models.Model):
    """Department model with image/PDF support"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description =CKEditor5Field(blank=True, null=True, config_name='extends',help_text="Rich text supported")
    introduction = models.TextField(blank=True, null=True, help_text="Brief introduction about the department")
    serial_number = models.PositiveIntegerField(blank=True, null=True)

    file = models.FileField(
        upload_to=department_file_path,
        validators=[validate_image_or_pdf, validate_image_or_pdf_size],
        blank=True,
        null=True,
        help_text="Department image/photo or PDF (max 10MB)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Branch(models.Model):
    """Branch model with image/PDF support"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255,blank=True, null=True)
  

    file = models.FileField(
        upload_to=branch_file_path,
        validators=[validate_image_or_pdf, validate_image_or_pdf_size],
        blank=True,
        null=True,
        help_text="Branch image/photo or PDF (max 10MB)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['location']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    """Course model with image/PDF support"""
    COURSE_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid (Online + Offline)'),
    ]
    
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE,
        related_name='courses'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    introduction = models.TextField(help_text="Rich text supported",blank=True, null=True)
    full_description = CKEditor5Field(blank=True, null=True, config_name='extends', help_text="Detailed course description")
    serial_number = models.PositiveIntegerField(blank=True, null=True)
    course_code = models.CharField(
        max_length=100, 
        unique=True, 
        null=True,
        blank=True,
        help_text="Course code (e.g., CS101)"
    )
    
    file = models.FileField(
        upload_to=course_file_path,
        validators=[validate_image_or_pdf, validate_image_or_pdf_size],
        blank=True,
        null=True,
        help_text="Course image/thumbnail or PDF (max 10MB)"
    )
    
    duration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g., 3 Years, 6 Months, 120 Hours"
    )
    eligibility = models.TextField(
        blank=True,
        null=True,
        help_text="Eligibility criteria for the course"
    )
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        default='offline',
        help_text="Course delivery mode"
    )
     
    soft_copy_amount=models.DecimalField(
           max_digits=10,
           decimal_places=2,
           null=True,
           blank=True,
           help_text="Amount for soft copy in INR"
    )
    hard_copy_amount=models.DecimalField(
           max_digits=10,
           decimal_places=2,
           null=True,
           blank=True,
           help_text="Amount for hard copy in INR"
    )
    courier_charge=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Courier charge in INR"
    )
    is_top_course = models.BooleanField(
        default=False,
        help_text="Mark as top/popular course"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['department', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_top_course']),
            models.Index(fields=['course_type']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.department.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.department.name} - {self.name}"