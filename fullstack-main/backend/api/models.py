from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    img = models.ImageField(upload_to='products/')  # 
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    prev_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    company = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    reviews = models.TextField(blank=True)
    rating = models.IntegerField(default=0)

    quantity = models.PositiveIntegerField(default=0)        
    is_new = models.BooleanField(default=False)              
    has_discount = models.BooleanField(default=False)        
    def __str__(self):
        return self.title
    
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class DeliveryAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=30)