import os
import django
#mark django settings module as settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InESS.settings')
django.setup()
import math
from django.shortcuts import render,redirect
from portfolio.models import *
from MasterPricing.models import *
from rfx.models import *
from django.contrib.auth.models import User, Group
import pytz
import concurrent.futures
import random
from Slate_CMT.templatetags.cmt_helper import *
# from Dashboard.templatetags.CMM_GSM_dashboard_helper import *
from django.http import JsonResponse,HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import get_template
import random
import string
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, Http404
import threading
import pandas as pd
from os import listdir
from os.path import isfile, join
from Slate_CMT import settings
from io import BytesIO
import numpy as np
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import random
# from datetime import datetime
import traceback
import sys
from django.core.mail import send_mail

#from pandarallel import pandarallel
import pandas as pd

import json
from datetime import timedelta
import datetime
from Slate_CMT.templatetags.masterprice_helper import *

from django.core.mail import EmailMessage
from django.template.loader import get_template

from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
import logging
from MasterPricing.models import MP_download_table
from django.utils import timezone
from django.db import connection
# from InputDB.views import masterpricing_sisense


# Create your views here.

LOGGER = logging.getLogger(__name__)
def is_number(string):
    '''Static function to check if Number'''
    try:
        float(string)
        return True
    except :
        return False
@login_required
def master_pricing_index(request):
    '''This function will provide index base page for Master pricing tab '''
    ##print(request.method)
    if has_permission(request.user,"PIC") or has_permission(request.user,"Manager") or has_permission(request.user,"Contract Manufacturer") or has_permission(request.user,"BP Team"):
        try:
            media_path = settings.MEDIA_ROOT +"QuarterHistory/"
            myfiles = [f for f in listdir(media_path) if isfile(join(media_path, f))]
        except:
            myfiles=[]
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        logic_GSM,created=master_temp.objects.get_or_create(Team='GSM Team')
        logic_CMM,created=master_temp.objects.get_or_create(Team='CMM Team')
        logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
        Quarter_History=MP_download_table.objects.exclude(Quarter=Current_quarter()).values_list('Quarter',flat=True).distinct()
        return render(request, "MasterPricing/index.html",{'files':myfiles,'logic_GSM':logic_GSM,'logic_CMM':logic_CMM,'logic_BP':logic_BP,'Quarter_History':Quarter_History})
    else:
        return render(request,'404.html')

@login_required
def masterpartlistsidebar(request):
    '''This will provide the initial data for the master pricing side bar component based on the CM and PIC'''
    SGD_parts=Portfolio.objects.filter(Quarter=Current_quarter(),cm='SGD').values_list('Number',flat=True).distinct('Number')
    JPE_parts=Portfolio.objects.filter(Quarter=Current_quarter(),cm='JPE').values_list('Number',flat=True).distinct('Number')
    FGN_parts=Portfolio.objects.filter(Quarter=Current_quarter(),cm='FGN').values_list('Number',flat=True).distinct('Number')
    HBG_parts=Portfolio.objects.filter(Quarter=Current_quarter(),cm='HBG').values_list('Number',flat=True).distinct('Number')
    JSJ_parts=Portfolio.objects.filter(Quarter=Current_quarter(),cm='JSJ').values_list('Number',flat=True).distinct('Number')
    JMX_parts=Portfolio.objects.filter(Quarter=Current_quarter(),cm='JMX').values_list('Number',flat=True).distinct('Number')

    parts=[
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Arista').filter(Part_Number__in=SGD_parts.filter(Ownership='Arista')).exclude(sent_to='cm').filter(cm__in=['SGD','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Arista').filter(Part_Number__in=JPE_parts.filter(Ownership='Arista')).exclude(sent_to='cm').filter(cm__in=['JPE','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            ##sanmina
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Sanmina').filter(Part_Number__in=SGD_parts.filter(Ownership='Sanmina')).filter(cm__in=['SGD','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            ##jabil
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Jabil').filter(Part_Number__in=JPE_parts.filter(Ownership='Jabil')).filter(cm__in=['JPE','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            #flex
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Arista').filter(Part_Number__in=FGN_parts.filter(Ownership='Arista')).exclude(sent_to='cm').filter(cm__in=['FGN','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Flex').filter(Part_Number__in=FGN_parts.filter(Ownership='Flex')).filter(cm__in=['FGN','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            #foxconn
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Arista').filter(Part_Number__in=HBG_parts.filter(Ownership='Arista')).exclude(sent_to='cm').filter(cm__in=['HBG','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Foxconn').filter(Part_Number__in=HBG_parts.filter(Ownership='Foxconn')).filter(cm__in=['HBG','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            #Jabil San Jose
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Arista').filter(Part_Number__in=JSJ_parts.filter(Ownership='Arista')).exclude(sent_to='cm').filter(cm__in=['JSJ','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Jabil San Jose').filter(Part_Number__in=JSJ_parts.filter(Ownership='Jabil San Jose')).filter(cm__in=['JSJ','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            #Jabil Mexico
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Arista').filter(Part_Number__in=JMX_parts.filter(Ownership='Arista')).exclude(sent_to='cm').filter(cm__in=['JMX','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),
            RFX.objects.filter(sent_quater=Current_quarter(),quarter=get_Next_quarter()[0]).filter(portfolio__Ownership='Jabil Mexico').filter(Part_Number__in=JMX_parts.filter(Ownership='Jabil Mexico')).filter(cm__in=['JMX','Global']).order_by('Part_Number').values_list('id','Part_Number','portfolio__Ownership','approval_status').distinct('Part_Number'),

        ]
    ##print(parts)
 
    return render(request, "MasterPricing/sidebar.html",{'parts':parts})
@login_required
def part_details_arista(request,id):
    '''**Removed url**'''

    return render(request,'404.html')
@login_required
def part_details_cm(request,id):
    '''
    HTML Page for MasterPricing Page for Single Part
    '''
    from MasterPricing.models import MP_download_table,Processing_list_MP
    ##Check if the parts is in Quoteing portal
    data = RFX.objects.get(id=id)
    if RFX.objects.filter(id=id).exists():
        data = RFX.objects.get(id=id)
        if Processing_list_MP.objects.filter(Part_Number=data.Part_Number).exists():
            ##If the parts are in processing queue it will send a loading page so user can wait till parts got loaded up
            return render(request, 'MasterPricing/processing.html')

        datass=RFX.objects.filter(approval_status='Approved',Quote_status='Quoted',sent_quater=Current_quarter()).filter(cm=data.cm).filter(Part_Number=data.Part_Number).filter(quarter=data.quarter,portfolio__Ownership=data.portfolio.Ownership)
        #Get only Approved data of RFQs
        if datass.exists():
            data=datass[0]

        cm=request.GET.get('cm')
        if cm == "JPE":
            bgcolor = "rgb(255, 192, 0, 0.2)"
        elif cm == "SGD": 
            bgcolor = "rgb(64, 191, 64, 0.2)"
        elif cm == "FGN":
            bgcolor = "rgb(255, 250, 69, 0.3)"
        elif cm == "HBG":
            bgcolor="rgb(200, 184, 138, 0.2)"
        elif cm == "JSJ":
            bgcolor="rgb(175,239,255, 0.2)"
        elif cm == "JMX":
            bgcolor="rgb(148,138,84,0.2)"
        else:
            bgcolor="rgb(134, 176, 73, 0.2)"

        if data.portfolio.Ownership=='Arista':
            cm=request.GET.get('cm')
            portfolio=Portfolio.objects.filter(
                Quarter=data.portfolio.Quarter,
                Number=data.portfolio.Number,
                cm=cm

            )
            ##print(portfolio)
            # mfrs = RFX.objects.filter(Part_Number=data.Part_Number).filter(quarter=data.quarter).filter(cm=data.cm)
            ##Getting the data related to the Customer PartNumber
            masterprice=RFX.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter()).filter(quarter=data.quarter).order_by('id')
            mfrs = RFX.objects.filter(approval_status='Approved',sent_quater=Current_quarter()).filter(Quote_status='Quoted').filter(cm__in=['Global',cm]).filter(Part_Number=data.Part_Number).filter(quarter__in=get_Next_quarter(q=1,this_quarter=True),portfolio__Ownership=data.portfolio.Ownership,portfolio__Arista_PIC__icontains=data.portfolio.Arista_PIC).exclude(portfolio__Cust_consign='Y',sent_to="cm")
            cms = RFX.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter()).filter(quarter__in=get_Next_quarter(q=1,this_quarter=True),portfolio__Ownership__in=[data.portfolio.Ownership,'Arista'],sent_to="cm",Quote_status='Quoted')[:1]
            mp = MP_download_table.objects.filter(Part_Number=data.Part_Number,Quarter=Current_quarter(),CM_download=cm)


            if mp.exists():
                mp=mp[0]
            else:
                mp=MP_download_table.objects.none()
            if not cms.exists():
                cms = RFX.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter()).filter(quarter__in=get_Next_quarter(q=1,this_quarter=True),portfolio__Ownership__in=[data.portfolio.Ownership,'Arista'],sent_to="cm")[:1]
            ##print('cms',cms.values('Item_Price'))
            ###send the variable for Lock and unlock status
            logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
            descion=get_po_delivery_calc(data.id)
            ##po delivery calculation
            try:
                if portfolio.exists() and descion:

                    ##delta based on the po or delivery
                    if descion=='PO':
                        DELTA=portfolio[0].PO_Based_Total_OH_sum_OPO-(portfolio[0].CQ_ARIS_FQ_sum_1_SANM_Demand+portfolio[0].CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
                    else:
                        DELTA=portfolio[0].Delivery_Based_Total_OH_sum_OPO_this_quarter-(portfolio[0].CQ_ARIS_FQ_sum_1_SANM_Demand+portfolio[0].CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
                else:
                    DELTA=None
            except:
                DELTA=None
            ##print('portfolio:',portfolio)
            ##print('DELTA:',DELTA)
            return render(request, 'MasterPricing/partdetails.html',context={'data':data,'masterprice':masterprice,'mfrs':mfrs,'cms':cms,'logic_BP':logic_BP,'portfolio':portfolio,'cm':cm,'DELTA':DELTA,'PO_DEL_decision':descion,'mp':mp,'bgcolor':bgcolor})

        else:
            ###ownership if cm
            cm=request.GET.get('cm')
            ##getting the cm site
            portfolio=Portfolio.objects.filter(
                Quarter=data.portfolio.Quarter,
                Number=data.portfolio.Number,
                cm=cm
            )

            ##print(portfolio)
            # mfrs = RFX.objects.filter(Part_Number=data.Part_Number).filter(quarter=data.quarter).filter(cm=data.cm)
            masterprice=RFX.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter()).filter(quarter=data.quarter).order_by('id')
            mfrs = RFX.objects.filter(approval_status='Approved',Quote_status='Quoted',sent_quater=Current_quarter()).filter(Part_Number=data.Part_Number).filter(quarter=data.quarter,portfolio__Ownership=data.portfolio.Ownership,portfolio__Arista_PIC__icontains=data.portfolio.Arista_PIC).exclude(portfolio__Cust_consign='Y',sent_to="cm")
            cms = RFX.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter()).filter(quarter=get_Next_quarter()[0],portfolio__Ownership__in=[data.portfolio.Ownership,'Arista'],sent_to="cm",Quote_status='Quoted')[:1]
            mp = MP_download_table.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter(), quarter=get_Next_quarter()[0],CM_download=cm)
            ##print(mp)
            if mp.exists():
                mp=mp[0]
            else:
                mp=MP_download_table.objects.none()
            if not cms.exists():
                cms = RFX.objects.filter(Part_Number=data.Part_Number,sent_quater=Current_quarter()).filter(quarter=get_Next_quarter()[0],portfolio__Ownership__in=[data.portfolio.Ownership,'Arista'],sent_to="cm")[:1]
            ##print('cms',cms.values('Item_Price'))
            logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
            descion=get_po_delivery_calc(data.id)
            try:
                if portfolio.exists() and descion:
                    if descion=='PO':
                        DELTA=portfolio[0].PO_Based_Total_OH_sum_OPO-(portfolio[0].CQ_ARIS_FQ_sum_1_SANM_Demand+portfolio[0].CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
                    else:
                        DELTA=portfolio[0].Delivery_Based_Total_OH_sum_OPO_this_quarter-(portfolio[0].CQ_ARIS_FQ_sum_1_SANM_Demand+portfolio[0].CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
                else:
                    DELTA=None
            except:
                DELTA=None
            return render(request, 'MasterPricing/partdetails_CMM.html',context={'data':data,'masterprice':masterprice,'mfrs':mfrs,'cms':cms,'logic_BP':logic_BP,'portfolio':portfolio,'cm':cm,'DELTA':DELTA,'PO_DEL_decision ':descion,'mp':mp,'bgcolor':bgcolor})

    else:
        return render(request,'404.html')

def refresh_quote_from_rfx(request,id):
    '''Not in use'''
    if Portfolio.objects.filter(id=id).exists():
        data = Portfolio.objects.get(id=id)
        mfrs = MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm)
        nextqtr=get_Next_quarter()
        for mfr in mfrs:
            if RFX.objects.filter(quarter=nextqtr[0]).filter(Part_Number=mfr.arista_partno).filter(Mfr_Part_Number=mfr.mpn_q1).filter(Mfr_Name=mfr.mfr_name_q1).filter(sent_to=mfr.sent_to).exists():
                rfx = RFX.objects.filter(quarter=nextqtr[0]).filter(Part_Number=mfr.arista_partno).filter(Mfr_Part_Number=mfr.mpn_q1).filter(Mfr_Name=mfr.mfr_name_q1).filter(sent_to=mfr.sent_to)[:1].get()
                if rfx.split_type == "Manual":
                    split=rfx.manual_split
                else:
                    split=rfx.suggested_split
            else:
                rfx = RFX.objects.none()

            masterpricing = MPTemplate.objects.get(id=mfr.id)

            masterpricing.current_updated_std_cost = rfx.std_cost if rfx else None
            masterpricing.ncnr_q1 = rfx.NCNR if rfx else None
            masterpricing.coo_q1 = rfx.COO if rfx else None
            masterpricing.inco_terms_q1 = rfx.Inco_Term if rfx else None
            masterpricing.soft_hard_tool_q1 = rfx.soft_hard_tool if rfx else None
            masterpricing.mpn_level_po_delivery_q1 = rfx.PO_Delivery if rfx else None
            masterpricing.split_q1 = split if rfx else None
            masterpricing.arista_pic_comments_for_quote_q1 = rfx.Arista_pic_comment if rfx else None
            masterpricing.supplier_comments_for_quote_q1 = rfx.CM_comments_on_Justifing_price if rfx else None
            masterpricing.cm_aditional_notes_q1 = rfx.CM_Notes_on_Supplier if rfx else None
            masterpricing.approval_status_PIC = rfx.approval_status_PIC if rfx else None
            masterpricing.approval_status_Manager = rfx.approval_status_Manager if rfx else None
            masterpricing.approval_status_Director = rfx.approval_status_Director if rfx else None
            masterpricing.sup_disti_name_from_cm_q1 = rfx.Supplier_Distributor_name_from_cm if rfx else None
            masterpricing.freight_cost_q1 = rfx.Freight_cost if rfx else None
            masterpricing.quoted_by_arista = rfx.Quoted_by if rfx else None
            masterpricing.sent_to = rfx.sent_to if rfx else None
            masterpricing.List = rfx.List if rfx else None
            masterpricing.tarrif = rfx.tarrif if rfx else None
            masterpricing.save()
        try:
            masterprice=MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(cm_partno=data.cm_Part_Number).filter(quarter=data.Quarter).exclude(current_updated_std_cost=None)[:1].get()
        except:
            masterprice=MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(cm_partno=data.cm_Part_Number).filter(quarter=data.Quarter)[:1].get()
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        mfrs = MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).filter(sent_to__in=["supplier","distributor"])
        cms = MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).filter(sent_to="cm")

        return render(request, 'MasterPricing/partdetails.html',context={'data':data,'masterprice':masterprice,'mfrs':mfrs,'cms':cms})
    else:
        return render(request,'404.html')

