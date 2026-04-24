from django.db import models
from django.contrib.auth.models import User


class PrescriptionOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    patient_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    delivery_address = models.TextField(help_text="Where should we deliver the medicines?")
    prescription_file = models.FileField(upload_to='prescriptions/')

    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Invoiced', 'Invoice Sent to Customer'),
        ('Paid', 'Payment Received'),
        ('Shipped', 'Order Shipped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.status}"


class Medicine(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, help_text="e.g., Vitamins, First Aid, Skincare")
    brand = models.CharField(max_length=100, default='eCure', help_text="e.g., Tylenol, Pfizer, Bayer")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)
    is_trending = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.quantity} of {self.medicine.name}"

    def sub_total(self):
        return self.medicine.price * self.quantity


class Order(models.Model):
    # Customer Details
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    shipping_address = models.TextField()

    # Order Details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price at the time of purchase")
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.medicine.name}"

class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, help_text="A short teaser for the homepage")
    content = models.TextField(help_text="The full article text")
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    published_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title