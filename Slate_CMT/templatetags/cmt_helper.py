'''
from CMT.cmt_helper import *
'''
from django.shortcuts import render,redirect
from time import sleep
from django import template
from django.http import JsonResponse,HttpResponse
from django.core.mail import EmailMessage
from django.db.models import Value as V
from django.db.models.functions import Concat   
from django.conf import settings
import json
from django.contrib.auth.models import User, Group
import datetime
from datetime import timedelta
from django.db import connection
from datetime import date
from email.utils import make_msgid

from dateutil.relativedelta import relativedelta
import random
import string
from portfolio.models import *
import threading

from portfolio.models import *
import os

from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.template.loader import render_to_string
import traceback
import sys
from django.template.loader import get_template

from django.test.client import RequestFactory
import logging

LOGGER = logging.getLogger(__name__)

# from MasterPricing.models import *
from django.db.models import Sum

register = template.Library()
# print(settings.PRODUCTION)
# production=settings.PRODUCTION
stage='arista-mpat.sandbox.inesssolutions.net'
@register.simple_tag
def Current_quarter(monthAsInt=int(date.today().strftime("%m"))):
    today = date.today()

    if monthAsInt<=3 and  monthAsInt>0:
        quarter="Q1'"+today.strftime("%y")
        return quarter
    elif monthAsInt<=6 and monthAsInt>=4 :
        quarter="Q2'"+today.strftime("%y")
        return quarter
    elif monthAsInt<=9 and monthAsInt>=7 :
        quarter="Q3'"+today.strftime("%y")
        return quarter
    elif monthAsInt<=12 and monthAsInt>=10 :
        quarter="Q4'"+today.strftime("%y")
        return quarter
    else:
        raise ValueError('The Month is Incorrect')

@register.simple_tag
def getLastDayOfquarter():
    today = date.today()
    monthAsInt=int(today.strftime("%m"))
    if monthAsInt<=4:
        quarter=today.strftime("%Y")+'-05-01'
        return quarter
    elif monthAsInt<=7 and monthAsInt>4 :
        quarter=today.strftime("%Y")+'-08-01'
        return quarter
    elif monthAsInt<=10 and monthAsInt>7 :
        quarter=today.strftime("%Y")+'-11-01'
        return quarter
    elif monthAsInt<=12 and monthAsInt>10 :
        quarter=today.strftime("%Y")+'-12-31'
        return quarter
    else:
        raise ValueError('The Month is Incorrect')
@register.simple_tag
def get_Next_quarter(q=4,s=Current_quarter(),this_quarter=False,prefix='',suffix=''):
    # print('into next quarter')
    year=int(s[3:])
    Q=int(s[1:2])
    quarter=[]
    for x in range(q):
        Q=1 if Q>3 else Q+1
        year=year+1 if Q==1 else year
        quarter.append(f'''Q{Q}'{year}''')
    if this_quarter:
        quarter.insert(0,f'''{prefix}{s}{suffix}''')
    return quarter

@register.simple_tag
def get_previous_quarter(q=4,s=Current_quarter(),this_quarter=False,prefix='',suffix=''):
    year=int(s[3:])
    Q=int(s[1:2])
    quarter=[]
    for x in range(q):
        Q=4 if Q<2 else Q-1
        year=year-1 if Q==4 else year
        quarter.append(f'''{prefix}Q{Q}'{year}{suffix}''')
    if this_quarter:
        quarter.insert(0,f'''{prefix}{s}{suffix}''')
    return quarter


@register.filter(name='has_group')
def has_group(user, group_name):
    g_l=group_name.split(',')
    g_l=[x.strip() for x in g_l]
    return user.groups.filter(name__in=g_l).exists()


@register.filter('dict_key')
def get_value_from_dict(dict_data, key):
    """
    usage example {{ your_dict|dict_key:your_key }}
    """
    try:
        if key:
            return dict_data.get(key)
    except:
        return ''
@register.simple_tag
def ORM(query):

	data=eval(query)
	return data

@register.simple_tag(name='sum')
def sum_list(*args):
    try:
        data=list(args)
        total=sum(data)
        print(total)
        return total
    except Exception as e:
        print(e)
        return '-'

