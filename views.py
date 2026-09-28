from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from inventory.models import Product
from core.models import BusinessSettings
from core.utils import is_manager, log_action
from .forms import CustomerForm
from .models import Customer, Sale, SaleItem, SaleReturn

def _invoice_no():
    last=Sale.objects.order_by("-id").first(); n=(last.id+1 if last else 1); return f"INV-{n:06d}"
def _discount_limit(user, settings):
    if user.is_superuser or user.groups.filter(name="Admin").exists(): return Decimal("100")
    if user.groups.filter(name="Manager").exists(): return settings.manager_max_discount
    return settings.seller_max_discount
@login_required
def customer_list(request):
    q=request.GET.get("q","").strip(); customers=Customer.objects.all()
    if q: customers=customers.filter(Q(name__icontains=q)|Q(phone__icontains=q)|Q(email__icontains=q))
    return render(request,"sales/customer_list.html",{"customers":customers,"q":q})
@login_required
def customer_create(request):
    form=CustomerForm(request.POST or None)
    if form.is_valid(): obj=form.save(); log_action(request,"Created customer",obj); messages.success(request,"Customer added."); return redirect("sales:customer_list")
    return render(request,"sales/customer_form.html",{"form":form,"title":"Add Customer"})
@login_required
def customer_update(request,pk):
    obj=get_object_or_404(Customer,pk=pk); form=CustomerForm(request.POST or None,instance=obj)
    if form.is_valid(): form.save(); log_action(request,"Updated customer",obj); messages.success(request,"Customer updated."); return redirect("sales:customer_list")
    return render(request,"sales/customer_form.html",{"form":form,"title":"Edit Customer"})
@login_required
def sale_create(request):
    products=list(Product.objects.filter(is_active=True,stock__gt=0).select_related("category")); walkin, _ = Customer.objects.get_or_create(name="Walk-in Customer"); customers=Customer.objects.all(); settings=BusinessSettings.get_solo(); discount_limit=_discount_limit(request.user,settings)
    if request.method=="POST":
        customer_id=request.POST.get("customer")
        if customer_id:
            customer=get_object_or_404(Customer,pk=customer_id)
        else:
            customer, _ = Customer.objects.get_or_create(name="Walk-in Customer")
        payment=request.POST.get("payment_method","cash") or "cash"; payment_reference=request.POST.get("payment_reference","").strip(); notes=request.POST.get("notes","")
        if payment not in {"cash","mobile","card","bank","mixed"}: payment="cash"
        if payment in {"mobile","card","bank"} and not payment_reference:
            messages.error(request,"Enter the payment transaction/reference number.")
            return render(request,"sales/sale_form.html",locals())
        selected=[]
        for p in products:
            try: qty=int(request.POST.get(f"qty_{p.id}",0))
            except ValueError: qty=0
            if qty>0: selected.append((p,qty))
        if not selected: messages.error(request,"Add at least one product."); return render(request,"sales/sale_form.html",locals())
        try: discount_amount=Decimal(request.POST.get("discount_amount","0") or 0)
        except Exception: discount_amount=Decimal("0")
        if discount_amount < 0:
            messages.error(request,"Discount amount cannot be negative.")
            return render(request,"sales/sale_form.html",locals())
        limit=_discount_limit(request.user,settings)
        with transaction.atomic():
            locked=[]
            for p,qty in selected:
                p=Product.objects.select_for_update().get(pk=p.pk)
                if qty>p.stock: messages.error(request,f"Insufficient stock for {p.name}. Available: {p.stock}."); return render(request,"sales/sale_form.html",locals())
                locked.append((p,qty))
            subtotal=sum((p.price*q for p,q in locked),Decimal("0")).quantize(Decimal("0.01"))
            max_discount=(subtotal*limit/Decimal("100")).quantize(Decimal("0.01"))
            if discount_amount > subtotal:
                messages.error(request,f"Discount cannot be greater than the subtotal ({subtotal:.2f} TZS).")
                return render(request,"sales/sale_form.html",locals())
            if discount_amount > max_discount:
                messages.error(request,f"Your maximum discount is {max_discount:.2f} TZS ({limit}% of the subtotal).")
                return render(request,"sales/sale_form.html",locals())
            discount_amount=discount_amount.quantize(Decimal("0.01"))
            discount_percent=(discount_amount/subtotal*Decimal("100")).quantize(Decimal("0.01")) if subtotal else Decimal("0")
            taxable=max(subtotal-discount_amount,Decimal("0"))
            tax=(taxable*settings.tax_rate/Decimal("100")).quantize(Decimal("0.01"))
            total=taxable+tax
            try:
                paid_raw=request.POST.get("amount_paid","").strip()
                paid=Decimal(paid_raw) if paid_raw else total
            except Exception:
                paid=total
            if paid<total: messages.error(request,"Amount paid cannot be less than the total for a completed sale."); return render(request,"sales/sale_form.html",locals())
            sale=Sale.objects.create(invoice_no=_invoice_no(),customer=customer,sold_by=request.user,payment_method=payment,payment_reference=payment_reference,notes=notes,subtotal=subtotal,discount=discount_amount,discount_percent=discount_percent,tax=tax,total=total,amount_paid=paid)
            for p,q in locked: SaleItem.objects.create(sale=sale,product=p,quantity=q,unit_price=p.price); p.stock-=q; p.save(update_fields=["stock","updated_at"])
            log_action(request,"Created sale",sale,f"Total={total}; Discount={discount_amount} TZS ({discount_percent}%)")
        messages.success(request,f"Sale {sale.invoice_no} completed."); return redirect("sales:sale_detail",pk=sale.pk)
    return render(request,"sales/sale_form.html",{"products":products,"customers":customers,"settings":settings,"discount_limit":discount_limit})
