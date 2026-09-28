from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("sales", "0002_professional_features")]
    operations = [migrations.AddField(model_name="sale", name="payment_reference", field=models.CharField(blank=True, max_length=100))]
