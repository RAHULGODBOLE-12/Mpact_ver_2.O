from django.db import models
from django_pandas.managers import DataFrameManager
from django.contrib.auth.models import User,Group

# Create your models here.
class logging(models.Model):
    name=models.CharField(max_length=255,null=True)
    exception=models.CharField(max_length=255,null=True)
    table_name=models.CharField(max_length=255,null=True)
    date_time=models.DateTimeField(auto_now_add=True)
    objects = DataFrameManager()
class helper_Portfolio(models.Model):
    table_name=models.CharField(max_length=255,null=True)
    Quarter=models.CharField(max_length=255,null=True)
    column_mapper=models.TextField(null=True)
    objects = DataFrameManager()


class Portfolio(models.Model):
    Quarter=models.CharField(max_length=255,null=True)#Created Quarter
    cm=models.CharField(max_length=255,null=True)#site SGD/JPE/...
    Number=models.CharField(max_length=255,null=True)#Customer part Number
    Lifecycle_Phase=models.CharField(max_length=255,null=True)#customer Lifecycle_Phase
    commodity=models.CharField(default='Miscellaneous',max_length=255,null=True)#commodity from Assign Part model
    Rev=models.CharField(max_length=255,null=True)#Customer Revision
    Mfr_Name=models.CharField(max_length=255,null=True)#Manufacture name
    Mfr_Part_Lifecycle_Phase=models.CharField(max_length=255,null=True)#Manufacture Lifecycle Phase
    Mfr_Part_Number=models.CharField(max_length=255,null=True)#Manufacture Part Number
    Qualification_Status=models.CharField(max_length=255,null=True)#Qualification Status
    cm_Part_Number=models.CharField(max_length=255,null=True)#Contract Manufacturer Part Number
    Arista_Part_Number=models.CharField(max_length=255,null=True)#Arista Part Number
    Cust_consign=models.CharField(max_length=255,null=True)#Cust_consign y/n
    Parts_controlled_by=models.CharField(max_length=255,null=True)#Parts_controlled_by Arista/CM(Sanmina/Jabil/....)
    Item_Desc=models.CharField(max_length=255,null=True)#Part Description
    LT=models.CharField(max_length=255,null=True)#Leadtime
    MOQ=models.CharField(max_length=255,null=True)#Minimum order quantity
    Original_PO_Delivery_sent_by_Mexico=models.CharField(max_length=255,null=True) #original PO/Delivery
    cm_Quantity_Buffer_On_Hand=models.CharField(max_length=255,null=True)#CM Buffer ON Hand Quantity
    cm_Quantity_On_Hand_CS_Inv=models.IntegerField(null=True)#CM Buffer ON Hand Inventory
    Open_PO_due_in_this_quarter=models.IntegerField(null=True)#Open PO due in current Quarter
    Open_PO_due_in_next_quarter=models.IntegerField(null=True)#Open po due in next quarter
    Delivery_Based_Total_OH_sum_OPO_this_quarter=models.IntegerField(null=True)#Delivery Based Total_OH +OPO Current quarter
    PO_Based_Total_OH_sum_OPO=models.IntegerField(null=True)#PO Based TotalOH + OPO
    CQ_ARIS_FQ_sum_1_SANM_Demand=models.IntegerField(null=True)#Current Quarter Demand Q
    CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand=models.IntegerField(null=True)#Future Quarter Demand Q+1
    CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand=models.IntegerField(null=True)#Future Quarter Demand Q+2
    CQ_sum_3_ARIS_FQ_SANM_Demand=models.IntegerField(null=True)#Future Quarter Demand Q+3
    Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista=models.IntegerField(null=True)#Delta = OH and OPO - DD
    ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std=models.FloatField(max_length=255,null=True)#Current Quarter Std cost
    CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD=models.FloatField(max_length=255,null=True)#CQ+1 (ARIS) / FQ+2 (CM) unit price (USD)
    Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1=models.FloatField(max_length=255,null=True)#Delta \n ARIS CQ+1 CM FQ+2 \nvs ARIS - CQ CM FQ
    Blended_AVG_PO_Receipt_Price=models.FloatField(max_length=255,null=True)#Sanmina Blended Avg PO Receipt Price
    Ownership=models.CharField(max_length=255,null=True)#Parts ownership Arista/Sanmina/Jabil
    Arista_PIC=models.CharField(max_length=255,null=True)#Full Name of PIC(GSM team/CMM Team)
    Team=models.CharField(max_length=255,null=True)#CMM/GSM
    rfq_sent_flag_supplier=models.CharField(default='Not Raised',max_length=255,null=True)#RFX Raise Flag(Not in use)
    rfq_sent_flag_cm=models.CharField(default='Not Raised',max_length=255,null=True)#RFX Raise Flag(Not in use)
    rfq_sent_flag_distributor=models.CharField(default='Not Raised',max_length=255,null=True)#RFX Raise Flag(Not in use)
    rfq_sent_distributor=models.CharField(max_length=255,null=True)#RFX Raise Flag(Not in use)
    Arista_pic_comment=models.CharField(max_length=255,null=True)#comments by pic
    offcycle=models.BooleanField(default=False,null=True)#offcycle Loaded from agile or manually uploaded parts
    bp_comment=models.TextField(default='',null=True)#comments
    created_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)#WHo created the portfolio django User model

    created_on=models.DateTimeField(auto_now_add=True,null=True)#created data time
    refreshed_comment=models.TextField(default='',null=True)#agile refresh(Added/Removed/deleted)
    refreshed_on=models.DateTimeField(null=True)#Agile refresh time
    refreshed_MRP_date=models.DateTimeField(null=True)#MRP date(Not in use)
    file_from=models.CharField(default='',max_length=255,null=True)#file from which site(JPE/SGD/FGN/../..)
    sgd_jpe_cost=models.CharField(default='-',max_length=255,null=True)#Combination of all cm cost (cost from SGD/from JPE/from FGN)
    

    objects = DataFrameManager()