def update_price_decision(request):
    '''
    Price decision:
    Keep Flat or Updated decision
    '''
    #print(request.POST)
    Part_Number=request.POST.get('Part_Number')
    while Processing_list_MP.objects.filter(Part_Number=Part_Number).exists():
        #print('wating for processing...')
        sleep(1)
    quarter=request.POST.get('quarter')
    cm=request.POST.get('cm')
    q=RFX.objects.filter(Part_Number=Part_Number,quarter=quarter,cm=cm)
    mp=MP_download_table.objects.filter(Part_Number=Part_Number,Quarter=Current_quarter(),CM_download=cm)

    previous=RFX.objects.filter(Part_Number=Part_Number,quarter=Current_quarter(),cm=[cm,'Global'])

    mp_instance=mp.first()
    try:
        change_flag=True if (mp_instance and mp_instance.current_qtr_decision) != request.POST.get('current_qtr_decision') else False
    except:
        change_flag=True
        LOGGER.error("LOG_MESSAGE", exc_info=1)


    #print(mp_instance.std_cost,'mp_instance.std_cost')
    if request.POST.get('current_qtr_decision') == "Keep Flat" and (mp_instance and mp_instance.std_cost) :

        if not float(mp_instance.current_final_std_cost) :
            return JsonResponse({'message':f'Please check if there is Previous cost is there for this part, current Previous cost :{mp_instance.current_final_std_cost}','status':400})
            
        if has_permission(request.user,'PIC'):
            try:
                po_dec="N/A" if float(request.POST.get('q+1_std_cost')) == float(request.POST.get('q_std_cost')) else float(request.POST.get('q+1_std_cost')) 
            except:
                po_dec=None
            mp.update(
                    current_qtr_decision=request.POST.get('current_qtr_decision'),
                    standard_price_q1=request.POST.get('q_std_cost'),
                    new_po_price=po_dec,
            )
            mp.update(
                arista_pic_approve_reject=request.POST.get('arista_pic_approve_reject'),
                arista_pic_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.email}'''
            )
            if change_flag:
                mp.update(
                    approve_reject_std_price=None,
                )
        elif has_permission(request.user,'Contract Manufacturer'):

            try:
                po_dec="N/A" if float(request.POST.get('q+1_std_cost')) == float(request.POST.get('q_std_cost')) else float(request.POST.get('q+1_std_cost')) 
            except:
                po_dec=None
            pic_price=mp_instance.Item_Price or mp_instance.Item_Price
            try:
                pic_price=float(pic_price)
            except:
                pic_price=None
            if request.POST.get('go_with_pic_price')=='Yes':
                if pic_price:
                    po_dec=pic_price
                    trigger_part(Part_Number)
                else:
                    return JsonResponse({'message':"Sorry. There is no price from PIC. Please use CM Price.",'status':400})
            else:
                trigger_part(Part_Number)
            mp.update(
                    current_qtr_decision=request.POST.get('current_qtr_decision'),
                    standard_price_q1=request.POST.get('q_std_cost'),
                    new_po_price=po_dec,
                    go_with_pic_price=request.POST.get('go_with_pic_price','no'),
            )

            mp.update(
                cm_approve_reject=request.POST.get('cm_approve_reject'),

                cm_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.last_name},{request.user.first_name}'''
            )
            if change_flag:
                #print('change_flag',change_flag)
                mp.update(
                    approve_reject_std_price=None,
                )
        mp_instance=mp.first()

        try:save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.current_qtr_decision, mp_instance.CM_download)
        except:pass
    elif request.POST.get('current_qtr_decision') == "Updated Price" and (mp_instance and mp_instance.std_cost):
        
        if has_permission(request.user,'PIC'):
            mp.update(
                    current_qtr_decision=request.POST.get('current_qtr_decision'),
                    standard_price_q1=mp_instance.std_cost,
                    new_po_price=None
            )
            mp.update(
                arista_pic_approve_reject=request.POST.get('arista_pic_approve_reject'),
                arista_pic_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.email}'''
            )
            if has_permission(request.user,'PIC'):
                mp.update(
                    arista_pic_approve_reject=request.POST.get('arista_pic_approve_reject'),
                    arista_pic_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.email}'''
                )
            if change_flag:
                mp.update(
                    approve_reject_std_price=None,
                )
        elif has_permission(request.user,'Contract Manufacturer'):
            
            standard_price_q1=request.POST.get('q+1_std_cost')

            pic_price=None or mp_instance.Item_Price
            try:
                pic_price=float(pic_price)
            except:
                pic_price=None
            if request.POST.get('go_with_pic_price')=='Yes':
                if pic_price:
                    #print(pic_price)
                    standard_price_q1=pic_price
                    trigger_part(Part_Number)

                else:
                    return JsonResponse({'message':"Sorry PIC have no price for this Part please use CM's cost",'status':400})
            else:
                trigger_part(Part_Number)
            #print(request.POST.get('q+1_std_cost'),standard_price_q1,request.POST.get('go_with_pic_price'))
            mp.update(
            current_qtr_decision=request.POST.get('current_qtr_decision'),
            standard_price_q1=standard_price_q1,
            go_with_pic_price=request.POST.get('go_with_pic_price','no'),
            new_po_price=None,
            )

            mp.update(
                cm_approve_reject=request.POST.get('cm_approve_reject'),

                cm_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.last_name},{request.user.first_name}'''
            )
            if change_flag:
                mp.update(
                    approve_reject_std_price=None,
                    
                )
        mp_instance=mp.first()
        try:save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.current_qtr_decision, mp_instance.CM_download)
        except:pass

    else:
        return JsonResponse({'message':'Please update the quote in quoting portal page','status':400})

    return JsonResponse({'message':'Successfully updated','status':200})



def price_approval(request):
    Part_Number=request.POST.get('Part_Number')
    quarter=request.POST.get('quarter')
    cm=request.POST.get('cm')
    # q=RFX.objects.filter(Part_Number=Part_Number,quarter=quarter,cm=cm)
    q=MP_download_table.objects.filter(Part_Number=Part_Number,Quarter=Current_quarter(),CM_download=cm)
    mp_instance = q.first()
    if request.POST.get('approve_reject_std_price') in ['Approved','Rejected']:

        if has_permission(request.user,'Contract Manufacturer')  :
            if request.POST.get('approve_reject_std_price')=='Approved' or (request.POST.get('approve_reject_std_price')=='Rejected' and request.POST.get('cm_approve_reject') and request.POST.get('cm_approve_reject').strip() ):
                #print(request.POST.get('approve_reject_std_price'))
                q.update(
                    approve_reject_std_price=request.POST.get('approve_reject_std_price'),
                    cm_approve_reject=request.POST.get('cm_approve_reject'),
                )
            else:
                return JsonResponse({'message':'Not Updated, Comment is mandatory while rejecting','status':406})
        if (has_permission(request.user,'Manager') or has_permission(request.user,'PIC'))  :
            if request.POST.get('approve_reject_std_price')=='Approved' or (request.POST.get('approve_reject_std_price')=='Rejected' and request.POST.get('arista_pic_approve_reject') and request.POST.get('arista_pic_approve_reject').strip() ):
                q.update(
                    approve_reject_std_price=request.POST.get('approve_reject_std_price'),
                    arista_pic_approve_reject=request.POST.get('arista_pic_approve_reject'),
                )
            else:
                return JsonResponse({'message':'Not Updated, Comment is mandatory while rejecting','status':406})
        mp_instance = q.first()
        save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter,request.POST.get('approve_reject_std_price'), mp_instance.CM_download)
        return JsonResponse({'message':'Successfully updated desision','status':200})
    else:
        return JsonResponse({'message':'failed to updated','status':406})

def apply_filter_masterpricing(request):
    currentqtr=Current_quarter()
    #print(request.POST.getlist('keepflat_updated'))
    #print(request.POST.getlist('po_or_delivery'))
    partslist=MPTemplate.objects.filter(quarter=currentqtr).filter(po_delivery__in=request.POST.getlist('po_or_delivery')).values('id','arista_partno','controlby').distinct('arista_partno')
    return render(request, "MasterPricing/filtersidebar.html",context={'partslist':partslist})


def upload(request):
    if request.method == 'POST' and request.FILES['attachment']:
        attachment = request.FILES['attachment']
        fs = FileSystemStorage()
        name= attachment.name
        filename = fs.save('QuarterHistory/'+name,attachment)
    return render(request, 'MasterPricing/index.html')
@login_required
def download_excel(request,file_name=''):
    file = request.POST.get('quarter_file')
    #print(file)
    fs = FileSystemStorage()
    if fs.exists('QuarterHistory/'+file):
        fh = fs.open('QuarterHistory/'+file)
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'inline; filename=' + file

    return response

columns_MP={
        "CM Part Number":"portfolio__cm_Part_Number",
        "Arista Part Number":"Part_Number",
        "Arista Consigned (Y/N)":"portfolio__Cust_consign",
        "Arista Part PO/ Delivery":"po_delivery",
        "CM PO/ Delivery Remarks":"CM_PO_Delivery_Remarks",#No need update
        "CM Quantity Buffer OH":"cm_Quantity_Buffer_On_Hand",
        "CM Quantity OH":"cm_Quantity_On_Hand_CS_Inv",
        "CM Open PO due Current Qtr":"Open_PO_due_in_this_quarter",
        "CM Open PO due Q+1":"Open_PO_due_in_next_quarter",
        "CM Total OH + OPO (Current Qtr) ":"Delivery_Based_Total_OH_sum_OPO_this_quarter",
        "CM Total OH + OPO(Q & Q+1)":"PO_Based_Total_OH_sum_OPO",
        "CM Current Quarter Demand ":"CQ_ARIS_FQ_sum_1_SANM_Demand",
        "CM Q+1 Demand":"CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
        "CM Q+2 Demand":"CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
        "CM Q+3 Demand":"CQ_sum_3_ARIS_FQ_SANM_Demand",
        "Delta = OH & Open PO - Demand (Current Qtr + Q+1)":"Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
        "Demand Coverage":"Demand_Coverage",
        "Current Qtr Final Std Cost":"current_final_std_cost",
        "Current Qtr":"sent_quater",
        "Final Std Cost Q+1":"standard_price_q1",
        "Q+1 Qtr":"quarter",
        "Delta = Final Std Cost Q+1 - Current Std Cost":"delta_std_previous_std",
        "% Increase or Decrease":"delta_std_previous_std%",
        "Blended Current Qtr AVG. PO Receipt Price":"portfolio__Blended_AVG_PO_Receipt_Price",
        "New PO Price":"new_po_price",
        "Approve/Reject Q+1 Std Cost":"approve_reject_std_price",#No need update
        "CM Q+1 decision comments":"cm_approve_reject",#No need update
        "Arista PIC Q+1 decision comments":"arista_pic_approve_reject",#No need update
        "BP team Approve/Reject Comments for Q+1":"BP_team_Approve_Reject_Comments",#No need update
        "Q+1 Decision (Flat/Updated Std Cost)":"current_qtr_decision",#No need update
        "Q+1 Final Std Cost PIC/Date/Timestamp":"arista_pic_updated_data_name",
        "Prior Qtr Delta = OH & Open PO - Demand (Current Qtr + Q+1)":"portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista_previous",
        "Current Qtr Updated Arista Std Cost":"standard_price_q1_previous",
        "Current Qtr Decision (Flat/Updated Std Cost)":"current_qtr_decision_previous",
        "Arista PIC Current Qtr decision comments":"arista_pic_approve_reject_previous",
        "CM Current Qtr decision comments":"cm_approve_reject_previous",
        "BP team Approve/Reject Comments for Current Qtr":"BP_team_Approve_Reject_Comments_previous",
        "CM Additional Notes on Supplier / distributor details. Current Qtr":"CM_Additional_Notes_on_Supplier_distributor_previous",#No need update
        "std price Q+1 ":"std_cost",
        "Arista Manufacturer Name Q+1":"Mfr_Name",
        "Arista Supplier / Distributor NameQ+1":"sent_to",
        "Item Description":"portfolio__Item_Desc",
        "Arista Supplier Quoted Price Q+1":"Item_Price",
        "Arista Qual Status Q+1":"portfolio__Qualification_Status",
        "Arista MPN PO/Delivery Q+1":"PO_Delivery",
        "Arista MOQ Q+1":"MOQ",
        "Arista MFG Lead Time Q+1":"Lead_Time",
        "Arista MPN Q+1":"portfolio__Mfr_Part_Number",
        "NCNR Q+1":"NCNR",
        "Arista COO Q+1":"COO",
        "Arista Inco Terms Q+1":"Inco_Term",
        "Arista Freight Cost Q+1":"Freight_cost",
        "Arista Supplier Comments Q+1":"Comments",
        "Arista Soft / Hard / Hybrid Tool Q+1":"soft_hard_tool",
        "Arista Revision Q+1":"portfolio__Rev",
        "Arista Lifecycle phase Q+1":"portfolio__Lifecycle_Phase",
        "Arista Business Split % Q+1":"split",
        "Part Ownership":"portfolio__Ownership",
        "Arista PIC":"portfolio__Arista_PIC",
        "Arista PIC Comments Q+1 to Suppliers":"Arista_pic_comment",
        "Arista PIC Comments Q+1 to CM":"Arista_PIC_Comments_to_CM",
        "Arista BP Comments Q+1":"Arista_BP_Comments",
        "Supplier/Distributor/Arista Uploaded Response Date/Timestamp":"Quoted_by",
        "CM Cost Q+1 Decision PIC/Date/Timestamp":"cm_updated_data_name",#No need update
        "CM Price Q+1 ":"CM_price",
        "CM Manufacturer Q+1 ":"CM_Manufacturer",
        "CM Supplier / Distributor name Q+1":"CM_Supplier_Distributor_name_from_cm",
        "CM MPN PO/Delivery Q+1":"CM_po_delivery",
        "CM MPN Q+1 ":"CM_mpn",
        "CM MOQ Q+1":"CM_MOQ",
        "CM MFG Lead time Q+1":"CM_Lead_Time",
        "CM NCNR Q+1":"CM_NCNR",
        'CM Tariff':"CM_tarrif",
        'CM List':"CM_List",
        'Current Qtr Std Cost Source':"CM_qty_std_source",
        "CM Comments for quote":"CM_comments",#No need update
        "CM Additional Notes on Supplier / distributor details. Q+1":"CM_Additional_Notes_on_Supplier_distributor",#No need update
        "CM Buyer Name":"CM_buyer",
        "CM quoted date":"CM_Quoted_by",
        "CM":"CM_download",
        "PIC Approval Timestamp":"pic_approval_timestamp",
        "Accepting PIC Cost":"go_with_pic_price",
}
@login_required
def download_approval(request,cm):
    download_approval_job(request,cm)

    return JsonResponse({'message':'Once report is ready we will send you to email'})


@login_required
def MP_instance_download(request,cm,mail=None):
    PIC_MP=request.GET.get('PIC_MP')
    Download_quarter=request.GET.get('Quarter',Current_quarter())

    df2=MP_download_table.objects.filter(Quarter=Download_quarter,CM_download=cm,portfolio_cm_Part_Number__isnull=False).order_by('Part_Number')
    if PIC_MP:
        df2=df2.filter(Quarter=Download_quarter,CM_download=cm,portfolio_Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')
    df2=df2.to_dataframe()
    #print(df2.columns)
    renamed_headers={f'''{value.replace('__','_').replace('%','_per')}''':f'{key}' for key,value in columns_MP.items()}
    df2=df2.replace({np.nan: None})
    df2['modified_by'] = df2['modified_by'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).replace(tzinfo=None))
    
    try:df2['pic_approval_timestamp'] = df2['pic_approval_timestamp'].apply(lambda x: x and x.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).replace(tzinfo=None))
    except:pass
    renamed_headers['modified_by']='Updated on'
    try:df2['Updated on'] = df2['Updated on'].dt.tz_localize(None)
    except:pass
    try:df2['pic_approval_timestamp'] = df2['pic_approval_timestamp'].dt.tz_localize(None)
    except:pass
    try:df2['Quoted_by'] = df2['Quoted_by'].dt.tz_localize(None)
    except:pass
    try:df2['cm_updated_data_name'] = df2['cm_updated_data_name'].dt.tz_localize(None)
    except:pass
    try:df2['arista_pic_updated_data_name'] = df2['arista_pic_updated_data_name'].dt.tz_localize(None)
    except:pass
    df2['sent_quater']=Download_quarter
    df2['quarter']=get_Next_quarter(s=Download_quarter)[0]
    df2.loc[(df2['po_delivery']=='Quote Not Raised') & (df2['portfolio_Ownership']!='Arista'),'po_delivery' ]=None
    db_columns=[ key for key,value in renamed_headers.items()]
    excel_columns=[ value for key,value in renamed_headers.items()]

    df2=df2.replace({'': None})
    df2=df2.replace({'None': None})
    df2=df2[db_columns]
    if cm != 'SGD':
            df2["portfolio_Blended_AVG_PO_Receipt_Price"]=None
            df2["go_with_pic_price"]=None
    try:
        df2['std_cost']=df2.loc[df2['std_cost']!='Quote Not Raised']['std_cost'].astype('float64')
    except Exception as e:
        print(e)
    for k in db_columns:
        try:
            df2[k]=df2[k].astype(float)
        except Exception as e:
            #print(k,e)
            pass
    # df2['delta_std_previous_std']=df2['standard_price_q1'].astype(float)-df2['current_final_std_cost'] 
    df2['delta_std_previous_std']=df2.standard_price_q1[df2.standard_price_q1 != "Quote Not Raised"].astype(float)-df2.current_final_std_cost[df2.current_final_std_cost != "Quote Not Raised"].astype(float) 
    df2['delta_std_previous_std_per']=((df2.current_final_std_cost[df2.current_final_std_cost != "Quote Not Raised"].astype(float)-df2.standard_price_q1[df2.standard_price_q1 != "Quote Not Raised"].astype(float))/df2.current_final_std_cost[df2.current_final_std_cost != "QuoteNot Raised"].astype(float))*-1
    df2['new_po_price']=df2.apply(lambda x: float(x['new_po_price']) if is_number(x['new_po_price']) else x['new_po_price'],axis=1)
    # df2.rename(columns=renamed_headers,inplace=True)
    # return HttpResponse(len(df2.columns))
    df2.set_axis(excel_columns, axis=1,inplace=True)
    # del df2['modified_by']
    with BytesIO() as b:
        with pd.ExcelWriter(b,options={'strings_to_numbers': True}) as writer:
            df2.to_excel(writer,index=False,sheet_name='Master Price Approval',float_format="%.5f")
            workbook = writer.book
            worksheet = writer.sheets['Master Price Approval']
            currency_format = workbook.add_format({'num_format': '_($* #,##0.00000_);_($* (#,##0.00000);_($* ""-""??_);_(@_)'})
            percentage = workbook.add_format({'num_format': '0.0 %'})
            worksheet.set_column('W:W',10,percentage)
            worksheet.set_column('R:R',13,currency_format)
            worksheet.set_column('T:T',13,currency_format)
            worksheet.set_column('X:X',13,currency_format)
            worksheet.set_column('AM:AM',13,currency_format)
            worksheet.set_column('BM:BM',13,currency_format)
            worksheet.set_column('Y:Y',13,currency_format)
            worksheet.set_column('V:V',13,currency_format)
            worksheet.set_column('AF:AL', None, None, {'hidden': True})
            worksheet.write_array_formula('P1:P1', '{=SUM(N1,O1)}')


            header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#B7DEE8',
            'border': 1})
            header_format_2 = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#FCD5B4',
            'border': 1})
            editable_colour = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#dfbab8',
            'border': 1})
            ##JPE
            header_format_3 = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#FFC000',
            'border': 1})

            if cm=='SGD':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#40bf40',
                'border': 1})
            if cm=='FGN':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#fffa45',
                'border': 1})
            if cm=='HBG':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#c8b88a',
                'border': 1})
            if cm=='JSJ':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#05afef',
                'border': 1})
            if cm=='JMX':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#948a54',
                'border': 1})
            
            header_format_4 = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#B1A0C7',
            'border': 1})

            for col_num, value in enumerate(df2.columns.values):
                if  col_num==4 or col_num==60 or col_num==61  or col_num==76 or col_num==74 or col_num==77:
                # if  col_num==4 or col_num==60 or col_num==61  or col_num==76 :
                    worksheet.write(0, col_num, value, editable_colour)

                elif col_num<=24:
                    worksheet.write(0, col_num, value, header_format)
                elif 23<col_num<=29:
                    worksheet.write(0, col_num, value, editable_colour)
                elif 29<col_num<=37:
                    worksheet.write(0, col_num, value, header_format_2)
                elif 37<col_num<=59:
                    worksheet.write(0, col_num, value, header_format_3)
                elif col_num==62:
                    worksheet.write(0, col_num, value, header_format_3)
                elif 59<col_num<=61:
                    worksheet.write(0, col_num, value, header_format_2)
                elif 61<col_num<=77:
                    worksheet.write(0, col_num, value, header_format_4)
                
                else:
                    worksheet.write(0, col_num, value, header_format)

                worksheet.data_validation('Z2:Z1048576', {'validate': 'list',
                                'source': ['Approved','Rejected'],
                                })
                worksheet.data_validation('CD2:CD1048576', {'validate': 'list',
                                'source': ['Yes','No'],
                                })
                worksheet.data_validation('AD2:AD1048576', {'validate': 'list',
                                'source': ['Keep Flat','Updated Price'],
                                })
                # worksheet.data_validation('Y2:Y1048576', {'validate': 'list',
                #                 'source': ['','Blank Out'],
                #                 })

            writer.save()
            if mail:
                mime= b.getvalue()
                #print(mime)
                return mime,f'Master Pricing CM={cm} {timezone.localtime(timezone.now()).strftime("Date=%m-%d-%Y Time=%H.%M.%S")}.xlsx'
            response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
            server=request.get_host()
            server=server.replace('arista-mpat','').replace('.inesssolutions.net','')
            response['Content-Disposition'] = f'inline; filename=Master Pricing CM={cm} From={server} {timezone.localtime(timezone.now()).strftime("Date=%m-%d-%Y Time=%H.%M.%S")}.xlsx'
            #print(response['Content-Disposition'] )
            return response

@multi_threading
@error_handle
def download_approval_job(request,cm):
    try:
        #pandarallel.initialize()
        q1=RFX.objects.exclude(RFX_id__isnull=True).filter(sent_quater=Current_quarter())

        if cm=='JPE' and (request.user.is_superuser or has_permission(request.user,'Super User') or has_permission(request.user,'PIC') or has_permission(request.user,'Manager') or has_permission(request.user,'JPE Contract Manufacturer')):
            q=q1.filter(portfolio__Ownership__in=['Arista','Jabil'],cm__in=['Global','JPE'])
        elif cm=='SGD' and (request.user.is_superuser or has_permission(request.user,'Super User') or has_permission(request.user,'PIC') or has_permission(request.user,'Manager') or has_permission(request.user,'SGD Contract Manufacturer')):
            q=q1.filter(portfolio__Ownership__in=['Arista','Sanmina'],cm__in=['Global','SGD'])
        if cm=='JPE':
            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Jabil'],cm='JPE',Quarter=Current_quarter()).values('Number','cm_Part_Number', "cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"
            ).to_dataframe()
        elif cm=='SGD':
            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Sanmina'],cm='SGD',Quarter=Current_quarter()).values('Number','cm_Part_Number',"cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista").to_dataframe()
        else:
            raise Exception("Permission Denied")


        df=q.filter(quarter__in=get_Next_quarter(1,this_quarter=True)).order_by('Part_Number').values(
        "id",
        "RFX_id",
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
        "portfolio__Quarter",
        "portfolio__cm",
        "portfolio__Number",
        "portfolio__Lifecycle_Phase",
        "portfolio__commodity",
        "portfolio__Rev",
        "portfolio__Mfr_Name",
        "portfolio__Mfr_Part_Lifecycle_Phase",
        "portfolio__Mfr_Part_Number",
        "portfolio__Qualification_Status",
        "portfolio__cm_Part_Number",
        "portfolio__Arista_Part_Number",
        "portfolio__Cust_consign",
        "portfolio__Parts_controlled_by",
        "portfolio__Item_Desc",
        "portfolio__LT",
        "portfolio__MOQ",
        "portfolio__Original_PO_Delivery_sent_by_Mexico",
        "portfolio__cm_Quantity_Buffer_On_Hand",
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
        "portfolio__Team",
        "portfolio__rfq_sent_flag_supplier",
        "portfolio__rfq_sent_flag_cm",
        "portfolio__rfq_sent_flag_distributor",
        "portfolio__rfq_sent_distributor",
        "portfolio__Arista_pic_comment",
        "portfolio__offcycle",
        "portfolio__bp_comment",
        "portfolio__created_by",
        "portfolio__bp_comment",
        "portfolio__refreshed_comment",
        "created_by",
        "Quoted_by",
        "arista_pic_updated_data_name",
        "quote_is_writable",
        "quote_freeze",
        "NCNR",
        "Team",
        "PO_Delivery",
        "soft_hard_tool",
        "suggested_split",
        "manual_split",
        "split_type",
        "approval_flag",
        "approval_status_PIC",
        "approval_status_Manager",
        "approval_status_Director",
        "approval_status",
        "split_comments",
        "approval1_comments",
        "approval2_comments",
        "std_cost",
        "CM_comments_on_Justifing_price",
        "Supplier_Distributor_name_from_cm",
        "CM_Additional_Notes_on_Supplier_distributor",
        "CM_Notes_on_Supplier",
        "CM_Manufacturer",
        "CM_mpn",
        "CM_buyer",
        "CM_qty_std_source",
        "po_delivery",
        "new_po_price",
        "current_final_std_cost",
        "current_updated_std_cost",
        "current_qtr_decision",
        "approve_reject_std_price",
        "cm_approve_reject",
        "arista_pic_approve_reject",
        "BP_team_Approve_Reject_Comments",
        "standard_price_q1",
        "Arista_PIC_Comments_to_CM",
        "Arista_BP_Comments",
        "cm_updated_data_name",
        "CM_PO_Delivery_Remarks"
        ).to_dataframe()
        df=df.loc[df['quarter']==get_Next_quarter()[0]]
        df_previous=df.loc[df['quarter']==get_previous_quarter()[0]]
        df.loc[df['split_type']=='Automated','split']=df['suggested_split']
        df.loc[df['split_type']=='Manual','split']=df['manual_split']
        df2=df.drop_duplicates(subset=['Part_Number'])

        df2=pd.merge(df2,Portfolio_init,left_on='Part_Number',right_on='Number',how='left')
        del df2['portfolio__cm_Part_Number']
        df2['portfolio__cm_Part_Number']=df2['cm_Part_Number']
        del df2['cm_Part_Number']
        df2.dropna(subset=['portfolio__cm_Part_Number'],inplace=True)
        df2.drop_duplicates(subset=['Part_Number'],inplace=True)

        df2['po_delivery']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'po_delivery',cms=cm),axis=1)
        #print('0%')
        df2.loc[df2['po_delivery']=='PO' ,'portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista']=df2['PO_Based_Total_OH_sum_OPO']-(df2['CQ_ARIS_FQ_sum_1_SANM_Demand']+df2['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'])
        #print('2%')
        df2.loc[df2['po_delivery']=='Delivery' ,'portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista']=df2['Delivery_Based_Total_OH_sum_OPO_this_quarter']-(df2['CQ_ARIS_FQ_sum_1_SANM_Demand']+df2['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'])
        #print('4%')
        df2['current_final_std_cost']=df2.apply(lambda x: get_previous_std_cost(x.Part_Number,'standard_price_q1',cm),axis=1)
        #print('6%')
        df2['sent_to']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'sent_to',cms=cm),axis=1)
        df2['std_cost']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'std_cost',cms=cm),axis=1)
        #print('8%')
        df2['Mfr_Name']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Mfr_Name',cms=cm),axis=1)
        #print('10%')
        df2['split']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'split','%',cms=cm),axis=1)
        #print('12%')
        df2['MOQ']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'MOQ',cms=cm),axis=1)
        #print('14%')
        df2['Lead_Time']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Lead_Time',cms=cm),axis=1)
        #print('16%')
        df2['portfolio__Mfr_Part_Number']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'portfolio__Mfr_Part_Number',cms=cm),axis=1)
        #print('18%')
        df2['NCNR']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'NCNR',cms=cm),axis=1)
        #print('20%')
        df2['COO']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'COO',cms=cm),axis=1)
        #print('22%')
        df2['PO_Delivery']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'PO_Delivery',cms=cm),axis=1)
        #print('24%')
        df2['Inco_Term']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Inco_Term',cms=cm),axis=1)
        #print('26%')
        df2['Item_Price']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Item_Price',cms=cm),axis=1)
        df2['Quoted_by']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Quoted_by',cms=cm),axis=1)
        #print('28%')
        df2['Freight_cost']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Freight_cost',cms=cm),axis=1)
        #print('30%')
        df2['Comments']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Comments',cms=cm),axis=1)
        #print('32%')
        df2['soft_hard_tool']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'soft_hard_tool',cms=cm),axis=1)
        #print('34%')
        df2['soft_hard_tool']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'soft_hard_tool',cms=cm),axis=1)
        df2['pic_approval_timestamp']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'modified_on',cms=cm),axis=1)
        #print('36%')
        df2['portfolio__Qualification_Status']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'portfolio__Qualification_Status',cms=cm),axis=1)
        #print('38%')

        #print('40%')
        df2['CM_price']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Item_Price',df),axis=1)
        #print('42%')
        df2['CM_Manufacturer']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_Manufacturer',df),axis=1)
        #print('44%')
        df2['CM_Supplier_Distributor_name_from_cm']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Supplier_Distributor_name_from_cm',df),axis=1)
        #print('46%')
        df2['CM_po_delivery']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'PO_Delivery',df),axis=1)
        #print('48%')
        df2['CM_mpn']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_mpn',df),axis=1)
        #print('50%')
        df2['CM_MOQ']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'MOQ',df),axis=1)
        #print('52%')
        df2['CM_Lead_Time']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Lead_Time',df),axis=1)
        #print('54%')
        df2['CM_NCNR']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'NCNR',df),axis=1)
        #print('56%')

        #print('58%')
        df2['CM_buyer']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_buyer',df),axis=1)
        #print('60%')
        # df2['CM_PO_Delivery_Remarks']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_PO_Delivery_Remarks',df),axis=1)
        #print('62%')
        df2['CM_comments']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Comments',df),axis=1)
        #print('64%')
        df2['CM_tarrif']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'tarrif',df),axis=1)
        #print('66%')
        df2['CM_List']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'List',df),axis=1)
        #print('68%')
        df2['CM_Quoted_by']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Quoted_by',df),axis=1)
        df2['CM_qty_std_source']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_qty_std_source',df),axis=1)
        #print('70%')
        df2.loc[df2['sent_to']=='cm' ,'sent_to']=None
        df2['quarter']=get_Next_quarter()[0]
        df2['sent_quater']=Current_quarter()
        if cm=='JPE':
            df2['portfolio__Blended_AVG_PO_Receipt_Price']=None
            df2['portfolio__cm_Quantity_Buffer_On_Hand']=None
        try:
            df2['Demand_Coverage']=df2.apply(lambda x: Demand_Coverage(x) , axis=1)
        except:
            df2['Demand_Coverage']=''
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        df2.drop_duplicates(subset=['Part_Number'],inplace=True)
        # try:df2['modified_on']=df2['modified_on'].dt.tz_convert(None)
        # except:pass
        # #print(df2['modified_on'])
        df2=df2.merge(df_previous.filter([
            "Part_Number",
            "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "standard_price_q1",
            'split',
        ]),on='Part_Number',how='outer',suffixes=('','_previous'))

        df2=df2.merge(df_previous.filter([
        "current_qtr_decision",
        "arista_pic_approve_reject",
        "cm_approve_reject",
        "BP_team_Approve_Reject_Comments_previous",
        "CM_Additional_Notes_on_Supplier_distributor_previous",
        ]),on='Part_Number',how='outer',suffixes=('','_previous'))


        df2['delta_std_previous_std']=df2['standard_price_q1']-df2['standard_price_q1_previous']
        df2['delta_std_previous_std_per']=(df2['standard_price_q1']-df2['standard_price_q1_previous'])/df2['standard_price_q1_previous']
        db_columns=[ value for key,value in columns_MP.items()]
        excel_columns=[ key for key,value in columns_MP.items()]
        df2=df2[db_columns]
        # return HttpResponse(len(df2.columns))
        df2.set_axis(excel_columns, axis=1,inplace=True)

        name=f'''MasterPricing_{cm}_{timezone.localtime(timezone.now()).strftime("%d-%m-%Y_%H:%M:%S")}_{randomString(8)}.xlsx'''
        with pd.ExcelWriter(os.path.join(settings.BASE_DIR,f'Reports/Email_file_serve/{name}'),engine = 'xlsxwriter',) as writer:
            df2.to_excel(writer,index=False,sheet_name='Master Price Approval')
            workbook = writer.book
            worksheet = writer.sheets['Master Price Approval']
            header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#B7DEE8',
            'border': 1})
            header_format_2 = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#FCD5B4',
            'border': 1})
            editable_colour = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#dfbab8',
            'border': 1})

            ##JPE
            header_format_3 = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#FFC000',
            'border': 1})

            if cm=='SGD':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#40bf40',
                'border': 1})
            if cm=='FGN':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#fffa45',
                'border': 1})
            if cm=='HBG':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#c8b88a',
                'border': 1})
            if cm=='JSJ':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#05afef',
                'border': 1})
            if cm=='JMX':
                header_format_3 = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#948a54',
                'border': 1})

            header_format_4 = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#B1A0C7',
            'border': 1})

# Change the header colors for column E, Y to AD, BI, BJ & BU- These are editable fields
# 2)Change BH color as Green. Same as Column AM to BG- These are quote fields received by GSM and CMM Team
# 3)Change Supplier comments for Quote as CM Quote comments. Display it in excel as well
            for col_num, value in enumerate(df2.columns.values):
                #print(col_num,value)
                if  col_num==4 or col_num==60 or col_num==61  or col_num==76 :
                    worksheet.write(0, col_num, value, editable_colour)

                elif col_num<=24:
                    worksheet.write(0, col_num, value, header_format)
                elif 23<col_num<=29:
                    worksheet.write(0, col_num, value, editable_colour)
                elif 29<col_num<=37:
                    worksheet.write(0, col_num, value, header_format_2)
                elif 37<col_num<=59:
                    worksheet.write(0, col_num, value, header_format_3)
                elif 59<col_num<=61:
                    worksheet.write(0, col_num, value, header_format_2)
                elif 61<col_num<=77:
                    worksheet.write(0, col_num, value, header_format_4)
                else:
                    worksheet.write(0, col_num, value, header_format)

                worksheet.data_validation('Z2:Z1048576', {'validate': 'list',
                                'source': ['Approved','Rejected'],
                                })
                worksheet.data_validation('AD2:AD1048576', {'validate': 'list',
                                'source': ['Keep Flat','Updated Price'],
                                })
                # worksheet.data_validation('Y2:Y1048576', {'validate': 'list',
                #                 'source': ['','Blank Out'],
                #                 })

            writer.save()
            if cm=='SGD':
                send_file_via_email(request,filename=name,subject='Master Pricing Tool - Master Price Report',body='''
                Your Master pricing SGD report is ready <a href='{%filename%}'>click to download<a>
                ''')
            elif cm=='JPE':
                send_file_via_email(request,filename=name,subject='Master Pricing Tool - Master Price Report',body='''
                Your Master pricing JPE report is ready <a href='{%filename%}'>click to download<a>
                ''')

            #print('Mail sent')
    except Exception as e:
        #print(e)
        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        #print(tb_str)
        send_mail(subject='Error from CMT Tool',message=tb_str,html_message=tb_str,from_email='Arista',recipient_list=['skarthick@inesssolutions.com'])

@login_required
def update_masterpricing(request):
    from MasterPricing.models import Processing_list_MP
    from time import sleep
    while Processing_list_MP.objects.all().exists():
        ##this will make the while loop to wait till the Processing_list is empty
        #print('mp processing so waiting...')
        sleep(1)
        
    success_count=0
    logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter()) #Getting the lock and unlock status(BP team operations)
    unlock=not logic_BP.lift_logic=='enable'
    if request.method=="POST":
        q=Portfolio.objects.filter(Quarter__in=get_Next_quarter(q=1,this_quarter=True))
        if has_permission(request.user,'Director') or has_permission(request.user,'BP Manager') :
            q=q
        elif has_permission(request.user,'PIC'):
            q=q.filter(Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')
        elif has_permission(request.user,'JPE Contract Manufacturer'):
            q=q.filter(Ownership__in=['Jabil','Arista'])
        elif has_permission(request.user,'SGD Contract Manufacturer'):
            q=q.filter(Ownership__in=['Sanmina','Arista'])
        elif has_permission(request.user,'FGN Contract Manufacturer'):
            q=q.filter(Ownership__in=['Flex','Arista'])
        elif has_permission(request.user,'HBG Contract Manufacturer'):
            q=q.filter(Ownership__in=['Foxconn','Arista'])
        elif has_permission(request.user,'JSJ Contract Manufacturer'):
            q=q.filter(Ownership__in=['Jabil San Jose','Arista'])
        elif has_permission(request.user,'JMX Contract Manufacturer'):
            q=q.filter(Ownership__in=['Jabil Mexico','Arista'])
        else:
            q=Portfolio.objects.none()
        file=request.FILES['Upload_Excel']
        df=pd.read_excel(file)
        df=df.replace({np.nan: None})
        db_columns=[value for key,value in columns_MP.items()]
        try:
            db_columns.append('Updated_on')
        except:
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        #print(len(db_columns))
        df.set_axis(db_columns, axis=1,inplace=True)
        error_index=[]

        to_email_list = []
        sgd_cm_email = []
        jpe_cm_email = []
        fgn_cm_email = []
        hbg_cm_email = []
        jsj_cm_email = []
        jmx_cm_email = []
        bp_email_list = []
        cm_set_list = []
        ahead_quarter = get_ahead_quarter()
        current_quarter = get_current_quarter()
        bp_team_count=0
        part_not_in_portfolio=0
        error_rows = []
        overall_counter=0
        for index, row in df.iterrows():

            overall_counter+=1
            if row['CM_download']=='SGD':
                p=q.filter(Number=str(row['Part_Number'])).filter(Ownership__in=['Sanmina','Arista'])
            elif row['CM_download']=='JPE':
                p=q.filter(Number=str(row['Part_Number'])).filter(Ownership__in=['Jabil','Arista'])
            elif row['CM_download']=='FGN':
                p=q.filter(Number=str(row['Part_Number'])).filter(Ownership__in=['Flex','Arista'])
            elif row['CM_download']=='HBG':
                p=q.filter(Number=str(row['Part_Number'])).filter(Ownership__in=['Foxconn','Arista'])
            elif row['CM_download']=='JSJ':
                p=q.filter(Number=str(row['Part_Number'])).filter(Ownership__in=['Jabil San Jose','Arista'])
            elif row['CM_download']=='JMX':
                p=q.filter(Number=str(row['Part_Number'])).filter(Ownership__in=['Jabil Mexico','Arista'])
            try:
                portfolio_part=p[0] if p.exists() else None
            except:
                portfolio_part=None
            p_all=MP_download_table.objects.filter(quarter__in=get_Next_quarter(q=1,this_quarter=True)).filter(CM_download=row['CM_download'],Part_Number=str(row['Part_Number']))
            
            #print(portfolio_part)
            if portfolio_part:
                ownership=portfolio_part.Ownership
                pic=portfolio_part.Arista_PIC
                p=MP_download_table.objects.filter(Quarter=Current_quarter(),portfolio_Ownership=ownership,CM_download=row['CM_download'],Part_Number=str(row['Part_Number']))

                #print(ownership,p,'*'*12)
                # return HttpResponse(df.columns)
                # standard_price_q1=MP_download_table.objects.filter(quarter=Current_quarter(),portfolio_Ownership=ownership,CM_download=row['CM_download'],sent_quater=get_previous_quarter()[0],Part_Number=row['Part_Number'])[0].standard_price_q1 if MP_download_table.objects.filter(quarter=Current_quarter(),portfolio_Ownership=ownership,CM_download=row['CM_download'],sent_quater=get_previous_quarter()[0],Part_Number=row['Part_Number']).exists() else ( Portfolio.objects.exclude(cm='Global').filter(cm=row['CM_download'],Quarter=Current_quarter(),Number=row['Part_Number'],Ownership=row['portfolio__Ownership'])[0].ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std if Portfolio.objects.exclude(cm='Global').filter(cm=row['CM_download'],Quarter=Current_quarter(),Number=row['Part_Number'],Ownership=row['portfolio__Ownership']).exists() else None)

                standard_price_q1=Portfolio.objects.exclude(cm='Global').filter(cm=row['CM_download'],Quarter=Current_quarter(),Number=row['Part_Number'],Ownership=row['portfolio__Ownership'])[0].ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std if Portfolio.objects.exclude(cm='Global').filter(cm=row['CM_download'],Quarter=Current_quarter(),Number=row['Part_Number'],Ownership=row['portfolio__Ownership']).exists() else None
                
                mp_instance=p.first()
                try:
                    change_flag=True if mp_instance.current_qtr_decision != row['current_qtr_decision'] else False
                except:
                    change_flag=True
                    LOGGER.error("LOG_MESSAGE", exc_info=1)
                if ownership=='Arista' and has_permission(request.user,'PIC'):
                    if str(row['current_qtr_decision']) == "Keep Flat"  and (mp_instance and mp_instance.std_cost) and (mp_instance and float(mp_instance.current_final_std_cost)) :
                        if (unlock or not mp_instance.standard_price_q1):
                            standard_price_q1_previous=MP_download_table.objects.filter(quarter=Current_quarter(),Part_Number=row['Part_Number'],CM_download=row['CM_download'])[0].standard_price_q1 if MP_download_table.objects.filter(quarter=Current_quarter(),Part_Number=row['Part_Number'],CM_download=row['CM_download']).exists() else None
                            

                            std_costs=RFX.objects.exclude(sent_to='cm').filter(quarter=get_Next_quarter()[0],sent_quater=Current_quarter(),Part_Number=row['Part_Number'],portfolio__Ownership=row['portfolio__Ownership'],approval_status='Approved',cm__in=[row['CM_download'],'Global'],Quote_status='Quoted')
                            if std_costs:
                                std_cost=std_costs[0].std_cost
                            else:
                                std_cost=0
                            
                            p.update(
                                    current_qtr_decision=row['current_qtr_decision'],
                                    standard_price_q1=standard_price_q1,
                                    arista_pic_approve_reject=row['arista_pic_approve_reject'],
                                    new_po_price=None if row['new_po_price']=='Blank Out' else ( "N/A" if standard_price_q1==std_cost else std_cost),
                                    arista_pic_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.email}''',
                            )
                            if change_flag:
                                p.update(
                                    approve_reject_std_price=None,
                                    # cm_approve_reject=None
                                )
                            success_count+=1
                            try:
                                mp_instance=p.first()
                                save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.current_qtr_decision, mp_instance.CM_download,threaded=False)

                            except Exception as e:
                                #print(e)
                                LOGGER.error("Unable to save %s notification details for bulk upload ", row['current_qtr_decision'])
                        else:
                            error_index.append(index)
                            error_rows.append('Part Is locked by BP Team Managers so decision cannot be changed')
                        p.update(
                                Arista_PIC_Comments_to_CM=row['Arista_PIC_Comments_to_CM'],

                        )

                    elif str(row['current_qtr_decision']) == "Updated Price" and (mp_instance and mp_instance.std_cost):

                        std_costs=MP_download_table.objects.filter(quarter=get_Next_quarter()[0],sent_quater=Current_quarter(),Part_Number=row['Part_Number'],portfolio_Ownership=row['portfolio__Ownership'],CM_download=row['CM_download'])
                        if std_costs:
                            std_cost=std_costs[0].std_cost
                        else:
                            std_cost=None
                        if (unlock or not mp_instance.standard_price_q1) :


                            p.update(
                                    current_qtr_decision=row['current_qtr_decision'],
                                    standard_price_q1=std_cost,
                                    arista_pic_approve_reject=row['arista_pic_approve_reject'],
                                    new_po_price=None,
                                    arista_pic_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.email}'''
                            )
                            if change_flag:
                                p.update(
                                    approve_reject_std_price=None,
                                    # cm_approve_reject=None
                                )
                            success_count+=1
                            try:
                                mp_instance=p.first()
                                save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.current_qtr_decision, mp_instance.CM_download,threaded=False)
                            except Exception as e:
                                LOGGER.error("Unable to save %s notification details for bulk upload ", row['current_qtr_decision'])
                        else:
                            error_index.append(index)
                            error_rows.append('Part Is locked by BP Team Managers so decision cannot be changed')
                        p.update(
                                Arista_PIC_Comments_to_CM=row['Arista_PIC_Comments_to_CM'],

                        )

                    else:
                        
                        if str(row['current_qtr_decision']) == "Updated Price":
                            error_rows.append('Please get the Quote From Supplier/Distributor')
                            error_index.append(index)
                        elif str(row['current_qtr_decision']) == "Keep Flat":
                            error_rows.append('Previous Quarter Std cost/ Current Quarter Std Cost is missing')
                            error_index.append(index)
                        else:
                            error_rows.append('Please submit your decision decision')
                            error_index.append(index)


                            

                elif ownership !='Arista' and has_permission(request.user,'Contract Manufacturer'):
                    if ownership !='Arista' and has_permission(request.user,'Contract Manufacturer'):
                        standard_price_q1=Portfolio.objects.exclude(cm='Global').filter(cm=row['CM_download'],Quarter=Current_quarter(),Number=row['Part_Number'],Ownership=row['portfolio__Ownership'])[0].ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std if Portfolio.objects.exclude(cm='Global').filter(cm=row['CM_download'],Quarter=Current_quarter(),Number=row['Part_Number'],Ownership=row['portfolio__Ownership']).exists() else None
                        mp_instance=p.first()
                        try:
                            change_flag=True if mp_instance.current_qtr_decision != row['current_qtr_decision'] else False
                        except:
                            change_flag=True
                            LOGGER.error("LOG_MESSAGE", exc_info=1)

                        
                        if str(row['current_qtr_decision']) == "Keep Flat" and (mp_instance and mp_instance.std_cost) and float(mp_instance.current_final_std_cost):
                            # if unlock and row['cm_approve_reject'] and str(row['cm_approve_reject']).strip() :
                            if (unlock or not mp_instance.standard_price_q1) :
                                # try:
                                standard_price_q1_previous=MP_download_table.objects.filter(quarter=Current_quarter(),Part_Number=row['Part_Number'],CM_download=row['CM_download'])[0].standard_price_q1 if MP_download_table.objects.filter(quarter=Current_quarter(),Part_Number=row['Part_Number'],CM_download=row['CM_download']).exists() else None
                                
                                
                                std_costs=RFX.objects.filter(sent_to='cm').filter(quarter=get_Next_quarter()[0],sent_quater=Current_quarter(),Part_Number=row['Part_Number'],portfolio__Ownership=row['portfolio__Ownership'],cm=row['CM_download'],Quote_status='Quoted')
                                if std_costs:
                                    try:
                                        std_cost=float(std_costs[0].Item_Price)
                                    except:std_cost=None
                                else:
                                    std_cost=None
                                
                                pic_price=None or mp_instance.Item_Price
                                try:
                                    pic_price=float(pic_price)
                                except:
                                    pic_price=None
                                if row['go_with_pic_price']=='Yes':
                                    if pic_price:
                                        std_cost=pic_price
                                        trigger_part(row['Part_Number'])
                                    else:
                                        error_index.append(index)
                                        error_rows.append('Please Select Yes/No under "accepting PIC price" column ')
                                        continue
                                else:
                                    trigger_part(row['Part_Number'])
                                try:standard_price_q1=float(standard_price_q1)
                                except:pass
                                p.update(
                                        current_qtr_decision=row['current_qtr_decision'],
                                        standard_price_q1=standard_price_q1,
                                        cm_approve_reject=row['cm_approve_reject'],
                                        go_with_pic_price=row['go_with_pic_price'],
                                        new_po_price=None if row['new_po_price']=='Blank Out' else ( "N/A" if standard_price_q1==std_cost else std_cost),
                                        cm_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.last_name},{request.user.first_name}''',
                                )
                                if change_flag:
                                    p.update(
                                        approve_reject_std_price=None,
                                        # arista_pic_approve_reject=None
                                    )
                                success_count+=1

                                

                                try:
                                    mp_instance=p.first()
                                    save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.current_qtr_decision, mp_instance.CM_download,threaded=False)
                                except Exception as e:
                                    #print('error',e)
                                    LOGGER.error("Unable to save %s notification details for bulk upload ", row['current_qtr_decision'])
                            else:
                                error_rows.append('Part Is locked by BP Team Managers so decision cannot be changed')
                                error_index.append(index)
                            p.update(
                                    CM_Additional_Notes_on_Supplier_distributor=row['CM_Additional_Notes_on_Supplier_distributor'],

                            )
                        elif str(row['current_qtr_decision']) == "Updated Price" and (mp_instance and mp_instance.std_cost):
                            # if unlock and row['cm_approve_reject'] and str(row['cm_approve_reject']).strip():
                            if (unlock or not mp_instance.standard_price_q1) :
                                std_costs=RFX.objects.filter(quarter=get_Next_quarter()[0],sent_quater=Current_quarter(),Part_Number=row['Part_Number'],sent_to='cm',portfolio__Ownership=row['portfolio__Ownership'],Quote_status='Quoted')
                                if std_costs:
                                    std_cost=std_costs[0].Item_Price
                                    pic_price=None or mp_instance.Item_Price
                                    try:
                                        pic_price=float(pic_price)
                                    except:
                                        pic_price=None
                                    if row['go_with_pic_price']=='Yes':
                                        if pic_price:
                                            std_cost=pic_price
                                            trigger_part(row['Part_Number'])
                                        else:
                                            error_index.append(index)
                                            error_rows.append('Please Select Yes/No under "accepting PIC price" column ')
                                            continue
                                    else:
                                        trigger_part(row['Part_Number'])
                                    
                                    p.update(
                                        current_qtr_decision=row['current_qtr_decision'],
                                        standard_price_q1=std_cost,
                                        cm_approve_reject=row['cm_approve_reject'],
                                        go_with_pic_price=row['go_with_pic_price'],
                                        new_po_price=None,
                                        cm_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.last_name},{request.user.first_name}''',
                                    )
                                    if change_flag:
                                        p.update(
                                            approve_reject_std_price=None,
                                        )
                                    success_count+=1
                            else:
                                error_rows.append('Part Is locked by BP Team Managers so decision cannot be changed')
                                error_index.append(index)

                            try:
                                mp_instance=p.first()
                                save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.current_qtr_decision, mp_instance.CM_download,threaded=False)
                            except Exception as e:
                                #print(e)
                                LOGGER.error("Unable to save %s notification details for bulk upload ", row['current_qtr_decision'])
                            
                            p.update(
                                    CM_Additional_Notes_on_Supplier_distributor=row['CM_Additional_Notes_on_Supplier_distributor'],
                            )

                        else:
                            if str(row['current_qtr_decision']) == "Updated Price":
                                error_rows.append('CM quote is not available')
                                error_index.append(index)
                            elif str(row['current_qtr_decision']) == "Keep Flat":
                                error_rows.append('Previous Quarter Std cost/ Current Quarter Std Cost is missing')
                                error_index.append(index)
                            else:
                                error_rows.append('Please submit your decision decision')
                                error_index.append(index)
                    # else:
                    #     pass
                elif ownership=='Arista' and has_permission(request.user,'Contract Manufacturer'):
                    if  p.filter(current_qtr_decision__isnull=False).count() and row['approve_reject_std_price']=='Approved' and mp_instance.current_qtr_decision and mp_instance.current_qtr_decision :

                        p.update(
                        approve_reject_std_price=row['approve_reject_std_price'],
                        cm_approve_reject=row['cm_approve_reject'],
                        cm_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.last_name},{request.user.first_name}''',
                        )
                        success_count+=1
                        mp_instance=p.first()
                        save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.approve_reject_std_price, mp_instance.CM_download,threaded=False)

                    elif (mp_instance and mp_instance.current_qtr_decision) and row['approve_reject_std_price'] == 'Rejected':
                        if row['cm_approve_reject'] and str(row['cm_approve_reject']).strip():
                            p.update(
                                    approve_reject_std_price=row['approve_reject_std_price'],
                                    cm_approve_reject=row['cm_approve_reject'],
                                    cm_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.last_name},{request.user.first_name}''',
                                    CM_Additional_Notes_on_Supplier_distributor=row['CM_Additional_Notes_on_Supplier_distributor'],
                            )
                            success_count+=1
                            mp_instance=p.first()
                            save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.approve_reject_std_price, mp_instance.CM_download,threaded=False)
                        else:
                            error_index.append(index)
                            error_rows.append('Comment is Mandatory for Rejection')

                    else:
                        error_index.append(index)
                        error_rows.append('Please select Approve/Reject or check if decision is made by PIC')
                    p.update(
                    CM_Additional_Notes_on_Supplier_distributor=row['CM_Additional_Notes_on_Supplier_distributor'],

                    )
                elif ownership !='Arista' and has_permission(request.user,'PIC'):

                    if  p.filter(current_qtr_decision__isnull=False).count() and  row['approve_reject_std_price'] == 'Approved' :
                        if mp_instance and mp_instance.current_qtr_decision:
                            p.update(
                            approve_reject_std_price=row['approve_reject_std_price'],
                            arista_pic_approve_reject=row['arista_pic_approve_reject'],
                            Arista_PIC_Comments_to_CM=row['Arista_PIC_Comments_to_CM'],

                            arista_pic_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")} {request.user.email}'''
                            )
                            success_count+=1
                        else:
                            error_index.append(index)
                            error_rows.append('Please wait till the Decision is made by the Contact Manufacturer')
                        
                    elif row['approve_reject_std_price'] == 'Rejected' :
                        if row['arista_pic_approve_reject'] and str(row['arista_pic_approve_reject']).strip():
                            if mp_instance and mp_instance.current_qtr_decision:
                                p.update(
                                    approve_reject_std_price=row['approve_reject_std_price'],
                                    arista_pic_approve_reject=row['arista_pic_approve_reject'],
                                    arista_pic_updated_data_name=f'''{timezone.localtime(timezone.now()).strftime("%m/%d/%Y, %H:%M:%S")}  {request.user.email}'''
                                    )
                                success_count+=1
                                mp_instance=p.first()
                                save_qtr_decision(request, mp_instance.Part_Number, mp_instance.quarter, mp_instance.approve_reject_std_price, mp_instance.CM_download,threaded=False)
                            else:
                                error_index.append(index)
                                error_rows.append('Please wait till the Decision is made by the Contact Manufacturer')
                        else:
                            error_index.append(index)
                            error_rows.append('Comment is Mandatory for Rejection')
                    else:
                        error_index.append(index)
                        error_rows.append('Please select Approve or Reject')

                elif  has_permission(request.user,'BP Manager'):
                        bp_team_count+=1
                        p.update(
                            BP_team_Approve_Reject_Comments=row['BP_team_Approve_Reject_Comments'],
                            Arista_BP_Comments=row['Arista_BP_Comments'],
                            CM_qty_std_source=row['CM_qty_std_source'],
                            CM_buyer=row['CM_buyer'],
                            CM_PO_Delivery_Remarks=row['CM_PO_Delivery_Remarks'],
                        )
                        
                        #print(bp_team_count,'CM_qty_std_source')
                else :
                    error_index.append(index)
                    error_rows.append('Please submit your decision decision')
                    #     error_index.append(index)
                
            else:
                error_index.append(index)
                error_rows.append('This Part is Not Valid')
                part_not_in_portfolio+=1

    error2 = pd.DataFrame(error_rows, columns = ['Error'],index=error_index)
    error_index=list(set(error_index))
    error=df[df.index.isin(error_index)].join(error2)
    #print(error)
    error=error.reset_index()
    error['index']=error['index']+1
    error=error.replace({np.nan:''})
    renamed_headers={f'''{value}''':f'{key}' for key,value in columns_MP.items()}
    temp=error.pop('Error')
    error.insert(1, 'Reason For Error', temp)
    error.rename(columns=renamed_headers,inplace=True)
    if len(error)==0:
        return JsonResponse({'status':'success','success_count':success_count, 'bp_team_count':f'{bp_team_count}/{overall_counter}'})
    else:
        table_html=error.to_html(index=False,justify='center',na_rep='', table_id='error_table',classes='table table-bordered text-nowrap table-xs font-small-4 table-responsive')
        table_html=table_html.replace('<tr style="text-align: center;">','<tr  style="text-align: center;"  class="bg-info bg-lighten-5">')
        return JsonResponse({
            'status':'error',
            'success_count':success_count,
            'bp_team_count':f'{bp_team_count}/{overall_counter}',
            'error_table':table_html
        })



