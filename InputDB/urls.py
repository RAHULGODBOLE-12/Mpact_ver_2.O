from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from portfolio.views import *
from InputDB.views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('import/topbom/GSM', import_top_bom_gsm, name='GSM_Top_BOM_Import'),
    path('import/topbom/CMM', import_top_bom_cmm, name='CMM_Top_BOM_Import'),
    path('import/historical_data', historical_data, name='Historical_Data'),
    path('import/historical_data_jpe', historical_data_jpe, name='Historical_Data_JPE'),
    path('import/npischedule', npischedule, name='npischedule_data'),
    path('Index/<str:team>', top_bom, name='Top_BOM'),
    path('delete_sgd_part/<str:id>', delete_sgd_part, name='delete_sgd_part'),
    path('delete_jpe_part/<str:id>', delete_jpe_part, name='delete_jpe_part'),
    path('delete_fgn_part/<str:id>', delete_fgn_part, name='delete_fgn_part'),

    path('refresh_top_bom', top_bom_refresh, name='Top_BOM_Refresh_SGD'),
    path('refresh_top_bom_fgn', top_bom_refresh_fgn, name='Top_BOM_Refresh_FGN'),

    path('refresh_npi_sgd', npi_refresh_sgd, name='NPI_refresh_SGD'),
    path('refresh_npi_jpe', npi_refresh_jpe, name='NPI_refresh_JPE'),
    path('refresh_top_bom_JPE', top_bom_refresh_jpe, name='Top_BOM_Refresh_JPE'),
    path('getqtrdata/<str:team>', top_bom_quarterwise, name='Top_BOM_Qtr_Data'),

    path('top_bom_addpart_sgd/', top_bom_addpart_sgd, name='top_bom_addpart_sgd'),
    path('top_bom_addpart_jpe/', top_bom_addpart_jpe, name='top_bom_addpart_jpe'),
    path('top_bom_addpart_fgn/', top_bom_addpart_fgn, name='top_bom_addpart_fgn'),

    path('bulkupload_jpe/', bulkupload_jpe, name='bulkupload_jpe'),
    path('bulkupload_sgd/', bulkupload_sgd, name='bulkupload_sgd'),
    path('bulkupload_fgn/', bulkupload_fgn, name='bulkupload_fgn'),

    path('new_basefile_sgd/', new_basefile_sgd, name='new_basefile_sgd'),
    path('new_basefile_jpe/', new_basefile_jpe, name='new_basefile_jpe'),
    path('new_basefile_fgn/', new_basefile_fgn, name='new_basefile_fgn'),

    path('compare_agile_sgd_basefile', compare_agile_sgd_basefile, name='compare_agile_sgd_basefile'),
    path('compare_agile_jpe_basefile', compare_agile_jpe_basefile, name='compare_agile_jpe_basefile'),
    path('compare_agile_fgn_basefile', compare_agile_fgn_basefile, name='compare_agile_fgn_basefile'),

    path('refreshbase/Production/<str:team>', refresh_base_file_prod_forecast, name='Top_BOM_Refresh_Base_Prod_Forecast'),
    path('addparts/Production/<str:team>', add_parts_production, name='Top_BOM_Add_Parts_Prod_Forecast'),
    path('addparts/NPI/<str:team>', add_parts_npi, name='Top_BOM_Add_Parts_NPI_Forecast'),
    path('refreshbase/NPI/<str:team>', refresh_base_file_npi_forecast, name='Top_BOM_Refresh_Base_NPI_Forecast'),
    path('Freeze/<str:team>', freezetopbom, name='Freeze_Top_BOM'),
    path('UnFreeze/<str:team>', unfreezetopbom, name='Unfreeze_Top_BOM'),
    path('History/<str:team>', Download_History, name='Download_History'),
    path('AlternateParts/<str:partno>/<str:assy>', Alternate_Parts, name='Alternate_Parts'),
    path('upload/production/parts/<str:cm>', update_production_forecast_part, name='update_production_forecast_part'),
    path('add/production/parts/<str:cm>', add_production_forecast_part, name='add_production_forecast_part'),
    path('download/<str:cm>', download_template, name='download_template'),



]
