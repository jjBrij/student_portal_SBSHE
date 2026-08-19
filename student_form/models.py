# student_form/models.py

from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from sbshe_student_portal.models import Course


class StudentForm(models.Model):
    """Student Form Model - Users submit, Admins view only"""
    
    # Copy Type Choices
    COPY_TYPE_CHOICES = [
        ('1', 'Soft Copy'),
        ('2', 'Hard Copy'),
    ]
    
    # Personal Information
    name = models.CharField(
        max_length=255,
        help_text="Student's full name"
    )
    father_name = models.CharField(
        max_length=255,
        help_text="Father's full name"
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Student's email address"
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be 10-15 digits"
            )
        ],
        help_text="Phone number (10-15 digits)"
    )
    address = models.TextField(
        help_text="Complete address"
    )
    pincode = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{5,10}$',
                message="Pincode must be 5-10 digits"
            )
        ],
        blank=True,
        null=True,
        help_text="Pincode (5-10 digits) - Optional"
    )
    
    # Copy Type
    copy_type = models.CharField(
        max_length=1,
        choices=COPY_TYPE_CHOICES,
        default='1',
        help_text="Select copy type"
    )
    
    # Course Reference - Only this, no separate course_code_display
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='student_forms',
        help_text="Select course"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_submitted = models.BooleanField(
        default=False,
        help_text="True when form is submitted"
    )
    submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the form was submitted"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student Form'
        verbose_name_plural = 'Student Forms'
        indexes = [
            models.Index(fields=['email'], name='student_form_email_idx'),
            models.Index(fields=['phone_number'], name='student_form_phone_idx'),
            models.Index(fields=['course'], name='student_form_course_idx'),
            models.Index(fields=['is_active'], name='student_form_active_idx'),
            models.Index(fields=['is_submitted'], name='student_form_submitted_idx'),
        ]

    def __str__(self):
        return f"{self.name} - {self.course.name} ({self.course.course_code})"

    def get_copy_type_display(self):
        """Get human-readable copy type"""
        return dict(self.COPY_TYPE_CHOICES).get(self.copy_type, '')
    
    def can_edit(self):
        """Check if the form can be edited"""
        return not self.is_submitted