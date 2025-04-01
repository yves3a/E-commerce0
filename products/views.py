from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, Product, Order, Category  # Import the Order model from models.py
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer, ProductSerializer, OrderSerializer
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, OrderForm 
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

# Custom pagination class for product views
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# ================== API Views ==================

# User API Views
class UserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

# Product API Views with search and filtering
class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        in_stock = self.request.query_params.get('in_stock')
        if in_stock is not None:
            queryset = queryset.filter(stock_quantity__gt=0 if in_stock.lower() == 'true' else 0)
        return queryset

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Order API Views
class OrderList(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

# ================== Template Views ==================

# User Signup View (Form-based)
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Signup successful! Welcome to the dashboard.')
            return redirect('user-dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                # Redirect to the appropriate dashboard based on user role
                return redirect('admin-dashboard' if getattr(user, 'role', None) == 'admin' else 'user-dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()

    # Ensure the correct path to the login template
    return render(request, 'login.html', {'form': form})

# User Logout View
def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('dashboard')

# User Dashboard
@login_required
def user_dashboard(request):
    orders = Order.objects.filter(user=request.user)
    products = Product.objects.all()
    context = {
        'orders': orders,
        'products': products,
    }
    return render(request, 'user-dashboard.html', context)

# Admin Dashboard
@login_required
def admin_dashboard(request):
    return render(request, 'admin-dashboard.html')  # Admin dashboard template needs to be created

# Product Detail View (Template-based)
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product-detail.html', {'product': product})

# Make Order View
@login_required
def make_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            
            # Validate stock quantity
            if order.quantity > order.product.stock_quantity:
                messages.error(request, "Not enough stock available.")
                return redirect('make-order')
            
            try:
                # Update stock and save order
                order.product.stock_quantity -= order.quantity
                order.product.save()
                order.save()
                messages.success(request, "Order placed successfully.")
                return redirect('user-dashboard')
            except Exception as e:
                messages.error(request, f"Error placing order: {str(e)}")
                return redirect('make-order')
    else:
        form = OrderForm()
    
    # Get all available products for the form
    products = Product.objects.filter(stock_quantity__gt=0)
    
    return render(request, 'make-order.html', {
        'form': form,
        'products': products
    })

# Order Edit View (Form-based)
@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully.')
            return redirect('user-dashboard')
    else:
        form = OrderForm(instance=order)
    return render(request, 'edit-order.html', {'form': form, 'order': order})

# Order Delete View
@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully.')
        return redirect('user-dashboard')
    return render(request, 'delete-order.html', {'order': order})

# Home View
def home(request):
    return render(request, 'home.html')

# Product List View (Template-based)
def product_list(request):
    # Get all products initially
    products = Product.objects.all()
    
    # Get all categories
    categories = Category.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Handle category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category__name__iexact=category)
    
    # Handle tab filtering
    tab = request.GET.get('tab', 'all')
    if tab == 'new':
        # Filter products created in the last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        products = products.filter(created_date__gte=seven_days_ago)
    elif tab == 'featured':
        # Get top 8 highest-priced products
        products = products.order_by('-price')[:8]
    elif tab == 'sale':
        # Products with stock > 10
        products = products.filter(stock_quantity__gt=10)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'current_search': search_query,
        'current_tab': tab,
    }
    
    return render(request, 'product-list.html', context)

@receiver(pre_save, sender=Order)
def calculate_total_price(sender, instance, **kwargs):
    instance.total_price = instance.quantity * instance.product.price

def product_details(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product-detail.html', {'product': product})

def search_products(request):
    # Get all products initially
    products = Product.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Handle category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category__name__iexact=category)
    
    # Handle tab filtering
    tab = request.GET.get('tab', 'all')
    if tab == 'new':
        # Filter products created in the last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        products = products.filter(created_date__gte=seven_days_ago)
    elif tab == 'featured':
        # Get top 8 highest-priced products
        products = products.order_by('-price')[:8]
    elif tab == 'sale':
        # Products with stock > 10
        products = products.filter(stock_quantity__gt=10)
    
    # Convert products to JSON
    products_data = [{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),  # Convert Decimal to string
        'stock_quantity': product.stock_quantity,
        'is_new': (timezone.now() - product.created_date).days <= 7,
        'is_featured': product.price > 1000,  # Example criteria
        'category': product.category.name if product.category else None,
    } for product in products]
    
    return JsonResponse({'products': products_data})

def dashboard_view(request):
    # Get all products initially
    products = Product.objects.all()
    
    # Get all categories
    categories = Category.objects.all()
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Handle category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category__name__iexact=category)
    
    # Handle tab filtering
    tab = request.GET.get('tab', 'all')
    if tab == 'new':
        # Filter products created in the last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        products = products.filter(created_date__gte=seven_days_ago)
    elif tab == 'featured':
        # Assuming we have a featured field, if not we'll use price as a proxy
        products = products.order_by('-price')[:8]
    elif tab == 'sale':
        # For demonstration, we'll consider products with stock > 10 as on sale
        products = products.filter(stock_quantity__gt=10)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'current_search': search_query,
        'current_tab': tab,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-order_date')[:5]  # Get last 5 orders
    context = {
        'user': user,
        'orders': orders,
    }
    return render(request, 'profile.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)

@login_required
def user_list(request):
    # Check if user is staff/admin
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view the user list.')
        return redirect('dashboard')
    
    # Get all users
    users = CustomUser.objects.all().order_by('username')
    
    return render(request, 'user-list.html', {'users': users})



