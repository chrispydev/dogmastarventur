from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageFile
from django.core.files.storage import default_storage
from datetime import datetime
import random
import string
import os

ImageFile.LOAD_TRUNCATED_IMAGES = True  # Allow truncated images to be loaded


class Customer(models.Model):
    name = models.CharField(max_length=150, default='name')
    next_of_kin = models.CharField(max_length=100, default='next_of_kin')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    customer_image = models.ImageField(
        upload_to='media_file', default='default.jpg')
    joined = models.DateTimeField(auto_now_add=True)
    account_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True)  # Field for account number

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
        """Generates a unique account number for each customer"""
        # Create a random account number (e.g., ACC-XXXX, where XXXX is a 4-digit number)
        account_number = 'ACC-' + ''.join(random.choices(string.digits, k=4))
        return account_number


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Collection(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)  # Changed to DateTimeField
    # Store geographic coordinates (lat, long)
    google_maps_url = models.URLField(
        max_length=200, blank=True, null=True)  # Google Maps URL link

    def save(self, *args, **kwargs):
        # Automatically update customer's balance when saving
        self.customer.balance += self.amount
        self.customer.save()

        # Generate Google Maps URL if latitude and longitude are provided
        if self.latitude is not None and self.longitude is not None:
            self.google_maps_url = self.get_google_maps_url(
                self.latitude, self.longitude)

        super().save(*args, **kwargs)

    def get_google_maps_url(self, latitude, longitude):
        """Generates the Google Maps URL for the location"""
        return f'https://www.google.com/maps?q={latitude},{longitude}'

    def __str__(self):
        return f"Collection by {self.worker} for {self.customer} on {self.date} at {self.latitude}, {self.longitude}"
