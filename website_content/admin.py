# website_content/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Menu, WebsiteContent

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

@admin.register(WebsiteContent)
class WebsiteContentAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'menu',
        'short_name',
        'serial_number',
        'file_preview',
        'is_active',
        'date',
        'created_at'
    ]
    list_filter = ['menu', 'is_active', 'date']
    search_fields = ['name', 'short_name', 'intro', 'serial_number', 'description']
    autocomplete_fields = ['menu']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Required Information', {
            'fields': ('menu', 'name')
        }),
        ('Additional Information', {
            'fields': ('short_name', 'serial_number')
        }),
        ('File', {
            'fields': ('file',)
        }),
        ('Content', {
            'fields': ('short_intro', 'intro', 'description')
        }),
        ('Meta', {
            'fields': ('date', 'url_link')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_preview(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                return format_html(
                    '<img src="{}" width="60" height="60" style="object-fit:cover; border-radius:5px;" />',
                    obj.file.url
                )
            elif ext in ['pdf', 'doc', 'docx', 'ppt', 'pptx']:
                return format_html(
                    '<a href="{}" target="_blank">📄 {}</a>',
                    obj.file.url,
                    ext.upper()
                )
        return format_html('<span style="color:gray;">No File</span>')
    file_preview.short_description = 'Preview'