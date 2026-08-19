# sbshe_student_portal/apps.py

from django.apps import AppConfig


class SbsheStudentPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sbshe_student_portal'
    
    def ready(self):
        # Import signals
        import sbshe_student_portal.signals