class logger_portfolio(models.Model):
    comments=models.TextField(max_length=255,null=True)
    error=models.TextField(max_length=255,null=True)
    status=models.BooleanField(null=True)
    completed_status=models.BooleanField(default=False,null=True)
    modified_on=models.DateTimeField(auto_now_add=True)
    modified_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)




class SGD_JBE_component_ss_team(models.Model):
    Contract_Mfr=models.CharField(max_length=255,null=True)
    quarter=models.CharField(max_length=255,null=True)
    APN=models.CharField(max_length=255,null=True)
    Arista_PIC=models.CharField(max_length=255,null=True)
    Ownership=models.CharField(max_length=255,null=True)
    Part_Desc=models.CharField(max_length=255,null=True)
    Annual_demand=models.IntegerField(null=True)
    CPN=models.CharField(max_length=255,null=True)
    total_OH=models.CharField(max_length=255,null=True)
    quarter_demand_1=models.IntegerField(null=True)
    quarter_demand_2=models.IntegerField(null=True)
    quarter_demand_3=models.IntegerField(null=True)
    quarter_demand_4=models.IntegerField(null=True)
    quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_std_2=models.FloatField(max_length=255,null=True)
    Part=models.CharField(max_length=255,null=True)
    Delta_std=models.FloatField(max_length=255,null=True)
    quarter_demand_1_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_demand_2_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_demand_3_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_demand_4_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    Delta_demand=models.FloatField(max_length=255,null=True)
    Delta_Demand_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    Delta_Demand_x_Delta_std=models.FloatField(max_length=255,null=True)
    quarter_demand_mapper=models.CharField(max_length=255,null=True)
    quarter_std_mapper=models.CharField(max_length=255,null=True)
    MRP_Report_Date=models.CharField(max_length=255,null=True)
    objects = DataFrameManager()

    def __str__(self):
        return f'''Contract_Mfr:{self.Contract_Mfr}|Quarter:{self.quarter}|APN:{self.APN}|Arista_PIC:{self.Arista_PIC}'''
class SGD_JBE_component_cmm_team(models.Model):
    Contract_Mfr=models.CharField(max_length=255,null=True)
    quarter=models.CharField(max_length=255,null=True)
    APN=models.CharField(max_length=255,null=True)
    Arista_PIC=models.CharField(max_length=255,null=True)
    Ownership=models.CharField(max_length=255,null=True)
    Part_Desc=models.CharField(max_length=255,null=True)
    Annual_demand=models.IntegerField(null=True)
    CPN=models.CharField(max_length=255,null=True)
    total_OH=models.CharField(max_length=255,null=True)
    quarter_demand_1=models.IntegerField(null=True)
    quarter_demand_2=models.IntegerField(null=True)
    quarter_demand_3=models.IntegerField(null=True)
    quarter_demand_4=models.IntegerField(null=True)
    quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_std_2=models.FloatField(max_length=255,null=True)
    Part=models.CharField(max_length=255,null=True)
    Delta_std=models.FloatField(max_length=255,null=True)
    quarter_demand_1_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_demand_2_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_demand_3_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    quarter_demand_4_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    Delta_demand=models.FloatField(max_length=255,null=True)
    Delta_Demand_x_quarter_std_1=models.FloatField(max_length=255,null=True)
    Delta_Demand_x_Delta_std=models.FloatField(max_length=255,null=True)
    quarter_demand_mapper=models.CharField(max_length=255,null=True)
    quarter_std_mapper=models.CharField(max_length=255,null=True)
    MRP_Report_Date=models.CharField(max_length=255,null=True)
    objects = DataFrameManager()

    def __str__(self):
        return f'''Contract_Mfr:{self.Contract_Mfr}|Quarter:{self.quarter}|APN:{self.APN}|Arista_PIC:{self.Arista_PIC}'''

