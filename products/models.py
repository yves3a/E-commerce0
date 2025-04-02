from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError

# Custom User Model
class CustomUser(AbstractUser):
    """
    Extended User model that adds role-based functionality.
    Inherits from Django's AbstractUser for base user functionality.
    """
    # Define available user roles
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    ]
    # Add role field with customer as default
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        """String representation of the user"""
        return self.username

    class Meta:
        """
        Meta class defining model permissions
        These permissions control access to different functionalities
        """
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
    """
    Model for product categories.
    Used to organize products into logical groups.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True)

    def __str__(self):
        """String representation of the category"""
        return self.name

    class Meta:
        """Meta class defining category-specific permissions"""
        permissions = [
            ("can_view_category", "Can view category"),
        ]


# Product Model
class Product(models.Model):
    """
    Model for store products.
    Contains all product-related information and inventory management.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # ImageField for product image
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation of the product"""
        return self.name

    def reduce_stock(self, quantity):
        """
        Reduce stock quantity when an order is placed
        Args:
            quantity: Amount to reduce from stock
        Returns:
            bool: True if stock was successfully reduced
        Raises:
            ValidationError: If quantity is invalid or insufficient stock
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be a positive integer.")
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        raise ValidationError("Not enough stock available.")

    def get_stock_status(self):
        """
        Returns True if stock is available
        Used to check product availability
        """
        return self.stock_quantity > 0

    def get_image_url(self):
        """
        Returns the URL of the product image
        Returns default image if no image is uploaded
        """
        return self.image.url if self.image else '/static/default_image.jpg'

    class Meta:
        """Meta class defining product-specific permissions"""
        permissions = [
            ("can_manage_inventory", "Can manage inventory"),
            ("can_update_product_quantity", "Can update product quantity"),
            ("can_manage_product_visibility", "Can manage product visibility"),
            ("can_view_product", "Can view product"),
        ]


# Order Model
class Order(models.Model):
    """
    Model for customer orders.
    Tracks order status and details.
    """
    # Define possible order statuses
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
        """String representation of the order"""
        return f"Order {self.id} by {self.user.username}"

    def clean(self):
        """
        Ensure quantity is positive
        Validates order data before saving
        """
        if self.quantity <= 0:
            raise ValidationError('Quantity must be a positive integer.')

    def order_total(self):
        """
        Calculate the total cost of the order
        Returns the product price multiplied by quantity
        """
        return self.quantity * self.product.price

    class Meta:
        """
        Meta class defining order-specific permissions and ordering
        Orders are sorted by date, newest first
        """
        permissions = [
            ("can_manage_orders", "Can manage orders"),
            ("can_view_order", "Can view order"),
        ]
        ordering = ['-order_date']