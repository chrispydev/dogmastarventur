import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from savings.models import Customer


@receiver(post_delete, sender=Customer)
def delete_customer_image(sender, instance, **kwargs):
    """Deletes the image associated with the Customer instance when it is deleted"""
    if instance.customer_image:
        if os.path.isfile(instance.customer_image.path):
            os.remove(instance.customer_image.path)
