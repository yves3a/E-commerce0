from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    # ================== API - User Management URLs ==================
    path('api/v1/users/', views.UserList.as_view(), name='user-list'),  # List and create users
    path('api/v1/users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),  # Retrieve, update, or delete a specific user
    path('api/v1/users/create/', views.UserCreate.as_view(), name='user-create'),  # Create a new user
    path('api/v1/users/update/<int:pk>/', views.UserDetail.as_view(), name='user-update'),  # Update user details (UserDetail already handles updates)
    path('api/v1/users/delete/<int:pk>/', views.UserDetail.as_view(), name='user-delete'),  # Delete a user (UserDetail already handles deletes)

    # ================== API - Product Management URLs ==================
    path('api/v1/products/', views.ProductList.as_view(), name='product-list'),  
    path('api/v1/products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),  
    path('api/v1/products/create/', views.ProductList.as_view(), name='create-product'),  
    path('api/v1/products/update/<int:pk>/', views.ProductDetail.as_view(), name='update-product'),  
    path('api/v1/products/delete/<int:pk>/', views.ProductDetail.as_view(), name='delete-product'), 

    # ================== API - Order Management URLs ==================
    path('api/v1/orders/', views.OrderList.as_view(), name='order-list'),  
    path('api/v1/orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),  
    path('api/v1/orders/create/', views.OrderList.as_view(), name='create-order'), 
    path('api/v1/orders/update/<int:pk>/', views.OrderDetail.as_view(), name='update-order'), 
    path('api/v1/orders/delete/<int:pk>/', views.OrderDetail.as_view(), name='delete-order'),  

    # ================== Frontend - Authentication and Views ==================
    path('products/', views.product_list, name='product-list'),  
    path('product/<int:id>/', views.product_details, name='product-details'),
    path('signup/', views.signup_view, name='signup'), 
    path('login/', views.login_view, name='login'),  
    path('logout/', views.logout_view, name='logout'), 

    # ================== Frontend - Order Management ==================
    path('order/create/', views.make_order, name='make-order'), 
    path('order/edit/<int:order_id>/', views.edit_order, name='edit-order'), 
    path('order/delete/<int:order_id>/', views.delete_order, name='delete-order'), 
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # ================== Frontend - User Dashboard ==================
    path('dashboard/', views.user_dashboard, name='user-dashboard'),  
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),  
    path('profile/', views.profile_view, name='profile'),
    path('order/<int:order_id>/', views.order_detail, name='order-detail'),
    path('users/', views.user_list, name='user-list'),  # Add user list URL

    # ================== API - Product Search ==================
    path('api/products/search/', views.search_products, name='api-products-search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
