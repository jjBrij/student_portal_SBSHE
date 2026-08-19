# materials/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Subject, SubjectMaterial


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = [
        'subject_code',
        'subject_name',
        'course',
        'academic_year',
        'semester',
        'materials_count',
        'is_active',
        'created_at'
    ]
    list_filter = ['course', 'course__department', 'academic_year', 'semester', 'is_active']
    search_fields = ['subject_code', 'subject_name', 'description', 'course__name']
    autocomplete_fields = ['course']
    prepopulated_fields = {'slug': ('subject_code', 'subject_name')}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'subject_code', 'subject_name', 'slug')
        }),
        ('Academic Details', {
            'fields': ('academic_year', 'semester')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def materials_count(self, obj):
        count = obj.materials.filter(is_active=True).count()
        color = 'green' if count > 0 else 'gray'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, count)
    materials_count.short_description = 'Active Materials'


@admin.register(SubjectMaterial)
class SubjectMaterialAdmin(admin.ModelAdmin):
    list_display = [
        'subject',
        'material_type',
        'file_preview',
        'is_active',
        'uploaded_at'
    ]
    list_filter = ['material_type', 'subject', 'subject__course', 'is_active']
    search_fields = ['subject__subject_code', 'subject__subject_name']
    autocomplete_fields = ['subject']
    readonly_fields = ['uploaded_at', 'updated_at']
    
    fieldsets = (
        ('Material Information', {
            'fields': ('subject', 'material_type')
        }),
        ('File', {
            'fields': ('file',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_preview(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return format_html(
                    '<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:5px;" />',
                    obj.file.url
                )
            elif ext in ['pdf', 'doc', 'docx', 'ppt', 'pptx']:
                return format_html(
                    '<a href="{}" target="_blank">📄 {}</a>',
                    obj.file.url,
                    ext.upper()
                )
        return format_html('<span style="color:gray;">No File</span>')
    file_preview.short_description = 'File Preview'