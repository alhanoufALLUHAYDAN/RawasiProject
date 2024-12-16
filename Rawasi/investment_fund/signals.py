from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Wallet  

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:  
        Wallet.objects.create(user=instance)
        print(f"Wallet created for user: {instance.username}")