class Top_Global_component(models.Model):
    APN=models.CharField(max_length=255,null=True)
    Part_Desc=models.CharField(max_length=255,null=True)
    Ownership_JPE=models.CharField(max_length=255,null=True)
    Arista_PIC_JPE=models.CharField(max_length=255,null=True)
    total_OH_JPE=models.IntegerField(null=True)
    Annual_demand_JPE=models.IntegerField(null=True)
    Delta_demand_JPE=models.IntegerField(null=True)
    quarter_std_1_JPE=models.FloatField(null=True)
    Delta_Demand_multiply_x_quarter_std_1_JPE=models.FloatField(null=True)
    Ownership_SGD=models.CharField(max_length=255,null=True)
    Arista_PIC_SGD=models.CharField(max_length=255,null=True)
    total_OH_SGD=models.IntegerField(null=True)
    Annual_demand_SGD=models.IntegerField(null=True)
    Delta_demand_SGD=models.IntegerField(null=True)
    quarter_std_1_SGD=models.FloatField(null=True)
    quarter_demand_1_x_quarter_std_1_SGD=models.FloatField(null=True)
    Global_Annual_Demand=models.IntegerField(null=True)
    Global_Spend=models.FloatField(null=True)
    Global_Spend_Percentage=models.FloatField(null=True)
    quarter=models.CharField(max_length=255,null=True)
    Team=models.CharField(max_length=255,null=True)
    MRP_Report_Date=models.CharField(max_length=255,null=True)
    objects = DataFrameManager()
    def __str__(self):
        return f'''Team:{self.Team}|Quarter:{self.quarter}|APN:{self.APN}|Arista_PIC:{self.Arista_PIC_JPE}'''

class Refreshed_top_component_JPE_SGD(models.Model):
    APN=models.CharField(max_length=255,null=True)
    Ownership=models.CharField(max_length=255,null=True)
    Arista_PIC=models.CharField(max_length=255,null=True)
    Part_Desc=models.CharField(max_length=255,null=True)
    PO_or_Delivery=models.CharField(max_length=255,null=True)
    CM_Buffer_On_Hand=models.FloatField(null=True)
    CM_Quantity_On_Hand_sum_CS_Inv=models.FloatField(null=True)
    Open_PO_due_in_Q=models.FloatField(null=True)
    Open_PO_due_in_Q1=models.FloatField(null=True)
    Delivery_Based_Total_OH_sum_OPO=models.FloatField(null=True)
    PO_Based_Total_OH_sum_OPO=models.FloatField(null=True)
    Q0_Demand=models.FloatField(null=True)
    Q1_Demand=models.FloatField(null=True)
    Q2_Demand=models.FloatField(null=True)
    Q3_Demand=models.FloatField(null=True)
    Delta_Demand=models.FloatField(null=True)
    quarter_std_2=models.FloatField(null=True)
    quarter_std_1=models.FloatField(null=True)
    Delta_std=models.FloatField(null=True)
    quarter_demand_2_x_quarter_std_1=models.FloatField(null=True)
    quarter_demand_3_x_quarter_std_1=models.FloatField(null=True)
    quarter_demand_4_x_quarter_std_1=models.FloatField(null=True)
    Delta_Demand_x_quarter_std_1=models.FloatField(null=True)
    Delta_Demand_x_Delta_std=models.FloatField(null=True)
    Delta_Demand_x_Delta_std_per=models.FloatField(null=True)
    quarter_demand_1_x_quarter_std_1=models.FloatField(null=True)
    Annual_Demand=models.FloatField(null=True)
    quarter=models.CharField(max_length=255,null=True)
    Team=models.CharField(max_length=255,null=True)
    Contract_Mfr=models.CharField(max_length=255,null=True)

