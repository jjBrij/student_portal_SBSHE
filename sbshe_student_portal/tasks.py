# sbshe_student_portal/tasks.py

from celery import shared_task
import os
import logging
from datetime import datetime, timedelta
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@shared_task
def log_admin_action_task(user_id, action, model, object_id):
    """Log admin actions asynchronously"""
    try:
        user = User.objects.get(id=user_id) if user_id else None
        username = user.username if user else 'Anonymous'
        logger.info(f"User {username} performed {action} on {model} {object_id} at {datetime.now()}")
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")

@shared_task
def log_user_login_task(user_id, ip_address):
    """Log user login asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"User {user.username} logged in from {ip_address} at {datetime.now()}")
    except Exception as e:
        logger.error(f"Failed to log user login: {e}")

@shared_task
def refresh_cache_task():
    """Refresh cache periodically"""
    try:
        from django.core.cache import cache
        from .models import Department, Branch, Course
        
        # Refresh departments cache
        departments = list(Department.objects.filter(is_active=True).values('id', 'name', 'slug'))
        cache.set('departments_queryset', departments, 60 * 30)
        
        # Refresh branches cache
        branches = list(Branch.objects.filter(is_active=True).values('id', 'name', 'slug'))
        cache.set('branches_queryset', branches, 60 * 30)
        
        # Refresh filters cache
        data = {
            'departments': departments,
            'branches': branches,
            'courses': list(Course.objects.filter(is_active=True).values('id', 'name', 'slug')),
            'course_types': [
                {'value': 'online', 'label': 'Online'},
                {'value': 'offline', 'label': 'Offline'},
                {'value': 'hybrid', 'label': 'Hybrid (Online + Offline)'},
            ]
        }
        cache.set('filters_data', data, 60 * 30)
        
        logger.info("Cache refreshed successfully")
    except Exception as e:
        logger.error(f"Failed to refresh cache: {e}")