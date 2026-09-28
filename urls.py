from django.urls import path
from . import views
app_name="sales"
urlpatterns=[path("",views.sale_list,name="sale_list"),path("new/",views.sale_create,name="sale_create"),path("<int:pk>/",views.sale_detail,name="sale_detail"),path("<int:pk>/cancel/",views.sale_cancel,name="sale_cancel"),path("<int:pk>/return/",views.sale_return,name="sale_return"),path("customers/",views.customer_list,name="customer_list"),path("customers/add/",views.customer_create,name="customer_create"),path("customers/<int:pk>/edit/",views.customer_update,name="customer_update"),path("reports/",views.reports,name="reports")]
