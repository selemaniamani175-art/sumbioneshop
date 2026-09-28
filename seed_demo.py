from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Category, Product
from sales.models import Customer
from decimal import Decimal
class Command(BaseCommand):
 help="Create demo user and sample inventory/customer records."
 def handle(self,*args,**kwargs):
  user,_=User.objects.get_or_create(username="admin",defaults={"is_staff":True,"is_superuser":True,"email":"admin@example.com"})
  user.is_staff=True; user.is_superuser=True; user.set_password("admin12345"); user.save()
  cat,_=Category.objects.get_or_create(name="General")
  samples=[("P001","Sugar",2500,40),("P002","Cooking Oil",6500,25),("P003","Soap",1800,50),("P004","Rice 1kg",3000,35)]
  for sku,name,price,stock in samples: Product.objects.get_or_create(sku=sku,defaults={"name":name,"category":cat,"price":Decimal(str(price)),"cost_price":Decimal(str(price*.8)),"stock":stock,"reorder_level":5})
  Customer.objects.get_or_create(name="Walk-in Customer",defaults={"phone":""})
  self.stdout.write(self.style.SUCCESS("Demo data created. Login: admin / admin12345"))
