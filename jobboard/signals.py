from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_company(sender, instance, created, **kwargs):
    if created:
        Company.objects.create(
            name=f"Default Company for {instance.username}",
            description="Automatically created default company.",
            created_by=instance
        )