def concat_row(Part_Number,sent_to,cm,PIC,df,value='Mfr_Name',append='',cms=None):
    try:
        ##print(value,cm,'++++++++++++++++++++++++++++')
        if value=='po_delivery' and cm!='Arista':
            parts=df.loc[df['Part_Number']==Part_Number].loc[df['Quote_status']=='Quoted'].loc[df['sent_to']=='cm'].loc[df['portfolio__Ownership']==cm]
            if not parts.empty:
                from MasterPricing.models import MP_download_table
                mp_parts=MP_download_table.objects.filter(Quarter=Current_quarter(),Part_Number=Part_Number,CM_download=cms)
                ##print('______=______',mp_parts,'po_delivery')
                if mp_parts:
                    mp_part=mp_parts.first()
                    ##print(mp_part.go_with_pic_price,)
                    if mp_part.go_with_pic_price=='Yes':
                        parts=df.loc[df['Part_Number']==Part_Number].loc[df['sent_quater']==Current_quarter()].loc[df['portfolio__Cust_consign']=='N'].loc[df['sent_to']!='cm'].loc[df['portfolio__Ownership'].isin([cm])].loc[df['portfolio__cm'].isin(['Global', cms])].loc[df['portfolio__Arista_PIC']==PIC].loc[df['sent_to']!='cm'].loc[df['approval_status']=='Approved'].loc[df['Quote_status']=='Quoted'].dropna(subset=['approval_status'],how='all')
                        value_need=''
                        if not parts.empty and value=='po_delivery':
                            parts['con']=parts.apply(lambda x: f'''{x['po_delivery']}''',axis=1)
                            data=parts['con'].to_list()
                            parts.dropna(subset=['PO_Delivery'],how='all',inplace=True)
                            data2=parts['PO_Delivery'].to_list()
                            data=[x for x in data if x!=None and x!='None' ]
                            data2=[x for x in data2 if x!=None and x!='None' ]
                            ##print(data,'+++++++++++++++++++')
                            if data:
                                value_need=data[0]
                            elif data2:
                                value_need=data2[0]
                            else:
                                value=''
                            return value_need
                        
                        return parts[value].to_list()[0]
                        
                return parts[value].to_list()[0]
            else:
                return ''
        elif value=='split' and cm!='Arista':
            return None
        elif value=='std_cost' and cm!='Arista':
            parts=df.loc[df['Part_Number']==Part_Number].loc[df['Quote_status']=='Quoted'].loc[df['sent_to']=='cm'].loc[df['portfolio__Ownership']==cm]
            if not parts.empty:
                return parts['Item_Price'].to_list()[0]
            else:
                return None
        parts=df.loc[df['Part_Number']==Part_Number].loc[df['portfolio__Ownership']==cm].loc[df['sent_to']!='cm']
        if parts.empty:
            if value=='modified_on':
                return None
            return "Quote Not Raised"
        # #print(df.loc[df['Part_Number']==Part_Number].loc[df['portfolio__Cust_consign']=='N'].loc[df['sent_to']!='cm'].loc[df['portfolio__Ownership'].isin([cm,'Arista'])].loc[df['portfolio__cm'].isin(['Global', cms])])
        parts=df.loc[df['Part_Number']==Part_Number].loc[df['sent_quater']==Current_quarter()].loc[df['portfolio__Cust_consign']=='N'].loc[df['sent_to']!='cm'].loc[df['portfolio__Ownership'].isin([cm,'Arista'])].loc[df['portfolio__cm'].isin(['Global', cms])].loc[df['portfolio__Arista_PIC']==PIC].loc[df['sent_to']!='cm'].loc[df['approval_status']=='Approved'].loc[df['Quote_status']=='Quoted'].dropna(subset=['approval_status'],how='all')
        value_need=''
        #print(parts)
        if not parts.empty and value=='po_delivery':
            parts['con']=parts.apply(lambda x: f'''{x['po_delivery']}''',axis=1)
            data=parts['con'].to_list()
            parts.dropna(subset=['PO_Delivery'],how='all',inplace=True)
            data2=parts['PO_Delivery'].to_list()
            data=[x for x in data if x!=None and x!='None' ]
            data2=[x for x in data2 if x!=None and x!='None' ]
            #print(data,'data')
            #print(data2,'data2')
            if data:
                value_need=data[0]
            elif data2:
                value_need=data2[0]
            else:
                value=''
            return value_need
        elif not parts.empty:
            parts['con']=parts.apply(lambda x: f'''{x[value]}''',axis=1)
            parts.dropna(subset=[value],how='all',inplace=True)
            data=parts['con'].to_list()
            for index,x in enumerate(data):
                if value=='po_delivery':
                    value_need=x
                    if value_need==None:
                        print(parts)
                    return value_need
                if value in ['Lead_Time','MOQ','split']:
                    x=int(float(x))
                if value=='std_cost':
                    value_need=x
                    return x
                if value=='modified_on':
                    value_need=x or None
                    return value_need
                    #print('modified_on',value_need)
                elif value=='sent_to':
                    # if data and all(data):
                    #     return data[0]
                    return '/'.join(data)

                elif index == len(data)-1:
                    value_need+=f'''{x}{append}'''
                else:
                    value_need+=f'''{x}{append} / '''
            #print(value,value_need,Part_Number)
        return value_need

    except Exception as e:
        LOGGER.error("LOG_MESSAGE", exc_info=1)
        return ''


