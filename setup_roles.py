from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from core.models import BusinessSettings

class Command(BaseCommand):
    help='Create Mauzo roles and default business settings'
    def handle(self,*args,**kwargs):
        for name in ['Admin','Manager','Seller']:
            Group.objects.get_or_create(name=name)
        BusinessSettings.get_solo()
        user=User.objects.filter(username='admin').first()
        if user:
            user.is_staff=True; user.is_superuser=True; user.set_password('admin12345'); user.save()
            self.stdout.write(self.style.SUCCESS('Admin account ready: admin / admin12345'))
        self.stdout.write(self.style.SUCCESS('Roles and business settings ready.'))
