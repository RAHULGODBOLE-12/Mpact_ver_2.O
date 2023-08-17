'''
from Supplier.views import *
from Supplier import views
'''
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
from django.contrib.auth import (authenticate,
                                get_user_model,
                                login,
                                logout)
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.core import serializers
from django.views.generic.edit import CreateView
from Supplier.models import *
# from CMT.cmt_helper import *
from django.db.models import Q
import pandas as pd
import os
import random
import numpy as np
from io import BytesIO
import pytz
from  django.core.serializers.json import DjangoJSONEncoder
import re
from InputDB.models import *
import logging
LOGGER = logging.getLogger(__name__)
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

@login_required   
def contactlist(request,Team=''):
    user_in_supplier=suppliers_detail.objects.values_list('user_model__id',flat=True)
    ''' Static page to return Html with Supplier name for dropdown.'''
    # User.objects.filter(groups__name='Suppliers/Distributors').exclude(id__in=user_in_supplier).delete()
    # supplierdetail = suppliers_detail.objects.all()
    pics = User.objects.filter(groups__name__in=['GSM Team'])
    mfr_name = DimAgileAmpartMfrIness.objects.values('mfr_name').distinct().using('inputdb')
    return render(request,'Supplier/supplier_contact.html',{'mfr_name':mfr_name,'Team':Team,'pics':pics})

@login_required   
def contactlist_data(request):
    ''' Provides the data for supplier page based on the logins'''
    
    #get the Team from webpage
    Team=request.GET.get('Team')
    
    init=suppliers_detail.objects.all()
    if request.user.is_superuser:
        ##if super user return the all supliers
        init=init
    else:
        ##Data filter:based on User_created(foregin key) and Team
        init=init.filter(User_created=request.user,Team=Team)
    ##require date to serialize
    data = init.values(
            'id',
            'Supplier_Name',
            'Distributor',
            'Arista_Commodity_Manager',
            'Commodity',
            'Contact',
            'Position',
            'Direct',
            'Mobile',
            'Email',
            'Comments',
            'password',
            'user_model__username',
            'modified_by',
            'modified_on',
            'user_model__is_active',
            'is_active',
            'User_created__username',
            'User_created',
    )

    return JsonResponse({'data':list(data)},safe=False)
@error_handle
@login_required
def import_contact(request,action):
    '''
    To Create new Supplier/Distributors
    '''
    ##getting the supplier groups for foregin key
    # supplier_group=Group.objects.get(name='Suppliers/Distributors')
    send_logger_tele(f'''{action}''')
    #predefined column dict for encode and decoding
    column_names={"Supplier_Name":"Supplier Name *",
            "Distributor":"Distributor",
            "Arista_Commodity_Manager":"Arista Commodity Manager",
            "Commodity":"Commodity",
            "Contact":"Contact *",
            "Position":"Position",
            "Direct":"Direct",
            "Mobile":"Mobile",
            "Email":"Email *",
            "Comments":"Comments",
            "user_model__is_active":'Allowed to Login',
            "is_active":'Can Quote',
            }
    if action=='import':
        ##creating with excel (bulk)
        file_input=request.FILES['contact_Excel']
        Team=request.POST.get('Team')
        print(Team,'Team')
        #reading the files
        df=pd.read_excel(file_input)
        df=df.replace({np.nan: None})
        None_email_index=[]
        #decoding the columns
        columns_name_decode={v:k for k,v in column_names.items()}
        df.rename(columns=columns_name_decode,inplace=True)
        #iterate the row
        for index, row in df.iterrows():
            if has_group(request.user,'Iness') :
                createduser=User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).order_by('id')[:1].get()
                createduser=User.objects.get(pk=createduser.id)
            else:
                createduser = request.user
            try:
                #getting if the row has Distributor if not set as NONE
                DISTRIBUTOR=row.get('Distributor') or None
                ##getting the email id as username
                username=row.get('Email')

                if (not username) or (not re.fullmatch(regex, row.get('Email'))):
                    ##used for sending error to user
                    raise ValueError('No email id found')

                try:
                    ##getting the userdetails from supplie table if we have any.
                    supplier=suppliers_detail.objects.get(Supplier_Name=row.get('Supplier_Name'),Email=username,User_created=createduser,Distributor=DISTRIBUTOR)
                except Exception as e:
                    print(e)
                    ##or Create new one
                    supplier=suppliers_detail()
                    created_supplier=True
                ##setting the data respective to the columns
                supplier.Supplier_Name=row['Supplier_Name']
                supplier.Arista_Commodity_Manager=row['Arista_Commodity_Manager']
                supplier.Commodity=row['Commodity']
                supplier.Contact=row['Contact']
                supplier.Position=row['Position']
                supplier.Direct=row['Direct']
                supplier.Mobile=row['Mobile']
                supplier.Email=row['Email']
                supplier.Distributor=DISTRIBUTOR
                supplier.Comments=row['Comments']
                supplier.Team=Team
                if not supplier.User_created or has_group(request.user,'Iness'):
                    ##settting the user who created it if already created just ignore it
                    supplier.User_created=createduser
                supplier.modified_by=request.user.username
                user_created,pasword=supplier.save()
                user=supplier.user_model
                print(user)
                ###notification for supplier
                print(user_created,'user_created')
                ##if the user is newly created,Send Email