def CM_details(Part_Number,cm,field,df):
    #print(Part_Number,cm,field)
    next_q=get_Next_quarter()[0]

    data=df.loc[df['Part_Number']==Part_Number].loc[df['sent_to']=='cm'].loc[df['quarter']==next_q].loc[df['cm']==cm]
    if not data.empty:
        # #print(data[field].iloc[0])
        return  data[field].iloc[0] if data[field].iloc[0]!=None and data['Quote_status'].iloc[0]!='No Bid'  else data['Quote_status'].iloc[0]
    else:
        return ''


@login_required
def extras(request):
    option=request.GET.get('option')
    if option=='lift_logic':
        if has_permission(request.user,'BP Team'):
            Team=request.GET.get('Team')
            action=request.GET.get('Action')
            notify=request.GET.get('notify')
            #print(notify)

            if action=='enable':
                data,created=master_temp.objects.get_or_create(Team=Team,quarter=Current_quarter())
                data.lift_logic='enable'
                data.user_modified=request.user
                data.save()
                try:
                    if notify:
                        send_master_lock_unlock_notification(request, subject = "Q+1 std cost is Locked", msg_line = 'BP team has Locked the Q+1 Final std cost in column T.  Arista PIC and Contract Manufacturer cannot revise any completed Keep Flat/Updated Q+1 price decisions in column T in Master Pricing page.  Only cost holes can be completed for Q+1 Final std cost in column T.  If the Q+1 Final std cost in column T is completed and the “std price Q+1” in column AM is revised by GSM (Arista Owned) or Contract Manufacturer (CM Owned), then Master Pricing page will auto push the revised Q+1 STD as New PO Price in column Y, any cost variances will need to be addressed using PPV process.')
                    else:
                        print('Notification skipped')
                except Exception as e:
                    LOGGER.info(" Unable to send mail notification for Locked parts in masterpricing")

            elif action=='disable':
                data,created=master_temp.objects.get_or_create(Team=Team,quarter=Current_quarter())
                data.lift_logic='disable'
                data.user_modified=request.user
                data.save()
                try:
                    if notify:
                        send_master_lock_unlock_notification(request, subject = "Q+1 std cost is Unlocked", msg_line = 'BP team has Unlocked the Q+1 final std cost. Arista PIC and Contract Manufacturer can make keep flat/ updated price decision in master pricing page. ')
                    else:
                        print('Notification skipped')
                except Exception as e:
                    LOGGER.info(" Unable to send mail notification for UnLocked parts in masterpricing")

            return redirect(reverse('Master_Pricing_Index'))
        else:
            return redirect(reverse('Master_Pricing_Index'))
    elif option=='blank_out':
        id=request.GET.get('part')
        cm=request.GET.get('cm')
        init=RFX.objects.get(id=id)
        # q=RFX.objects.filter(Part_Number=init.Part_Number,quarter=init.quarter,cm=init.cm)
        q=MP_download_table.objects.filter(Part_Number=init.Part_Number,Quarter=Current_quarter(),CM_download=cm)
        if init.portfolio.Ownership=='Arista' and ( has_permission(request.user,'CMM') or has_permission(request.user,'GSM') ):
            q.update(new_po_price=None)
        elif init.portfolio.Ownership!='Arista' and has_permission(request.user,'Contract Manufacturer'):
            q.update(new_po_price=None)
        else:
            return JsonResponse({'status':401,'message':'Permission denied'})
        return JsonResponse({'status':200,'message':'Done'})
    elif option=='revert_if_flat':
        id=request.GET.get('part')
        cm=request.GET.get('cm')

        decision=request.GET.get('decision')
        std_cost=request.GET.get('std_cost')
        init=RFX.objects.get(id=id)
        q=RFX.objects.filter(Part_Number=init.Part_Number,quarter=init.quarter,cm=init.cm)
        q=MP_download_table.objects.filter(Part_Number=init.Part_Number,Quarter=Current_quarter(),CM_download=cm)
        if init.portfolio.Ownership=='Arista' and ( has_permission(request.user,'CMM') or has_permission(request.user,'GSM') ):
            if decision=='Keep Flat':
                q.update(new_po_price=std_cost)
            else:
                return JsonResponse({'status':500,'message':"Decision is updated price, So can't updated the New Po"})

        elif init.portfolio.Ownership!='Arista' and has_permission(request.user,'Contract Manufacturer'):
            if decision=='Keep Flat':
                q.update(new_po_price=std_cost)
            else:
                return JsonResponse({'status':500,'message':"Decision is updated price, So can't updated the New Po"})
        else:
            return JsonResponse({'status':401,'message':'Permission denied'})
        return JsonResponse({'status':200,'message':'Done'})

