'''
from excel_processor import portfolio
from importlib import *
reload(portfolio)
from excel_processor.portfolio import *
from InputDB.models import *
'''
from InputDB.models import *
# from rfx.views import create_rfx
import json
from io import BytesIO

import pandas as pd
from Slate_CMT.templatetags.cmt_helper import *
import numpy as np
from random import randint
import pyexcel
from portfolio.models import *
import os
from django.contrib.auth.models import User,Group
from django.db.models import Q
from django.utils import timezone
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Value as V
from django.db.models.functions import Concat   


def portfolio_creation(request,CM_loc='SGD'):
    '''
    ######Portfolio Creator######
    Type:Static Function
    Arg:request,date(o),Contract Manufacturer location
    ####process#####:
    1.List the files and Read the first(based on time uploaded) excel from the 'input_files/excel_files/Portfolio_inputs' appending CM name 'SGD' or 'JPE' base on the site,
    2.converting the input file as Dataframe
    3.Fetching the agile data for those parts from DimAgileAmpartMfrIness(model) and create a database
    4.Rename the header of the input files to generic on which is defined in column name 'db_header2'
    5.Make as left join on the input dataframe with agile dataframe
    6.Assign the Team based ont the Arista_PIC Name column based the user in GSM Team and CMM Team
    7.Global Portfolio Creation,
        1.Get the all the parts with IN (partnumber in df) filter from all other CMs eg.if CM='SGD' take parts from JPE ,FGN excluding 'SGD'
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
    8.While saving check if the combination exits is exits update it or create it
    9.On all the above process,we are make another 3 dataframe which
        has parts which are not in agile, successfully saved parts and parts which are unassigned and send those df to the mail id of the creator(took from request)
    10.if the created list has CMM part raise rfq for cm if not ignore
    11.Return the part_list
    12.send the mails


    '''
    refresh_flag=request.GET.get('refresh')

    #print(CM_loc)
    final_list=[]
    this_quarter=Current_quarter()
    previous_quarter=get_previous_quarter()
    next_quarter=get_Next_quarter()
    f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
    gsm_Team=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    f_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('first_name',flat=True)
    l_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('last_name',flat=True)
    gsm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
    gsm_Team.extend(gsm_manager)

    path=os.path.join(settings.BASE_DIR,'input_files/excel_files/Portfolio_inputs')

    if CM_loc=='SGD':
        ###SGD
        files_SGD_path=sorted(os.scandir(f'''{path}/SGD'''), key=lambda t: t.stat().st_mtime)
        files_SGD=[x for x in files_SGD_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and  not x.name.startswith('~$')]
        files_SGD.reverse()
        #print(files_SGD[0].path)
        excel_SGD=pd.ExcelFile(files_SGD[0].path)
        # sheet_SGD=[x for x in excel_SGD.sheet_names if 'Kickstart' in x]
        KICK_SGD=pd.read_excel(excel_SGD,sheet_name=excel_SGD.sheet_names[0])
        #print(KICK_SGD)

        filter_SGD=[
        KICK_SGD.columns[0],   #'Sanmina Part Number',
        KICK_SGD.columns[1],   #'Arista Part Number',
        KICK_SGD.columns[2],   #'Cust. consign (Y/N)',
        KICK_SGD.columns[3],   #'Parts controlled by',
        KICK_SGD.columns[4],   #'Item Desc',
        KICK_SGD.columns[6],   #'LT\n  (in Working 5 business days)',
        KICK_SGD.columns[7],   #'MOQ',
        KICK_SGD.columns[8],   #'Original PO/Delivery sent by Mexico',
        KICK_SGD.columns[10],   #'Sanmina Quantity Buffer On Hand based on April 1',
        KICK_SGD.columns[11],   #'Sanmina Quantity On Hand + CS Inv. based on April 1',
        KICK_SGD.columns[12],   #"Open PO due in CQ2'20 as of April 1",
        KICK_SGD.columns[13],   #"Open PO due in CQ3'20 as of April 1",
        KICK_SGD.columns[14],   #"Delivery Based Total OH + OPO (CQ2'20)",
        KICK_SGD.columns[15],   #"PO Based Total OH + OPO\n  (CQ2’20 & CQ3'20)",
        KICK_SGD.columns[16],   #"CQ2´20 (ARIS) / FQ3'20 (SANM) Demand as of April 1",
        KICK_SGD.columns[17],   #"CQ3'20 (ARIS) / FQ4'20 (SANM) Demand as of April 1",
        KICK_SGD.columns[18],   #"CQ4'20 (ARIS) / FQ1'21 (SANM) Demand as of April 1",
        KICK_SGD.columns[19],   #"CQ1'21 (ARIS) / FQ2'20 (SANM) Demand as of April 1",
        KICK_SGD.columns[20],   #"Delta = OH & Open PO - DD (CQ2'20 + CQ3´20-Arista)",
        KICK_SGD.columns[21],   #"ARIS - CQ2'20/ SANM - FQ3'20 unit price (USD) / Current std.",
        KICK_SGD.columns[22],   #"CQ3'20 (ARIS) / FQ4'20 (SANM) unit price (USD)",
        KICK_SGD.columns[23],   #"Delta \n ARIS CQ3'20 SANM FQ4'20 \nvs ARIS - CQ2'20 SANM FQ3'20",
        KICK_SGD.columns[26],   #'Blended AVG. PO Receipt Price (Jan-Mar 20)',
        KICK_SGD.columns[40],   #"(CQ3'20)\n  Ownership",
        KICK_SGD.columns[41],   #"(CQ3'20)\n  Arista PIC",
        ]
        KICK_SGD=KICK_SGD.filter(filter_SGD)
    if CM_loc=='JPE':
        ##JPE
        files_JPE_path=sorted(os.scandir(f'''{path}/JPE'''), key=lambda t: t.stat().st_mtime)
        files_JPE=[x for x in files_JPE_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_JPE.reverse()
        excel_JPE=pd.ExcelFile(files_JPE[0].path)

        KICK_JPE=pd.read_excel(excel_JPE,sheet_name=excel_JPE.sheet_names[0])
        #print(KICK_JPE) 
        
        filter_JPE=[
            KICK_JPE.columns[0],  #'JPN'
            KICK_JPE.columns[1],  #'APN'
            KICK_JPE.columns[2],  #'Cust. consign (Y/N)'
            KICK_JPE.columns[39],  #"Ownership (Q1'20)"
            KICK_JPE.columns[4],  #'Item Desc'
            KICK_JPE.columns[9],  #'LT in Weeks/7day calendar'
            KICK_JPE.columns[10],  #'MOQ'
            KICK_JPE.columns[13],  #'Delivery / PO'
            KICK_JPE.columns[15],  #'JPE Quantity on hand'
            KICK_JPE.columns[15],  #'JPE Quantity on hand'
            KICK_JPE.columns[16],  #"Open PO due in Q4'19"
            KICK_JPE.columns[17],  #"Open PO due in Q1'20"
            KICK_JPE.columns[18],  #'Total OH + OPO (Q4 only)'
            KICK_JPE.columns[19],  #'Total OH + OPO (Q4 & Q1)'
            KICK_JPE.columns[20],  #"Q4'19 Demand"
            KICK_JPE.columns[21],  #"Q1'20 Demand"
            KICK_JPE.columns[22],  #"Q2'20 Demand"
            KICK_JPE.columns[23],  #'Unnamed: 23'
            KICK_JPE.columns[24],  #'Delta = OH & Open PO - DD'
            KICK_JPE.columns[26],  #"Q4'19 unit price (USD)"
            KICK_JPE.columns[27],  #"Q1'20unit price (USD)"
            KICK_JPE.columns[28],  #'Delta = Q120 - Q419'
            KICK_JPE.columns[31],  #'Unnamed: 29'
            KICK_JPE.columns[39],  #"Ownership (Q1'20)"
            KICK_JPE.columns[40],  #"Arista PIC (Q1'20)
        ]
        KICK_JPE[KICK_JPE.columns[31]]=0
        KICK_JPE=KICK_JPE.filter(filter_JPE)
    
    if CM_loc=='JSJ':
        ##JSJ
        files_JSJ_path=sorted(os.scandir(f'''{path}/JSJ'''), key=lambda t: t.stat().st_mtime)
        files_JSJ=[x for x in files_JSJ_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_JSJ.reverse()
        excel_JSJ=pd.ExcelFile(files_JSJ[0].path)
        # sheet_JSJ=[x for x in excel_JSJ.sheet_names if 'MasterFile (initial)' in x]
        KICK_JSJ=pd.read_excel(excel_JSJ,sheet_name=excel_JSJ.sheet_names[0])
        #print(KICK_JSJ) 
        
        filter_JSJ=[
            KICK_JSJ.columns[0],  #'JPN'
            KICK_JSJ.columns[1],  #'APN'
            KICK_JSJ.columns[2],  #'Cust. consign (Y/N)'
            KICK_JSJ.columns[35],  #"Ownership (Q1'20)"
            KICK_JSJ.columns[4],  #'Item Desc'
            KICK_JSJ.columns[9],  #'LT in Weeks/7day calendar'
            KICK_JSJ.columns[10],  #'MOQ'
            KICK_JSJ.columns[9],  #'Delivery / PO'
            KICK_JSJ.columns[11],  #'JSJ Quantity on hand'
            KICK_JSJ.columns[11],  #'JSJ Quantity on hand'
            KICK_JSJ.columns[12],  #"Open PO due in Q4'19"
            KICK_JSJ.columns[13],  #"Open PO due in Q1'20"
            KICK_JSJ.columns[14],  #'Total OH + OPO (Q4 only)'
            KICK_JSJ.columns[15],  #'Total OH + OPO (Q4 & Q1)'
            KICK_JSJ.columns[16],  #"Q4'19 Demand"
            KICK_JSJ.columns[17],  #"Q1'20 Demand"
            KICK_JSJ.columns[18],  #"Q2'20 Demand"
            KICK_JSJ.columns[19],  #'Unnamed: 23'
            KICK_JSJ.columns[20],  #'Delta = OH & Open PO - DD'
            KICK_JSJ.columns[22],  #"Q4'19 unit price (USD)"
            KICK_JSJ.columns[23],  #"Q1'20unit price (USD)"
            KICK_JSJ.columns[24],  #'Delta = Q120 - Q419'
            KICK_JSJ.columns[31],  #'Unnamed: 29'
            KICK_JSJ.columns[35],  #"Ownership (Q1'20)"
            KICK_JSJ.columns[36],  #"Arista PIC (Q1'20)
        ]
        KICK_JSJ[KICK_JSJ.columns[31]]=0
        KICK_JSJ=KICK_JSJ.filter(filter_JSJ)
    
    if CM_loc=='JMX':
        ##JMX
        files_JMX_path=sorted(os.scandir(f'''{path}/JMX'''), key=lambda t: t.stat().st_mtime)
        files_JMX=[x for x in files_JMX_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_JMX.reverse()
        excel_JMX=pd.ExcelFile(files_JMX[0].path)
        # sheet_JMX=[x for x in excel_JMX.sheet_names if 'MasterFile (initial)' in x]
        KICK_JMX=pd.read_excel(excel_JMX,sheet_name=excel_JMX.sheet_names[0])
        #print(KICK_JMX) 
        
        filter_JMX=[
            KICK_JMX.columns[0],  #'JPN'
            KICK_JMX.columns[1],  #'APN'
            KICK_JMX.columns[2],  #'Cust. consign (Y/N)'
            KICK_JMX.columns[35],  #"Ownership (Q1'20)"
            KICK_JMX.columns[4],  #'Item Desc'
            KICK_JMX.columns[9],  #'LT in Weeks/7day calendar'
            KICK_JMX.columns[10],  #'MOQ'
            KICK_JMX.columns[9],  #'Delivery / PO'
            KICK_JMX.columns[11],  #'JMX Quantity on hand'
            KICK_JMX.columns[11],  #'JMX Quantity on hand'
            KICK_JMX.columns[12],  #"Open PO due in Q4'19"
            KICK_JMX.columns[13],  #"Open PO due in Q1'20"
            KICK_JMX.columns[14],  #'Total OH + OPO (Q4 only)'
            KICK_JMX.columns[15],  #'Total OH + OPO (Q4 & Q1)'
            KICK_JMX.columns[16],  #"Q4'19 Demand"
            KICK_JMX.columns[17],  #"Q1'20 Demand"
            KICK_JMX.columns[18],  #"Q2'20 Demand"
            KICK_JMX.columns[19],  #'Unnamed: 23'
            KICK_JMX.columns[20],  #'Delta = OH & Open PO - DD'
            KICK_JMX.columns[22],  #"Q4'19 unit price (USD)"
            KICK_JMX.columns[23],  #"Q1'20unit price (USD)"
            KICK_JMX.columns[24],  #'Delta = Q120 - Q419'
            KICK_JMX.columns[31],  #'Unnamed: 29'
            KICK_JMX.columns[35],  #"Ownership (Q1'20)"
            KICK_JMX.columns[36],  #"Arista PIC (Q1'20)
        ]
        KICK_JMX[KICK_JMX.columns[31]]=0
        KICK_JMX=KICK_JMX.filter(filter_JMX)

    if CM_loc=='FGN':
        ##FGN
        files_FGN_path=sorted(os.scandir(f'''{path}/FGN'''), key=lambda t: t.stat().st_mtime)
        files_FGN=[x for x in files_FGN_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_FGN.reverse()
        excel_FGN=pd.ExcelFile(files_FGN[0].path)
        # sheet_FGN=[x for x in excel_FGN.sheet_names if 'MasterFile (initial)' in x]
        KICK_FGN=pd.read_excel(excel_FGN,sheet_name=excel_FGN.sheet_names[0])
        #print(KICK_FGN)
        #print(files_FGN[0].path)
        filter_FGN=[
            KICK_FGN.columns[0],  #'FGN Part Number'
            KICK_FGN.columns[1],  #'APN'
            KICK_FGN.columns[2],  #'Cust. consign (Y/N)'
            KICK_FGN.columns[35],  #"Ownership (Q1'20)"
            KICK_FGN.columns[4],  #'Item Desc'
            # KICK_FGN.columns[9],  #'LT in Weeks/7day calendar' !missing
            # KICK_FGN.columns[10],  #'MOQ'!missing
            KICK_FGN.columns[9],  #'Delivery / PO'
            KICK_FGN.columns[11],  #'FGN Quantity on hand'
            KICK_FGN.columns[11],  #'FGN Quantity on hand'
            KICK_FGN.columns[12],  #"Open PO due in Q4'19"
            KICK_FGN.columns[13],  #"Open PO due in Q1'20"
            KICK_FGN.columns[14],  #'Total OH + OPO (Q4 only)'
            KICK_FGN.columns[15],  #'Total OH + OPO (Q4 & Q1)'
            KICK_FGN.columns[16],  #"Q4'19 Demand"
            KICK_FGN.columns[17],  #"Q1'20 Demand"
            KICK_FGN.columns[18],  #"Q2'20 Demand"
            KICK_FGN.columns[19],  #'Unnamed: 23'
            KICK_FGN.columns[20],  #'Delta = OH & Open PO - DD'
            KICK_FGN.columns[22],  #"Q4'19 unit price (USD)"
            KICK_FGN.columns[23],  #"Q1'20unit price (USD)"
            KICK_FGN.columns[24],  #'Delta = Q120 - Q419'
            KICK_FGN.columns[27],  #'Unnamed: 29'
            KICK_FGN.columns[35],  #"Ownership (Q1'20)"
            KICK_FGN.columns[36],  #"Arista PIC (Q1'20)
        ]

        KICK_FGN=KICK_FGN.filter(filter_FGN)
    
    agile_data=DimAgileAmpartMfrIness.objects.using('inputdb')

    if CM_loc=='HBG':
        ##HBG
        files_HBG_path=sorted(os.scandir(f'''{path}/HBG'''), key=lambda t: t.stat().st_mtime)
        files_HBG=[x for x in files_HBG_path if ((x.name.endswith('xlsx') or x.name.endswith('xls'))) and not x.name.startswith('~$') ]
        files_HBG.reverse()
        excel_HBG=pd.ExcelFile(files_HBG[0].path)
        # sheet_HBG=[x for x in excel_HBG.sheet_names if 'MasterFile (initial)' in x]
        KICK_HBG=pd.read_excel(excel_HBG,sheet_name=excel_HBG.sheet_names[0])
        #print(KICK_HBG)
        #print(files_HBG[0].path)
        filter_HBG=[
            KICK_HBG.columns[0],  #'HBG Part Number'
            KICK_HBG.columns[1],  #'APN'
            KICK_HBG.columns[2],  #'Cust. consign (Y/N)'
            KICK_HBG.columns[35],  #"Ownership (Q1'20)"
            KICK_HBG.columns[4],  #'Item Desc'
            KICK_HBG.columns[31],  #'LT in Weeks/7day calendar' 
            KICK_HBG.columns[30],  #'MOQ'
            KICK_HBG.columns[9],  #'Delivery / PO'
            KICK_HBG.columns[11],  #'HBG Quantity on hand'
            KICK_HBG.columns[11],  #'HBG Quantity on hand'
            KICK_HBG.columns[12],  #"Open PO due in Q4'19"
            KICK_HBG.columns[13],  #"Open PO due in Q1'20"
            KICK_HBG.columns[14],  #'Total OH + OPO (Q4 only)'
            KICK_HBG.columns[15],  #'Total OH + OPO (Q4 & Q1)'
            KICK_HBG.columns[16],  #"Q4'19 Demand"
            KICK_HBG.columns[17],  #"Q1'20 Demand"
            KICK_HBG.columns[18],  #"Q2'20 Demand"
            KICK_HBG.columns[19],  #'Unnamed: 23'
            KICK_HBG.columns[20],  #'Delta = OH & Open PO - DD'
            KICK_HBG.columns[22],  #"Q4'19 unit price (USD)"
            KICK_HBG.columns[23],  #"Q1'20unit price (USD)"
            KICK_HBG.columns[24],  #'Delta = Q120 - Q419'
            KICK_HBG.columns[27],  #'Unnamed: 29'
            KICK_HBG.columns[35],  #"Ownership (Q1'20)"
            KICK_HBG.columns[36],  #"Arista PIC (Q1'20)
        ]

        KICK_HBG=KICK_HBG.filter(filter_HBG)
        #print(KICK_HBG,'KICK_HBG')

    agile_data=DimAgileAmpartMfrIness.objects.using('inputdb')
    
    
    if CM_loc=='SGD':
        agile_data=agile_data.filter(ampart__in=KICK_SGD["Arista Part Number"].to_list()).to_dataframe()
        error_NotInagile_table=KICK_SGD[~KICK_SGD["Arista Part Number"].isin(agile_data['ampart'])]
        #print(error_NotInagile_table)

        #print(len(agile_data))
        #print('data loaded from agile')
        agile_data.drop_duplicates(subset=['ampart','mfr_name','mfr_part_number'],inplace=True)
        agile_data.rename(columns={
        'id':'id',
        'ampart':'Number',
        'ampart_rev':'Rev',
        'ampart_lifecycle':'Lifecycle Phase',
        'ampart_desc':'Agile Item Desc',
        'mfr_name':'Mfr. Name (Manufacturers)',
        'mfr_lifecycle_phase':'Mfr. Part Lifecycle Phase (Manufacturers)',
        'mfr_qualification_status':'Qualification Status (Manufacturers)',
        'mfr_part_number':'Mfr. Part Number (Manufacturers)',
        'mfrdescription':'mfrdescription',
        'updateddate':'updateddate',
        },inplace=True)
        agile_filter=[
        'Number', #ampart
        'Lifecycle Phase',#ampart_lifecycle
        'Rev',#ampart_rev
        'Agile Item Desc',#Agile Item Desc
        'Mfr. Name (Manufacturers)',#mfr_name
        'Mfr. Part Lifecycle Phase (Manufacturers)', #ampart_lifecycle
        'Mfr. Part Number (Manufacturers)', #mfr_PARTNUMBER
        'Qualification Status (Manufacturers)', #mfr_qualification_status
        ]

        agile_data=agile_data.filter(agile_filter)


        agile_data_filtered=agile_data[agile_data['Number'].isin(KICK_SGD["Arista Part Number"].to_list())]
        portfolio=pd.merge(agile_data_filtered, KICK_SGD, left_on="Number", right_on="Arista Part Number",how='left')
        portfolio['Item Desc']=portfolio['Agile Item Desc']
        del portfolio['Agile Item Desc']

        db_header={
        portfolio.columns[0]:"Number",
        portfolio.columns[1]:"Lifecycle_Phase",
        portfolio.columns[2]:"Rev",
        portfolio.columns[3]:"Mfr_Name",
        portfolio.columns[4]:"Mfr_Part_Lifecycle_Phase",
        portfolio.columns[5]:"Mfr_Part_Number",
        portfolio.columns[6]:"Qualification_Status",

        portfolio.columns[7]:"cm_Part_Number",
        portfolio.columns[8]:"Arista_Part_Number",
        portfolio.columns[9]:"Cust_consign",
        portfolio.columns[10]:"Parts_controlled_by",
        portfolio.columns[11]:"Item_Desc",
        portfolio.columns[12]:"LT",
        portfolio.columns[13]:"MOQ",
        portfolio.columns[14]:"Original_PO_Delivery_sent_by_Mexico",
        portfolio.columns[15]:"cm_Quantity_Buffer_On_Hand",
        portfolio.columns[16]:"cm_Quantity_On_Hand_CS_Inv",
        portfolio.columns[17]:"Open_PO_due_in_this_quarter",
        portfolio.columns[18]:"Open_PO_due_in_next_quarter",
        portfolio.columns[19]:"Delivery_Based_Total_OH_sum_OPO_this_quarter",
        portfolio.columns[20]:"PO_Based_Total_OH_sum_OPO",
        portfolio.columns[21]:"CQ_ARIS_FQ_sum_1_SANM_Demand",
        portfolio.columns[22]:"CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
        portfolio.columns[23]:"CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
        portfolio.columns[24]:"CQ_sum_3_ARIS_FQ_SANM_Demand",
        portfolio.columns[25]:"Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
        portfolio.columns[26]:"ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std",
        portfolio.columns[27]:"CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD",
        portfolio.columns[28]:"Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1",
        portfolio.columns[29]:"Blended_AVG_PO_Receipt_Price",
        portfolio.columns[30]:"Ownership",
        portfolio.columns[31]:"Arista_PIC",
        }
        #print(db_header)
        portfolio.rename(columns=db_header,inplace=True)
        portfolio['Quarter']=this_quarter
        try:
            portfolio.loc[portfolio[f"Arista_PIC"].isin(gsm_Team),'Team' ]='GSM Team'
            # portfolio.loc[portfolio[f"Arista_PIC"].isin(cmm_team),'Team' ]='CMM Team'
        except Exception as e:
            print(e)
        portfolio['cm']='SGD'
        portfolio['file_from']='SGD'
        part_list=portfolio.Number.drop_duplicates().tolist()
        portfolio2=Portfolio.objects.filter(Quarter=Current_quarter(),Number__in=part_list).filter(~Q(file_from='SGD') & ~Q(cm__icontains='Global')).values(*portfolio.columns.tolist()).to_dataframe()

    if CM_loc=='JPE':
        agile_data=agile_data.filter(ampart__in=KICK_JPE["APN"].to_list()).to_dataframe()
        error_NotInagile_table=KICK_JPE[~KICK_JPE["APN"].isin(agile_data['ampart'])]
        agile_data.drop_duplicates(subset=['ampart','mfr_name','mfr_part_number'],inplace=True)
        agile_data.rename(columns={
        'id':'id',
        'ampart':'Number',
        'ampart_rev':'Rev',
        'ampart_lifecycle':'Lifecycle Phase',
        'ampart_desc':'Agile Item Desc',
        'mfr_name':'Mfr. Name (Manufacturers)',
        'mfr_lifecycle_phase':'Mfr. Part Lifecycle Phase (Manufacturers)',
        'mfr_qualification_status':'Qualification Status (Manufacturers)',
        'mfr_part_number':'Mfr. Part Number (Manufacturers)',
        'mfrdescription':'mfrdescription',
        'updateddate':'updateddate',
        },inplace=True)
        agile_filter=[
        'Number', #ampart
        'Lifecycle Phase',#ampart_lifecycle
        'Rev',#ampart_rev
        'Agile Item Desc',#Agile Item Desc
        'Mfr. Name (Manufacturers)',#mfr_name
        'Mfr. Part Lifecycle Phase (Manufacturers)', #ampart_lifecycle
        'Mfr. Part Number (Manufacturers)', #mfr_PARTNUMBER
        'Qualification Status (Manufacturers)', #mfr_qualification_status
        ]

        agile_data=agile_data.filter(agile_filter)

        agile_data_filtered2=agile_data[agile_data['Number'].isin(KICK_JPE["APN"].to_list())]
        # To database
        portfolio2=pd.merge(agile_data_filtered2, KICK_JPE, left_on="Number", right_on="APN",how='left')

        portfolio2['Item Desc']=portfolio2['Agile Item Desc']
        del portfolio2['Agile Item Desc']

        db_header2=[
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
        ]

        # portfolio2.set_axis(db_header2,axis=1,inplace=True)
        print('gsm_Team',gsm_Team)
        portfolio2.columns = db_header2
        portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(gsm_Team),'Team' ]='GSM Team'
        # portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(cmm_team),'Team' ]='CMM Team'
        #print(portfolio2.Team)

        portfolio2['Quarter']=this_quarter
        portfolio2['cm_Quantity_Buffer_On_Hand']=0
        portfolio2['Blended_AVG_PO_Receipt_Price']=0
        portfolio2['cm']='JPE'    
        #print(portfolio2.columns)
        portfolio2['file_from']='JPE'
        part_list=portfolio2.Number.drop_duplicates().tolist()
        portfolio=Portfolio.objects.filter(Quarter=Current_quarter(),Number__in=part_list).filter(~Q(file_from='JPE') & ~Q(cm__icontains='Global')).values(*portfolio2.columns.tolist()).to_dataframe()
        ####end final calculations
    if CM_loc=='FGN':
        agile_data=agile_data.filter(ampart__in=KICK_FGN["APN"].to_list()).to_dataframe()
        error_NotInagile_table=KICK_FGN[~KICK_FGN["APN"].isin(agile_data['ampart'])]
        print(KICK_FGN["APN"])
        print(agile_data,"Agile Data")
        agile_data.drop_duplicates(subset=['ampart','mfr_name','mfr_part_number'],inplace=True)
        agile_data.rename(columns={
            'id':'id',
            'ampart':'Number',
            'ampart_rev':'Rev',
            'ampart_lifecycle':'Lifecycle Phase',
            'ampart_desc':'Agile Item Desc',
            'mfr_name':'Mfr. Name (Manufacturers)',
            'mfr_lifecycle_phase':'Mfr. Part Lifecycle Phase (Manufacturers)',
            'mfr_qualification_status':'Qualification Status (Manufacturers)',
            'mfr_part_number':'Mfr. Part Number (Manufacturers)',
            'mfrdescription':'mfrdescription',
            'updateddate':'updateddate',
        },inplace=True)
        agile_filter=[
        'Number', #ampart
        'Lifecycle Phase',#ampart_lifecycle
        'Rev',#ampart_rev
        'Agile Item Desc',#Agile Item Desc
        'Mfr. Name (Manufacturers)',#mfr_name
        'Mfr. Part Lifecycle Phase (Manufacturers)', #ampart_lifecycle
        'Mfr. Part Number (Manufacturers)', #mfr_PARTNUMBER
        'Qualification Status (Manufacturers)', #mfr_qualification_status
        ]

        agile_data=agile_data.filter(agile_filter)

        agile_data_filtered2=agile_data[agile_data['Number'].isin(KICK_FGN["APN"].to_list())]
        # To database
        portfolio2=pd.merge(agile_data_filtered2, KICK_FGN, left_on="Number", right_on="APN",how='left')
        portfolio2['Item Desc']=portfolio2['Agile Item Desc']
        del portfolio2['Agile Item Desc']

        db_header2=[
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
        ]
        #print(portfolio2.columns)
        portfolio2.set_axis(db_header2,axis=1,inplace=True)

        portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(gsm_Team),'Team' ]='GSM Team'
        # portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(cmm_team),'Team' ]='CMM Team'
        portfolio2['Quarter']=this_quarter
        portfolio2['cm_Quantity_Buffer_On_Hand']=0
        portfolio2['Blended_AVG_PO_Receipt_Price']=0
        portfolio2['cm']='FGN'    
        #print(portfolio2.columns)
        portfolio2['file_from']='FGN'
        part_list=portfolio2.Number.drop_duplicates().tolist()
        portfolio=Portfolio.objects.filter(~Q(file_from='FGN') & ~Q(cm__icontains='Global')).filter(Quarter=Current_quarter(),Number__in=part_list).values(*portfolio2.columns.tolist()).to_dataframe()
        #print(portfolio)

        ####end final calculations
    
    if CM_loc=='JSJ':
        agile_data=agile_data.filter(ampart__in=KICK_JSJ["APN"].to_list()).to_dataframe()
        error_NotInagile_table=KICK_JSJ[~KICK_JSJ["APN"].isin(agile_data['ampart'])]
        agile_data.drop_duplicates(subset=['ampart','mfr_name','mfr_part_number'],inplace=True)
        agile_data.rename(columns={
        'id':'id',
        'ampart':'Number',
        'ampart_rev':'Rev',
        'ampart_lifecycle':'Lifecycle Phase',
        'ampart_desc':'Agile Item Desc',
        'mfr_name':'Mfr. Name (Manufacturers)',
        'mfr_lifecycle_phase':'Mfr. Part Lifecycle Phase (Manufacturers)',
        'mfr_qualification_status':'Qualification Status (Manufacturers)',
        'mfr_part_number':'Mfr. Part Number (Manufacturers)',
        'mfrdescription':'mfrdescription',
        'updateddate':'updateddate',
        },inplace=True)
        agile_filter=[
        'Number', #ampart
        'Lifecycle Phase',#ampart_lifecycle
        'Rev',#ampart_rev
        'Agile Item Desc',#Agile Item Desc
        'Mfr. Name (Manufacturers)',#mfr_name
        'Mfr. Part Lifecycle Phase (Manufacturers)', #ampart_lifecycle
        'Mfr. Part Number (Manufacturers)', #mfr_PARTNUMBER
        'Qualification Status (Manufacturers)', #mfr_qualification_status
        ]

        agile_data=agile_data.filter(agile_filter)

        agile_data_filtered2=agile_data[agile_data['Number'].isin(KICK_JSJ["APN"].to_list())]
        # To database
        portfolio2=pd.merge(agile_data_filtered2, KICK_JSJ, left_on="Number", right_on="APN",how='left')

        portfolio2['Item Desc']=portfolio2['Agile Item Desc']
        del portfolio2['Agile Item Desc']

        db_header2=[
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
        ]

        # portfolio2.set_axis(db_header2,axis=1,inplace=True)
        portfolio2.columns = db_header2
        portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(gsm_Team),'Team' ]='GSM Team'
        # portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(cmm_team),'Team' ]='CMM Team'
        #print(portfolio2.Team,"Team")

        portfolio2['Quarter']=this_quarter
        portfolio2['cm_Quantity_Buffer_On_Hand']=0
        portfolio2['Blended_AVG_PO_Receipt_Price']=0
        portfolio2['cm']='JSJ'    
        #print(portfolio2.columns,"Columns")
        portfolio2['file_from']='JSJ'
        part_list=portfolio2.Number.drop_duplicates().tolist()
        portfolio=Portfolio.objects.filter(Quarter=Current_quarter(),Number__in=part_list).filter(~Q(file_from='JSJ') & ~Q(cm__icontains='Global')).values(*portfolio2.columns.tolist()).to_dataframe()
        ####end final calculations
    
    if CM_loc=='JMX':
        agile_data=agile_data.filter(ampart__in=KICK_JMX["APN"].to_list()).to_dataframe()
        error_NotInagile_table=KICK_JMX[~KICK_JMX["APN"].isin(agile_data['ampart'])]
        agile_data.drop_duplicates(subset=['ampart','mfr_name','mfr_part_number'],inplace=True)
        agile_data.rename(columns={
        'id':'id',
        'ampart':'Number',
        'ampart_rev':'Rev',
        'ampart_lifecycle':'Lifecycle Phase',
        'ampart_desc':'Agile Item Desc',
        'mfr_name':'Mfr. Name (Manufacturers)',
        'mfr_lifecycle_phase':'Mfr. Part Lifecycle Phase (Manufacturers)',
        'mfr_qualification_status':'Qualification Status (Manufacturers)',
        'mfr_part_number':'Mfr. Part Number (Manufacturers)',
        'mfrdescription':'mfrdescription',
        'updateddate':'updateddate',
        },inplace=True)
        agile_filter=[
        'Number', #ampart
        'Lifecycle Phase',#ampart_lifecycle
        'Rev',#ampart_rev
        'Agile Item Desc',#Agile Item Desc
        'Mfr. Name (Manufacturers)',#mfr_name
        'Mfr. Part Lifecycle Phase (Manufacturers)', #ampart_lifecycle
        'Mfr. Part Number (Manufacturers)', #mfr_PARTNUMBER
        'Qualification Status (Manufacturers)', #mfr_qualification_status
        ]

        agile_data=agile_data.filter(agile_filter)

        agile_data_filtered2=agile_data[agile_data['Number'].isin(KICK_JMX["APN"].to_list())]
        # To database
        portfolio2=pd.merge(agile_data_filtered2, KICK_JMX, left_on="Number", right_on="APN",how='left')

        portfolio2['Item Desc']=portfolio2['Agile Item Desc']
        del portfolio2['Agile Item Desc']

        db_header2=[
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
        ]
            
        portfolio2.set_axis(db_header2,axis=1,inplace=True)
        portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(gsm_Team),'Team' ]='GSM Team'
        # portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(cmm_team),'Team' ]='CMM Team'
        #print(portfolio2.Team)

        portfolio2['Quarter']=this_quarter
        portfolio2['cm_Quantity_Buffer_On_Hand']=0
        portfolio2['Blended_AVG_PO_Receipt_Price']=0
        portfolio2['cm']='JMX'    
        #print(portfolio2.columns)
        portfolio2['file_from']='JMX'
        part_list=portfolio2.Number.drop_duplicates().tolist()
        portfolio=Portfolio.objects.filter(Quarter=Current_quarter(),Number__in=part_list).filter(~Q(file_from='JMX') & ~Q(cm__icontains='Global')).values(*portfolio2.columns.tolist()).to_dataframe()
        ####end final calculations

    if CM_loc=='HBG':
        agile_data=agile_data.filter(ampart__in=KICK_HBG["APN"].to_list()).to_dataframe()
        error_NotInagile_table=KICK_HBG[~KICK_HBG["APN"].isin(agile_data['ampart'])]
        agile_data.drop_duplicates(subset=['ampart','mfr_name','mfr_part_number'],inplace=True)
        agile_data.rename(columns={
            'id':'id',
            'ampart':'Number',
            'ampart_rev':'Rev',
            'ampart_lifecycle':'Lifecycle Phase',
            'ampart_desc':'Agile Item Desc',
            'mfr_name':'Mfr. Name (Manufacturers)',
            'mfr_lifecycle_phase':'Mfr. Part Lifecycle Phase (Manufacturers)',
            'mfr_qualification_status':'Qualification Status (Manufacturers)',
            'mfr_part_number':'Mfr. Part Number (Manufacturers)',
            'mfrdescription':'mfrdescription',
            'updateddate':'updateddate',
        },inplace=True)
        agile_filter=[
        'Number', #ampart
        'Lifecycle Phase',#ampart_lifecycle
        'Rev',#ampart_rev
        'Agile Item Desc',#Agile Item Desc
        'Mfr. Name (Manufacturers)',#mfr_name
        'Mfr. Part Lifecycle Phase (Manufacturers)', #ampart_lifecycle
        'Mfr. Part Number (Manufacturers)', #mfr_PARTNUMBER
        'Qualification Status (Manufacturers)', #mfr_qualification_status
        ]

        agile_data=agile_data.filter(agile_filter)

        agile_data_filtered2=agile_data[agile_data['Number'].isin(KICK_HBG["APN"].to_list())]
        # To database
        portfolio2=pd.merge(agile_data_filtered2, KICK_HBG, left_on="Number", right_on="APN",how='left')

        portfolio2['Item Desc']=portfolio2['Agile Item Desc']
        del portfolio2['Agile Item Desc']

        db_header2=[
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
        ]

        portfolio2.set_axis(db_header2,axis=1,inplace=True)
        portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(gsm_Team),'Team' ]='GSM Team'
        # portfolio2.loc[portfolio2[f"Arista_PIC"].astype(str).str.split('/').str[0].isin(cmm_team),'Team' ]='CMM Team'
        #print(portfolio2.Team)

        portfolio2['Quarter']=this_quarter
        portfolio2['cm_Quantity_Buffer_On_Hand']=0
        portfolio2['Blended_AVG_PO_Receipt_Price']=0
        portfolio2['cm']='HBG'    
        #print(portfolio2.columns)
        portfolio2['file_from']='HBG'
        part_list=portfolio2.Number.drop_duplicates().tolist()
        portfolio=Portfolio.objects.filter(Quarter=Current_quarter(),Number__in=part_list).filter(~Q(file_from='HBG') & ~Q(cm__icontains='Global')).values(*portfolio2.columns.tolist()).to_dataframe()
        ####end final calculations



    #####global portfolio logic
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
        'Original_PO_Delivery_sent_by_Mexico',
        'file_from',
        ]
    def concat_cm(s):
        '''
        This will create a list of cm for portfolio logic
        '''
        s=s.to_list()
        #print(s)
        return json.dumps(s)

    def order(price_list,cm_list):
        '''
        This will create a Item price for global Part combining like eg.price_from_sgd/price_from_jpe/price_from_fgn/price_from_hbg
        '''
        price_list=json.loads(price_list)
        cm_list=json.loads(cm_list)
        #print('price_list',price_list)
        #print('cm_list',cm_list)
        
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
        data=data.lower().replace('nan','-')
        #print(data)
        return data
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

        
    

    portfolio_bak=portfolio.copy()
    portfolio2_bak=portfolio2.copy()

    portfolio_bak['unique_field']=portfolio_bak['Mfr_Name'].astype(str)+'###'+portfolio_bak['Number'].astype(str)+'###'+portfolio_bak['Mfr_Part_Number'].astype(str)+'###'+portfolio_bak['Ownership'].astype(str)
    portfolio2_bak['unique_field']=portfolio2_bak['Mfr_Name'].astype(str)+'###'+portfolio2_bak['Number'].astype(str)+'###'+portfolio2_bak['Mfr_Part_Number'].astype(str)+'###'+portfolio2_bak['Ownership'].astype(str)

    #portfolio_global_bak=portfolio_bak.append(portfolio2_bak,ignore_index=True)
    portfolio_global_bak=pd.concat([portfolio_bak,portfolio2_bak],ignore_index=True)
    portfolio_global_bak.drop(join_field[1:],axis=1,inplace=True)

    error_while_saving=pd.DataFrame()
    error_while_saving_partnumber=[]
    undefined_parts=pd.DataFrame()
    #print(portfolio)
    #print(portfolio2)

    if  not portfolio2.empty or not portfolio.empty :

        portfolio['unique_field']=portfolio['Mfr_Name'].astype(str)+'###'+portfolio['Number'].astype(str)+'###'+portfolio['Mfr_Part_Number'].astype(str)+'###'+portfolio['Ownership'].astype(str)
        portfolio2['unique_field']=portfolio2['Mfr_Name'].astype(str)+'###'+portfolio2['Number'].astype(str)+'###'+portfolio2['Mfr_Part_Number'].astype(str)+'###'+portfolio2['Ownership'].astype(str)
        # portfolio['file_from']='SGD'
        # portfolio2['file_from']='JPE'

        #portfolio_global=portfolio.append(portfolio2,ignore_index=True)
        portfolio_global=pd.concat([portfolio,portfolio2],ignore_index=True)

        del portfolio['unique_field']
        del portfolio2['unique_field']

        portfolio_global=portfolio_global.filter(join_field)
        portfolio_global.fillna(0,inplace=True)
        portfolio_global['cm_Quantity_Buffer_On_Hand']=portfolio_global['cm_Quantity_Buffer_On_Hand'].astype(float).astype('int64')
        
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
            "Original_PO_Delivery_sent_by_Mexico":po_delivery,
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
                'Original_PO_Delivery_sent_by_Mexico',
                "file_from",
        ]

        portfolio_global = portfolio_global.reset_index()
        #print(portfolio_global['Original_PO_Delivery_sent_by_Mexico'])
        def po_delivery_cal(Original_PO_Delivery_sent_by_Mexico,Delivery_Based_Total_OH_sum_OPO_this_quarter,PO_Based_Total_OH_sum_OPO,CQ_ARIS_FQ_sum_1_SANM_Demand,CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand):
            #print(Original_PO_Delivery_sent_by_Mexico,Delivery_Based_Total_OH_sum_OPO_this_quarter,PO_Based_Total_OH_sum_OPO,CQ_ARIS_FQ_sum_1_SANM_Demand,CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand)
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
        print(type(portfolio_global["cm_Quantity_On_Hand_CS_Inv"]),'sssss')
        data=portfolio_global["cm_Quantity_On_Hand_CS_Inv"].astype(int)
        #print(portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"],"Global Demand")
        portfolio_global["cm_Quantity_On_Hand_CS_Inv"]=round(data,5)
        portfolio_global["Open_PO_due_in_this_quarter"]=round(portfolio_global["Open_PO_due_in_this_quarter"].astype(int),5)
        portfolio_global["Open_PO_due_in_next_quarter"]=round(portfolio_global["Open_PO_due_in_next_quarter"].astype(int),5)
        portfolio_global["Delivery_Based_Total_OH_sum_OPO_this_quarter"]=round(portfolio_global["Delivery_Based_Total_OH_sum_OPO_this_quarter"].astype(int),5)
        portfolio_global["PO_Based_Total_OH_sum_OPO"]=round(portfolio_global["PO_Based_Total_OH_sum_OPO"].astype(int),5)
        portfolio_global["CQ_ARIS_FQ_sum_1_SANM_Demand"]=round(portfolio_global["CQ_ARIS_FQ_sum_1_SANM_Demand"].astype(int),5)
        portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"]=round(portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"].astype(int),5)
        portfolio_global["CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"]=round(portfolio_global["CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"].astype(int),5)
        portfolio_global["CQ_sum_3_ARIS_FQ_SANM_Demand"]=round(portfolio_global["CQ_sum_3_ARIS_FQ_SANM_Demand"].astype(int),5)
        portfolio_global["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"]=round(portfolio_global["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"].astype(int),5)
        portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD"]=round(portfolio_global["CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD"].astype(int),5)
        portfolio_global["Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1"]=round(portfolio_global["Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1"].astype(int),5)
        portfolio_global["Blended_AVG_PO_Receipt_Price"]=round(portfolio_global["Blended_AVG_PO_Receipt_Price"].astype(int),5)
        portfolio_global["ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std"]=round(portfolio_global["ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std"].astype(int),5)

        try:portfolio_global['sgd_jpe_cost']=portfolio_global.apply(lambda x:order(x.std_cost,x.file_from),axis=1)
        except:portfolio_global['sgd_jpe_cost']=None
        portfolio_global['Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista']=portfolio_global.apply(lambda x:po_delivery_cal(x.Original_PO_Delivery_sent_by_Mexico,x.Delivery_Based_Total_OH_sum_OPO_this_quarter,x.PO_Based_Total_OH_sum_OPO,x.CQ_ARIS_FQ_sum_1_SANM_Demand,x.CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand),axis=1)
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
        q=Portfolio.objects.filter(Quarter=Current_quarter())
        # q.update(refreshed_comment='Deleted')

        if CM_loc=='SGD':
            portfolio.fillna(0,inplace=True)
            portfolio['sgd_jpe_cost']=round(portfolio['ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std'],5).astype(str)+'/-/-/-/-/-'
            final_list.append(portfolio)
            final_list.append(portfolio_global_final)
            undefined_parts=portfolio.loc[~portfolio[f"Team"].isin(['CMM Team','GSM Team'])]

        elif CM_loc=='JPE' :

            portfolio.fillna(0,inplace=True)
            portfolio2['sgd_jpe_cost']='-/'+round(portfolio2['ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std'],5).astype(str)+'/-/-/-/-'
            #print(portfolio2['sgd_jpe_cost'])
            undefined_parts=portfolio2.loc[~portfolio2[f"Team"].isin(['CMM Team','GSM Team'])]
            #print(portfolio2.Arista_PIC)
            #print(portfolio_global_final.Arista_PIC)
            final_list.append(portfolio2)
            final_list.append(portfolio_global_final)
        elif CM_loc=='FGN' :

            portfolio.fillna(0,inplace=True)
            portfolio2['sgd_jpe_cost']='-/-/'+round(portfolio2['ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std'],5).astype(str)+'/-/-/-'
            #print(portfolio2['sgd_jpe_cost'])
            undefined_parts=portfolio2.loc[~portfolio2[f"Team"].isin(['CMM Team','GSM Team'])]
            final_list.append(portfolio2)
            final_list.append(portfolio_global_final)
        
        elif CM_loc=='HBG' :

            portfolio.fillna(0,inplace=True)
            portfolio2['sgd_jpe_cost']='-/-/-/'+round(portfolio2['ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std'],5).astype(str)+'/-/-'
            #print(portfolio2['sgd_jpe_cost'])
            undefined_parts=portfolio2.loc[~portfolio2[f"Team"].isin(['CMM Team','GSM Team'])]
            final_list.append(portfolio2)
            final_list.append(portfolio_global_final)
        
        elif CM_loc=='JSJ' :

            portfolio.fillna(0,inplace=True)
            portfolio2['sgd_jpe_cost']='-/-/-/-/'+round(portfolio2['ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std'],5).astype(str)+'/-'
            #print(portfolio2['sgd_jpe_cost'])
            undefined_parts=portfolio2.loc[~portfolio2[f"Team"].isin(['CMM Team','GSM Team'])]
            final_list.append(portfolio2)
            final_list.append(portfolio_global_final)
        
        elif CM_loc=='JMX' :

            portfolio.fillna(0,inplace=True)
            portfolio2['sgd_jpe_cost']='-/-/-/-/-/'+round(portfolio2['ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std'],5).astype(str)
            #print(portfolio2['sgd_jpe_cost'])
            undefined_parts=portfolio2.loc[~portfolio2[f"Team"].isin(['CMM Team','GSM Team'])]
            final_list.append(portfolio2)
            final_list.append(portfolio_global_final)

        
        #print(final_list,"Final")
        for portfolio_cat in final_list:
            portfolio_cat.fillna(0,inplace=True)
            portfolio_cat['Ownership'] = portfolio_cat['Ownership'].str.strip()
            portfolio_cat['Arista_PIC'] = portfolio_cat['Arista_PIC'].str.strip()
            portfolio_cat["cm_Quantity_On_Hand_CS_Inv"]=round(portfolio_cat["cm_Quantity_On_Hand_CS_Inv"],5)
            portfolio_cat["Open_PO_due_in_this_quarter"]=round(portfolio_cat["Open_PO_due_in_this_quarter"],5)
            portfolio_cat["Open_PO_due_in_next_quarter"]=round(portfolio_cat["Open_PO_due_in_next_quarter"],5)
            portfolio_cat["Delivery_Based_Total_OH_sum_OPO_this_quarter"]=round(portfolio_cat["Delivery_Based_Total_OH_sum_OPO_this_quarter"],5)
            portfolio_cat["PO_Based_Total_OH_sum_OPO"]=round(portfolio_cat["PO_Based_Total_OH_sum_OPO"],5)
            portfolio_cat["CQ_ARIS_FQ_sum_1_SANM_Demand"]=round(portfolio_cat["CQ_ARIS_FQ_sum_1_SANM_Demand"],5)
            portfolio_cat["CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"]=round(portfolio_cat["CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand"],5)
            portfolio_cat["CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"]=round(portfolio_cat["CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand"],5)
            portfolio_cat["CQ_sum_3_ARIS_FQ_SANM_Demand"]=round(portfolio_cat["CQ_sum_3_ARIS_FQ_SANM_Demand"],5)
            portfolio_cat["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"]=round(portfolio_cat["Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista"],5)
            portfolio_cat["CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD"]=round(portfolio_cat["CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD"],5)
            portfolio_cat["Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1"]=round(portfolio_cat["Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1"],5)
            portfolio_cat["Blended_AVG_PO_Receipt_Price"]=round(portfolio_cat["Blended_AVG_PO_Receipt_Price"],5)
            portfolio_cat["ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std"]=round(portfolio_cat["ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std"],5)
            bulk_save=[]

            portfolio_in_db=q.filter(Arista_Part_Number__in=portfolio_cat['Arista_Part_Number'].to_list()).to_dataframe()
            print(portfolio_cat,'portfolio_cat')
            # print(portfolio_in_db,"Portfolio in db")
            for index, row in portfolio_cat.iterrows():
                print(row['Team'],'rowsssss')
                try:
                    #print(row['Arista_Part_Number'],row['Team'])
                    if row['Team'] in ['GSM Team','CMM Team']:
                        print('llalalalalala')
                        fil_part=portfolio_in_db.loc[ (portfolio_in_db['Arista_Part_Number']==row['Arista_Part_Number']) & (portfolio_in_db['Mfr_Part_Number']==row['Mfr_Part_Number']) & (portfolio_in_db['Mfr_Name']==row['Mfr_Name']) & (portfolio_in_db['Ownership']==row['Ownership']) & (portfolio_in_db['cm']==row['cm']) ]
                        if not fil_part.empty:
                            parts=q.filter(Q(Arista_Part_Number=row['Arista_Part_Number']) & Q(Mfr_Part_Number=row['Mfr_Part_Number']) & Q(Mfr_Name=row['Mfr_Name'])&Q(Ownership=row['Ownership']) & Q(cm=row['cm']))
                            temp=row.to_dict()
                            temp['refreshed_comment']='Updated'
                            temp['refreshed_on']=timezone.localtime(timezone.now())
                            parts.update(**temp)
                            # parts.update(refreshed_comment='Updated',refreshed_on=timezone.localtime(timezone.now()))
                            #print('updated')
                            
                        else:
                            print("Check if empty")
                            instance=Portfolio(**row.to_dict())
                            instance.refreshed_comment='Added'
                            instance.refreshed_on=timezone.localtime(timezone.now())
                            instance.save()
                            if refresh_flag:
                                check=q.filter(Q(Arista_Part_Number=row['Arista_Part_Number']) & Q  (Mfr_Part_Number=row['Mfr_Part_Number']) & Q(Mfr_Name=row['Mfr_Name'])& ~Q(Ownership=row['Ownership']) & Q(file_from=CM_loc) & Q(cm=CM_loc))
                                if check.exists():
                                    #print('*checking...'*100)
                                    from rfx.models import RFX
                                    from portfolio.views import create_global
                                    
                                    RFX.objects.filter(portfolio__in=check).delete()
                                    for x in check:
                                        log=delete_log(
                                        Arista_Part_Number=x.Arista_Part_Number,
                                        Quarter=x.Quarter,
                                        cm=x.cm,
                                        Number=x.Number,
                                        Mfr_Name=x.Mfr_Name,
                                        Mfr_Part_Number=x.Mfr_Part_Number,
                                        user=request.user,
                                        )
                                        log.save()
                                    ids=list(check.values_list('id',flat=True))
                                    check.update(Quarter='deleted')
                                    for x in Portfolio.objects.filter(id__in=ids):
                                        create_global(request,x,False)
                                    Portfolio.objects.filter(id__in=ids).delete()
                            #print('Saved')
                except Exception as e:
                    #print(e)
                    error_while_saving_partnumber.append(row['Arista_Part_Number'])
            # if not refresh_flag:
            #     Portfolio.objects.bulk_create(bulk_save,batch_size=5000)
    error_while_saving['Arista Part Number']=error_while_saving_partnumber
    error_while_saving['Error Assumption']='Data Mismatched'
    errorCount=len(error_while_saving)
    total_count=sum([len(x) for x in final_list])-errorCount
    #print(error_while_saving)
    error_while_saving.drop_duplicates(subset=['Arista Part Number'],inplace=True)
    print(error_while_saving,'error_while_saving')
    email_to=[]
    if CM_loc=='SGD':
        user_belong_to_this=list(set(portfolio["Arista_PIC"].to_list()))
    else:
        user_belong_to_this=list(set(portfolio2["Arista_PIC"].to_list()))

    for user in user_belong_to_this:
        datas=User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name__icontains=user)
        if datas.exists():
            email_to.append(datas[0].email)
        else:
            print('user not found')
    #print(email_to)

    email_to.append(request.user.email)
    if email_to:
        send_notification(request,user_to=None,to=email_to,user_from='MASTER PRICING AUTOMATION TOOL',
                body=f'''
                        Hello,

                        Your {CM_loc} Portfolio page has been been refreshed in Arista Master Pricing Automation tool. 

                        Regards,
                        MASTER PRICING AUTOMATION TOOL

                                        ''',
                    subject=f'''Parts Added to Portfolio''',title=None,)
    print(error_NotInagile_table,'error_NotInagile_table')

    if not (error_NotInagile_table.empty and error_while_saving.empty and undefined_parts.empty):
        print('ssjdjjdj')
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                if not error_NotInagile_table.empty:

                    error_NotInagile_table.to_excel(writer,index=False,sheet_name='Parts Not In agile')
                if not error_while_saving.empty:
                    error_while_saving.to_excel(writer,index=False,sheet_name='Error While Saving to Portfolio')
                if not undefined_parts.empty:
                    undefined_parts.to_excel(writer,index=False,sheet_name='Non Assigned Parts')

                writer.save()

                file_MIME=b.getvalue()

                send_notification(request,user_to=None,to_mail_id=[request.user.email],user_from='MASTER PRICING AUTOMATION TOOL',
                body=f'''
                Hello {request.user.first_name},

                Portfolio has been been refreshed for {total_count} part(s) Successfully with the inputfile,
                Unloaded parts are attached as excel (if any)


                <i>Note: Don't Reply to this mail</i>

                Regards,
                MASTER PRICING AUTOMATION TOOL



                ''',
                subject=f'''
                Unaccepted part(s) during portfolio refresh
                ''',
                title=None,Attach_file=['Portfolio Un-uploaded.xlsx',file_MIME])
    #### Auto quote raisser for CM
    part_list=[]
    for portfolio_cat in final_list:
        part_list+=portfolio_cat['Arista_Part_Number'].to_list()
    #print(part_list,"Parts List")  
    ids=list(Portfolio.objects.filter(Arista_Part_Number__in=part_list,Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm='SGD').distinct('Arista_Part_Number').values_list('id',flat=True))
    ids2=list(Portfolio.objects.filter(Arista_Part_Number__in=part_list,Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm='JPE').distinct('Arista_Part_Number').values_list('id',flat=True))
    ids3=list(Portfolio.objects.filter(Arista_Part_Number__in=part_list,Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm='FGN').distinct('Arista_Part_Number').values_list('id',flat=True))
    ids4=list(Portfolio.objects.filter(Arista_Part_Number__in=part_list,Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm='HBG').distinct('Arista_Part_Number').values_list('id',flat=True))
    ids5=list(Portfolio.objects.filter(Arista_Part_Number__in=part_list,Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm='JSJ').distinct('Arista_Part_Number').values_list('id',flat=True))
    ids6=list(Portfolio.objects.filter(Arista_Part_Number__in=part_list,Quarter=Current_quarter()).exclude(cm='Global').filter(Team='CMM Team').filter(cm='JMX').distinct('Arista_Part_Number').values_list('id',flat=True))

    ids=ids+ids2+ids3+ids4+ids5+ids6
    # create_rfx(request,parts=ids,To=['cm'],created_by=request.user,Arista_pic_comment='')
    auto_clean_rfx_cm()
    return part_list