#                 if user_created:
#                         send_notification(request,to_mail_id=user.email if str(get_url(request)) in production else 'srinithins@arista.com',user_from='Arista Master Pricing Automation Tool',subject='Credentials created for Arista Master Pricing Automation Tool',body=f''' 
# Hello {user.first_name},
# <br>
# <br>
# <br>
# User credentials for “Arista Master Pricing Automation Tool”  has been created for you. <br>
# Please find your Username and Password as mentioned below. 
# <br>
# <br>

# Username: <b style='color: darkslateblue;'>{user.username}</b><br>
# Password: <b style='color: darkslateblue;' >{pasword}</b><br>
# <br>
# <br>
# Tool Link is https://{get_url(request)}/
# <br>
# <br>
# <br>
# Once logged in, to change the password use this link https://{get_url(request)}/password_change/
# <br>

# <br>
# <br>
# If you have any questions regarding the tool you can send an email to {createduser.first_name} {createduser.last_name} ({createduser.email})
# <br>
# <br>
# <br>
# Regards,
# <br>
# Arista Master Pricing Automation Tool

                    
#                     ''',title=None,from_name='')
#                         print('Created',username)

            except Exception as e :
                tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                print(tb_str)
                send_logger_tele(tb_str)
                LOGGER.error("LOG_MESSAGE", exc_info=1)

                None_email_index.append(index)
        ##creating the Table for error with the raise value appended
        table=df[df.index.isin(None_email_index)].fillna('').to_html(classes='table table-xs text-nowarp font-small-2 table-responsive table-striped')
        print(None_email_index)
        if len(None_email_index)!=0:
            #sending the data to frontend based on the data in HTML formated
            data=f''' 
            <h5> kindly Fill the Mandatory field and re-upload the excel with only that rows this for your reference<br>*Contact person name should not exceed 30 Chars</h5><br>{table}'''
            return JsonResponse({'data':data},safe=False)
        else :
            print('ndndndn')
            data='success'
            return JsonResponse({'data':data},safe=False)

    elif action=='supplier_add':
        '''Supplier creation through form '''
        data=request.POST
        #getting if the row has Distributor if not set as NONE
        DISTRIBUTOR=data.get('Distributor') or None

        Team=data.get('Team')
        created_supplier=None

        if (not data.get('Email')) or (not re.fullmatch(regex, data.get('Email'))):
            #retuning id there is no email id
            return JsonResponse({'message':'Invalid Email','status':5000})
       
        else:
            username=data.get('Email')
            createduser=User.objects.get(pk=data.get('User_created'))
            try:
                if data.get('supplier_id'):
                    id=int(data.get('supplier_id'))
                    supplier=suppliers_detail.objects.get(id=id)
                    supplier.Supplier_Name=data.get('Supplier_Name')
                    supplier.Email=username
                    supplier.Distributor=DISTRIBUTOR
                else:
                    supplier=suppliers_detail.objects.get(Supplier_Name=data.get('Supplier_Name'),Email=username,User_created=request.user,Distributor=DISTRIBUTOR)
            except Exception as e:
                supplier=suppliers_detail()
                created_supplier=True
            supplier.Supplier_Name=data.get('Supplier_Name')
            supplier.Arista_Commodity_Manager=data.get('Arista_Commodity_Manager')
            supplier.Commodity=data.get('Commodity')
            supplier.Contact=data.get('Contact')
            supplier.Position=data.get('Position')
            supplier.Direct=data.get('Direct')
            supplier.Mobile=data.get('Mobile')
            supplier.Email=data.get('Email')
            supplier.Distributor=DISTRIBUTOR
            supplier.Comments=data.get('Comments')
            supplier.Team=data.get('Team')
            if not supplier.User_created or has_group(request.user,'Iness'):
                supplier.User_created=createduser
            supplier.modified_by=request.user.username
            user_created=supplier.save()
            user=supplier.user_model
            print(user)
            ###notification for supplier
            print(user_created,'user_created')
