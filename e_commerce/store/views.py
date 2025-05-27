from django.shortcuts import render, redirect,redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Cart, Inventory, Order, Payment, CartItem,UserProfile, OrderItem
from .forms import UserLoginForm, OrderForm, InventoryForm,UserRegisterForm
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.contrib import messages

# Admin credentials stored in session for demo purposes
ADMIN_CREDENTIALS_KEY = 'admin_credentials'

def get_admin_credentials(request):
    creds = request.session.get(ADMIN_CREDENTIALS_KEY)
    if not creds:
        creds = {'username': 'MADHAN', 'password': '1234'}
        request.session[ADMIN_CREDENTIALS_KEY] = creds
    return creds

def set_admin_credentials(request, username, password):
    request.session[ADMIN_CREDENTIALS_KEY] = {'username': username, 'password': password}

def admin_login(request):
    error = None
    creds = get_admin_credentials(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == creds['username'] and password == creds['password']:
            request.session['admin_credentials'] = creds
            request.session['is_admin_logged_in'] = True
            return redirect('store:admin_dashboard')
        else:
            error = 'Invalid admin credentials'
    return render(request, 'store/admin_login.html', {'error': error})

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('is_admin_logged_in'):
            return view_func(request, *args, **kwargs)
        return redirect('store:admin_login')
    return _wrapped_view

@admin_required
def admin_dashboard(request):
    return render(request, 'store/admin_dashboard.html')

@admin_required
def change_admin_credentials(request):
    creds = get_admin_credentials(request)
    error = None
    success = None
    if request.method == 'POST':
        current_username = request.POST.get('current_username')
        current_password = request.POST.get('current_password')
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        if current_username == creds['username'] and current_password == creds['password']:
            set_admin_credentials(request, new_username, new_password)
            success = "Credentials updated successfully."
        else:
            error = "Current credentials are incorrect."
    return render(request, 'store/change_credentials.html', {'error': error, 'success': success})

@admin_required
def admin_orders_view(request):
    orders = Order.objects.all()
    updated_order_id = request.session.pop('updated_order_id', None)
    return render(request, 'store/admin_orders_view.html', {
        'orders': orders,
        'updated_order_id': updated_order_id
    })

def admin_logout(request):
    request.session.flush()
    return redirect('store:admin_login')

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store:user_dashboard')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'store/login.html', {'form': form})

@login_required
def user_dashboard(request):
    return render(request, 'store/user_dashboard.html')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def inventory_view(request):
    products = Inventory.objects.all()
    return render(request, 'store/inventory.html', {'products': products})


@login_required
def payment_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    orders = Order.objects.filter(user=request.user).order_by('-order_date')

    if request.method == 'POST':
        payment_successful = True  # Replace with actual payment logic
        if payment_successful:
            order = Order.objects.create(
                user=request.user,
                total=total_price,
                status='pending'
            )
            for item in cart_items:
                order.items.create(product=item.product, quantity=item.quantity)
            cart_items.delete()
            return redirect('store:user_orders')
    return render(request, 'store/payments.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'orders': orders
    })

def user_logout(request):
    logout(request)
    return redirect('store:login')

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.email = form.cleaned_data['email']
            user.save()
            # Save profile
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            return redirect('store:login')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})

def admin_inventory_view(request):
    creds = request.session.get('admin_credentials')
    if not creds or not request.session.get('is_admin_logged_in'):
        return redirect('store:admin_login')
    products = Inventory.objects.all()
    return render(request, 'store/admin_inventory.html', {'products': products})

def add_product(request):
    creds = request.session.get('admin_credentials')
    if not creds or not request.session.get('is_admin_logged_in'):
        return redirect('store:admin_login')
    if not request.session.get('admin_credentials'):
        return redirect('store:admin_login')
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:admin_inventory')
    else:
        form = InventoryForm()
    return render(request, 'store/add_product.html', {'form': form})

def edit_product(request, pk):
    if not request.session.get('admin_credentials') or not request.session.get('is_admin_logged_in'):
        return redirect('store:admin_login')
    product = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store:admin_inventory')
    else:
        form = InventoryForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form, 'product': product})

def delete_product(request, pk):
    if not request.session.get('admin_credentials') or not request.session.get('is_admin_logged_in'):
        return redirect('store:admin_login')
    product = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('store:admin_inventory')
    return render(request, 'store/confirm_delete.html', {'product': product})

@login_required
def add_to_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(Inventory, id=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item.save()
    return redirect('store:user_inventory')

def user_inventory_view(request):
    inventory = Inventory.objects.all()  # Show all products (from admin inventory to user inventory)
    return render(request, 'store/user_inventory.html', {'inventory': inventory})

@login_required
def remove_from_cart(request, item_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=item_id)
    cart_item.delete()
    return redirect('store:cart')

@login_required
def increase_quantity(request, item_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('store:cart')

@login_required
def decrease_quantity(request, item_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('store:cart')

@login_required
def user_orders_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'user_orders.html', {'orders': orders})

@admin_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        order.status = status
        order.save()
        request.session['updated_order_id'] = order.id
    return redirect('store:admin_orders')

@login_required
def place_order(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number')
        card_name = request.POST.get('card_name')
        card_expiry = request.POST.get('card_expiry')
        card_cvv = request.POST.get('card_cvv')

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        order = Order.objects.create(user=request.user, status='Pending')
        total_amount = 0

        for item in cart_items:
            order_item = OrderItem.objects.create(
                product=item.product,
                quantity=item.quantity
            )
            order.items.add(order_item)
            total_amount += item.product.price * item.quantity

        cart_items.delete()

        # Save payment info
        payment = Payment.objects.create(
            order=order,
            amount=total_amount,
            payment_method=payment_method,
            status='Completed' if payment_method == 'cod' else 'Pending'
        )

        # Add success message
        messages.success(request, "Payment completed and your order is confirmed!")

        return redirect('store:payments')
    return redirect('cart')