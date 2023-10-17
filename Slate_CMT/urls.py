
from django.contrib import admin
from django.urls import path, include
from Slate_CMT.views import *
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "InESS Backend Administration"
admin.site.site_title = "InESS Admin Portal"
admin.site.index_title = "Welcome to InESS Backend"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', logins, name='logins'),
    path('accounts/logout/',logout_view,name='logout'),
    path('accounts/',logins,name='logins'),
    path('',home,name='home'),
    path('RFX/', include('rfx.urls')),
    path('portfolio/',include('portfolio.urls')),
    path('supplier/',include('Supplier.urls')),
    path('Master_pricing/',include('MasterPricing.urls')),
    path('login_via_admin/user/<int:id>', login_via_admin, name="login_via_admin"),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
