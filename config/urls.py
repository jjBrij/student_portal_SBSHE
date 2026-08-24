# project/urls.py (main project)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from sbshe_student_portal.views import RootView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Main API - includes all endpoints
    path('api/', include('sbshe_student_portal.urls')),
    # Root view
    path('', RootView.as_view(), name='api-root'),
    path('api/materials/', include('materials.urls')),  
    path('api/', include('website_content.urls')),  # ADD THIS
    path('ckeditor5/', include('django_ckeditor_5.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)