@register.simple_tag
def has_permission(user,group=None):
    
    if group=='Supplier':
            if user in User.objects.filter(groups=Group.objects.get(name='Suppliers/Distributors')):
                return True
            else:return False
    elif group=='PIC':
            if user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or user in User.objects.filter(groups=Group.objects.get(name='CMM Team')) or user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or user in User.objects.filter(groups=Group.objects.get(name='Iness')):
                return True
            else:return False
    elif group=='Manager':
            if user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')):
                return True
            else:return False
    elif group=='Contract Manufacturer' :
            if user in User.objects.filter(groups=Group.objects.get(name='SGD Contract Manufacturer')) or user in User.objects.filter(groups=Group.objects.get(name='JPE Contract Manufacturer')) or user in User.objects.filter(groups=Group.objects.get(name='FGN Contract Manufacturer')) or user in User.objects.filter(groups=Group.objects.get(name='HBG Contract Manufacturer')) :
                return True
            else:return False
    elif group=='Iness' :
            if user in User.objects.filter(groups=Group.objects.get(name='Iness'))  :
                return True
            else:return False
    # elif user.is_superuser :
    #     return True
    # elif user in User.objects.filter(groups=Group.objects.get(name='Director')):
    #     return True
    else:
        if group=='GSM Manager':
            if user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) :
                return True
        elif group=='CMM Manager':
            if user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) :
                return True
            else:return False
        elif group=='BP Team':
            if user in User.objects.filter(groups=Group.objects.get(name='BP Team'))  or user in User.objects.filter(groups=Group.objects.get(name='BP Manager')):
                return True
            else:return False
        elif group=='BP Manager':
            if  user in User.objects.filter(groups=Group.objects.get(name='BP Manager')) or user in User.objects.filter(groups=Group.objects.get(name='BP JPE Manager')) or user in User.objects.filter(groups=Group.objects.get(name='BP SGD Manager')) or user in User.objects.filter(groups=Group.objects.get(name='BP FGN Manager')) or user in User.objects.filter(groups=Group.objects.get(name='BP HBG Manager')):
                return True
            else:return False
        elif group.startswith('CMM'):
            if user in User.objects.filter(groups=Group.objects.get(name='CMM Team')) or user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or user in User.objects.filter(groups=Group.objects.get(name='Iness')):
                return True
            else:return False
        elif group.startswith('GSM'):
            if user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or user in User.objects.filter(groups=Group.objects.get(name='Iness')):
                return True
            else:return False
        elif group=='JPE Contract Manufacturer' :
            if user in User.objects.filter(groups=Group.objects.get(name='JPE Contract Manufacturer')) :
                return True
            else:return False
        elif group=='SGD Contract Manufacturer' :
            if user in User.objects.filter(groups=Group.objects.get(name='SGD Contract Manufacturer')):
                return True
        elif group=='FGN Contract Manufacturer' :
            if user in User.objects.filter(groups=Group.objects.get(name='FGN Contract Manufacturer')):
                return True
            else:return False
        elif group=='HBG Contract Manufacturer' :
            if user in User.objects.filter(groups=Group.objects.get(name='HBG Contract Manufacturer')):
                return True
            else:return False
        elif group=='Contract Manufacturer' :
            if user in User.objects.filter(groups=Group.objects.get(name='SGD Contract Manufacturer')) or user in User.objects.filter(groups=Group.objects.get(name='JPE Contract Manufacturer')) or user in User.objects.filter(groups=Group.objects.get(name='FGN Contract Manufacturer')) or user in User.objects.filter(groups=Group.objects.get(name='HBG Contract Manufacturer')):
                return True
            else:return False

        elif group=='Super User':
            if user in User.objects.filter(groups=Group.objects.get(name='Super User')):
                return True
            else:return False
        elif group=='Manager':
            if user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')):
                return True
            else:return False
        elif group=='Director':
            if user in User.objects.filter(groups=Group.objects.get(name='Director')):
                return True
            else:return False
        elif group=='Supplier':
            if user in User.objects.filter(groups=Group.objects.get(name='Suppliers/Distributors')):
                return True
            else:return False
        else:
            return False
def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))


def multi_threading(function):
    def decorator(*args, **kwargs):
        t = threading.Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator


@register.simple_tag
def current_qtr_start_end():
    now = datetime.datetime.now().month
    year = datetime.datetime.now().year
    if (now >= 1 and now <= 3):
        start = str(year) + "-01-01"
        end = str(year) + "-03-31"
    elif (now >= 4 and now <= 6):
        start = str(year) + "-04-01"
        end = str(year) + "-06-30"
    elif (now >= 7 and now <= 9):
        start = str(year) + "-07-01"
        end = str(year) + "-09-30"
    else:
        start = str(year) + "-10-01"
        end = str(year) + "-12-31"
    start_end = [start, end]

    return start_end

