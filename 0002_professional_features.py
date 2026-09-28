import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.core.validators
from decimal import Decimal
class Migration(migrations.Migration):
    dependencies=[("sales","0001_initial"),("core","0001_initial")]
    operations=[
        migrations.AddField(model_name="sale",name="subtotal",field=models.DecimalField(decimal_places=2,default=0,max_digits=12)),
        migrations.AddField(model_name="sale",name="discount",field=models.DecimalField(decimal_places=2,default=0,max_digits=12)),
        migrations.AddField(model_name="sale",name="discount_percent",field=models.DecimalField(decimal_places=2,default=0,max_digits=5,validators=[django.core.validators.MinValueValidator(0),django.core.validators.MaxValueValidator(100)])),
        migrations.AddField(model_name="sale",name="tax",field=models.DecimalField(decimal_places=2,default=0,max_digits=12)),
        migrations.AddField(model_name="sale",name="amount_paid",field=models.DecimalField(decimal_places=2,default=0,max_digits=12)),
        migrations.AddField(model_name="sale",name="status",field=models.CharField(choices=[("completed","Completed"),("cancelled","Cancelled")],default="completed",max_length=20)),
        migrations.AddField(model_name="sale",name="cancellation_reason",field=models.TextField(blank=True)),
        migrations.AddField(model_name="sale",name="cancelled_at",field=models.DateTimeField(blank=True,null=True)),
        migrations.AddField(model_name="sale",name="cancelled_by",field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name="cancelled_sales",to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="saleitem",name="discount",field=models.DecimalField(decimal_places=2,default=0,max_digits=12)),
        migrations.AlterField(model_name="sale",name="payment_method",field=models.CharField(choices=[("cash","Cash"),("mobile","Mobile Money"),("card","Card"),("bank","Bank Transfer"),("mixed","Mixed")],default="cash",max_length=20)),
        migrations.CreateModel(name="SaleReturn",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("quantity",models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),("reason",models.CharField(max_length=255)),("created_at",models.DateTimeField(auto_now_add=True)),("processed_by",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="processed_returns",to=settings.AUTH_USER_MODEL)),("product",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="returns",to="inventory.product")),("sale",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name="returns",to="sales.sale"))])
    ]
