from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
# Create your views here.
from django.http import HttpResponse, Http404
from portfolio.models import *
from django.http import JsonResponse,HttpResponse
from Slate_CMT.templatetags.cmt_helper import *
from email import encoders
from django.core.mail import EmailMessage
from django.core.mail import EmailMessage
from django.template.loader import get_template
import random
import string
import traceback
import sys
import os
from django.conf import settings
import pandas as pd
from django.db.models import Q, F, FloatField, ExpressionWrapper, Sum
import numpy as np
# from rfx.views import create_rfx
from io import BytesIO
from django.core.files.storage import FileSystemStorage
import os,shutil
from InputDB.models import *
# from excel_processor.portfolio import *
# from CMT.models import *
from rfx.models import *
from dateutil.parser import parse
from django.utils.dateparse import parse_date
import traceback
import sys
from django.db.models import Count, Sum, F, FloatField
import logging
import json
from django.db.models import Value as V
from django.db.models.functions import Concat   
from Supplier.models import *
from email.mime.base import MIMEBase


LOGGER = logging.getLogger(__name__)

def user_names():
    '''This will send all the username from GSM and CMM team as tuple(t1,t2)'''
    f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
    gsm_Team=[f'''{f_name[x]} {l_name[x]}''' for x in range(len(f_name)) ]
    l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
    f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
    cmm_team=[f'''{f_name[x]} {l_name[x]}''' for x in range(len(f_name)) ]
    cmm_team.sort()
    gsm_Team.sort()
    return (gsm_Team,cmm_team)


