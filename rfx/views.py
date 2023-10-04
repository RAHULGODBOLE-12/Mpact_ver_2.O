from rfx.models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
# Create your views here.
from django.http import HttpResponse, Http404
from django.http import HttpResponse, Http404
from portfolio.models import *
from django.http import JsonResponse, HttpResponse
from Slate_CMT.templatetags.cmt_helper import *
from django.core.mail import EmailMessage
from django.template.loader import get_template
import random
import string
import os
from django.conf import settings
import pandas as pd
from django.db.models import Q
import numpy as np
import operator
from django.db.models import Q
from functools import reduce
from Supplier.models import suppliers_detail
from io import BytesIO
# from History.models import *
# from .json_for_table import approval_status
from django.contrib.sites.shortcuts import get_current_site
import json
import pytz
from datetime import timedelta
import datetime
from functools import reduce
import logging
from django.core.files.storage import FileSystemStorage
from django.db.models import Value as V
from django.db.models.functions import Concat   
# from rfx.models import Apply_split
from django.db.models import Avg

import os
from django.utils import timezone
LOGGER = logging.getLogger(__name__)


@login_required
def quote_page(request):
    '''Static page for Quoting portal'''
    LOGGER.info(f'Quote Page Open by {request.user.first_name} {request.user.last_name}')
    auto_clean_rfx_cm()
    return render(request, 'rfx/quote_page.html')


