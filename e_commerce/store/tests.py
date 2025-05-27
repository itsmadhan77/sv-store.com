from django.test import TestCase
from django.urls import reverse
from .models import User, Cart, Inventory, Order, Payment

class StoreTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.cart = Cart.objects.create(user=self.user)
        self.inventory_item = Inventory.objects.create(name='Test Product', price=10.00, stock=100)
        self.order = Order.objects.create(user=self.user, total_amount=10.00)
        self.payment = Payment.objects.create(order=self.order, amount=10.00, status='Completed')

    def test_user_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, testuser')

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)

    def test_inventory_item_creation(self):
        self.assertEqual(self.inventory_item.name, 'Test Product')
        self.assertEqual(self.inventory_item.price, 10.00)

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.total_amount, 10.00)

    def test_payment_creation(self):
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.amount, 10.00)
        self.assertEqual(self.payment.status, 'Completed')