@login_required
def sale_list(request):
    q=request.GET.get("q","").strip(); sales=Sale.objects.select_related("customer","sold_by")
    if q: sales=sales.filter(Q(invoice_no__icontains=q)|Q(customer__name__icontains=q))
    return render(request,"sales/sale_list.html",{"sales":sales,"q":q})
@login_required
def sale_detail(request,pk):
    sale=get_object_or_404(Sale.objects.select_related("customer","sold_by","cancelled_by").prefetch_related("items__product","returns__product"),pk=pk)
    return render(request,"sales/sale_detail.html",{"sale":sale})
@login_required
def sale_cancel(request,pk):
    if not is_manager(request.user): messages.error(request,"Manager or Admin access required."); return redirect("sales:sale_detail",pk=pk)
    sale=get_object_or_404(Sale,pk=pk)
    if sale.status=="cancelled": messages.info(request,"Sale is already cancelled."); return redirect("sales:sale_detail",pk=pk)
    if request.method=="POST":
        with transaction.atomic():
            for item in sale.items.select_related("product"):
                p=Product.objects.select_for_update().get(pk=item.product_id); p.stock+=item.quantity; p.save(update_fields=["stock","updated_at"])
            sale.status="cancelled"; sale.cancelled_by=request.user; sale.cancellation_reason=request.POST.get("reason",""); sale.cancelled_at=timezone.now(); sale.save(update_fields=["status","cancelled_by","cancellation_reason","cancelled_at"]); log_action(request,"Cancelled sale",sale,sale.cancellation_reason)
        messages.success(request,"Sale cancelled and stock restored."); return redirect("sales:sale_detail",pk=pk)
    return render(request,"sales/cancel_sale.html",{"sale":sale})
@login_required
def sale_return(request,pk):
    sale=get_object_or_404(Sale,pk=pk)
    if sale.status=="cancelled": messages.error(request,"Cancelled sale cannot be returned."); return redirect("sales:sale_detail",pk=pk)
    if request.method=="POST":
        item=get_object_or_404(SaleItem,pk=request.POST.get("item"),sale=sale)
        try: qty=int(request.POST.get("quantity","0"))
        except ValueError: qty=0
        already=SaleReturn.objects.filter(sale=sale,product=item.product).aggregate(v=Sum("quantity"))["v"] or 0
        if qty<1 or qty+already>item.quantity: messages.error(request,"Return quantity exceeds the remaining sold quantity.")
        else:
            with transaction.atomic():
                p=Product.objects.select_for_update().get(pk=item.product_id); p.stock+=qty; p.save(update_fields=["stock","updated_at"])
                ret=SaleReturn.objects.create(sale=sale,product=p,quantity=qty,reason=request.POST.get("reason","Customer return"),processed_by=request.user); log_action(request,"Processed return",ret,ret.reason)
            messages.success(request,"Return processed and stock restored."); return redirect("sales:sale_detail",pk=pk)
    return render(request,"sales/return_form.html",{"sale":sale,"items":sale.items.select_related("product")})
@login_required
def reports(request):
    sales=Sale.objects.filter(status="completed").select_related("customer","sold_by")
    start=request.GET.get("start"); end=request.GET.get("end")
    if start: sales=sales.filter(created_at__date__gte=start)
    if end: sales=sales.filter(created_at__date__lte=end)
    agg=sales.aggregate(revenue=Sum("total"),discount=Sum("discount"),tax=Sum("tax"))
    revenue=agg["revenue"] or Decimal("0")
    cost=Decimal("0")
    for sale in sales.prefetch_related("items__product"): cost+=sum((i.product.cost_price*i.quantity for i in sale.items.all()),Decimal("0"))
    return render(request,"reports.html",{"sales":sales[:200],"total":revenue,"count":sales.count(),"discount_total":agg["discount"] or 0,"tax_total":agg["tax"] or 0,"cost":cost,"profit":revenue-cost,"start":start or "","end":end or ""})
