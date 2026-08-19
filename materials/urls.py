# materials/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, SubjectMaterialViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'materials', SubjectMaterialViewSet, basename='material')

urlpatterns = [
    path('', include(router.urls)),
]