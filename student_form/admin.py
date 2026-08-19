# student_form/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import StudentForm


@admin.register(StudentForm)
class StudentFormAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name', 
        'father_name', 
        'email', 
        'phone_number',
        'course_link',
        'copy_type_display_admin',
        'submission_status',
        'is_active', 
        'submitted_at',
        'created_at'
    ]
    list_filter = ['copy_type', 'is_active', 'is_submitted', 'course', 'created_at']
    search_fields = ['name', 'father_name', 'email', 'phone_number', 'address', 'course__name', 'course__course_code']
    autocomplete_fields = ['course']
    ordering = ['-created_at']
    readonly_fields = [
        'created_at', 'updated_at', 'is_submitted', 'submitted_at'
    ]
    list_per_page = 25
    list_max_show_all = 100
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'father_name', 'email', 'phone_number')
        }),
        ('Address Details', {
            'fields': ('address', 'pincode')
        }),
        ('Course & Copy Type', {
            'fields': ('course', 'copy_type')
        }),
        ('Submission Status', {
            'fields': ('is_submitted', 'submitted_at'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def course_link(self, obj):
        """Display course with link to course admin"""
        if obj.course:
            url = f"/admin/sbshe_student_portal/course/{obj.course.id}/change/"
            return format_html(
                '<a href="{}" target="_blank">{} ({})</a>',
                url,
                obj.course.name,
                obj.course.course_code
            )
        return "-"
    course_link.short_description = 'Course'
    course_link.admin_order_field = 'course__name'
    
    def copy_type_display_admin(self, obj):
        """Display copy type with color coding"""
        colors = {
            '1': '#2196F3',
            '2': '#4CAF50'
        }
        labels = {
            '1': '📄 Soft Copy',
            '2': '📘 Hard Copy'
        }
        color = colors.get(obj.copy_type, '#9E9E9E')
        label = labels.get(obj.copy_type, 'Unknown')
        return format_html(
            '<span style="color:{}; font-weight:bold; background:#f5f5f5; padding:2px 8px; border-radius:4px;">{}</span>',
            color, label
        )
    copy_type_display_admin.short_description = 'Copy Type'
    
    def submission_status(self, obj):
        """Display submission status with color coding"""
        if obj.is_submitted:
            return format_html(
                '<span style="color:#4CAF50; font-weight:bold; background:#E8F5E9; padding:3px 10px; border-radius:12px;">✅ Submitted</span>'
            )
        return format_html(
            '<span style="color:#FF9800; font-weight:bold; background:#FFF3E0; padding:3px 10px; border-radius:12px;">⏳ Pending</span>'
        )
    submission_status.short_description = 'Status'
    submission_status.admin_order_field = 'is_submitted'
    
    actions = ['mark_as_submitted', 'mark_as_pending', 'activate_forms', 'deactivate_forms']
    
    def mark_as_submitted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_submitted=True, submitted_at=timezone.now())
        self.message_user(request, f'{updated} forms marked as submitted.', messages.SUCCESS)
    mark_as_submitted.short_description = "✅ Mark as Submitted"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(is_submitted=False, submitted_at=None)
        self.message_user(request, f'{updated} forms marked as pending.', messages.WARNING)
    mark_as_pending.short_description = "⏳ Mark as Pending"
    
    def activate_forms(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} forms activated.', messages.SUCCESS)
    activate_forms.short_description = "🟢 Activate selected forms"
    
    def deactivate_forms(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} forms deactivated.', messages.WARNING)
    deactivate_forms.short_description = "🔴 Deactivate selected forms"