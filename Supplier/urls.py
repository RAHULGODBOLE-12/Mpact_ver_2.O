from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Supplier.views import *

from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('supplierdetail/contactbase/<str:Team>', contactlist, name="contactlist"),
    path('supplierdetail/data', contactlist_data, name="contactlist_data"),
    path('importdetail/<str:action>', import_contact, name="import_contact"),
	path('template/download/',download_massupload_template, name="download_massupload_template")
    
    ]