# website_content/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebsiteContentViewSet

router = DefaultRouter()
router.register(r'website-content', WebsiteContentViewSet, basename='website-content')

urlpatterns = [
    path('', include(router.urls)),
]