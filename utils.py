from .models import AuditLog, BusinessSettings

def is_admin(user): return user.is_superuser or user.groups.filter(name="Admin").exists()
def is_manager(user): return is_admin(user) or user.groups.filter(name="Manager").exists()
def log_action(request, action, obj=None, details=""):
    AuditLog.objects.create(user=request.user if request.user.is_authenticated else None, action=action,
        model_name=obj.__class__.__name__ if obj else "", object_id=str(obj.pk) if obj and getattr(obj,"pk",None) else "",
        details=details, ip_address=request.META.get("REMOTE_ADDR"))

def settings_obj(): return BusinessSettings.get_solo()
