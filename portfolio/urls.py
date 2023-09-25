
from django.contrib import admin
from django.urls import path
from portfolio.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from portfolio import json_for_table

urlpatterns = [

path('portfolio/<str:team>',portfolio,name='portfolio'),
path('portfolio/json/', login_required(json_for_table.Portfolio_data.as_view()), name="Portfolio_data"),
path('top_component/download/<str:file>', download_portfolio, name="download_portfolio"),
path('portfolio/agile_refresh/',file_operations, name="agile_refresh"),
path('portfolio/filter/advancefilter/<str:Team>/<str:section>/<str:field>/',advance_filter,name='advance_filter'),
path('file_operations/<str:operation>/', file_operations, name="portfolio_file_operations"),
path('portfolio/download/<str:Team>',file_operations, name="download_portfolio_kickstart"),
path('render_portfolio/', render_portfolio, name="render_portfolio"),
path('get_data/', get_data, name="get_data"),
path('portfolio_action', portfolio_action, name="portfolio_action"),
path('portfolio/send_rfx/',send_rfx_input,name='send_rfx'),
path('portfolio/distributor_selection/',distributor_selection, name="distributor_selection"),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)