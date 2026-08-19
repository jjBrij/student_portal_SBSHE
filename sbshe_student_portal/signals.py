# sbshe_student_portal/signals.py

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

@receiver(pre_delete, sender=User)
def delete_user_token(sender, instance, **kwargs):
    """
    Delete the user's token when the user is deleted
    """
    try:
        # Try to get and delete the token
        token = Token.objects.get(user=instance)
        token.delete()
        logger.info(f"Deleted token for user {instance.username}")
    except Token.DoesNotExist:
        # Token doesn't exist, that's fine
        logger.info(f"No token found for user {instance.username}")
    except Exception as e:
        logger.error(f"Error deleting token for user {instance.username}: {e}")