@login_required
def top_component(request,team=None):
    '''
    Type:Static Function
    Arg:request,Team
    ####process#####:
    This will return main page for top component bases on the team
    '''
    if team=='GSM' and (request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user in User.objects.filter(groups=Group.objects.get(name='Super User')) or request.user.is_superuser or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor'))):
        try:
            SGE_ss_team_headers_demand=eval(SGD_JBE_component_ss_team.objects.filter(Contract_Mfr='Sanmina').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            SGE_ss_team_headers_std=eval(SGD_JBE_component_ss_team.objects.filter(Contract_Mfr='Sanmina').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            JPE_ss_team_headers_demand=eval(SGD_JBE_component_ss_team.objects.filter(Contract_Mfr='Jabil').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            JPE_ss_team_headers_std=eval(SGD_JBE_component_ss_team.objects.filter(Contract_Mfr='Jabil').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            if has_permission(request.user,'Super User') or request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or request.user.is_superuser  or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor')):
                user=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
            else:
                user=User.objects.filter(username=request.user.username).values_list('first_name',flat=True)
        except Exception as e:
            #print(e)
            SGE_ss_team_headers_demand=None
            SGE_ss_team_headers_std=None
            JPE_ss_team_headers_demand=None
            JPE_ss_team_headers_std=None
        return render(request,"portfolio/top_component.html",
        context={
        'SGE_ss_team_headers_demand':SGE_ss_team_headers_demand,
        'SGE_ss_team_headers_std':SGE_ss_team_headers_std,
        'JPE_ss_team_headers_demand':JPE_ss_team_headers_demand,
        'JPE_ss_team_headers_std':JPE_ss_team_headers_std,
        'users':user,
        'quarter':Current_quarter(),
        })
    elif team=='CMM' and (request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or request.user in User.objects.filter(groups=Group.objects.get(name='CMM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser or request.user in User.objects.filter(groups=Group.objects.get(name='Super User')) or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor'))):
        try:
            SGE_cmm_team_headers_demand=eval(SGD_JBE_component_cmm_team.objects.filter(Contract_Mfr='Sanmina').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            SGE_cmm_team_headers_std=eval(SGD_JBE_component_cmm_team.objects.filter(Contract_Mfr='Sanmina').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            JPE_cmm_team_headers_demand=eval(SGD_JBE_component_cmm_team.objects.filter(Contract_Mfr='Jabil').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            JPE_cmm_team_headers_std=eval(SGD_JBE_component_cmm_team.objects.filter(Contract_Mfr='Jabil').values_list('quarter_demand_mapper',flat=True).distinct()[0])
            if has_permission(request.user,'Super User')  or request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or request.user.is_superuser or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor')):
                user=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
            else:
                user=User.objects.filter(username=request.user.username).values_list('first_name',flat=True)
        except :
            SGE_cmm_team_headers_demand=None
            SGE_cmm_team_headers_std=None
            JPE_cmm_team_headers_demand=None
            JPE_cmm_team_headers_std=None
        return render(request,"portfolio/top_component_cmm.html",
        context={
        'SGE_cmm_team_headers_demand':SGE_cmm_team_headers_demand,
        'SGE_cmm_team_headers_std':SGE_cmm_team_headers_std,
        'JPE_cmm_team_headers_demand':JPE_cmm_team_headers_demand,
        'JPE_cmm_team_headers_std':JPE_cmm_team_headers_std,
        'quarter':Current_quarter(),
        'users':user
        }
    )
    else :
        return redirect('/')

@login_required
def refreshed_top_component(request,team=None):
    '''
    Type:Static Function
    Arg:request,Team
    ####process#####:
    This will return main page for top component bases on the team
    '''
    if team=='GSM' and has_permission(request.user,'CMM'):

        if request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or request.user.is_superuser:
            user=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
        else:
            user=User.objects.filter(username=request.user.username).values_list('first_name',flat=True)

        return render(request,"portfolio/refreshed_top_component.html",
        context={
        'Team':'GSM',
        'users':user,
        'quarter':Current_quarter(),
        })
    elif team=='CMM' and has_permission(request.user,'CMM'):

        if request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or request.user.is_superuser:
            user=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
        else:
            user=User.objects.filter(username=request.user.username).values_list('first_name',flat=True)


        return render(request,"portfolio/refreshed_top_component.html",
        context={
        'Team':'CMM',
        'quarter':Current_quarter(),
        'users':user
        }
    )
    else :
        return redirect('/')

@login_required
def portfolio(request,team):

    print('team',team)
    '''
    Type:Static Function
    Arg:request,Team
    ####process#####:
    This function is as dynamic function which return value based on the team and option field
    # team =='GSM':
        this will return portfolio page for GSM Team
    # team =='CMM':
        this will return portfolio page for CMM Team
    # team =='CMM_Supplier':
        this will return portfolio page for CMM_Supplier
    #option=='check_box':
        this will check and uncheck the checkbox based the id and state Received in GET('state','id') in session(Check_box_portfolio)
    #option=='comment':
        to update the comment field in portfolio row
    #option=='PIC_Comment_download':
        this will return a excel file with their all parts assigned to them(request.user) with the columns 'Number','cm','Arista_PIC','Arista_pic_comment
    #elif option=='PIC_Comment_upload':
        this will get a excel file with their all parts assigned to them(request.user) with the columns 'Number','cm','Arista_PIC','Arista_pic_comment
         and save them based on the id to portfolio table with the updated value(above format will be the template).
    elif option=='portfolio_field_editable':
        1.field=='Arista_PIC':
                This will get a pic name with respect to portfolio id
                from request and Change the name for all apn also assign the team based on the New PIC name
        2.else:change the value based the field which will be on GET based on the id
            request.GET.get('value'),request.GET.get('field')
    elif option=='delete_portfolio':
        This will delete the portfolio row based on the APN,cm,quarter (fetched from portfolio id) and call the create_global.
    *basic logics, Roles and permission are self explanatory
    *column_names_portfolio this is used as dictionary for decoding and encoding headers
    '''

    if team =='GSM':
        request.session['Check_box_portfolio']=[]
        try:
            columns_name=eval(helper_Portfolio.objects.filter(table_name='Portfolio')[0].column_mapper)
        except:
            columns_name={}
            LOGGER.error("LOG_MESSAGE", exc_info=1)
        Portfolio.objects.filter(Quarter='deleted').delete()
        past_quarter=Portfolio.objects.exclude(Quarter=Current_quarter()).distinct('Quarter').values_list('Quarter',flat=True)
        cms=['FGN','SGD','JMX','JSJ']
        return render(request,'portfolio/portfolio.html',context={"columns_name":columns_name,'past_quarter':past_quarter,'cms':cms})
    elif team =='CMM':
        Portfolio.objects.filter(Quarter='deleted').delete()
        Page_title='Portfolio Contract Manufacture'
        request.session['Check_box_portfolio']=[]
        try:
            columns_name=eval(helper_Portfolio.objects.filter(table_name='Portfolio')[0].column_mapper)
        except:
            columns_name={}
            LOGGER.error("LOG_MESSAGE", exc_info=1)
        past_quarter=Portfolio.objects.exclude(Quarter=Current_quarter()).distinct('Quarter').values_list('Quarter',flat=True) 
        return render(request,'portfolio/portfolio_CMM.html',context={"columns_name":columns_name,"Page_title":Page_title,'past_quarter':past_quarter})
    elif team =='CMM_Supplier':
        Portfolio.objects.filter(Quarter='deleted').delete()
        Page_title='CMM Portfolio'
        request.session['Check_box_portfolio']=[]
        past_quarter=Portfolio.objects.exclude(Quarter=Current_quarter()).distinct('Quarter').values_list('Quarter',flat=True) 
        try:
            columns_name=eval(helper_Portfolio.objects.filter(table_name='Portfolio')[0].column_mapper)
        except:
            columns_name={}
            LOGGER.error("LOG_MESSAGE", exc_info=1)

            
        return render(request,'portfolio/portfolio_CMM.html',context={"columns_name":columns_name,'Page_title':Page_title,'past_quarter':past_quarter})
    else:
        option=request.GET.get('option')
        #print(option)
        if option=='check_box':
            data = []
            try:
                #check_box=request.session['Check_box_portfolio']
                if 'Check_box_portfolio' not in request.session:
                    check_box=[]
                else :
                    check_box=request.session['Check_box_portfolio']
            except:
                request.session['Check_box_portfolio']=[]
                check_box=[]
                LOGGER.error("LOG_MESSAGE", exc_info=1)
                

            #print(request.GET['State'])
            if request.GET['State'] == 'true':
                check_box.append(int(request.GET['id']))

            elif request.GET['State'] == 'false':
                check_box.remove(int(request.GET['id']))
                #print(check_box)

            else:
                pass
            # check_box=list(Portfolio.objects.filter(id__in=check_box,rfq_sent_flag_supplier__icontains='Not Raised').values_list('id',flat=True))
            request.session['Check_box_portfolio']=check_box
            request.session.modified = True
            return JsonResponse({'status':200,'selected':len(request.session['Check_box_portfolio'])},safe=False)
        elif option=='comment':
            #print(request.GET)
            data=Portfolio.objects.get(id=request.GET.get('id'))
            data.Arista_pic_comment=request.GET.get('value')
            data.save()
            return JsonResponse({'status':200,'message':'Done'},safe=False)
        elif option=='PIC_Comment_download':
            team_name=request.GET.get('Team')

            if team_name=='CMM Team' and request.user in User.objects.filter(groups=Group.objects.get(name='CMM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager'))  :
                data=Portfolio.objects.filter(Team='CMM Team',Quarter=Current_quarter()).filter(Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')
                df=data.exclude(cm='Global').values('Number','cm','Arista_PIC','Arista_pic_comment').distinct('Number','cm').to_dataframe()

            elif team_name=='GSM Team' and request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager'))  :
                data=Portfolio.objects.filter(Team='GSM Team',Quarter=Current_quarter()).filter(Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')
                df=data.values('Number','cm','Arista_PIC','Arista_pic_comment').distinct('Number','cm').to_dataframe()        

            elif team_name=='CMM Team' and ( has_permission(request.user,'Super User') or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser):
                f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
                l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
                team_member_list=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
                data=Portfolio.objects.filter(Team='CMM Team',Quarter=Current_quarter())
                df=data.exclude(cm='Global').values('Number','cm','Arista_PIC','Arista_pic_comment').distinct('Number','cm').to_dataframe()

            elif team_name=='GSM Team' and ( has_permission(request.user,'Super User') or  request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser):
                f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
                l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
                team_member_list=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
                data=Portfolio.objects.filter(Team="GSM Team",Quarter=Current_quarter())
                df=data.values('Number','cm','Arista_PIC','Arista_pic_comment').distinct('Number','cm').to_dataframe()

            # fields={k:v for k,v in column_names_portfolio.items()}
            df.rename(columns=column_names_portfolio,inplace=True)
            with BytesIO() as b:
                with pd.ExcelWriter(b) as writer:
                    df.to_excel(writer,index=False,sheet_name=f'PIC Comments')
                    writer.save()
                    response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = f'inline; filename=PIC Comments Upload.xlsx'
                    return response
        elif option=='PIC_Comment_upload':

            Team=request.GET.get('Team')
            team_name=request.GET.get('Team')
            if team_name=='CMM Team' and request.user in User.objects.filter(groups=Group.objects.get(name='CMM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager'))  :
                data=Portfolio.objects.filter(Team='CMM Team',Quarter=Current_quarter()).filter(Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')


            elif team_name=='GSM Team' and request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager'))  :
                data=Portfolio.objects.filter(Team='GSM Team',Quarter=Current_quarter()).filter(Arista_PIC__icontains=f'{request.user.first_name} {request.user.last_name}')


            elif team_name=='CMM Team' and ( has_permission(request.user,'Super User') or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser):
                f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
                l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
                team_member_list=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
                data=Portfolio.objects.filter(Team='CMM Team',Quarter=Current_quarter())


            elif team_name=='GSM Team' and ( has_permission(request.user,'Super User') or  request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser):
                f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
                l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
                team_member_list=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
                data=Portfolio.objects.filter(Team="GSM Team",Quarter=Current_quarter())




            xlx=request.FILES['Upload_Excel']
            df=pd.read_excel(xlx)
            fields={v:k for k,v in column_names_portfolio.items()}
            df.rename(columns=fields,inplace=True)
            df.dropna(inplace=True)
            df=df.replace({np.nan: None})
            q=data
            for index,row in df.iterrows():
                q.filter(Number__icontains=row['Number'],cm__icontains=row['cm']).update(Arista_pic_comment=row['Arista_pic_comment'])

            return JsonResponse({'message':'Comments Updated','status':200})
        elif option=='portfolio_field_editable':
            #print(request.GET)
            value=request.GET.get('value')
            field=request.GET.get('field')
            data=Portfolio.objects.get(id=request.GET.get('id'))
            datas=Portfolio.objects.filter(Quarter=data.Quarter,
                                    Number=data.Number,
                                    cm=data.cm,
            )
            datas_in_both=Portfolio.objects.filter(Quarter=data.Quarter,
                                    Number=data.Number,
                                    cm__in=['SGD','JPE','FGN','HBG','JSJ','JMX']
            )
            if field=='Arista_PIC':
                try:
                    
                    if value.isdigit():
                        user=User.objects.get(id=value)
                        value=f"{user.first_name} {user.last_name}"
                        datas.update(**{field:value})
                        check_global=datas_in_both.exclude(Arista_PIC=value).distinct('Arista_PIC').values_list('Arista_PIC',flat=True)
                        if not check_global.exists():
                            Portfolio.objects.filter(Quarter=data.Quarter,
                            Number=data.Number,cm='Global').update(Arista_PIC=value)

                        #print(data.Team)
                        #print(user.groups.values_list('name',flat=True))
                        if not (data.Team in user.groups.values_list('name',flat=True) or f"{data.Team.split(' ')[0]} Manager" in  user.groups.values_list('name',flat=True)):
                            #print('Changed team')
                            team_decision="CMM Team" if data.Team=='GSM Team' else "GSM Team"
                            if team_decision=="CMM Team":
                                dd=Portfolio.objects.filter(Quarter=data.Quarter,
                                                        Number=data.Number,
                                                        
                                                        
                                                        )
                                ids=list(dd.values_list('id',flat=True))
                                Portfolio.objects.filter(id__in=ids).update(Quarter='deleted')
                                for x in Portfolio.objects.filter(id__in=ids):
                                    create_global(request,x,False)
                                Portfolio.objects.filter(id__in=ids).update(Quarter=Current_quarter())

                                dd.update(**{'Team':team_decision,field:value})
                                for x in Portfolio.objects.filter(id__in=ids):
                                    create_global(request,x,False)
                            elif team_decision=="GSM Team":
                                dd=Portfolio.objects.filter(Quarter=data.Quarter,
                                                        Number=data.Number,
                                                        
                                                        )
                                ids=list(dd.values_list('id',flat=True))
                                Portfolio.objects.filter(id__in=ids).update(Quarter='deleted')
                                for x in Portfolio.objects.filter(id__in=ids):
                                    create_global(request,x,False)
                                Portfolio.objects.filter(id__in=ids).update(Quarter=Current_quarter())

                                dd.update(**{'Team':team_decision,field:value})
                                for x in Portfolio.objects.filter(id__in=ids):
                                    create_global(request,x,False)
                            #print(datas.values('Team'))
                            
                            global_portfolio=Portfolio.objects.filter(Quarter=data.Quarter,
                                    Number=data.Number,
                                    cm='Global',
                                    
                                    )
                            RFX.objects.filter(portfolio__in=global_portfolio).delete()
                            data=RFX.objects.filter(portfolio__in=datas)
                            data.delete()
                            ids=list(datas.exclude(cm='Global').filter(Team='CMM Team').values_list('id',flat=True))
                            for x in Portfolio.objects.filter(id__in=ids):
                                create_global(request,x,False)
                            create_rfx(request,parts=ids,To=['cm'],created_by=None,Arista_pic_comment='')
                        else:
                            if data.Team=='GSM Team':
                                datas=Portfolio.objects.filter(
                                                        Quarter=data.Quarter,
                                                        Number=data.Number,
                                                        cm=data.cm,
                                                        )
                                datas.update(**{field:value})
                    else:
                        datas.update(**{field:value})
                        try:value=value.split('/')[0]
                        except:value=value
                        #print(value)
                        user=User.objects.filter(first_name__icontains=value.split(' ')[0])[0]
                        #print(user)
                        #print(user.groups.values_list('name',flat=True))
                        if not (data.Team in user.groups.values_list('name',flat=True) or f"{data.Team.split(' ')[0]} Manager" in  user.groups.values_list('name',flat=True)):
                            #print('Changed team')

                            datas.update(Team="CMM Team"if data.Team=='GSM Team' else "GSM Team")
                            #print(datas.values('Team'))
                            global_portfolio=Portfolio.objects.filter(Quarter=data.Quarter,
                                    Number=data.Number,
                                    cm='Global',
                                    
                                    )
                            RFX.objects.filter(portfolio__in=global_portfolio).delete()
                            data=RFX.objects.filter(portfolio__in=datas)
                            data.delete()
                            ids=list(datas.exclude(cm='Global').filter(Team='CMM Team').values_list('id',flat=True))
                            for x in Portfolio.objects.filter(id__in=ids):
                                create_global(request,x,False)
                            create_rfx(request,parts=ids,To=['cm'],created_by=None,Arista_pic_comment='')
                        # datas.update(**{field:value})

                except Exception as e:
                    send_logger_tele(e)
                    LOGGER.error("LOG_MESSAGE", exc_info=1)
                    
            else:
                ids=list(datas.values_list('id',flat=True))
                Portfolio.objects.filter(id__in=ids).update(Quarter='deleted')
                for x in Portfolio.objects.filter(id__in=ids):
                    create_global(request,x,False)
                Portfolio.objects.filter(id__in=ids).update(Quarter=Current_quarter())
                Portfolio.objects.filter(id__in=ids).update(**{field:value})
                for x in Portfolio.objects.filter(id__in=ids):
                    create_global(request,x,False)

            return JsonResponse({'status':200,'message':'Done'},safe=False)
        elif option=='delete_portfolio':
            from MasterPricing.models import MP_download_table,master_temp
            logic_BP,created = master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
            unlock=not logic_BP.lift_logic=='enable'
            id=request.GET.get('id')
            data=Portfolio.objects.get(id=id)
            if not has_group(request.user,'BP Team,Admin'):
                return JsonResponse({'status':400,'message':f'Sorry,You have no permission to delete.'},safe=False)
            if not unlock:
                return JsonResponse({'status':400,'message':f'Please unlock the Master Pricing Page to delete'},safe=False)
            if data.cm=='Global':
                return JsonResponse({'status':400,'message':f'Please delete only in Regional tab.'},safe=False)
            if request.GET.get('mpn_delete'):
                datas=Portfolio.objects.filter(id=data.id)
            else:
                datas=Portfolio.objects.filter(Team=data.Team).filter(Quarter=data.Quarter,cm=data.cm,Arista_Part_Number=data.Arista_Part_Number)
            rfq=RFX.objects.filter(portfolio__in = datas)
            count=rfq.delete()
            datas_list=list(datas)
            datas.delete()
            inst=delete_log(
                Arista_Part_Number=data.Arista_Part_Number,
                Quarter=data.Quarter,
                cm=data.cm,
                Number=data.Number,
                Mfr_Name=None,
                Mfr_Part_Number=None,
                user=request.user,
            )
            inst.save()
            for data in datas_list:
                create_global(request,data,False)
                
            LOGGER.info("Portfolio Part - " + data.Arista_Part_Number + ' Deleted By ' + request.user.first_name + ' ' + request.user.last_name)
            mp=MP_download_table.objects.filter(Quarter=Current_quarter(),Part_Number=data.Arista_Part_Number,CM_download=data.cm).delete()
            return JsonResponse({'status':200,'message':f'Part Number has been removed from the system ,{count[0]} RFQ(s) removed and {mp[0]} Master Pricing line removed'},safe=False)


###Download Section
@login_required
def send_download_response(request,path=''):
    '''
    Type:Static Function
    Arg:request,path
    ####process#####:
    This is as basic file sever api, this will send the file from the path based on the 'path' argument.
    '''
    file_path = os.path.join(settings.BASE_DIR, path)
    #print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    response = HttpResponse()
    response.status_code = 404
    return response


@login_required
@login_required
def excel_filter(request):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    As request.method=="POST":
        This will get the file from request.FILES['Upload_Excel'] decode the file header with column_names_portfolio
        create a dict from the giving excel file and pass the dict as Q filter and get the values as id and 
        Store ids as list to the session named filter_excel_portfolio
    '''
    if request.method=="POST":
        model=Portfolio
        xlx=request.FILES['Upload_Excel']
        df=pd.read_excel(xlx)
        df=df.replace({pd.np.nan: None})
        column_names_decode={v:k for k,v in column_names_portfolio.items()}
        df.rename(columns=column_names_decode,inplace=True)

        concat_list = []
        for column in df.columns:
            concat_list.append(column)
            concat_list.append(V('####'))
        concat_list.pop(-1)

        df['search'] = df[df.columns].apply(lambda x: '####'.join(x), axis=1)
        #print(df['search'])
        qs = Portfolio.objects.annotate(search=Concat(*concat_list)).filter(
            search__in=df['search']).values_list('id',flat=True)
        request.session['filter_excel_portfolio']=list(qs)
        request.session.modified= True
        return HttpResponse('Success')
    else:
        return HttpResponse('not allowed')

@login_required
def advance_filter(request,Team,section,field):
    '''
    Type:Static Function
    Arg:request,Team,section,field
    ####process#####:
    #section=='get_value'
        return list of data of the given field from their session['current_filtered_portfolio] only for the field in argument
    #section=='filter_form' and field=='all_data':
        this will create a dict which can be passed in to django orm filter based on the Post data from the form
        and save the result id to  session['current_filtered_portfolio]
    #
    

    '''
    if section=='get_value':
        id=request.session['current_filtered_portfolio']
        q=Portfolio.objects.filter(id__in=id)
        #print(q)
        data=q.exclude(**{f"{field}__isnull":True}).values_list(field,flat=True).distinct()
        return JsonResponse(list(data),safe=False)
    if section=='filter_form' and field=='all_data':
        data=request.POST
        #print(data)
        fields=data.getlist('fields[]')
        q = Q()
        for x in fields:
            if data.get('type')=='or':
                q |=Q(**{f'{x}__in':data.getlist(f'{x}_value[]') })
            else:
                q &=Q(**{f'{x}__in':data.getlist(f'{x}_value[]') })
        qs = Portfolio.objects.filter(q).values_list('id',flat=True)
        request.session['advance_filter_portfolio']=list(qs)
        request.session.modified= True
        #print(request.session['advance_filter_portfolio'])
        return HttpResponse(request,len(qs))

column_names_portfolio={
        "cm":"Global/Regional",
        "cm_Part_Number":"CM Part Number",
        "Arista_Part_Number":"Arista Part Number",
        "Item_Desc":"Item Description",
        "Ownership":"Ownership",
        "Arista_PIC":"Arista PIC",
        'commodity':'Commodity Name',
        "Lifecycle_Phase":"Arista Lifecycle phase",
        "Rev":"Revision",
        "Mfr_Name":"Manufacturer Name",
        "Mfr_Part_Lifecycle_Phase":"Manufacturer Lifecycle phase",
        "Mfr_Part_Number":"Manufacturer Part Number",
        "Qualification_Status":"Arista Qualification status",
        "Cust_consign":"Cust Consigned",
        "Original_PO_Delivery_sent_by_Mexico":"PO / Delivery",
        "cm_Quantity_Buffer_On_Hand":"CM Quantity Buffer On Hand",
        "cm_Quantity_On_Hand_CS_Inv":"CM Quantity On Hand + CS Inv",
        "Quarter":"Current Quarter",
        "Open_PO_due_in_this_quarter":"Open PO Due (Current Quarter)",
        "Open_PO_due_in_next_quarter":"Open PO Due (Q+1)",
        "Delivery_Based_Total_OH_sum_OPO_this_quarter":"CM Total OH + OPO (Current Quarter)",
        "PO_Based_Total_OH_sum_OPO":"CM Total OH + OPO (Q & Q+1)",
        "CQ_ARIS_FQ_sum_1_SANM_Demand":"Current Quarter Demand",
        "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":"Q+1 Demand",
        "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand":"Q+2 Demand",
        "CQ_sum_3_ARIS_FQ_SANM_Demand":"Q+3 Demand",
        "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista":"Delta = OH and OPO - DD",
        # "ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std":"Current Quarter Std cost($)",
        "sgd_jpe_cost":"Current Qtr Std Cost (SGD / JPE / FGN / HBG / JSJ / JMX) $",
        "Blended_AVG_PO_Receipt_Price":"Sanmina Blended Avg PO Receipt Price ($)",
        "Team":"Team",
        'Arista_pic_comment':'Arista PIC comment to Suppliers',
        "Parts_controlled_by":"Parts Controlled by",
        "rfq_sent_flag_supplier":"RFQ Sent Status",
    }
@login_required
def download_portfolio(request,file='',mail=False):
    '''
    Type:Static Function
    Arg:request,date(o),Contract Manufacturer location
    ####process#####:
    1.This will return all data from portfolio as excel based on the request.user based on the file and permission
    2.elif file =='filtered_portfolio':
        This will return the excel file of portfolio which is filtered from session['current_filtered_portfolio'] id(s).
    3.Other files:
        This will return based on the team and permission
            portfolio_CMM=CMM_Team
            portfolio_SS=GSM_Team
        
    '''
    Quarter=request.GET.get('Quarter',Current_quarter())
    fields=[k for k,v in column_names_portfolio.items()]
    alias=[v for k,v in column_names_portfolio.items()]
    # alias=["Global/Regional","CM Part Number","Arista Part Number","Item Description","Ownership","Arista PIC",'Commodity Name',"Arista Lifecycle phase","Revision","Manufacturer Name","Manufacturer Lifecycle phase","Manufacturer Part Number","Arista Qualification status","Cust Consigned","PO / Delivery","CM Quantity Buffer On Hand","CM Quantity On Hand + CS Inv","Current Quarter","Open PO Due (Current Quarter)","Open PO Due  (Q+1)","Total OH + OPO (Current Quarter)","Total OH +OPO  (Q+1)", "Current Quarter Demand", "Q+1 Demand", "Q+2 Demand", "Q+3 Demand", "Delta = OH and OPO - DD", "Current Quarter Std cost","Sanmina Blended Avg PO Receipt Price ($)","Team",'Arista PIC comment to Suppliers',"Parts Controlled by","RFQ sent to suppliers", "RFQ sent to CM", "RFQ sent to Distributor"]
    if file =='SS_Report' and has_permission(request.user,'GSM'):
        return send_download_response(request,path=f"Reports/{get_Next_quarter()[0]} Sourcing Team Global demand.xlsx")
    elif file =='CMM_Report' and has_permission(request.user,'CMM'):
        return send_download_response(request,path=f"Reports/{get_Next_quarter()[0]} Operational Team Global demand.xlsx")

    elif file =='filtered_portfolio':
        df=Portfolio.objects.filter(id__in=request.session['current_filtered_portfolio']).values(*fields).order_by('Number').to_dataframe()
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.to_excel(writer,index=False,header=alias,columns=fields,sheet_name=f'{get_Next_quarter()[0]} Portfolio (filtered)')
                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename={get_Next_quarter()[0]} Portfolio Filtered.xlsx'
                return response

    elif file=='portfolio_CMM' and (has_permission(request.user,'CMM') or has_permission(request.user,'BP Team')):

        df=Portfolio.objects.filter(Quarter=Quarter).filter(Team='CMM Team').exclude(cm='Global').order_by('Number').values(*fields).to_dataframe()
        # df.drop(['Number','LT','MOQ','CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD','Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1','bp_comment'],axis=1,inplace=True)

        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.to_excel(writer,index=False,header=alias,columns=fields)
                writer.save()
                if mail:
                    return b.getvalue(),f'{get_Next_quarter()[0]} Portfolio  CMM Team.xlsx'
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename={get_Next_quarter()[0]} Portfolio  CMM Team.xlsx'
                return response

    elif file=='portfolio_SS' and (has_permission(request.user,'GSM') or has_permission(request.user,'BP Team') ):
        df=Portfolio.objects.filter(Quarter=Quarter).filter(Team='GSM Team').order_by('Number').values(*fields).to_dataframe()
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.to_excel(writer,index=False,header=alias,columns=fields)
                writer.save()
                if mail:
                    return b.getvalue(),f'{get_Next_quarter()[0]} Portfolio  GSM Team.xlsx'
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename={get_Next_quarter()[0]} Portfolio  GSM Team.xlsx'
                return response
    else:
        raise Http404


@login_required
def send_rfx_input(request):
    '''
    Type:Function
    Arg:request
    ####process#####:
    1.POST:
        This will receive the parts id(from session['Check_box_portfolio'] or  ) here we need to validate the parts is really their part based on the pic name and send them list of parts
        to create_rfx func.
    else:
        returns the selected part count, supplier not exists and the disabled supplier for the selected parts
        
    '''
    if request.method=='POST':
        #print('request.POST')
        To=request.POST.getlist('To')
        
        Quote_Type=request.POST.get('Quote_Type')
        notification=True if request.POST.get('notification') else False
        if request.user.is_superuser:
            
            current_part=list(Portfolio.objects.exclude(rfq_sent_flag_supplier='Quote Raised').filter(id__in=request.session['current_filtered_portfolio']).values_list('id',flat=True))

        else:
            current_part=list(Portfolio.objects.exclude(rfq_sent_flag_supplier='Quote Raised').filter(id__in=request.session['current_filtered_portfolio'],Arista_PIC__icontains=f"{request.user.first_name} {request.user.last_name}").values_list('id',flat=True))

        selected_part=request.session['Check_box_portfolio']
        selected_part=current_part if selected_part==[] else selected_part
        this_quarter=request.POST.get('this_quarter')
        next_quarter=request.POST.get('next_quarter')
        this=True if this_quarter =='True' else False
        if this_quarter and next_quarter:
            this=get_Next_quarter(1,this_quarter=True)
        elif this_quarter:
            this=[Current_quarter()]
        else:
            this=get_Next_quarter(1)
        #print(request.POST)
        create_rfx(request,parts=selected_part,To=To,created_by=request.user,Quote_Type=Quote_Type,Arista_pic_comment='No comments yet' if request.POST.get('Arista_pic_comment')=='' else request.POST.get('Arista_pic_comment'),this=this,notification=notification )
        request.session['Check_box_portfolio']=[]
       
        return JsonResponse({'message':'RFQ process is in Queue. We will inform you through email once it is completed','Quote_Type':Quote_Type,'to':To,'count':len(selected_part)})


    else:
        selected_part=len(request.session.get('Check_box_portfolio',[]))
        Team=request.GET.get('Team')
        #print(Team)
        if request.user.is_superuser:
            current_part=Portfolio.objects.exclude(rfq_sent_flag_supplier='Quote Raised').filter(id__in=request.session.get('Check_box_portfolio') or check_rfx_global(request.session['current_filtered_portfolio']))
        else:
            current_part=Portfolio.objects.exclude(rfq_sent_flag_supplier='Quote Raised').filter(id__in=request.session.get('Check_box_portfolio') or check_rfx_global(request.session['current_filtered_portfolio']),Arista_PIC__icontains=f"{request.user.first_name} {request.user.last_name}")
        if request.user.is_superuser:
            user_owner=User.objects.annotate(full_name=Concat('first_name', V(' '),'last_name')).filter(full_name__in=current_part.values_list('Arista_PIC',flat=True))
            disabled_suppliers=suppliers_detail.objects.filter(Supplier_Name__in=current_part.values_list('Mfr_Name',flat=True)).filter(User_created__in=user_owner).filter(Q(user_model__is_active=False) | Q(is_active=False))
        else:
            disabled_suppliers=suppliers_detail.objects.filter(User_created=request.user,Supplier_Name__in=current_part.values_list('Mfr_Name',flat=True)).filter(Q(user_model__is_active=False) | Q(is_active=False))
        all_suppliers=list(current_part.distinct('Mfr_Name').values_list('Mfr_Name',flat=True))
        if request.user.is_superuser:
            suppliers_non_exists=[x for x in all_suppliers if not suppliers_detail.objects.filter(User_created__in=user_owner,Supplier_Name__icontains=x).count()]
        else:
            suppliers_non_exists=[x for x in all_suppliers if not suppliers_detail.objects.filter(User_created=request.user,Supplier_Name__icontains=x).count()]
        #print(suppliers_non_exists,"Test")
        json_disabled_suppliers=list(disabled_suppliers.values('Supplier_Name','Contact','Email'))
        selected_part=selected_part or current_part.count()

        return JsonResponse({'count':selected_part,'disabled_supplier':json_disabled_suppliers,'suppliers_non_exists':suppliers_non_exists})

@login_required
def offcycle(request,Team,option):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    this process is for loading portfolio parts but without agile data auto fetch here agile data is loaded in the excel it self
    same process as portfolio Creation
    if option=='excel_import':
        this will Load  the excel which has the partnumber 
    elif option=='download_template':
        To download the offcycle template
    
    

    '''
    column_names_portfolio_avl={
        "cm":"Global/Regional *",
        "cm_Part_Number":"CM Part Number *",
        "Arista_Part_Number":"Arista Part Number *",
        "Item_Desc":"Item Description",
        "Ownership":"Ownership *",
        "Arista_PIC":"Arista PIC *",
        'commodity':'Commodity Name',
        "Lifecycle_Phase":"Arista Lifecycle phase",
        "Rev":"Revision",
        "Mfr_Name":"Manufacturer Name *",
        "Mfr_Part_Lifecycle_Phase":"Manufacturer Lifecycle phase",
        "Mfr_Part_Number":"Manufacturer Part Number *",
        "Qualification_Status":"Arista Qualification status",
        "Cust_consign":"Cust Consigned *",
        "Original_PO_Delivery_sent_by_Mexico":"PO / Delivery",
        "cm_Quantity_Buffer_On_Hand":"CM Quantity Buffer On Hand",
        "cm_Quantity_On_Hand_CS_Inv":"CM Quantity On Hand + CS Inv",
        "Quarter":"Current Quarter",
        "Open_PO_due_in_this_quarter":"Open PO Due (Current Quarter)",
        "Open_PO_due_in_next_quarter":"Open PO Due  (Q+1)",
        "Delivery_Based_Total_OH_sum_OPO_this_quarter":"CM Total OH + OPO (Current Quarter)",
        "PO_Based_Total_OH_sum_OPO":"CM Total OH + OPO(Q & Q+1)",
        "CQ_ARIS_FQ_sum_1_SANM_Demand":"Current Quarter Demand",
        "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":"Q+1 Demand",
        "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand":"Q+2 Demand",
        "CQ_sum_3_ARIS_FQ_SANM_Demand":"Q+3 Demand",
        "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista":"Delta = OH and OPO - DD",
        "sgd_jpe_cost":"Current Qtr Std Cost (SGD / JPE / FGN / HBG / JSJ / JMX) $",
        "Blended_AVG_PO_Receipt_Price":"Sanmina Blended Avg PO Receipt Price ($)",
        "Team":"Team",
        'Arista_pic_comment':'Arista PIC comment to Suppliers',
        "Parts_controlled_by":"Parts Controlled by*",
        "rfq_sent_flag_supplier":"RFQ sent to suppliers",
        "rfq_sent_flag_cm":"RFQ sent to CM",
        "rfq_sent_flag_distributor":"RFQ sent to Distributor",
        "rfq_sent_flag_distributor":"RFQ sent to Distributor",
        "bp_comment":'BP Comments',
        "CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD":'Current Qtr +1 std cost ($)',
        "Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1":"Delta std cost ($)",
    }
    if option=='excel_import':
        
        error_index=[]
        error=False
        data=request.FILES['excel_file']
        df=pd.read_excel(data)
        column_names_decode={v:k for k,v in column_names_portfolio_avl.items()}
        df.rename(columns=column_names_decode,inplace=True)
        df=df.replace({np.nan: None})
        created=[]
        
        pic_list = []
        
        for index, row in df.iterrows():

            if User.objects.filter(groups__name__icontains='GSM').annotate(full_name=Concat('first_name', V(' '),'last_name')).filter(full_name__icontains=row['Arista_PIC'].split('/')[0]).exists():
                Team='GSM Team'
            elif User.objects.filter(groups__name__icontains='CMM').annotate(full_name=Concat('first_name', V(' '),'last_name')).filter(full_name__icontains=row['Arista_PIC'].split('/')[0]).exists():
                Team='CMM Team'
            else:
                error=True
                error_index.append(index)
            datas=Portfolio.objects.filter(Team=Team).filter(Quarter=Current_quarter(),Arista_Part_Number=row['Arista_Part_Number'],Mfr_Name=row['Mfr_Name'],cm=row['cm'])
            if datas.exists() and error:
                error_index.append(index)
                
            elif datas.exists():
                datas.update(
                    Mfr_Part_Lifecycle_Phase=row['Mfr_Part_Lifecycle_Phase'],
                    Mfr_Part_Number=row['Mfr_Part_Number'],
                    Qualification_Status=row['Qualification_Status'],
                    Cust_consign=row['Cust_consign'],
                    Item_Desc=row['Item_Desc'],
                    LT=row['LT'],
                    MOQ=row['MOQ'],
                    Original_PO_Delivery_sent_by_Mexico=row['Original_PO_Delivery_sent_by_Mexico'],
                    cm_Quantity_Buffer_On_Hand=row['cm_Quantity_Buffer_On_Hand'],
                    cm_Quantity_On_Hand_CS_Inv=row['cm_Quantity_On_Hand_CS_Inv'],
                    Open_PO_due_in_this_quarter=row['Open_PO_due_in_this_quarter'],
                    Open_PO_due_in_next_quarter=row['Open_PO_due_in_next_quarter'],
                    Delivery_Based_Total_OH_sum_OPO_this_quarter=row['Delivery_Based_Total_OH_sum_OPO_this_quarter'],
                    PO_Based_Total_OH_sum_OPO=row['PO_Based_Total_OH_sum_OPO'],
                    CQ_ARIS_FQ_sum_1_SANM_Demand=row['CQ_ARIS_FQ_sum_1_SANM_Demand'],
                    CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand=row['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'],
                    CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand=row['CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand'],
                    CQ_sum_3_ARIS_FQ_SANM_Demand=row['CQ_sum_3_ARIS_FQ_SANM_Demand'],
                    Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista=row['Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista'],
                    ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std=row['sgd_jpe_cost'],
                    sgd_jpe_cost=f"{row['sgd_jpe_cost']}/-".replace('None','-') if row['cm']=='SGD' else f"-/{row['sgd_jpe_cost']}".replace('None','-') ,
                    CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD=row['CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD'],
                    Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1=row['Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1'],
                    Blended_AVG_PO_Receipt_Price=row['Blended_AVG_PO_Receipt_Price'],
                    bp_comment=row['bp_comment'],
                    file_from=row['cm'],

                )
                #print('Updated with new values')
                create_global(request,datas[0])

            else:
                #print('############################',row['Arista_Part_Number'])
                data=Portfolio(
                    cm_Part_Number=row['cm_Part_Number'],
                    Arista_Part_Number=row['Arista_Part_Number'],
                    Number=row['Arista_Part_Number'],
                    Quarter=Current_quarter(),
                    cm=row['cm'],
                    Ownership=row['Ownership'],
                    Arista_PIC=row['Arista_PIC'],
                    Parts_controlled_by=row['Parts_controlled_by'],
                    Lifecycle_Phase=row['Lifecycle_Phase'],
                    Rev=row['Rev'],
                    Mfr_Name=row['Mfr_Name'],
                    Mfr_Part_Lifecycle_Phase=row['Mfr_Part_Lifecycle_Phase'],
                    Mfr_Part_Number=row['Mfr_Part_Number'],
                    Qualification_Status=row['Qualification_Status'],
                    Cust_consign=row['Cust_consign'],
                    Item_Desc=row['Item_Desc'],
                    LT=row['LT'],
                    MOQ=row['MOQ'],
                    Original_PO_Delivery_sent_by_Mexico=row['Original_PO_Delivery_sent_by_Mexico'],
                    cm_Quantity_Buffer_On_Hand=row['cm_Quantity_Buffer_On_Hand'],
                    cm_Quantity_On_Hand_CS_Inv=row['cm_Quantity_On_Hand_CS_Inv'],
                    Open_PO_due_in_this_quarter=row['Open_PO_due_in_this_quarter'],
                    Open_PO_due_in_next_quarter=row['Open_PO_due_in_next_quarter'],
                    Delivery_Based_Total_OH_sum_OPO_this_quarter=row['Delivery_Based_Total_OH_sum_OPO_this_quarter'],
                    PO_Based_Total_OH_sum_OPO=row['PO_Based_Total_OH_sum_OPO'],
                    CQ_ARIS_FQ_sum_1_SANM_Demand=row['CQ_ARIS_FQ_sum_1_SANM_Demand'],
                    CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand=row['CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand'],
                    CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand=row['CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand'],
                    CQ_sum_3_ARIS_FQ_SANM_Demand=row['CQ_sum_3_ARIS_FQ_SANM_Demand'],
                    Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista=row['Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista'],
                    ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std=row['sgd_jpe_cost'],
                    sgd_jpe_cost=f"{row['sgd_jpe_cost']}/-/-".replace('None','-') if row['cm']=='SGD' else (f"-/{row['sgd_jpe_cost']}/-".replace('None','-') if row['cm']=='JPE' else f"-/-/{row['sgd_jpe_cost']}".replace('None','-') ),
                    CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD=row['CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD'],
                    Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1=row['Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1'],
                    Blended_AVG_PO_Receipt_Price=row['Blended_AVG_PO_Receipt_Price'],
                    bp_comment=row['bp_comment'],
                    Team=Team,
                    file_from=row['cm'],

                )
                data.created_by=request.user
                data.offcycle=True
                data.save()
                create_global(request,data)
                created.append(data.id)
                pic_list.append(row['Arista_PIC'])
        non_avl_notified_mail(request, list(set(pic_list)))
                
        ids=list(Portfolio.objects.filter(Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm__in=['SGD','FGN','HBG','JSJ','JMX']).distinct('Arista_Part_Number').filter(id__in=created).values_list('id',flat=True))
        id2=list(Portfolio.objects.filter(Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm='JPE').distinct('Arista_Part_Number').filter(id__in=created).values_list('id',flat=True))
        ids.extend(id2)
        ids=list(set(ids))
        if ids:
            create_rfx(request,parts=ids,To=['cm'],created_by=None,Arista_pic_comment='')
            auto_clean_rfx_cm()
        if error_index:
            table=df[df.index.isin(error_index)].fillna('').to_html(classes='table table-xs text-nowarp font-small-2 table-responsive table-striped')

            return JsonResponse({'data':table})
        return JsonResponse({'data':'success'})

    elif option=='download_template':
        with BytesIO() as b:
            data=Portfolio.objects.none().values(

"cm_Part_Number",
"Arista_Part_Number",
"cm",
"Ownership",
"Arista_PIC",
"Parts_controlled_by",
"Lifecycle_Phase",
"Rev",
"Mfr_Name",
"Mfr_Part_Lifecycle_Phase",
"Mfr_Part_Number",
"Qualification_Status",
"Cust_consign",
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
"sgd_jpe_cost",
"CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD",
"Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1",
"Blended_AVG_PO_Receipt_Price",
"bp_comment",

            ).to_dataframe()
            with pd.ExcelWriter(b) as writer:
                user=[ f'''{x.first_name} {x.last_name}''' for x in User.objects.filter(groups__in=[Group.objects.get(name='GSM Team'),Group.objects.get(name='CMM Team')])]+[
                                            "Kathy Ch'ng/Erlyn",
                                            "Kathy Ch'ng/Huan",
                                            "Kathy Ch'ng/Rima",
                                            "Kathy Ch'ng/Susan",
                                            "Kathy Ch'ng/Yonn",
                                            "Kathy Ch'ng/Eduardo",
                                            "Lai Chen Soong/John",
                                            "Lai Chen Soong/Susan",
                                            "Lai Chen Soong/Yonn",
                                            "Lai Chen Soong/Erlyn",
                                            "Lai Chen Soong/Eduardo",
                                        ]
                user_list=pd.DataFrame(user)                       
                data.rename(columns=column_names_portfolio_avl,inplace=True)
                data.to_excel(writer,index=False,sheet_name='Non-AVL template')
                user_list.to_excel(writer,index=False,header=False,sheet_name='Sheet2')
                worksheet = writer.sheets['Non-AVL template']
                usersheet = writer.sheets['Sheet2']
                usersheet.hide()
                worksheet.data_validation('C2:C1048576', {'validate': 'list',
                                    'source': ['SGD','JPE','FGN','HBG','JSJ','JMX'],
                                    })
                worksheet.data_validation('D2:D1048576', {'validate': 'list',
                                    'source': ['Arista','Sanmina','Jabil','Flex','Foxconn','Jabil San Jose','Jabil Mexico'],
                                    })
                worksheet.data_validation('M2:M1048576', {'validate': 'list',
                                    'source': ['Y','N'],
                                    })
                worksheet.data_validation('Q2:Q1048576', {'validate': 'list',
                                    'source': ['PO','Delivery'],
                                    })
                
                #print(user)
                worksheet.data_validation('E2:E1048576', {'validate': 'list',
                                        'source': '=Sheet2!A:A'
                                    })

                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'inline; filename=Non-AVL template.xlsx'
                return response




def file_operations(request,operation):
    '''
    Type:Dynamic Function
    Arg:request,operation
    ####process#####:
    operation=load:
        
        This will return the list of data in the CM folders ie.sgd,jpe,fgn,hbg,jsj,jmx,...
        with the files in with ui
    elif operation=='delete':
        delete a file from the folder
    elif operation=='form':
        this form is to save the file uploaded by the user based on the cm folders
    elif operation=='download':
        Will return the file which the user clicked  and this is based on cm and file name
    elif operation=='download':
        Will return the file which the user clicked  and this is based on cm and file name
    elif operation=='check_render':
        this is a function which excute on intervel of time which work as blocker for portfolio
        if any portfolio is renderding this will block every ones portfolio hence new parts are getting added

    ####comments:
        this is the place where BP team upload the files for portfolio creation
    '''
    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Portfolio_inputs')
    if operation=='load':
        files_SGD_path=sorted(os.scandir(f'''{path}/SGD'''), key=lambda t: t.stat().st_mtime)
        files_SGD=[ [x.name,x.stat().st_size/1000] for x in files_SGD_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and  not x.name.startswith('~$')]
        files_SGD.reverse()
        files_JPE_path=sorted(os.scandir(f'''{path}/JPE'''), key=lambda t: t.stat().st_mtime)
        files_JPE=[[x.name,x.stat().st_size/1000] for x in files_JPE_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_JPE.reverse()
        files_FGN_path=sorted(os.scandir(f'''{path}/FGN'''), key=lambda t: t.stat().st_mtime)
        files_FGN=[[x.name,x.stat().st_size/1000] for x in files_FGN_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_FGN.reverse()
        files_HBG_path=sorted(os.scandir(f'''{path}/HBG'''), key=lambda t: t.stat().st_mtime)
        files_HBG=[[x.name,x.stat().st_size/1000] for x in files_HBG_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_HBG.reverse()
        files_JSJ_path=sorted(os.scandir(f'''{path}/JSJ'''), key=lambda t: t.stat().st_mtime)
        files_JSJ=[[x.name,x.stat().st_size/1000] for x in files_JSJ_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_JSJ.reverse()
        files_JMX_path=sorted(os.scandir(f'''{path}/JMX'''), key=lambda t: t.stat().st_mtime)
        files_JMX=[[x.name,x.stat().st_size/1000] for x in files_JMX_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_JMX.reverse()
        # SGD_date=VwFactSgdMrpIness.objects.using('inputdb').values_list('reportdate',flat=True).order_by('-reportdate').distinct()

        # try:
        #     refreshed_date=Portfolio.objects.filter(refreshed_MRP_date__isnull=False).latest('id').refreshed_MRP_date.date()
        # except:
        #     refreshed_date=None
        #     LOGGER.error("LOG_MESSAGE", exc_info=1)
        cms=['FGN','SGD','JMX','JSJ']
            
        return render(request,template_name='portfolio/file_operations.html',
        context={
            "files_SGD":files_SGD,
            "files_JPE":files_JPE,
            "files_FGN":files_FGN,
            "files_HBG":files_HBG,
            "files_JSJ":files_JSJ,
            "files_JMX":files_JMX,
            'cms':cms,
            # 'SGD_date':SGD_date,
            # 'refreshed_date':refreshed_date
            })
    elif operation=='delete':
        file_name=request.GET.get('file_name')
        print('file_name')
        # cm=file_name.split('/')[0]
        cm=request.GET.get('cm')
        print(cm,'cm')
        if not os.path.exists(os.path.join(settings.BASE_DIR, f"{path}/backup/{cm}")):
            os.makedirs(os.path.join(settings.BASE_DIR, f"{path}/backup/{cm}"))
        shutil.move(os.path.join(settings.BASE_DIR, f"{path}/{cm}/{file_name}"), os.path.join(settings.BASE_DIR, f"{path}/backup/{file_name}"))
        # os.remove()
        return JsonResponse({'status':'success'})
    elif operation=='form':
        #print(request.POST)
        cm=request.POST.get('cm')
        file_To_Replace=request.POST.get('file_To_Replace')
        files=request.FILES['files']

        if True:
            #print(files)
            pd.read_excel(files)

            fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, f'{path}/{cm}/'))
            if file_To_Replace=='add':
                fs.save(files.name, files)
            else:
                #print(file_To_Replace)
                fs.delete(name=file_To_Replace)
                fs.save(file_To_Replace, files)
            return JsonResponse({'status':'success'})
        else :
            return JsonResponse({'status':'error',"message":'Invalid excel Format'})
    elif operation=='download':
        file=request.GET.get('name')
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    elif operation=='check_render':
        if logger_portfolio.objects.filter(completed_status=False).exists():
            data=logger_portfolio.objects.filter(completed_status=False)[0]
            name=data.modified_by.first_name+' '+data.modified_by.last_name
            status=True
        else:
            name=''
            status=False
        return JsonResponse({'status':status,'name':name},safe=False)

@multi_threading
def render_portfolio_task(request,date,CM_loc):
    '''
    Type:Static Function(multi_threading)
    Arg:request
    ####process#####:
    This is an multi thread function which run the task in backend and doesn't make the user to wait
   
    every render is saved in logger_portfolio makeing flag to started,stopped and stopped due to error
    '''
    try:
        instance=logger_portfolio(modified_by=request.user)
        instance.save()
        try:
            parts_created=portfolio_creation(request,date,CM_loc)
            instance.comments="Portfolio Updated successfully,"
            send_push_notification(request.user,subject='Success, Portfolio Refresh',text='Portfolio has been refreshed successfully',url='#')
            instance.status=True
            instance.completed_status=True
            instance.save()
        except Exception as error:
            instance.comments="portfolio updation failed, kindly check the file"
            tb_str = ''.join(traceback.format_exception(None, error, error.__traceback__))
            #print(tb_str)
            instance.error=tb_str
            instance.status=False
            instance.completed_status=True
            instance.save()
            send_push_notification(request.user,subject='Error in Portfolio Refresh',text='Portfolio refresh Failed, Please check the file.If any help needed contact suppport',url='#')
            LOGGER.error("LOG_MESSAGE", exc_info=1)
            

        try:
            part_all_list=parts_detail.objects.values_list('cpn',flat=True)
            qr=Portfolio.objects.filter(Number__in=parts_created).distinct('Number').values_list('Number',flat=True)
            bulk=[]
            for part in qr:
                p=parts_detail.objects.filter(cpn=part)
                if p:
                    p=p[0]
                    Portfolio.objects.filter(Number=part).update(
                        commodity=p.commodity,
                        )
            send_push_notification(request.user,subject='Success, Parts are assigned',text='Parts have been assigned by as per Part Assigner Page',url='#')
        except Exception as e:
            tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
            #print(tb_str)

            instance.status=False
            instance.completed_status=True
            instance.save()
            LOGGER.error("LOG_MESSAGE", exc_info=1)


        instance.completed_status=True
        instance.save()
    except :
        instance.completed_status=True
        instance.save()
        LOGGER.error("LOG_MESSAGE", exc_info=1)
        
    finally:
        instance.completed_status=True
        instance.save()




@error_handle
@login_required
def render_portfolio(request):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    This is place where the portfolio_creation is trigged from the user side 
    here we check if they have permission to refresh or update the Portfolio
    '''
    if (has_permission(request.user,'Super User') or request.user.is_superuser) and not logger_portfolio.objects.filter(completed_status=False).exists():
        date=request.GET.get('date')
        CM_loc=request.GET.get('CM_loc')

        render_portfolio_task(request,date,CM_loc)
        
        return JsonResponse({'status':'success','message':'Task Started, we will notify you'})
    elif logger_portfolio.objects.filter(completed_status=False).exists():
        return JsonResponse({'status':'error','message':'Another process is running'})
    else:
        return JsonResponse({'status':'error','message':'you have No Permission'})

def Refresh_Top_Component_JPE(request):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    This is an multi thread function which run the task in backend and doesn't make the user to wait
   
    this will render the  top Component for JPE 
    '''
    starttime = datetime.datetime.now()
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    reportdate = request.POST.get('reportdate')
    val = request.POST.get('quarter')
    currentqtr = Current_quarter()
    quarter=get_Next_quarter()
    exceldata=pd.read_excel(request.FILES['jpe_comp'])
    #print(exceldata)
    timerange = []
    qtr = []
    for i in range(int(val), 4+int(val)):
        start_end = qtr_start_end_manual(str(i))
        timerange.append([start_end[0],start_end[1]])
        qtr.append(start_end[2])
    #df1 = pd.DataFrame(columns=['cpn','apn','arista_pic','ownership','part_desc','po_or_delivery','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','quarter','team','contract_mfr'])
    #df = pd.DataFrame(VwFactJpeMrpIness.objects.using('inputdb').filter(reportdate=reportdate).values('origpartcode','lodid','jabilowninventory','poqty','demandqty','caldate').annotate(OH=Sum(F('lodid') + F('jabilowninventory') + F('poqty'))))
    #df1=pd.pivot_table(df,index=["origpartcode",'lodid','jabilowninventory','poqty','OH'],values=['demandqty'],aggfunc=np.sum)
    #df1['Q1'] = df1.apply(lambda x: df.loc[(df.caldate >= parse_date(start_end[0])) & (df.caldate <= parse_date(start_end[0])), 'demandqty'].sum(), axis=1)
    delete = TopComponentJpe.objects.using('inputdb').filter(contract_mfr = "JPE").delete()
    #print("is deleted",delete)
    parts = VwFactJpeMrpIness.objects.using('inputdb').raw("SELECT T1.`ID`, T1.`StandardPrice`, T1.`OrigPartCode`, T1.`AristaPartnumber`,SUM(T1.`LodID`) AS Lodid, SUM(T1.`JabilOwnInventory`) AS Inv, SUM(T1.`POQty`) PO, T2.Q1, T3.Q2, T4.Q3, T5.Q4 FROM (SELECT * FROM `vw_fact_jpe_mrp_iness` WHERE `ReportDate` = '"+ str(reportdate) +"' GROUP BY `OrigPartCode`) AS T1 LEFT JOIN (SELECT `OrigPartCode`, SUM(IFNULL(`demandqty`,0)) AS Q1 FROM `vw_fact_jpe_mrp_iness` WHERE `CalDate` BETWEEN '"+ str(timerange[0][0]) +"' AND '"+ str(timerange[0][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `OrigPartCode`) AS T2 ON T1.OrigPartCode = T2.OrigPartCode LEFT JOIN (SELECT `OrigPartCode`, SUM(IFNULL(`demandqty`,0)) AS Q2 FROM `vw_fact_jpe_mrp_iness` WHERE `CalDate` BETWEEN '"+str (timerange[1][0]) +"' AND '"+ str(timerange[1][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `OrigPartCode`) AS T3 ON T1.OrigPartCode = T3.OrigPartCode LEFT JOIN (SELECT `OrigPartCode`, SUM(IFNULL(`demandqty`,0)) AS Q3 FROM `vw_fact_jpe_mrp_iness` WHERE `CalDate` BETWEEN '"+ str(timerange[2][0]) +"' AND '"+ str(timerange[2][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `OrigPartCode`) AS T4 ON T1.OrigPartCode = T4.OrigPartCode Left JOIN (SELECT `OrigPartCode`, SUM(IFNULL(`demandqty`,0)) AS Q4 FROM `vw_fact_jpe_mrp_iness` WHERE `CalDate` BETWEEN '"+ str(timerange[3][0]) +"' AND '"+str (timerange[3][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `OrigPartCode`) AS T5 ON T1.OrigPartCode = T5.OrigPartCode GROUP BY COALESCE(T1.`AristaPartnumber`, T1.`OrigPartCode`)")
    f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
    gsm_Team=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    f_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('last_name',flat=True)
    gsm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    gsm_Team.extend(gsm_manager)
    #print('GSM Team',gsm_Team)
    l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
    f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
    cmm_team=[f'''{list(f_name)[x]} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    f_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('last_name',flat=True)
    cmm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    cmm_team.extend(cmm_manager)
    #print('CMM Team',cmm_team)
    for part in parts:
        if parts_detail.objects.filter(cpn=part.aristapartnumber).filter(cm="JPE").exists():
            assignedparts = parts_detail.objects.filter(cpn=part.aristapartnumber).filter(cm="JPE")[:1].get()
            pic = assignedparts.arista_pic
            owner = assignedparts.Ownership
            cm = assignedparts.cm
            if pic in gsm_Team:
                team = "GSM Team"
            elif pic in cmm_team:
                team = "CMM Team"
            else:
                team = None
        else:
            assignedparts = parts_detail.objects.none()
            pic = None
            owner = None
            cm = None
            team = None
        if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=part.aristapartnumber).exists():
            agile = FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=part.aristapartnumber)[:1].get()
            desc = agile.ampart_description
        else:
            desc = None
        prevqtr = currentqtr + " unit price (USD)"
        quotqtr = quarter[0] + " unit price (USD)"
        exceldata=exceldata.fillna(0)
        std_cost_1 = exceldata[exceldata["APN"] == part.aristapartnumber][prevqtr].tolist()
        std_cost_2 = exceldata[exceldata["APN"] == part.aristapartnumber][quotqtr].tolist()
        #print(std_cost_2)
        totaloh = part.Lodid + part.Inv + part.PO
        if part.Q1 == None : Q1=0
        else : Q1=part.Q1
        if part.Q2 == None : Q2=0
        else : Q2=part.Q2
        if part.Q3 == None : Q3=0
        else : Q3=part.Q3
        if part.Q4 == None : Q4=0
        else : Q4=part.Q4
        if len(std_cost_1) == 0 : stdprice1=0.0
        else : stdprice1=std_cost_1[0]
        if len(std_cost_2) == 0 : stdprice2=0.0
        else : stdprice2=std_cost_2[0]
        anualdemand = Q1 + Q2 + Q3 + Q4
        delta = anualdemand - totaloh
        if delta < 0 : delta=0
        #print("Q1 Demand",Q1)
        topcomp = TopComponentJpe(
            cpn = part.origpartcode,
            apn = part.aristapartnumber,
            arista_pic = pic,
            ownership = owner,
            part_desc = desc,
            #po_or_delivery = podel,
            cm_buffer_on_hand = part.Lodid,
            cs_inv = part.Inv,
            open_po = part.PO,
            total_oh = round(totaloh,5),
            q0_demand = round(Q1,5),
            q1_demand = round(Q2,5),
            q2_demand = round(Q3,5),
            q3_demand = round(Q4,5),
            annual_demand = round(anualdemand,5),
            delta_demand = round(float(delta),5),
            quarter_std_1 = round(stdprice1,5),
            quarter_std_2 = round(stdprice2,5),
            delta_std = round(abs(stdprice2 - stdprice1),5),
            delta_demand_x_quarter_std_1 = round(float(Q1) * float(stdprice2),5),
            delta_demand_2_x_quarter_std_1 = round(float(Q2) * float(stdprice2),5),
            delta_demand_3_x_quarter_std_1 = round(float(Q3) * float(stdprice2),5),
            delta_demand_4_x_quarter_std_1 = round(float(Q4) * float(stdprice2),5),
            delta_demand_x_delta_std = round(float(delta) * float(stdprice2),5),
            delta_demand_x_delta_std_per = round(float(delta),5) * round(abs(stdprice1 - stdprice2),5),
            quarter = currentqtr,
            qtr_id = int(val),
            team = team,
            contract_mfr = "JPE",
            qtr_col = ','.join(qtr),
            reportdate = reportdate,
        )
        topcomp.save(using="inputdb")
        if TopComponentGlobal.objects.using('inputdb').filter(apn=part.aristapartnumber).exists():
            TopComponentGlobal.objects.using('inputdb').filter(apn=part.aristapartnumber).update(
                jpeowner = owner,
                jpepic = pic,
                jpedemand = round(anualdemand,5),
                jpeoh = round(totaloh,5),
                jpestd = round(stdprice2,5),
                jpedelta = round(float(delta),5)
            )
        else:
            global_data=TopComponentGlobal(
                apn = part.aristapartnumber,
                jpepic = pic,
                part_desc = desc,
                jpeowner = owner,
                jpedemand = round(anualdemand,5),
                jpeoh = round(totaloh,5),
                jpestd = round(stdprice2,5),
                jpedelta = round(float(delta),5),
                cm = "JPE"
            )
            global_data.save(using="inputdb")
    endtime = datetime.datetime.now()
    text = "<b>Start Time :</b> "+ str(starttime) +"<br> <b> End Time :</b> "+ str(endtime)
    return redirect('Refresh_Components')

@login_required
def Refresh_Top_Component_SGD(request):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    This is an multi thread function which run the task in backend and doesn't make the user to wait
   
    this will render the  top Component for SGD 
    '''
    starttime = datetime.datetime.now()
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    reportdate = request.POST.get('reportdate')
    val = request.POST.get('quarter')
    currentqtr = Current_quarter()
    quarter=get_Next_quarter()
    exceldata=pd.read_excel(request.FILES['sgd_comp'])
    timerange = []
    qtr = []
    for i in range(int(val), 4+int(val)):
        start_end = qtr_start_end_manual(str(i))
        timerange.append([start_end[0],start_end[1]])
        qtr.append(start_end[2])
    #df1 = pd.DataFrame(columns=['cpn','apn','arista_pic','ownership','part_desc','po_or_delivery','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','quarter','team','contract_mfr'])
    delete = TopComponentSgd.objects.using('inputdb').filter(contract_mfr = "SGD").delete()
    #delete_global = TopComponentGlobal.objects.using('inputdb').filter(cm = "SGD").delete()
    #print("is deleted",delete)
    parts = VwFactSgdMrpIness.objects.using('inputdb').raw("SELECT T1.`id`, SUM(T1.`onhandqty`) AS OH, SUM(T1.`bufferstock`) AS Buffer, SUM(T1.`openpoopenqty`) AS Openpo, T1.`quotedprice`, T1.`part`, T1.`AristaPartnumber`, T2.Q1, T3.Q2, T4.Q3, T5.Q4 FROM (SELECT * FROM `vw_fact_sgd_mrp_iness` WHERE `ReportDate` = '"+ str(reportdate) +"' GROUP BY `part`) AS T1 LEFT JOIN (SELECT `part`, SUM(IFNULL(`demandqty`,0)) AS Q1 FROM `vw_fact_sgd_mrp_iness` WHERE `CalDate` BETWEEN '"+ str(timerange[0][0]) +"' AND '"+ str(timerange[0][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `part`) AS T2 ON T1.part = T2.part LEFT JOIN (SELECT `part`, SUM(IFNULL(`demandqty`,0)) AS Q2 FROM `vw_fact_sgd_mrp_iness` WHERE `CalDate` BETWEEN '"+str (timerange[1][0]) +"' AND '"+ str(timerange[1][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `part`) AS T3 ON T1.part = T3.part LEFT JOIN (SELECT `part`, SUM(IFNULL(`demandqty`,0)) AS Q3 FROM `vw_fact_sgd_mrp_iness` WHERE `CalDate` BETWEEN '"+ str(timerange[2][0]) +"' AND '"+ str(timerange[2][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `part`) AS T4 ON T1.part = T4.part Left JOIN (SELECT `part`, SUM(IFNULL(`demandqty`,0)) AS Q4 FROM `vw_fact_sgd_mrp_iness` WHERE `CalDate` BETWEEN '"+ str(timerange[3][0]) +"' AND '"+str (timerange[3][1]) +"' AND `ReportDate` = '"+ str(reportdate) +"' GROUP BY `part`) AS T5 ON T1.part = T5.part GROUP BY COALESCE(T1.`AristaPartnumber`, T1.`part`)")
    f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
    gsm_Team=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    f_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('last_name',flat=True)
    gsm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    gsm_Team.extend(gsm_manager)
    #print('GSM Team',gsm_Team)
    l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
    f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
    cmm_team=[f'''{list(f_name)[x]} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    f_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('last_name',flat=True)
    cmm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    cmm_team.extend(cmm_manager)
    #print('CMM Team',cmm_team)
    for part in parts:
        #print(part.part)
        if parts_detail.objects.filter(cpn=part.aristapartnumber).filter(cm="SGD").exists():
            assignedparts = parts_detail.objects.filter(cpn=part.aristapartnumber).filter(cm="SGD")[:1].get()
            pic = assignedparts.arista_pic
            owner = assignedparts.Ownership
            cm = assignedparts.cm
            if pic in gsm_Team:
                team = "GSM Team"
            elif pic in cmm_team:
                team = "CMM Team"
            else:
                team = None
        else:
            assignedparts = parts_detail.objects.none()
            pic = None
            owner = None
            cm = None
            team = None
        if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=part.aristapartnumber).exists():
            agile = FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=part.aristapartnumber)[:1].get()
            desc = agile.ampart_description
        else:
            desc = None
        prevqtr = "ARIS - C" + currentqtr + "/ SANM - F"+ quarter[0] + " unit price (USD) / Current std."
        quotqtr = "C"+ quarter[0] + " (ARIS) / F"+ quarter[1] + " (SANM) unit price (USD)"
        exceldata=exceldata.fillna(0)
        std_cost_1 = exceldata[exceldata["Arista Part Number"] == part.aristapartnumber][prevqtr].tolist()
        std_cost_2 = exceldata[exceldata["Arista Part Number"] == part.aristapartnumber][quotqtr].tolist()
        totaloh = part.Buffer + part.OH + part.Openpo
        if part.Q1 == None : Q1=0
        else : Q1=part.Q1
        if part.Q2 == None : Q2=0
        else : Q2=part.Q2
        if part.Q3 == None : Q3=0
        else : Q3=part.Q3
        if part.Q4 == None : Q4=0
        else : Q4=part.Q4
        if len(std_cost_1) == 0 : stdprice1=0.0
        else : stdprice1=std_cost_1[0]
        if len(std_cost_2) == 0 : stdprice2=0.0
        else : stdprice2=std_cost_2[0]
        anualdemand = Q1 + Q2 + Q3 + Q4
        delta = anualdemand - totaloh
        if delta < 0 : delta=0
        topcomp = TopComponentSgd(
            cpn = part.part,
            apn = part.aristapartnumber,
            arista_pic = pic,
            ownership = owner,
            part_desc = desc,
            #po_or_delivery = podel,
            cm_buffer_on_hand = part.Buffer,
            cs_inv = part.OH,
            open_po = part.Openpo,
            total_oh = round(totaloh,5),
            q0_demand = round(Q1,5),
            q1_demand = round(Q2,5),
            q2_demand = round(Q3,5),
            q3_demand = round(Q4,5),
            annual_demand = round(anualdemand,5),
            delta_demand = round(float(delta),5),
            quarter_std_1 = round(stdprice1,5),
            quarter_std_2 = round(stdprice2,5),
            delta_std = round(abs(stdprice1 - stdprice2),5),
            delta_demand_x_quarter_std_1 = round(float(Q1) * float(stdprice2),5),
            delta_demand_2_x_quarter_std_1 = round(float(Q2) * float(stdprice2),5),
            delta_demand_3_x_quarter_std_1 = round(float(Q3) * float(stdprice2),5),
            delta_demand_4_x_quarter_std_1 = round(float(Q4) * float(stdprice2),5),
            delta_demand_x_delta_std = round(float(delta) * float(stdprice2),5),
            delta_demand_x_delta_std_per = round(float(delta),5) * round(abs(stdprice1 - stdprice2),5),
            quarter = currentqtr,
            qtr_id = int(val),
            team = team,
            contract_mfr = "SGD",
            qtr_col = ','.join(qtr),
            reportdate = reportdate,
        )
        topcomp.save(using="inputdb")
        if TopComponentGlobal.objects.using('inputdb').filter(apn=part.aristapartnumber).exists():
            TopComponentGlobal.objects.using('inputdb').filter(apn=part.aristapartnumber).update(
                sgdowner = owner,
                sgdpic = pic,
                sgddemand = round(anualdemand,5),
                sgdoh = round(totaloh,5),
                sgdstd = round(stdprice2,5),
                sgddelta = round(float(delta),5)
            )
        else:
            global_data=TopComponentGlobal(
                apn = part.aristapartnumber,
                #arista_pic = pic,
                sgdpic = pic,
                part_desc = desc,
                sgdowner = owner,
                sgddemand = round(anualdemand,5),
                sgdoh = round(totaloh,5),
                sgdstd = round(stdprice2,5),
                sgddelta = round(float(delta),5),
                cm = "SGD"
            )
            global_data.save(using="inputdb")
            #print('updated')
    endtime = datetime.datetime.now()
    text = "<b>Start Time :</b> "+ str(starttime) +"<br> <b> End Time :</b> "+ str(endtime)
    return redirect('Refresh_Components')

@login_required
def top_component_new(request,team=None):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    top_component_new(By karthik)
    '''
    if team=='GSM' and (request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user in User.objects.filter(groups=Group.objects.get(name='Super User')) or request.user.is_superuser or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor'))):
        if has_permission(request.user,'Super User') or request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or request.user.is_superuser  or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor')):
            user=User.objects.filter(groups__in=Group.objects.filter(name__in=['GSM Team','GSM Manager'])).values_list('id',flat=True)
        else:
            user=User.objects.filter(username=request.user.username).values_list('id',flat=True)
        sgdreportdate=VwFactSgdMrpIness.objects.using('inputdb').raw("SELECT `id`, `ReportDate` FROM `vw_fact_sgd_mrp_iness` GROUP BY `ReportDate` ORDER BY `ReportDate` DESC LIMIT 8")
        Qtr_id = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`qtr_id`),`id` FROM `top_component_sgd` LIMIT 1")
        column = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`qtr_col`),`id` FROM `top_component_sgd` LIMIT 1")
        reportdate = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`reportdate`),`id` FROM `top_component_sgd` LIMIT 1")
        for id in Qtr_id:
            Qtr_id = id.qtr_id
        for col in column:
            column = col.qtr_col.split(',')
        for date in reportdate:
            reportdate = date.reportdate
        quote_qtr=get_Next_quarter()
        return render(request,"portfolio/top_component_gsm_new.html",
        context={
        'users':user,
        'quarter':Current_quarter(),
        'quote_qtr':quote_qtr,
        'sgdreportdate':sgdreportdate,
        'Qtr_id':Qtr_id,
        'column':column,
        'reportdate':reportdate,
        })
    elif team=='CMM' and (request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or request.user in User.objects.filter(groups=Group.objects.get(name='CMM Team')) or request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or request.user.is_superuser or request.user in User.objects.filter(groups=Group.objects.get(name='Super User')) or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor'))):
        if has_permission(request.user,'Super User')  or request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or request.user.is_superuser or request.user in User.objects.filter(groups=Group.objects.get(name='BP Supervisor')):
            user=User.objects.filter(groups__in=Group.objects.filter(name__in=['CMM Team','CMM Manager'])).values_list('id',flat=True)
        else:
            user=User.objects.filter(username=request.user.username).values_list('id',flat=True)
        jpereportdate=VwFactJpeMrpIness.objects.using('inputdb').raw("SELECT `ID`, `ReportDate` FROM `vw_fact_jpe_mrp_iness` GROUP BY `ReportDate` ORDER BY `ReportDate` DESC LIMIT 8")
        Qtr_id = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`qtr_id`),`id` FROM `top_component_sgd` LIMIT 1")
        column = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`qtr_col`),`id` FROM `top_component_sgd` LIMIT 1")
        reportdate = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`reportdate`),`id` FROM `top_component_sgd` LIMIT 1")
        for id in Qtr_id:
            Qtr_id = id.qtr_id
        for col in column:
            column = col.qtr_col.split(',')
        for date in reportdate:
            reportdate = date.reportdate
        quote_qtr=get_Next_quarter()
        return render(request,"portfolio/top_component_cmm_new.html",
        context={
        'quarter':Current_quarter(),
        'quote_qtr':quote_qtr,
        'jpereportdate':jpereportdate,
        'Qtr_id':Qtr_id,
        'column':column,
        'reportdate':reportdate,
        'users':user
        }
    )
    elif team == 'unassigned':
        Qtr_id = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`qtr_id`),`id` FROM `top_component_sgd` LIMIT 1")
        column = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`qtr_col`),`id` FROM `top_component_sgd` LIMIT 1")
        reportdate = TopComponentSgd.objects.using('inputdb').raw("SELECT DISTINCT(`reportdate`),`id` FROM `top_component_sgd` LIMIT 1")
        for id in Qtr_id:
            Qtr_id = id.qtr_id
        for col in column:
            column = col.qtr_col.split(',')
        for date in reportdate:
            reportdate = date.reportdate
        quote_qtr=get_Next_quarter()
        return render(request,"portfolio/top_component_unassigned.html",
        context={
        'quarter':Current_quarter(),
        'quote_qtr':quote_qtr,
        'Qtr_id':Qtr_id,
        'column':column,
        'reportdate':reportdate,
        })
    else:
        return redirect('/')

@login_required
def Refresh_Components(request):
    sgdreportdate=VwFactSgdMrpIness.objects.using('inputdb').raw("SELECT `id`, `ReportDate` FROM `vw_fact_sgd_mrp_iness` GROUP BY `ReportDate` ORDER BY `ReportDate` DESC LIMIT 8")
    jpereportdate=VwFactJpeMrpIness.objects.using('inputdb').raw("SELECT `ID`, `ReportDate` FROM `vw_fact_jpe_mrp_iness` GROUP BY `ReportDate` ORDER BY `ReportDate` DESC LIMIT 8")
    #globaldata = TopComponentSgd.objects.using('inputdb').all().union(TopComponentJpe.objects.using('inputdb').all())
    #print(globaldata)
    return render(request,"portfolio/top_component_refresh.html",
        context={
        'sgdreportdate':sgdreportdate,
        'jpereportdate':jpereportdate,
        #'globaldata':globaldata,
        })

@login_required
def export_top_component(request, team):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    export_top_component(By karthik)
    '''
    if team == "GSM":
        f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
        l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
        gsm_Team=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
        f_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('first_name',flat=True)
        l_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('last_name',flat=True)
        gsm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
        gsm_Team.extend(gsm_manager)
        columns = ['cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team']
        alias = ['CPN','APN','Arista Pic','Ownership','Part Desc','CM Buffer On Hand','CS Inv','Open PO','Total OH','CQ Demand','CQ + 1 Demand','CQ + 2 Demand','CQ + 3 Demand','Annual Demand','Delta Demand','CQ - 1 Std. Cost','Current Quarter Std. Cost','Delta Std.','CQ * Current qtr std cost','CQ + 1 * Current qtr std cost','CQ + 2 * Current qtr std cost','CQ + 3 * Current qtr std cost','Delta Demand * Current Qtr std cost','Delta Demand * Delta Std. Cost','Team']
        df1=pd.DataFrame(TopComponentSgd.objects.using('inputdb').filter(team='GSM Team').values_list('cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team'),columns=columns)
        df2=pd.DataFrame(TopComponentJpe.objects.using('inputdb').filter(team='GSM Team').values_list('cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team'),columns=columns)
        global_alias = ['APN','Part Desc','Ownership (JPE)','Arista Pic (JPE)','Total OH (JPE)','Annual Demand (JPE)','Delta Demand (JPE)','Current Qtr std cost (JPE)','Delta Demand * CQ Std. Cost (JPE)','Ownership (SGD)','Arista Pic (SGD)','Total OH (SGD)','Annual Demand (SGD)','Delta Demand (SGD)','Current Qtr std cost (SGD)','Delta Demand * CQ Std. Cost (SGD)','Global Annual Demand - OH','Global Spend ((Sanmina Demand * Sanmina STD) + ( Jabil Demand * Jabil STD))','Percentage of the Global Spend']
        global_sgd=pd.DataFrame(TopComponentGlobal.objects.using('inputdb').filter(Q(sgdpic__in=gsm_Team)|Q(jpepic__in=gsm_Team)).values_list('apn','part_desc','jpeowner','jpepic','jpeoh','jpedemand','jpedelta','jpestd','sgdowner','sgdpic','sgdoh','sgddemand','sgddelta','sgdstd').annotate(Delta_Demand_x_quarter_std_1_JPE=ExpressionWrapper(F('jpedelta') * F('jpestd'), output_field=FloatField())).annotate(Delta_Demand_x_quarter_std_1_SGD=ExpressionWrapper(F('sgddelta') * F('sgdstd'), output_field=FloatField())).annotate(Global_Annual_Demand=ExpressionWrapper(F('sgddelta') + F('jpedelta'), output_field=FloatField())).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())))
        global_sgd['Global Spend %'] = round((global_sgd[17] / global_sgd[17].sum()) * 100,2)
        #print(global_sgd.columns.values)
        global_sgd = global_sgd[[0,1,2,3,4,5,6,7,14,8,9,10,11,12,13,15,16,17,'Global Spend %']]
        global_sgd = global_sgd.sort_values(by=[17], ascending=False)
        #print(global_sgd.columns.values)
        memb=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('id',flat=True)
        gsm_Team=[f'''{(list(memb)[x])}''' for x in range(len(memb)) ]
        mgr=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('id',flat=True)
        gsm_manager=[f'''{(list(mgr)[x])}''' for x in range(len(mgr)) ]
        gsm_Team.extend(gsm_manager)

        #writer = pd.ExcelWriter('Top Component GSM Team.xlsx', engine='xlsxwriter')
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df1.to_excel(writer,index=False,header=alias, sheet_name='Sanmina')
                df2.to_excel(writer,index=False,header=alias, sheet_name='Jabil')
                global_sgd.to_excel(writer,index=False,header=global_alias, sheet_name='Global')
                for i in gsm_Team:
                    userdetails=User.objects.get(id=i)
                    if TopComponentGlobal.objects.using('inputdb').filter(Q(jpepic=userdetails.first_name + ' ' + userdetails.last_name) | Q(sgdpic=userdetails.first_name + ' ' + userdetails.last_name)).exists() :
                        global_sgd=pd.DataFrame(TopComponentGlobal.objects.using('inputdb').filter(Q(jpepic=userdetails.first_name + ' ' + userdetails.last_name) | Q(sgdpic=userdetails.first_name + ' ' + userdetails.last_name)).values_list('apn','part_desc','jpeowner','jpepic','jpeoh','jpedemand','jpedelta','jpestd','sgdowner','sgdpic','sgdoh','sgddemand','sgddelta','sgdstd').annotate(Delta_Demand_x_quarter_std_1_JPE=ExpressionWrapper(F('jpedelta') * F('jpestd'), output_field=FloatField())).annotate(Delta_Demand_x_quarter_std_1_SGD=ExpressionWrapper(F('sgddelta') * F('sgdstd'), output_field=FloatField())).annotate(Global_Annual_Demand=ExpressionWrapper(F('sgddelta') + F('jpedelta'), output_field=FloatField())).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())))
                        global_sgd['Global Spend %'] = round((global_sgd[17] / global_sgd[17].sum()) * 100,2)
                        global_sgd = global_sgd[[0,1,2,3,4,5,6,7,14,8,9,10,11,12,13,15,16,17,'Global Spend %']]
                        global_sgd = global_sgd.sort_values(by=[17], ascending=False)
                        global_sgd.to_excel(writer,index=False,header=global_alias, sheet_name=userdetails.first_name + ' ' + userdetails.last_name + ' Parts')

                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename="Top Component GSM Team.xlsx"'
                return response
    if team == "CMM":
        f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
        l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
        cmm_Team=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
        f_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('first_name',flat=True)
        l_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('last_name',flat=True)
        cmm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
        cmm_Team.extend(cmm_manager)
        columns = ['cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team']
        alias = ['CPN','APN','Arista Pic','Ownership','Part Desc','CM Buffer On Hand','CS Inv','Open PO','Total OH','CQ Demand','CQ + 1 Demand','CQ + 2 Demand','CQ + 3 Demand','Annual Demand','Delta Demand','CQ - 1 Std. Cost','Current Quarter Std. Cost','Delta Std.','CQ * Current qtr std cost','CQ + 1 * Current qtr std cost','CQ + 2 * Current qtr std cost','CQ + 3 * Current qtr std cost','Delta Demand * Current Qtr std cost','Delta Demand * Delta Std. Cost','Team']
        df1=pd.DataFrame(TopComponentSgd.objects.using('inputdb').filter(team='CMM Team').values_list('cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team'),columns=columns)
        df2=pd.DataFrame(TopComponentJpe.objects.using('inputdb').filter(team='CMM Team').values_list('cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team'),columns=columns)
        global_alias = ['APN','Part Desc','Ownership (JPE)','Arista Pic (JPE)','Total OH (JPE)','Annual Demand (JPE)','Delta Demand (JPE)','Current Qtr std cost (JPE)','Delta Demand * CQ Std. Cost (JPE)','Ownership (SGD)','Arista Pic (SGD)','Total OH (SGD)','Annual Demand (SGD)','Delta Demand (SGD)','Current Qtr std cost (SGD)','Delta Demand * CQ Std. Cost (SGD)','Global Annual Demand - OH','Global Spend ((Sanmina Demand * Sanmina STD) + ( Jabil Demand * Jabil STD))','Percentage of the Global Spend']
        global_sgd=pd.DataFrame(TopComponentGlobal.objects.using('inputdb').filter(Q(sgdpic__in=cmm_Team)|Q(jpepic__in=cmm_Team)).values_list('apn','part_desc','jpeowner','jpepic','jpeoh','jpedemand','jpedelta','jpestd','sgdowner','sgdpic','sgdoh','sgddemand','sgddelta','sgdstd').annotate(Delta_Demand_x_quarter_std_1_JPE=ExpressionWrapper(F('jpedelta') * F('jpestd'), output_field=FloatField())).annotate(Delta_Demand_x_quarter_std_1_SGD=ExpressionWrapper(F('sgddelta') * F('sgdstd'), output_field=FloatField())).annotate(Global_Annual_Demand=ExpressionWrapper(F('sgddelta') + F('jpedelta'), output_field=FloatField())).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())))
        global_sgd['Global Spend %'] = round((global_sgd[17] / global_sgd[17].sum()) * 100,2)
        global_sgd = global_sgd[[0,1,2,3,4,5,6,7,14,8,9,10,11,12,13,15,16,17,'Global Spend %']]
        global_sgd = global_sgd.sort_values(by=[17], ascending=False)
        #print(global_sgd)
        memb=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('id',flat=True)
        cmm_Team=[f'''{(list(memb)[x])}''' for x in range(len(memb)) ]
        mgr=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('id',flat=True)
        cmm_manager=[f'''{(list(mgr)[x])}''' for x in range(len(mgr)) ]
        cmm_Team.extend(cmm_manager)

        #writer = pd.ExcelWriter('Top Component CMM Team.xlsx', engine='xlsxwriter')
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df1.to_excel(writer,index=False,header=alias, sheet_name='Sanmina')
                df2.to_excel(writer,index=False,header=alias, sheet_name='Jabil')
                global_sgd.to_excel(writer,index=False,header=global_alias, sheet_name='Global')
                for i in cmm_Team:
                    userdetails=User.objects.get(id=i)
                    if TopComponentGlobal.objects.using('inputdb').filter(Q(jpepic=userdetails.first_name + ' ' + userdetails.last_name) | Q(sgdpic=userdetails.first_name + ' ' + userdetails.last_name)).exists() :
                        global_sgd=pd.DataFrame(TopComponentGlobal.objects.using('inputdb').filter(Q(jpepic=userdetails.first_name + ' ' + userdetails.last_name) | Q(sgdpic=userdetails.first_name + ' ' + userdetails.last_name)).values_list('apn','part_desc','jpeowner','jpepic','jpeoh','jpedemand','jpedelta','jpestd','sgdowner','sgdpic','sgdoh','sgddemand','sgddelta','sgdstd').annotate(Delta_Demand_x_quarter_std_1_JPE=ExpressionWrapper(F('jpedelta') * F('jpestd'), output_field=FloatField())).annotate(Delta_Demand_x_quarter_std_1_SGD=ExpressionWrapper(F('sgddelta') * F('sgdstd'), output_field=FloatField())).annotate(Global_Annual_Demand=ExpressionWrapper(F('sgddelta') + F('jpedelta'), output_field=FloatField())).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())))
                        #print(global_sgd.head())
                        global_sgd['Global Spend %'] = round((global_sgd[17] / global_sgd[17].sum()) * 100,2)
                        global_sgd = global_sgd[[0,1,2,3,4,5,6,7,14,8,9,10,11,12,13,15,16,17,'Global Spend %']]
                        global_sgd = global_sgd.sort_values(by=[17], ascending=False)
                        global_sgd.to_excel(writer,index=False,header=global_alias, sheet_name=userdetails.first_name + ' ' + userdetails.last_name + ' Parts')

                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename="Top Component CMM Team.xlsx"'
                return response
    if team == "unassigned":
        columns = ['cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team']
        alias = ['CPN','APN','Arista Pic','Ownership','Part Desc','CM Buffer On Hand','CS Inv','Open PO','Total OH','CQ Demand','CQ + 1 Demand','CQ + 2 Demand','CQ + 3 Demand','Annual Demand','Delta Demand','CQ - 1 Std. Cost','Current Quarter Std. Cost','Delta Std.','CQ * Current qtr std cost','CQ + 1 * Current qtr std cost','CQ + 2 * Current qtr std cost','CQ + 3 * Current qtr std cost','Delta Demand * Current Qtr std cost','Delta Demand * Delta Std. Cost','Team']
        df1=pd.DataFrame(TopComponentSgd.objects.using('inputdb').filter(team= None).values_list('cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team'),columns=columns)
        df2=pd.DataFrame(TopComponentJpe.objects.using('inputdb').filter(team= None).values_list('cpn','apn','arista_pic','ownership','part_desc','cm_buffer_on_hand','cs_inv','open_po','total_oh','q0_demand','q1_demand','q2_demand','q3_demand','annual_demand','delta_demand','quarter_std_1','quarter_std_2','delta_std','delta_demand_x_quarter_std_1','delta_demand_2_x_quarter_std_1','delta_demand_3_x_quarter_std_1','delta_demand_4_x_quarter_std_1','delta_demand_x_delta_std','delta_demand_x_delta_std_per','team'),columns=columns)
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df1.to_excel(writer,index=False,header=alias, sheet_name='Sanmina')
                df2.to_excel(writer,index=False,header=alias, sheet_name='Jabil')
                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename="Top Component Un Assigned.xlsx"'
                return response    
       
@login_required     
def download_topbom(request,Team=''):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    download_topbom(By karthik)
    '''
    
    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Sample_files/')    
    if Team == 'JPE':
        file='Top_BOM_JPE_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'SGD':
        file='Top_BOM_SGD_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'FGN':
        file='Top_BOM_FGN_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'HBG':
        file='Top_BOM_HBG_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'JSJ':
        file='Top_BOM_JSJ_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'JMX':
        file='Top_BOM_JMX_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
        
       
@login_required     
def download_topcomponent(request,Team=''):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    Here based on the path it return the file(xlsx)
    '''
    
    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Sample_files/')    
    if Team == 'JPE':
        file='Top_Component_JPE_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'SGD':
        file='Top_Component_SGD_Template.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
       
@login_required     
def download_portfolio_kickstart(request,Team=''):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    Return a file of templete Portfolio input file as excel from a static folder, Based on CM
    '''
    
    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Sample_files/')    
    if Team == 'JPE':
        file='JPE_Kickstart_Template_File.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'SGD':
        file='SGD_Kickstart_Template_File.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'FGN':
        file='FGN_Kickstart_Template_File.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'HBG':
        file='HBG_Kickstart_Template_File.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'JSJ':
        file='JSJ_Kickstart_Template_File.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response
    if Team == 'JMX':
        file='JMX_Kickstart_Template_File.xlsx'
        #print(file)

        fs = FileSystemStorage(location=path)
        if fs.exists(f'{file}'):
            fh = fs.open(f'{file}')
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={file}'
            return response

            
def create_global(request,portfolio_id,offcycle=True):
    '''
    1.Get the all the parts with portfolio_id filter from all  CM
        2.Convert them to dataframe and append to the newly created dataframe after joining.
        3.Groups all the portfolio(created from input and fetched from portfolio) Row(s) based [Mfr_Name,Number,Mfr_Part_Number,Ownership], with  the group.sum() of:
                cm_Quantity_Buffer_On_Hand,
                cm_Quantity_On_Hand_CS_Inv,
                Open_PO_due_in_this_quarter,
                Open_PO_due_in_next_quarter,
                Delivery_Based_Total_OH_sum_OPO_this_quarter,
                PO_Based_Total_OH_sum_OPO,
                CQ_ARIS_FQ_sum_1_SANM_Demand,
                CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand,
                CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand,
                CQ_sum_3_ARIS_FQ_SANM_Demand,
                Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista,
                CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD,
                Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1,
                Blended_AVG_PO_Receipt_Price,
                ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std
        4.Save the all dataframe to Portfolio Table
    '''
    columns=[
            "Number",
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
            "Original_PO_Delivery_sent_by_Mexico",
            "file_from",]
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
        "Original_PO_Delivery_sent_by_Mexico",
        'file_from',
        ]
    portfolio=Portfolio.objects.filter(Quarter=Current_quarter(),Number=str(portfolio_id.Number),Mfr_Name=portfolio_id.Mfr_Name,Ownership=portfolio_id.Ownership,Mfr_Part_Number=portfolio_id.Mfr_Part_Number,cm__in=['SGD','FGN','HBG','JSJ','JMX']).exclude(cm='Global').values(*columns).to_dataframe()
    portfolio2=Portfolio.objects.filter(Quarter=Current_quarter(),Number=str(portfolio_id.Number),Mfr_Name=portfolio_id.Mfr_Name,Ownership=portfolio_id.Ownership,Mfr_Part_Number=portfolio_id.Mfr_Part_Number,cm='JPE').exclude(cm='Global').values(*columns).to_dataframe()
    #print(portfolio)
    #print(portfolio2)
    portfolio_bak=portfolio.copy()
    portfolio2_bak=portfolio2.copy()
    portfolio_bak['unique_field']=portfolio_bak['Mfr_Name'].astype(str)+'###'+portfolio_bak['Number'].astype(str)+'###'+portfolio_bak['Mfr_Part_Number'].astype(str)+'###'+portfolio_bak['Ownership'].astype(str)
    portfolio2_bak['unique_field']=portfolio2_bak['Mfr_Name'].astype(str)+'###'+portfolio2_bak['Number'].astype(str)+'###'+portfolio2_bak['Mfr_Part_Number'].astype(str)+'###'+portfolio2_bak['Ownership'].astype(str)

    #portfolio_global_bak=portfolio_bak.append(portfolio2_bak,ignore_index=True)
    portfolio_global_bak = pd.concat([portfolio2_bak,portfolio_bak],ignore_index=True)
    portfolio_global_bak.drop(join_field[1:],axis=1,inplace=True)
    #print(portfolio_global_bak)
    if not portfolio_global_bak.empty:
        portfolio['unique_field']=portfolio['Mfr_Name'].astype(str)+'###'+portfolio['Number'].astype(str)+'###'+portfolio['Mfr_Part_Number'].astype(str)+'###'+portfolio['Ownership'].astype(str)
        portfolio2['unique_field']=portfolio2['Mfr_Name'].astype(str)+'###'+portfolio2['Number'].astype(str)+'###'+portfolio2['Mfr_Part_Number'].astype(str)+'###'+portfolio2['Ownership'].astype(str)
        # portfolio['file_from']='SGD'
        # portfolio2['file_from']='JPE'
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
            try:
                place_fgn=cm_list.index('FGN')
                fgn_price=round(price_list[place_fgn],5)
            except:
                fgn_price='-'
            try:
                place_hbg=cm_list.index('HBG')
                hbg_price=round(price_list[place_hbg],5)
            except:
                hbg_price='-'
            try:
                place_jsj=cm_list.index('JSJ')
                jsj_price=round(price_list[place_jsj],5)
            except:
                jsj_price='-'
            try:
                place_jmx=cm_list.index('JMX')
                jmx_price=round(price_list[place_jmx],5)
            except:
                jmx_price='-'
            data=f'{sgd_price}/{jpe_price}/{fgn_price}/{hbg_price}/{jsj_price}/{jmx_price}'
            return data.replace('None','-')
        def po_delivery(s):
            '''
            Po / Delivery logic based on the max count in the group_by values if PO count is greater than delivery then it
            will return po else it will return Delivery and vice versa,if equal it will be PO
            '''
            po_count=(s == 'PO').sum()
            Delivery_count=(s == 'Delivery').sum()
            if Delivery_count>po_count:
                return 'Delivery'
            else:
                return 'PO'
        #portfolio_global=portfolio.append(portfolio2,ignore_index=True)
        portfolio_global = pd.concat([portfolio2,portfolio],ignore_index=True)
        portfolio_global=portfolio_global.groupby('unique_field').agg(
            {
            # "cm_Quantity_Buffer_On_Hand":'sum',
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
             "Original_PO_Delivery_sent_by_Mexico":po_delivery,
            "file_from":concat_cm
            }
        )
        portfolio_global.columns = [
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
                'Original_PO_Delivery_sent_by_Mexico',
                "file_from",
        ]
        def po_delivery_cal(Original_PO_Delivery_sent_by_Mexico,Delivery_Based_Total_OH_sum_OPO_this_quarter,PO_Based_Total_OH_sum_OPO,CQ_ARIS_FQ_sum_1_SANM_Demand,CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand):
            '''This will return a value by calucluating 
            if its po (PO_Based_Total_OH_sum_OPO-(CQ_ARIS_FQ_sum_1_SANM_Demand+CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand))
            if its delivery PO_Based_Total_OH_sum_OPO-(CQ_ARIS_FQ_sum_1_SANM_Demand+CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
            '''
            if not str(CQ_ARIS_FQ_sum_1_SANM_Demand).isdigit():
                CQ_ARIS_FQ_sum_1_SANM_Demand=0
            if not str(CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand).isdigit():
                CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand=0
            if Original_PO_Delivery_sent_by_Mexico == 'PO':
                data=PO_Based_Total_OH_sum_OPO-(CQ_ARIS_FQ_sum_1_SANM_Demand+CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
            else:
                data=Delivery_Based_Total_OH_sum_OPO_this_quarter-(CQ_ARIS_FQ_sum_1_SANM_Demand+CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
            #print('po_delivery_cal',data)


            return data
        portfolio_global = portfolio_global.reset_index()
        portfolio_global['sgd_jpe_cost']=portfolio_global.apply(lambda x:order(x.std_cost,x.file_from),axis=1)
        portfolio_global['Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista']=portfolio_global.apply(lambda x:po_delivery_cal(x.Original_PO_Delivery_sent_by_Mexico,x.Delivery_Based_Total_OH_sum_OPO_this_quarter,x.PO_Based_Total_OH_sum_OPO,x.CQ_ARIS_FQ_sum_1_SANM_Demand,x.CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand),axis=1)
        del portfolio_global['std_cost']
        del portfolio_global['file_from']
        portfolio_global.fillna(0,inplace=True)
        

        #print('global')

        portfolio_global_final=portfolio_global_bak.merge(portfolio_global,on='unique_field')
        portfolio_global_final.drop_duplicates(subset=['unique_field'],inplace=True )
        portfolio_global_final.drop(['unique_field'],axis=1,inplace=True)
        portfolio_global_final['cm']='Global'
        portfolio_global_final['cm_Part_Number']=''
        
        if offcycle:
            portfolio_global_final['offcycle']=True
        else:
            portfolio_global_final['offcycle']=False
        portfolio_global_final['Team']=portfolio_id.Team
        portfolio_global_final['refreshed_on']=timezone.localtime(timezone.now())
        for index, row in portfolio_global_final.iterrows():
            data,created=Portfolio.objects.get_or_create(Number=str(row['Number']),Mfr_Name=row['Mfr_Name'],Mfr_Part_Number=row['Mfr_Part_Number'],cm='Global',Ownership=row['Ownership'],Quarter=Current_quarter())
            if created:
                row['refreshed_comment']='Added'
            Portfolio.objects.filter(id=data.id).update(**row.to_dict())
    else:
        #print('Deleting global....')
        global_folio=Portfolio.objects.filter(Number=str(portfolio_id.Number),Mfr_Name=portfolio_id.Mfr_Name,Mfr_Part_Number=portfolio_id.Mfr_Part_Number,cm='Global',Ownership=portfolio_id.Ownership,Quarter=Current_quarter())
        RFX.objects.filter(portfolio__in=global_folio).delete()
        global_folio.delete()
def top_dist(x):
    '''return the first object from the list '''
    try:return x[0]
    except:return None

def distributor_selection(request):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    This function will return a html string of the table.
    we get the parts from request.session['current_filtered_portfolio'] or request.session['Check_box_portfolio']
    and fetch the distributors based on the user and users supplier page.
    Created a table with check box for the ditributor columns with the quote data.
    |partnumber|dist1|dist2 |dist3 |
    |asy-xxx-12|     |raised|      |
    |asy-xxx-13|  o  |raised|raised|
    |asy-xxx-14|  o  |   o  |raised|
    The example shown above is the required output in UI
    o=checkbox(selectable)
    empty=Dist not found for that part
    raised=Quote raised for the parts already

    '''
    Team=request.GET.get('Team','CMM Team')
    #print(Team)
    current_part=request.session['current_filtered_portfolio']
    selected_part=request.session['Check_box_portfolio']
    selected_part=current_part if selected_part==[] else selected_part
    portfolio_data=Portfolio.objects.filter(id__in=check_rfx_global(selected_part),Quarter=Current_quarter())
    if request.user.is_superuser:
        user_owner=User.objects.annotate(full_name=Concat('first_name', V(' '),'last_name')).filter(full_name__in=portfolio_data.values_list('Arista_PIC',flat=True))
        supplier_data=suppliers_detail.objects.filter(User_created__in=user_owner,is_active=True,user_model__is_active=True,Supplier_Name__in=portfolio_data.values_list('Mfr_Name',flat=True)).filter(Distributor__isnull=False).exclude(Distributor__exact='').distinct('Supplier_Name','Distributor').values('Supplier_Name','Distributor','Team').to_dataframe()
    else:
        supplier_data=suppliers_detail.objects.filter(User_created=request.user,is_active=True,user_model__is_active=True,Supplier_Name__in=portfolio_data.values_list('Mfr_Name',flat=True)).filter(Distributor__isnull=False).exclude(Distributor__exact='').distinct('Supplier_Name','Distributor').values('Supplier_Name','Distributor','Team').to_dataframe()
    #print(supplier_data)

    supplier_data['Distributor']=supplier_data['Distributor']
    data=portfolio_data.values('Number','Mfr_Name','cm').to_dataframe()
    
    
    data_dict=portfolio_data.values('Number','id','cm','Mfr_Name').to_dataframe().to_dict('record')
    # data_dict={x['Number']:x['id'] for x in data_dict}
    
    data_dict={f"{x['cm']}__{x['Number']}__{x['Mfr_Name']}":x['id'] for x in data_dict}
    data=data.merge(supplier_data,right_on='Supplier_Name',left_on='Mfr_Name',how='inner')
    
    data.dropna(subset=['Distributor'],inplace=True)
    data['value']=data['Distributor']
    # print(data)
    # print(data_dict,'data_dictdata_dictdata_dictdata_dictdata_dictdata_dict')
    def get_cell(x):
        '''returns a data for a hml table cell with html tags'''
        Number=data.loc[x.index.values[0],'Number']
        cm=data.loc[x.index.values[0],'cm']
        Mfr_Name=data.loc[x.index.values[0],'Mfr_Name']
        quote_stat=[]
        Quote_details=find_partial_quote(Portfolio.objects.get(id=data_dict.get(f"{cm}__{Number}__{Mfr_Name}")),to_cal=True)
        quote_stat=Quote_details['sent_dist']
        quote_stat_q=Quote_details['sent_dist_q']
        status=[]
        # print(x,Number,cm,'sent_dist_qsent_dist_qsent_dist_q')
        if not x.empty and  x.to_list()[0] in quote_stat:
            # print(quote_stat,'quote_statquote_statquote_statquote_stat')
            status.append('Raised for Q+1')
        if not x.empty and  x.to_list()[0] in quote_stat_q:
            status.append('Raised for Q ')
        # cell=f""" <input style='width:100%' type='checkbox' checked='checked' class='distributor_selection_checkbox {x.to_list()[0].replace(' ','_')}_cb' id='{x.index.values[0]}'  value='{x.to_list()[0]}' name='{cm}__{Number}' /> """ if not x.empty and not x.to_list()[0] in quote_stat else ('Quote Raised' if not x.empty else '')
        if len(status)>=2:
            cell="""Raised for Q+1 and Q """
        else:
            cell='<br>'.join(status)+f""" <br><input style='width:100%' type='checkbox' checked='checked' class='distributor_selection_checkbox {x.to_list()[0].replace(' ','_')}_cb' id='{x.index.values[0]}'  value='{x.to_list()[0]}' name='{cm}__{Number}' /> """ 
        
        return cell
    try:
        data['unique']=data['Number']+'##########'+data['Mfr_Name']+'##########'+data['cm']
        # data=pd.pivot_table(data,values='value',index=['unique'],columns=['Distributor'],aggfunc=lambda x:f""" <input style='width:100%' type='checkbox' checked='checked' class='distributor_selection_checkbox' id='{x.index.values[0]}'  value='{x.to_list()[0]}' name='{data.loc[x.index.values[0],'Number']}' />  <label for="{x.index.values[0]}">{x.to_list()[0]}</label>""" if not x.empty else '')
        data=pd.pivot_table(data,values='value',index=['unique'],columns=['Distributor'],aggfunc=lambda x:get_cell(x))
        data.columns = [''.join(col).strip() for col in data.columns.values]
        data.columns=[f'''
        {x}<br><button  type=button class='header_cb btn btn-sm btn-info' onclick="check_all_with_row(this,'{x.replace(' ','_')}','check')"><i class="fa fa-check-circle"></i></button>
        <button  type=button class='header_cb btn btn-sm btn-danger' onclick="check_all_with_row(this,'{x.replace(' ','_')}','uncheck')"><i class="fa fa-minus-circle"></i></button>
        ''' for x in data.columns]
        data = data.reset_index()
        data[f'''
        <input type="text" class="form-control input CM_search " placeholder="Search CM Site" /> <br>
        CM Site''']=data['unique'].str.split('##########').str[2]
        data[f'''
        <input type="text" class="form-control input mfr_search " placeholder="Search MFR" /> <br>
        Mfr Name''']=data['unique'].str.split('##########').str[1]
        data[f'''
        <input type="text" class="form-control input APN_search " placeholder="Search Part" /> <br>
        APN''']=data['unique'].str.split('##########').str[0]
        del data['unique']
        data=data.filter(data.columns.to_list()[::-1])
        data.fillna('-',inplace=True)

        data=data.to_html(
            index=False,
            escape=False,
            table_id='distributor_selection_table',
            border=0,
            classes='table table-xs font-small-1 text-nowrap  table-condensed table-striped table-bordered distributor_selection_table_class',
            justify='center')
    except Exception as e:
        tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        #print(tb_str)
        data='<h2>No Distributor found for the selected Parts<h2>'
    #print(data)
    return render(request,'portfolio/components/distributor_selection.html',{'data':data})


@multi_threading
def non_avl_notified_mail(request, pic_list):
    '''
    This method send notification while adding non avl parts
    '''
    try:
        if len(pic_list) != 0:
            bp_email = list(User.objects.filter(groups__name='Super User').values_list('email', flat=True))
            subject = "NON AVL portfolio is refreshed"
            for i in pic_list:
                to = list(User.objects.filter(first_name=i.split('/')[0].split(' ')[0], last_name=i.split('/')[0].split(' ')[1]).values_list('email', flat=True))
                message = get_template('email/portfolio/add_parts_avl.html').render({
                                                                                    'arista_pic':i,
                                                                                    'email_from':settings.EMAIL_HOST_USER, 
                                                                                    'production_url':settings.PRODUCTION,
                                                                                    'server_url': settings.SERVER_TYPE,
                                                                                    'cc':list(set(bp_email)),
                                                                                    'to':to,
                                                                                    'subject':subject})
                if settings.SERVER_TYPE == settings.PRODUCTION:
                    msg = EmailMessage(subject, message, to=to, cc=list(set(bp_email+['sathya.narayanan@arista.com'])))
                    
                else:
                    msg = EmailMessage(subject, message, to=['skarthick@inesssolutions.com'], cc=['sathya.narayanan@arista.com'])
            
                msg.content_subtype = 'html'
                msg.send()
                LOGGER.info("Non avl parts added notification details send to %s", i)
    except Exception as e:
        LOGGER.error("Unable to send Non avl notification details",exc_info=1)    
def agile_refresh(request=None):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    this is user side trigger for agile_refresh_worker which can trigger all parts to refresh or single part
    '''
    portfolio_instance=None

    porfolio_id=request.POST.get('porfolio_id',None)
    if porfolio_id:
        instance=Portfolio.objects.get(id=int(porfolio_id))
        portfolio_instance=Portfolio.objects.filter(Number=instance.Number,cm=instance.cm,Quarter=instance.Quarter)
    agile_refresh_worker_threaded(portfolio_instance,request)
    if portfolio_instance:
        return JsonResponse({'message':f'Agile data is updating for {portfolio_instance[0].Number}'})
    else:
        return JsonResponse({'message':'Agile data is updating...'})

@multi_threading
def agile_refresh_worker_threaded(portfolio_parts=None,request=None):
    agile_refresh_worker(portfolio_parts,request)
    

def agile_refresh_worker(portfolio_parts=None,request=None):
    '''
    Type:Static Function
    Arg:request
    ####process#####:
    this will refresh the data which fetched from agile based on the input value in portfolio_parts
    Updated fields from Agile: Lifecycle_Phase,Rev,Item_Desc,Mfr_Name,Mfr_Part_Lifecycle_Phase,Mfr_Part_Number,Qualification_Status

    '''
    bulk=[]
    new_bulk=[]
    new_bulk_id=[]
    bulk_deleted=[]
    bulk_updated=[]

    if portfolio_parts:
        current_portfolio=portfolio_parts
    else:
        current_portfolio=Portfolio.objects.filter(Quarter=Current_quarter())
        #print(current_portfolio)
    agile_data=DimAgileAmpartMfrIness.objects.using('inputdb').filter(ampart__in=list(current_portfolio.distinct('Number').values_list('Number',flat=True))).to_dataframe()
    agile_data['unique']=agile_data['ampart'].astype(str)+'####'+agile_data['mfr_name'].astype(str)+'####'+agile_data['mfr_part_number'].astype(str)
    for portfolio in current_portfolio:
        
        agile_parts=agile_data.loc[
            (agile_data.ampart == portfolio.Number) & (agile_data.mfr_name == portfolio.Mfr_Name) & (agile_data.mfr_part_number==portfolio.Mfr_Part_Number)
            ]
         ####portfolio creation new
        

        if not agile_parts.empty:
            if portfolio.Lifecycle_Phase!=agile_parts.iloc[0].ampart_lifecycle or portfolio.Rev!=agile_parts.iloc[0].ampart_rev or portfolio.Item_Desc!=agile_parts.iloc[0].ampart_desc or portfolio.Mfr_Name!=agile_parts.iloc[0].mfr_name or portfolio.Mfr_Part_Lifecycle_Phase!=agile_parts.iloc[0].mfr_lifecycle_phase or portfolio.Mfr_Part_Number!=agile_parts.iloc[0].mfr_part_number or portfolio.Qualification_Status!=agile_parts.iloc[0].mfr_qualification_status:
                portfolio.Lifecycle_Phase=agile_parts.iloc[0].ampart_lifecycle
                portfolio.Rev=agile_parts.iloc[0].ampart_rev
                portfolio.Item_Desc=agile_parts.iloc[0].ampart_desc
                portfolio.Mfr_Name=agile_parts.iloc[0].mfr_name
                portfolio.Mfr_Part_Lifecycle_Phase=agile_parts.iloc[0].mfr_lifecycle_phase
                portfolio.Mfr_Part_Number=agile_parts.iloc[0].mfr_part_number
                portfolio.Qualification_Status=agile_parts.iloc[0].mfr_qualification_status
                portfolio.refreshed_comment='Updated'

                portfolio.refreshed_on=timezone.localtime(timezone.now())
                portfolio.save()
                bulk_updated.append(portfolio)
                #print(portfolio.Number)
            else:
                portfolio.refreshed_comment='No Change'
                portfolio.refreshed_on=timezone.localtime(timezone.now())
                portfolio.save()
                bulk.append(portfolio)
                #print(f'No Change in {portfolio.Number}')
                pass
        else:
            #print('deleted')
            if portfolio.refreshed_comment!='Deleted from Agile':
                portfolio.refreshed_comment='Deleted from Agile'
                portfolio.refreshed_on=timezone.localtime(timezone.now())
                portfolio.save()

                bulk_deleted.append(portfolio.id)

        if portfolio.cm!='Global':
            new_parts=agile_data.loc[agile_data.ampart == portfolio.Number].loc[~agile_data.unique.isin(list(current_portfolio.filter(cm=portfolio.cm,Number=portfolio.Number).annotate(unique=Concat('Number', V('####'), 'Mfr_Name', V('####'),'Mfr_Part_Number')).values_list('unique',flat=True)))]
            #print(new_parts)
            for index,new_part in new_parts.iterrows():
                new_port=Portfolio.objects.get(id=portfolio.id) 
                new_port.id=None
                new_port.pk=None
                new_port.Mfr_Part_Number=new_part.mfr_part_number
                new_port.Rev=new_part.ampart_rev
                new_port.Item_Desc=new_part.ampart_desc
                new_port.Mfr_Name=new_part.mfr_name
                new_port.Mfr_Part_Lifecycle_Phase=new_part.mfr_lifecycle_phase
                new_port.Qualification_Status=new_part.mfr_qualification_status
                new_port.refreshed_comment='Auto Added'
                new_port.file_from=portfolio.file_from
                new_port.save()
                new_bulk.append(new_port)

    # updated_portfolio=Portfolio.objects.bulk_update(bulk_updated,fields=[
    #     "Lifecycle_Phase",
    #     "Rev",
    #     "Item_Desc",
    #     "Mfr_Name",
    #     "Mfr_Part_Lifecycle_Phase",
    #     "Mfr_Part_Number",
    #     "Qualification_Status",
    #     "refreshed_comment",
    #     "refreshed_on",
    # ],batch_size=1000) or []
    # print(updated_portfolio)
    # Portfolio.objects.bulk_update(bulk,fields=[
    #     "Lifecycle_Phase",
    #     "Rev",
    #     "Item_Desc",
    #     "Mfr_Name",
    #     "Mfr_Part_Lifecycle_Phase",
    #     "Mfr_Part_Number",
    #     "Qualification_Status",
    #     "refreshed_comment",
    #     "refreshed_on",
    # ],batch_size=1000)
    # created_=Portfolio.objects.bulk_create(new_bulk,batch_size=1000,ignore_conflicts=True) or []
    created_=new_bulk

    for x in new_bulk:
        create_global(None,x,False)
    new_df=Portfolio.objects.filter(id__in=[x.id for x in created_]).values(
        "Number",
        "Lifecycle_Phase",
        "Rev",
        "Item_Desc",
        "Mfr_Name",
        "Mfr_Part_Lifecycle_Phase",
        "Mfr_Part_Number",
        "Qualification_Status",
        "refreshed_comment",
        ).to_dataframe() 
    deleted_df=Portfolio.objects.filter(id__in=bulk_deleted).values(
        "Number",
        "Lifecycle_Phase",
        "Rev",
        "Item_Desc",
        "Mfr_Name",
        "Mfr_Part_Lifecycle_Phase",
        "Mfr_Part_Number",
        "Qualification_Status",
        "refreshed_comment",
    ).to_dataframe() 
    updated_df=Portfolio.objects.filter(id__in=[x.id for x in bulk_updated]).values(
        "Number",
        "Lifecycle_Phase",
        "Rev",
        "Item_Desc",
        "Mfr_Name",
        "Mfr_Part_Lifecycle_Phase",
        "Mfr_Part_Number",
        "Qualification_Status",
        "refreshed_comment",
    ).to_dataframe() 

    if deleted_df.empty==False or new_df.empty==False or  updated_df.empty==False :
        if settings.SERVER_TYPE == settings.PRODUCTION:
            if request:
                email = [request.user.email]
            else:
                email = list(User.objects.filter(groups__name__in=['BP Team',
                    'GSM Manager',]).values_list('email',flat=True))
                email.append('sathya@inesssolutions.com')

            
        else:
            email =['skarthick@inesssolutions.com','sathya@inesssolutions.com']

        msg=EmailMessage(subject='MPAT Automatic weekly Agile Refresh',body=f''' 
Hello Arista Team,



{'Arista MPAT portfolio data has been refreshed Manually for the selected part,' if portfolio_parts else 'MPAT portfolio data has been automatically refreshed with recent Agile information over the weekend.' }



Please find attached excel to identify the list of parts which are updated, deleted and added in the recent Agile refresh.

Kindly raise RFQ in MPAT for the newly added parts.

Regards,

ARISTA MASTER PRICING AUTOMATION TOOL
        
        '''.replace('\n','<br>'),from_email=f'Portfolio Auto Refresh <srv-masterpricing@arista.com>', to=email)
        msg.content_subtype = 'html'
        if new_df.empty==False:
            msg.attach('New Parts.xlsx',df_to_excel_b(new_df.drop_duplicates(subset=['Lifecycle_Phase','Mfr_Name','Mfr_Part_Number'],)), 'application/ms-excel')
        if deleted_df.empty==False:
            msg.attach('deleted from agile.xlsx',df_to_excel_b(deleted_df.drop_duplicates(subset=['Lifecycle_Phase','Mfr_Name','Mfr_Part_Number'],)), 'application/ms-excel')
        if updated_df.empty==False:
            msg.attach('Updated Parts.xlsx',df_to_excel_b(updated_df.drop_duplicates(subset=['Lifecycle_Phase','Mfr_Name','Mfr_Part_Number'],)), 'application/ms-excel')
        msg.extra_headers['Message-ID'] = make_msgid()
        status=msg.send()
        #print(status,'mail sent')
            
        
        

def df_to_excel_b(df,):
    #print('df_to_excel_b',df)
    with BytesIO() as b:
        with pd.ExcelWriter(b) as writer:
            df.to_excel(writer, index=False,)
            writer.save()
            file_MIME=b.getvalue()
            return file_MIME

@login_required        
def owners(request):
    qtr = Current_quarter()
    data = Portfolio.objects.raw('''select id,"Number",
        array_to_string(array_agg(distinct "Ownership"),'/') AS Ownership,
        array_to_string(array_agg(distinct "Team"),'/') AS Team,
        array_to_string(array_agg(distinct GSMSGD),',') AS GSMSGD,
        array_to_string(array_agg(distinct GSMJPE),',') AS GSMJPE,
        array_to_string(array_agg(distinct GSMJSJ),',') AS GSMJSJ,
        array_to_string(array_agg(distinct GSMJMX),',') AS GSMJMX,
        array_to_string(array_agg(distinct GSMFGN),',') AS GSMFGN,
        array_to_string(array_agg(distinct GSMHBG),',') AS GSMHBG,
        array_to_string(array_agg(distinct CMMSGD),',') AS CMMSGD,
        array_to_string(array_agg(distinct CMMJPE),',') AS CMMJPE,
        array_to_string(array_agg(distinct CMMJSJ),',') AS CMMJSJ,
        array_to_string(array_agg(distinct CMMJMX),',') AS CMMJMX,
        array_to_string(array_agg(distinct CMMFGN),',') AS CMMFGN,
        array_to_string(array_agg(distinct CMMHBG),',') AS CMMHBG,
        array_to_string(array_agg(distinct PIC),',') AS PIC
        from (Select 1 as id,"Number","Team","Ownership",
            Case When "cm"='SGD' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMSGD,
            Case When "cm"='JPE' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJPE,
            Case When "cm"='JSJ' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJSJ,
            Case When "cm"='JMX' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJMX,
            Case When "cm"='FGN' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMFGN,
            Case When "cm"='HBG' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMHBG,
            Case When "cm"='SGD' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMSGD,
            Case When "cm"='JPE' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJPE,
            Case When "cm"='JSJ' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJSJ,
            Case When "cm"='JMX' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJMX,
            Case When "cm"='FGN' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMFGN,
            Case When "cm"='HBG' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMHBG,
            "Arista_PIC" AS PIC
        From public.portfolio_portfolio
        where "Quarter" = %s and cm != 'Global'
        GROUP BY id,"Number","Team","Ownership") as table1

        GROUP BY id,"Number"''',[qtr])
    
    return render(request,"portfolio/owners.html",context={'quarter':Current_quarter(),'data':data})

def ownerdetails_daily_email():
    qtr = Current_quarter()
    data = Portfolio.objects.raw('''select id,"Number",
        array_to_string(array_agg(distinct "Ownership"),'/') AS Ownership,
        array_to_string(array_agg(distinct "Team"),'/') AS Team,
        array_to_string(array_agg(distinct GSMSGD),',') AS GSMSGD,
        array_to_string(array_agg(distinct GSMJPE),',') AS GSMJPE,
        array_to_string(array_agg(distinct GSMJSJ),',') AS GSMJSJ,
        array_to_string(array_agg(distinct GSMJMX),',') AS GSMJMX,
        array_to_string(array_agg(distinct GSMFGN),',') AS GSMFGN,
        array_to_string(array_agg(distinct GSMHBG),',') AS GSMHBG,
        array_to_string(array_agg(distinct CMMSGD),',') AS CMMSGD,
        array_to_string(array_agg(distinct CMMJPE),',') AS CMMJPE,
        array_to_string(array_agg(distinct CMMJSJ),',') AS CMMJSJ,
        array_to_string(array_agg(distinct CMMJMX),',') AS CMMJMX,
        array_to_string(array_agg(distinct CMMFGN),',') AS CMMFGN,
        array_to_string(array_agg(distinct CMMHBG),',') AS CMMHBG,
        array_to_string(array_agg(distinct PIC),',') AS PIC
        from (Select 1 as id,"Number","Team","Ownership",
            Case When "cm"='SGD' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMSGD,
            Case When "cm"='JPE' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJPE,
            Case When "cm"='JSJ' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJSJ,
            Case When "cm"='JMX' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJMX,
            Case When "cm"='FGN' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMFGN,
            Case When "cm"='HBG' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMHBG,
            Case When "cm"='SGD' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMSGD,
            Case When "cm"='JPE' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJPE,
            Case When "cm"='JSJ' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJSJ,
            Case When "cm"='JMX' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJMX,
            Case When "cm"='FGN' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMFGN,
            Case When "cm"='HBG' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMHBG,
            "Arista_PIC" AS PIC
        From public.portfolio_portfolio
        where "Quarter" = %s and cm != 'Global'
        GROUP BY id,"Number","Team","Ownership") as table1

        GROUP BY id,"Number"''',[qtr])
    df = pd.DataFrame([item.__dict__ for item in data])
    df['pic'] = [get_username(item.pic) for item in data]
    df = df[df.pic.isnull()]
 
    remove_df=df.drop(['_state','id'],axis=1)
    remove_df.rename(columns = {'Number':'APN','ownership':'Ownership','team':'Team','gsmsgd':'GSM-SGD','gsmjpe':'GSM-JPE','gsmjsj':'GSM-JSJ','gsmjmx':'GSM-JMX','gsmfgn':'GSM-FGN','gsmhbg':'GSM-HBG','cmmsgd':'CMM-SGD','cmmjpe':'CMM-JPE','cmmjsj':'CMM-JSJ','cmmjmx':'CMM-JMX','cmmfgn':'CMM-FGN','cmmhbg':'CMM-HBG','pic':'PIC'}, inplace = True)
    
    if not df.empty:
        path=r"media//ownerdetails//"
        currenttimeanddate=datetime.datetime.today().strftime("%d-%m-%Y %H:%M")
  
        name= datetime.datetime.today().strftime("%d-%m-%Y %H:%M")+'-Ownerdetails.xlsx'
        remove_df.to_excel(path+currenttimeanddate+'-Ownerdetails.xlsx',index=False)

        attachment = open(path+currenttimeanddate+'-Ownerdetails.xlsx', "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % name)    
        subject='Owner Details'
        if  settings.SERVER_TYPE == settings.PRODUCTION:
            email_to=['hnguyen@arista.com','maryb@arista.com','cwliaw@arista.com','mamta@arista.com','saragarcia@arista.com']
        else:
            email_to=['skarthick@inesssolutions.com','sathya@inesssolutions.com']

        email=EmailMessage(subject=subject,body=f''' 
Hello BP Team,

PIC Owner mismatch data is listed in the attached excel.


Regards,

ARISTA MASTER PRICING AUTOMATION TOOL
        
        '''.replace('\n','<br>'), to=email_to, cc=['skarthick@inesssolutions.com','sathya@inesssolutions.com'])
        email.content_subtype = 'html'
        #email.attach(filename=name, mimetype='application/vnd.ms-excel')
        email.attach(part)
        email.send()
        
        #return HttpResponse('successfully sent')
    else: 
        print('No Data Available')
        #Wsubject='This quarter No data'
        #email_to=['skarthick@inesssolutions.com','sathya@inesssolutions.com']
        #body='This Quarter has No Data'
        #email=EmailMessage(subject=subject, to=email_to, cc=['skarthick@inesssolutions.com'])
        #email.send()
        #return HttpResponse('successfully 22')



def ownerdetails_monthly_email():
    qtr = Current_quarter()
    data = Portfolio.objects.raw('''select id,"Number",
        array_to_string(array_agg(distinct "Ownership"),'/') AS Ownership,
        array_to_string(array_agg(distinct "Team"),'/') AS Team,
        array_to_string(array_agg(distinct GSMSGD),',') AS GSMSGD,
        array_to_string(array_agg(distinct GSMJPE),',') AS GSMJPE,
        array_to_string(array_agg(distinct GSMJSJ),',') AS GSMJSJ,
        array_to_string(array_agg(distinct GSMJMX),',') AS GSMJMX,
        array_to_string(array_agg(distinct GSMFGN),',') AS GSMFGN,
        array_to_string(array_agg(distinct GSMHBG),',') AS GSMHBG,
        array_to_string(array_agg(distinct CMMSGD),',') AS CMMSGD,
        array_to_string(array_agg(distinct CMMJPE),',') AS CMMJPE,
        array_to_string(array_agg(distinct CMMJSJ),',') AS CMMJSJ,
        array_to_string(array_agg(distinct CMMJMX),',') AS CMMJMX,
        array_to_string(array_agg(distinct CMMFGN),',') AS CMMFGN,
        array_to_string(array_agg(distinct CMMHBG),',') AS CMMHBG,
        array_to_string(array_agg(distinct PIC),',') AS PIC
        from (Select 1 as id,"Number","Team","Ownership",
            Case When "cm"='SGD' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMSGD,
            Case When "cm"='JPE' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJPE,
            Case When "cm"='JSJ' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJSJ,
            Case When "cm"='JMX' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMJMX,
            Case When "cm"='FGN' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMFGN,
            Case When "cm"='HBG' and "Team"='GSM Team' Then "Arista_PIC" Else Null End As GSMHBG,
            Case When "cm"='SGD' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMSGD,
            Case When "cm"='JPE' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJPE,
            Case When "cm"='JSJ' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJSJ,
            Case When "cm"='JMX' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMJMX,
            Case When "cm"='FGN' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMFGN,
            Case When "cm"='HBG' and "Team"='CMM Team' Then "Arista_PIC" Else Null End As CMMHBG,
            "Arista_PIC" AS PIC
        From public.portfolio_portfolio
        where "Quarter" = %s and cm != 'Global'
        GROUP BY id,"Number","Team","Ownership") as table1

        GROUP BY id,"Number"''',[qtr])
    df = pd.DataFrame([item.__dict__ for item in data])
    df['pic'] = [get_username(item.pic) for item in data]
 
    remove_df=df.drop(['_state','id'],axis=1)
    remove_df.rename(columns = {'Number':'APN','ownership':'Ownership','team':'Team','gsmsgd':'GSM-SGD','gsmjpe':'GSM-JPE','gsmjsj':'GSM-JSJ','gsmjmx':'GSM-JMX','gsmfgn':'GSM-FGN','gsmhbg':'GSM-HBG','cmmsgd':'CMM-SGD','cmmjpe':'CMM-JPE','cmmjsj':'CMM-JSJ','cmmjmx':'CMM-JMX','cmmfgn':'CMM-FGN','cmmhbg':'CMM-HBG','pic':'PIC'}, inplace = True)
    if not df.empty:
        path=r"media//ownerdetails//"
        currenttimeanddate=datetime.datetime.today().strftime("%d-%m-%Y %H:%M")
  
        name= datetime.datetime.today().strftime("%d-%m-%Y %H:%M")+'-Ownerdetails.xlsx'
        remove_df.to_excel(path+currenttimeanddate+'-Ownerdetails.xlsx',index=False)

        attachment = open(path+currenttimeanddate+'-Ownerdetails.xlsx', "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % name)    
        subject='Monthly Part Owner Details'
           
        if  settings.SERVER_TYPE == settings.PRODUCTION:
            email_to=['hnguyen@arista.com','maryb@arista.com','cwliaw@arista.com','mamta@arista.com','saragarcia@arista.com']
        else:
            email_to=['skarthick@inesssolutions.com','sathya@inesssolutions.com']
        email=EmailMessage(subject=subject,body=f''' 
Hello BP Team,

PIC Owner data is listed in the attached excel.


Regards,

ARISTA MASTER PRICING AUTOMATION TOOL
        
        '''.replace('\n','<br>'), to=email_to, cc=['skarthick@inesssolutions.com','sathya@inesssolutions.com'])
        email.content_subtype = 'html'
        #email.attach(filename=name, mimetype='application/vnd.ms-excel')
        email.attach(part)
        email.send()
        
        #return HttpResponse('successfully sent')
    else: 
        print('No Data Available')