@login_required
def his_parts(request):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    This will return a list of parts to the user based on the persmission,
    pic will get the data which has the name in arista_pic col.
    and Manufacture will get the data where the name matchs in mfr_name columns
    superadmin will get all the data with current quarter
    *filter parameter is option to apply quote status field on the final query set
    *Mfr_Name parameter is option to apply Mfr_Name  field on the final query set
    '''
    if has_permission(request.user, 'Super User') or request.user.is_superuser or 'Director' in request.user.groups.values_list('name', flat=True):
        parts_GSM = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='GSM Team').order_by('Part_Number').exclude(sent_to='cm')
        parts_CMM = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').order_by('Part_Number').exclude(sent_to='cm')

    else:
        

        if has_permission(request.user,'CMM') or has_permission(request.user,'GSM'):
            parts_GSM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).exclude(sent_to='cm').filter(Team='GSM Team').filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('Part_Number')
            parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).exclude(sent_to='cm').filter(Team='CMM Team').filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('Part_Number')

        elif has_permission(request.user,'JPE Contract Manufacturer'):
            parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').filter(cm='JPE').filter(sent_to='cm').order_by('Part_Number')
            parts_GSM=RFX.objects.none()
        elif has_permission(request.user,'SGD Contract Manufacturer'):
            parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').filter(cm='SGD').filter(sent_to='cm').order_by('Part_Number')
            parts_GSM=RFX.objects.none()
        elif has_permission(request.user,'FGN Contract Manufacturer'):
            parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').filter(cm='FGN').filter(sent_to='cm').order_by('Part_Number')
            parts_GSM=RFX.objects.none()
        elif has_permission(request.user,'HBG Contract Manufacturer'):
            parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').filter(cm='HBG').filter(sent_to='cm').order_by('Part_Number')
            parts_GSM=RFX.objects.none()
        elif has_permission(request.user,'JSJ Contract Manufacturer'):
            parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').filter(cm='JSJ').filter(sent_to='cm').order_by('Part_Number')
            parts_GSM=RFX.objects.none()
        elif has_permission(request.user,'JMX Contract Manufacturer'):
            parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').filter(cm='JMX').filter(sent_to='cm').order_by('Part_Number')
            parts_GSM=RFX.objects.none()
        elif suppliers_detail.objects.filter(user_model__email__iexact=request.user.email).exists():
            distributor_name=suppliers_detail.objects.filter(user_model=request.user)

            # supplier_data=suppliers_detail.objects.filter(user_model__email__iexact=request.user.email,is_active=True)
            # print(distributor_name)
            # print(supplier_data)
            # parts_GSM=RFX.objects.filter(sent_quater=Current_quarter(),sent_to='supplier',quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='GSM Team').order_by('Part_Number').filter(Mfr_Name__in=suppliers_detail.objects.filter(user_model__email__iexact=request.user.email,is_active=True).values_list('Supplier_Name',flat=True))
            # print(parts_GSM)
            # print(is_distributor(request.user),'is_distributor(request.user)')
            # if is_distributor(request.user):
            #     try:
            #         distributor_name=distributor_name.exclude(Distributor='').filter(Distributor__isnull=False,user_model__is_active=True)[0].Distributor
            #         print(distributor_name,'distributor_name',supplier_data.filter(Distributor__isnull=True))

            #         parts_GSM=RFX.objects.filter(Team='GSM Team').filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).order_by('Part_Number').filter(Q(Mfr_Name__in=supplier_data.filter(Distributor__isnull=True).values_list('Supplier_Name',flat=True)) | Q(sent_to__icontains=distributor_name))
            #         parts_CMM=RFX.objects.filter(Team='CMM Team').filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).order_by('Part_Number').filter(Q(Mfr_Name__in=supplier_data.filter(Distributor__isnull=True).values_list('Supplier_Name',flat=True)) | Q(sent_to__icontains=distributor_name))
            #     except Exception as e:

            #         LOGGER.error("Is distributor Log", exc_info=1)
            #         parts_CMM=RFX.objects.filter(Team='CMM Team').filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).order_by('Part_Number').filter(Mfr_Name__in=supplier_data.values_list('Supplier_Name',flat=True)).exclude(sent_to='cm')
            #         LOGGER.error(f"Is distributor parts_CMM: {parts_CMM}")
            # else:
            #     parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(2,this_quarter=True)).filter(Team='CMM Team').order_by('Part_Number').filter(Mfr_Name__in=supplier_data.values_list('Supplier_Name',flat=True)).exclude(sent_to='cm')
            # print(parts_GSM,parts_CMM)
            data=his_quotes_rfx(request.user)
            parts_GSM=data.filter(Team='GSM Team').order_by('Part_Number')
            parts_CMM=data.filter(Team='CMM Team').order_by('Part_Number')
            #print(parts_GSM,parts_CMM)
        else:
            parts_CMM = RFX.objects.none()
            parts_GSM = RFX.objects.none()

    Mfr_names = set(list(parts_GSM.values_list('Mfr_Name', flat=True).distinct())+list(parts_CMM.values_list('Mfr_Name', flat=True).distinct()))
    if request.GET.get('filter_parameter'):
        #print(request.GET.get('filter_parameter'))
        #print(request.GET.get('value'))
        parts_CMM = parts_CMM.filter(**{request.GET.get('filter_parameter'): request.GET.get('value')})
        parts_GSM = parts_GSM.filter(**{request.GET.get('filter_parameter'): request.GET.get('value')})

    if request.GET.get('Mfr_Name'):
        #print(request.GET)

        parts_CMM = parts_CMM.filter(**{'Mfr_Name': request.GET.get('Mfr_Name')})
        parts_GSM = parts_GSM.filter(**{'Mfr_Name': request.GET.get('Mfr_Name')})
    request.session['session_quote_parts'] = list(set(list(parts_CMM.values_list('id', flat=True))+list(parts_GSM.values_list('id', flat=True))))

    try:
        parts_CMM = parts_CMM.values_list('Part_Number', 'id', 'Quote_status', 'quote_is_writable', 'cm')
    except:
        LOGGER.error("LOG_MESSAGE", exc_info=1)

    try:
        parts_GSM = parts_GSM.values_list('Part_Number', 'id', 'Quote_status', 'quote_is_writable', 'cm')
    except:
        LOGGER.error("LOG_MESSAGE", exc_info=1)


    return render(request,'rfx/components/parts_sidebar.html',context={
        'parts':[parts_GSM.filter(~Q(RFX_id=None)),parts_CMM.filter(~Q(RFX_id=None)),],
        'Mfr_names':Mfr_names,
        'selected_Mfr_name':request.GET.get('Mfr_Name'),
    })

# @login_required
#     if has_permission(request.user,'Super User') or request.user.is_superuser or 'Director' in request.user.groups.values_list('name',flat=True):
#         parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).filter(Team='CMM Team').order_by('Part_Number').exclude(sent_to='cm')

#     else:
#         if suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user).exists():
#             distributor_name=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user)[0].Distributor
#             # supplier_data=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user).values_list('Supplier_Name')
#             supplier_data=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model__email=request.user.email).values_list('Supplier_Name')
#             parts_GSM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).filter(Team='GSM Team').order_by('Part_Number').filter(Mfr_Name__in=supplier_data)
#             parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).filter(Team='CMM Team').order_by('Part_Number').filter(Mfr_Name__in=supplier_data).exclude(sent_to='cm')
#             if distributor_name:
#                 parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).filter(Team='CMM Team').order_by('Part_Number').filter(Q(Mfr_Name__in=supplier_data)&Q(sent_to__icontains=distributor_name.replace('distributor_to_','')))
#         elif has_permission(request.user,'CMM') or has_permission(request.user,'GSM'):
#             parts_GSM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).exclude(sent_to='cm').filter(Team='GSM Team').filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('Part_Number')
#             parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).exclude(sent_to='cm').filter(Team='CMM Team').filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('Part_Number')

#         elif has_permission(request.user,'JPE Contract Manufacturer'):
#             parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).filter(Team='CMM Team').filter(cm='JPE').filter(sent_to='cm').order_by('Part_Number')
#             parts_GSM=RFX.objects.none()
#         elif has_permission(request.user,'SGD Contract Manufacturer'):
#             parts_CMM=RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter(1)[0]).filter(Team='CMM Team').filter(cm='SGD').filter(sent_to='cm').order_by('Part_Number')
#             parts_GSM=RFX.objects.none()
#         else:
#             parts_CMM=RFX.objects.none()
#             parts_GSM=RFX.objects.none()

#     try:parts_CMM=parts_CMM.values_list('Part_Number','id','Quote_status')
#     except:pass
#     try:parts_GSM=parts_GSM.values_list('Part_Number','id','Quote_status')
#     except:pass
#     if request.GET.get('filter_parameter'):
#         print(request.GET.get('filter_parameter'))
#         print(request.GET.get('value'))
#         parts_CMM=parts_CMM.filter(**{request.GET.get('filter_parameter'):request.GET.get('value')})
#         parts_GSM=parts_GSM.filter(**{request.GET.get('filter_parameter'):request.GET.get('value')})
#     parts_CMM=parts_CMM.filter(Quote_status=status)
#     parts_GSM=parts_GSM.filter(Quote_status=status)

#     return render(request,'rfx/components/parts_sidebar.html',context={'parts':[parts_GSM.filter(~Q(RFX_id=None))
#     ,parts_CMM.filter(~Q(RFX_id=None))
#     ,]})


@login_required
def download_upload_quote(request, action=''):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    This will return a file of parts to the user based on the permission,
    pic will get the data which has the name in arista_pic col.
    and Manufacture will get the data where the name matchs in mfr_name columns
    superadmin will get all the data with current quarter
    action == 'Download':
        will return  excel with date to quote for supplier based on the above critira
    action == 'Download_cm':
        will return  excel with date to quote for cm based on the above critira
    elif action == 'Upload':
        This will get the excel as input and update the quote based on the id for supplier
    elif action == 'Upload_cm':
        This will get the excel as input and update the quote based on the id for cm
    
    '''
    status = request.GET.get('status')
    Inco_Term = ["CFR", "CIF", "CIP", "CPT", "DAF", "DAP", "DAT", "DDP", "DDU", "DEQ",
                 "DES", "EXG", "EXW", "FAS", "FCA", "FH", "FOB", "FOC", "FOR", "FOT", "FRD", "HC","N/A" ]
    Lifecycle_Phase = ["EOL", "Active", "Obsolete"]
    column_names = {
        "id": "RFQ Id",
        "quarter": 'Quarter',
        "Part_Number": 'Part Number',
        "Mfr_Name": 'Manufacturer Name',
        "cm": 'Global/Regional',
        "portfolio__Lifecycle_Phase": 'Arista Lifecycle phase',
        "portfolio__Rev": 'Revision',
        "portfolio__Mfr_Name": 'Portfolio Manufacturer Name',
        "portfolio__Mfr_Part_Lifecycle_Phase": 'Manufacturer Lifecycle phase',
        "portfolio__Mfr_Part_Number": 'Portfolio Manufacturer Part Number',
        "portfolio__Qualification_Status": 'Arista Qualification status',
        "portfolio__cm_Part_Number": 'CM Part Number',
        "portfolio__Arista_Part_Number": 'Arista Part Number',
        "Annual Demand": "Annual Demand",
        "portfolio__Cust_consign": 'Cust Consigned',
        "portfolio__Item_Desc": 'Item Description',
        "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand": 'Quarterly Demand',
        "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista": 'Required Quantity',
        "portfolio__Original_PO_Delivery_sent_by_Mexico": 'PO / Delivery',
        "portfolio__Ownership": 'Ownership',
        "Quote_Type": 'Quote Type',
        "portfolio__Arista_PIC": 'Arista PIC',
        "previous_Item_price": 'Current Quarter Item Price',
        "previous_lead_time": 'Current Quarter Lead Time (In Weeks)',
        "previous_moq": 'Current Quarter MOQ',
        "suggested_moq": 'Suggested MOQ',
        "portfolio__Arista_pic_comment": 'Arista pic comment',
        "Item_Price": 'Item Price ($) *',
        "Lead_Time": 'Lead Time (in weeks) *',
        "MOQ": 'MOQ *',
        "List": 'List',
        "tarrif": 'Tariff',
        "COO": 'COO *',
        "Inco_Term": 'Inco Term *',
        "NCNR": 'NCNR',
        "PO_Delivery": 'PO/Delivery *',
        "Freight_cost": 'Freight Cost ($)',
        "soft_hard_tool": 'Soft/Hard Tool',
        "Life_Cycle": 'Life Cycle',
        "Quote_status": 'Quote Status',
        "Comments": 'Comments',
        "sent_to": 'Sent To',
        "created_on": 'RFQ Raised on (US/Pacific)',
        "quote_freeze": 'Status',
        'due_date':'Due date (US/Pacific)'
    }

    # "portfolio__Parts_controlled_by":'Parts_controlled_by',
    # "Region":'Region',
    # "Geo":'Geo',

    column_names_cm = {
        "id": "RFQ Id",
        "quarter": 'quarter',
        "Part_Number": 'Arista Part Number',
        "cm": 'cm',
        "portfolio__cm_Part_Number": 'CM Part Number',
        "portfolio__Cust_consign": 'Cust Consign',
        "portfolio__Item_Desc": 'Item Desc',
        "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand": 'Quarterly Demand',
        "Annual Demand": "Annual Demand",
        "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista": 'Delta Demand.',
        "portfolio__Original_PO_Delivery_sent_by_Mexico": 'Original PO Delivery',
        "portfolio__Ownership": 'Ownership',
        "previous_Item_price": 'Previous quarter Item Price ($)',
        "previous_lead_time": 'Previous Quarter Lead time (In Weeks)',
        "previous_moq": 'Previous Quarter MOQ',
        "suggested_moq": 'Suggested MOQ',
        "Quote_Type": 'Quote Type',
        "portfolio__Arista_PIC": 'Arista PIC',
        "portfolio__Arista_pic_comment": 'Arista pic comment',
        "Item_Price": 'Item Price ($) *',
        "Lead_Time": 'CM MFG Lead time (in weeks) *',
        "MOQ": 'CM MOQ *',
        "List": 'List',
        "tarrif": 'Tariff',
        "NCNR": 'CM NCNR',
        "PO_Delivery": 'CM MPN PO/Delivery *',
        'CM_Manufacturer': 'CM Manufacturer Name *',
        "Supplier_Distributor_name_from_cm": 'CM Supplier / Distributor Name *',
        "CM_mpn": 'CM MPN *',
        "CM_buyer": 'CM Buyer Name *',
        "CM_qty_std_source": 'Current Qtr Std Cost Source',
        'Quote_status': 'Quote Status',
        "Comments": 'CM Comments',

        # "Mfr_Name":'Mfr Name',
        # "COO":'COO',
        # "Inco_Term":'Inco Term',
        # "Freight_cost":'Freight cost ($)',
        # "soft_hard_tool":'Soft/Hard tool',
        # "Region":'Region',
        # "Geo":'Geo',
        # "Life_Cycle":'Life Cycle',
        # "portfolio__Lifecycle_Phase":'Lifecycle Phase',
        # "portfolio__Rev":'Rev',
        # "portfolio__Mfr_Name":'Mfr Name',
        # "portfolio__Mfr_Part_Lifecycle_Phase":'Mfr Part Lifecycle Phase',
        # "portfolio__Mfr_Part_Number":'Mfr Part Number',
        # "portfolio__Qualification_Status":'Qualification Status',
        # "portfolio__Arista_Part_Number":'Arista Part Number',
        # "portfolio__Parts_controlled_by":'Parts controlled by',

    }

    if action == 'Download':
        if request.user.is_superuser or 'Director' in request.user.groups.values_list('name', flat=True) or 'Super User' in request.user.groups.values_list('name', flat=True):
            parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).order_by('id')
            #print(parts)

        else:
            if suppliers_detail.objects.filter(user_model=request.user).exists():
                parts=his_quotes_rfx(request.user)

            elif has_permission(request.user,'CMM') or has_permission(request.user,'GSM'):

                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(
                    portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('Part_Number')

            else:
                parts=RFX.objects.none()
        parts=parts.exclude(RFX_id__isnull=True).exclude(sent_to='cm').filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(1,this_quarter=True))
        if request.GET.get('award_letter'):
            return download_award(request,parts.values_list('id',flat=True),supplier=True)

        try:
            parts = parts.filter(id__in=request.session['session_quote_parts']).order_by('id')
        except:
            if status != 'All' and status != None:
                parts = parts.filter(Quote_status=status).order_by('id')
        columns = [
            "id",
            "quarter",
            "Part_Number",
            "Mfr_Name",
            "cm",
            "portfolio__Lifecycle_Phase",
            "portfolio__Rev",
            "portfolio__Mfr_Name",
            "portfolio__Mfr_Part_Lifecycle_Phase",
            "portfolio__Mfr_Part_Number",
            "portfolio__Qualification_Status",
            # "portfolio__cm_Part_Number",
            "portfolio__Arista_Part_Number",
            "portfolio__Cust_consign",
            # "portfolio__Parts_controlled_by",
            "portfolio__Item_Desc",
            "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
            "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
            "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "portfolio__Original_PO_Delivery_sent_by_Mexico",
            "portfolio__Ownership",
            "portfolio__Arista_PIC",
            "portfolio__Arista_pic_comment",
            "Item_Price",
            "Lead_Time",
            "Lead_Time",
            "List",
            "tarrif",
            "COO",
            'MOQ',
            "Inco_Term",
            "NCNR",
            "PO_Delivery",
            "Freight_cost",
            "soft_hard_tool",
            "Quote_Type",
            # "Region",
            # "Geo",
            "Life_Cycle",
            "Quote_status",
            "Comments",
            "sent_to",
            "created_on",
            "quote_freeze",
            "due_date",
        ]

        data = parts.order_by('Part_Number').values(*columns).to_dataframe()
        data.loc[data['portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista'] >= 0, 'portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista'] = 0
        data['portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista'] = abs( data['portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista'])
        try:
            data['sent_to'] = data['sent_to'].str.replace( 'distributor_to_', '')
        except:
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        data.insert(13, "Annual Demand",
                    data["portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand"] +
                    data["portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"] +
                    data["portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"] +
                    data["portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand"])

        try:
            data['suggested_moq']=None
            # data['suggested_moq']=data.apply(lambda x:suggested_moq(x['portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand']),axis=1)
        except:
            data['suggested_moq'] = None
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        data.drop([
            "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
            "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
        ], inplace=True, axis=1)
        data['previous_moq'] = None
        data['previous_lead_time'] = None
        data['previous_Item_price'] = None
        for index, row in data.iterrows():
            print(row['Part_Number'])
            try:
                previous_qtr=RFX.objects.filter(sent_quater=get_previous_quarter()[0],sent_to=row['sent_to'],Part_Number=row['Part_Number'],Mfr_Name=row['Mfr_Name'],portfolio__Ownership=row['portfolio__Ownership'],portfolio__Mfr_Part_Number=row['portfolio__Mfr_Part_Number'])[:1].get()
                condition = (data['sent_to']==row['sent_to']) & (data['Part_Number']==row['Part_Number']) & (data['Mfr_Name']==row['Mfr_Name']) & (data['portfolio__Ownership']==row['portfolio__Ownership']) & (data['portfolio__Mfr_Part_Number']==row['portfolio__Mfr_Part_Number'])
                data.loc[condition, 'previous_moq'] = previous_qtr.MOQ
                data.loc[condition, 'previous_lead_time'] = previous_qtr.Lead_Time
                data.loc[condition, 'previous_Item_price'] = previous_qtr.Item_Price
            except:
                pass
        #try:
        #    data['previous_moq'] = data.apply(lambda x: previous_values('MOQ', x['Part_Number'], x["Mfr_Name"], x['portfolio__Ownership'],x['sent_to'],x['portfolio__Mfr_Part_Number']), axis=1)
        #    data['previous_lead_time'] = data.apply(lambda x: previous_values('Lead_Time', x['Part_Number'], x["Mfr_Name"], x['portfolio__Ownership'],x['sent_to'],x['portfolio__Mfr_Part_Number']), axis=1)
        #    data['previous_Item_price'] = data.apply(lambda x: previous_values('Item_Price', x['Part_Number'], x["Mfr_Name"], x['portfolio__Ownership'],x['sent_to'],x['portfolio__Mfr_Part_Number']), axis=1)
        #except:
        #    data['previous_moq'] = None
        #    data['previous_lead_time'] = None
        #    data['previous_Item_price'] = None
        #    LOGGER.error("LOG_MESSAGE", exc_info=1)

        field=[k for k,v in column_names.items() ]
        #print(field)
        data = data.filter(field)
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        data['created_on'] = data['created_on'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).replace(tzinfo=None))
        data['created_on'] = pd.to_datetime(data['created_on']).dt.date
        # data['due_date'] = data['due_date'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).replace(tzinfo=None))
        # data['due_date'] = pd.to_datetime(data['due_date']).dt.date
        data.loc[data['quote_freeze'] == True, 'quote_freeze'] = 'Closed'
        data.loc[data['quote_freeze'] == False, 'quote_freeze'] = 'Open'
        #print(pd.to_datetime(data['created_on']).dt.date)
        data.rename(columns=column_names, inplace=True)
        # alias=["RFX Id","Quarter","Part Number","Manufacturer Name","Global/Regional","Arista Lifecycle phase","Revision","Portfolio Manufacturer Name","Manufacturer Lifecycle phase","Manufacturer Part Number","Arista Qualification status","CM Part Number","Arista Part Number","Cust Consigned","Item Description","Annual Demand","Quarterly Demand","Delta Demand","PO / Delivery","Ownership","Arista PIC","Item Price ($) *","Lead Time (in weeks) *",'MOQ *',"List","Tarrif","COO *","Inco Term *","NCNR","PO/Delivery *","Freight Cost ($) *","Soft/Hard Tool","Quote Type","Life Cycle *","Quote Status","Comments *"]
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                data.to_excel(writer, index=False, sheet_name='Submit Quote', startrow=1)

                workbook = writer.book
                worksheet = writer.sheets['Submit Quote']
                merge_format1 = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#e6e6ff'})
                merge_format2 = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#ccfff5'})

                worksheet.merge_range('D1:Z1', 'Part Description(Read only)', merge_format1)
                worksheet.merge_range('AA1:AN1', 'Submit your quote details here', merge_format2)
                num = {'validate': 'decimal',
                       'criteria': 'between',
                       'minimum': 0,
                       'maximum': 10000000000000.0,
                       'input_title': 'Enter the values:',
                       'input_message': 'Use only Numerics',
                       'error_title': 'Input value not valid!',
                       'error_message': 'It should be decimal',
                       }
                worksheet.data_validation('AA3:AC1048576', num)
                worksheet.data_validation('AJ3:AJ1048576', num)
                worksheet.data_validation('AH3:AH1048576', {'validate': 'list',
                                                            'source': RFX.val_NCNR,
                                                            })

                worksheet.data_validation('AI3:AI1048576', {'validate': 'list',
                                                            'source': RFX.val_PO_Delivery,
                                                            })
                worksheet.data_validation('AK3:AK1048576', {'validate': 'list',
                                                            'source': RFX.val_soft_hard_tool,

                                                            })
                worksheet.data_validation('AF3:AF1048576', {'validate': 'list',
                                                            'source': RFX.val_COO,
                                                            })
                worksheet.data_validation('AG3:AG1048576', {'validate': 'list',
                                                            'source': RFX.val_Inco_Term,
                                                            })
                worksheet.data_validation('AL3:AL1048576', {'validate': 'list',
                                                            'source': RFX.val_Life_Cycle,
                                                            })
                worksheet.data_validation('AM3:AM1048576', {'validate': 'list',
                                                            'source': ['No BID', 'Non Quoted', 'Quoted', ],
                                                            })
                # worksheet.data_validation('AI3:AI1048576', {'validate': 'list',
                #                     'source': RFX.val_Region,
                #                     })
                # worksheet.data_validation('AJ3:AJ1048576', {'validate': 'list',
                #                     'source': RFX.val_Geo,
                #                     })
                writer.save()
                response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'inline; filename="Submit Quote.xlsx"'
                return response
    elif action == 'Download_cm':
        if request.user.is_superuser or 'Director' in request.user.groups.values_list('name', flat=True) or 'Super User' in request.user.groups.values_list('name', flat=True):
            parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(
                3, this_quarter=True)).filter(Team='CMM Team', sent_to='cm').order_by('id')
        else:
            if suppliers_detail.objects.filter(is_active=True,user_model__is_active=True, user_model=request.user).exists():
                distributor_name = suppliers_detail.objects.filter(is_active=True,user_model__is_active=True, user_model=request.user)[0].Distributor
                supplier_data = suppliers_detail.objects.filter(is_active=True,user_model__is_active=True, user_model=request.user).values_list('Supplier_Name')
                #print(supplier_data)
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).order_by('Part_Number').filter(Mfr_Name__in=supplier_data)
                if distributor_name:
                    parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(
                        Team='CMM Team').order_by('Part_Number').filter(RFX_id__icontains=f"_to_distributor_to_{distributor_name}")
                else:
                    parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(
                        Team='CMM Team').order_by('Part_Number').filter(Q(Mfr_Name__in=supplier_data) & Q(sent_to=f"supplier"))
            elif has_permission(request.user, 'CMM') or has_permission(request.user, 'GSM'):

                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(
                    portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('Part_Number')
            elif has_permission(request.user, 'JPE Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JPE').filter(sent_to='cm').order_by('Part_Number')
            elif has_permission(request.user, 'JSJ Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JSJ').filter(sent_to='cm').order_by('Part_Number')
            elif has_permission(request.user, 'JMX Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JMX').filter(sent_to='cm').order_by('Part_Number')
            elif has_permission(request.user, 'SGD Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='SGD').filter(sent_to='cm').order_by('Part_Number')
            elif has_permission(request.user, 'FGN Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='FGN').filter(sent_to='cm').order_by('Part_Number')
            elif has_permission(request.user, 'HBG Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='HBG').filter(sent_to='cm').order_by('Part_Number')

            
            else:
                parts=RFX.objects.none()

        if status!='All' and status!=None:
            parts=parts.filter(Quote_status=status)

        columns_cm=[
                "id",
                "quarter",
                "Part_Number",
                # "Mfr_Name",
                "cm",
                "portfolio__cm_Part_Number",
                # "portfolio__Arista_Part_Number",
                "portfolio__Cust_consign",
                "portfolio__Item_Desc",
                "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
                "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
                "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
                "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
                "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
                "portfolio__Original_PO_Delivery_sent_by_Mexico",
                "portfolio__Ownership",
                "portfolio__Arista_PIC",
                "Item_Price",
                "Lead_Time",
                "MOQ",
                "List",
                "tarrif",
                "NCNR",
                "PO_Delivery",
                "CM_Manufacturer",
                "Supplier_Distributor_name_from_cm",
                "CM_mpn",
                # "CM_buyer",
                # "CM_qty_std_source",
                "Quote_Type",
                "Quote_status",
                "Comments",
                ]

                #"portfolio__Lifecycle_Phase",
                #"portfolio__Rev",
                #"portfolio__Mfr_Name",
                #"portfolio__Mfr_Part_Lifecycle_Phase",
                #"portfolio__Mfr_Part_Number",
                #"portfolio__Qualification_Status",
                #"portfolio__Parts_controlled_by",
                #"Region",
                #"Geo",

        data=parts.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(1,this_quarter=True)).order_by('Part_Number').values(*columns_cm).to_dataframe()
        data.portfolio__Mfr_Name='NA'
        data.portfolio__Mfr_Part_Number='NA'
        data.insert (9, "Annual Demand",
                                        data["portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand"]+
                                        data["portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"]+
                                        data["portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"]+
                                        data["portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand"])
        try:
            data['suggested_moq']=None
            # data['suggested_moq']=data.apply(lambda x:suggested_moq(x['portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand']),axis=1)
        except:
            data['suggested_moq'] = None
            LOGGER.error("LOG_MESSAGE", exc_info=1)
        data.drop([
            "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
            "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
        ], inplace=True, axis=1)
        data['previous_moq'] = None
        data['previous_lead_time'] = None
        data['previous_Item_price'] = None
        for index, row in data.iterrows():
            try:
                previous_qtr=RFX.objects.filter(sent_quater=get_previous_quarter()[0],sent_to=row['sent_to'],Part_Number=row['Part_Number'],Mfr_Name=row['Mfr_Name'],portfolio__Ownership=row['portfolio__Ownership'],portfolio__Mfr_Part_Number=row['portfolio__Mfr_Part_Number'])[:1].get()
                condition = (data['sent_to']==row['sent_to']) & (data['Part_Number']==row['Part_Number']) & (data['Mfr_Name']==row['Mfr_Name']) & (data['portfolio__Ownership']==row['portfolio__Ownership']) & (data['portfolio__Mfr_Part_Number']==row['portfolio__Mfr_Part_Number'])
                data.loc[condition, 'previous_moq'] = previous_qtr.MOQ
                data.loc[condition, 'previous_lead_time'] = previous_qtr.Lead_Time
                data.loc[condition, 'previous_Item_price'] = previous_qtr.Item_Price
            except:
                pass
        #try:
        #    data['previous_moq'] = data.apply(lambda x: previous_values('MOQ', x['Part_Number'], x["Mfr_Name"], x['portfolio__Ownership'],x['sent_to'],x['portfolio__Mfr_Part_Number']), axis=1)
        #    data['previous_lead_time'] = data.apply(lambda x: previous_values('Lead_Time', x['Part_Number'], x["Mfr_Name"], x['portfolio__Ownership'],x['sent_to'],x['portfolio__Mfr_Part_Number']), axis=1)
        #    data['previous_Item_price'] = data.apply(lambda x: previous_values('Item_Price', x['Part_Number'], x["Mfr_Name"], x['portfolio__Ownership'],x['sent_to'],x['portfolio__Mfr_Part_Number']), axis=1)
        #except Exception as e:
            #print(e)
        #    data['previous_moq'] = None
        #    data['previous_lead_time'] = None
        #    data['previous_Item_price'] = None
        #    LOGGER.error("LOG_MESSAGE", exc_info=1)

        field=[k for k,v in column_names_cm.items() ]
        #print(field)
        data=data.filter(field)
        data.rename(columns=column_names_cm,inplace=True)
        
        cmquote_data = CM_Quotes.objects.filter(rfq_id__in=data["RFQ Id"].values.tolist())
        cm_quotes_columns = {
            "Item_Price": 'Item Price ($) *',
            "Lead_Time": 'CM MFG Lead time (in weeks) *',
            "MOQ": 'CM MOQ *',
            "List": 'List',
            "tarrif": 'Tariff',
            "NCNR": 'CM NCNR',
            "PO_Delivery": 'CM MPN PO/Delivery *',
            'CM_Manufacturer': 'CM Manufacturer Name *',
            "Supplier_Distributor_name_from_cm": 'CM Supplier / Distributor Name *',
            "CM_mpn": 'CM MPN *',
            'rfq_id':'RFQ Id',
            'suggested_split':'suggested_split',
            'manual_split':'manual_split',
            'split_type':'split_type'
        }
        field = [k for k, v in cm_quotes_columns.items()]
        cmquote_data = pd.DataFrame(cmquote_data.values(*field))
        cmquote_data.rename(columns=cm_quotes_columns,inplace=True)
        cmquote_data['RFQ Id']=cmquote_data['RFQ Id'].astype(int)
        cm_quote_exists = data[data['RFQ Id'].isin(set(cmquote_data["RFQ Id"].values.tolist()))]
        cm_quote_not_exists = data[~data['RFQ Id'].isin(set(cmquote_data["RFQ Id"].values.tolist()))]
        cm_quote_not_exists["Business Split %"] = None
        cm_quote_exists=pd.merge(data, cmquote_data, on='RFQ Id', how='right')
        cm_quote_exists['Item Price ($) *_x']=cm_quote_exists['Item Price ($) *_y']
        cm_quote_exists['CM MFG Lead time (in weeks) *_x']=cm_quote_exists['CM MFG Lead time (in weeks) *_y']
        cm_quote_exists['CM MOQ *_x']=cm_quote_exists['CM MOQ *_y']
        cm_quote_exists['List_x']=cm_quote_exists['List_y']
        cm_quote_exists['Tariff_x']=cm_quote_exists['Tariff_y']
        cm_quote_exists['CM NCNR_x']=cm_quote_exists['CM NCNR_y']
        cm_quote_exists['CM MPN PO/Delivery *_x']=cm_quote_exists['CM MPN PO/Delivery *_y']
        cm_quote_exists['CM Manufacturer Name *_x']=cm_quote_exists['CM Manufacturer Name *_y']
        cm_quote_exists['CM Supplier / Distributor Name *_x']=cm_quote_exists['CM Supplier / Distributor Name *_y']
        cm_quote_exists['CM MPN *_x']=cm_quote_exists['CM MPN *_y']
        cm_quote_exists['Business Split %'] = cm_quote_exists.apply(lambda row: row['manual_split'] if row['split_type']=="Manual" else row['suggested_split'], axis=1)
        cm_quote_exists.drop(['Item Price ($) *_y','CM MFG Lead time (in weeks) *_y','CM MOQ *_y','List_y','Tariff_y','CM NCNR_y','CM MPN PO/Delivery *_y','CM Manufacturer Name *_y','CM Supplier / Distributor Name *_y','CM MPN *_y','suggested_split','manual_split','split_type'], axis=1,inplace=True)
        cm_quote_exists.rename(columns = {'Item Price ($) *_x':'Item Price ($) *','CM MFG Lead time (in weeks) *_x':'CM MFG Lead time (in weeks) *','CM MOQ *_x':'CM MOQ *','List_x':'List','Tariff_x':'Tariff','CM NCNR_x':'CM NCNR','CM MPN PO/Delivery *_x':'CM MPN PO/Delivery *','CM Manufacturer Name *_x':'CM Manufacturer Name *','CM Supplier / Distributor Name *_x':'CM Supplier / Distributor Name *','CM MPN *_x':'CM MPN *'}, inplace = True)
        data=pd.concat([cm_quote_not_exists,cm_quote_exists])
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                data.to_excel(writer, index=False,
                              sheet_name='Submit Quote', startrow=1)
                #print(data)

                workbook = writer.book
                worksheet = writer.sheets['Submit Quote']
                merge_format1 = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#e6e6ff'})
                merge_format2 = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#ccfff5'})

                worksheet.merge_range(
                    'D1:R1', 'Part Description(Read only)', merge_format1)
                worksheet.merge_range(
                    'S1:AE1', 'Submit your quote details here', merge_format2)
                num = {'validate': 'decimal',
                       'criteria': 'between',
                       'minimum': 0,
                       'maximum': 10000000000000.0,
                       'input_title': 'Enter the values:',
                       'input_message': 'Use only Numerics',
                       'error_title': 'Input value not valid!',
                       'error_message': 'It should be decimal',
                       }
                worksheet.data_validation('S3:U1048576', num)

                worksheet.data_validation('X3:X1048576', {'validate': 'list',
                                                          'source': RFX.val_NCNR,
                                                          })

                worksheet.data_validation('Y3:Y1048576', {'validate': 'list',
                                                          'source': RFX.val_PO_Delivery,
                                                          })

                worksheet.data_validation('AC3:AC1048576', {'validate': 'list',
                                                            'source': ['No BID', 'Non Quoted', 'Quoted', ],
                                                            })
                # worksheet.data_validation('AJ3:AJ1048576', {'validate': 'list',
                #                     'source': RFX.val_Region,
                #                     })
                # worksheet.data_validation('AK3:AK1048576', {'validate': 'list',
                #                     'source': RFX.val_Geo,
                #                     })
                writer.save()
                response = HttpResponse(
                    b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'inline; filename="Submit Quote CM.xlsx"'
                return response

    elif action == 'Upload':
        #print('into upload')
        column_names_decode = {v: k for k, v in column_names.items()}
        #print(column_names_decode)
        file = request.FILES['Upload_Excel']
        df = pd.read_excel(file, header=1,keep_default_na=False)
        df = df.replace({pd.np.nan: None})

        # print(df.columns)
        # print(len(column_names_decode),len(df.columns))
        # if len(column_names_decode)!=len(df.columns):
        #     return JsonResponse({'status':'Invalid','data':None})
        df.rename(columns=column_names_decode, inplace=True)
        if request.user.is_superuser or 'Director' in request.user.groups.values_list('name', flat=True):
            parts = RFX.objects.filter(sent_quater=Current_quarter(
            ), quarter__in=get_Next_quarter(3, this_quarter=True))
            #print(parts)

        elif suppliers_detail.objects.filter(is_active=True, user_model=request.user).exists():

                distributor_name=suppliers_detail.objects.filter(user_model=request.user,is_active=True)
                # supplier_data=suppliers_detail.objects.filter(user_model=request.user).values_list('Supplier_Name',flat=True)
                supplier_data=suppliers_detail.objects.filter(user_model__email__iexact=request.user.email,is_active=True).values_list('Supplier_Name',flat=True)
                #print(supplier_data)
                parts=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(3,this_quarter=True)).order_by('created_on').filter(Mfr_Name__in=supplier_data)
                if is_distributor(request.user):
                    try:
                        distributor_name=distributor_name.exclude(Distributor='').filter(Distributor__isnull=False)[0].Distributor
                        parts=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(3,this_quarter=True)).order_by('created_on').filter(reduce(operator.or_, (Q(sent_to__icontains=x) for x in [distributor_name.strip(),'supplier'])))
                    except:
                        parts=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(3,this_quarter=True)).order_by('created_on').filter(Q(Mfr_Name__in=supplier_data)&Q(sent_to=f"supplier"))
                else:
                    parts=RFX.objects.filter(sent_quater=Current_quarter(),quarter__in=get_Next_quarter(3,this_quarter=True)).order_by('created_on').filter(Q(Mfr_Name__in=supplier_data)&Q(sent_to=f"supplier"))
        elif has_permission(request.user,'CMM') or has_permission(request.user,'GSM'):

            parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(
                portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('created_on')

        else:
            parts = RFX.objects.none()
        # df=df.replace({pd.np.nan: None})
        parts = parts.filter(quote_freeze=False, quote_is_writable=True)
        #print(df.head())
        error_rows = []
        error_index = []
        success_count = 0
        filtered_df = df.dropna(subset=[
            "Item_Price",
            "Lead_Time",
            "MOQ",
            "COO",
            "Inco_Term",
            "PO_Delivery",
        ])
        filtered_df.drop(filtered_df.loc[filtered_df['COO']==""].index, inplace=True)
        filter_df2=df.loc[df['Quote_status'] == 'No BID']
        filtered_df=pd.concat([filtered_df,filter_df2])
        # filtered_df.append(filtered_df.loc[filtered_df['Quote_status']=='No BID'],ignore_index=True)
        filtered_df.drop_duplicates(subset=['id'],inplace=True)

        non_nan_list = filtered_df.index.tolist()
        list_of_id = []
        for index, row in filtered_df.iterrows():

            try:
                if row['Quote_status'] == 'No BID':
                    try:
                        data = parts.get(id=row['id'])
                    except:
                        raise ValueError("You Can't Quote for this part")
                        
                    if row['Comments'] == ' ' or row['Comments'] == '' or row['Comments'] == None:
                        raise ValueError("Comments mandatory for No BID parts")

                    #print(data.RFX_id)
                    data.Quote_status = 'No BID'
                    data.Comments = row['Comments']
                    data.save(user=request.user, Quote=True)
                    success_count += 1
                    #print('Saved')
                    list_of_id.append(data.id)

                else:
                    try:
                        data = parts.get(id=row['id'])
                    except:
                        raise ValueError("You Can't Quote for this part,Contact PIC")


                    data.Item_Price=row['Item_Price']
                    #print(data.Item_Price)
                    data.Lead_Time = row['Lead_Time']
                    data.MOQ = row['MOQ']
                    data.List = row['List']
                    data.tarrif = row['tarrif']
                    data.COO = row['COO']
                    data.Inco_Term = row['Inco_Term']
                    data.NCNR = row['NCNR']
                    data.PO_Delivery = row['PO_Delivery']
                    data.Freight_cost = row['Freight_cost']
                    data.soft_hard_tool = row['soft_hard_tool']
                    data.Quote_Type = row['Quote_Type']
                    # data.Region=row['Region']
                    # data.Geo=row['Geo']
                    data.Life_Cycle = row['Life_Cycle']
                    data.Quote_status = 'Quoted'
                    data.Comments = row['Comments']
                    data.save(user=request.user, Quote=True)
                    success_count += 1
                    #print('Saved')

                    list_of_id.append(data.id)

            except Exception as e:
                import traceback
                tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                #print(tb_str)

                error_rows.append(e)
                error_index.append(index)
                LOGGER.error("LOG_MESSAGE", exc_info=1)

        error2 = pd.DataFrame(error_rows, columns = ['Error'],index=error_index)
        error1=df[~df.index.isin(non_nan_list)].copy()
        error2=df[df.index.isin(error_index)].join(error2)
        error1['Error']='Fill the Required fields'
        error=error1.append(error2)
        column_re=list(error.columns)
        column_re.insert(0,column_re.pop(len(column_re)-1))
        error=error.filter(column_re)
        error=error.reset_index()
        #print('error',error)
        error['index']=error['index']+3
        error=error.replace({pd.np.nan:''})
        error.rename(columns={'index':'Excel row'},inplace=True)

        save_quote_notified_data(request, value=list_of_id, status='Quoted')

        if len(error)==0:
            return JsonResponse({'status':'success','success_count':success_count})
        else:
            del error['id']
            return JsonResponse({
                'status': 'error',
                'success_count': success_count,
                'error_table': error.rename(columns=column_names).to_html(index=False, justify='center', na_rep='', classes='compact table table-xs nowarp font-small-3 table-responsive table-striped text-nowarp')
            })
    elif action == 'Upload_cm':
        #print('into upload')
        column_names_decode = {v: k for k, v in column_names_cm.items()}
        file = request.FILES['Upload_Excel']
        df = pd.read_excel(file, header=1)
        df.rename(columns=column_names_decode, inplace=True)
        if request.user.is_superuser or 'Director' in request.user.groups.values_list('name', flat=True):
            parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='GSM Team').order_by('id')
        else:
            if suppliers_detail.objects.filter(is_active=True,user_model__is_active=True, user_model=request.user).exists():
                distributor_name = suppliers_detail.objects.filter(is_active=True,user_model__is_active=True, user_model=request.user)[0].Distributor
                supplier_data = suppliers_detail.objects.filter(is_active=True,user_model__is_active=True, user_model=request.user).values_list('Supplier_Name')
                #print(supplier_data)
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).order_by('created_on').filter(Mfr_Name__in=supplier_data)
                if distributor_name:
                    parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').order_by('created_on').filter(RFX_id__icontains=f"_to_distributor_to_{distributor_name}")
                else:
                    parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').order_by('created_on').filter(Q(Mfr_Name__in=supplier_data) & Q(sent_to=f"supplier"))
            elif has_permission(request.user, 'CMM') or has_permission(request.user, 'GSM'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('created_on')
            elif has_permission(request.user, 'JPE Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JPE').filter(sent_to='cm').order_by('created_on')
            elif has_permission(request.user, 'JSJ Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JSJ').filter(sent_to='cm').order_by('created_on')
            elif has_permission(request.user, 'JMX Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JMX').filter(sent_to='cm').order_by('created_on')
            elif has_permission(request.user, 'SGD Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='SGD').filter(sent_to='cm').order_by('created_on')
            elif has_permission(request.user, 'FGN Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='FGN').filter(sent_to='cm').order_by('created_on')
            elif has_permission(request.user, 'HBG Contract Manufacturer'):
                parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='HBG').filter(sent_to='cm').order_by('created_on')

            else:
                parts = RFX.objects.none()
        df = df.replace({pd.np.nan: None})
        #print(parts)
        error_rows = []
        error_index = []
        success_count = 0
        list_of_id=[]
        filtered_df = df.dropna(subset=[
            "Item_Price",
            "Lead_Time",
            "MOQ",
            "PO_Delivery",
            "CM_Manufacturer",
            "Supplier_Distributor_name_from_cm",
            "CM_mpn",
        ])

        filter_df2=df.loc[df['Quote_status'] == 'No BID']
        filtered_df=pd.concat([filtered_df,filter_df2])
        non_nan_list = filtered_df.index.tolist()
        filtered_df.drop_duplicates(subset=['id'],inplace=True)
        
        for index, row in filtered_df.iterrows():
            try:
                if row['Quote_status'] == 'No BID':
                    data = parts.get(id=row['id'])
                    data.Quote_status = 'No BID'
                    data.Comments = row['Comments']
                    data.save(user=request.user)
                    success_count += 1
                    #print('Saved')

                else:
                    data = parts.get(id=row['id'])
                    if data.sent_to=='cm':
                        if data.Item_Price!=round(float(row['Item_Price']), 5):
                            #print(f"data.Item_Price!=round(float(row['Item_Price']), 5):")
                            erase_mp(data)
                        elif data.Lead_Time != int(row['Lead_Time']):
                            #print(f"data.Lead_Time != row['Lead_Time']:")
                            erase_mp(data)
                        elif int(data.MOQ) != int(row['MOQ']):
                            #print(f"data.MOQ != row['MOQ']:")
                            erase_mp(data)
                        elif data.List != row['List']:
                            #print(f"data.List != row['List']:")
                            erase_mp(data)
                        elif data.tarrif != row['tarrif']:
                            #print(f"data.tarrif != row['tarrif']:")
                            erase_mp(data)
                        elif data.NCNR != row['NCNR']:
                            #print(f"data.NCNR != row['NCNR']:")
                            erase_mp(data)
                        elif data.PO_Delivery != row['PO_Delivery']:
                            #print(f"data.PO_Delivery != row['PO_Delivery']:")
                            erase_mp(data)
                        elif data.Quote_Type != row['Quote_Type']:
                            #print(f"data.Quote_Type != row['Quote_Type']:")
                            erase_mp(data)
                        elif data.Supplier_Distributor_name_from_cm != row['Supplier_Distributor_name_from_cm']:
                            #print(f"data.Supplier_Distributor_name_from_cm != row['Supplier_Distributor_name_from_cm']:")
                            erase_mp(data)
                        elif data.CM_mpn != row['CM_mpn']:
                            #print(f"data.CM_mpn != row['CM_mpn']:")
                            erase_mp(data)
                        elif data.Quote_Type != row['Quote_Type']:
                            #print(f"data.Quote_Type != row['Quote_Type']:")
                            erase_mp(data)
                        elif data.CM_Manufacturer != row['CM_Manufacturer']:
                            #print(f"data.CM_Manufacturer != row['CM_Manufacturer']:")
                            erase_mp(data)
                        else:
                            print('No changes')

                    data.Item_Price = round(float(row['Item_Price']), 5)
                    data.Lead_Time = row['Lead_Time']
                    data.MOQ = row['MOQ']
                    data.List = row['List']
                    data.tarrif = row['tarrif']
                    data.NCNR = row['NCNR']
                    data.PO_Delivery = row['PO_Delivery']
                    data.Quote_Type = row['Quote_Type']
                    # data.Region=row['Region']
                    # data.Geo=row['Geo']
                    data.Quote_status = 'Quoted'
                    data.Supplier_Distributor_name_from_cm = row['Supplier_Distributor_name_from_cm']
                    data.CM_mpn = row['CM_mpn']
                    # data.CM_buyer = row['CM_buyer']
                    # data.CM_qty_std_source = row['CM_qty_std_source']
                    data.Quote_Type = row['Quote_Type']
                    data.CM_Manufacturer = row['CM_Manufacturer']
                    data.Comments = row['Comments']
                    data.save(user=request.user,Quote=True)
                    success_count += 1
                    #print('Saved')
                    list_of_id.append(data.id)
            except Exception as e:
                error_rows.append(e)
                error_index.append(index)
                LOGGER.error("LOG_MESSAGE", exc_info=1)
        error2 = pd.DataFrame(error_rows, columns=['Error'], index=error_index)
        error1 = df[~df.index.isin(non_nan_list)].copy()
        error2 = df[df.index.isin(error_index)].join(error2)
        error1['Error'] = 'Fill the Required fields'
        error = error1.append(error2)
        column_re = list(error.columns)
        column_re.insert(0, column_re.pop(len(column_re)-1))
        error = error.filter(column_re)
        error = error.reset_index()
        #print('error', error)
        error['index'] = error['index']+3
        # error=error.replace({pd.np.nan:''})
        save_quote_notified_data(request, value=list_of_id, status='Quoted')
        if len(error) == 0:
            return JsonResponse({'status': 'success', 'success_count': success_count})
        else:
            return JsonResponse({
                'status': 'error',
                'success_count': success_count,
                'error_table': error.to_html(index=False, justify='center', na_rep='', classes='compact table table-xs nowarp font-small-3 table-responsive table-striped text-nowarp')
            })


# @login_required
# def download_filtered_quote(request,action,status):
#     Inco_Term=["CFR","CIF","CIP","CPT","DAF","DAP","DAT","DDP","DDU","DEQ","DES","EXG","EXW","FAS","FCA","FH","FOB","FOC","FOR","FOT","FRD","HC", ]
#     Lifecycle_Phase=["EOL","Active","Obsolete"]
#     column_names={
#             "RFX_id":"RFQ Id",
#             "quarter":'Quarter',
#             "Part_Number":'Part Number',
#             "Mfr_Name":'Manufacturer Name',
#             "cm":'Global/Regional',
#             "portfolio__Lifecycle_Phase":'Arista Lifecycle phase',
#             "portfolio__Rev":'Revision',
#             "portfolio__Mfr_Name":'Portfolio Manufacturer Name',
#             "portfolio__Mfr_Part_Lifecycle_Phase":'Manufacturer Lifecycle phase',
#             "portfolio__Mfr_Part_Number":'Portfolio Manufacturer Part Number',
#             "portfolio__Qualification_Status":'Arista Qualification status',
#             "portfolio__cm_Part_Number":'CM Part Number',
#             "portfolio__Arista_Part_Number":'Arista Part Number',
#             "portfolio__Cust_consign":'Cust Consigned',
#             "portfolio__Item_Desc":'Item Description',
#             "Annual Demand":"Annual Demand",
#             "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":'Quarterly Demand',
#             "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista":'Delta Demand',
#             "portfolio__Original_PO_Delivery_sent_by_Mexico":'PO / Delivery',
#             "portfolio__Ownership":'Ownership',
#             "portfolio__Arista_PIC":'Arista PIC',
#             "Item_Price":'Item Price ($) *',
#             "Lead_Time":'Lead Time (in weeks) *',
#             "MOQ":'MOQ *',
#             "List":'List',
#             "tarrif":'Tariff',
#             "COO":'COO *',
#             "Inco_Term":'Inco Term *',
#             "NCNR":'NCNR',
#             "PO_Delivery":'PO/Delivery *',
#             "Freight_cost":'Freight Cost ($) *',
#             "soft_hard_tool":'Soft/Hard Tool',
#             "Quote_Type":'Quote Type',
#             "Life_Cycle":'Life Cycle *',
#             "Quote_status":'Quote Status',
#             "Comments":'Comments',
#             "Arista pic comment":'portfolio__Arista_pic_comment',
#         }

#             #"portfolio__Parts_controlled_by":'Parts_controlled_by',
#             #"Region":'Region',
#             #"Geo":'Geo',

#     column_names_cm={
#             "RFX_id":"RFQ Id",
#             "quarter":'quarter',
#             "Part_Number":'Arista Part Number',
#             "Mfr_Name":'Mfr Name',
#             "cm":'cm',
#             "portfolio__Lifecycle_Phase":'Lifecycle Phase',
#             "portfolio__Rev":'Rev',
#             "portfolio__Mfr_Name":'Mfr Name',
#             "portfolio__Mfr_Part_Lifecycle_Phase":'Mfr Part Lifecycle Phase',
#             "portfolio__Mfr_Part_Number":'Mfr Part Number',
#             "portfolio__Qualification_Status":'Qualification Status',
#             "portfolio__cm_Part_Number":'CM Part Number',
#             "portfolio__Arista_Part_Number":'Arista Part Number',
#             "portfolio__Cust_consign":'Cust Consign',
#             "portfolio__Parts_controlled_by":'Parts controlled by',
#             "portfolio__Item_Desc":'Item Desc',
#             "Annual Demand":"Annual Demand",
#             "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":'Quarterly Demand',
#             "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista":'Delta Demand.',
#             "portfolio__Original_PO_Delivery_sent_by_Mexico":'Original PO Delivery',
#             "portfolio__Ownership":'Ownership',
#             "portfolio__Arista_PIC":'Arista PIC',
#             "Item_Price":'Item Price ($) *',
#             "Lead_Time":'CM MFG Lead time (in weeks) *',
#             "MOQ":'CM MOQ *',
#             "List":'List',
#             "tarrif":'Tariff',
#             "COO":'COO',
#             "Inco_Term":'Inco Term',
#             "NCNR":'CM NCNR',
#             "PO_Delivery":'CM MPN PO/Delivery *',
#             "Freight_cost":'Freight cost ($)',
#             "soft_hard_tool":'Soft/Hard tool',
#             "Quote_Type":'Quote Type',
#             "Region":'Region',
#             "Geo":'Geo',
#             "Life_Cycle":'Life Cycle',
#             'Quote_status':'Quote Status',
#             'CM_Manufacturer':'CM Manufacturer Name *',
#             "Supplier_Distributor_name_from_cm":'CM Supplier / Distributor Name *',
#             "CM_mpn":'CM MPN *',
#             "CM_buyer":'CM Buyer Name *',
#             "CM_qty_std_source":'Current Qtr Std Cost Source',
#             "Comments":'CM Comments',
#             "Arista pic comment":'portfolio__Arista_pic_comment',
#         }

#     if action=='Download_filtered':

#         if request.user.is_superuser or 'Director' in request.user.groups.values_list('name',flat=True):
#             parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Quote_status=status).order_by('id')
#             print(parts)

#         else:
#             if suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user).exists():
#                 distributor_name=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user)[0].Distributor
#                 supplier_data=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user).values_list('Supplier_Name',flat=True)
#                 print(supplier_data)
#                 parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Quote_status=status).order_by('created_on').filter(Mfr_Name__in=supplier_data)
#                 if distributor_name:
#                     parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Quote_status=status).order_by('created_on').filter(RFX_id__icontains=f"_to_distributor_to_{distributor_name}")
#                 else:
#                     parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Quote_status=status).order_by('created_on').filter(Q(Mfr_Name__in=supplier_data)&Q(sent_to=f"supplier"))
#             elif has_permission(request.user,'CMM') or has_permission(request.user,'GSM'):

#                 parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').filter(Quote_status=status).order_by('created_on')

#             else:
#                 parts=RFX.objects.none()
#         parts=parts.exclude(RFX_id__isnull=True).exclude(sent_to='cm').filter(quarter__in=get_Next_quarter(1,this_quarter=True))
#         print('new parts',parts)
#         columns=[
#                 "RFX_id",
#                 "quarter",
#                 "Part_Number",
#                 "Mfr_Name",
#                 "cm",
#                 "portfolio__Lifecycle_Phase",
#                 "portfolio__Rev",
#                 "portfolio__Mfr_Name",
#                 "portfolio__Mfr_Part_Lifecycle_Phase",
#                 "portfolio__Mfr_Part_Number",
#                 "portfolio__Qualification_Status",
#                 "portfolio__cm_Part_Number",
#                 "portfolio__Arista_Part_Number",
#                 "portfolio__Cust_consign",
#                 #"portfolio__Parts_controlled_by",
#                 "portfolio__Item_Desc",
#                 "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
#                 "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
#                 "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
#                 "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
#                 "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
#                 "portfolio__Original_PO_Delivery_sent_by_Mexico",
#                 "portfolio__Ownership",
#                 "portfolio__Arista_PIC",
#                 "Item_Price",
#                 "Lead_Time",
#                 "MOQ",
#                 "List",
#                 "tarrif",
#                 "COO",
#                 "Inco_Term",
#                 "NCNR",
#                 "PO_Delivery",
#                 "Freight_cost",
#                 "soft_hard_tool",
#                 "Quote_Type",
#                 #"Region",
#                 #"Geo",
#                 "Life_Cycle",
#                 "Quote_status",
#                 "Comments",
#                 'portfolio__Arista_pic_comment',

#                 ]

#         data=parts.values(*columns).to_dataframe()
#         data.insert (13, "Annual Demand",
#                                         data["portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand"]+
#                                         data["portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"]+
#                                         data["portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"]+
#                                         data["portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand"])
#         data.drop([
#             "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
#             "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
#             "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
#         ],inplace=True,axis=1)
#         data.rename(columns=column_names,inplace=True)
#         # alias=["RFX Id","Quarter","Part Number","Manufacturer Name","Global/Regional","Arista Lifecycle phase","Revision","Portfolio Manufacturer Name","Manufacturer Lifecycle phase","Manufacturer Part Number","Arista Qualification status","CM Part Number","Arista Part Number","Cust Consigned","Item Description","Annual Demand","Quarterly Demand","Delta Demand","PO / Delivery","Ownership","Arista PIC","Item Price ($) *","Lead Time (in weeks) *",'MOQ *',"List","Tarrif","COO *","Inco Term *","NCNR","PO/Delivery *","Freight Cost ($) *","Soft/Hard Tool","Quote Type","Life Cycle *","Quote Status","Comments *"]
#         with BytesIO() as b:
#             with pd.ExcelWriter(b) as writer:
#                 data.to_excel(writer,index=False,sheet_name='Submit Quote',startrow=1)

#                 workbook = writer.book
#                 worksheet = writer.sheets['Submit Quote']
#                 merge_format1 = workbook.add_format({
#                 'bold': 1,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'fg_color': '#e6e6ff'})
#                 merge_format2 = workbook.add_format({
#                 'bold': 1,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'fg_color': '#ccfff5'})


#                 worksheet.merge_range('D1:U1', 'Part Description(Read only)', merge_format1)
#                 worksheet.merge_range('V1:AJ1', 'Make Your Quote Here(Don"t fill no need columns)', merge_format2)
#                 num={'validate': 'decimal',
#                     'criteria': 'between',
#                     'minimum': 0,
#                     'maximum': 10000000000000.0,
#                     'input_title': 'Enter the values:',
#                     'input_message': 'Use only Numerics',
#                     'error_title': 'Input value not valid!',
#                     'error_message': 'It should be decimal',
#                                     }
#                 worksheet.data_validation('V3:X1048576', num)
#                 worksheet.data_validation('AE3:AE1048576',num )
#                 worksheet.data_validation('AC3:AC1048576', {'validate': 'list',
#                                     'source': RFX.val_NCNR,
#                                     })

#                 worksheet.data_validation('AD3:AD1048576', {'validate': 'list',
#                 'source': RFX.val_PO_Delivery,
#                 })
#                 worksheet.data_validation('AF3:AF1048576', {'validate': 'list',
#                 'source': RFX.val_soft_hard_tool,

#                 })
#                 worksheet.data_validation('AB3:AB1048576', {'validate': 'list',
#                 'source': RFX.val_Inco_Term,
#                 })
#                 worksheet.data_validation('AH3:AH1048576', {'validate': 'list',
#                                    'source': RFX.val_Life_Cycle,
#                                    })
#                 worksheet.data_validation('AI3:AI1048576', {'validate': 'list',
#                                     'source': ['No BID','Non Quoted','Quoted',],
#                                     })
#                 # worksheet.data_validation('AI3:AI1048576', {'validate': 'list',
#                 #                     'source': RFX.val_Region,
#                 #                     })
#                 # worksheet.data_validation('AJ3:AJ1048576', {'validate': 'list',
#                 #                     'source': RFX.val_Geo,
#                 #                     })
#                 writer.save()
#                 response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
#                 response['Content-Disposition'] = 'inline; filename="Submit Quote.xlsx"'
#                 return response

#     elif action=='Download_cm_filtered':
#         if request.user.is_superuser or 'Director' in request.user.groups.values_list('name',flat=True):
#             parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Team='CMM Team',sent_to='cm').filter(Quote_status=status).order_by('id')
#         else:
#             if suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user).exists():
#                 distributor_name=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user)[0].Distributor
#                 supplier_data=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,user_model=request.user).values_list('Supplier_Name')
#                 print(supplier_data)
#                 parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).order_by('created_on').filter(Mfr_Name__in=supplier_data).filter(Quote_status=status)
#                 if distributor_name:
#                     parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Team='CMM Team').order_by('created_on').filter(RFX_id__icontains=f"_to_distributor_to_{distributor_name}").filter(Quote_status=status)
#                 else:
#                     parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Team='CMM Team').order_by('created_on').filter(Q(Mfr_Name__in=supplier_data)&Q(sent_to=f"supplier")).filter(Quote_status=status)
#             elif has_permission(request.user,'CMM') or has_permission(request.user,'GSM'):

#                 parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}').order_by('created_on').filter(Quote_status=status)
#             elif has_permission(request.user,'JPE Contract Manufacturer'):
#                 parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Team='CMM Team').filter(cm='JPE').filter(sent_to='cm').order_by('created_on').filter(Quote_status=status)

#             elif has_permission(request.user,'SGD Contract Manufacturer'):
#                 parts=RFX.objects.filter(quarter__in=get_Next_quarter(3,this_quarter=True)).filter(Team='CMM Team').filter(cm='SGD').filter(sent_to='cm').order_by('created_on').filter(Quote_status=status)

#             else:
#                 parts=RFX.objects.none()

#         columns_cm=[
#                 "RFX_id",
#                 "quarter",
#                 "Part_Number",
#                 # "Mfr_Name",
#                 "cm",
#                 "portfolio__cm_Part_Number",
#                 # "portfolio__Arista_Part_Number",
#                 "portfolio__Cust_consign",
#                 "portfolio__Item_Desc",
#                 "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
#                 "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
#                 "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
#                 "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
#                 "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
#                 "portfolio__Original_PO_Delivery_sent_by_Mexico",
#                 "portfolio__Ownership",
#                 "portfolio__Arista_PIC",
#                 "Item_Price",
#                 "Lead_Time",
#                 "MOQ",
#                 "List",
#                 "tarrif",
#                 "NCNR",
#                 "PO_Delivery",
#                 "CM_Manufacturer",
#                 "Supplier_Distributor_name_from_cm",
#                 "CM_mpn",
#                 "CM_buyer",
#                 "CM_qty_std_source",
#                 "Quote_Type",
#                 "Quote_status",
#                 "Comments",
#                 ]

#                 #"portfolio__Lifecycle_Phase",
#                 #"portfolio__Rev",
#                 #"portfolio__Mfr_Name",
#                 #"portfolio__Mfr_Part_Lifecycle_Phase",
#                 #"portfolio__Mfr_Part_Number",
#                 #"portfolio__Qualification_Status",
#                 #"portfolio__Parts_controlled_by",
#                 #"Region",
#                 #"Geo",

#         data=parts.filter(quarter__in=get_Next_quarter(1,this_quarter=True)).values(*columns_cm).to_dataframe()
#         data.portfolio__Mfr_Name='NA'
#         data.portfolio__Mfr_Part_Number='NA'
#         data.insert (9, "Annual Demand",
#                                         data["portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand"]+
#                                         data["portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"]+
#                                         data["portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"]+
#                                         data["portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand"])
#         data.drop([
#             "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
#             "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
#             "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
#         ],inplace=True,axis=1)
#         data.rename(columns=column_names_cm,inplace=True)
#         #"Arista Lifecycle phase","Revision","Manufacturer Name","Manufacturer Lifecycle phase","Manufacturer Part Number","Arista Qualification status",
#         # alias_cm=["RFX Id","Quarter","Part Number","Manufacturer Name","CM","CM Part Number","Cust Consigned","Item Description","Annual Demand","Quarterly Demand","Delta Demand","PO / Delivery","Ownership","Arista PIC","Item Price ($) *","Lead Time (in weeks) *",'MOQ *',"NCNR","PO/Delivery *","CM Manufacturer *","Supplier/Distributor Name from CM *","CM MPN *","CM Buyer *","CM Qty Std. Source","Quote Type","Quote Status","Comments"]
#         with BytesIO() as b:
#             with pd.ExcelWriter(b) as writer:
#                 data.to_excel(writer,index=False,sheet_name='Submit Quote',startrow=1)
#                 print(data)

#                 workbook = writer.book
#                 worksheet = writer.sheets['Submit Quote']
#                 merge_format1 = workbook.add_format({
#                 'bold': 1,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'fg_color': '#e6e6ff'})
#                 merge_format2 = workbook.add_format({
#                 'bold': 1,
#                 'border': 1,
#                 'align': 'center',
#                 'valign': 'vcenter',
#                 'fg_color': '#ccfff5'})


#                 worksheet.merge_range('D1:M1', 'Part Description(Read only)', merge_format1)
#                 worksheet.merge_range('N1:Z1', 'Make Your Quote Here(Don"t fill no need columns)', merge_format2)
#                 num={'validate': 'decimal',
#                     'criteria': 'between',
#                     'minimum': 0,
#                     'maximum': 10000000000000.0,
#                     'input_title': 'Enter the values:',
#                     'input_message': 'Use only Numerics',
#                     'error_title': 'Input value not valid!',
#                     'error_message': 'It should be decimal',
#                                     }
#                 worksheet.data_validation('N3:P1048576', num)

#                 worksheet.data_validation('S3:S1048576', {'validate': 'list',
#                                     'source': RFX.val_NCNR,
#                                     })

#                 worksheet.data_validation('T3:T1048576', {'validate': 'list',
#                     'source': RFX.val_PO_Delivery,
#                     })

#                 worksheet.data_validation('AA3:AA1048576', {'validate': 'list',
#                                     'source': ['No BID','Non Quoted','Quoted',],
#                                     })
#                 # worksheet.data_validation('AJ3:AJ1048576', {'validate': 'list',
#                 #                     'source': RFX.val_Region,
#                 #                     })
#                 # worksheet.data_validation('AK3:AK1048576', {'validate': 'list',
#                 #                     'source': RFX.val_Geo,
#                 #                     })
#                 writer.save()
#                 response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
#                 response['Content-Disposition'] = 'inline; filename="Submit Quote.xlsx"'
#                 return response


# Quote form
@login_required
def this_part_quote_page(request):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    This will return the details for one part based on the id 
    sent_to == 'cm':
        This will return cm template
    else:
        will return supplier quote template

    '''
    Required = get_Next_quarter(q=1,this_quarter=True)
    id = request.GET.get('part')
    data = RFX.objects.get(id=id)
    Quotes = RFX.objects.filter(cm=data.cm,
                                Mfr_Name=data.Mfr_Name,
                                Mfr_Part_Number=data.Mfr_Part_Number,
                                Part_Number=data.Part_Number,
                                portfolio__Team=data.Team,
                                sent_to=data.sent_to,
                                sent_quater=Current_quarter()).filter(quarter__in=get_Next_quarter(q=1, this_quarter=True))
    user=User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name=data.portfolio.Arista_PIC.split('/')[0])
    if user:
        pic=user[0]
        award,created=Split_award.objects.get_or_create(user=pic) 

    previous_Quotes = RFX.objects.filter(
                                cm=data.cm,
                                Mfr_Name=data.Mfr_Name,
                                Mfr_Part_Number=data.Mfr_Part_Number,
                                Part_Number=data.Part_Number,
                                portfolio__Team=data.Team,
                                sent_to=data.sent_to,
                                sent_quater=get_previous_quarter()[0]).first()

    if data.sent_to == 'cm':
        if CM_Quotes.objects.filter(rfq_id=id).exists():
            cmquotes = CM_Quotes.objects.filter(rfq_id=id)
            cm_std_cost = cmquotes[:1].get().std_cost
            splits = split_for_cm_quote(id)
            for_std = [i['id'] for i in splits]
            print(CM_Quotes.objects.filter(id__in=for_std))
            po_del=cm_po_delivery_calc(CM_Quotes.objects.filter(id__in=for_std))
            print(po_del,"PO Del")
        else:
            cmquotes = CM_Quotes.objects.none()
            cm_std_cost = None
            po_del = None
        return render(request, 'rfx/components/quote_form_CMM_cm.html', context={'Quotes': Quotes, 'Required': Required,'previous_Quotes':previous_Quotes,'cmquotes':cmquotes,'cm_std_cost':cm_std_cost,'po_del':po_del})
    return render(request, 'rfx/components/quote_form.html', context={'Quotes': Quotes, 'Required': Required,'previous_Quotes':previous_Quotes})


@login_required
def make_quote(request, action):
    '''
    Type:Static Function
    Arg:request,action
    ####process#####:
    this will update the quote data from ui based on the roles
    action == 'quote':
        save the data based on rfx.id
    elif action=='Not_quote':
        this will set the rfx status to no_bid and update the comment
    

    '''

    if action == 'quote':
        form_data = request.POST
        id = form_data.getlist('id')
        Item_Price = form_data.getlist('Item_Price')
        Lead_Time = form_data.getlist('Lead_Time')
        MOQ = form_data.getlist('MOQ')
        List = form_data.getlist('List')
        tarrif = form_data.getlist('tarrif')
        COO = form_data.getlist('COO')
        Inco_Term = form_data.getlist('Inco_Term')
        MPQ = form_data.getlist('MPQ')
        Assembly_cost = form_data.getlist('Assembly_cost')
        Freight_cost = form_data.getlist('Freight_cost')
        Masked_Price = form_data.getlist('Masked_Price')
        Life_Cycle = form_data.getlist('Life_Cycle')
        Comments = form_data.getlist('Comments')
        NCNR = form_data.getlist('NCNR')
        PO_Delivery = form_data.getlist('PO_Delivery')
        soft_hard_tool = form_data.getlist('soft_hard_tool')
        #print(soft_hard_tool)

        CM_Manufacturer = form_data.getlist('CM_Manufacturer')
        Supplier_Distributor_name_from_cm = form_data.getlist('Supplier_Distributor_name_from_cm')
        CM_mpn = form_data.getlist('CM_mpn')
        # CM_buyer = form_data.getlist('CM_buyer')
        # CM_qty_std_source = form_data.getlist('CM_qty_std_source')

        permission_denied_quote = []
        LOGGER.info(f'Quote Page Login: {request.user.first_name} {request.user.last_name},{request.POST} ')

        permission_denied_quote=[]
        LOGGER.info(f'Quote Page Login: {request.user.first_name} {request.user.last_name},{request.POST} ')

        try:
            Region = form_data.getlist('Region') if form_data.getlist('Region') != [] else [None, None, None, None]
            Geo = form_data.getlist('Geo') if form_data.getlist('Geo') else [None, None, None, None]
        except:
            Region = [None, None, None, None]
            Geo = [None, None, None, None]
            LOGGER.error("LOG_MESSAGE", exc_info=1)
        if has_group(request.user,'Contract Manufacturer'):
            for q in range(len(id)):
                cm_quotes = CM_Quotes.objects.filter(rfq_id=id[q]).aggregate(LT=Avg('Lead_Time'),MQ=Avg('MOQ'))
                data = RFX.objects.get(id=id[q])
                if data.quote_is_writable:
                    if data.sent_to=='cm':
                        if data.Item_Price != Handel_Index_error(Item_Price,q,digit=True):
                            print(f'data.Item_Price != Handel_Index_error(Item_Price,q,digit=True):')
                            erase_mp(data)
                        elif data.Lead_Time != Handel_Index_error([str(cm_quotes['LT'])],q,digit=True):
                            print(f'data.Lead_Time != Handel_Index_error(Lead_Time,q,digit=False):')
                            erase_mp(data)
                        elif data.MOQ != Handel_Index_error([str(cm_quotes['MQ'])],q,digit=True):
                            print(f'data.MOQ != Handel_Index_error(MOQ,q,digit=False):')
                            erase_mp(data)
                        elif data.List != Handel_Index_error(List,q,digit=False):
                            print(f'data.List != Handel_Index_error(List,q,digit=False):')
                            erase_mp(data)
                        elif data.tarrif != Handel_Index_error(tarrif,q,digit=False):
                            print(f'data.tarrif != Handel_Index_error(tarrif,q,digit=False):')
                            erase_mp(data)
                        elif data.COO != Handel_Index_error(COO,q,digit=False):
                            print(f'data.COO != Handel_Index_error(COO,q,digit=False):')
                            erase_mp(data)
                        elif data.Inco_Term != Handel_Index_error(Inco_Term,q,digit=False):
                            print(f'data.Inco_Term != Handel_Index_error(Inco_Term,q,digit=False):')
                            erase_mp(data)
                        elif data.Freight_cost != Handel_Index_error(Freight_cost,q):
                            print(f'data.Freight_cost != Handel_Index_error(Freight_cost,q):')
                            erase_mp(data)
                        elif data.Life_Cycle != Handel_Index_error(Life_Cycle,q,digit=False):
                            print(f'data.Life_Cycle != Handel_Index_error(Life_Cycle,q,digit=False):')
                            erase_mp(data)
                        elif data.Comments != Handel_Index_error(Comments,q,digit=False):
                            print(f'data.Comments != Handel_Index_error(Comments,q,digit=False):')
                            erase_mp(data)
                        elif data.Region != Handel_Index_error(Region,q,digit=False):
                            print(f'data.Region != Handel_Index_error(Region,q,digit=False):')
                            erase_mp(data)
                        elif data.Geo != Handel_Index_error(Geo,q,digit=False):
                            print(f'data.Geo != Handel_Index_error(Geo,q,digit=False):')
                            erase_mp(data)
                        elif data.NCNR != Handel_Index_error(NCNR,q,digit=False):
                            print(f'data.NCNR != Handel_Index_error(NCNR,q,digit=False):')
                            erase_mp(data)
                        elif data.PO_Delivery != Handel_Index_error(PO_Delivery,q,digit=False):
                            print(f'data.PO_Delivery != Handel_Index_error(PO_Delivery,q,digit=False):')
                            erase_mp(data)
                        elif data.soft_hard_tool != Handel_Index_error(soft_hard_tool,q,digit=False):
                            print(f'data.soft_hard_tool != Handel_Index_error(soft_hard_tool,q,digit=False):')
                            erase_mp(data)
                        elif data.CM_Manufacturer != Handel_Index_error(CM_Manufacturer,q,digit=False):
                            print(f'data.CM_Manufacturer != Handel_Index_error(CM_Manufacturer,q,digit=False):')
                            erase_mp(data)
                        elif data.Supplier_Distributor_name_from_cm != Handel_Index_error(Supplier_Distributor_name_from_cm,q,digit=False):
                            print(f'data.Supplier_Distributor_name_from_cm != Handel_Index_error(Supplier_Distributor_name_from_cm,q,digit=False):')
                            erase_mp(data)
                        elif data.CM_mpn != Handel_Index_error(CM_mpn,q,digit=False):
                            print(f'data.CM_mpn != Handel_Index_error(CM_mpn,q,digit=False):')
                            erase_mp(data)
                        else:
                            print('No changes in quote')

                    data.Item_Price=Handel_Index_error(Item_Price,q,digit=True)
                    data.Lead_Time=Handel_Index_error([cm_quotes['LT']],q,digit=False)
                    data.MOQ=Handel_Index_error([cm_quotes['MQ']],q,digit=False)
                    data.List=Handel_Index_error(List,q,digit=False)
                    data.tarrif=Handel_Index_error(tarrif,q,digit=False)
                    data.COO=Handel_Index_error(COO,q,digit=False)
                    data.Inco_Term=Handel_Index_error(Inco_Term,q,digit=False)
                    data.Freight_cost=Handel_Index_error(Freight_cost,q)
                    data.Life_Cycle=Handel_Index_error(Life_Cycle,q,digit=False)
                    data.Comments=Handel_Index_error(Comments,q,digit=False)
                    data.Region=Handel_Index_error(Region,q,digit=False)
                    data.Geo=Handel_Index_error(Geo,q,digit=False)
                    data.NCNR=Handel_Index_error(NCNR,q,digit=False)
                    data.PO_Delivery=Handel_Index_error(PO_Delivery,q,digit=False)
                    data.soft_hard_tool=Handel_Index_error(soft_hard_tool,q,digit=False)
                    data.CM_Manufacturer=Handel_Index_error(CM_Manufacturer,q,digit=False)
                    data.Supplier_Distributor_name_from_cm=Handel_Index_error(Supplier_Distributor_name_from_cm,q,digit=False)
                    data.CM_mpn=Handel_Index_error(CM_mpn,q,digit=False)
                    # data.CM_buyer=Handel_Index_error(CM_buyer,q,digit=False)
                    # data.CM_qty_std_source=Handel_Index_error(CM_qty_std_source,q,digit=False)
                    data.Quote_status='Quoted'

                    if data.sent_to=='cm':
                        print('Cm Quote approved')
                    data.save(user=request.user, Quote=True)

                else:
                    permission_denied_quote.append(q)
        else:
            for q in range(len(id)):
                data = RFX.objects.get(id=id[q])
                if data.quote_is_writable:
                    if data.sent_to=='cm':
                        if data.Item_Price != Handel_Index_error(Item_Price,q,digit=True):
                            print(f'data.Item_Price != Handel_Index_error(Item_Price,q,digit=True):')
                            erase_mp(data)
                        elif data.Lead_Time != Handel_Index_error(Lead_Time,q,digit=True):
                            print(f'data.Lead_Time != Handel_Index_error(Lead_Time,q,digit=False):')
                            erase_mp(data)
                        elif data.MOQ != Handel_Index_error(MOQ,q,digit=True):
                            print(f'data.MOQ != Handel_Index_error(MOQ,q,digit=False):')
                            erase_mp(data)
                        elif data.List != Handel_Index_error(List,q,digit=False):
                            print(f'data.List != Handel_Index_error(List,q,digit=False):')
                            erase_mp(data)
                        elif data.tarrif != Handel_Index_error(tarrif,q,digit=False):
                            print(f'data.tarrif != Handel_Index_error(tarrif,q,digit=False):')
                            erase_mp(data)
                        elif data.COO != Handel_Index_error(COO,q,digit=False):
                            print(f'data.COO != Handel_Index_error(COO,q,digit=False):')
                            erase_mp(data)
                        elif data.Inco_Term != Handel_Index_error(Inco_Term,q,digit=False):
                            print(f'data.Inco_Term != Handel_Index_error(Inco_Term,q,digit=False):')
                            erase_mp(data)
                        elif data.Freight_cost != Handel_Index_error(Freight_cost,q):
                            print(f'data.Freight_cost != Handel_Index_error(Freight_cost,q):')
                            erase_mp(data)
                        elif data.Life_Cycle != Handel_Index_error(Life_Cycle,q,digit=False):
                            print(f'data.Life_Cycle != Handel_Index_error(Life_Cycle,q,digit=False):')
                            erase_mp(data)
                        elif data.Comments != Handel_Index_error(Comments,q,digit=False):
                            print(f'data.Comments != Handel_Index_error(Comments,q,digit=False):')
                            erase_mp(data)
                        elif data.Region != Handel_Index_error(Region,q,digit=False):
                            print(f'data.Region != Handel_Index_error(Region,q,digit=False):')
                            erase_mp(data)
                        elif data.Geo != Handel_Index_error(Geo,q,digit=False):
                            print(f'data.Geo != Handel_Index_error(Geo,q,digit=False):')
                            erase_mp(data)
                        elif data.NCNR != Handel_Index_error(NCNR,q,digit=False):
                            print(f'data.NCNR != Handel_Index_error(NCNR,q,digit=False):')
                            erase_mp(data)
                        elif data.PO_Delivery != Handel_Index_error(PO_Delivery,q,digit=False):
                            print(f'data.PO_Delivery != Handel_Index_error(PO_Delivery,q,digit=False):')
                            erase_mp(data)
                        elif data.soft_hard_tool != Handel_Index_error(soft_hard_tool,q,digit=False):
                            print(f'data.soft_hard_tool != Handel_Index_error(soft_hard_tool,q,digit=False):')
                            erase_mp(data)
                        elif data.CM_Manufacturer != Handel_Index_error(CM_Manufacturer,q,digit=False):
                            print(f'data.CM_Manufacturer != Handel_Index_error(CM_Manufacturer,q,digit=False):')
                            erase_mp(data)
                        elif data.Supplier_Distributor_name_from_cm != Handel_Index_error(Supplier_Distributor_name_from_cm,q,digit=False):
                            print(f'data.Supplier_Distributor_name_from_cm != Handel_Index_error(Supplier_Distributor_name_from_cm,q,digit=False):')
                            erase_mp(data)
                        elif data.CM_mpn != Handel_Index_error(CM_mpn,q,digit=False):
                            print(f'data.CM_mpn != Handel_Index_error(CM_mpn,q,digit=False):')
                            erase_mp(data)
                        else:
                            print('No changes in quote')

                    data.Item_Price=Handel_Index_error(Item_Price,q,digit=True)
                    data.Lead_Time=Handel_Index_error(Lead_Time,q,digit=False)
                    data.MOQ=Handel_Index_error(MOQ,q,digit=False)
                    data.List=Handel_Index_error(List,q,digit=False)
                    data.tarrif=Handel_Index_error(tarrif,q,digit=False)
                    data.COO=Handel_Index_error(COO,q,digit=False)
                    data.Inco_Term=Handel_Index_error(Inco_Term,q,digit=False)
                    data.Freight_cost=Handel_Index_error(Freight_cost,q)
                    data.Life_Cycle=Handel_Index_error(Life_Cycle,q,digit=False)
                    data.Comments=Handel_Index_error(Comments,q,digit=False)
                    data.Region=Handel_Index_error(Region,q,digit=False)
                    data.Geo=Handel_Index_error(Geo,q,digit=False)
                    data.NCNR=Handel_Index_error(NCNR,q,digit=False)
                    data.PO_Delivery=Handel_Index_error(PO_Delivery,q,digit=False)
                    data.soft_hard_tool=Handel_Index_error(soft_hard_tool,q,digit=False)
                    data.CM_Manufacturer=Handel_Index_error(CM_Manufacturer,q,digit=False)
                    data.Supplier_Distributor_name_from_cm=Handel_Index_error(Supplier_Distributor_name_from_cm,q,digit=False)
                    data.CM_mpn=Handel_Index_error(CM_mpn,q,digit=False)
                    # data.CM_buyer=Handel_Index_error(CM_buyer,q,digit=False)
                    # data.CM_qty_std_source=Handel_Index_error(CM_qty_std_source,q,digit=False)
                    data.Quote_status='Quoted'

                    if data.sent_to=='cm':
                        print('Cm Quote approved')
                    data.save(user=request.user, Quote=True)

                else:
                    permission_denied_quote.append(q)

        try:
            save_quote_notified_data(request, value=id, status='Quoted')
        except:
            LOGGER.error("LOG_MESSAGE", exc_info=1)


        return JsonResponse({'message':'Quote Updated','status':200}) if permission_denied_quote==[] else JsonResponse({'message':'You have no permission to quote','status':403})
    elif action=='Not_quote':
        ids=request.POST.getlist("id[]")
        Comment=request.POST.get("Comment")
        for id in ids:
            try:
                data = RFX.objects.get(id=id)
                if data.sent_to=='cm':
                    if data.Item_Price:
                        erase_mp(data)
                data.Quote_status = 'No BID'
                data.Comments = Comment
                data.Item_Price=None
                data.Lead_Time=None
                data.MOQ=None
                data.List=None
                data.tarrif=None
                data.COO=None
                data.Inco_Term=None
                data.Freight_cost=None
                data.Life_Cycle=None
                data.NCNR=None
                data.PO_Delivery=None
                data.soft_hard_tool=None
                data.save(user=request.user, Quote=True)
                Apply_split(data.Part_Number,data.Team,data.cm,data.sent_to)
            except Exception as e:
                LOGGER.error("LOG_MESSAGE", exc_info=1)

        return HttpResponse('Success')


@multi_threading
def create_rfx(request=None,parts=[],To=[],created_by=None,Quote_Type=None,Arista_pic_comment='',this=False,notification=True):
    '''
    Type:Static Function
    Arg:request=None,parts=[],To=[],created_by=None,Quote_Type=None,Arista_pic_comment='',this=False,notification=True
    ####process#####:
    * Logic here is to create and send rfx for part in 'parts' argument,
    * we send RFQ or only next quarter and current_quarter(optional)
    * we send RFQ as regional(ie.sgd,jpe,fgn,jmx,jsj,hbg) and global
    * The rfq are send based on the supplier page of the user who logged in
    * RFQ is created based on the  distributor is selected from the distributor selection box.
    * Multiple rfq will not be raised even accidentally
    * Rfq will not be raised for the parts which have no supplier and email will be notified about that incident
    * To identity if the quote is sent to distributor or supplier, the 'sent_to' column will be 'supplier' if supplier or the name of the distributor ie.'Avent' and cm will marked as 'cm'
    * Quote can't be raised as global and regional only one case is possible,it will abort the operation if tried
    * Every process will be intimated as mail if part raised,unraised or in case of error
    '''
    if not parts:
        return None
    logger=send_fx_queue_logger()
    logger.to_create_count=(len(parts)*len(To))*3
    logger.created_by=created_by
    Team=Portfolio.objects.get(id=parts[0]).Team
    Quarters=get_Next_quarter(q=1)
    print(Quarters)
    suppliers=[]
    suppliers_email=[]
    cms=[]
    portfolio_id_list = []
    suppliers_not_in_contact = []
    if this:
        Quarters=this
    due_date=None
    if request.POST.get('due_date') and request.POST.get('due_date')!='':
        due_date=request.POST.get('due_date')
        print(due_date)
    counter=0
    not_created=[]
    print(request.POST)
    if Team == 'GSM Team':
        # parts = Portfolio.objects.exclude(rfq_sent_flag_supplier='Quote Raised').filter(id__in=parts).values_list('id', flat=True)
        parts = check_rfx_global(Portfolio.objects.filter(id__in=parts).values_list('id', flat=True))
    for to in To:
        for quarter in Quarters:
            for part in parts:
                quotes_for_approved_part = 0
                data = Portfolio.objects.get(id=part)
                if request.user.is_superuser:
                    user_owner=User.objects.annotate(full_name=Concat('first_name', V(' '),'last_name')).filter(full_name=data.Arista_PIC)
                else:
                    user_owner=User.objects.none()
                print(data.Arista_PIC,user_owner)
                rfx_flag=False
                if to=='supplier':
                    # if quarter != Current_quarter():
                    #     data.rfq_sent_flag_supplier='Quote Raised'
                    rfx_flag=True
                    if Team=='GSM Team':
                        quotes_for_approved_part=RFX.objects.filter(sent_quater=Current_quarter(),quarter=quarter,approval_status='Approved',sent_to='supplier',Part_Number=data.Number,cm=data.cm).count()
                        print(quotes_for_approved_part)
                        
                elif to == 'cm':
                    # data.rfq_sent_flag_cm='Sent'
                    rfx_flag = True
                elif to == 'distributor':
                    # data.rfq_sent_flag_distributor='Sent'
                    rfx_flag=False

                if to=='distributor':
                    quotes_for_approved_part=RFX.objects.exclude(sent_to='cm').filter(sent_quater=Current_quarter(),quarter=quarter,approval_status='Approved',Part_Number=data.Number,cm=data.cm).count()
                    if request.user.is_superuser:
                        as_dist=suppliers_detail.objects.filter(Supplier_Name=data.Mfr_Name,is_active=True).filter(User_created__in=user_owner).exists()
                        suppliersss = suppliers_detail.objects.filter(Supplier_Name=data.Mfr_Name,is_active=True).filter(User_created__in=user_owner).distinct()
                    else:
                        as_dist=suppliers_detail.objects.filter(Supplier_Name=data.Mfr_Name,is_active=True).filter(User_created=request.user).exists()
                        suppliersss = suppliers_detail.objects.filter(Supplier_Name=data.Mfr_Name,is_active=True).filter(User_created=request.user).distinct()
                    print(as_dist)
                    if as_dist:
                        rfx_flag = False
                        # print(suppliers_detail.objects.filter(Supplier_Name=data.Mfr_Name).filter(Team=data.Team).distinct())
                        for dist in suppliersss:
                            print(dist.Distributor,request.POST)
                            if dist.Distributor==None:
                                rfx_flag=True
                            elif dist.Distributor in request.POST.getlist(f"{data.cm}__{data.Number}",[]):
                                RFX_id = f'''RFX_{Current_quarter()}_{quarter}_{data.cm}_{data.Mfr_Name}_{data.Mfr_Part_Number}_{data.Number}_{data.Team}_to_{to}_to_{dist.Distributor}'''
                                if to == 'supplier':
                                    q = [data.cm]
                                    query = reduce(operator.and_, (Q(
                                        RFX_id__icontains=f'RFX_{Current_quarter()}_{quarter}_{item}_{data.Mfr_Name}_{data.Mfr_Part_Number}_{data.Number}_{data.Team}_to_{"supplier" if to=="distributor" else to}') for item in q))
                                else:
                                    q = ['Global']
                                    query = reduce(operator.and_, (Q(RFX_id__icontains = f'RFX_{Current_quarter()}_{quarter}_{item}_{data.Mfr_Name}_{data.Mfr_Part_Number}_{data.Number}_{data.Team}_to_{to}_to_{dist.Distributor}') for item in q))
                                print(RFX.objects.filter(query).exists())
                                print('*'*100)
                                print(query,'query')
                                if not RFX.objects.filter(query).exists():
                                    try:
                                        print(RFX_id,'RFX_id')
                                        instance = RFX.objects.get(
                                            RFX_id__icontains=RFX_id)
                                        # print('Updating')
                                    except:
                                        counter += 1
                                        print('Creating')
                                        instance = RFX()
                                        LOGGER.error("LOG_MESSAGE", exc_info=1)

                                    instance.portfolio=data
                                    instance.created_by=created_by
                                    instance.sent_to=f'{dist.Distributor if dist.Distributor else "supplier"}'
                                    instance.quarter=quarter
                                    if data.cm== 'Global':
                                        instance.Quote_Type='Global'
                                    else:
                                        instance.Quote_Type = 'Regional'
                                    instance.Arista_pic_comment = Arista_pic_comment
                                    if request.user.is_superuser and not suppliers_detail.objects.filter(Supplier_Name=instance.portfolio.Mfr_Name,is_active=True, User_created__in=user_owner).exists():
                                        not_created.append(part)
                                        suppliers_not_in_contact.append(instance.portfolio.Mfr_Name)
                                    elif not request.user.is_superuser and not suppliers_detail.objects.filter(Supplier_Name=instance.portfolio.Mfr_Name,is_active=True, User_created=request.user).exists():
                                        not_created.append(part)
                                        suppliers_not_in_contact.append(instance.portfolio.Mfr_Name)
                                        # print('Not created')
                                    else:
                                        try:
                                            if quotes_for_approved_part:
                                                instance.quote_is_writable=False
                                                instance.quote_freeze=True
                                            instance.due_date=due_date
                                            instance.save()
                                        except:
                                            not_created.append(part)
                                            LOGGER.error("LOG_MESSAGE", exc_info=1)

                                        portfolio_id_list.append(instance.portfolio.id)
                                        if not to=='cm' :
                                            data.rfq_sent_flag_supplier=get_quote_status(data)
                                        suppliers.append(instance.portfolio.Mfr_Name)
                                        suppliers_email.append(dist.user_model.email)
                                        cms.append(instance.portfolio.cm)
                                        # print(instance.RFX_id)
                                        print(data)
                                        data.save()

                                else:
                                    not_created.append(part)
                                    # print('Not created')
                    else:
                        rfx_flag = True

                if to == 'cm':
                    print("Sending to Supplier")
                    if RFX.objects.filter(cm=data.cm, Part_Number=data.Number, sent_quater=Current_quarter(), quarter=quarter, portfolio__Ownership=data.Ownership, sent_to='cm').exists():
                        rfx_flag = False
                        print('cm Quote exists ', data.Number)
                if rfx_flag:
                    RFX_id = f'''RFX_{Current_quarter()}_{quarter}_{data.cm}_{data.Mfr_Name}_{data.Mfr_Part_Number}_{data.Number}_{data.Team}_to_{'supplier' if to=='distributor' else to}'''
                    # print(RFX_id)
                    # print(to)
                    if to == 'supplier':
                        q = [data.cm]
                        # send_logger_tele(f'{data.cm} {to}')
                        print("Test")
                        query = reduce(operator.and_, (Q(
                            RFX_id__icontains=f'RFX_{Current_quarter()}_{quarter}_{item}_{data.Mfr_Name}_{data.Mfr_Part_Number}_{data.Number}_{data.Team}_to_{"supplier" if to=="distributor" else to}') for item in q))
                    else:
                        q = ['Global']
                        query = reduce(operator.and_, (Q(
                            RFX_id__icontains=f'RFX_{Current_quarter()}_{quarter}_{item}_{data.Mfr_Name}_{data.Mfr_Part_Number}_{data.Number}_{data.Team}_to_{"supplier" if to=="distributor" else to}') for item in q))
                    # print(RFX.objects.filter(query))
                    if not RFX.objects.filter(query).exists():
                        try:
                            instance = RFX.objects.get(RFX_id__icontains=RFX_id)
                            # print('Updating ')
                        except:
                            print('Creating the quote without constrain')
                            instance = RFX()
                            LOGGER.error("LOG_MESSAGE", exc_info=1)
                        print('supplier' if to=='distributor' else to)
                        instance.portfolio=data
                        instance.created_by=created_by
                        instance.sent_to='supplier' if to=='distributor' else to
                        instance.quarter=quarter
                        if data.cm== 'Global':
                            instance.Quote_Type='Global'
                        else:
                            instance.Quote_Type = 'Regional'
                        instance.Arista_pic_comment = Arista_pic_comment
                        print(user_owner,suppliers_detail.objects.filter(Supplier_Name=instance.portfolio.Mfr_Name,is_active=True, User_created__in=user_owner))
                        if request.user.is_superuser and not suppliers_detail.objects.filter(Supplier_Name=instance.portfolio.Mfr_Name,is_active=True, User_created__in=user_owner).exists() and not to == 'cm':
                            not_created.append(part)
                            suppliers_not_in_contact.append(instance.portfolio.Mfr_Name)
                            print('Not created due to Superadmin supplier not there')
                        elif not request.user.is_superuser and not suppliers_detail.objects.filter(Supplier_Name=instance.portfolio.Mfr_Name,is_active=True, User_created=request.user).exists() and not to == 'cm':
                            not_created.append(part)
                            suppliers_not_in_contact.append(instance.portfolio.Mfr_Name)
                            print('Not created due to supplier not there')
                        elif RFX.objects.filter(cm__in=['Global'] if data.cm != 'Global' else ['SGD', 'JPE','FGN','HBG','JSJ','JMX'], Part_Number=data.Number, sent_quater=Current_quarter(), sent_to='supplier').exists():
                            not_created.append(part)
                            print('Not created due to Quote available')

                        else:
                            try:
                                if quotes_for_approved_part:
                                    instance.quote_is_writable=False
                                    instance.quote_freeze=True
                                instance.due_date=due_date
                                instance.save()
                            except:
                                not_created.append(part)
                                LOGGER.error("LOG_MESSAGE", exc_info=1)

                            portfolio_id_list.append(instance.portfolio.id)
                            print(get_quote_status(data),"Quote Status")
                            if not to=='cm':
                                data.rfq_sent_flag_supplier=get_quote_status(data)
                            if request.user.is_superuser:
                                suppliersss = suppliers_detail.objects.filter(Supplier_Name=instance.portfolio.Mfr_Name,Distributor__isnull=True,is_active=True).filter(User_created__in=user_owner).distinct('user_model__email').values_list('user_model__email',flat=True)
                            else:
                                suppliersss = suppliers_detail.objects.filter(Supplier_Name=instance.portfolio.Mfr_Name,Distributor__isnull=True,is_active=True).filter(User_created=request.user).distinct('user_model__email').values_list('user_model__email',flat=True)
                            for sup in suppliersss:
                                suppliers_email.append(sup)
                            suppliers.append(instance.portfolio.Mfr_Name)
                            cms.append(instance.portfolio.cm)
                            print(instance.RFX_id)
                            data.save()
                            previous_split_set(instance)
                    else:
                        not_created.append(part)
                        # print('Not created')

    cms=list(set(cms))

    portfolio_df = Portfolio.objects.filter(id__in=portfolio_id_list).values('Mfr_Name', 'Mfr_Part_Number', 'Arista_Part_Number', 'cm').to_dataframe()
    with BytesIO() as b:
        with pd.ExcelWriter(b) as writer:
            portfolio_df.to_excel(writer, index=False, sheet_name='Quote_Raised_Parts', header=['Mfr Name', 'Mfr Part Number', 'Arista Part Number', 'cm'])
            writer.close()
            file_MIME=b.getvalue()

    if 'cm' in To and cms:
        # quote_email_notification(request,created_by=created_by,suppliers=suppliers,suppliers_not_in_contact=suppliers_not_in_contact,Team=Team)
        quote_email_notification(request, created_by=created_by, suppliers=cms, suppliers_not_in_contact=[], Team=None, notification_to='cm')

    else:
        quote_email_notification(request, created_by=created_by, suppliers=suppliers, suppliers_not_in_contact=suppliers_not_in_contact, Team=Team, notification=notification, attachment=["RFQ Raised Parts.xlsx", file_MIME],suppliers_email=suppliers_email)
    logger.Created_count = counter
    logger.error = 'No Error' if not_created == [] else f'''rfq already existed for {not_created} '''
    #print('No Error' if not_created == [] else f'''rfq already existed for {not_created} ''')
    logger.save()
    if not 'cm' in To:
        send_push_notification(created_by, subject='Success,RFQ Has been sent,Check mail for Report of Unsent Quotes', text=f'RFQ has send for {counter}' if not_created == [] else f'''RFQ sent for {counter} parts,RFQ already existed for {len(not_created)} parts''', url='Analysis_page', args=[Team.replace(' Team', '')])

# Analysis
@login_required
def shared_status_change(request):
    status=request.GET.get('shared_status')
    #print(status)
    shared_status,created=Split_award.objects.get_or_create(user=request.user)
    if status:
        shared_status.share_award=True
    else:
        shared_status.share_award=False
    shared_status.save()
    return JsonResponse({'message':'done','status':200})


@error_handle
@login_required
def Analysis_page(request, team):
    shared_status,created=Split_award.objects.get_or_create(user=request.user)
    if team == 'GSM':
        Page_title = 'Quote Analysis GSM'
        Team = 'GSM Team'
        request.session['Check_box_analysis'] = []
        request.session['current_filtered_RFX'] = []
        Quarters = RFX.objects.filter(Team='GSM Team').exclude(sent_quater=Current_quarter()).distinct('sent_quater').values_list('sent_quater', flat=True)
        return render(request, 'rfx/rfx_analysis.html', {'Team': Team, 'Quarters': Quarters,"shared_status":shared_status})
    elif team == 'CMM':
        Page_title = 'Quote Analysis CMM'
        Team = 'CMM Team'
        request.session['current_filtered_RFX'] = []

        request.session['Check_box_analysis'] = []
        request.session['current_filtered_RFX'] = []
        Quarters = RFX.objects.filter(Team='GSM Team').exclude(
            sent_quater=Current_quarter()).distinct('sent_quater').values_list('sent_quater', flat=True)

        return render(request, 'rfx/rfx_analysis.html', {'Team': Team, 'Quarters': Quarters,"shared_status":shared_status})

    else:
        option = request.GET.get('option')
        #print(option, 'ss')
        if option == 'check_box':
            data = []
            try:
                #check_box = request.session['Check_box_analysis']
                if 'Check_box_analysis' not in request.session:
                    check_box = []
                else:
                    check_box = request.session['Check_box_analysis']
            except:
                request.session['Check_box_analysis'] = []
                check_box = []
                LOGGER.error("LOG_MESSAGE", exc_info=1)

            #print(request.GET['State'])

            if request.GET['State'] == 'true':
                check_box.append(int(request.GET['id']))

            elif request.GET['State'] == 'false':
                check_box.remove(int(request.GET['id']))

            else:
                pass

            request.session['Check_box_analysis'] = check_box
            request.session.modified = True
            return JsonResponse({'status': 200, 'selected': len(request.session.get('Check_box_analysis') or request.session.get('current_filtered_RFX'))}, safe=False)
        elif option == 'comments':
            comment = request.GET.get('comment')
            field = request.GET.get('field')
            id = request.GET.get('id')
            #print(comment, field, id)
            data = RFX.objects.get(id=int(id))
            #print(data)
            datas = RFX.objects.filter(quarter__in=get_Next_quarter(
                q=1, this_quarter=True), portfolio__Ownership=data.portfolio.Ownership, Part_Number=data.Part_Number)
            datas.update(**{field: comment})
            return JsonResponse({'status': 200, 'message': 'Comment Updated'}, safe=False)
        elif option == 'comments_mp':
            from MasterPricing.models import MP_download_table

            comment=request.GET.get('comment')
            cm=request.GET.get('cm')
            field=request.GET.get('field')
            id=request.GET.get('id')
            #print(comment,field,id)
            data=RFX.objects.get(id=int(id))
            datas=MP_download_table.objects.filter(Part_Number=data.Part_Number,Quarter=Current_quarter(),CM_download=cm)
            datas.update(**{field:comment})
            return JsonResponse({'status':200,'message':'Comment Updated'},safe=False)
        elif option=='quote_access_controller':

            state=request.GET.get('state')

            if state=='true':
                ids=request.session['Check_box_analysis']

                for id in ids:
                    data=RFX.objects.get(pk=id)
                    RFX_base_id=data.RFX_id[15:]

                    data=RFX.objects.filter(RFX_id__icontains=RFX_base_id).filter(sent_quater=Current_quarter(),quarter=data.quarter,)
                    data.exclude(approval_status='Approved').filter(quote_freeze=False).update(
                        quote_is_writable=True
                    )

                if ids != []:
                    save_lock_access_notified_data(request, ids, True)

                if ids==[]:
                    data=RFX.objects.filter(id__in=request.session['current_filtered_RFX'])
                    if True :
                        data.exclude(approval_status='Approved').filter(quote_freeze=False).update(
                            quote_is_writable=True
                        )

                    save_lock_access_notified_data(request, ids, True)

            elif state == 'false':
                ids = request.session['Check_box_analysis']
                for id in ids:

                    data=RFX.objects.get(pk=id)

                    if True :
                        RFX_base_id=data.RFX_id[15:]

                        data=RFX.objects.filter(RFX_id__icontains=RFX_base_id).filter(sent_quater=Current_quarter())
                        data.update(
                            quote_is_writable=False
                        )
                if ids != []:
                    save_lock_access_notified_data(request, ids, False)
                if ids == []:
                    data = RFX.objects.filter(
                        id__in=request.session['current_filtered_RFX'])
                    if True:
                        data.update(
                            quote_is_writable=False
                        )
                    save_lock_access_notified_data(request, ids, False)


            return JsonResponse({'status':200,'message':'Updated Successfully'})
        elif option=='delete_rfx_bulk':
            ids=request.session['Check_box_analysis']
            selected=request.session['current_filtered_RFX']
            
            if ids==[]:
                #print('into full delete')
                ids = RFX.objects.filter(id__in=selected)
                LOGGER.info(f'deleted all rfx by {request.user.first_name} {request.user.last_name} count {len(ids)}')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id__in=ids).values_list('portfolio__id',flat=True)).filter(rfq_sent_flag_cm='Sent').update(rfq_sent_flag_cm='Not Raised')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id__in=ids).values_list('portfolio__id',flat=True)).filter(rfq_sent_flag_distributor='Sent').update(rfq_sent_flag_distributor='Not Raised')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id__in=ids).values_list('portfolio__id',flat=True)).filter(rfq_sent_distributor='Sent').update(rfq_sent_distributor='Not Raised')
                for x in selected:
                    try:
                        data = RFX.objects.get(id=x)
                        datas = RFX.objects.filter(
                            sent_to=data.sent_to,
                            Part_Number=data.Part_Number,
                            Mfr_Part_Number=data.Mfr_Part_Number,
                            Mfr_Name=data.Mfr_Name,
                            cm=data.cm,
                            sent_quater=data.sent_quater
                        ).exclude(approval_status='Approved')
                        RFX.objects.filter(
                            Part_Number=data.Part_Number,
                            cm=data.cm,
                            sent_quater=data.sent_quater,
                        ).exclude(approval_status='Approved').update(split_type='Automated',manual_split=None)
                        Portfolio.objects.filter(id__in=datas.values_list('portfolio__id', flat=True)).update(rfq_sent_flag_supplier='Partially Raised')
                        datas.delete()
                        Apply_split(data.Part_Number,data.Team,data.cm,data.sent_to)
                        for x in RFX.objects.filter(Part_Number=data.Part_Number,cm=data.cm,sent_quater=data.sent_quater,sent_to=data.sent_to).exclude(sent_to='cm'):
                            x.save()

                        
                        #print('deleted', datas)
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                # for x in RFX.objects.filter(Portfolio_in=data.values('portfolio')).exclude(sent_to='cm'):
                #     x.save()

                return JsonResponse({'status': 200, 'message': 'Selected parts deleted Successfully'})
            elif ids != []:
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id__in=ids).values_list('portfolio__id',flat=True)).update(rfq_sent_flag_supplier='Not Raised')
                LOGGER.info(f'deleted  rfx by {request.user.first_name} {request.user.last_name} count {len(ids)}')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id__in=ids).values_list('portfolio__id',flat=True)).filter(rfq_sent_flag_cm='Sent').update(rfq_sent_flag_cm='Not Raised')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id__in=ids).values_list('portfolio__id',flat=True)).filter(rfq_sent_flag_distributor='Sent').update(rfq_sent_flag_distributor='Not Raised')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id__in=ids).values_list('portfolio__id',flat=True)).filter(rfq_sent_distributor='Sent').update(rfq_sent_distributor='Not Raised')
                for x in ids:
                    try:
                        data=RFX.objects.get(id=x)
                        datas=RFX.objects.filter(
                                    sent_to=data.sent_to,
                                    Part_Number=data.Part_Number,
                                    Mfr_Part_Number=data.Mfr_Part_Number,
                                    Mfr_Name=data.Mfr_Name,
                                    cm=data.cm,
                                    sent_quater=data.sent_quater
                                    ).exclude(approval_status='Approved')
                        RFX.objects.filter(
                            Part_Number=data.Part_Number,
                            cm=data.cm,
                            sent_quater=data.sent_quater,
                        ).exclude(approval_status='Approved').update(split_type='Automated',manual_split=None)
                        Portfolio.objects.filter(id__in=datas.values_list('portfolio__id',flat=True)).update(rfq_sent_flag_supplier='Not Raised')
                        datas.delete()
                        for x in RFX.objects.filter(Part_Number=data.Part_Number,cm=data.cm,sent_quater=data.sent_quater,sent_to=data.sent_to).exclude(sent_to='cm'):
                            x.save()
                        Apply_split(data.Part_Number,data.Team,data.cm,data.sent_to)
                        #print('deleted', datas)
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                
                return JsonResponse({'status': 200, 'message': 'Selected parts deleted Successfully'})
            else:
                return JsonResponse({'status': 200, 'message': 'No Parts deleted'})

        elif option == 'delete_rfx':
            try:
                id = request.GET.get('id')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id=id).values_list('portfolio__id',flat=True)).filter(rfq_sent_flag_cm='Sent').update(rfq_sent_flag_cm='No Sent')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id=id).values_list('portfolio__id',flat=True)).filter(rfq_sent_flag_distributor='Sent').update(rfq_sent_flag_distributor='No Sent')
                # Portfolio.objects.filter(id__in=RFX.objects.filter(id=id).values_list('portfolio__id',flat=True)).filter(rfq_sent_distributor='Sent').update(rfq_sent_distributor='No Sent')
                try:
                    data = RFX.objects.get(id=id)
                    dd = RFX.objects.filter(
                        sent_to=data.sent_to,
                        Part_Number=data.Part_Number,
                        Mfr_Part_Number=data.Mfr_Part_Number,
                        Mfr_Name=data.Mfr_Name,
                        cm=data.cm,
                        sent_quater=data.sent_quater).exclude(approval_status='Approved')
                    Portfolio.objects.filter(id__in=dd.values_list('portfolio__id', flat=True)).update(rfq_sent_flag_supplier='Partially Raised')
                    RFX.objects.filter(
                            Part_Number=data.Part_Number,
                            cm=data.cm,
                            sent_quater=data.sent_quater,
                        ).exclude(approval_status='Approved').update(split_type='Automated',manual_split=None)
                    dd.delete()
                    Apply_split(data.Part_Number,data.Team,data.cm,data.sent_to)
                    for x in RFX.objects.filter(Part_Number=data.Part_Number,cm=data.cm,sent_quater=data.sent_quater,sent_to=data.sent_to).exclude(sent_to='cm'):
                            x.save()

                except Exception as e:
                    LOGGER.error("LOG_MESSAGE", exc_info=1)

                return JsonResponse({'status': 200, 'message': 'Deleted Successfully'})
            except:
                return JsonResponse({'status':200,'message':"Delete Wouldn't complete please try again "})
        elif option=='approval_rfx_all':
            ids=request.session.get('Check_box_analysis')
            unable_to_approve_parts = []
            print(ids)
            print('into permission approval_rfx_all')
            
            if has_permission(request.user,'PIC') or has_permission(request.user,'Manager') or request.user.is_superuser:
                print('into permission approval_rfx_all')
                data = RFX.objects.filter(portfolio__Arista_PIC__icontains=request.user.first_name)
                if request.user.is_superuser:
                    data = RFX.objects.filter(sent_quater=Current_quarter())
                data = data.filter(id__in=ids or request.session['current_filtered_RFX'])
                if data[0].Team == 'CMM Team':
                    for i in data.filter(Quote_status='Quoted'):
                        part_count = data.filter(Part_Number=i.Part_Number, cm=i.cm, sent_quater=i.sent_quater, quarter=i.quarter).count()
                        if  part_count<=1 and not RFX.objects.filter(Part_Number=i.Part_Number, cm=i.cm, sent_quater=i.sent_quater, quarter=i.quarter,approval_status='Approved').count()>1:
                            RFX.objects.filter(Part_Number=i.Part_Number, cm=i.cm, sent_quater=i.sent_quater, quarter=i.quarter,approval_status='Approved').update(approval_status='Rejected')
                            data.filter(Quote_status='Quoted', id=i.id).update(
                                approval_status='Approved',
                                quote_freeze=True,
                                quote_is_writable=False,
                            )
                            save_approval_status_notified_data(request, [data.filter(Quote_status='Quoted').values_list('id', flat=True)], status='Approved', role='CMM')
                            save_lock_access_notified_data(request, [data.values_list('id', flat=True)], bool=False)
                        else:
                           
                            unable_to_approve_parts.append(i.id)
                            
                   
                else:
                    ids_notification = []
                    #print(data)

                    
                    for part in data:
                        APN = RFX.objects.filter(sent_quater=Current_quarter()).filter(sent_to=part.sent_to, quarter=part.quarter, portfolio__Team=part.portfolio.Team, cm=part.cm, Part_Number=part.Part_Number)
                        if APN.filter(Quote_status='Quoted').count():
                            APN.update(
                                quote_freeze=True,
                                quote_is_writable=False,
                            )
                            if part.Quote_status == 'Quoted':
                                part.approval_status_PIC = 'Approved'
                                # part.approval_status='Approved'
                                part.quote_freeze = True
                                part.quote_is_writable = False
                                part.save(user=request.user)
                                approval_status_set(part.id)
                                ids_notification.append(part.id)
                            else:
                                part.approval_status_PIC = 'Approved'
                                part.quote_freeze = True
                                part.quote_is_writable = False
                                part.save(user=request.user)
                                approval_status_set(part.id)
                                ids_notification.append(part.id)

                    approval_bulk(data,request.user)
                    save_lock_access_notified_data(request, [data.filter(Quote_status='Quoted').values_list('id',flat=True)], bool=False)
                    save_approval_status_notified_data(request,ids_notification, status='Approved', role='PIC')
                #'No BID', 'Non Quoted', 
                data.filter(Quote_status__in=['Quoted']).update(
                    quote_is_writable=False,
                    quote_freeze=True
                )
                #print(unable_to_approve_parts)
                # send_logger_tele('approval_rfx_all PIC')
                LOGGER.info(f'approved rfx all {request.user.first_name} {request.user.last_name}')
                if not unable_to_approve_parts:
                    return JsonResponse({'status': 200, 'message': 'Approved and sent to next level'})
                else:
                    error_table=RFX.objects.filter(id__in=unable_to_approve_parts).values(
                        "id",
                        "Part_Number",
                        "sent_to",
                        "Mfr_Part_Number",
                        "Mfr_Name",
                        "Item_Price",
                        "cm",
                    ).to_dataframe()
                    error_table.rename(columns=column_names_analysis,inplace=True)
                    error_table=error_table.replace({pd.np.nan:''})
                    error_table=error_table.to_html(index=False,border=0, justify='center', na_rep='', classes='compact table-xs font-small-3 table-responsive table-striped table-bordered')
                    return JsonResponse({'state':'Unapproved Parts', 'message': '''<span class='secondary text-bold-500 font-medium-3'>Below list of parts are not approved due to the following reasons,</span><br>
                    <b class='danger'>Reason:</b><br>
                    <div class='pl-1 info '>
                    1)Approve only Quoted parts <br>
                    2)Please approve only one MPN per APN<br>
                    </div>
                    ''', 'error_table':error_table})

                    
            # elif request.user.is_superuser:
            #     data=RFX.objects.filter(Team=request.GET.get('Team'))
            #     if ids:
            #         data=data.filter(id__in=ids)
            #     else:
            #         data=data.filter(id__in=request.session['current_filtered_RFX'])
            #     if data[0].Team=='CMM Team':
            #         data.filter(Quote_status='Quoted').update(
            #                 approval_status='Approved',
            #                 quote_freeze=True,
            #                 quote_is_writable=False,

            #             )
            #     else:
            #         ids_notification=[]
            #         for part in data:
            #             RFX.objects.filter(sent_quater=Current_quarter()).filter(sent_to=part.sent_to,Part_Number=part.Part_Number).update(
            #                     quote_freeze=True,
            #                     quote_is_writable=False,
            #                     )
            #             if part.Quote_status=='Quoted' or part.Quote_status=='No BID' :
            #                 part.approval_status_PIC='Approved'
            #                 # part.approval_status='Approved'
            #                 part.quote_freeze=True
            #                 part.quote_is_writable=False
            #                 part.save(user=request.user)
            #                 approval_status_set(part.id)
            #                 ids_notification.append(part.id)
            #             else:
            #                 part.approval_status_PIC='Approved'
            #                 part.quote_freeze=True
            #                 part.quote_is_writable=False
            #                 part.save(user=request.user)
            #                 approval_status_set(part.id)
            #                 ids_notification.append(part.id)

            #         save_lock_access_notified_data(request, ids_notification, bool=False)
            #         approval_bulk(data,request.user)
            #         save_lock_access_notified_data(request, [data.filter(Quote_status='Quoted').values_list('id',flat=True)], bool=False)

            #     data.update(
            #         quote_is_writable=False,
            #         quote_freeze=True,
            #     )
            #     # send_logger_tele('approval_rfx_all SU')

            #     return JsonResponse({'status':200,'message':'Approved and sent to next level'})
            else:
                #print('into permission else')

                return JsonResponse({'status': 400, 'message': 'No permission'})

        elif option == 'approval_rfx':
            #print(request.GET)
            
            if request.GET.get('status')=='Approve':
                part=RFX.objects.get(id=request.GET.get('id'))

                if part.split_type=='Automated':
                    split=part.suggested_split
                else:
                    split = part.manual_split

                if not request.GET.get('role') == 'CMM':
                    RFX.objects.filter(sent_quater=Current_quarter(),quarter=part.quarter).filter(sent_to=part.sent_to, Part_Number=part.Part_Number).update(
                        quote_freeze=True,
                        quote_is_writable=False,
                    )
                if request.GET.get('role') == 'PIC':
                    RFX.objects.filter(sent_quater=Current_quarter(),quarter=part.quarter).filter(sent_to=part.sent_to, Part_Number=part.Part_Number).update(
                        quote_freeze=True,
                        quote_is_writable=False,
                    )
                    part.approval_status_PIC = 'Approved'
                    # part.approval_status='Approved'
                    part.quote_freeze = True
                    part.quote_is_writable = False
                    part.save(user=request.user)
                    approval_status_set(part.id)
                    save_approval_status_notified_data(request,[part.id], status='Approved', role='PIC')

                    save_lock_access_notified_data(request, [part.id], bool=False)
                # elif request.GET.get('role')=='Manager':
                #     if str(part.approval_flag)=='20' :
                #         part.approval_status_Manager='Approved'
                #         part.approval_status='Approved'
                #         part.quote_freeze=True
                #         part.quote_is_writable=False
                #         part.save(user=request.user)
                #         approval_status_set(part.id)
                #         manager_approval_status = request.GET.get('status')+' '+str(part.approval_flag)

                #     elif str(part.approval_flag)=='30' :
                #         part.approval_status_Manager='Approved'
                #         part.approval_status_Director='Approval Pending'
                #         part.quote_freeze=True
                #         part.quote_is_writable=False
                #         part.save(user=request.user)
                #         approval_status_set(part.id)
                #         manager_approval_status = request.GET.get('status')+' '+str(part.approval_flag)

                # elif request.GET.get('role')=='Director':

                #     if str(part.approval_flag)=='30':
                #         part.approval_status_Director='Approved'
                #         part.approval_status='Approved'
                #         part.quote_freeze=True
                #         part.quote_is_writable=False
                #         part.save(user=request.user)
                #     approval_status_set(part.id)
                elif request.GET.get('role') == 'CMM' and has_permission(request.user, 'CMM'):
                    RFX.objects.filter(
                        Part_Number=part.Part_Number,
                        sent_quater=part.sent_quater,
                        quarter=part.quarter,
                        cm=part.cm,
                        approval_status='Approved'
                    ).update(
                        approval_status='Rejected'
                    )

                    part.approval_status = 'Approved'
                    part.quote_freeze = True
                    part.quote_is_writable = False
                    part.save(user=request.user)
                    RFX.objects.filter(
                        Part_Number=part.Part_Number,
                        sent_quater=part.sent_quater,
                        quarter=part.quarter,
                        cm=part.cm,
                    ).update(
                        quote_freeze=True
                    )
                    save_approval_status_notified_data(request, [part.id], status='Approved', role='CMM')
                    save_lock_access_notified_data(request, [part.id], bool=False)
                else:
                    return JsonResponse({'status': 403, 'message': 'Permission denied'})

            elif request.GET.get('status') == 'Reject_bulk':
                #print(request.GET)
                
                parts_id=request.session['Check_box_analysis'] or request.session['current_filtered_RFX']

                parts=RFX.objects.filter(id__in=parts_id)
                for part in parts:
                    if part.split_type == 'Automated':
                        split = part.suggested_split
                    else:
                        split = part.manual_split
                    Comments = request.GET.get('comment')
                    if request.GET.get('role') == 'PIC':
                        RFX.objects.filter(cm=part.cm,sent_quater=Current_quarter(), quarter=part.quarter).filter( Part_Number=part.Part_Number).update(
                            quote_freeze=False,
                            approval_status_PIC=None,
                            approval_status=None,

                            )

                        RFX.objects.filter(cm=part.cm,sent_quater=Current_quarter(),quarter=part.quarter).filter(Quote_status__in=['Quoted'],Part_Number=part.Part_Number).update(
                            quote_freeze=False,
                            approval_status_PIC='Approval Pending',
                            approval_status='PIC Approval Pending',
                            PIC_accept_reject_comments=Comments
                            )
                        check_auto_wipe(part)
                        # part.approval_status_PIC='Approval pending'
                        # part.approval_status_Manager='Approval No Need'
                        # part.approval_status_Director='Approval No Need'
                        # part.approval_status='PIC Approval Pending'
                        # part.quote_freeze=False
                        # part.PIC_accept_reject_comments=Comments
                        # part.save(user=request.user)
                        # if str(part.approval_flag)=='10' :
                        #     part.approval_status_PIC='Approval Pending'
                        #     part.approval_status_Manager='Approval No Need'
                        #     part.approval_status_Director='Approval No Need'
                        #     part.approval_status='PIC Approval Pending'
                        #     part.quote_freeze=False
                        #     part.quote_is_writable=False
                        #     part.PIC_accept_reject_comments=Comments
                        #     part.save(user=request.user)
                        #     approval_status_set(part.id)
                        # if split==0 :
                        #     part.approval_status_PIC='Approval Pending'
                        #     part.approval_status_Manager='Approval Pending PIC'
                        #     part.approval_status_Director='Approval No Need'
                        #     part.approval_status='PIC Approval Pending'
                        #     part.PIC_accept_reject_comments=Comments
                        #     approval_status_set(part.id)

                        #     part.quote_freeze=False
                        #     part.quote_is_writable=False
                        #     part.save(user=request.user)

                        # if str(part.approval_flag)=='20' :
                        #     part.approval_status_PIC='Approval Pending'
                        #     part.approval_status_Manager='Approval Pending PIC'
                        #     part.approval_status_Director='Approval No Need'
                        #     part.approval_status='PIC Approval Pending'
                        #     part.PIC_accept_reject_comments=Comments
                        #     approval_status_set(part.id)
                        #     part.quote_freeze=False
                        #     part.quote_is_writable=False
                        #     part.save(user=request.user)
                        # elif str(part.approval_flag)=='30' :
                        #     part.approval_status_PIC='Approval Pending'
                        #     part.approval_status_Manager='Approval Pending PIC'
                        #     part.approval_status_Director='Approval Pending Manager'
                        #     part.approval_status='PIC Approval Pending'
                        #     part.PIC_accept_reject_comments=Comments
                        #     part.quote_freeze=False
                        #     part.quote_is_writable=False
                        #     part.save(user=request.user)
                        #     approval_status_set(part.id)
                        ### part.approval_status_PIC='Approval Pending'
                        ### part.approval_status='PIC Approval Pending'
                        ### part.quote_freeze=False
                        ### part.quote_is_writable=False
                        ### part.portfolio.Arista_pic_comment=Comments
                        ### part.save(user=request.user)
                    elif request.GET.get('role')=='CMM' and has_permission(request.user,'CMM'):
                        from MasterPricing.models import master_temp
                        logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
                        lock=logic_BP.lift_logic=='enable'
                        if  lock:
                            return JsonResponse({'status': 403, 'message': 'Master pricing page is locked by BP Team'})
                        RFX.objects.filter(id=part.id).update(
                            approval_status='Rejected',
                            quote_freeze=False,
                            approval1_comments=Comments,
                        )
                        check_auto_wipe(part)
                        try:
                            delete_data_with_approved_status(request, status='Approved', rfx_id=part.id)
                        except:
                            LOGGER.error("LOG_MESSAGE", exc_info=1)

                        #print('Approval Pending')
                    else:
                        print({'status':403,'message':'Permission denied'})
            elif request.GET.get('status')=='Reject':
                part=RFX.objects.get(id=request.GET.get('id'))

                if part.split_type=='Automated':
                    split=part.suggested_split
                else:
                    split = part.manual_split

                Comments = request.GET.get('comment')
                # send_logger_tele(f"Reject,Role:{request.GET.get('role')},Flag:{part.approval_flag},message:{Comments}")
                if part.split_type == 'Automated':
                    split = part.suggested_split
                else:
                    split = part.manual_split
                #print(request.GET)
                if request.GET.get('role') == 'PIC':
                    RFX.objects.filter(cm=part.cm,sent_quater=Current_quarter(), quarter=part.quarter).filter( Part_Number=part.Part_Number).update(
                        quote_freeze=False,
                        approval_status_PIC=None,
                        approval_status=None,

                        )

                    RFX.objects.filter(cm=part.cm,sent_quater=Current_quarter(),quarter=part.quarter).filter(Quote_status__in=['Quoted'],Part_Number=part.Part_Number).update(
                        quote_freeze=False,
                        approval_status_PIC='Approval Pending',
                        approval_status='PIC Approval Pending',
                        PIC_accept_reject_comments=Comments
                        )
                    check_auto_wipe(part)
                            
                    # part.approval_status_PIC='Approval Pending'
                    # part.approval_status_Manager='Approval No Need'
                    # part.approval_status_Director='Approval No Need'
                    # part.approval_status='PIC Approval Pending'
                    # part.quote_freeze=False
                    # part.PIC_accept_reject_comments=Comments
                    # part.save(user=request.user)
                    # if str(part.approval_flag)=='10' :
                    #     part.approval_status_PIC='Approval Pending'
                    #     part.approval_status_Manager='Approval No Need'
                    #     part.approval_status_Director='Approval No Need'
                    #     part.approval_status='PIC Approval Pending'
                    #     part.quote_freeze=False
                    #     part.quote_is_writable=False
                    #     part.PIC_accept_reject_comments=Comments
                    #     part.save(user=request.user)
                    #     approval_status_set(part.id)
                    # if split==0 :
                    #     part.approval_status_PIC='Approval Pending'
                    #     part.approval_status_Manager='Approval Pending PIC'
                    #     part.approval_status_Director='Approval No Need'
                    #     part.approval_status='PIC Approval Pending'
                    #     part.PIC_accept_reject_comments=Comments
                    #     approval_status_set(part.id)

                    #     part.quote_freeze=False
                    #     part.quote_is_writable=False
                    #     part.save(user=request.user)

                    # if str(part.approval_flag)=='20' :
                    #     part.approval_status_PIC='Approval Pending'
                    #     part.approval_status_Manager='Approval Pending PIC'
                    #     part.approval_status_Director='Approval No Need'
                    #     part.approval_status='PIC Approval Pending'
                    #     part.PIC_accept_reject_comments=Comments
                    #     approval_status_set(part.id)
                    #     part.quote_freeze=False
                    #     part.quote_is_writable=False
                    #     part.save(user=request.user)
                    # elif str(part.approval_flag)=='30' :
                    #     part.approval_status_PIC='Approval Pending'
                    #     part.approval_status_Manager='Approval Pending PIC'
                    #     part.approval_status_Director='Approval Pending Manager'
                    #     part.approval_status='PIC Approval Pending'
                    #     part.PIC_accept_reject_comments=Comments
                    #     part.quote_freeze=False
                    #     part.quote_is_writable=False
                    #     part.save(user=request.user)
                    #     approval_status_set(part.id)
                    ### part.approval_status_PIC='Approval Pending'
                    ### part.approval_status='PIC Approval Pending'
                    ### part.quote_freeze=False
                    ### part.quote_is_writable=False
                    ### part.portfolio.Arista_pic_comment=Comments
                    ### part.save(user=request.user)
                elif request.GET.get('role')=='CMM' and has_permission(request.user,'CMM'):
                    from MasterPricing.models import master_temp
                    logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
                    lock=logic_BP.lift_logic=='enable'
                    if  lock:
                        return JsonResponse({'status': 403, 'message': 'Master pricing page is locked by BP Team'})
                    RFX.objects.filter(id=part.id).update(
                        approval_status='Rejected',
                        quote_freeze=False,
                        approval1_comments=Comments,
                    )
                    check_auto_wipe(part)
                    try:
                        delete_data_with_approved_status(request, status='Approved', rfx_id=part.id)
                    except:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)

                    #print('Approval Pending')
                else:
                    return JsonResponse({'status': 403, 'message': 'Permission denied'})

            return JsonResponse({'status': 200, 'message': 'Updated Successfully'})
        elif option == 'Shareable':
            part=RFX.objects.get(id=int(request.GET.get('id')))
            part.Shareable=not part.Shareable
            part.save()
            return JsonResponse({'status': 200, 'message': f'{part.Mfr_Part_Number} Successfully { "shared" if part.Shareable else "unshared"}  '})
        elif option == 'Shareable_bulk':
            parts_id=request.session['Check_box_analysis'] or request.session['current_filtered_RFX']
            part=RFX.objects.filter(id__in=parts_id)
            data= True if request.GET.get('value')=='yes' else False
            result=part.update(Shareable=data)
            return JsonResponse({'status': 200, 'message': f'Successfully { "shared" if data else "unshared"} for {result} Part(s)  '})




@login_required
def history(request, id):
    data = Master_history_rfx.objects.filter(model_id__id=id)
    data_json = []
    for history in data:
        json=history.data_dict_as_dict
        json["comment"]=history.comment
        json["modified_by"]=history.modified_by and history.modified_by.username
        json["modified_by_email"]=history.modified_by_email
        json["modified_on"]=history.modified_on
        data_json.append(dict(json))
    # data_json=[(x.data_dict_as_dict) for x in data]
    return JsonResponse({'data': data_json}, safe=False)


@login_required
def manual_split_set(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        data = RFX.objects.get(id=id)
        if data.quote_freeze == False:
            #print(request.GET)
            datas=RFX.objects.filter(Team=data.Team).filter(~Q(RFX_id=None) & Q(sent_quater=Current_quarter()) & Q(cm=data.cm) &Q(quarter=data.quarter)).filter(Part_Number=data.Part_Number).filter(Quote_status='Quoted').order_by('Item_Price')
        else:
            datas = 'No_rights'
        #print(datas)
        return render(request, 'rfx/components/split_form.html', {'data': datas,'instance':data})
    if request.method == 'POST':
        from CMT.masterprice_helper import get_po_delivery_calc
        #print(request.POST)
        id = request.POST.getlist('id')
        split_value = [float(x) for x in request.POST.getlist('split_value')]
        if sum(split_value) == 100:
            split_comments = request.POST.getlist('comments')
            for x in range(len(id)):
                data = RFX.objects.filter(id=id[x])
                data.update(
                    manual_split=split_value[x],
                    split_type='Manual',
                    split_comments=split_comments[x],
                    po_delivery=get_po_delivery_calc(id[x])
                )
                #print('Flag:', data[0].approval_flag)
                if data[0].approval_flag == '10' and split_value[x] != 0:
                    data.update(approval_status_PIC='Approval pending',
                                approval_status_Manager='Approval No Need',
                                approval_status_Director='Approval No Need',
                                approval_status='PIC Approval Pending')
                elif data[0].approval_flag == '20' and split_value[x] != 0:
                    data.update(approval_status_PIC='Approval pending',
                                approval_status_Manager='Approval pending PIC',
                                approval_status_Director='Approval No Need',
                                approval_status='PIC Approval Pending')
                elif data[0].approval_flag == '30' and split_value[x] != 0:
                    data.update(approval_status_PIC='Approval pending',
                                approval_status_Manager='Approval pending PIC',
                                approval_status_Director='Approval pending Manager',
                                approval_status='PIC Approval Pending')
                elif split_value[x] == 0:
                    data.update(
                        approval_status_PIC='Approval pending',
                        approval_status_Manager='Approval No Need',
                        approval_status_Director='Approval No Need',
                        approval_status='PIC Approval Pending'
                    )
            std_generator(RFX.objects.filter(id__in=id))
            return JsonResponse({'status': 200, 'message': 'Split Updated'})
        else:
            #print(split_value)
            return JsonResponse({'status': 403, 'message': 'Split Not Updated'})


@login_required
def Comments(request):
    try:
        data = request.POST
        Comments = data.get('Comment')
        id = data.get('id')
        field = data.get('field')
        data = RFX.objects.get(id=id)
        d = Portfolio.objects.get(id=data.portfolio.id)
        d.Arista_pic_comment = Comments
        d.save()
        return JsonResponse({'status': 200, 'message': 'Updated successfully'})
    except Exception as e:
        LOGGER.error("LOG_MESSAGE", exc_info=1)

        return JsonResponse({'status':403,'message':e})


def approval_bulk(data, user):

    # data.update(
    #         quote_is_writable=False,
    #         quote_freeze=True
    #             )
    data = data.filter(approval_status_PIC__icontains='pending').exclude(
        Quote_status='Non Quoted')
    data.update(
            quote_is_writable=False,
            quote_freeze=True,
            approval_status_PIC='Approved',
            approval_status='Approved',
                )

    for x in data:
        #print(x)
        if x.split_type == 'Automated':
            split = x.suggested_split
        else:
            split = x.manual_split
        if str(x.approval_flag) == '10':
            x.approval_status_PIC = 'Approved'
            x.approval_status = 'Approved'
            x.save(user=user)
        elif split == 0:
            x.approval_status_PIC = 'Approved'
            x.approval_status = 'Approved'
            x.save(user=user)
        elif str(x.approval_flag) == '20':
            x.approval_status_PIC = 'Approved'
            x.approval_status_Manager = 'Approval pending'
            x.approval_status = 'Manager Approval Pending'
            x.save(user=user)
        elif str(x.approval_flag) == '30':
            x.approval_status_PIC = 'Approved'
            x.approval_status_Manager = 'Approval pending'
            x.approval_status = 'Manager Approval Pending'
            x.save(user=user)
        approval_status_set(x.id)

# @login_required
# def price_bench_marking(request):
#     try:
#         df=RFX.objects.filter(Team='CMM Team').to_dataframe()
#         df.RFX_id=df.RFX_id.str.split('_to_').str[0]
#         df.sent_to=df['sent_to'].str.replace(' ','')
#         data=df.pivot(index='RFX_id', columns='sent_to', values=['Item_Price','Comments'])
#         print(data)
#         data.columns=data.columns.to_flat_index()
#         data.reset_index(inplace=True)
#         temp=df.filter(['RFX_id','Part_Number', 'Mfr_Part_Number',
#                         'Mfr_Name', 'cm', ])
#         data=temp.merge(data,on='RFX_id')
#         del data['RFX_id']
#         data.drop_duplicates(inplace=True)
#         itemprice=[]
#         for x in data.columns:
#             if str(x).startswith("('Item_Price"):
#                 itemprice.append(x)
#             else:
#                 continue
#         itemprice.reverse()
#         data['Item benchmark']=data.fillna(0).filter(itemprice).idxmax(axis=1).str[1].str.replace('distributor_to_','')
#         data.fillna('',inplace=True)
#         return JsonResponse({'table':data.to_html(classes='table text-nowarp table-responsive table-xs table-striped table-hover export_table font-small-1',
#                             table_id='price_bench_marking_table',index=False,na_rep='')})
#     except:
#         return JsonResponse({'table':'<h3>Table Not Available</h3>'})


@login_required
def price_bench_marking(request):
    # try:
    pd.set_option('display.float_format', lambda x: '%.5f' % x)

    columns = {
        'Part_Number': 'Part Number',
        'Mfr_Name': 'Mfr Name',
        'Mfr_Part_Number': 'Mfr Part Number',
        'Item_Price': 'Item Price',
        'Item_Price_JPE': 'Item Price JPE',
        'Item_Price_JSJ': 'Item Price JSJ',
        'Item_Price_JMX': 'Item Price JMX',
        'Item_Price_SGD': 'Item Price SGD',
        'Item_Price_FGN': 'Item Price FGN',
        'Item_Price_HBG': 'Item Price HBG',
        'MOQ': 'MOQ',
        'MOQ_SGD': 'MOQ SGD',
        'MOQ_JPE': 'MOQ JPE',
        'MOQ_JSJ': 'MOQ JSJ',
        'MOQ_JMX': 'MOQ JMX',
        'MOQ_FGN': 'MOQ FGN',
        'MOQ_HBG': 'MOQ HBG',
        'sent_to': 'sent to',
        'Lead_Time': 'Lead Time',
        'Lead_Time_SGD': 'Lead Time SGD',
        'Lead_Time_JPE': 'Lead Time JPE',
        'Lead_Time_JSJ': 'Lead Time JSJ',
        'Lead_Time_JMX': 'Lead Time JMX',
        'Lead_Time_FGN': 'Lead Time FGN',
        'Lead_Time_HBG': 'Lead Time HBG',
        'Quoted_by': 'Supplier/Dist. Quoted By'
    }
    q_Supplier = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).exclude(sent_to='cm')
    q_cm_JPE = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm', cm='JPE')
    q_cm_SGD = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm', cm='SGD')
    q_cm_FGN = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm', cm='FGN')
    q_cm_HBG = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm', cm='HBG')
    q_cm_JSJ = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm', cm='JSJ')
    q_cm_JMX = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm', cm='JMX')
    df_Supplier = q_Supplier.values(
        'Part_Number',
        'Mfr_Name',
        'Mfr_Part_Number',
        'Item_Price',
        'MOQ',
        'Lead_Time',
        'sent_to',
        'cm',
        'Quoted_by',

    ).to_dataframe()
    df_cm_JPE = q_cm_JPE.values('Part_Number', 'Item_Price', 'Lead_Time', 'MOQ').to_dataframe()
    df_cm_SGD = q_cm_SGD.values('Part_Number', 'Item_Price', 'Lead_Time', 'MOQ').to_dataframe()
    df_cm_FGN = q_cm_FGN.values('Part_Number', 'Item_Price', 'Lead_Time', 'MOQ').to_dataframe()
    df_cm_HBG = q_cm_HBG.values('Part_Number', 'Item_Price', 'Lead_Time', 'MOQ').to_dataframe()
    df_cm_JSJ = q_cm_JSJ.values('Part_Number', 'Item_Price', 'Lead_Time', 'MOQ').to_dataframe()
    df_cm_JMX = q_cm_JMX.values('Part_Number', 'Item_Price', 'Lead_Time', 'MOQ').to_dataframe()
    data = pd.merge(df_Supplier, df_cm_JPE, on='Part_Number',suffixes=['', '_JPE'], how='left')
    data = pd.merge(data, df_cm_SGD, on='Part_Number',suffixes=['', '_SGD'], how='left')
    data = pd.merge(data, df_cm_FGN, on='Part_Number',suffixes=['', '_FGN'], how='left')
    data = pd.merge(data, df_cm_HBG, on='Part_Number',suffixes=['', '_HBG'], how='left')
    data = pd.merge(data, df_cm_JSJ, on='Part_Number',suffixes=['', '_JSJ'], how='left')
    data = pd.merge(data, df_cm_JMX, on='Part_Number',suffixes=['', '_JMX'], how='left')
    field = [k for k, v in columns.items()]
    data = data.filter(field)
    data.fillna(value=np.nan, inplace=True)
    data.rename(columns=columns, inplace=True)
    data.fillna('-', inplace=True)
    #print(data)
    return JsonResponse({'table': data.to_html(classes='table  table-bordered table-striped text-nowrap table-xs font-small-2 export_table', table_id='price_bench_marking_table', justify='center', index=False, na_rep='-')})
    # except:
    # return JsonResponse({'table':'<h3>Table Not Available</h3>'})


def Handel_Index_error(lists, place, digit=False):
    try:
        values = lists[place]
    except IndexError:
        values = None
    if digit:
        try:
            values = round(float(values), 5)
        except:
            values = None
            LOGGER.error("LOG_MESSAGE", exc_info=1)

    if values=='':
        values=None

    return values


@login_required
def advance_filter(request, Team, section, field):
    if section == 'get_value':
        id = request.session['his_analysis']
        #print(id)
        q = RFX.objects.filter(id__in=id)
        #print(q)
        data = q.exclude(**{f"{field}__isnull": True}
                         ).values_list(field, flat=True).distinct()
        return JsonResponse(list(data), safe=False)
    if section == 'filter_form' and field == 'all_data':
        data = request.POST
        #print(data)
        fields = data.getlist('fields[]')
        q = Q()
        for x in fields:
            q &= Q(**{f'{x}__in': data.getlist(f'{x}_value[]')})
        qs = RFX.objects.filter(q).values_list('id', flat=True)
        request.session['advance_filter_RFX'] = list(qs)
        request.session.modified = True
        #print(request.session['advance_filter_RFX'])
        return HttpResponse(request, len(qs))


@multi_threading
def previous_split_set(rfx):
    data = RFX.objects.filter(quarter=Current_quarter()).filter(
        **{'sent_to': rfx.sent_to, 'Part_Number': rfx.Part_Number, 'Mfr_Part_Number': rfx.Mfr_Part_Number, 'Mfr_Name': rfx.Mfr_Name, })
    if data:
        if data[0].split_type == 'Manual':
            previous_split = data[0].manual_split
        else:
            previous_split = data[0].suggested_split
    else:
        previous_split = None
    rfx.previous_split = previous_split
    rfx.save()


column_names_analysis = {
    "Part_Number": "Arista Part Number or APN",
    "Mfr_Name": "Mfr Name",
    "Item_Price": "Quoted Price",
    "Mfr_Part_Number": "Mfr Part Number or MPN",
    "cm": "CM",
    "Lead_Time": "Lead Time",
    "MOQ": "MOQ",
    "suggested_split": "Suggested Split",
    "manual_split": "Manual Split *",
    "portfolio__Qualification_Status": "Qual Status",
    "previous_split": "Previous Qtr Split",
    "approval_status_PIC": "PIC Approval Status",
    "approval_status_Manager": "Manager Approval Status",
    "PIC_accept_reject_comments": "PIC Approval / Rejection Comments",
    "split_comments": "Manual Split Comments*",
    "approval1_comments": "Manager Approval / Rejection Comments",
    "std_cost": "New Std Cost",
    "approval_status_Director": "Director Approval Status",
    "approval2_comments": "Director Approval / Rejection Comments",
    "id": "RFQ ID",
    "quarter": "Quarter",
    "sent_to": "Sent To",
    "List": "List",
    "tarrif": "Tariff",
    "COO": "COO",
    "Inco_Term": "Inco Terms",
    "Freight_cost": "Freight",
    "Quote_Type": "Quote Type",
    "Life_Cycle": "Supplier Lifecycle",
    "Comments": "Supplier Comments",
    "Quote_status": "Quote status",
    "NCNR": "NCNR",
    "Team": "Team",
    'PO_Delivery': "PO / Delivery",
    'soft_hard_tool': "Soft / Hard Tool",
    "sent_quater": "RFQ sent Quarter",
    "portfolio__Lifecycle_Phase": "Lifecycle phase",
    "portfolio__commodity": "Commodity",
    "portfolio__Rev": "Rev",
    "portfolio__Mfr_Part_Lifecycle_Phase": "Mfr Lifecycle",
    "portfolio__cm_Part_Number": "CM Part Number",
    "portfolio__Cust_consign": "Cust Consign",
    "portfolio__Parts_controlled_by": "Parts Controlled by",
    "portfolio__Item_Desc": "Item Desc",
    "portfolio__Original_PO_Delivery_sent_by_Mexico": "Original PO / Delivery",
    "portfolio__cm_Quantity_Buffer_On_Hand": "CM Qty Buffer On Hand",
    "portfolio__cm_Quantity_On_Hand_CS_Inv": "CM Qty On Hand Cs Inv",
    "portfolio__Open_PO_due_in_this_quarter": "Open PO Current Qtr",
    "portfolio__Open_PO_due_in_next_quarter": "Open PO Q+1",
    "portfolio__Delivery_Based_Total_OH_sum_OPO_this_quarter": "Delivery based Total OH + OPO Current Qtr",
    "portfolio__PO_Based_Total_OH_sum_OPO": "PO based Total OH +OPO",
    "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand": "Current Qtr Demand",
    "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand": "Q+1 Demand",
    "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand": "Q+2 Demand",
    "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand": "Q+3 Demand",
    "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista": "Delta Demand",
    # "portfolio__ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std":"Current Qtr std cost",
    "portfolio__sgd_jpe_cost": "Current Qtr Std Cost (SGD / JPE / FGN / HBG / JSJ / JMX) $",
    "portfolio__Blended_AVG_PO_Receipt_Price": "Sanmina Blended Avg PO Receipt Price",
    "portfolio__Ownership": "Ownership",
    "portfolio__Arista_PIC": "Arista PIC",
    "portfolio__offcycle": "Offcycle",
    "portfolio__bp_comment": "BP comments",
    "Quoted_by": "Quoted by",
    "split_type": "Split Type",
    'created_by__username': 'Created by',
    "modified_on": 'Modified on',
    "created_on": 'Created on',
    "approval_status": 'Approval Status',
    'portfolio__cm': 'cm',
    'portfolio__Mfr_Name': 'Mfr_Name',
    'portfolio__Mfr_Part_Number': 'Mfr_Part_Number',
    'portfolio__MOQ': 'MOQ',
    'portfolio__Team': 'Team',
    'created_by': 'created_by',
    'modified_on': 'modified_on',
    'created_on': 'created_on',
    'quote_is_writable': 'quote_is_writable',
    'quote_freeze': 'quote_freeze',
    'approval_flag': 'approval_flag',
    'new_po_price': 'new_po_price',
    'current_final_std_cost': 'current_final_std_cost',
    'current_updated_std_cost': 'current_updated_std_cost',
    'current_qtr_decision': 'current_qtr_decision',
    'approve_reject_std_price': 'approve_reject_std_price',
    'cm_approve_reject': 'cm_approve_reject',
    'arista_pic_approve_reject': 'arista_pic_approve_reject',
    'bp_team_approve_reject': 'bp_team_approve_reject',
    'standard_price_q1': 'standard_price_q1',
    'BP_team_Approve_Reject_Comments': 'BP_team_Approve_Reject_Comments',
    'Arista_PIC_Comments_to_CM': 'Arista_PIC_Comments_to_CM',
    'Arista_BP_Comments': 'Arista_BP_Comments',
    'CM_Additional_Notes_on_Supplier_distributor':
    'CM_Additional_Notes_on_Supplier_distributor',
    'CM_PO_Delivery_Remarks': 'CM_PO_Delivery_Remarks',
    'final_split': 'Final Split (%)'
}


@login_required
def download_rfx(request,Team='',mail=False):
    if Team=='GSM Team' :
        fields=[
                "Part_Number",
                "Mfr_Name",
                "Item_Price",
                "Mfr_Part_Number",
                "cm",
                "Lead_Time",
                "MOQ",
                "suggested_split",
                "manual_split",
                "portfolio__Qualification_Status",
                "previous_split",
                "approval_status_PIC",
                "approval_status_Manager",
                "PIC_accept_reject_comments",
                "split_comments",
                "approval1_comments",
                "std_cost",
                "approval_status_Director",
                "approval2_comments",
                "id",
                "quarter",
                "sent_to",
                "List",
                "tarrif",
                "COO",
                "Inco_Term",
                "Freight_cost",
                "Quote_Type",
                "Life_Cycle",
                "Comments",
                "Quote_status",
                "NCNR",
                "Team",
                'PO_Delivery',
                'soft_hard_tool',
                "sent_quater",
                "portfolio__Lifecycle_Phase",
                "portfolio__commodity",
                "portfolio__Rev",
                "portfolio__Mfr_Part_Lifecycle_Phase",
                "portfolio__cm_Part_Number",
                "portfolio__Cust_consign",
                "portfolio__Parts_controlled_by",
                "portfolio__Item_Desc",
                "portfolio__Original_PO_Delivery_sent_by_Mexico",
                "portfolio__cm_Quantity_Buffer_On_Hand",
                "portfolio__cm_Quantity_On_Hand_CS_Inv",
                "portfolio__Open_PO_due_in_this_quarter",
                "portfolio__Open_PO_due_in_next_quarter",
                "portfolio__Delivery_Based_Total_OH_sum_OPO_this_quarter",
                "portfolio__PO_Based_Total_OH_sum_OPO",
                "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
                "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
                "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
                "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
                "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
                # "portfolio__ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std",
                "portfolio__sgd_jpe_cost",
                "portfolio__Blended_AVG_PO_Receipt_Price",
                "portfolio__Ownership",
                "portfolio__Arista_PIC",
                "portfolio__offcycle",
                "portfolio__bp_comment",
                "Quoted_by",
                "split_type",
                'created_by__username',
                "Quoted_by",
                "modified_on",
                "created_on",
                "approval_status",

                ]



    elif  Team=='CMM Team':
        ###cmm,
        fields=[
            "id",
            "quarter",
            "sent_to",
            "Part_Number",
            "Mfr_Part_Number",
            "Mfr_Name",
            "cm",
            "Arista_pic_comment",
            "Item_Price",
            "Lead_Time",
            "MOQ",
            "List",
            "tarrif",
            "COO",
            "Inco_Term",
            "MPQ",
            "Assembly_cost",
            "Freight_cost",
            "Masked_Price",
            "Quote_Type",
            "Region",
            "Geo",
            "Life_Cycle",
            "Comments",
            "Quote_status",
            "sent_quater",
            "portfolio__Number",
            "portfolio__Lifecycle_Phase",
            "portfolio__commodity",
            "portfolio__Rev",
            "portfolio__Mfr_Part_Lifecycle_Phase",
            "portfolio__Qualification_Status",
            "portfolio__cm_Part_Number",
            "portfolio__Arista_Part_Number",
            "portfolio__Cust_consign",
            "portfolio__Parts_controlled_by",
            "portfolio__Item_Desc",
            "portfolio__LT",
            "portfolio__Original_PO_Delivery_sent_by_Mexico",
            "portfolio__cm_Quantity_Buffer_On_Hand",
            "portfolio__cm_Quantity_On_Hand_CS_Inv",
            "portfolio__Open_PO_due_in_this_quarter",
            "portfolio__Open_PO_due_in_next_quarter",
            "portfolio__Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "portfolio__PO_Based_Total_OH_sum_OPO",
            "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
            "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
            "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "portfolio__ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std",
            "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD",
            "portfolio__Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1",
            "portfolio__Blended_AVG_PO_Receipt_Price",
            "portfolio__Ownership",
            "portfolio__Arista_PIC",
            "portfolio__offcycle",
            "portfolio__bp_comment",
            "Quoted_by",
            "NCNR",
            "Team",
            "PO_Delivery",
            "soft_hard_tool",
            "std_cost",
            "suggested_split",
            "manual_split",
            "previous_split",
            "split_type",
            "approval_status_PIC",
            "approval_status_Manager",
            "approval_status_Director",
            "approval_status",
            "split_comments",
            "approval1_comments",
            "approval2_comments",
            "CM_comments_on_Justifing_price",
            "Supplier_Distributor_name_from_cm",
            "CM_Notes_on_Supplier",
            "CM_Manufacturer",
            "CM_mpn",
            "CM_buyer",
            "CM_qty_std_source",
            "po_delivery",
            "modified_on",
            "created_on",
        ]
    if request.GET.get('template')=='excel_filter':
        df=RFX.objects.none().values(
                "id",
                "quarter",
                "sent_to",
                "Part_Number",
                "Mfr_Part_Number",
                "Mfr_Name",
                "cm",

            ).to_dataframe()
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.rename(columns=column_names_analysis, inplace=True)
                df.to_excel(writer, index=False, sheet_name='Quote Analysis')
                writer.save()
                response = HttpResponse(
                    b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'inline; filename=Quote_Analysis.xlsx'
                return response
    
    if request.GET.get('Quarter'):
        if Team == 'GSM Team':
            initial = RFX.objects.filter(Q(portfolio__Team='GSM Team') & Q(sent_quater=request.GET.get('Quarter')))
            if has_permission(request.user, 'Super User') or request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser:
                #print('into super user')
                data = initial
            elif request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')):
                #print(request.user.username)

                data=initial.filter(portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')
            else:
                data = RFX.objects.none()

        elif Team == 'CMM Team':
            initial = RFX.objects.exclude(sent_to='cm').filter(Q(portfolio__Team='CMM Team') & Q(sent_quater=request.GET.get('Quarter')))
            if has_permission(request.user, 'Super User') or request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser:
                data = initial
            elif request.user in User.objects.filter(groups=Group.objects.get(name='CMM Team')):
                data = initial.filter(
                    portfolio__Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')
            else:
                data = RFX.objects.none()
        else:
            data = RFX.objects.none()
    if request.GET.get('Quarter'):
        data = data.filter(sent_quater=request.GET.get('Quarter'))
    else:
        data=RFX.objects.filter(id__in=request.session['current_filtered_RFX'])
    df=data.order_by('Part_Number').values(*fields).to_dataframe()
    df.loc[df['Quote_status']!='Quoted','suggested_split']=None
    df['modified_on'] = df['modified_on'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).replace(tzinfo=None))
    df['created_on'] = df['created_on'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).replace(tzinfo=None))
    LOGGER.info(f'RFQ downloaded by {request.user.first_name} {request.user.last_name}')
    if Team=='GSM Team' :
        df.loc[df['split_type'] == 'Automated', 'final_split'] = df['suggested_split']
        df.loc[df['split_type'] == 'Manual', 'final_split'] = df['manual_split']
        df.loc[df['approval_status'] != 'Approved', 'final_split'] = None

        if request.GET.get('award_letter'):
            return download_award(request,data.values_list('id',flat=True),supplier=False)

        
    with BytesIO() as b:
        with pd.ExcelWriter(b) as writer:
            df.rename(columns=column_names_analysis, inplace=True)
            df.to_excel(writer, index=False, sheet_name='Quote Analysis')
            writer.save()
            if mail:
                return b.getvalue(),f'Quote Analysis {Team}.xlsx'
            response = HttpResponse(
                b.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'inline; filename=Quote_Analysis.xlsx'
            return response

# bulk split upload


@login_required
def upload_split(request):
    try:
        File = request.FILES['Upload_Excel']
        df = pd.read_excel(File,keep_default_na=False)
        df = df.replace({'': None})
        df = df.replace({'NaN': None})
        df = df.replace({'nan': None})
        column_names_decode = {v: k for k, v in column_names_analysis.items()}
        df.rename(columns=column_names_decode, inplace=True)
        df=df.loc[~df['manual_split'].isna()]
        #print(df)
        df = df[df['Quote_status'] == 'Quoted']
        #print(df['manual_split'])
        try:del df['final_split']
        except:pass
        df_db=RFX.objects.filter(Quote_status='Quoted',sent_quater=Current_quarter(),quarter__in=df['quarter'].to_list(),Part_Number__in=df['Part_Number'].to_list(),cm__in=df['cm'].to_list()).values(*df.columns).to_dataframe()
        df['unique'] = df['quarter']+df['Part_Number']+df['cm']

        def NoneFinder(x):
            x = x.to_list()
            return False if None in x else True
        def Partcountval(x):
            return True if len(df.loc[df['Part_Number']==x]) == len(df_db.loc[df_db['Part_Number']==x]) else False
        manual_split_validator = df.groupby('unique').agg({
            'Part_Number': 'first',
            'quarter': 'first',
            'manual_split': 'sum',
            'split_comments': NoneFinder,
        })
        
        manual_split_validator['Partcountval']=manual_split_validator.apply(lambda x:Partcountval(x['Part_Number']),axis=1)
        
        #print(manual_split_validator['Partcountval'])
    except Exception as e:
        #print(e)
        LOGGER.error("LOG_MESSAGE", exc_info=1)

        return JsonResponse({'error_table':f'{e}','status':415,'message':'Upload the correct file'})

    manual_split_validator.loc[manual_split_validator['manual_split']==100,'validator']=True
    manual_split_validator.loc[manual_split_validator['manual_split']!=100,'validator']=False
    manual_split_validator.loc[manual_split_validator['manual_split']!=100,'validator']=False
    manual_split_validator.loc[manual_split_validator['split_comments']==False,'validator']=False
    manual_split_validator.loc[manual_split_validator['split_comments']==False,'split_comments']='Please Add Split Comments for all rows,'
    manual_split_validator.loc[manual_split_validator['split_comments']==True,'split_comments']='Check the Split Value,'
    manual_split_validator.loc[manual_split_validator['Partcountval']==True,'Partcountval']='.'
    manual_split_validator.loc[manual_split_validator['Partcountval']==False,'validator']=False
    manual_split_validator.loc[manual_split_validator['Partcountval']==False,'Partcountval']='Please check whether all MPN is present for this APN'
    manual_split_validator['split_comments']=manual_split_validator['split_comments']+manual_split_validator['Partcountval']
    err=manual_split_validator[manual_split_validator['validator']==False].filter(['Part_Number','manual_split','split_comments'])

    if not err.empty:
        LOGGER.info(f'Split uploaded by {request.user.first_name} {request.user.last_name} with error')
        return JsonResponse({'error_table':err.rename(columns={'manual_split':'Total split','Part_Number':'Part Number','split_comments':'Comments'}).to_html(index=False,justify='left',classes='table table-xs table-striped table-hover compact'),'status':422,
        'message':'''
           &ensp; We consider only quoted part. The Manual split which has been set for the below part(s) is/are incorrect. <br>&ensp;Total split Value must be equal to 100%. Also please note that comments column is a mandatory field.<br>&ensp; Please remove the parts which you do not wanted to change any splits.

        '''})
    else:
        counter = 0
        ipq=[]
        for index, row in df.iterrows():
            split_comments = row['split_comments']

            data = RFX.objects.filter(id=row["id"])
            check_approved=data.filter(approval_status = 'Approved').exists()
            if data and (not check_approved):
                manual_split=row['manual_split'] if row['manual_split']!='nan'  else 0
                #print(manual_split)
                if data[0].portfolio.Qualification_Status!='Qualified' and manual_split>0:
                    ipq.extend(RFX.objects.filter(Part_Number=data[0].Part_Number,quarter=data[0].quarter,cm=data[0].cm).values_list('id',flat=True))

                data.update(
                    manual_split=manual_split,
                    split_type='Manual',
                    split_comments=split_comments,
                )
                if data[0].approval_flag == '10' and manual_split != 0:
                    data.update(approval_status_PIC='Approval pending',
                                approval_status_Manager='Approval No Need',
                                approval_status_Director='Approval No Need',
                                approval_status='PIC Approval Pending'
                                )
                elif data[0].approval_flag == '20' and manual_split != 0:
                    data.update(approval_status_PIC='Approval pending',
                                approval_status_Manager='Approval pending PIC',
                                approval_status_Director='Approval No Need',
                                approval_status='PIC Approval Pending'
                                )
                elif data[0].approval_flag == '30' and manual_split != 0:
                    data.update(approval_status_PIC='Approval pending',
                                approval_status_Manager='Approval pending PIC',
                                approval_status_Director='Approval pending Manager',
                                approval_status='PIC Approval Pending'
                                )
                elif manual_split == 0:
                    data.update(
                        approval_status_PIC='Approval pending',
                        approval_status_Manager='Approval No Need',
                        approval_status_Director='Approval No Need',
                        approval_status='PIC Approval Pending'
                    )
                counter += 1

        # std_generator(RFX.objects.filter(id__in=df['id'].to_list()))
        std_generator_bulk(RFX.objects.filter(id__in=df['id'].to_list()))
        bg_save_rfx(RFX.objects.filter(id__in=df['id'].to_list()))
        ipq_df=RFX.objects.filter(id__in=ipq).values(
                        "Part_Number",
                        "Mfr_Part_Number",
                        "Mfr_Name",
                        'portfolio__Qualification_Status',
                        'manual_split',).to_dataframe()
        if not ipq_df.empty:
            LOGGER.info(f'Split uploaded by {request.user.first_name} {request.user.last_name} with iqp')
            return JsonResponse({'error_table':ipq_df.rename(columns={
            "Part_Number":'Part Number',
            "Mfr_Part_Number":'Mfr Part Number',
            "Mfr_Name":'Mfr. Name',
            "portfolio__Qualification_Status":'Qualification Status',
            "manual_split":'Manual split',
                }).to_html(index=False,justify='left',na_rep='-',classes='table table-grey  compact table-borderless border border-0 table-striped table-hover table-xs nowarp '),'status':422,
            'message':f'''
            Split has been uploaded successfully for {counter} Part(s),<br><h3 class='badge badge-warning'>Note:</b>Below parts are not qualified yet but split has been updated, Please verify.</h3>

            '''})

        LOGGER.info(
            f'Split uploaded by {request.user.first_name} {request.user.last_name} with no error')
        return JsonResponse({'error_table': None, 'status': 200, 'message': f'Split has been uploaded for {counter}'})


@multi_threading
def bg_save_rfx(data):
    for x in data:
        x.save()


def approval_status_set(id):
    #print('Into Approval Status')
    part = RFX.objects.get(id=id)
    if part.Team == 'CMM Team':
        return None
    data = RFX.objects.filter(quarter=part.quarter).filter(portfolio__Team=part.portfolio.Team, cm=part.cm, Part_Number=part.Part_Number, Quote_status='Quoted')
    data_nq = RFX.objects.filter(quarter=part.quarter).filter(portfolio__Team=part.portfolio.Team, cm=part.cm, Part_Number=part.Part_Number)
    #print(data.values("approval_status_PIC","approval_status_Manager","approval_status_Manager",))
    count = data.count()
    PIC = data.filter(approval_status_PIC__in=['Approved']).count()
    Manager = data.filter(approval_status_Manager__in=['Approved', 'Approval No Need']).count()
    Director = data.filter(approval_status_Director__in=['Approved', 'Approval No Need']).count()
    PIC = PIC if PIC != 0 else -1
    Manager = Manager if Manager != 0 else -1
    Director = Director if Director != 0 else -1
    #print('count', count)
    #print('PIC', PIC)
    #print('Manager', Manager)
    #print('Director', Director)
    # if count!=PIC:
    #     print('PIC Approval Pending')
    #     data.update(approval_status='PIC Approval Pending')
    # elif count!=Manager:
    #     print('Manager Approval Pending')
    #     data.update(approval_status='Manager Approval Pending')
    # elif count!=Director:
    #     print('Director Approval Pending')
    #     data.update(approval_status='Director Approval Pending')
    # elif count==PIC and count==Manager and count==Director:
    #     print('Approved')
    #     data.update(approval_status='Approved')
    # else:
    #     print('Un Conditioned')
    if count != PIC:
        #print('PIC Approval Pending')
        data.update(approval_status='PIC Approval Pending')
    # elif count!=Manager:
    #     print('Manager Approval Pending')
    #     data.update(approval_status='Manager Approval Pending')
    # elif count!=Director:
    #     print('Director Approval pending')
    #     data.update(approval_status='Director Approval pending')
    elif count == PIC:
        #print('Approved')
        data.update(approval_status='Approved')
    else:
        print('Un Conditioned')
@login_required
def excel_filter(request, *args):
    if True:
        model = RFX
        #print(args)
        if args:
            df = args[0]
        else:
            xlx = request.FILES['Upload_Excel']
            df = pd.read_excel(xlx)
        try:
            column_names_decode = {v: k for k,
                                   v in column_names_analysis.items()}
        except:
            LOGGER.error("LOG_MESSAGE", exc_info=1)

            return HttpResponse('not allowed')
        df.rename(columns=column_names_decode, inplace=True)
        try:del df['final_split']
        except:pass
        df = df.replace({np.nan: None})
        q = Q()
        for column in df.columns:
            q &= Q(**{f'{column}__in': df[column].to_list()})

        qs = model.objects.filter(q).values_list('id', flat=True)

        request.session['filter_excel_RFX'] = list(qs)
        request.session.modified = True

        return HttpResponse('Success')

    else:
        return HttpResponse('not allowed')


def quote_email_notification(request, created_by=None, suppliers=[], suppliers_not_in_contact=[], Team=None, notification_to='supplier', notification=True, **extras):
    '''
    Type:Static Function
    Arg:request
    Process:
    This func is to send bulk email for quoting process
    * This will send mail to all supplier and distributor
    * This will not send multiple notification
    * The mail contains the name of the quote initiator and Mfr Name 

    '''
    if notification_to == 'supplier':
        supplier_email=extras.get('suppliers_email')
        #print(supplier_email,"extras.get('suppliers_email')")
        suppliers = list(set(suppliers))
        suppliers_not_in_contact = list(set(suppliers_not_in_contact))
        #print(set(suppliers))
        #print(set(suppliers_not_in_contact))

        try:
            url = get_current_site(request).domain
        except:
            url = settings.PRODUCTION
        if notification:
            for user in suppliers:
                for supplier in suppliers_detail.objects.filter(user_model__is_active=True, is_active=True).filter(Supplier_Name=user, Team=Team).distinct('user_model__email'):
                    # email for each suppier with cc to rfq created user
                    if supplier.user_model.email in supplier_email:
                        send_notification(request, user_to=None, to_mail_id=[supplier.user_model.email], user_from=f"Arista Master Pricing Automation Tool",
                                        body=f'''
            Hello,

            Below is the link to a Request for Quote (RFQ) from Arista Master Pricing tool.

            Please visit the link and review the RFQ where you may enter your response directly through the website.

            https://{url}/

            Kindly do not reply to srv-masterpricing@arista.com.
            For Questions related to RFQ please contact PIC {created_by.email}

            Regards,
            Arista Master Pricing Automation Tool



                        ''',
                                        subject=f'''
                        RFQ for {supplier.Supplier_Name} from Arista MPA Tool
                        ''',
                        title=None,cc=[created_by.email])
                        print(f'you are having awaiting Quote pls check, by {created_by.first_name} {created_by.last_name} ,to=[{supplier.user_model.email}],cc=[{created_by.email}]')

        #Confirmation mail
        list_of_sup=''
        for id,name in enumerate(suppliers_not_in_contact,):
            list_of_sup+=f"{id+1}. {name}<br>"
        send_notification(request,user_to=None,to_mail_id=[created_by.email],user_from=f"RFQ Notification",
        subject='''
                RFQ sent Status
                ''',
                          body=f'''
    Hello,

    RFQ is sent for the selected parts{'' if notification else '(without notifying supplier)'} {f'except for the below list of suppliers because they are not in Supplier contact list<br> {list_of_sup}' if list_of_sup else '' }

    Note: RFQ sent data is listed in the attached excel.

    Regards,
    Arista Master Pricing tool

    ''',

        title=None,Attach_file=extras.get('attachment'),cc=[])
    elif notification_to=='cm':
        cms=list(set(suppliers))
        try:url=get_current_site(request).domain
        except:url=settings.PRODUCTION
        users=[]
        cc=[]
        for cm in cms:
            users.append(
                {'to': User.objects.filter(groups__name__icontains=f'{cm} Contract Manufacture').values_list('email', flat=True),
                 'cc': User.objects.filter(groups__name=f'BP {cm} Manager').values_list('email', flat=True),
                 'cm': cm
                 }
            )
        for cm in users:
            #print(users)
            send_notification(request, user_to=None, to=list(cm['to']), user_from=f"Arista Master Pricing Automation Tool",
                              body=f'''
    Hello,

    Request for Quote (RFQ) from Arista Master Pricing tool.

    Please visit the link and review the RFQ where you may need to enter your response directly through the website.

    https://{url}/

    Kindly do not reply to srv-masterpricing@arista.com.
    For Questions related to RFQ please contact {','.join(cm['cc'])}

    Regards,
    Arista Master Pricing Automation Tool



                ''',
                              subject=f'''
                RFQ for {cm['cm']} from Arista MPA Tool
                ''',
                title=None,cc=list(cm['cc']))



@login_required
def file_serve(request):
    '''This is static file server for the file in rfx folder'''
    try:
        file = request.GET.get('file')
        fs = FileSystemStorage()
        files = open(os.path.join(settings.BASE_DIR, 'rfx/files/'+file), 'rb')
        response = HttpResponse(files, content_type="application/octet-stream")
        response['Content-Disposition'] = 'inline; filename=' + file

        return response
    except Exception as e:
        #print(e)
        raise Http404


@login_required
def save_predefined_filters(request):
    '''This will save the filter excel as a value in database to access same combination'''
    option = request.GET.get('option')
    if request.method == 'POST':
        name = request.POST.get('name')
        xlx = request.FILES['Upload_Excel']
        df = pd.read_excel(xlx)
        json_data = df.to_json()
        #print(name, 'Name of filter')
        predefined_filter(name='Un Named Filter' if name == '' else name,
                          data=json.dumps(json_data),
                          created_by=request.user
                          ).save()
        excel_filter(request, df)
        return HttpResponse('Success')
    elif option == 'filter':
        id = request.GET.get('id')
        df = pd.read_json(json.loads(
            predefined_filter.objects.get(id=id).data))
        excel_filter(request, df)
        return HttpResponse('Success')
    elif option == 'delete':
        id = request.GET.get('id')
        predefined_filter.objects.get(id=id).delete()
        return HttpResponse('Success deleted')
    else:
        filters = predefined_filter.objects.filter(created_by=request.user)
        #print(filters)
        return render(request,'rfx/components/predefined_filters.html',{'filters':filters})




# from django.shortcuts import render

# # Create your views here.

# import logging
# from inbound_email.signals import email_received

# def on_email_received(sender, **kwargs):
#     """Handle inbound emails."""
#     email = kwargs.pop('email')
#     request = kwargs.pop('request')
#     # your code goes here - save the email, respond to it, etc.
#     print(
#         "New email received from %s: %s",
#         email.from_email,
#         email.subject
#     )

# # pass dispatch_uid to prevent duplicates:
# # https://docs.djangoproject.com/en/dev/topics/signals/
# # email_received.connect(on_email_received, dispatch_uid="something_unique")
# email_received.connect(on_email_received, dispatch_uid="121weqsaqeawdxas1w12weds")

@multi_threading
def save_lock_access_notified_data(request, value, bool):
    '''
    This method save the lock access details
    '''
    try:
        data = RFX.objects.filter(
            id__in=value or request.session['current_filtered_RFX'])
        if data.exists() is True:
            for i in data:
                arista_pic = i.portfolio.Arista_PIC
                if i.Team == 'CMM Team' and i.sent_to != 'supplier':
                    supplier_email = suppliers_detail.objects.filter(Supplier_Name__icontains=i.Mfr_Name, Team=i.Team,is_active=True, Distributor__icontains=i.sent_to).values('user_model__email')
                elif i.Team == 'CMM Team' and i.sent_to == 'supplier':
                    supplier_email = suppliers_detail.objects.filter(Supplier_Name__icontains=i.Mfr_Name,is_active=True, Team=i.Team).filter(Q(Distributor__isnull=True) | Q(Distributor='')).values('user_model__email')
                else:
                    supplier_email=suppliers_detail.objects.filter(Supplier_Name__icontains=i.Mfr_Name,is_active=True, Team=i.Team).values('user_model__email')

                today = timezone.localtime(timezone.now())
                current_date = today.strftime("%m-%d-%Y, %H:%M:%S")
                cm_list = []
                global_cm = Portfolio.objects.filter(
                    Arista_Part_Number=i.portfolio.Arista_Part_Number, Quarter=Current_quarter()).distinct('cm').exclude(cm='Global')
                for s in global_cm.values_list('cm'):
                    cm_list.append(s[0])
                cm_set_list = set(cm_list)

                to = User.objects.filter(first_name=arista_pic.split('/')[0].split(' ')[0], last_name=arista_pic.split('/')[0].split(' ')[1]).values('email')
                
                jpe_cm_cc_email = User.objects.none()
                sgd_cm_cc_email = User.objects.none()
                fgn_cm_cc_email = User.objects.none()
                hbg_cm_cc_email = User.objects.none()
                jsj_cm_cc_email = User.objects.none()
                jmx_cm_cc_email = User.objects.none()
                if i.cm == 'JPE':
                    jpe_cm_cc_email = User.objects.filter(groups__name='JPE Contract Manufacturer').values('email')
                if i.cm == 'JSJ':
                    jsj_cm_cc_email = User.objects.filter(groups__name='JSJ Contract Manufacturer').values('email')
                if i.cm == 'JMX':
                    jmx_cm_cc_email = User.objects.filter(groups__name='JMX Contract Manufacturer').values('email')
                if i.cm == 'SGD':
                    sgd_cm_cc_email = User.objects.filter(groups__name='SGD Contract Manufacturer').values('email')
                if i.cm == 'FGN':
                    fgn_cm_cc_email = User.objects.filter(groups__name='FGN Contract Manufacturer').values('email')
                if i.cm == 'HBG':
                    hbg_cm_cc_email = User.objects.filter(groups__name='HBG Contract Manufacturer').values('email')

                sgd_cm_email = []
                for t in sgd_cm_cc_email:
                    to_dict = {"email": t['email']}
                    sgd_cm_email.append(to_dict)
                sgd_email = json.dumps(sgd_cm_email)

                jpe_cm_email = []
                for t in jpe_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jpe_cm_email.append(to_dict)
                jpe_email = json.dumps(jpe_cm_email)

                jsj_cm_email = []
                for t in jsj_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jsj_cm_email.append(to_dict)
                jsj_email = json.dumps(jsj_cm_email)

                jmx_cm_email = []
                for t in jmx_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jmx_cm_email.append(to_dict)
                jmx_email = json.dumps(jmx_cm_email)

                fgn_cm_email = []
                for t in fgn_cm_cc_email:
                    to_dict = {"email": t['email']}
                    fgn_cm_email.append(to_dict)
                fgn_email = json.dumps(fgn_cm_email)

                hbg_cm_email = []
                for t in hbg_cm_cc_email:
                    to_dict = {"email": t['email']}
                    hbg_cm_email.append(to_dict)
                hbg_email = json.dumps(hbg_cm_email)

                to_email_list = []
                for t in to:
                    to_dict = {"email": t['email']}
                    to_email_list.append(to_dict)
                to_email = json.dumps(to_email_list)

                supplier_email_list = []
                for c in supplier_email:
                    cc_dict = {"email": c['user_model__email']}
                    supplier_email_list.append(cc_dict)
                cc_email = json.dumps(supplier_email_list)

                created_by = request.user.first_name+" "+request.user.last_name
                try:
                    url = get_current_site(request).domain
                except:
                    url = ""
                notification = LockAccessEmailNotification(
                        Arista_Part_Number=i.Part_Number,
                        status_updated_by=created_by,
                        Mfr_Part_Number=i.Mfr_Part_Number,
                        Arista_PIC=arista_pic,
                        to=to_email,
                        supplier_email=cc_email,
                        team=i.Team,
                        cm=i.cm,
                        sent_to=i.sent_to,
                        created_at=current_date,
                        sgd_cm_email = sgd_email,
                        jpe_cm_email = jpe_email,
                        jsj_cm_email = jsj_email,
                        jmx_cm_email = jmx_email,
                        fgn_cm_email = fgn_email,
                        hbg_cm_email = hbg_email,
                        lock_status = bool,
                        Mfr_Name=i.Mfr_Name,
                        rfx_id=i.id,
                        current_url=url,
                        logged_in_user_group=request.user.groups.values('name')[0]['name']
                    )
                notification.save()
    except Exception as e:
        LOGGER.info(f'Error arises while modified lock access status {e}')

@multi_threading
def delete_data_with_approved_status(request, status, rfx_id):
    '''
    This method deleted the data with approved status as 'Approved'
    '''
    #print("Data Deleted for ", rfx_id)
    QuoteEmailNotification.objects.filter(Rfx_id=rfx_id, status=status).delete()
    LOGGER.info("Approval status data deleted for %s", rfx_id)

@multi_threading
def save_approval_status_notified_data(request, value, status, role):
    '''
    This method  handles data related to approval status
    '''
    try:
        data=RFX.objects.filter(id__in=value or request.session['current_filtered_RFX'])

        if data.exists() is True:
            for i in data:
                #print(i.cm, "save_approval_status_notified_data()")
                
                if role == 'PIC':
                    global_cm = Portfolio.objects.filter(
                        Arista_Part_Number=i.portfolio.Arista_Part_Number, Quarter=Current_quarter()).distinct('cm').exclude(cm='Global')
                    cm_list = []
                    for s in global_cm.values_list('cm'):
                        cm_list.append(s[0])
                    if ['JPE'] == cm_list:
                        jpe_cm_cc_email = User.objects.filter(groups__name='JPE Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = 'JPE'
                    elif ['SGD'] == cm_list:
                        sgd_cm_cc_email = User.objects.filter(groups__name='SGD Contract Manufacturer').values('email')
                        jpe_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = 'SGD'
                    elif ['FGN'] == cm_list:
                        fgn_cm_cc_email = User.objects.filter(groups__name='FGN Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = 'FGN'
                    elif ['HBG'] == cm_list:
                        hbg_cm_cc_email = User.objects.filter(groups__name='HBG Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = 'HBG'
                    elif ['JSJ'] == cm_list:
                        jsj_cm_cc_email = User.objects.filter(groups__name='JSJ Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = 'JSJ'
                    elif ['JMX'] == cm_list:
                        jmx_cm_cc_email = User.objects.filter(groups__name='JMX Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        data_cm = 'JMX'

                    elif "SGD" in cm_list or "JPE" in cm_list or "FGN" in cm_list or "HBG" in cm_list or "JSJ" in cm_list or "JMX" in cm_list:
                        jpe_cm_cc_email = User.objects.filter(groups__name='JPE Contract Manufacturer').values('email') if "JPE" in cm_list else User.objects.none()
                        sgd_cm_cc_email = User.objects.filter(groups__name='SGD Contract Manufacturer').values('email') if "SGD" in cm_list else User.objects.none()
                        fgn_cm_cc_email = User.objects.filter(groups__name='FGN Contract Manufacturer').values('email') if "FGN" in cm_list else User.objects.none()
                        hbg_cm_cc_email = User.objects.filter(groups__name='HBG Contract Manufacturer').values('email') if "HBG" in cm_list else User.objects.none()
                        jsj_cm_cc_email = User.objects.filter(groups__name='JSJ Contract Manufacturer').values('email') if "JSJ" in cm_list else User.objects.none()
                        jmx_cm_cc_email = User.objects.filter(groups__name='JMX Contract Manufacturer').values('email') if "JMX" in cm_list else User.objects.none()
                        data_cm = 'Global'
                    else:
                        jpe_cm_cc_email = User.objects.none()
                        sgd_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = 'Global'
                elif role == 'CMM':
                    if i.cm == 'SGD':
                        sgd_cm_cc_email = User.objects.filter(groups__name='SGD Contract Manufacturer').values('email')
                        jpe_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = i.cm
                    elif i.cm == 'JPE':
                        jpe_cm_cc_email = User.objects.filter(groups__name='JPE Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = i.cm
                    elif i.cm == 'FGN':
                        fgn_cm_cc_email = User.objects.filter(groups__name='FGN Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = i.cm
                    elif i.cm == 'HBG':
                        hbg_cm_cc_email = User.objects.filter(groups__name='HBG Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = i.cm
                    elif i.cm == 'JSJ':
                        jsj_cm_cc_email = User.objects.filter(groups__name='JSJ Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        jmx_cm_cc_email = User.objects.none()
                        data_cm = i.cm
                    elif i.cm == 'JMX':
                        jmx_cm_cc_email = User.objects.filter(groups__name='JMX Contract Manufacturer').values('email')
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        data_cm = i.cm
                    else:
                        jmx_cm_cc_email = User.objects.none()
                        sgd_cm_cc_email = User.objects.none()
                        jpe_cm_cc_email = User.objects.none()
                        hbg_cm_cc_email = User.objects.none()
                        jsj_cm_cc_email = User.objects.none()
                        fgn_cm_cc_email = User.objects.none()
                        data_cm = i.cm

                today = timezone.localtime(timezone.now())
                current_date = today.strftime("%m-%d-%Y, %H:%M:%S")
                bp_email = User.objects.filter(
                    groups__name='Super User').values('email')
                director_email = User.objects.filter(
                    groups__name='Director').values('email')
                gsm_manager_email = User.objects.filter(
                    groups__name='GSM Manager').values('email')
                to = User.objects.filter(first_name__icontains=i.portfolio.Arista_PIC.split('/')[0].split(' ')[0], last_name__icontains=i.portfolio.Arista_PIC.split('/')[0].split(' ')[-1]).values('email')
                
                director_email_list = []
                for d in director_email:
                    cc_dict = {"email": d['email']}
                    director_email_list.append(cc_dict)
                dictr_email = json.dumps(director_email_list)

                gsm_manager_email_list = []
                for g in gsm_manager_email:
                    cc_dict = {"email": g['email']}
                    gsm_manager_email_list.append(cc_dict)
                gsm_mger_email = json.dumps(gsm_manager_email_list)

                sgd_cm_email = []
                for t in sgd_cm_cc_email:
                    to_dict = {"email": t['email']}
                    sgd_cm_email.append(to_dict)
                sgd_email = json.dumps(sgd_cm_email)

                jpe_cm_email = []
                for t in jpe_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jpe_cm_email.append(to_dict)
                jpe_email = json.dumps(jpe_cm_email)

                jsj_cm_email = []
                for t in jsj_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jsj_cm_email.append(to_dict)
                jsj_email = json.dumps(jsj_cm_email)

                jmx_cm_email = []
                for t in jmx_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jmx_cm_email.append(to_dict)
                jmx_email = json.dumps(jmx_cm_email)

                fgn_cm_email = []
                for t in fgn_cm_cc_email:
                    to_dict = {"email": t['email']}
                    fgn_cm_email.append(to_dict)
                fgn_email = json.dumps(fgn_cm_email)

                hbg_cm_email = []
                for t in hbg_cm_cc_email:
                    to_dict = {"email": t['email']}
                    hbg_cm_email.append(to_dict)
                hbg_email = json.dumps(hbg_cm_email)

                to_email_list = []
                for t in to:
                    to_dict = {"email": t['email']}
                    to_email_list.append(to_dict)
                to_email = json.dumps(to_email_list)

                bp_email_list = []
                for c in bp_email:
                    cc_dict = {"email": c['email']}
                    bp_email_list.append(cc_dict)
                cc_email = json.dumps(bp_email_list)
                created_by = request.user.first_name+" "+request.user.last_name

                try:url=get_current_site(request).domain
                except:url=""

                notification = QuoteEmailNotification(
                    Arista_Part_Number=i.Part_Number,
                    created_by=created_by,
                    Mfr_Part_Number=i.Mfr_Part_Number,
                    Arista_PIC=i.portfolio.Arista_PIC,
                    to=to_email,
                    bp_email=cc_email,
                    team=i.Team,
                    cm=i.cm if role == 'CMM' else data_cm,
                    sent_to=i.sent_to,
                    created_at=current_date,
                    sgd_cm_email=sgd_email,
                    jpe_cm_email=jpe_email,
                    fgn_cm_email=fgn_email,
                    hbg_cm_email=hbg_email,
                    jsj_cm_email=jsj_email,
                    jmx_cm_email=jmx_email,
                    director_email=dictr_email,
                    gsm_manager_email=gsm_mger_email,
                    status=status,
                    approval_status_modified_by_role=role,
                    logged_in_user_group=request.user.groups.values('name')[0]['name'],
                    Mfr_Name=i.Mfr_Name,
                    Rfx_id=i.id,
                    current_url=url
                )
                notification.save()
                LOGGER.info(
                    "PIC approval Accept notification details saved successfully", exc_info=1)
    except:
        LOGGER.error(
            "Unable to save PIC approval Accept notification details", exc_info=1)


@multi_threading
def save_quote_notified_data(request, value, status):
    '''
    This method stores make_quote method returned data for quote_email_processing
    '''
    try:
        data = RFX.objects.filter(id__in=value)
        if data.exists() is True:
            for i in data:
                today = timezone.localtime(timezone.now())
                current_date = today.strftime("%m-%d-%Y, %H:%M:%S")
                bp_email = User.objects.filter(groups__name='Super User').values('email')
                to = User.objects.filter(first_name__icontains=i.portfolio.Arista_PIC.split('/')[0].split(' ')[0], last_name=i.portfolio.Arista_PIC.split('/')[0].split(' ')[-1]).values('email')
                gsm_mger_email = User.objects.filter(groups__name='GSM Manager').values('email')
                
                jpe_cm_cc_email = User.objects.none()
                sgd_cm_cc_email = User.objects.none()
                fgn_cm_cc_email = User.objects.none()
                hbg_cm_cc_email = User.objects.none()
                jsj_cm_cc_email = User.objects.none()
                jmx_cm_cc_email = User.objects.none()

                if i.cm == 'JPE':
                    jpe_cm_cc_email = User.objects.filter(groups__name='JPE Contract Manufacturer').values('email')

                if i.cm == 'SGD':
                    sgd_cm_cc_email = User.objects.filter(groups__name='SGD Contract Manufacturer').values('email')

                if i.cm == 'FGN':
                    fgn_cm_cc_email = User.objects.filter(groups__name='FGN Contract Manufacturer').values('email')
                
                if i.cm == 'HBG':
                    hbg_cm_cc_email = User.objects.filter(groups__name='HBG Contract Manufacturer').values('email')
                
                if i.cm == 'JSJ':
                    hbg_cm_cc_email = User.objects.filter(groups__name='JSJ Contract Manufacturer').values('email')
                
                if i.cm == 'JMX':
                    hbg_cm_cc_email = User.objects.filter(groups__name='JMX Contract Manufacturer').values('email')
                    
                    


                sgd_cm_email = []
                for t in sgd_cm_cc_email:
                    to_dict = {"email": t['email']}
                    sgd_cm_email.append(to_dict)
                sgd_email = json.dumps(sgd_cm_email)

                jpe_cm_email = []
                for t in jpe_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jpe_cm_email.append(to_dict)
                jpe_email = json.dumps(jpe_cm_email)

                jsj_cm_email = []
                for t in jsj_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jsj_cm_email.append(to_dict)
                jsj_email = json.dumps(jsj_cm_email)

                jmx_cm_email = []
                for t in jmx_cm_cc_email:
                    to_dict = {"email": t['email']}
                    jmx_cm_email.append(to_dict)
                jmx_email = json.dumps(jmx_cm_email)

                fgn_cm_email = []
                for t in fgn_cm_cc_email:
                    to_dict = {"email": t['email']}
                    fgn_cm_email.append(to_dict)
                fgn_email = json.dumps(fgn_cm_email)

                hbg_cm_email = []
                for t in hbg_cm_cc_email:
                    to_dict = {"email": t['email']}
                    hbg_cm_email.append(to_dict)
                hbg_email = json.dumps(hbg_cm_email)

                to_email_list = []
                for t in to:
                    to_dict = {"email": t['email']}
                    to_email_list.append(to_dict)
                to_email = json.dumps(to_email_list)

                bp_email_list = []
                for c in bp_email:
                    cc_dict = {"email": c['email']}
                    bp_email_list.append(cc_dict)
                cc_email = json.dumps(bp_email_list)
                try:url=get_current_site(request).domain
                except:url=""
                
                notification = QuoteEmailNotification(Arista_Part_Number=i.Part_Number,
                        created_by=' ',
                        Mfr_Part_Number=i.Mfr_Part_Number,
                        Arista_PIC=i.portfolio.Arista_PIC,
                        to=to_email,
                        bp_email=cc_email,
                        team=i.Team,
                        cm=i.cm,
                        sent_to=i.sent_to,
                        created_at=current_date,
                        sgd_cm_email = sgd_email,
                        jpe_cm_email = jpe_email,
                        fgn_cm_email = fgn_email,
                        hbg_cm_email = hbg_email,
                        jsj_cm_email = jsj_email,
                        jmx_cm_email = jmx_email,
                        is_quoted=True,
                        status='Quoted',
                        Mfr_Name=i.Mfr_Name,
                        Rfx_id=i.id,
                        current_url=url
                )
                notification.save()
    except Exception as e:
        LOGGER.info(f'Unable to save quote email details due to', exc_info=1)
from string import ascii_uppercase


def check_auto_wipe(part):
    approved_count=RFX.objects.filter(sent_quater=Current_quarter(), quarter=part.quarter).filter(Part_Number=part.Part_Number,cm=part.cm,approval_status='Approved').count()
    from MasterPricing.models import MP_download_table
    if not approved_count:

        if part.cm=='Global':
            data_JPE=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download='JPE')
            data_SGD=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download='SGD')
            data_FGN=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download='FGN')
            data_HBG=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download='HBG')
            data_JSJ=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download='JSJ')
            data_JMX=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download='JMX')
            if data_JPE:
                instance_jpe=data_JPE.first()
                if instance_jpe.standard_price_q1:
                    instance_jpe.reset_descion
            if data_SGD:
                instance_sgd=data_SGD.first()
                if instance_sgd.standard_price_q1:
                    instance_sgd.reset_descion
            if data_FGN:
                instance_fgn=data_FGN.first()
                if instance_fgn.standard_price_q1:
                    instance_fgn.reset_descion
            if data_HBG:
                instance_hbg=data_HBG.first()
                if instance_hbg.standard_price_q1:
                    instance_hbg.reset_descion
            if data_JSJ:
                instance_jsj=data_JSJ.first()
                if instance_jsj.standard_price_q1:
                    instance_jsj.reset_descion
            if data_JMX:
                instance_jmx=data_JMX.first()
                if instance_jmx.standard_price_q1:
                    instance_jmx.reset_descion
            print('***************************')
        elif part.portfolio.Ownership=='Arista' :
            data_cm=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download=part.cm)

            if data_cm:
                instance=data_cm.first()
                if instance.standard_price_q1:
                    instance.reset_descion
        elif part.portfolio.Ownership!='Arista' :
            data_cm=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download=part.cm)
            if data_cm:
                instance=data_cm.first()
                if instance.go_with_pic_price=='Yes':
                    if instance.standard_price_q1:
                        instance.reset_descion

def erase_mp(part):
    print(f'WIPING MP FOR {part}')
    print(part.Item_Price)
    from MasterPricing.models import MP_download_table
    data_cm=MP_download_table.objects.filter(Part_Number=part.Part_Number,sent_quater=Current_quarter(),CM_download=part.cm)
    if data_cm:
        if part.sent_to=='cm':
            instance=data_cm.first()
            if instance.go_with_pic_price!='Yes':
                if instance.standard_price_q1:
                    instance.reset_descion

def his_quotes_rfx(user):
    supplier=suppliers_detail.objects.filter(user_model=user,is_active=True)
    query_set=Q()
    data = RFX.objects.none()
    if supplier.exists():
        for x in supplier:
            query_set |= Q(sent_to=x.Distributor or 'supplier',Mfr_Name=x.Supplier_Name,portfolio__Arista_PIC__icontains=f'{x.User_created.first_name} {x.User_created.last_name}')

        data = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(2,this_quarter=True)).filter(query_set)
    return data
        
def download_award(request,partnumber,supplier=True):
    '''
    This will return Split finalized excel
    '''
    fields=[
        'Part_Number',
        'Mfr_Name',
        'Item_Price',
        'Mfr_Part_Number',
        'cm',
        'Lead_Time',
        'MOQ',
        'portfolio__Qualification_Status',
        'id',
        'quarter',
        'sent_to',
        'List',
        'tarrif',
        'COO',
        'Inco_Term',
        'Freight_cost',
        'Life_Cycle',
        'Comments',
        'NCNR',
        'PO_Delivery',
        'soft_hard_tool',
        'sent_quater',
        'portfolio__Rev',
        'portfolio__Mfr_Part_Lifecycle_Phase',
        'portfolio__Parts_controlled_by',
        'portfolio__Item_Desc',
        'portfolio__Ownership',
        'portfolio__Arista_PIC',
        ]
    df=RFX.objects.filter(id__in=partnumber).order_by('Part_Number').values(*fields).to_dataframe()
    df=df.filter(fields)
    df_award=pd.DataFrame(data={'rfx':RFX.objects.filter(id__in=df['id'].to_list() )})
    #print(df_award)
    df_award['id']=df_award['rfx'].apply(lambda x:x.id)
    df_award['id']=df_award['id'].astype('int')
    df['id']=df['id'].astype('int')
    if supplier:
        df_award['Split Alloted(%)']=df_award['rfx'].apply(lambda x:x.award)
    else:
        df_award['Split Alloted(%)']=df_award['rfx'].apply(lambda x:x.award_pid)
    del df_award['rfx']
    #print(df)
    df=df.merge(df_award,on='id')

    ###portfolio
    if supplier:
        qq=Portfolio.objects.filter(Quarter=Current_quarter(),Team='GSM Team',Number__in=df.loc[df['Split Alloted(%)']>0]['Part_Number'].to_list())
    else:
        qq=Portfolio.objects.filter(Quarter=Current_quarter(),Team='GSM Team',Number__in=df['Part_Number'].to_list())

    initial_q=qq.values(
        "cm",
        "Number",
        "Ownership",
        "Mfr_Name",
        "Mfr_Part_Number",

        "cm_Quantity_Buffer_On_Hand",
        "cm_Quantity_On_Hand_CS_Inv",
        "Open_PO_due_in_this_quarter",
        "Open_PO_due_in_next_quarter",
        "Delivery_Based_Total_OH_sum_OPO_this_quarter",
        "PO_Based_Total_OH_sum_OPO",
        "CQ_ARIS_FQ_sum_1_SANM_Demand",
        "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
        "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
        "CQ_sum_3_ARIS_FQ_SANM_Demand",
    ).to_dataframe()
    #need to add color once CM name added
    cms=['Global','SGD','JPE','FGN','HBG','JSJ','JMX']
    cms_colours=['#ffffff','#40bf40','#FFC000','#fffa45','#c8b88a','#05afef','#948a54']
    cms_colour=iter(cms_colours)
    for cm in cms:
        df=pd.merge(df,initial_q.loc[initial_q['cm']==cm],how='left',left_on=['Part_Number','portfolio__Ownership','Mfr_Name','Mfr_Part_Number'], right_on =['Number','Ownership','Mfr_Name','Mfr_Part_Number'],right_index=False,suffixes=[f'',f'_{cm}'],)

    for x in cms:
        try:del df[f'cm_{x}']
        except:pass
        try:del df[f'Number_{x}']
        except:pass
        try:del df[f'Ownership_{x}']
        except:pass
        try:del df[f'Number']
        except:pass
        try:del df[f'Ownership']
        except:pass
    cols={
    "cm_Quantity_Buffer_On_Hand":"CM Quantity Buffer On Hand",
    "cm_Quantity_On_Hand_CS_Inv":"CM Quantity On Hand + CS Inv",
    "Open_PO_due_in_this_quarter":"Open PO Due (Current Quarter)",
    "Open_PO_due_in_next_quarter":"Open PO Due (Q+1)",
    "Delivery_Based_Total_OH_sum_OPO_this_quarter":"CM Total OH + OPO (Current Quarter)",
    "PO_Based_Total_OH_sum_OPO":"CM Total OH + OPO (Q & Q+1)",
    "CQ_ARIS_FQ_sum_1_SANM_Demand":"Current Quarter Demand",
    "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":"Q+1 Demand",
    "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand":"Q+2 Demand",
    "CQ_sum_3_ARIS_FQ_SANM_Demand":"Q+3 Demand",
    
    }
    rename_col={}
    for cm in cms:
        for k,v in cols.items():
            if cm=='Global':
                rename_col[f'{k}']=v
            else:
                rename_col[f'{k}_{cm}']=v

    df.rename(columns=rename_col,inplace=True)
    
    with BytesIO() as b:
        with pd.ExcelWriter(b) as writer:
            df.rename(columns=column_names_analysis, inplace=True)
            df.to_excel(writer, index=False, sheet_name='Award Letter',startrow=1)
            workbook = writer.book
            worksheet = writer.sheets['Award Letter']
            split_data=workbook.add_format({
                    'fg_color': '#C9D8EF',
                    })
            
            worksheet.set_column('AC1:AC1',None,split_data)
            
            headers_alpha=list(islice(multiletters(ascii_uppercase), 200))
            #print(headers_alpha)
            from_col='AD'
            from_col_place=headers_alpha.index(from_col)
            for cm in cms:
                merge_format1 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': cms_colour.__next__(),
                })
                ranged=headers_alpha[from_col_place:from_col_place+10]
                #print(ranged[0],ranged[-1])
                worksheet.merge_range(
                f'{ranged[0]}1:{ranged[-1]}1', f'{cm}', merge_format1)
                from_col_place=from_col_place+10
                
           

            writer.save()

            server=request.get_host()
            server=server.replace('arista-mpat','').replace('.inesssolutions.net','')
            response = HttpResponse(
                b.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'inline; filename=Award Letter From={server} {timezone.localtime(timezone.now()).strftime("Date=%m-%d-%Y Time=%H.%M.%S")}.xlsx'
            return response

def CM_Quoting(request):
    quotes = CM_Quotes()
    quotes.rfq_id = request.POST.get('rfq_id')
    quotes.Item_Price = request.POST.get('CM_Item_Price')
    quotes.Lead_Time = request.POST.get('CM_Lead_Time')
    quotes.MOQ = request.POST.get('CM_MOQ')
    quotes.List = request.POST.get('CM_List')
    quotes.tarrif = request.POST.get('CM_tarrif')
    quotes.NCNR = request.POST.get('CM_NCNR')
    quotes.PO_Delivery = request.POST.get('CM_PO_Delivery')
    quotes.CM_comments = request.POST.get('CM_Comments')
    quotes.Supplier_Distributor_name_from_cm = request.POST.get('CM_Supplier_Distributor_Name')
    quotes.CM_Manufacturer = request.POST.get('CM_MFR_Name')
    quotes.CM_mpn = request.POST.get('CM_MPN')
    quotes.Quote_status = request.POST.get('CM_Quote_Status')
    quotes.save()
    splits = split_for_cm_quote(request.POST.get('rfq_id'))
    print(splits)
    for_std=[]
    for split in splits:
        CM_Quotes.objects.filter(id=split['id']).update(suggested_split=split['split'])
        for_std.append(split['id'])
    std=cm_quote_std_generator(CM_Quotes.objects.filter(id__in=for_std))
    po_del=cm_po_delivery_calc(CM_Quotes.objects.filter(id__in=for_std))
    cmqs=CM_Quotes.objects.filter(rfq_id=request.POST.get('rfq_id'))
    lt = "/".join(map(str, cmqs.values_list('Lead_Time',flat=True)))
    moq = "/".join(map(str, cmqs.values_list('MOQ',flat=True)))
    mfr = "/".join(cmqs.values_list('CM_Manufacturer',flat=True))
    sup = "/".join(cmqs.values_list('Supplier_Distributor_name_from_cm',flat=True))
    mpn = "/".join(cmqs.values_list('CM_mpn',flat=True))
    list = "/".join(cmqs.values_list('List',flat=True))
    tarrif = "/".join(cmqs.values_list('tarrif',flat=True))
    print(po_del,std)
    return JsonResponse({'status':'200','message':"CM Quote Added Successfully",'rfx_id':request.POST.get('rfq_id'),'po_del':po_del,'std':std,'lt':lt,'moq':moq,'mfr':mfr,'sup':sup,'mpn':mpn,'list':list,'tarrif':tarrif},safe=False)
    
def upload_cm_quote(request):
    status = request.GET.get('status')
    Inco_Term = ["CFR", "CIF", "CIP", "CPT", "DAF", "DAP", "DAT", "DDP", "DDU", "DEQ",
                 "DES", "EXG", "EXW", "FAS", "FCA", "FH", "FOB", "FOC", "FOR", "FOT", "FRD", "HC","N/A" ]
    Lifecycle_Phase = ["EOL", "Active", "Obsolete"]
    column_names_cm = {
        "id": "RFQ Id",
        "quarter": 'quarter',
        "Part_Number": 'Arista Part Number',
        "cm": 'cm',
        "portfolio__cm_Part_Number": 'CM Part Number',
        "portfolio__Cust_consign": 'Cust Consign',
        "portfolio__Item_Desc": 'Item Desc',
        "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand": 'Quarterly Demand',
        "Annual Demand": "Annual Demand",
        "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista": 'Delta Demand.',
        "portfolio__Original_PO_Delivery_sent_by_Mexico": 'Original PO Delivery',
        "portfolio__Ownership": 'Ownership',
        "previous_Item_price": 'Previous quarter Item Price ($)',
        "previous_lead_time": 'Previous Quarter Lead time (In Weeks)',
        "previous_moq": 'Previous Quarter MOQ',
        "suggested_moq": 'Suggested MOQ',
        "Quote_Type": 'Quote Type',
        "portfolio__Arista_PIC": 'Arista PIC',
        "portfolio__Arista_pic_comment": 'Arista pic comment',
        "Item_Price": 'Item Price ($) *',
        "Lead_Time": 'CM MFG Lead time (in weeks) *',
        "MOQ": 'CM MOQ *',
        "List": 'List',
        "tarrif": 'Tariff',
        "NCNR": 'CM NCNR',
        "PO_Delivery": 'CM MPN PO/Delivery *',
        'CM_Manufacturer': 'CM Manufacturer Name *',
        "Supplier_Distributor_name_from_cm": 'CM Supplier / Distributor Name *',
        "CM_mpn": 'CM MPN *',
        "CM_buyer": 'CM Buyer Name *',
        "CM_qty_std_source": 'Current Qtr Std Cost Source',
        'Quote_status': 'Quote Status',
        "Comments": 'CM Comments',
        "manual_split":"Business Split %",
    }
    #print('into upload')
    column_names_decode = {v: k for k, v in column_names_cm.items()}
    file = request.FILES['Upload_Excel']
    df = pd.read_excel(file, header=1)
    df.rename(columns=column_names_decode, inplace=True)

    filtered_df = df.dropna(subset=[
        "Item_Price",
        "Lead_Time",
        "MOQ",
        "PO_Delivery",
        "CM_Manufacturer",
        "Supplier_Distributor_name_from_cm",
        "CM_mpn",
        "manual_split",
    ])

    filter_df2=df.loc[df['Quote_status'] == 'No BID']
    filter_df3 = df[pd.isnull(df['manual_split'])]
    filtered_df=pd.concat([filtered_df,filter_df2])
    business_split_issue=filtered_df.loc[filtered_df.groupby(['id'])['manual_split'].transform(func=sum)!=100,:]
    business_split_issue=business_split_issue.loc[business_split_issue['Quote_status'] != 'No BID']
    filtered_df=filtered_df.loc[filtered_df.groupby(['id'])['manual_split'].transform(func=sum)==100,:]
    filtered_df=pd.concat([filtered_df,filter_df3])
    print(filtered_df)
    for index, row in filtered_df.iterrows():
        if CM_Quotes.objects.filter(rfq_id=row['id'],CM_mpn=row['CM_mpn']).exists():
            quotes = CM_Quotes.objects.filter(rfq_id=row['id'],CM_mpn=row['CM_mpn'])[:1].get()
        else:
            quotes = CM_Quotes()
        quotes.rfq_id = row['id']
        quotes.Item_Price = row['Item_Price']
        quotes.Lead_Time = row['Lead_Time']
        quotes.MOQ = row['MOQ']
        quotes.List = row['List']
        quotes.tarrif = row['tarrif']
        quotes.NCNR = row['NCNR']
        quotes.PO_Delivery = row['PO_Delivery']
        quotes.CM_comments = row['Comments']
        quotes.Supplier_Distributor_name_from_cm = row['Supplier_Distributor_name_from_cm']
        quotes.CM_Manufacturer = row['CM_Manufacturer']
        quotes.CM_mpn = row['CM_mpn']
        quotes.Quote_status = row['Quote_status']
        quotes.manual_split = row['manual_split']
        quotes.split_type = "Automated" if not row['manual_split'] >= 0 else "Manual"
        quotes.save()
        splits = split_for_cm_quote(row['id'])
        print(splits)
        for_std=[]
        for split in splits:
            CM_Quotes.objects.filter(id=split['id']).update(suggested_split=split['split'])
            for_std.append(split['id'])
        std=cm_quote_std_generator(CM_Quotes.objects.filter(id__in=for_std))
        print(std)
    error_rows = []
    error_index = []
    list_of_id=[]
    filtered_df = df.dropna(subset=[
        "Item_Price",
        "Lead_Time",
        "MOQ",
        "PO_Delivery",
        "CM_Manufacturer",
        "Supplier_Distributor_name_from_cm",
        "CM_mpn",
        "manual_split",
    ])
    print(filtered_df)
    filter_df2=df.loc[df['Quote_status'] == 'No BID']
    filter_df3 = df[pd.isnull(df['manual_split'])]
    filtered_df=filtered_df.loc[filtered_df.groupby(['id'])['manual_split'].transform(func=sum)==100,:]
    filtered_df=pd.concat([filtered_df,filter_df2])
    filtered_df=pd.concat([filtered_df,filter_df3])
    non_nan_list = filtered_df.index.tolist()
    filtered_df.drop_duplicates(subset=['id'],inplace=True)
    if has_permission(request.user, 'JPE Contract Manufacturer'):
        parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JPE').filter(sent_to='cm').order_by('created_on')
    elif has_permission(request.user, 'JSJ Contract Manufacturer'):
        parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JSJ').filter(sent_to='cm').order_by('created_on')
    elif has_permission(request.user, 'JMX Contract Manufacturer'):
        parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='JMX').filter(sent_to='cm').order_by('created_on')
    elif has_permission(request.user, 'SGD Contract Manufacturer'):
        parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='SGD').filter(sent_to='cm').order_by('created_on')
    elif has_permission(request.user, 'FGN Contract Manufacturer'):
        parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='FGN').filter(sent_to='cm').order_by('created_on')
    elif has_permission(request.user, 'HBG Contract Manufacturer'):
        parts = RFX.objects.filter(sent_quater=Current_quarter(), quarter__in=get_Next_quarter(3, this_quarter=True)).filter(Team='CMM Team').filter(cm='HBG').filter(sent_to='cm').order_by('created_on')
    else:
        parts = RFX.objects.none()
    success_count=0
    for index, row in filtered_df.iterrows():
        #try:
        if row['Quote_status'] == 'No BID':
            data = parts.get(id=row['id'])
            data.Quote_status = 'No BID'
            data.Comments = row['Comments']
            data.save(user=request.user)
            success_count += 1
            #print('Saved')

        else:
            print('inside quote')
            data = parts.get(id=row['id'])
            cmqs = CM_Quotes.objects.filter(rfq_id=row['id'])
            cm_quotes = cmqs.aggregate(LT=Avg('Lead_Time'),MQ=Avg('MOQ'))
            splits = split_for_cm_quote(row['id'])
            for_std = [i['id'] for i in splits]
            po_del=cm_po_delivery_calc(CM_Quotes.objects.filter(id__in=for_std))
            print(po_del)
            mfr = "/".join(cmqs.values_list('CM_Manufacturer',flat=True))
            sup = "/".join(cmqs.values_list('Supplier_Distributor_name_from_cm',flat=True))
            mpn = "/".join(cmqs.values_list('CM_mpn',flat=True))
            list = "/".join(cmqs.values_list('List',flat=True))
            tarrif = "/".join(cmqs.values_list('tarrif',flat=True))
            cm_std_cost = cmqs[:1].get().std_cost
            if data.sent_to=='cm':
                if data.Item_Price!=round(float(cm_std_cost), 5):
                    erase_mp(data)
                elif data.Lead_Time != int(cm_quotes['LT']):
                    erase_mp(data)
                elif int(data.MOQ) != int(cm_quotes['MQ']):
                    erase_mp(data)
                elif data.List != list:
                    erase_mp(data)
                elif data.tarrif != tarrif:
                    erase_mp(data)
                elif data.PO_Delivery != po_del:
                    erase_mp(data)
                elif data.Quote_Type != row['Quote_Type']:
                    erase_mp(data)
                elif data.Supplier_Distributor_name_from_cm != sup:
                    erase_mp(data)
                elif data.CM_mpn != mpn:
                    erase_mp(data)
                elif data.CM_Manufacturer != mfr:
                    erase_mp(data)
                else:
                    print('No changes')

            data.Item_Price = round(float(cm_std_cost), 5)
            data.Lead_Time = int(cm_quotes['LT'])
            data.MOQ = int(cm_quotes['MQ'])
            data.List = list
            data.tarrif = tarrif
            data.NCNR = row['NCNR']
            data.PO_Delivery = po_del
            data.Quote_Type = row['Quote_Type']
            # data.Region=row['Region']
            # data.Geo=row['Geo']
            data.Quote_status = 'Quoted'
            data.Supplier_Distributor_name_from_cm = sup
            data.CM_mpn = mpn
            # data.CM_buyer = row['CM_buyer']
            # data.CM_qty_std_source = row['CM_qty_std_source']
            data.CM_Manufacturer = mfr
            data.Comments = row['Comments']
            data.save(user=request.user,Quote=True)
            success_count += 1
            #print('Saved')
            list_of_id.append(data.id)
        #except Exception as e:
        #    error_rows.append(e)
        #    error_index.append(index)
        #    LOGGER.error("LOG_MESSAGE", exc_info=1)
    #print(error_rows)
    status="error" if not business_split_issue.empty else "success"
    return JsonResponse({'status':status,'message':'Quote Submited Sucessfully','error_table':business_split_issue.to_html(index=False, justify='center', na_rep='', classes='compact table table-xs nowarp font-small-3 table-responsive table-striped text-nowarp'),'success_count':success_count})

@login_required
def cm_manual_split_set(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        cms = request.GET.get('cms')
        data = RFX.objects.get(id=id)
        if has_group(request.user,'CMM Team') or request.user.is_superuser:
            data = RFX.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm', cm=cms)[:1].get()
            id=data.id
        if data.quote_freeze == False:
            datas = CM_Quotes.objects.filter(rfq_id=id)
        else:
            datas = 'No_rights'
        print(datas)
        return render(request, 'rfx/components/cm_split_form.html', {'data': datas,'instance':data})
    if request.method == 'POST':
        id = request.POST.getlist('id')
        split_value = [float(x) for x in request.POST.getlist('split_value')]
        if sum(split_value) == 100:
            split_comments = request.POST.getlist('comments')
            for x in range(len(id)):
                data = CM_Quotes.objects.filter(id=id[x])
                if has_group(request.user,'CMM Team') or request.user.is_superuser:
                    data.update(
                        arista_suggested=split_value[x],
                        arista_comments=split_comments[x],
                    )
                else:
                    data.update(
                        manual_split=split_value[x],
                        split_type='Manual',
                        CM_comments=split_comments[x],
                    )
            std=cm_quote_std_generator(CM_Quotes.objects.filter(id__in=id).filter(manual_split__gt=0))
            return JsonResponse({'status': 200, 'rfq_id': int(data[0].rfq_id), 'message': 'Split Updated'})
        else:
            #print(split_value)
            return JsonResponse({'status': 403, 'rfq_id': int(data[0].rfq_id), 'message': 'Split Not Updated'})

@login_required
def cm_quote_analysis(request):
    columns = {
        'RFX_id':'RFX ID',
        'Part_Number': 'Part Number',
        'Mfr_Name': 'Mfr Name',
        'Mfr_Part_Number': 'Mfr Part Number',
        'CM_mpn':'CM MPN',
        'CM_Manufacturer':'CM Manufacturer',
        'std_cost': 'Std Cost',
        'Item_Price':'Item Price',
        'MOQ':'MOQ',
        'Lead_Time':'Lead Time',
        'List':'List',
        'tarrif':'Tarrif',
        'NCNR':'NCNR',
        'PO_Delivery':'PO Delivery',
        'split_type':'Split Type',
        'suggested_split':'Suggested Split',
        'arista_suggested':'Arista Suggested',
        'manual_split':'Manual Split',
        'CM_comments':'CM Comments',
        'arista_comments':'Arista Comments',
        'sent_to': 'Sent to',   
        'Quoted_by': 'Supplier/Dist. Quoted By'
    }
    if CM_Quotes.objects.exists():
        q_Supplier = RFX.objects.filter(sent_quater=Current_quarter(), Team='CMM Team', quarter__in=get_Next_quarter(1, this_quarter=True)).filter(sent_to='cm')
        rfxs = q_Supplier.values('id','RFX_id','Part_Number','Mfr_Name','Mfr_Part_Number','sent_to','Quoted_by').to_dataframe()
        cmquotes=pd.DataFrame(CM_Quotes.objects.all().values())
        cmquotes['rfq_id']=cmquotes['rfq_id'].astype(int)
        #ids=CM_Quotes.objects.all().values_list('rfq_id',flat=True)
        #rfxs=pd.DataFrame(RFX.objects.filter(id__in=list(ids)).values('id','RFX_id','Part_Number','Mfr_Name','Mfr_Part_Number','sent_to','Quoted_by'))
        cmquotes=pd.merge(rfxs, cmquotes, left_on='id', right_on='rfq_id', how='right')
        field = [k for k, v in columns.items()]
        data = cmquotes.filter(field)
        data.fillna(value=np.nan, inplace=True)
        data.rename(columns=columns, inplace=True)
        data.fillna('-', inplace=True)
    else:
        data = pd.DataFrame(columns=columns)
    return JsonResponse({'table': data.to_html(classes='table  table-bordered table-striped text-nowrap table-xs font-small-2 export_table', table_id='cm_quote_analysis_table', justify='center', index=False, na_rep='-')})
    