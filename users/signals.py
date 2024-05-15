from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging
from django.core.mail import send_mail
from django.conf import settings
# Set up the logger
logger = logging.getLogger(__name__)


# @receiver(post_save, sender=Profile)
def createProfile(sender, instance, created, **kwargs):

    if created:
        user = instance
        profile = Profile.objects.create(
            user=user, 
            username=user.username, 
            email=user.email, 
            name=user.first_name
        )
        # subject = 'Welcome to DevCollab'
        # message = 'Thank you for joining  DevCollab. We are glad you joined us.'
        # send_mail(
        #     subject,
        #     message,
        #     settings.EMAIL_HOST_USER,
        #     [profile.email],
        #     fail_silently=False
        # )

def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user
    if created == False:
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email
        user.save()


@receiver(post_delete, sender=Profile)
def deleteUser(sender, instance, **kwargs):
    # Check if the instance and its user attribute are not None
    if instance is None or instance.user is None:
        logger.error("Profile instance or its user attribute is None.")
        return

    # Log the user ID before attempting deletion
    logger.info(f"User ID before deletion attempt: {instance.user.id}")

    # Attempt to delete the user instance
    try:
        instance.user.delete()
        logger.info("User deleted successfully.")
    except Exception as e:
        logger.error(f"Received exception when deleting user: {e}")
        raise ValueError(f"Received exception when deleting user: {e}") from e


post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)
