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
from portfolio.portfolio import *



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
        cms=['FGN','SGD','JMX','JSJ','JPE']
        print(columns_name,'columns_name')
        return render(request,'portfolio/portfolio.html',context={"columns_name":columns_name,'past_quarter':past_quarter,'cms':cms})
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
        cms=['FGN','SGD','JMX','JSJ','JPE']
            
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
            print(data,'data')
            name=data.modified_by.first_name+' '+data.modified_by.last_name
            status=True
        else:
            name=''
            status=False
        return JsonResponse({'status':status,'name':name},safe=False)

@multi_threading
def render_portfolio_task(request,CM_loc):
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
            parts_created=portfolio_creation(request,CM_loc)
            instance.comments="Portfolio Updated successfully,"
            # send_push_notification(request.user,subject='Success, Portfolio Refresh',text='Portfolio has been refreshed successfully',url='#')
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
            # send_push_notification(request.user,subject='Error in Portfolio Refresh',text='Portfolio refresh Failed, Please check the file.If any help needed contact suppport',url='#')
            LOGGER.error("LOG_MESSAGE", exc_info=1)
            

        # try:
        #     part_all_list=parts_detail.objects.values_list('cpn',flat=True)
        #     qr=Portfolio.objects.filter(Number__in=parts_created).distinct('Number').values_list('Number',flat=True)
        #     bulk=[]
        #     for part in qr:
        #         p=parts_detail.objects.filter(cpn=part)
        #         if p:
        #             p=p[0]
        #             Portfolio.objects.filter(Number=part).update(
        #                 commodity=p.commodity,
        #                 )
        #     send_push_notification(request.user,subject='Success, Parts are assigned',text='Parts have been assigned by as per Part Assigner Page',url='#')
        # except Exception as e:
        #     tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        #     #print(tb_str)

        #     instance.status=False
        #     instance.completed_status=True
        #     instance.save()
        #     LOGGER.error("LOG_MESSAGE", exc_info=1)


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

        CM_loc=request.GET.get('CM_loc')
        print(CM_loc,'aaaa')
        render_portfolio_task(request,CM_loc)
        
        return JsonResponse({'status':'success','message':'Task Started, we will notify you'})
    elif logger_portfolio.objects.filter(completed_status=False).exists():
        return JsonResponse({'status':'error','message':'Another process is running'})
    else:
        return JsonResponse({'status':'error','message':'you have No Permission'})

def get_data(request):
    data=Portfolio.objects.filter(Team="GSM Team",Quarter=Current_quarter()).values('cm','Number','Arista_Part_Number','Mfr_Name')
    return JsonResponse({'data':list(data)},safe=False)


def portfolio_action(request):
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
            
        print(check_box,'check_box')
        #print(request.GET['State'])
        if request.GET['State'] == 'true':
            check_box.append(int(request.GET['id']))

        elif request.GET['State'] == 'false':
            check_box.remove(int(request.GET['id']))
            #print(check_box)
        else:
            pass
        print(check_box,'check_box_2')
        # check_box=list(Portfolio.objects.filter(id__in=check_box,rfq_sent_flag_supplier__icontains='Not Raised').values_list('id',flat=True))
        request.session['Check_box_portfolio']=check_box
        request.session.modified = True
        return JsonResponse({'status':200,'selected':len(request.session['Check_box_portfolio'])},safe=False)