#             if user_created:
#                 #sending mail
#                 send_notification(request,to_mail_id=user.email if str(get_url(request)) in production else 'srinithins@arista.com',user_from='Arista Master Pricing Automation Tool',subject='Credentials created for Arista Master Pricing Automation Tool',body=f''' 
# Hello {user.first_name},
# <br>
# <br>
# <br>
# User credentials for “Arista Master Pricing Automation Tool”  has been created for you. <br>
# Please find your Username and Password as mentioned below. 
# <br>
# <br>

# Username: <b style='color: darkslateblue;'>{user.username}</b><br>
# Password: <b style='color: darkslateblue;' >{pasword}</b><br>
# <br>
# <br>
# Tool Link is https://{get_url(request)}/
# <br>
# <br>
# <br>
# Once logged in, to change the password use this link https://{get_url(request)}/password_change/
# <br>

# <br>
# <br>
# If you have any questions regarding the tool you can send an email to {createduser.first_name} {createduser.last_name} ({createduser.email})
# <br>
# <br>
# <br>
# Regards,
# <br>
# Arista Master Pricing Automation Tool

                    
#                     ''',title=None,from_name='')
#             send_logger_tele('Created')
            if created_supplier:
                return JsonResponse({'message':'New Supplier Created','status':200})
            else:
                return JsonResponse({'message':'Supplier Details Updated','status':200})

            
    elif action=="delete":
        ###removing the supplier
        id=request.GET.get('id')
        print(id,'id')
        supplier=suppliers_detail.objects.get(pk=int(id))
        try:
            #deleteing the supplier from supplier table if only one supplier is assigned for one User(get raise error if there is multiple row)
            user=suppliers_detail.objects.get(user_model=supplier.user_model)
            print(user,'user')
            User.objects.get(id=user.user_model.id).delete()
        except Exception as e:
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        try:
            #if we have more than one suplier or one user we are just deleteing the supplier row,Not deleting the User
            supplier.delete()
            pass
        except:
            LOGGER.error("LOG_MESSAGE", exc_info=1)

        # return HttpResponse('Supplier Deleted')
        return JsonResponse({'status':200},safe=False)
        
    elif action=='access':
        id=request.GET.get('id')
        access=request.GET.get('access')
        print(access)
        ##getting the supplier id
        supplier=suppliers_detail.objects.get(pk=id)
        ##getting th user
        user=User.objects.get(pk=supplier.user_model.id)
        ##logging instance to log supplier
        log=suppliers_detail_log()
        if access=='login_enable':
            ##Allowing the user to login
            log.log='Unblocking User from Login'
            user.is_active=True 
            user.save()
        if access== 'login_disable':
            ##Dis-Allowing the user to login
            log.log='Blocking User from Login'
            user.is_active=False 
            user.save()
        if access=='disable':
            ##disabling the  user only from this supplier and disabling the quote ability
            supplier.is_active=False
            supplier.save()
            log.log='Disabled Quoting'
        if access=='enable':
            ##Enabling the  user only from this supplier and enabling the quote ability
            log.log='Enabled Quoting'
            supplier.is_active=True
            supplier.save()
        log.modified_by=request.user
        log.save()
        ##adding th supplier log to the many to many log
        supplier.logger.add(log)
        supplier.save()
        return HttpResponse('Supplier Deleted')
    
    elif action=='get_log':
        ##getting the logs based on the  supplier and create a table and sending to the frontend 
        id=request.GET.get('id')
        time_zone=request.GET.get('time_zone')
        supplier=suppliers_detail.objects.get(pk=id)
        print(supplier)
        df=supplier.logger.values(
            "modified_by",
            "modified_by__first_name",
            "modified_by__last_name",
            "modified_on",
            "log",
        ).to_dataframe()
        print(df,'df')
        if not df.empty:
            df['modified_by']=df['modified_by__first_name']+' '+df['modified_by__last_name']
            del df['modified_by__first_name']
            del df['modified_by__last_name']
            print(df)
            df['modified_on']=df['modified_on'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(time_zone)).replace(tzinfo=None).strftime("%m/%d/%Y, %H:%M:%S"))
            df.rename(columns={
                "modified_by":'Modified by',
                "modified_on":'Modified on',
                "log":'Log Message',
            },inplace=True)
            table=df.to_html(justify='center', classes='table table-sm font-small-3 table-hover table-striped table-border table-bordered text-nowarp nowarp', border=0, index=False, table_id='log_table_view', na_rep=''),
        else:
            table=''' <h3> No Log Found for this Supplier/Distributor</h3> '''            
        return JsonResponse({'table':table,'supplier_name':supplier.Supplier_Name+', Distributor'+str(supplier.Distributor or ' -' )},safe=False)
    
    elif action=='download':
        ###Make a excel from the supplier tabled based on the Team and User
        Team=request.GET.get('Team')
        print(Team)
        if request.GET.get('blocked'):
            ##downloading only blocked
            df=suppliers_detail.objects.filter(Team=Team).values("Supplier_Name","Distributor","Arista_Commodity_Manager","Commodity","Contact","Position","Direct","Mobile","Email","Comments","user_model__is_active","is_active").to_dataframe()
        else:
            if request.user.is_superuser:
                df=suppliers_detail.objects.filter(Team=Team,user_model__is_active=True).values("Supplier_Name","Distributor","Arista_Commodity_Manager","Commodity","Contact","Position","Direct","Mobile","Email","Comments").to_dataframe()
            else:
                df=suppliers_detail.objects.filter(Team=Team,user_model__is_active=True,User_created=request.user).values("Supplier_Name","Distributor","Arista_Commodity_Manager","Commodity","Contact","Position","Direct","Mobile","Email","Comments").to_dataframe()
            
        df.rename(columns=column_names,inplace=True)
        with BytesIO() as b:
                with pd.ExcelWriter(b) as writer:  
                    df.to_excel(writer,index=False,sheet_name='Supplier')
                    writer.close()
                    response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'inline; filename=Supplier_list.xlsx'
                    return response
                
    elif action=='setdata':
        ###to set change from username to email id use this path "SupplierContact/importdetail/setdata" this will change the supplier email as username
        for user in User.objects.filter(groups__name='Suppliers/Distributors'):
            user.username=user.email
            try:
                user.save()
            except Exception as e:
                print(e)
                user.delete()   
        return JsonResponse({'status':'changed'})         
      
@login_required     
def download_massupload_template(request):
    #returning the Import template
    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Sample_files/')    
    file='Supplier_Mass_Upload_Template.xlsx'
    fs = FileSystemStorage(location=path)
    if fs.exists(f'{file}'):
        fh = fs.open(f'{file}')
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = f'inline; filename={file}'
        return response


    


