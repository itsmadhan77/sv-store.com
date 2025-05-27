from django.contrib import admin
from .models import User, Cart, Inventory, Order, Payment

#admin.site.register(User)
admin.site.register(Cart)
admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(Payment)