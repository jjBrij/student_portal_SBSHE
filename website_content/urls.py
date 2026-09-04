# website_content/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebsiteContentViewSet,MenuViewSet

router = DefaultRouter()
router.register(r'website-content', WebsiteContentViewSet, basename='website-content')
router.register(r'website-menu', MenuViewSet, basename='menus')

urlpatterns = [
    path('', include(router.urls)),
]