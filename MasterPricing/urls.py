from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MasterPricing.views import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Index', master_pricing_index, name='Master_Pricing_Index'),
    path('extras', extras, name='MP_extras'),
    path('masterpartlistsidebar', masterpartlistsidebar, name='masterpartlistsidebar'),
    path('update_price_decision', update_price_decision, name='update_price_decision'),
    path('price_approval', price_approval, name='price_approval'),
    path('apply_filter_masterpricing', apply_filter_masterpricing, name='apply_filter_masterpricing'),
    path('partdetails/Arista/<str:id>', part_details_arista, name='part_details_arista'),
    #path('partdetails/Arista/RFX/<str:id>', part_details_arista_rfx, name='part_details_arista_rfx'),
    path('partdetails/CM/<str:id>', part_details_cm, name='part_details_cm'),
    path('Refresh/Quote/<str:id>', refresh_quote_from_rfx, name='refresh_quote_from_rfx'),
    path('download_excel/<str:file_name>', download_excel, name='download_excel'),
    path('update_masterpricing', update_masterpricing, name='update_masterpricing'),
    path('upload/', upload, name='upload'),
    path('download_approval/<str:cm>', download_approval, name='download_approval'),
    path('MP_instance_download/<str:cm>', MP_instance_download, name='MP_instance_download'),
    path('MP_Updater_status/', MP_Updater_status, name='MP_Updater_status'),
    path('upload_po_receipt', upload_po_receipt, name='upload_po_receipt'),
	path('download_receipt_sample_files/<str:Team>/',download_receipt_template, name='download_receipt_template'),
    path('quote_page/file_instruction', file_instruction, name="file_instruction"),
    path('sisence', sisense_update, name="sisense_update"),
    path('test_po_del_logic', test_po_del_logic, name="test_po_del_logic"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
