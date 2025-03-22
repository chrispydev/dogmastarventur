from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageFile
from django.utils.timezone import now
import random
import string

ImageFile.LOAD_TRUNCATED_IMAGES = True  # Allow truncated images to be loaded


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class CompanyAccount(models.Model):
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)

    @classmethod
    def get_instance(cls):
        """Ensures there is only one company account."""
        instance, _ = cls.objects.get_or_create(id=1)
        return instance

    def update_balance(self):
        """Ensures company balance matches total customer balances."""
        total_customer_balance = Customer.objects.aggregate(models.Sum('balance'))[
            'balance__sum'] or 0.00
        self.balance = total_customer_balance
        self.save()

    def __str__(self):
        return f"Company Account - Balance: GH₵{self.balance}"


class Customer(models.Model):
    name = models.CharField(max_length=150)
    next_of_kin = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    customer_image = models.ImageField(
        upload_to='media_file', default='default.jpg')
    created_by = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,  # ✅ Use SET_NULL instead of a function
        null=True,
        blank=True,
        related_name='customers_created'
    )

    joined = models.DateTimeField(auto_now_add=True)
    account_number = models.CharField(
        max_length=30, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save customer balance and update company balance"""
        if not self.account_number:
            self.account_number = self.generate_account_number()

        super().save(*args, **kwargs)

        # Update company balance when customer balance changes
        company = CompanyAccount.get_instance()
        company.update_balance()

        try:
            img_path = self.customer_image.path  # Get the image path
            img = Image.open(img_path)

            # Ensure compatibility by converting RGBA to RGB
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Resize only if the image is larger than the desired size
            max_size = 800
            if img.height > max_size or img.width > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Save the resized image back to the same path
            img.save(img_path, format='JPEG', quality=90)
        except Exception as e:
            print(f"Error processing image: {e}")

    def generate_account_number(self):
        """Generates a unique account number for each customer."""
        while True:
            account_number = f"DSV-ACC-{now().strftime('%Y%m%d')}-" + ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
            if not Customer.objects.filter(account_number=account_number).exists():
                return account_number


class Collection(models.Model):
    worker = models.ForeignKey(
        Worker, on_delete=models.SET_DEFAULT, default=None)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=150, blank=True)

    def save(self, *args, **kwargs):
        """Store customer name, increase balance, and update company balance"""
        if self.customer:
            self.customer_name = self.customer.name  # Store customer's name
            self.customer.balance += self.amount
            self.customer.save()

            # Update company balance
            company = CompanyAccount.get_instance()
            company.update_balance()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Collection by {self.worker} for {self.customer_name} on {self.date}"


class Deduction(models.Model):
    DEDUCTION_CHOICES = [
        ('customer', 'Customer Account'),
        ('company', 'Company Account')
    ]

    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="deductions")
    deduction_type = models.CharField(max_length=10, choices=DEDUCTION_CHOICES)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_deducted = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Ensure sufficient balance before deduction"""
        if self.deduction_type == "customer":
            if not self.customer:
                raise ValueError(
                    "Customer is required for customer deductions.")
            if self.customer.balance < self.amount:
                raise ValueError("Insufficient balance in customer's account.")
            self.customer.balance -= self.amount
            self.customer.save()

        elif self.deduction_type == "company":
            company = CompanyAccount.get_instance()
            if company.balance < self.amount:
                raise ValueError("Insufficient balance in company account.")
            company.balance -= self.amount
            company.save()

        super().save(*args, **kwargs)

    def __str__(self):
        if self.deduction_type == "customer":
            customer_name = self.customer.name if self.customer else "Unknown Customer"
            return f"GH₵{self.amount} deducted from {customer_name} by {self.admin.username}"
        return f"GH₵{self.amount} deducted from Company Account by {self.admin.username}"