def upload_po_receipt(request):
    excel=request.FILES['Upload_Excel_po_receipt']
    df=pd.read_excel(excel)
    df.drop_duplicates(subset=[df.columns[1]],inplace=True)
    df=df.filter([df.columns[1],df.columns[13]])
    # data=Portfolio.objects.filter(Quarter=Current_quarter(),cm__in=['Global','SGD'])
    updated_mp=[]
    for index,row in df.iterrows():
        try:
            #print(row[df.columns[0]])
            for x in MP_download_table.objects.filter(Quarter=Current_quarter()).filter(Part_Number__iexact=row[df.columns[0]]) :
                x.portfolio_Blended_AVG_PO_Receipt_Price=row[df.columns[1]]
                updated_mp.append(x)
            
            # data.filter(Number__icontains=row[df.columns[0]]).update(Blended_AVG_PO_Receipt_Price=row[df.columns[1]])
        except Exception as e:
            print(e)
    MP_download_table.objects.bulk_update(updated_mp,['portfolio_Blended_AVG_PO_Receipt_Price'],batch_size=1000)
    return JsonResponse({'status':'success','success_count':-1})


@login_required
def download_receipt_template(request,Team=''):

    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Sample_files/')

    if Team == 'SGD':
        file='SGD_Receipt_Template.xlsx'
        #print(file)
        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
        else:
            raise Http404

