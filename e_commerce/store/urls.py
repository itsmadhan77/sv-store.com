from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('orders/', views.user_orders_view, name='user_orders'),
    path('place_order/', views.place_order, name='place_order'),
    path('admin/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('payments/', views.payment_view, name='payments'),
    path('a_login/', views.admin_login, name='admin_login'),
    path('a_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('a_logout/', views.admin_logout, name='admin_logout'),
    path('a_change_credentials/', views.change_admin_credentials, name='change_admin_credentials'),
    path('a_inventory/', views.admin_inventory_view, name='admin_inventory'),
    path('a_inventory/add/', views.add_product, name='add_product'),
    path('a_inventory/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('a_inventory/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/dashboard/view_inventory/', views.user_inventory_view, name='user_inventory'),
    path('register/', views.user_register, name='register'),
   
    
]