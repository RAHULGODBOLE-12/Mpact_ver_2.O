
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
path('portfolio/agile_refresh/',agile_refresh, name="agile_refresh"),
path('portfolio/filter/advancefilter/<str:Team>/<str:section>/<str:field>/',advance_filter,name='portfolio_advance_filter'),
path('portfolio/<str:team>',portfolio,name='portfolio'),
path('file_operations/<str:operation>/', file_operations, name="portfolio_file_operations"),
path('portfolio/download/<str:Team>',download_portfolio_kickstart, name="download_portfolio_kickstart"),
path('render_portfolio/', render_portfolio, name="render_portfolio"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)