@register.simple_tag
def qtr_start_end_manual(value):
    #print(value)
    if value == '0':
        date = datetime.datetime.today()
    elif value == '1':
        date = datetime.datetime.today() + relativedelta(months=+3)
    elif value == '2':
        date = datetime.datetime.today() + relativedelta(months=+6)
    elif value == '3':
        date = datetime.datetime.today() + relativedelta(months=+9)
    elif value == '4':
        date = datetime.datetime.today() + relativedelta(months=+12)
    else :
        date = datetime.datetime.today()
    #print(date)
    now = date.month
    year = date.year
    if (now >= 1 and now <= 3):
        start = str(year) + "-04-01"
        end = str(year) + "-06-30"
        Qtr = "Q2'" + str(year)[-2:]
    elif (now >= 4 and now <= 6):
        start = str(year) + "-07-01"
        end = str(year) + "-09-30"
        Qtr = "Q3'" + str(year)[-2:]
    elif (now >= 7 and now <= 9):
        start = str(year) + "-10-01"
        end = str(year) + "-12-31"
        Qtr = "Q4'" + str(year)[-2:]
    else:
        start = str(year + 1) + "-01-01"
        end = str(year + 1) + "-03-31"
        Qtr = "Q1'" + str(year + 1)[-2:]
    start_end = [start, end, Qtr]

    return start_end


def quote_qtr_start_end():
    now = datetime.datetime.now().month
    year = datetime.datetime.now().year
    if (now >= 1 and now <= 3):
        start = str(year) + "-04-01"
        end = str(year) + "-06-30"
        q4end = str(year + 1) + "-03-31"
        scenariostart = str(year - 1) + "-12-15"
        scenarioend = str(year - 1) + "-12-31"
    elif (now >= 4 and now <= 6):
        start = str(year) + "-07-01"
        end = str(year) + "-09-30"
        q4end = str(year + 1) + "-06-30"
        scenariostart = str(year) + "-03-15"
        scenarioend = str(year) + "-03-31"
    elif (now >= 7 and now <= 9):
        start = str(year) + "-10-01"
        end = str(year) + "-12-31"
        q4end = str(year + 1) + "-09-31"
        scenariostart = str(year) + "-06-15"
        scenarioend = str(year) + "-06-30"
    else:
        start = str(year + 1) + "-01-01"
        end = str(year + 1) + "-03-31"
        q4end = str(year + 1) + "-12-31"
        scenariostart = str(year) + "-09-15"
        scenarioend = str(year) + "-09-30"
    start_end = [start, end, q4end, scenariostart, scenarioend]

    return start_end



def compare_values_dict(old_data,new_data):
    data_old={}
    data_new={}
    for k,v in old_data.items():
        if not old_data[k]==new_data[k]:
            data_old[k]=old_data[k]
            data_new[k]=new_data[k]
    return [data_old,data_new]

@register.simple_tag
def is_in_group(var, args):
	if args is None:
		return False
	arg_list = [arg.strip() for arg in args.split(',')]
	return var in arg_list

@register.simple_tag()
def get_user_name(user):
    username = user.first_name + " " + user.last_name
    return username



# @register.simple_tag()
# def get_po_delivery_calc(id):
#     if Portfolio.objects.filter(id=id).exists():
#         data = Portfolio.objects.get(id=id)
#         if MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).filter(mpn_level_po_delivery_q1="PO").exists() and MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).exclude(mpn_level_po_delivery_q1="PO").exists():
#             pos=MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).filter(mpn_level_po_delivery_q1="PO").exclude(split_q1=None)
#             deliverys=MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).exclude(mpn_level_po_delivery_q1="PO").exclude(split_q1=None)
#             totsplit_po=0
#             totsplit_del=0
#             for po in pos:
#                 totsplit_po = totsplit_po + float(po.split_q1)
#             for delivery in deliverys:
#                 totsplit_del = totsplit_del + float(delivery.split_q1)
#             if totsplit_po > totsplit_del:
#                 podelivery = pos[0].mpn_level_po_delivery_q1
#             elif totsplit_po == totsplit_del:
#                 podelivery = pos[0].mpn_level_po_delivery_q1
#             else:
#                 podelivery = deliverys[0].mpn_level_po_delivery_q1
#         elif MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).filter(mpn_level_po_delivery_q1="PO").exists():
#             po = MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).filter(mpn_level_po_delivery_q1="PO")
#             podelivery = po[0].mpn_level_po_delivery_q1
#         elif MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).exclude(mpn_level_po_delivery_q1="PO").exists():
#             delivery = MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).exclude(mpn_level_po_delivery_q1="PO")
#             podelivery = delivery[0].mpn_level_po_delivery_q1
#         MPTemplate.objects.filter(arista_partno=data.Arista_Part_Number).filter(quarter=data.Quarter).filter(cm=data.cm).update(po_delivery=podelivery)
#         return podelivery
#     return None

Month=[ "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",]
Q1=Month[0:3]
Q2=Month[3:6]
Q3=Month[6:9]
Q4=Month[9:12]


def send_file_via_email(request,filename,subject='File from MPT',body='''
Here is the file
<a href='{%filename%}' target='_blank'>click here</a>
'''):
    base_url=get_current_site(request).domain
    path=reverse('file_download_via_email',args=[filename])
    html=body.replace('{%filename%}',f"http://{base_url}{path}")
    if base_url==production or base_url==stage :
        to_mail=request.user.email
    else:
        to_mail='srinithin@inesssolutions.com'
    try:send_push_notification(request.user, subject=subject, text=strip_tags(html), url=f"http://{base_url}{path}")
    except:pass
    status=send_mail(subject=subject,message=body,html_message=html,from_email='iness@gmail.com',recipient_list=[to_mail,'srinithins@arista.com'])
    print(status)