def save_qtr_decision(request, Part_Number, quarter, status, cm,threaded=True):
    if threaded:
        #print('threaded')
        t = threading.Thread(target = save_qtr_decision_fn, args=(request, Part_Number, quarter, status,cm), kwargs={})
        t.daemon = True
        t.start()
    else:
        #print('Un-threaded')
        save_qtr_decision_fn(request, Part_Number, quarter, status, cm)

def save_qtr_decision_fn(request, Part_Number, quarter, status, cm):
    try:
        mp_data = MP_download_table.objects.filter(quarter=quarter, Part_Number=Part_Number, CM_download=cm)
        #print(mp_data.values()[0]['portfolio_Ownership'])
        if mp_data.exists() is True:
            today = timezone.localtime(timezone.now())
            current_date = today.strftime("%m-%d-%Y, %H:%M:%S")
            bp_email = User.objects.filter(groups__name='Super User').values('email')
            to = User.objects.filter( first_name__icontains=mp_data.values()[0]['portfolio_Arista_PIC'].split('/')[0].split(' ')[0],last_name__icontains=mp_data.values()[0]['portfolio_Arista_PIC'].split('/')[0].split(' ')[-1]  ).values('email')

            if cm == 'JPE':
                jpe_cm_cc_email = User.objects.filter(groups__name='JPE Contract Manufacturer').values('email')
                sgd_cm_cc_email = User.objects.none()
                fgn_cm_cc_email = User.objects.none()
                hbg_cm_cc_email = User.objects.none()
                jsj_cm_cc_email = User.objects.none()
                jmx_cm_cc_email = User.objects.none()


            elif cm == 'SGD':
                sgd_cm_cc_email = User.objects.filter(groups__name='SGD Contract Manufacturer').values('email')
                jpe_cm_cc_email = User.objects.none()
                fgn_cm_cc_email = User.objects.none()
                hbg_cm_cc_email = User.objects.none()
                jsj_cm_cc_email = User.objects.none()
                jmx_cm_cc_email = User.objects.none()

            elif cm == 'FGN':
                fgn_cm_cc_email = User.objects.filter(groups__name='FGN Contract Manufacturer').values('email')
                jpe_cm_cc_email = User.objects.none()
                sgd_cm_cc_email = User.objects.none()
                hbg_cm_cc_email = User.objects.none()
                jsj_cm_cc_email = User.objects.none()
                jmx_cm_cc_email = User.objects.none()
            
            elif cm == 'HBG':
                hbg_cm_cc_email = User.objects.filter(groups__name='HBG Contract Manufacturer').values('email')
                jpe_cm_cc_email = User.objects.none()
                sgd_cm_cc_email = User.objects.none()
                fgn_cm_cc_email = User.objects.none()
                jsj_cm_cc_email = User.objects.none()
                jmx_cm_cc_email = User.objects.none()
            
            elif cm == 'JSJ':
                jsj_cm_cc_email = User.objects.filter(groups__name='JSJ Contract Manufacturer').values('email')
                jpe_cm_cc_email = User.objects.none()
                sgd_cm_cc_email = User.objects.none()
                fgn_cm_cc_email = User.objects.none()
                hbg_cm_cc_email = User.objects.none()
                jmx_cm_cc_email = User.objects.none()
            
            elif cm == 'JMX':
                jmx_cm_cc_email = User.objects.filter(groups__name='JMX Contract Manufacturer').values('email')
                jpe_cm_cc_email = User.objects.none()
                sgd_cm_cc_email = User.objects.none()
                fgn_cm_cc_email = User.objects.none()
                jsj_cm_cc_email = User.objects.none()
                hbg_cm_cc_email = User.objects.none()


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
            
            notification = EmailNotification(Arista_Part_Number=mp_data.values()[0]['Part_Number'],
                    updated_by=created_by,
                    Mfr_Part_Number='-',
                    Arista_PIC=mp_data.values()[0]['portfolio_Arista_PIC'],
                    to=to_email,
                    bp_email=cc_email,
                    team='GSM Team' if mp_data.values()[0]['portfolio_Ownership'] == 'Arista' else 'CMM Team',
                    cm=cm,
                    sent_to=mp_data.values()[0]['sent_to'],
                    created_at=current_date,
                    sgd_cm_email = sgd_email,
                    jpe_cm_email = jpe_email,
                    fgn_cm_email = fgn_email,
                    hbg_cm_email = hbg_email,
                    jsj_cm_email = jsj_email,
                    jmx_cm_email = jmx_email,
                    ownership=mp_data.values()[0]['portfolio_Ownership'],
                    current_qtr_decision=status,
                    current_url=url,
                    rfx_id='-',
                    Mfr_Name='-',
                    logged_in_user_group=request.user.groups.values('name')[0]['name'] if not request.user.is_superuser else request.user.username
            )
            notification.save()
            LOGGER.info(" %s notification details saved successfully", status)

        else:
            LOGGER.info("Unable to save %s notification details for (%s - %s - %s)", status,Part_Number,quarter,cm)

    except Exception as e:
        LOGGER.error("No data for saving %s notification details",status, exc_info=1)


def get_email_list(email_data):
    """
    This method processes email list
    """
    data_list = []
    for i in range(0,len(email_data)):
        data_list.append(email_data[i]['email'])
    email_data_set = set(data_list)
    email_list = list(email_data_set)
    return email_list


def send_email(subject, message, to, cc):
    """
    This method handles email sending operation
    """
    if settings.PRODUCTION == settings.SERVER_TYPE:
        msg = EmailMessage(subject, message, to=to, cc=list(set(cc+['sathya.narayanan@arista.com'])))
        msg.content_subtype = 'html'
        msg.send()

    elif settings.PRODUCTION != settings.SERVER_TYPE:
        msg = EmailMessage(subject, message, to=['skarthick@inesssolutions.com'], cc=['sathya.narayanan@arista.com'])
        msg.content_subtype = 'html'
        msg.send()

@multi_threading
def send_master_lock_unlock_notification(request, subject, msg_line):
    '''
    This method send Lock/Unlock Modified status to GSM/CMM team/CM and BP Team
    '''
    try:
        bp_email = User.objects.filter(groups__name="Super User").values('email')
        bp_email_data_list = get_email_list(bp_email)

        gsm_pic_email = User.objects.filter(groups__name="GSM Team").values('email')
        gsm_pic_email_data_list = get_email_list(gsm_pic_email)

        gsm_manager_email = User.objects.filter(groups__name="GSM Manager").values('email')
        gsm_manager_email_data_list = get_email_list(gsm_manager_email)

        cmm_pic_email = User.objects.filter(groups__name="CMM Team").values('email')
        cmm_pic_email_data_list = get_email_list(cmm_pic_email)

        cmm_manager_email = User.objects.filter(groups__name="CMM Manager").values('email')
        cmm_manager_email_data_list = get_email_list(cmm_manager_email)

        sgd_email = User.objects.filter(groups__name='SGD Contract Manufacturer').values('email')
        sgd_email_data_list = get_email_list(sgd_email)

        jpe_email = User.objects.filter(groups__name='JPE Contract Manufacturer').values('email')
        jpe_email_data_list = get_email_list(jpe_email)
        fgn_email = User.objects.filter(groups__name='FGN Contract Manufacturer').values('email')
        fgn_email_data_list = get_email_list(fgn_email)
        hbg_email = User.objects.filter(groups__name='HBG Contract Manufacturer').values('email')
        hbg_email_data_list = get_email_list(hbg_email)
        jsj_email = User.objects.filter(groups__name='JSJ Contract Manufacturer').values('email')
        jsj_email_data_list = get_email_list(jsj_email)
        jmx_email = User.objects.filter(groups__name='JMX Contract Manufacturer').values('email')
        jmx_email_data_list = get_email_list(jmx_email)

        sgd_bp_mail = User.objects.filter(groups__name='BP SGD Manager').values_list('email', flat=True).exclude(email='sathya.narayanan@arista.com')[0]
        jpe_bp_mail = User.objects.filter(groups__name='BP JPE Manager').values_list('email', flat=True).exclude(email='sathya.narayanan@arista.com')[0]
        fgn_bp_mail = User.objects.filter(groups__name='BP FGN Manager').values_list('email', flat=True).exclude(email='sathya.narayanan@arista.com')[0]
        hbg_bp_mail = User.objects.filter(groups__name='BP HBG Manager').values_list('email', flat=True).exclude(email='sathya.narayanan@arista.com')[0]
        jsj_bp_mail = User.objects.filter(groups__name='BP JSJ Manager').values_list('email', flat=True).exclude(email='sathya.narayanan@arista.com')[0]
        jmx_bp_mail = User.objects.filter(groups__name='BP JMX Manager').values_list('email', flat=True).exclude(email='sathya.narayanan@arista.com')[0]

        message = get_template('email/masterpricing/enable_disable_part.html').render({
                                                            'email_from':settings.EMAIL_HOST_USER,

                                                            'status': msg_line,
                                                            'production_url':settings.PRODUCTION,
                                                            'server_url': settings.SERVER_TYPE,
                                                            'cc':bp_email_data_list,
                                                            'subject':subject,
                                                            'gsm_pic_email':gsm_pic_email_data_list,
                                                            'gsm_manager_email':gsm_manager_email_data_list,
                                                            'cmm_pic_email':cmm_pic_email_data_list,
                                                            'cmm_manager_email':cmm_manager_email_data_list,
                                                            'sgd_email':sgd_email_data_list,
                                                            'jpe_email':jpe_email_data_list,
                                                            'fgn_email':fgn_email_data_list,
                                                            'hbg_email':hbg_email_data_list,
                                                            'jsj_email':jsj_email_data_list,
                                                            'jmx_email':jmx_email_data_list,
                                                            'huan':sgd_bp_mail,
                                                            'mary':jpe_bp_mail,
                                                            'hbg_bp':hbg_bp_mail,
                                                            'fgn_bp':fgn_bp_mail,
                                                            'jsj_bp':jsj_bp_mail,
                                                            'jmx_bp':jmx_bp_mail,
                                                            })
        send_email(subject, message,  to=gsm_pic_email_data_list+gsm_manager_email_data_list+cmm_pic_email_data_list+cmm_manager_email_data_list, cc=list(set(bp_email_data_list)))
        send_email(subject, message,  to=sgd_email_data_list, cc=list(set(bp_email_data_list)))
        send_email(subject, message,  to=jpe_email_data_list, cc=list(set(bp_email_data_list)))
        send_email(subject, message,  to=fgn_email_data_list, cc=list(set(bp_email_data_list)))
        send_email(subject, message,  to=hbg_email_data_list, cc=list(set(bp_email_data_list)))
        send_email(subject, message,  to=jsj_email_data_list, cc=list(set(bp_email_data_list)))
        send_email(subject, message,  to=jmx_email_data_list, cc=list(set(bp_email_data_list)))

    except Exception as e:
        LOGGER.info(" Unable to send mail notification for %s in masterpricing", subject, exc_info=1)


@login_required
def file_instruction(request,):
    if request.user.groups.filter(name__icontains='JPE Contract Manufacturer').count():
        file='JPE_Master_Pricing - Instructions.pdf'

    elif request.user.groups.filter(name__icontains='SGD Contract Manufacturer').count():
        file='SGD_Master_Pricing - Instructions.pdf'
    elif request.user.groups.filter(name__icontains='GSM').count():
        file='GSM_Team_Master_Pricing - Instructions.pdf'
    elif request.user.groups.filter(name__icontains='CMM').count():
        file='CMM_Team_Master_Pricing - Instructions.pdf'
    else:
        file='BP_Team_Master_Pricing - Instructions.pdf'

    fs = FileSystemStorage()

    files=open(os.path.join(settings.BASE_DIR,'rfx/files/'+file),'rb')
    response = HttpResponse(files, content_type="application/octet-stream")
    response['Content-Disposition'] = 'inline; filename='+file

    return response
    
