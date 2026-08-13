from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import os

# ==================== VALIDATORS ====================
def validate_image_size(value):
    """Validate image size (max 5MB)"""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("Maximum image size is 5MB")

def validate_file_size(value):
    """Validate file size (max 10MB)"""
    filesize = value.size
    if filesize > 10 * 1024 * 1024:
        raise ValidationError("Maximum file size is 10MB")

# ==================== IMAGE UPLOAD PATHS ====================
def department_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"department_{instance.id}_{filename}"
    return f"departments/{instance.slug}/{filename}"

def branch_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"branch_{instance.id}_{filename}"
    return f"branches/{instance.slug}/{filename}"

def course_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"course_{instance.id}_{filename}"
    return f"courses/{instance.department.slug}/{filename}"

def assignment_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.course.id}_{instance.id}_{filename}"
    return f"assignments/course_{instance.course.id}/{filename}"

# ==================== MODELS ====================

class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    introduction = models.TextField(help_text="Brief introduction about the department")
    image = models.ImageField(
        upload_to=department_image_path,
        validators=[validate_image_size],
        blank=True,
        null=True,
        help_text="Department image/photo (max 5MB)"
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
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to=branch_image_path,
        validators=[validate_image_size],
        blank=True,
        null=True,
        help_text="Branch image/photo (max 5MB)"
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
    introduction = models.TextField(help_text="Rich text supported")
    full_description = models.TextField(help_text="Detailed course description")
    
    image = models.ImageField(
        upload_to=course_image_path,
        validators=[validate_image_size],
        blank=True,
        null=True,
        help_text="Course image/thumbnail (max 5MB)"
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


class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField(help_text="Detailed instructions for the assignment")
    file = models.FileField(
        upload_to=assignment_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt']),
            validate_file_size
        ],
        blank=True,
        null=True,
        help_text="Optional PDF or document file"
    )
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-deadline']
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['deadline']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)