from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageFile
from django.core.files.storage import default_storage


ImageFile.LOAD_TRUNCATED_IMAGES = True  # Allow truncated images to be loaded


class Customer(models.Model):
    name = models.CharField(max_length=150, default='name')
    next_of_kin = models.CharField(max_length=100, default='next_of_kin')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    customer_image = models.ImageField(
        upload_to='media_file', default='default.jpg')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            img = Image.open(self.customer_image.path)

            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Resize image if larger than 800x800
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)

            # Save the image using the storage backend
            with default_storage.open(self.customer_image.name, 'wb') as f:
                img.save(f, 'JPEG')
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
