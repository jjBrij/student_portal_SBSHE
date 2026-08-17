# sbshe_student_portal/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Department, Branch, Course, CourseMaterial


# Custom User Admin with token cleanup
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'has_token']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ()}),
    )
    actions = ['activate_users', 'deactivate_users', 'delete_users_with_tokens']
    
    def has_token(self, obj):
        try:
            Token.objects.get(user=obj)
            return True
        except ObjectDoesNotExist:
            return False
        except Exception:
            return False
    has_token.short_description = 'Has Token'
    has_token.boolean = True
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def delete_users_with_tokens(self, request, queryset):
        deleted_count = 0
        error_count = 0
        
        for user in queryset:
            try:
                try:
                    token = Token.objects.get(user=user)
                    token.delete()
                except ObjectDoesNotExist:
                    pass
                except Exception:
                    pass
                
                user.delete()
                deleted_count += 1
            except IntegrityError as e:
                error_count += 1
                self.message_user(
                    request, 
                    f'Error deleting user {user.username}: {str(e)}', 
                    level=messages.ERROR
                )
            except Exception as e:
                error_count += 1
                self.message_user(
                    request, 
                    f'Error deleting user {user.username}: {str(e)}', 
                    level=messages.ERROR
                )
        
        if deleted_count > 0:
            self.message_user(
                request, 
                f'Successfully deleted {deleted_count} users and their tokens.'
            )
        if error_count > 0:
            self.message_user(
                request, 
                f'Failed to delete {error_count} users.',
                level=messages.WARNING
            )
    delete_users_with_tokens.short_description = "Delete selected users (with tokens)"

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                try:
                    token = Token.objects.get(user=obj)
                    token.delete()
                except ObjectDoesNotExist:
                    pass
                except Exception:
                    pass
                
                obj.delete()
            except IntegrityError:
                self.message_user(
                    request, 
                    f'Error deleting user {obj.username}. Token cleanup failed.',
                    level=messages.ERROR
                )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'file_preview', 'is_active', 'course_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'introduction']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'file')
        }),
        ('Description', {
            'fields': ('description', 'introduction')
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
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return format_html(
                    '<img src="{}" width="60" height="60" style="object-fit:cover; border-radius:5px;" />', 
                    obj.file.url
                )
            elif ext == 'pdf':
                return format_html(
                    '<a href="{}" target="_blank">📄 PDF</a>', 
                    obj.file.url
                )
        return format_html('<span style="color:gray;">No File</span>')
    file_preview.short_description = 'Preview'
    
    def course_count(self, obj):
        count = obj.courses.filter(is_active=True).count()
        color = 'green' if count > 0 else 'gray'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, count)
    course_count.short_description = 'Active Courses'
    course_count.admin_order_field = 'courses__count'  # Allow ordering


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'location', 'file_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'location', 'created_at']
    search_fields = ['name', 'description', 'location']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'file')
        }),
        ('Description', {
            'fields': ('description', 'location')
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
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return format_html(
                    '<img src="{}" width="60" height="60" style="object-fit:cover; border-radius:50%;" />', 
                    obj.file.url
                )
            elif ext == 'pdf':
                return format_html(
                    '<a href="{}" target="_blank">📄 PDF</a>', 
                    obj.file.url
                )
        return format_html('<span style="color:gray;">No File</span>')
    file_preview.short_description = 'Preview'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'course_code', 'department', 'course_type', 'duration',
        'file_preview', 'is_top_course', 'is_active', 
        'get_material_count', 'created_at'  # Changed from material_count to get_material_count
    ]
    list_filter = ['department', 'course_type', 'is_active', 'is_top_course', 'created_at']
    search_fields = ['name', 'introduction', 'full_description', 'department__name']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['department']
    ordering = ['-is_top_course', 'department', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'name', 'slug', 'course_code', 'file')
        }),
        ('Description', {
            'fields': ('introduction', 'full_description')
        }),
        ('Course Details', {
            'fields': ('duration', 'eligibility', 'course_type')
        }),
        ('Status', {
            'fields': ('is_active', 'is_top_course')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_preview(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return format_html(
                    '<img src="{}" width="60" height="60" style="object-fit:cover; border-radius:5px;" />', 
                    obj.file.url
                )
            elif ext == 'pdf':
                return format_html(
                    '<a href="{}" target="_blank">📄 PDF</a>', 
                    obj.file.url
                )
        return format_html('<span style="color:gray;">No File</span>')
    file_preview.short_description = 'Preview'
    
    def get_material_count(self, obj):
        """Get count of active materials for this course"""
        count = obj.materials.filter(is_active=True).count()
        color = 'green' if count > 0 else 'gray'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, count)
    get_material_count.short_description = 'Active Materials'
    get_material_count.admin_order_field = 'materials__count'
    
    actions = ['mark_as_top_course', 'unmark_as_top_course']
    
    def mark_as_top_course(self, request, queryset):
        updated = queryset.update(is_top_course=True)
        self.message_user(request, f'{updated} courses marked as top courses.')
    mark_as_top_course.short_description = "Mark selected courses as Top"
    
    def unmark_as_top_course(self, request, queryset):
        updated = queryset.update(is_top_course=False)
        self.message_user(request, f'{updated} courses unmarked as top courses.')
    unmark_as_top_course.short_description = "Unmark selected courses as Top"


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'material_type', 'course', 'course_code', 'subject_code',
        'academic_year', 'file_preview', 'deadline', 'is_active', 'created_at'
    ]
    list_filter = [
        'material_type', 'course', 'academic_year', 'is_active', 
        'deadline', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'instructions', 'course__name', 
        'course_code', 'subject_code'
    ]
    autocomplete_fields = ['course']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'course_code']
    
    fieldsets = (
        ('Type & Course', {
            'fields': ('course', 'course_code', 'material_type')
        }),
        ('Subject Details', {
            'fields': ('subject_code', 'academic_year', 'semester')
        }),
        ('Content', {
            'fields': ('title', 'description', 'instructions')
        }),
        ('File & Deadline', {
            'fields': ('file', 'deadline')
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
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return format_html(
                    '<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:5px;" />', 
                    obj.file.url
                )
            elif ext == 'pdf':
                return format_html(
                    '<a href="{}" target="_blank">📄 PDF</a>', 
                    obj.file.url
                )
        return format_html('<span style="color:gray;">No File</span>')
    file_preview.short_description = 'File'
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions