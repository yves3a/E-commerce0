from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError

# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return self.username

    class Meta:
        permissions = [
            ("can_manage_everything", "Can manage everything in the system"),
            ("can_manage_products", "Can manage products (add, edit, delete)"),
            ("can_edit_content", "Can edit content but cannot delete"),
            ("can_manage_discounts", "Can manage discounts"),
            ("can_manage_orders", "Can manage orders"),
            ("can_manage_customers", "Can manage customer information"),
            ("can_view_customer_info", "Can view customer information"),
            ("can_assist_issues", "Can assist with customer issues"),
            ("can_view_orders", "Can view orders"),
            ("can_read_only", "Can only view data"),
            ("can_manage_promotions", "Can manage promotions and discounts"),
            ("can_manage_product_visibility", "Can manage product visibility"),
            ("can_manage_inventory", "Can manage inventory"),
            ("can_update_product_quantity", "Can update product quantity"),
        ]


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("can_view_category", "Can view category"),
        ]


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # ImageField for product image
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):
        """Reduce stock quantity when an order is placed"""
        if quantity <= 0:
            raise ValidationError("Quantity must be a positive integer.")
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        raise ValidationError("Not enough stock available.")

    def get_stock_status(self):
        """Returns True if stock is available"""
        return self.stock_quantity > 0

    def get_image_url(self):
        """Returns the URL of the product image"""
        return self.image.url if self.image else '/static/default_image.jpg'

    class Meta:
        permissions = [
            ("can_manage_inventory", "Can manage inventory"),
            ("can_update_product_quantity", "Can update product quantity"),
            ("can_manage_product_visibility", "Can manage product visibility"),
            ("can_view_product", "Can view product"),
        ]


# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processed', 'Processed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def clean(self):
        """Ensure quantity is positive"""
        if self.quantity <= 0:
            raise ValidationError('Quantity must be a positive integer.')

    def order_total(self):
        """Calculate the total cost of the order"""
        return self.quantity * self.product.price

    class Meta:
        permissions = [
            ("can_manage_orders", "Can manage orders"),
            ("can_view_order", "Can view order"),
        ]
        ordering = ['-order_date']