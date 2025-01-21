from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageFile
from django.core.files.storage import default_storage
from datetime import datetime
import random
import string
from django.utils.timezone import now

ImageFile.LOAD_TRUNCATED_IMAGES = True  # Allow truncated images to be loaded


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


def set_customer_creator(worker):
    """Callback function to set the created_by field when a Worker is deleted."""
    # Assuming that the worker who created this customer is still available
    return worker.created_by  # Adjust this as needed based on your logic


class Customer(models.Model):
    name = models.CharField(max_length=150)
    next_of_kin = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    customer_image = models.ImageField(
        upload_to='media_file', default='default.jpg')
    created_by = models.ForeignKey(
        Worker,
        # Set the worker who created this when the worker is deleted
        on_delete=models.SET(set_customer_creator),
        null=True,
        blank=True,
        related_name='customers_created'
    )
    joined = models.DateTimeField(
        auto_now_add=True)  # Changed to DateTimeField
    account_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            img_path = self.customer_image.path  # Get the image path
            img = Image.open(img_path)

            # Ensure compatibility by converting RGBA to RGB
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Resize only if the image is larger than the desired size
            max_size = 800
            if img.height > max_size or img.width > max_size:
                img.thumbnail((max_size, max_size), Image.ANTIALIAS)

            # Save the resized image back to the same path
            img.save(img_path, format='JPEG', quality=90)
        except Exception as e:
            print(f"Error processing image: {e}")

    def generate_account_number(self):
        """Generates a unique account number for each customer."""
        while True:
            # Prefix with "ACC", current year, and a random alphanumeric string
            account_number = f"ACC-{now().strftime('%Y%m%d')}-" + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
            if not Customer.objects.filter(account_number=account_number).exists():
                return account_number


class Collection(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)  # Changed to DateTimeField

    def save(self, *args, **kwargs):
        # Automatically update customer's balance when saving
        self.customer.balance += self.amount
        self.customer.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Collection by {self.worker} for {self.customer} on {self.date}"
