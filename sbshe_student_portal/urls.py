# sbshe_student_portal/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, BranchViewSet, CourseViewSet, 
    CourseMaterialViewSet, RootView
)
from .authentication import (
    jwt_login, jwt_refresh, jwt_logout, 
    jwt_register, jwt_user_info, admin_create_user
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'materials', CourseMaterialViewSet, basename='material')

# API URL Patterns
urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # JWT Authentication endpoints
    path('auth/login/', jwt_login, name='jwt_login'),
    path('auth/refresh/', jwt_refresh, name='jwt_refresh'),
    path('auth/logout/', jwt_logout, name='jwt_logout'),
    path('auth/register/', jwt_register, name='jwt_register'),
    path('auth/me/', jwt_user_info, name='jwt_user_info'),
    path('auth/admin/create-user/', admin_create_user, name='admin_create_user'),
]