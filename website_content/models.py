# website_content/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
import os

def validate_file_size(value):
    """Validate file size (max 10MB)"""
    filesize = value.size
    if filesize > 10 * 1024 * 1024:
        raise ValidationError("Maximum file size is 10MB")

def get_upload_path(instance, filename):
    """Upload path for website content files"""
    menu_name = instance.menu.name.lower().replace(' ', '-') if instance.menu else 'general'
    content_name = instance.name.lower().replace(' ', '-')[:50]
    return f"website_content/{menu_name}/{content_name}/{filename}"

class Menu(models.Model):
    """Menu model for website navigation"""
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
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

    def __str__(self):
        return self.name

class WebsiteContent(models.Model):
    """Website Content model"""
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.PositiveIntegerField(blank=True, null=True)
    file = models.FileField(
        upload_to=get_upload_path,
        validators=[validate_file_size],
        blank=True,
        null=True
    )
    
    short_intro = models.TextField(blank=True, null=True)
    intro = models.TextField(blank=True, null=True)
    description = CKEditor5Field(blank=True, null=True, config_name='extends')
    
    date = models.DateField(blank=True, null=True)
    url_link = models.URLField(max_length=500, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['menu']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.menu.name} - {self.name}"