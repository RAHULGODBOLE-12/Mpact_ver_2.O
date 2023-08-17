from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from portfolio import json_for_table
from django.contrib.auth.decorators import login_required
from rfx import json_for_table
from rfx.views import *