@multi_threading
def send_notification(request,user_to=None,to_mail_id=None,to=None,user_from=None,body='',subject='',title=None,from_name='',Attach_file=None,**extra):
    sleep(random.randint(0,10))
    subject=subject.strip()
    title=title or subject.replace('\n','')
    base_url=get_current_site(request).domain
    print(base_url,production)

    if base_url==production:
        message = render_to_string('email/genric_template.html',{'title':title.replace('\n','<br>'),'body':body.replace('\n','<br>'),'base_url':base_url})
        try:
            cc=extra['cc']
        except:
            cc=[]
        try:
            msg=EmailMessage(subject=subject.replace('\n',''),body=message,from_email=f'{user_from} <srv-masterpricing@arista.com>', to= to if to else[to_mail_id if user_to==None else user_to.email],cc=cc)
            msg.content_subtype = 'html'
            if Attach_file:
                msg.attach(Attach_file[0], Attach_file[1], 'application/ms-excel')
                
            msg.extra_headers['Message-ID'] = make_msgid()
            # status=msg.send()
            print("before save data: base_url==production")
            try:
                mail_sent_by = request.user.first_name+" "+request.user.last_name
                email_data = DataToHandleMailing(
                        mail_status = 'Outbox',
                        message_id = msg.extra_headers['Message-ID'],
                        from_address = settings.EMAIL_HOST_USER,
                        to_address = to if to else[to_mail_id if user_to==None else user_to.email],
                        cc_address = cc,
                        mail_subject = subject,
                        mail_content = message,
                        mail_triggered_by = mail_sent_by
                        )
                print("mail_sent_by:", mail_sent_by)
                
                email_data.save()
            except Exception as e:
                print(e)
            
            if not status:
                send_logger_tele(f"Failed to send mail to {to_mail_id if user_to==None else user_to.email} by the sender {user_from} ")
        except Exception as e:
                print(e)
                status=EmailMessage('Email Failed to send',body=message,from_email=f'Failed from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                # status=msg.send()
    else:
        message = render_to_string('email/genric_template.html',{'title':title.replace('\n','<br>'),'body':body.replace('\n','<br>'),'base_url':base_url})
        try:
            cc=extra['cc']
        except:
            cc=[]
        try:
            print(to ,cc)
            msg=EmailMessage(subject=subject.replace('\n',''),body=f"{'*'*20}<br>to={to if to else[to_mail_id if user_to==None else user_to.email]}<br>cc={cc}<br> test version<br>{'*'*20}<br>"+message,from_email=f'{user_from} <srv-masterpricing@arista.com>', to=['srinithin@inesssolutions.com'],cc=['skarthick@inesssolutions.com'])
            msg.content_subtype = 'html'
            if Attach_file:
                msg.attach(Attach_file[0], Attach_file[1], 'application/ms-excel')
            msg.extra_headers['Message-ID'] = make_msgid()
            # status=msg.send()
            print("before save data: >>>")
            
            try:
                mail_sent_by = request.user.first_name+" "+request.user.last_name
                email_data = DataToHandleMailing(
                        mail_status = 'Outbox',
                        message_id = msg.extra_headers['Message-ID'],
                        from_address = settings.EMAIL_HOST_USER,
                        to_address = ['srinithin@inesssolutions.com'],
                        cc_address = ['skarthick@inesssolutions.com'],
                        mail_subject = subject,
                        mail_content = message,
                        mail_triggered_by = mail_sent_by
                        )
                print("mail_sent_by:", mail_sent_by)
                email_data.save()
            except Exception as e:
                print(e)
            if not status:
                send_logger_tele(f"Failed to send mail to {to_mail_id if user_to==None else user_to.email} by the sender {user_from} ")
        except Exception as e:
                print(e)
                status=EmailMessage('Email Failed to send',body=message,from_email=f'Failed from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
                # status=msg.send()
def get_url(request):
    return get_current_site(request).domain



@register.simple_tag()
def his_notification(request,type='None'):
    notification=Master_notification.objects.filter(user=request.user,notification_read=False).order_by('-created_on')
    unread=Master_notification.objects.filter(user=request.user,notification_read=False).count()
    if type=='text':
        return [render_to_string("notifications_content.html",{'notifications':[notification,unread]}),unread]
    else:
        return render(request,"notifications_content.html",{'notifications':[notification,unread]})

def make_as_read_notification(request):
    notification=Master_notification.objects.filter(user=request.user)
    unread=Master_notification.objects.filter(user=request.user).update(notification_read=True)
    return JsonResponse({'message':'success'})

def send_push_notification(user,subject='You Have notifcation',text='No text',url='/',args=[]):
    try:
        url=reverse(url,args=args)
    except Exception as e:
        print(e)
        url=url
    instance=Master_notification(
        user=user,
        message=subject,
        text=text,
        url=url,
    )
    instance.save()
    payload = {'head': 'Master Pricing Tool', 'body': subject, 'url': url}
    send_user_notification(user, payload=payload, ttl=1000)
    return True

@multi_threading
def send_logger_tele(text):
    # try:
    #     # bot=telebot.TeleBot("1298031498:AAEf0sl_DmiAMa3JqP1qlGk_79ApLw-XHxU")
    #     # bot.send_message(110663594,str(text))
    #     print(text)
    # except:
        # print(text)
    print(text)

def error_handle(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            print(tb_str)
            msg=EmailMessage(subject='Error with traceback',body=tb_str,from_email=f'Error from MPAT <srv-masterpricing@arista.com>', to=['skarthick@inesssolutions.com'])
            # msg.send()
            send_logger_tele(tb_str)
            return None
    return inner
def error_handle_500(func):
    def inner(*args, **kwargs):
        try:
            try:request=args[0]
            except:request=[]
            return func(*args, **kwargs)
        except Exception as e:
            try:
                return render(request,'500.html')
            except:
                pass
            tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            print(tb_str)
            send_logger_tele(tb_str)
            return None
    return inner


@register.simple_tag()
def names_of_pic(Team=None):
    print(Team)
    data= User.objects.filter(groups__name__in=['GSM Team','CMM Team','GSM Manager','CMM Manager'])
    # data= User.objects.filter(groups=Group.objects.get(name=Team))
    names=[[f"{x.first_name} {x.last_name}",x.id]for x in data]
    return names


@register.simple_tag()
def suggested_moq(demand):
    try:
        per_demand=demand/100
        suggested_moq=int(per_demand*15)
        print(suggested_moq)
        return suggested_moq
    except:
        return None

@multi_threading
def auto_clean_rfx_cm():
    '''Clean the data from rfx where there is multiple quote for cm '''
    for cm in ['SGD','JPE','FGN','HBG']:
        from rfx.models import RFX
        data=RFX.objects.filter(sent_to='cm',sent_quater=Current_quarter(),quarter=get_Next_quarter()[0],cm=cm)
        for x in data:
            for j in data.filter(Part_Number=x.Part_Number).order_by('-Quote_status')[1:]:
                print(j)
                j.delete()

def negative_validator(data,message='field'):
    if data!=None and str(int(data)).isdigit():
        if float(data)>0:
            print(data,message)
            return data
        else:
            raise ValueError(f'Invalid data should be greater than 0 on {message}')
    else:
        return data
    

def previous_values(field,part,Mfr_Name,portfolio__Ownership,sent_to,portfolio_Mfr_Part_Number,Quarter=None):
    from rfx.models import RFX
    print(field,part,sent_to,portfolio_Mfr_Part_Number)
    q=RFX.objects.filter(sent_quater=get_previous_quarter()[0],sent_to=sent_to,Part_Number=part,Mfr_Name=Mfr_Name,portfolio__Ownership=portfolio__Ownership,portfolio__Mfr_Part_Number=portfolio_Mfr_Part_Number).values_list(field,flat=True)
    if q:
        return list(q)[0]
    else:
        return None
@register.simple_tag()
def rfq_raise_count(request,Team):
    from rfx.models import RFX
    print(Team)
    if has_permission(request.user,'Manager') or request.user.is_superuser:
        total_global=Portfolio.objects.filter(Quarter=Current_quarter(),cm='Global',Team__icontains=Team).count()
        total_region=Portfolio.objects.filter(Quarter=Current_quarter(),Team__icontains=Team).exclude(cm='Global').count()
        total_APN=Portfolio.objects.filter(Quarter=Current_quarter(),Team__icontains=Team).exclude(cm='Global').distinct('Number').count()
        total=total_global+total_region
        total_raised=RFX.objects.exclude(sent_to='cm').filter(portfolio__in=Portfolio.objects.filter(Quarter=Current_quarter(),Team__icontains=Team)).count()
        total_raised_APN=RFX.objects.exclude(sent_to='cm').filter(portfolio__in=Portfolio.objects.filter(Quarter=Current_quarter(),Team__icontains=Team)).distinct('portfolio__Number').count()
    else:
        total_global=Portfolio.objects.filter(Arista_PIC__icontains=f'{request.user.first_name}').filter(Quarter=Current_quarter(),cm='Global',Team__icontains=Team).count()
        total_region=Portfolio.objects.filter(Arista_PIC__icontains=f'{request.user.first_name}').filter(Quarter=Current_quarter(),Team__icontains=Team).exclude(cm='Global').count()
        total_APN=Portfolio.objects.filter(Arista_PIC__icontains=f'{request.user.first_name}').filter(Quarter=Current_quarter(),cm='Global',Team__icontains=Team).distinct('Number').count()
        total=total_global+total_region
        total_raised=RFX.objects.exclude(sent_to='cm').filter(portfolio__in=Portfolio.objects.filter(Arista_PIC__icontains=f'{request.user.first_name}',Quarter=Current_quarter(),Team__icontains=Team)).count()
        total_raised_APN=RFX.objects.exclude(sent_to='cm').filter(portfolio__in=Portfolio.objects.filter(Arista_PIC__icontains=f'{request.user.first_name}',Quarter=Current_quarter(),Team__icontains=Team)).distinct('portfolio__Number').count()
    print([total_global,total_region,total,total_raised])

    return [total_global,total_region,total,total_raised,0 if total==0 else (total_raised/total)*100,total_APN,total_raised_APN]

@register.simple_tag()
def is_distributor(user):
    from Supplier.models import suppliers_detail
    data=suppliers_detail.objects.filter(user_model__email__iexact=user.email,Distributor__isnull=False).exclude(Distributor='')

    if data.exists():
        Distributor=data[0].Distributor
        if Distributor:
            return True
        else:
            return False
    else:
        return False
@register.simple_tag()
def which_login(user):
    from Supplier.models import suppliers_detail
    data=suppliers_detail.objects.filter(user_model=user)
    if data.exists():
        Team=data[0].Team
        return Team
    else:
        return None

def find_partial_quote(portfolio,to_cal=False):
    '''returns a dict of data to find if any quote is raised or not,compare the portfolio in rfx table'''
    from rfx.models import RFX
    from Supplier.models import suppliers_detail
    user_owner=User.objects.annotate(full_name=Concat('first_name', V(' '),'last_name')).filter(full_name__icontains=portfolio.Arista_PIC)
    sent_r=RFX.objects.exclude(sent_to__in=['supplier','cm']).filter(portfolio=portfolio,sent_quater=Current_quarter())
    sent_dist=sent_r.filter(quarter=get_Next_quarter(q=1)[0]).values_list('sent_to',flat=True)
    sent_dist_Q=sent_r.filter(quarter=Current_quarter()).values_list('sent_to',flat=True)

    send_count=sent_r.count()
    
    sent_supplier_q1=RFX.objects.filter(sent_to='supplier').filter(portfolio=portfolio,sent_quater=Current_quarter(),quarter=get_Next_quarter(q=1)[0]).count()
    sent_supplier_q=RFX.objects.filter(sent_to='supplier').filter(portfolio=portfolio,sent_quater=Current_quarter(),quarter=Current_quarter()).count()
    
    sent_dist_q1=RFX.objects.exclude(sent_to__in=['supplier','cm']).filter(portfolio=portfolio,sent_quater=Current_quarter(),quarter=get_Next_quarter(q=1)[0]).count()
    sent_dist_q=RFX.objects.exclude(sent_to__in=['supplier','cm']).filter(portfolio=portfolio,sent_quater=Current_quarter(),quarter=Current_quarter()).count()
    print(sent_supplier_q1 , sent_supplier_q , sent_dist_q1 , sent_dist_q)
    dist_count=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,Supplier_Name=portfolio.Mfr_Name,Team=portfolio.Team,Distributor__isnull=False).filter(User_created__in=user_owner).distinct('Distributor').count()
    supp_count=suppliers_detail.objects.filter(is_active=True,user_model__is_active=True,Supplier_Name=portfolio.Mfr_Name,Team=portfolio.Team,Distributor__isnull=True).filter(User_created__in=user_owner).distinct('Supplier_Name').count()
    decision_tree=[sent_supplier_q1>=supp_count,sent_supplier_q>=supp_count , sent_dist_q1>=dist_count , sent_dist_q>=dist_count]
    # print(decision_tree)
    decision=False if False in decision_tree else True
    sent=any([sent_dist_q1 , sent_dist_q])
    sent_all=any([sent_supplier_q1 , sent_supplier_q , sent_dist_q1 , sent_dist_q])
    print(decision,sent_all,supp_count,dist_count)
    payload={
        'all':decision and sent_all,
        'sent':sent,
        'sent_all':sent_all,
        'dis':dist_count,
        'supp':supp_count,
        'partial':not decision,
        'dis_q':sent_dist_q,
        'dis_q1':sent_dist_q1,
        'supp_q':sent_supplier_q,
        'supp_q1':sent_supplier_q1,
        
        }
    if to_cal:
        payload['sent_dist']=list(sent_dist)
        payload['sent_dist_q']=list(sent_dist_Q)

    # print(payload)
    return payload

def get_quote_status(portfolio):
    data=find_partial_quote(portfolio)
    if data['all']:
        return 'Quote Raised'
    elif data['partial']:
        return 'Partially Raised'
    elif data['sent'] ==False:
        return 'Not Raised'
    else:
        return 'Not Raised'
def if_raised_Global(item):
    from rfx.models import RFX
    return RFX.objects.filter(sent_quater=Current_quarter(),Part_Number=item.Number,Team=item.Team,cm__in=['Global'] if item.cm!='Global' else ['JPE','SGD','FXN','HBG','JSJ','JMX']).exists()

def check_rfx_global(items_id):
    '''
    This will return list of data which if the part have global rfq raised
    '''
    from rfx.models import RFX
    data=[]
    for item_id in items_id:
        instance=Portfolio.objects.get(id=item_id)
        if not if_raised_Global(instance):
            data.append(item_id)
        else:
            pass
    print(data)
    return data

def get_mail_id(pic_name):
    pic_name=pic_name.strip()
    user_data=User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name__icontains=pic_name)
    if user_data.exists():
        return user_data[0].email
    else :
        return ''
def recalculate_global(partnumber):
    columns=["Number",
    "Lifecycle_Phase",
    "Rev",
    "Mfr_Name",
    "Mfr_Part_Lifecycle_Phase",
    "Mfr_Part_Number",
    "Qualification_Status",
    "cm_Part_Number",
    "Arista_Part_Number",
    "Cust_consign",
    "Parts_controlled_by",
    "Item_Desc",
    "LT",
    "MOQ",
    "Original_PO_Delivery_sent_by_Mexico",
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
    "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
    "ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std",
    "CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD",
    "Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1",
    "Blended_AVG_PO_Receipt_Price",
    "Ownership",
    "Arista_PIC",
    'Quarter',
    'file_from',
    ]
    portfolio=Portfolio.objects.filter(Quarter=Current_quarter(),Number__in=[partnumber],file_from='JPE').exclude(cm='Global').values(*columns).to_dataframe()
    portfolio2=Portfolio.objects.filter(Quarter=Current_quarter(),Number__in=[partnumber],file_from='SGD').exclude(cm='Global').values(*columns).to_dataframe()
    print(portfolio,portfolio2)
    join_field=[
        'unique_field',
        'cm_Quantity_Buffer_On_Hand', 'cm_Quantity_On_Hand_CS_Inv',
        'Open_PO_due_in_this_quarter', 'Open_PO_due_in_next_quarter',
        'Delivery_Based_Total_OH_sum_OPO_this_quarter',
        'PO_Based_Total_OH_sum_OPO', 'CQ_ARIS_FQ_sum_1_SANM_Demand',
        'CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand',
        'CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand', 'CQ_sum_3_ARIS_FQ_SANM_Demand',
        'Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista',
        'ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std',
        'CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD',
        'Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1',
        'Blended_AVG_PO_Receipt_Price',
        'file_from',
        ]
    def concat_cm(s):
        s=s.to_list()
        return json.dumps(s)

    def order(price_list,cm_list):
        price_list=json.loads(price_list)[:2]
        cm_list=json.loads(cm_list)[:2]
        
        try:
            place_sgd=cm_list.index('SGD')
            sgd_price=round(price_list[place_sgd],5)
        except:
            sgd_price='-'
        try:
            place_jpe=cm_list.index('JPE')
            jpe_price=round(price_list[place_jpe],5)
        except:
            jpe_price='-'
        data=f'{sgd_price}/{jpe_price}'
        return data
    

    portfolio_bak=portfolio.copy()
    portfolio2_bak=portfolio2.copy()

    portfolio_bak['unique_field']=portfolio_bak['Mfr_Name'].astype(str)+'###'+portfolio_bak['Number'].astype(str)+'###'+portfolio_bak['Mfr_Part_Number'].astype(str)+'###'+portfolio_bak['Ownership'].astype(str)
    portfolio2_bak['unique_field']=portfolio2_bak['Mfr_Name'].astype(str)+'###'+portfolio2_bak['Number'].astype(str)+'###'+portfolio2_bak['Mfr_Part_Number'].astype(str)+'###'+portfolio2_bak['Ownership'].astype(str)

    portfolio_global_bak=portfolio_bak.append(portfolio2_bak,ignore_index=True)
    portfolio_global_bak.drop(join_field[1:],axis=1,inplace=True)





    portfolio['unique_field']=portfolio['Mfr_Name'].astype(str)+'###'+portfolio['Number'].astype(str)+'###'+portfolio['Mfr_Part_Number'].astype(str)+'###'+portfolio['Ownership'].astype(str)
    portfolio2['unique_field']=portfolio2['Mfr_Name'].astype(str)+'###'+portfolio2['Number'].astype(str)+'###'+portfolio2['Mfr_Part_Number'].astype(str)+'###'+portfolio2['Ownership'].astype(str)
    # portfolio['file_from']='SGD'
    # portfolio2['file_from']='JPE'

    portfolio_global=portfolio.append(portfolio2,ignore_index=True)

    del portfolio['unique_field']
    del portfolio2['unique_field']

    portfolio_global=portfolio_global.filter(join_field)
    portfolio_global.fillna(0,inplace=True)
    portfolio_global['cm_Quantity_Buffer_On_Hand']=portfolio_global['cm_Quantity_Buffer_On_Hand'].astype('int64')
    portfolio_global=portfolio_global.groupby('unique_field').agg(
        {
        "cm_Quantity_Buffer_On_Hand":'sum',
        "cm_Quantity_On_Hand_CS_Inv":'sum',
        "Open_PO_due_in_this_quarter":'sum',
        "Open_PO_due_in_next_quarter":'sum',
        "Delivery_Based_Total_OH_sum_OPO_this_quarter":'sum',
        "PO_Based_Total_OH_sum_OPO":'sum',
        "CQ_ARIS_FQ_sum_1_SANM_Demand":'sum',
        "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":'sum',
        "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand":'sum',
        "CQ_sum_3_ARIS_FQ_SANM_Demand":'sum',
        "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista":'sum',
        "CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD":'sum',
        "Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1":'sum',
        "Blended_AVG_PO_Receipt_Price":'sum', 
        "ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std":['sum',concat_cm],
        "file_from":concat_cm
        }
    )
    portfolio_global.columns = [
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
            "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
            "CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD",
            "Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1",
            "Blended_AVG_PO_Receipt_Price",
            "ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std",
            "std_cost",
            "file_from",
    ]
    portfolio_global = portfolio_global.reset_index()
    portfolio_global["cm_Quantity_On_Hand_CS_Inv"]=round(portfolio_global["cm_Quantity_On_Hand_CS_Inv"],5)
    portfolio_global["Open_PO_due_in_this_quarter"]=round(portfolio_global["Open_PO_due_in_this_quarter"],5)
    portfolio_global["Open_PO_due_in_next_quarter"]=round(portfolio_global["Open_PO_due_in_next_quarter"],5)
    portfolio_global["Delivery_Based_Total_OH_sum_OPO_this_quarter"]=round(portfolio_global["Delivery_Based_Total_OH_sum_OPO_this_quarter"],5)
    portfolio_global["PO_Based_Total_OH_sum_OPO"]=round(portfolio_global["PO_Based_Total_OH_sum_OPO"],5)
    portfolio_global["CQ_ARIS_FQ_sum_1_SANM_Demand"]=round(portfolio_global["CQ_ARIS_FQ_sum_1_SANM_Demand"],5)
    portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"]=round(portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"],5)
    portfolio_global["CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"]=round(portfolio_global["CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"],5)
    portfolio_global["CQ_sum_3_ARIS_FQ_SANM_Demand"]=round(portfolio_global["CQ_sum_3_ARIS_FQ_SANM_Demand"],5)
    portfolio_global["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"]=round(portfolio_global["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"],5)
    portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD"]=round(portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD"],5)
    portfolio_global["Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1"]=round(portfolio_global["Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1"],5)
    portfolio_global["Blended_AVG_PO_Receipt_Price"]=round(portfolio_global["Blended_AVG_PO_Receipt_Price"],5)
    portfolio_global["ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std"]=round(portfolio_global["ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std"],5)

    portfolio_global['sgd_jpe_cost']=portfolio_global.apply(lambda x:order(x.std_cost,x.file_from),axis=1)
    del portfolio_global['std_cost']
    del portfolio_global['file_from']
    # portfolio_global=portfolio_global.groupby('unique_field').sum()
    # portfolio_global.to_excel('portfolio_global.xlsx')
    portfolio_global.fillna(0,inplace=True)

    
    portfolio_global_final=portfolio_global_bak.merge(portfolio_global,on='unique_field')
    portfolio_global_final.drop_duplicates(subset=['unique_field'],inplace=True )
    portfolio_global_final.drop(['unique_field'],axis=1,inplace=True)
    portfolio_global_final['cm']='Global'
    portfolio_global_final['cm_Part_Number']=''
    # portfolio_global.to_excel('portfolio_global_final.xlsx')
    print(portfolio_global_final)

    
from itertools import count, product, islice

def multiletters(seq):
    for n in count(1):
        for s in product(seq, repeat=n):
            yield ''.join(s)


@register.simple_tag()
def get_portfolio_files(cm):
    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Portfolio_inputs')
    files_path=sorted(os.scandir(f'''{path}/{cm}'''), key=lambda t: t.stat().st_mtime)
    files=[[x.name,x.stat().st_size/1000] for x in files_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
    files.reverse()
    return files