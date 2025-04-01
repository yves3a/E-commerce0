from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product, Category
from .models import Order


# Custom action for Category
def mark_as_updated(modeladmin, request, queryset):
    updated_count = queryset.update(name='Updated Category')
    modeladmin.message_user(request, f"{updated_count} categories have been updated.")

mark_as_updated.short_description = "Mark selected categories as updated"

# Inline Product editing in Category
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

# Custom admin for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    actions = [mark_as_updated]
    inlines = [ProductInline]

# Custom admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    ordering = ('-price',)

# Custom admin for CustomUser
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

# Register models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, 
admin.site.register(Order))


