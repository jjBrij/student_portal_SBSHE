# student_form/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentFormViewSet

# Use empty string - the parent URL will handle the prefix
router = DefaultRouter()
router.register(r'', StudentFormViewSet, basename='student-form')

urlpatterns = [
    path('', include(router.urls)),
]