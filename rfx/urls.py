from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from portfolio import json_for_table
from django.contrib.auth.decorators import login_required
from rfx import json_for_table
from rfx.views import *

urlpatterns = [
    path('quote_page/', quote_page, name="quote_page"),
    path('quote_page/his_parts/', his_parts, name="his_parts"),
    # path('quote_page/his_parts_filtered/<str:status>', his_parts_filtered, name="his_parts_filtered"),
    path('quote_page/this_part_quote_page/', this_part_quote_page, name="this_part_quote_page"),
    path('quote_page/make_quote/<str:action>', make_quote, name="make_quote"),
    path('quote_page/download_upload_quote/<str:action>', download_upload_quote, name="download_upload_quote"),
    path('quote_page/file_serve', file_serve, name="file_serve"),
    ####Analysis page
    path('Analysis_page/<str:team>/', Analysis_page, name="Analysis_page"),
    path('Analysis_page/table/json', login_required(json_for_table.Analysis_data.as_view()), name="Analysis_data"),
    path('Analysis_page/history/table/json/<str:id>', history, name="rfx_history"),
    path('Analysis_page/set/manual_split_set/', manual_split_set, name="manual_split_set"),
    path('Analysis_page/set/cm_manual_split_set/', cm_manual_split_set, name="cm_manual_split_set"),
    path('Analysis_page/set/comment/', Comments, name="Comments"),
    path('Analysis_page/filter/excel/',excel_filter,name='rfx_excel_filter'),
    path('Analysis_page/filter/saved/',save_predefined_filters,name='rfx_save_predefined_filters'),

    path('Analysis_page/CMM/price_bench_marking/', price_bench_marking, name="price_bench_marking"),
    path('Analysis_page/filter/advancefilter/<str:Team>/<str:section>/<str:field>/',advance_filter,name='rfx_advance_filter'),
    path('Analysis_page/download/<str:Team>', download_rfx, name="download_rfx"),
    path('Analysis_page/upload/split/', upload_split, name="Analysis_upload_split"),
    path('split_share/', shared_status_change, name="shared_status_change"),
    path('CM_Quoting/', CM_Quoting, name="CM_Quoting"),
    path('upload_cm_quote/', upload_cm_quote, name="upload_cm_quote"),
    path('cm_quote_analysis/', cm_quote_analysis, name="cm_quote_analysis"),
    ]