class Refreshed_top_component_Global_component(models.Model):
    quarter=models.CharField(max_length=255,null=True)
    Team=models.CharField(max_length=255,null=True)
    APN=models.CharField(max_length=255,null=True)
    Part_Desc=models.CharField(max_length=255,null=True)
    Ownership_JPE=models.CharField(max_length=255,null=True)
    Arista_PIC_JPE=models.CharField(max_length=255,null=True)
    PO_or_Delivery_JPE=models.CharField(max_length=255,null=True)
    CM_Buffer_On_Hand_JPE=models.FloatField(null=True)
    CM_Quantity_On_Hand_sum_CS_Inv_JPE=models.FloatField(null=True)
    Open_PO_due_in_Q_JPE=models.FloatField(null=True)
    Open_PO_due_in_Q1_JPE=models.FloatField(null=True)
    Delivery_Based_Total_OH_sum_OPO_JPE=models.FloatField(null=True)
    PO_Based_Total_OH_sum_OPO_JPE=models.FloatField(null=True)
    Q0_Demand_JPE=models.FloatField(null=True)
    Q1_Demand_JPE=models.FloatField(null=True)
    Q2_Demand_JPE=models.FloatField(null=True)
    Q3_Demand_JPE=models.FloatField(null=True)
    Annual_Demand_JPE=models.FloatField(null=True)
    Delta_Demand_JPE=models.FloatField(null=True)
    quarter_std_1_JPE=models.FloatField(null=True)
    Delta_Demand_x_quarter_std_1_JPE=models.FloatField(null=True)
    Ownership_SGD=models.CharField(max_length=255,null=True)
    Arista_PIC_SGD=models.CharField(max_length=255,null=True)
    PO_or_Delivery_SGD=models.CharField(max_length=255,null=True)
    CM_Buffer_On_Hand_SGD=models.FloatField(null=True)
    CM_Quantity_On_Hand_sum_CS_Inv_SGD=models.FloatField(null=True)
    Open_PO_due_in_Q_SGD=models.FloatField(null=True)
    Open_PO_due_in_Q1_SGD=models.FloatField(null=True)
    Delivery_Based_Total_OH_sum_OPO_SGD=models.FloatField(null=True)
    PO_Based_Total_OH_sum_OPO_SGD=models.FloatField(null=True)
    Q0_Demand_SGD=models.FloatField(null=True)
    Q1_Demand_SGD=models.FloatField(null=True)
    Q2_Demand_SGD=models.FloatField(null=True)
    Q3_Demand_SGD=models.FloatField(null=True)
    Annual_Demand_SGD=models.FloatField(null=True)
    Delta_Demand_SGD=models.FloatField(null=True)
    Delta_std_SGD=models.FloatField(null=True)
    quarter_std_1_SGD=models.FloatField(null=True)
    Delta_Demand_x_quarter_std_1_SGD=models.FloatField(null=True)
    Global_Annual_Demand_SGD=models.FloatField(null=True)
    Global_Spend_SGD=models.FloatField(null=True)
    Global_Spend_Percentage_SGD=models.FloatField(null=True)


class delete_log(models.Model):
    Arista_Part_Number=models.CharField(max_length=255,null=True)
    Quarter=models.CharField(max_length=255,null=True)
    cm=models.CharField(max_length=255,null=True)
    Number=models.CharField(max_length=255,null=True)
    Mfr_Name=models.CharField(max_length=255,null=True)
    Mfr_Part_Number=models.CharField(max_length=255,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    deleted_on=models.DateTimeField(auto_now_add=True,null=True)


class QuoteEmailNotification(models.Model):
    """
    This model stores email notified data
    """
    Arista_Part_Number = models.CharField(max_length=255,default=None,null=True)
    Arista_PIC = models.CharField(max_length=255,default=None,null=True)
    Mfr_Part_Number = models.CharField(max_length=255,default=None,null=True)
    Mfr_Name = models.CharField(max_length=255,default=None,null=True)
    Rfx_id = models.CharField(max_length=255,default=None,null=True)

    to = models.TextField(default=None,null=True)
    bp_email = models.TextField(default=None,null=True)
    created_at = models.TextField(default=None,null=True)
    created_by = models.TextField(default=None,null=True)
    team = models.CharField(max_length=255,default=None,null=True)
    sent_to = models.CharField(max_length=255,default=None,null=True)
    is_email_sent = models.BooleanField(default=False,null=True)
    is_quoted = models.BooleanField(default=False,null=True)
    is_locked = models.BooleanField(default=False,null=True)
    sgd_cm_email = models.TextField(default=None,null=True)
    jpe_cm_email = models.TextField(default=None,null=True)
    status = models.TextField(default=None,null=True) 
    cm  = models.CharField(max_length=50,default=None,null=True)
    current_url  = models.CharField(max_length=255,default=None,null=True)
    logged_in_user_group  = models.CharField(max_length=255, null=True,default=None)
    gsm_manager_email = models.TextField(default=None,null=True)
    director_email = models.TextField(default=None,null=True)
    approval_status_modified_by_role = models.CharField(max_length=255,default=None,null=True)
    fgn_cm_email = models.TextField(default=None,null=True)
    hbg_cm_email = models.TextField(default=None,null=True)
    jsj_cm_email = models.TextField(default=None,null=True)
    jmx_cm_email = models.TextField(default=None,null=True)