# from MasterPricing import views
# from importlib import reload
# reload(views)
from MasterPricing import views
from django import db
def MP_creation(cm):
    try:
        db.connections.close_all()
        processed_list=list(Processing_list_MP.objects.filter(cm=cm).values_list('id',flat=True))
        current_Part=list(Processing_list_MP.objects.filter(cm=cm).distinct('Part_Number').values_list('Part_Number',flat=True))
        print(current_Part)
        q1=RFX.objects.exclude(RFX_id__isnull=True).filter(sent_quater=Current_quarter(),Part_Number__in=current_Part)
        if cm=='JPE' :
            q=q1.filter(portfolio__Ownership__in=['Arista','Jabil'],cm__in=['Global','JPE'])
            #print(q)

            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Jabil'],cm='JPE',Quarter=Current_quarter(),Number__in=current_Part).values('Number',"Item_Desc","Rev","Lifecycle_Phase",'cm_Part_Number', "cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "Ownership",
            "Arista_PIC",
            "Cust_consign",
            ).to_dataframe()
            print(Portfolio_init,"JPE")
        elif cm=='SGD':
            q=q1.filter(portfolio__Ownership__in=['Arista','Sanmina'],cm__in=['Global','SGD'])
            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Sanmina'],cm='SGD',Quarter=Current_quarter(),Number__in=current_Part).values('Number','Item_Desc',"Rev","Lifecycle_Phase",'cm_Part_Number',"cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "Ownership",
            "Arista_PIC",
            "Cust_consign",
            ).to_dataframe()
        elif cm=='FGN':
            q=q1.filter(portfolio__Ownership__in=['Arista','Flex'],cm__in=['Global','FGN'])
            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Flex'],cm='FGN',Quarter=Current_quarter(),Number__in=current_Part).values('Number',"Rev","Lifecycle_Phase","Item_Desc",'cm_Part_Number',"cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "Ownership",
            "Arista_PIC",
            "Cust_consign",
            ).to_dataframe()
        elif cm=='HBG':
            q=q1.filter(portfolio__Ownership__in=['Arista','Foxconn'],cm__in=['Global','HBG'])
            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Foxconn'],cm='HBG',Quarter=Current_quarter(),Number__in=current_Part).values('Number',"Rev","Lifecycle_Phase","Item_Desc",'cm_Part_Number',"cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "Ownership",
            "Arista_PIC",
            "Cust_consign",
            ).to_dataframe()
        elif cm=='JSJ':
            q=q1.filter(portfolio__Ownership__in=['Arista','Jabil San Jose'],cm__in=['Global','JSJ'])
            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Jabil San Jose'],cm='JSJ',Quarter=Current_quarter(),Number__in=current_Part).values('Number',"Rev","Lifecycle_Phase","Item_Desc",'cm_Part_Number',"cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "Ownership",
            "Arista_PIC",
            "Cust_consign",
            ).to_dataframe()
        elif cm=='JMX':
            q=q1.filter(portfolio__Ownership__in=['Arista','Jabil Mexico'],cm__in=['Global','JMX'])
            Portfolio_init=Portfolio.objects.filter(Ownership__in=['Arista','Jabil Mexico'],cm='JMX',Quarter=Current_quarter(),Number__in=current_Part).values('Number',"Rev","Lifecycle_Phase","Item_Desc",'cm_Part_Number',"cm_Quantity_Buffer_On_Hand","cm_Quantity_On_Hand_CS_Inv",
            
            "Open_PO_due_in_this_quarter",
            "Open_PO_due_in_next_quarter",
            "Delivery_Based_Total_OH_sum_OPO_this_quarter",
            "PO_Based_Total_OH_sum_OPO",
            "CQ_ARIS_FQ_sum_1_SANM_Demand",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
            "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
            "CQ_sum_3_ARIS_FQ_SANM_Demand",
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "Ownership",
            "Arista_PIC",
            "Cust_consign",
            ).to_dataframe()
        else:
            raise Exception("Permission Denied")
        print(Portfolio_init,"JPE")


        df=q.filter(quarter__in=get_Next_quarter(2,this_quarter=True)).order_by('Part_Number').values(
        "id",
        "RFX_id",
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
        "portfolio__Quarter",
        "portfolio__cm",
        "portfolio__Number",
        "portfolio__Lifecycle_Phase",
        "portfolio__commodity",
        "portfolio__Rev",
        "portfolio__Mfr_Name",
        "portfolio__Mfr_Part_Lifecycle_Phase",
        "portfolio__Mfr_Part_Number",
        "portfolio__Qualification_Status",
        "portfolio__cm_Part_Number",
        "portfolio__Arista_Part_Number",
        "portfolio__Cust_consign",
        "portfolio__Parts_controlled_by",

        "portfolio__LT",
        "portfolio__MOQ",
        "portfolio__Original_PO_Delivery_sent_by_Mexico",
        "portfolio__cm_Quantity_Buffer_On_Hand",
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
        "portfolio__Team",
        "portfolio__rfq_sent_flag_supplier",
        "portfolio__rfq_sent_flag_cm",
        "portfolio__rfq_sent_flag_distributor",
        "portfolio__rfq_sent_distributor",
        "portfolio__Arista_pic_comment",
        "portfolio__offcycle",
        "portfolio__bp_comment",
        "portfolio__created_by",
        "portfolio__bp_comment",
        "portfolio__refreshed_comment",
        "created_by",
        "Quoted_by",
        "arista_pic_updated_data_name",
        "quote_is_writable",
        "quote_freeze",
        "NCNR",
        "Team",
        "PO_Delivery",
        "soft_hard_tool",
        "suggested_split",
        "manual_split",
        "split_type",
        "approval_flag",
        "approval_status_PIC",
        "approval_status_Manager",
        "approval_status_Director",
        "approval_status",
        "split_comments",
        "approval1_comments",
        "approval2_comments",
        "std_cost",
        "CM_comments_on_Justifing_price",
        "Supplier_Distributor_name_from_cm",
        "CM_Additional_Notes_on_Supplier_distributor",
        "CM_Notes_on_Supplier",
        "CM_Manufacturer",
        "CM_mpn",
        "CM_buyer",
        "CM_qty_std_source",
        "po_delivery",
        "new_po_price",
        "current_final_std_cost",
        "current_updated_std_cost",
        "current_qtr_decision",
        "approve_reject_std_price",
        "cm_approve_reject",
        "arista_pic_approve_reject",
        "BP_team_Approve_Reject_Comments",
        "standard_price_q1",
        "Arista_PIC_Comments_to_CM",
        "Arista_BP_Comments",
        "cm_updated_data_name",
        "CM_PO_Delivery_Remarks",
        "Quoted_by",
        'modified_on',
        ).to_dataframe()
        df=df.loc[df['quarter']==get_Next_quarter()[0]]

        df_previous=df.loc[df['quarter']==get_previous_quarter()[0]]
        df.loc[df['split_type']=='Automated','split']=df['suggested_split']
        df.loc[df['split_type']=='Manual','split']=df['manual_split']
        df2=df.drop_duplicates(subset=['Part_Number'])

        df2=pd.merge(df2,Portfolio_init,left_on='Part_Number',right_on='Number',how='right')

        df2['portfolio__Item_Desc']=df2['Item_Desc']
        df2["portfolio__Rev"]=df2['Rev']
        df2["portfolio__Lifecycle_Phase"]=df2['Lifecycle_Phase']
        del df2['portfolio__cm_Part_Number']
        df2['portfolio__cm_Part_Number']=df2['cm_Part_Number']
        del df2['cm_Part_Number']
        df2.loc[df2['portfolio__Ownership'].isna(),'portfolio__Ownership']=df2['Ownership']
        df2.loc[df2['portfolio__Arista_PIC'].isna(),'portfolio__Arista_PIC']=df2['Arista_PIC']
        df2.loc[df2['portfolio__Cust_consign'].isna(),'portfolio__Cust_consign']=df2['Cust_consign']
        del  df2['Ownership']
        del  df2['Arista_PIC']
        del  df2['Cust_consign']


        df2.drop_duplicates(subset=['Number'],inplace=True)
        df2['Part_Number']=df2['Number']
        df2=df2.replace({np.nan: None})
        logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
        unlock=not logic_BP.lift_logic=='enable'

        

        try:
            if not df2.empty:
                #print('*************************')
                df2['po_delivery']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'po_delivery',cms=cm),axis=1)

                df2.loc[df2['po_delivery']=='PO' ,'Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista']=df2['PO_Based_Total_OH_sum_OPO']-(df2['CQ_ARIS_FQ_sum_1_SANM_Demand']+df2['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'])

                df2.loc[df2['po_delivery']=='Delivery' ,'Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista']=df2['Delivery_Based_Total_OH_sum_OPO_this_quarter']-(df2['CQ_ARIS_FQ_sum_1_SANM_Demand']+df2['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'])
                #print(df2['Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista'])
                df2['current_final_std_cost']=df2.apply(lambda x: get_previous_std_cost(x.Part_Number,'standard_price_q1',cm),axis=1)

                df2['sent_to']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'sent_to',cms=cm),axis=1)
                df2['std_cost']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'std_cost',cms=cm),axis=1)

                df2['Mfr_Name']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Mfr_Name',cms=cm),axis=1)

                df2['split']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'split','%',cms=cm),axis=1)

                df2['MOQ']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'MOQ',cms=cm),axis=1)

                df2['Lead_Time']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Lead_Time',cms=cm),axis=1)

                df2['portfolio__Mfr_Part_Number']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'portfolio__Mfr_Part_Number',cms=cm),axis=1)

                df2['NCNR']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'NCNR',cms=cm),axis=1)

                df2['COO']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'COO',cms=cm),axis=1)

                df2['PO_Delivery']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'PO_Delivery',cms=cm),axis=1)

                df2['Inco_Term']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Inco_Term',cms=cm),axis=1)

                df2['Item_Price']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Item_Price',cms=cm),axis=1)
                df2['Quoted_by']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Quoted_by',cms=cm),axis=1)

                df2['Freight_cost']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Freight_cost',cms=cm),axis=1)

                df2['Comments']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'Comments',cms=cm),axis=1)


                df2['soft_hard_tool']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'soft_hard_tool',cms=cm),axis=1)

                df2['portfolio__Qualification_Status']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'portfolio__Qualification_Status',cms=cm),axis=1)
                df2['pic_approval_timestamp']=df2.apply(lambda x: concat_row(x.Part_Number,x.sent_to,x.portfolio__Ownership,x.portfolio__Arista_PIC,df,'modified_on',cms=cm),axis=1)


                df2['CM_price']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Item_Price',df),axis=1)

                df2['CM_Manufacturer']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_Manufacturer',df),axis=1)

                df2['CM_Supplier_Distributor_name_from_cm']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Supplier_Distributor_name_from_cm',df),axis=1)

                df2['CM_po_delivery']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'PO_Delivery',df),axis=1)

                df2['CM_mpn']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_mpn',df),axis=1)

                df2['CM_MOQ']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'MOQ',df),axis=1)

                df2['CM_Lead_Time']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Lead_Time',df),axis=1)

                df2['CM_NCNR']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'NCNR',df),axis=1)

                df2['CM_buyer']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_buyer',df),axis=1)

                # df2['CM_PO_Delivery_Remarks']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_PO_Delivery_Remarks',df),axis=1)

                df2['CM_comments']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Comments',df),axis=1)

                df2['CM_tarrif']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'tarrif',df),axis=1)

                df2['CM_List']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'List',df),axis=1)

                df2['CM_qty_std_source']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'CM_qty_std_source',df),axis=1)
                df2['CM_Quoted_by']=df2.apply(lambda x:CM_details(x.Part_Number,cm,'Quoted_by',df),axis=1)
                
                df2.loc[df2['pic_approval_timestamp']=='','pic_approval_timestamp']=None
                #print('****************************')
                df2.loc[df2['sent_to']=='cm' ,'sent_to']=None
                if cm=='JPE':
                    df2['portfolio__Blended_AVG_PO_Receipt_Price']=None
                    df2['portfolio__cm_Quantity_Buffer_On_Hand']=None
                try:

                    df2['Demand_Coverage']=df2.apply(lambda x: Demand_Coverage(x) , axis=1)
                except:
                    df2['Demand_Coverage']=''
                    LOGGER.error("LOG_MESSAGE", exc_info=1)

                df2.dropna(subset=['portfolio__cm_Part_Number'],inplace=True)
                df2.drop_duplicates(subset=['Part_Number'],inplace=True)
                # try:df2['modified_on']=df2['modified_on'].dt.tz_convert(None)
                # except:pass
                # print(df2['modified_on'])
                df2=df2.merge(df_previous.filter([
                    "Part_Number",
                    "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
                    "standard_price_q1",
                    'split',
                    ]),on='Part_Number',how='outer',suffixes=('','_previous'))
                df_previous_mp=MP_download_table.objects.filter(Part_Number__in=current_Part,quarter=get_Next_quarter()[0],CM_download=cm).values(
                    "Part_Number",
                    "current_qtr_decision",
                    "arista_pic_approve_reject",
                    "cm_approve_reject",
                    "BP_team_Approve_Reject_Comments_previous",
                    "CM_Additional_Notes_on_Supplier_distributor_previous",
                ).to_dataframe()

                df2=df2.merge(df_previous_mp.filter([
                    "Part_Number",
                    "current_qtr_decision",
                    "arista_pic_approve_reject",
                    "cm_approve_reject",
                    "BP_team_Approve_Reject_Comments_previous",
                    "CM_Additional_Notes_on_Supplier_distributor_previous",
                    ]),on='Part_Number',how='outer',suffixes=('','_previous'))

                df2['delta_std_previous_std']=df2['standard_price_q1']-df2['standard_price_q1_previous']
                df2['delta_std_previous_std%']=(df2['standard_price_q1']-df2['standard_price_q1_previous'])/df2['standard_price_q1_previous']
                columns_MP_inverted={v:k for k,v in columns_MP.items()}
                excluded=[
                "approve_reject_std_price",
                "standard_price_q1",
                "new_po_price",
                "current_qtr_decision",
                "cm_approve_reject",
                "arista_pic_approve_reject",
                "BP_team_Approve_Reject_Comments",
                "Arista_BP_Comments",
                "Arista_PIC_Comments_to_CM",
                "CM_PO_Delivery_Remarks",
                "arista_pic_updated_data_name",
                "cm_updated_data_name",
                "CM_Additional_Notes_on_Supplier_distributor",
                "portfolio__Blended_AVG_PO_Receipt_Price",
                "CM_qty_std_source",
                "CM_buyer",
                "go_with_pic_price",
                ]
                
                for col in excluded:
                    del columns_MP_inverted[col]
                columns_MP_strip={v:k for k,v in columns_MP_inverted.items()}
                
                db_columns=[ value for key,value in columns_MP_strip.items()]
                excel_columns=[ key for key,value in columns_MP_strip.items()]
                df2['CM_download']=cm
                # df2['sent_quater']=Current_quarter()
                # print(df2)
                df2=df2[db_columns]
                # print(df2.columns )
                db_columns=[x.replace('__','_') for x in db_columns]
                db_columns=[x.replace('%','_per') for x in db_columns]
                # return HttpResponse(len(df2.columns))

                df2.set_axis(db_columns, axis=1,inplace=True)
                df2=df2.replace({np.nan: None})
            #print(df2.to_csv('mppp.csv'),'df3333')
        except Exception as e:
            LOGGER.error("LOG_MESSAGE", exc_info=1)

            tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            #print(tb_str)
            df2['CM_download']=cm
        finally:
            pass
        # MP_download_table.objects.filter(Part_Number__in=current_Part,CM_download=cm,Quarter=MP_quarter).delete()
        # MP_download_table.objects.filter(Part_Number__in=current_Part,CM_download=cm,Quarter=Current_quarter()).delete()
        
        
        for index, row in df2.iterrows():
            datas=MP_download_table.objects.filter(Part_Number=row['Part_Number'],CM_download=row['CM_download'],Quarter=Current_quarter())

            if datas.exists():
                #print(datas.first().standard_price_q1)
                if unlock or not datas.first().standard_price_q1:
                    updated_value=row.to_dict()
                    
                    
                    datas.update(**updated_value)
                    
                    print(datas.first().Part_Number)
                    print('updated..')
                    print("Unlocked")
                else:
                    print("Locked")
                    MP_instance=datas.first()
                    updated_value=row.to_dict()
                    if updated_value['std_cost']:
                        if MP_instance.portfolio_Ownership=='Arista':

                            if not (MP_instance and MP_instance.std_cost)==updated_value['std_cost']:
                                if MP_instance.portfolio_Ownership=='Arista':
                                    if MP_instance.current_qtr_decision=='Keep Flat' and MP_instance.standard_price_q1==updated_value['std_cost']:
                                        #print('Keep Flat')
                                        MP_instance.new_po_price='N/A'
                                        MP_instance.save()
                                    elif MP_instance.current_qtr_decision=='Updated Price' and MP_instance.standard_price_q1==updated_value['std_cost']:
                                        #print('Updated Price')
                                        MP_instance.new_po_price=None
                                        MP_instance.save()
                                    else:
                                        #print('elsee')
                                        MP_instance.new_po_price=updated_value['std_cost']
                                        MP_instance.save()
                                    try:
                                        if not MP_instance.new_po_price in ['N/A',None,MP_instance.standard_price_q1]:
                                            save_new_po_price_change_notified_data(MP_instance.Part_Number, MP_instance.portfolio_Ownership, MP_instance.CM_download, MP_instance.portfolio_Arista_PIC, MP_instance.sent_to,status="New PO Price Change")
                                    except Exception as e:
                                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                        else:
                            if MP_instance.go_with_pic_price=='Yes':
                                if True:
                                    pic_price=None or MP_instance.Item_Price
                                    try:
                                        pic_price=float(pic_price)
                                    except:
                                        pic_price=None

                                    if MP_instance.current_qtr_decision=='Keep Flat' and MP_instance.standard_price_q1==updated_value['Item_Price']:
                                        #print('Keep Flat')
                                        MP_instance.new_po_price='N/A'
                                        MP_instance.save()
                                    elif MP_instance.current_qtr_decision=='Updated Price' and MP_instance.standard_price_q1==updated_value['Item_Price']:
                                        #print('Updated Price')
                                        MP_instance.new_po_price=None
                                        MP_instance.save()
                                    else:
                                        #print('elsee')
                                        MP_instance.new_po_price=float(updated_value['Item_Price'])
                                        MP_instance.save()


                                    if pic_price:
                                        # MP_instance.new_po_price=pic_price
                                        try:
                                            save_new_po_price_change_notified_data(MP_instance.Part_Number, MP_instance.portfolio_Ownership, MP_instance.CM_download, MP_instance.portfolio_Arista_PIC, MP_instance.sent_to,status="New PO Price Change")
                                        except Exception as e:
                                            LOGGER.error("LOG_MESSAGE", exc_info=1)
                                    
                                        #MP_instance.save()
                            else:
                                if True:
                                    if MP_instance.current_qtr_decision=='Keep Flat' and MP_instance.standard_price_q1 == updated_value['std_cost']:
                                        #print('Keep Flat')
                                        MP_instance.new_po_price='N/A'
                                        MP_instance.save()
                                    elif MP_instance.current_qtr_decision=='Updated Price' and MP_instance.standard_price_q1==updated_value['std_cost']:
                                        #print('Updated Price')
                                        MP_instance.new_po_price=None
                                        MP_instance.save()
                                    else:
                                        #print('elsee')
                                        MP_instance.new_po_price=updated_value['std_cost']
                                        MP_instance.save()
                                    #try:
                                    #    if not MP_instance.new_po_price in ['N/A',None,MP_instance.standard_price_q1]:
                                    #        save_new_po_price_change_notified_data(MP_instance.Part_Number, MP_instance.portfolio_Ownership, MP_instance.CM_download, MP_instance.portfolio_Arista_PIC, MP_instance.sent_to,status="New PO Price Change")
                                    #except Exception as e:
                                    #    LOGGER.error("LOG_MESSAGE", exc_info=1)
                                    
                                    #MP_instance.save()
                    datas.update(**updated_value)
                    print("Updated.....")
                    mp_po_delivery_calc(row['Part_Number'],row['CM_download'],Current_quarter())
            else:
                #print('datas')
                MP_instance=MP_download_table(**row.to_dict())
                MP_instance.save()
                
                #print(MP_instance.Part_Number)
                #print('saved..')
        if len(processed_list) > 2000:
            del_split=math.ceil(len(processed_list)/2000)
        else:
            del_split=50
        for x in np.array_split(processed_list,del_split):
            Processing_list_MP.objects.filter(id__in=list(x)).delete()
        

    except Exception as e:
        LOGGER.error("LOG_MESSAGE", exc_info=1)

        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        print(tb_str)
    finally:
        pass
        # send_mail(subject='Error from CMT Tool',message=tb_str,html_message=tb_str,from_email='Arista',recipient_list=['skarthick@inesssolutions.com'])
