'''
from CMT.cmt_helper import *
'''
from django import template
from django.contrib.auth.models import User, Group
import datetime
from datetime import timedelta
from django.db import connection
from datetime import date
import random
import string
from portfolio.models import *
import threading
from Slate_CMT.models import *
from portfolio.models import *
from MasterPricing.models import *
from django.db.models import *
from rfx.models import *
from Slate_CMT.templatetags.cmt_helper import *

@register.simple_tag()
def get_arista_ctl_sgd_parts():
    from rfx.models import RFX
    currentqtr=Current_quarter()
    print(currentqtr)
    rfx=RFX.objects.filter(portfolio__Parts_controlled_by='Arista').filter(portfolio__cm='SGD')
    print(rfx)
    return rfx

@register.simple_tag()
def get_po_delivery_calc(id,sent_to=None):
    '''for Customer part we make some calculation for po_delivery based on the count of po and delivery
            If count of delivery is greater than deivery than delivery will be returned else PO
    '''
    print(id)
    print("Inside Actual PO Delivery")
    from rfx.models import RFX
    try:
        init=RFX.objects.get(id=id)
        decision='PO'
        data=RFX.objects.exclude(sent_to='cm').filter(Part_Number=init.Part_Number,quarter=init.quarter,Team=init.Team,cm__in=['Global',init.cm],Quote_status='Quoted')
        if init.split_type=='Automated':
            data=data.order_by('-suggested_split').values()
            split_type='suggested_split'
        else:
            data=data.order_by('-manual_split').values()
            split_type='manual_split'
        print(split_type)

        if data.count()==1:
            decision=data[0]['PO_Delivery']

        elif data.count()==2:
            rfx=RFX.objects.exclude(sent_to='cm').filter(Part_Number=init.Part_Number,quarter=init.quarter,Team=init.Team,cm__in=['Global',init.cm],Quote_status='Quoted').order_by('-'+split_type)
            #print(data[0]['PO_Delivery']==data[1]['PO_Delivery'])
            #print(data[0]['PO_Delivery'],data[1]['PO_Delivery'],data[0]['id'],data[1]['id'])
            po_del = rfx.values_list("PO_Delivery",flat=True)
            po_del = list(po_del)
            split = rfx.values_list(split_type,flat=True)
            split = list(split)
            print(po_del,split)
            if split[0] == split[1]:
                decision= po_del[0] if po_del[0] == po_del[1] else 'PO'
            elif split[0] > split[1]:
                decision= po_del[0]
            elif split[0] < split[1]:
                decision= po_del[1]
            print("Final Decision :",decision)

        elif data.count()>2:
            data=RFX.objects.exclude(sent_to='cm').filter(Part_Number=init.Part_Number,quarter=init.quarter,Team=init.Team,cm__in=['Global',init.cm],Quote_status='Quoted').order_by('-'+split_type).values()
            Po=data.filter(PO_Delivery='PO').aggregate(Sum(split_type))[f'{split_type}__sum']
            Delivery=data.filter(PO_Delivery='Delivery').aggregate(Sum(split_type))[f'{split_type}__sum']
            
            Po=0 if Po==None else Po
            Delivery=0 if Delivery==None else Delivery
            

            if Delivery > Po:
                decision='Delivery'
            else:
                decision='PO'
            print(decision)
            
        else:
            decision=None
            
    except Exception as e:
        print(e)
        decision=None
    #print(decision)
    return decision

