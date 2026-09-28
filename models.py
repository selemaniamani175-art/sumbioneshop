from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from inventory.models import Product

class Customer(models.Model):
    name=models.CharField(max_length=150)
    phone=models.CharField(max_length=30,blank=True)
    email=models.EmailField(blank=True)
    address=models.CharField(max_length=255,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["name"]
    def __str__(self): return self.name

class Sale(models.Model):
    PAYMENT_CHOICES=[("cash","Cash"),("mobile","Mobile Money"),("card","Card"),("bank","Bank Transfer"),("mixed","Mixed")]
    STATUS_CHOICES=[("completed","Completed"),("cancelled","Cancelled")]
    invoice_no=models.CharField(max_length=30,unique=True)
    customer=models.ForeignKey(Customer,on_delete=models.PROTECT,related_name="sales")
    sold_by=models.ForeignKey("auth.User",on_delete=models.PROTECT,related_name="sales")
    payment_method=models.CharField(max_length=20,choices=PAYMENT_CHOICES,default="cash")
    payment_reference=models.CharField(max_length=100,blank=True)
    notes=models.TextField(blank=True)
    subtotal=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    discount=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    discount_percent=models.DecimalField(max_digits=5,decimal_places=2,default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])
    tax=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    total=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    amount_paid=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="completed")
    cancelled_by=models.ForeignKey("auth.User",null=True,blank=True,on_delete=models.PROTECT,related_name="cancelled_sales")
    cancellation_reason=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    cancelled_at=models.DateTimeField(null=True,blank=True)
    class Meta: ordering=["-created_at"]
    def __str__(self): return self.invoice_no
    @property
    def balance(self): return max(self.total - self.amount_paid, Decimal("0"))
    @property
    def change(self): return max(self.amount_paid - self.total, Decimal("0"))
    def recalculate_total(self):
        self.subtotal=sum((i.subtotal for i in self.items.all()),Decimal("0"))
        self.total=max(self.subtotal-self.discount+self.tax,Decimal("0")); self.save(update_fields=["subtotal","total"])

class SaleItem(models.Model):
    sale=models.ForeignKey(Sale,on_delete=models.CASCADE,related_name="items")
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name="sale_items")
    quantity=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price=models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(Decimal("0"))])
    discount=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    @property
    def gross(self): return self.quantity*self.unit_price
    @property
    def subtotal(self): return max(self.gross-self.discount,Decimal("0"))
    def __str__(self): return f"{self.sale.invoice_no} - {self.product.name}"

class SaleReturn(models.Model):
    sale=models.ForeignKey(Sale,on_delete=models.PROTECT,related_name="returns")
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name="returns")
    quantity=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason=models.CharField(max_length=255)
    processed_by=models.ForeignKey("auth.User",on_delete=models.PROTECT,related_name="processed_returns")
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Return {self.sale.invoice_no} - {self.product.name}"
