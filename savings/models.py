from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageFile
from django.core.files.storage import default_storage
from datetime import datetime

ImageFile.LOAD_TRUNCATED_IMAGES = True  # Allow truncated images to be loaded


class Customer(models.Model):
    name = models.CharField(max_length=150, default='name')
    next_of_kin = models.CharField(max_length=100, default='next_of_kin')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    customer_image = models.ImageField(
        upload_to='media_file', default='default.jpg')
    joined = models.DateTimeField(auto_now_add=True)

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


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


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