@register.simple_tag()
def mp_po_delivery_calc_logic(Part_Number,quarter,cm):
    from rfx.models import RFX
    print("Inside MP PO Delivery")
    '''for Customer part we make some calculation for po_delivery based on the count of po and delivery
            If count of delivery is greater than deivery than delivery will be returned else PO
    '''
    try:
        decision='PO'
        data_ids=RFX.objects.exclude(sent_to='cm').filter(Part_Number=Part_Number,sent_quater=quarter,cm__in=['Global',cm],Quote_status='Quoted').values_list('id',flat=True)
        data_ids = list(data_ids)
        print(data_ids[0])
        data1=RFX.objects.filter(id=data_ids[0]).values('id','split_type','suggested_split','manual_split','PO_Delivery')[:1].get()
        data=RFX.objects.filter(id__in=data_ids).values('id','split_type','suggested_split','manual_split','PO_Delivery')
        print(data[0]['id'])
        print(data[1]['id'])
        if data1['split_type']=='Automated':
            data=data.order_by('-suggested_split').values()
            split_type='suggested_split'
        else:
            data=data.order_by('-manual_split').values()
            split_type='manual_split'
        print(split_type)

        if data.count()==1:
            decision=data[0]['PO_Delivery']

        elif data.count()==2:
            rfx=RFX.objects.filter(id__in=data_ids).values('id','split_type','suggested_split','manual_split','PO_Delivery').order_by('-'+split_type)
            po_del = rfx.values_list("PO_Delivery",flat=True)
            po_del = list(po_del)
            split = rfx.values_list(split_type,flat=True)
            split = list(split)
            print(po_del,split)
            if split[0] == split[1]:
                decision= po_del[0] if po_del[0] == po_del[1] else 'PO'
            elif split[0] > split[1]:
                decision= po_del[0]
            elif split[0] < split[1]:
                decision= po_del[1]

        elif data.count()>2:
            data=RFX.objects.filter(id__in=data_ids).values('id','split_type','suggested_split','manual_split','PO_Delivery').order_by('-'+split_type).values()
            Po=data.filter(PO_Delivery='PO').aggregate(Sum(split_type))[f'{split_type}__sum']
            Delivery=data.filter(PO_Delivery='Delivery').aggregate(Sum(split_type))[f'{split_type}__sum']
            
            Po=0 if Po==None else Po
            Delivery=0 if Delivery==None else Delivery
            

            if Delivery > Po:
                decision='Delivery'
            else:
                decision='PO'
            print(decision)
            
        else:
            decision=None
        
    except Exception as e:
        print(e)
        decision=None
    print(decision)
    return decision

@register.simple_tag()
def get_previous_cost(Part_Number,cat,cm):
    from rfx.models import RFX
    std=RFX.objects.exclude(cm='Global').filter(quarter=Current_quarter(),Part_Number=Part_Number,sent_quater=get_previous_quarter()[0],cm=cm,Quote_status='Quoted').values_list(cat,flat=True)
    portfolio_cost=RFX.objects.filter(quarter=Current_quarter(),Part_Number=Part_Number,sent_quater=Current_quarter(),cm=cm).values_list('portfolio__sgd_jpe_cost',flat=True)
    if not std :
        return [None]
    print([std[0],portfolio_cost[0] if portfolio_cost else None])
    
    return [std[0],portfolio_cost[0] if portfolio_cost else None]

def get_previous_std_cost(Part_Number,cat,cm):
    from rfx.models import RFX
    std=RFX.objects.exclude(cm='Global').filter(quarter=Current_quarter(),Part_Number=Part_Number,sent_quater=get_previous_quarter()[0],cm=cm,Quote_status='Quoted').values_list(cat,flat=True)
    portfolio_cost=Portfolio.objects.exclude(cm='Global').filter(Quarter=Current_quarter(),Number=Part_Number,cm=cm).order_by('-ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std').values_list('ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std',flat=True)
    if not std :
        if  portfolio_cost:
            return portfolio_cost[0]
        return None
    return std[0] or portfolio_cost[0] if portfolio_cost else None

@multi_threading
def send_logger_tele(text):
    # try:
    #     import telebot
    #     bot=telebot.TeleBot("1298031498:AAEf0sl_DmiAMa3JqP1qlGk_79ApLw-XHxU")
    #     bot.send_message(110663594,str(text))
    #     print(text)
    # except:
    #     print(text)
    print(text)