def Demand_Coverage(x):

    if x['CQ_ARIS_FQ_sum_1_SANM_Demand'] <1 and x['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'] <1:
        return "No Demand"
    elif (x['CQ_ARIS_FQ_sum_1_SANM_Demand'] >= 1  or x['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'] >= 1 ) and round(x["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"]) == 0 :
        return "Can Cover Demand"
    elif (x['CQ_ARIS_FQ_sum_1_SANM_Demand'] >= 1 or x['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'] >= 1) and x["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"] >= 1 :
        return "Can Cover Demand"
    elif (x['CQ_ARIS_FQ_sum_1_SANM_Demand']>=1 or x['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand']>=1) and x["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"]<1:
        return "Can't Cover Demand"

    # if x['CQ_ARIS_FQ_sum_1_SANM_Demand']<1 and x['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand']<1:
    #     return "No Demand"
    # elif (x['CQ_ARIS_FQ_sum_1_SANM_Demand']>=1 or x['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand']>=1) and x["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"]>=1:
    #     return "Can Cover Demand"
    # elif (x['CQ_ARIS_FQ_sum_1_SANM_Demand']<1 or x['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand']<1) and x["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"]<1:
    #     return "Can't Cover Demand"
    # else:
    #     return ""
def MP_Updater_status(request):
    if request.GET.get('update_all'):
        RFX.objects.filter(sent_quater=Current_quarter()).update(sent_quater=Current_quarter())
        return JsonResponse({'status':'Master Pricing is regenerating as per your request'})
    if request.GET.get('update_portfolio'):
        Portfolio.objects.filter(Quarter=Current_quarter()).update(Quarter=Current_quarter())
        return JsonResponse({'status':'Master Pricing is regenerating as per your request'})
    parts=Processing_list_MP.objects.all()
    if parts.exists():
        return JsonResponse({'status':True})
    else :
        return JsonResponse({'status':False})
from time import sleep
@multi_threading
def MP_Updater():
    try:
        #pandarallel.initialize()
        print('[MP_Updater] Running as Parallel Thread [WATCH DOG]')
        while True:
            try:
                print('[MP_Updater] watching..')
                parts=Processing_list_MP.objects.all()
                while parts.exists():
                    print('[MP_Updater] Parts Changed Updating MP')
                    try:
                        MP_creation('SGD')
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                        print(tb_str)
                        print('MP_Updater stopped')
                        msg=EmailMessage(subject='MP_Updater as error ',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                        msg.send()

                    try:
                        MP_creation('JPE')
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                        print(tb_str)
                        print('MP_Updater stopped')
                        msg=EmailMessage(subject='MP_Updater as error ',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                        msg.send()
                    try:
                        MP_creation('FGN')
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                        print(tb_str)
                        print('MP_Updater stopped')
                        msg=EmailMessage(subject='MP_Updater as error ',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                        msg.send()
                    try:
                        MP_creation('HBG')
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                        print(tb_str)
                        print('MP_Updater stopped')
                        msg=EmailMessage(subject='MP_Updater as error ',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                        msg.send()
                    try:
                        MP_creation('JSJ')
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                        print(tb_str)
                        print('MP_Updater stopped')
                        msg=EmailMessage(subject='MP_Updater as error ',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                        msg.send()
                    try:
                        MP_creation('JMX')
                    except Exception as e:
                        LOGGER.error("LOG_MESSAGE", exc_info=1)
                        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                        print(tb_str)
                        print('MP_Updater stopped')
                        msg=EmailMessage(subject='MP_Updater as error ',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                        msg.send()

                sleep(20)
            except Exception as e:
                tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                print(tb_str)
                print('MP_Updater stopped')
                msg=EmailMessage(subject='MP_Updater as error ',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                msg.send()
                connection.close()
                sleep(30)
                #connection.connect()


    except Exception as e:

        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        ##print(tb_str)
        #print('MP_Updater stopped')

        msg=EmailMessage(subject='MP_Updater stopped',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
        msg.send()
    finally:
        sleep(10)
        MP_Updater()

# MP_Updater(request)


def save_new_po_price_change_notified_data(Part_Number, portfolio_Ownership, CM_download, portfolio_Arista_PIC, sent_to, status):
    '''
    This method will save data while new_po_price has being changed
    '''
    try:
        today = timezone.localtime(timezone.now())
        current_date = today.strftime("%m-%d-%Y, %H:%M:%S")
        if not EmailNotification.objects.filter(Arista_Part_Number=Part_Number,Arista_PIC=portfolio_Arista_PIC,team='GSM Team' if portfolio_Ownership == 'Arista' else 'CMM Team',cm=CM_download,sent_to=sent_to,current_qtr_decision="New PO Price Change",is_email_sent=False).exists():
            notification = EmailNotification(Arista_Part_Number=Part_Number,updated_by='NIL',Mfr_Part_Number='NIL',Arista_PIC=portfolio_Arista_PIC,to="-",bp_email="-",team='GSM Team' if portfolio_Ownership == 'Arista' else 'CMM Team',cm=CM_download,sent_to=sent_to,created_at=current_date,sgd_cm_email = "-",jpe_cm_email = "-",ownership=portfolio_Ownership,current_qtr_decision="New PO Price Change",current_url='NIL',rfx_id='NIL',Mfr_Name='NIL',logged_in_user_group='NIL')
            notification.save()
            LOGGER.info("%s notification details saved successfully", status)
    except Exception as e:
        LOGGER.error("No data for saving %s notification details",status, exc_info=1)

@multi_threading
def trigger_part(part):
    data=RFX.objects.filter(Part_Number=part,sent_quater=Current_quarter())
    for x in data:
        x.save()
        break
def truncate_sisence_table():
    masterpricing_sisense.objects.using('inputdb').raw('TRUNCATE TABLE `InputDB_masterpricing_sisense`')
    masterpricing_sisense.objects.using('inputdb').raw('ALTER TABLE `InputDB_masterpricing_sisense` AUTO_INCREMENT = 1')

def sisense_update(request=None):
    psql = MP_download_table.objects.filter(Quarter=Current_quarter())
    for parts in psql:
        mpdb = masterpricing_sisense()
        mpdb.portfolio_cm_part_number=parts.portfolio_cm_Part_Number
        mpdb.arista_part_number=parts.Part_Number
        mpdb.portfolio_cust_consign=parts.portfolio_Cust_consign
        mpdb.arista_po_delivery=parts.CM_PO_Delivery_Remarks
        mpdb.cm_po_delivery_remarks=parts.po_delivery
        mpdb.cm_quantity_buffer_on_hand=parts.cm_Quantity_Buffer_On_Hand if parts.cm_Quantity_Buffer_On_Hand and not parts.cm_Quantity_Buffer_On_Hand == 'Quote Not Raised' else None
        mpdb.cm_quantity_on_hand_cs_inv=parts.cm_Quantity_On_Hand_CS_Inv if parts.cm_Quantity_On_Hand_CS_Inv and not parts.cm_Quantity_On_Hand_CS_Inv == 'Quote Not Raised' else None
        mpdb.open_po_due_in_this_quarter=parts.Open_PO_due_in_this_quarter if parts.Open_PO_due_in_this_quarter and not parts.Open_PO_due_in_this_quarter == 'Quote Not Raised' else None
        mpdb.open_po_due_in_next_quarter=parts.Open_PO_due_in_next_quarter if parts.Open_PO_due_in_next_quarter and not parts.Open_PO_due_in_next_quarter == 'Quote Not Raised' else None
        mpdb.delivery_based_total_oh_sum_opo_this_quarter=parts.Delivery_Based_Total_OH_sum_OPO_this_quarter if parts.Delivery_Based_Total_OH_sum_OPO_this_quarter and not parts.Delivery_Based_Total_OH_sum_OPO_this_quarter == 'Quote Not Raised' else None
        mpdb.po_based_total_oh_sum_opo=parts.PO_Based_Total_OH_sum_OPO if parts.PO_Based_Total_OH_sum_OPO and not parts.PO_Based_Total_OH_sum_OPO == 'Quote Not Raised' else None
        mpdb.cq_aris_fq_sum_1_sanm_demand=parts.CQ_ARIS_FQ_sum_1_SANM_Demand if parts.CQ_ARIS_FQ_sum_1_SANM_Demand and not parts.CQ_ARIS_FQ_sum_1_SANM_Demand == 'Quote Not Raised' else None
        mpdb.cq_sum_1_aris_fq_sum_2_sanm_demand=parts.CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand if parts.CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand and not parts.CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand == 'Quote Not Raised' else None
        mpdb.cq_sum_2_aris_fq_sum_3_sanm_demand=parts.CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand if parts.CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand and not parts.CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand == 'Quote Not Raised' else None
        mpdb.cq_sum_3_aris_fq_sanm_demand=parts.CQ_sum_3_ARIS_FQ_SANM_Demand if parts.CQ_sum_3_ARIS_FQ_SANM_Demand and not parts.CQ_sum_3_ARIS_FQ_SANM_Demand == 'Quote Not Raised' else None
        mpdb.delta_oh_and_open_po_dd_cq_sum_cq_sum_1_arista=parts.Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista if parts.Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista and not parts.Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista == 'Quote Not Raised' else None
        mpdb.demand_coverage=parts.Demand_Coverage
        mpdb.current_final_std_cost=parts.current_final_std_cost if parts.current_final_std_cost and not parts.current_final_std_cost == 'Quote Not Raised' else None
        mpdb.sent_quater=parts.sent_quater
        mpdb.standard_price_q1=parts.standard_price_q1 if parts.standard_price_q1 and not parts.standard_price_q1 == 'Quote Not Raised' else None
        mpdb.qplus1=parts.quarter
        mpdb.delta_std_previous_std=parts.delta_std_previous_std
        mpdb.delta_std_previous_std_per=parts.delta_std_previous_std_per
        mpdb.portfolio_blended_avg_po_receipt_price=parts.portfolio_Blended_AVG_PO_Receipt_Price if parts.portfolio_Blended_AVG_PO_Receipt_Price and not parts.portfolio_Blended_AVG_PO_Receipt_Price == 'Quote Not Raised' else None
        mpdb.new_po_price=parts.new_po_price if parts.new_po_price and not parts.new_po_price == 'N/A' and not parts.new_po_price == 'Quote Not Raised' else None
        mpdb.approve_reject_std_price=parts.approve_reject_std_price
        mpdb.cm_approve_reject=parts.cm_approve_reject
        mpdb.arista_pic_approve_reject=parts.arista_pic_approve_reject
        mpdb.bp_team_approve_reject_comments=parts.BP_team_Approve_Reject_Comments
        mpdb.current_qtr_decision=parts.current_qtr_decision
        mpdb.arista_pic_updated_data_name=parts.arista_pic_updated_data_name
        mpdb.portfolio_delta_oh_and_ope_previous=parts.portfolio_Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista_previous
        mpdb.standard_price_q1_previous=parts.standard_price_q1_previous if parts.standard_price_q1_previous and not parts.standard_price_q1_previous == 'Quote Not Raised' else None
        mpdb.current_qtr_decision_previous=parts.current_qtr_decision_previous
        mpdb.arista_pic_approve_reject_previous=parts.arista_pic_approve_reject_previous
        mpdb.cm_approve_reject_previous=parts.cm_approve_reject_previous
        mpdb.bp_team_approve_reject_comments_previous=parts.BP_team_Approve_Reject_Comments_previous
        mpdb.cm_additional_notes_on_supplier_distributor_previous=parts.CM_Additional_Notes_on_Supplier_distributor_previous
        mpdb.std_cost=parts.std_cost if parts.std_cost and not parts.std_cost == 'Quote Not Raised' else None
        mpdb.mfr_name=parts.Mfr_Name
        mpdb.sent_to=parts.sent_to
        mpdb.portfolio_item_desc=parts.portfolio_Item_Desc
        mpdb.item_price=parts.Item_Price
        mpdb.portfolio_qualification_status=parts.portfolio_Qualification_Status
        mpdb.po_delivery=parts.PO_Delivery
        mpdb.moq=parts.MOQ
        mpdb.lead_time=parts.Lead_Time
        mpdb.portfolio_mfr_part_number=parts.portfolio_Mfr_Part_Number
        mpdb.ncnr=parts.NCNR
        mpdb.coo=parts.COO
        mpdb.inco_term=parts.Inco_Term
        mpdb.freight_cost=parts.Freight_cost
        mpdb.comments=parts.Comments
        mpdb.soft_hard_tool=parts.soft_hard_tool
        mpdb.portfolio_rev=parts.portfolio_Rev
        mpdb.portfolio_lifecycle_phase=parts.portfolio_Lifecycle_Phase
        mpdb.split=parts.split
        mpdb.portfolio_ownership=parts.portfolio_Ownership
        mpdb.portfolio_arista_pic=parts.portfolio_Arista_PIC
        mpdb.arista_pic_comment=parts.Arista_pic_comment
        mpdb.arista_pic_comments_to_cm=parts.Arista_PIC_Comments_to_CM
        mpdb.arista_bp_comments=parts.Arista_BP_Comments
        mpdb.quoted_by=parts.Quoted_by
        mpdb.cm_updated_data_name=parts.cm_updated_data_name
        mpdb.cm_price=parts.CM_price if parts.CM_price and not parts.CM_price == 'Quote Not Raised' else None
        mpdb.cm_manufacturer=parts.CM_Manufacturer
        mpdb.cm_supplier_distributor_name_from_cm=parts.CM_Supplier_Distributor_name_from_cm
        mpdb.cm_po_delivery=parts.CM_po_delivery
        mpdb.cm_mpn=parts.CM_mpn
        mpdb.cm_moq=parts.CM_MOQ if parts.CM_MOQ and not parts.CM_MOQ == 'Quote Not Raised' else None
        mpdb.cm_lead_time=parts.CM_Lead_Time if parts.CM_Lead_Time and not parts.CM_Lead_Time == 'Quote Not Raised' else None
        mpdb.cm_ncnr=parts.CM_NCNR
        mpdb.cm_tarrif=parts.CM_tarrif
        mpdb.cm_list=parts.CM_List
        mpdb.cm_qty_std_source=parts.CM_qty_std_source
        mpdb.cm_comments=parts.CM_comments
        mpdb.cm_additional_notes_on_supplier_distributor=parts.CM_Additional_Notes_on_Supplier_distributor
        mpdb.cm_buyer=parts.CM_buyer
        mpdb.cm=parts.CM_download
        mpdb.cm_quoted_by=parts.CM_Quoted_by
        mpdb.pic_approval_timestamp=parts.pic_approval_timestamp
        mpdb.modified_by=parts.modified_by
        mpdb.go_with_pic_price=parts.go_with_pic_price
        mpdb.save(using="inputdb")

def mp_po_delivery_calc(pno,cm,qtr):
    datas=MP_download_table.objects.filter(Part_Number=pno,CM_download=cm,Quarter=qtr)
    for MP_instance in datas:
        #Secondary update for New PO Price
        if MP_instance.current_qtr_decision=='Keep Flat' and MP_instance.standard_price_q1 == MP_instance.std_cost and MP_instance.go_with_pic_price != "Yes":
            MP_instance.new_po_price='N/A'
            MP_instance.save()
        elif MP_instance.current_qtr_decision=='Updated Price' and MP_instance.standard_price_q1==MP_instance.std_cost and MP_instance.go_with_pic_price != "Yes":
            MP_instance.new_po_price=None
            MP_instance.save()
        #try:
        #    print(MP_instance.portfolio_Arista_PIC)
        #    usergroup=get_user_group(MP_instance.portfolio_Arista_PIC)
        #    if not "CMM Team" in usergroup:
        #        po_del=mp_po_delivery_calc_logic(MP_instance.Part_Number,MP_instance.Quarter,MP_instance.CM_download)
        #        MP_instance.po_delivery=po_del
        #        MP_instance.save()
        #except Exception as e:
            #tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            #print(e)
        #print(MP_instance.Part_Number)
        print('updated..')

def reset_new_po(request=None):
    path = "/Users/karthicksaravanavelan/Downloads/fwnewpopriceerrorapns"
    os.chdir(path)
    data = pd.read_excel('SGD Date=09-26-2022 Time=00.20.20.xlsx')
    row_iter = data.iterrows()
    for index, row in row_iter:
        if row['Q+1 Decision (Flat/Updated Std Cost)'] == "Keep Flat":
            new_po = "N/A"
        elif row['Q+1 Decision (Flat/Updated Std Cost)'] == "Updated Price":
            new_po = None
        else:
            new_po = None
        MP_download_table.objects.filter(portfolio_cm_Part_Number=row['CM Part Number'],Part_Number=row['Arista Part Number'],sent_quater=row['Current Qtr']).update(new_po_price=new_po)
        ##print(new_po)
    return HttpResponse("Updated")

def test_po_del_logic(request=None):
    print(get_po_delivery_calc(677054))