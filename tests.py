from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from inventory.models import Category, Product
from .models import Customer, Sale, SaleItem
from decimal import Decimal
class SalesTests(TestCase):
 def setUp(self):
  self.user=User.objects.create_user(username="tester",password="Pass12345!")
  self.client.login(username="tester",password="Pass12345!")
  c=Category.objects.create(name="General")
  self.p=Product.objects.create(sku="P001",name="Pen",category=c,price=Decimal("1000"),stock=10)
  self.cust=Customer.objects.create(name="Customer")
 def test_dashboard_requires_login(self):
  self.client.logout(); r=self.client.get(reverse("core:dashboard")); self.assertEqual(r.status_code,302)
 def test_create_sale(self):
  r=self.client.post(reverse("sales:sale_create"),{"customer":self.cust.id,"payment_method":"cash","qty_%s"%self.p.id:"2"})
  self.assertEqual(r.status_code,302); self.p.refresh_from_db(); self.assertEqual(self.p.stock,8); self.assertEqual(Sale.objects.count(),1); self.assertEqual(Sale.objects.first().total,Decimal("2000"))
