from django.db import models

from django.db import models
from django.forms.models import model_to_dict
from django_pandas.managers import DataFrameManager
from portfolio.models import Portfolio
from Slate_CMT.templatetags.cmt_helper import *
from django.db.models import Q
from django.contrib.auth.models import User,Group
from django.utils import timezone
from Supplier.models import suppliers_detail
# Create your models here.

class RFX(models.Model):
    ''' 
    This is The Main TABLE FOR RFQ Data(Quote Data)
    
    '''
    RFX_id=models.CharField(max_length=255,unique=True,null=True)       #Unique id Based Part, Mfr_Name, Quarter, 
    quarter=models.CharField(max_length=255,null=True)      #Sent Quarter
    sent_to=models.CharField(max_length=255,null=True)      #This field indicates if the quote is for supplier or Distributor or CM
    Part_Number=models.CharField(max_length=255,null=True)      #CPN
    Mfr_Part_Number=models.CharField(max_length=255,null=True)
    Mfr_Name=models.CharField(max_length=255,null=True)     #Manufacture Name
    cm=models.CharField(max_length=255,null=True)   #Cm Site
    Arista_pic_comment=models.CharField(max_length=255,null=True)
    ###Form Field
    Item_Price=models.FloatField(null=True)     #form field(external)
    Lead_Time=models.IntegerField(null=True)    #form field(external)
    MOQ=models.IntegerField(null=True)         #form field(external)
    List=models.CharField(max_length=255,null=True,default=' ')      #form field(external)
    tarrif=models.CharField(max_length=255,null=True,default=' ')       #form field(external)
    COO=models.CharField(max_length=255,null=True)       #form field(external)      
    Inco_Term=models.CharField(max_length=255,null=True,default='-')       #form field(external)
    MPQ=models.IntegerField(null=True)       #form field(external)
    Assembly_cost=models.FloatField(null=True)       #form field(external)
    Freight_cost=models.FloatField(null=True)       #form field(external)
    Masked_Price=models.FloatField(null=True)       #form field(external)
    Quote_Type=models.CharField(max_length=255,null=True)   #Indicate if Quote is Global or Reginal
    Region=models.CharField(max_length=255,null=True,default='-')       #form field(external)
    Geo=models.CharField(max_length=255,null=True,default='-')      #form field(external)
    Life_Cycle=models.CharField(max_length=255,null=True,default='-')   #form field(external)
    Comments=models.TextField(null=True,max_length=1000,default=' ')    #form field(external)
    Quote_status=models.CharField(max_length=255,null=True,default='Non Quoted')        #Status of the quote
    sent_quater=models.CharField(max_length=255,null=True,default=Current_quarter)      #Quote raised quarter
    portfolio=models.ForeignKey(Portfolio,on_delete= models.PROTECT,null=True)  #Portfolio which has all data related to rfx (Parent of this Quote),Protected field need to delete the child to delete the Parent (it wont cascade)
    created_by=models.ForeignKey(User,on_delete= models.PROTECT,null=True) #User who created this Quote,Protected field need to delete RFQ to delete the User (it wont cascade)
    Quoted_by=models.CharField(max_length=255,null=True) #Details who quote 'Name: {user.first_name}, email: {user.email}, Type:{supplier/distributor/cm}, Date: {timezone.localtime(timezone.now()).strftime('%m/%d/%Y, %H:%M:%S')}'''
    modified_on=models.DateTimeField(auto_now=True,null=True)  #dynamic datetime
    created_on=models.DateTimeField(auto_now_add=True,null=True) #dynamic datetime
    quote_is_writable=models.BooleanField(default=True)  #Bool which indicate if the Quote is still open to Quote
    quote_freeze=models.BooleanField(default=False) #Bool which indicate if the Quote is still open to Quote
    NCNR=models.CharField(max_length=255,null=True,default='-') #form field(external)
    Team=models.CharField(max_length=255,null=True)     #denotes team if GSM or CMM
    PO_Delivery=models.CharField(max_length=255,null=True)  #form field(external)
    soft_hard_tool=models.CharField(max_length=255,null=True,default='-') #form field(external)
    suggested_split=models.FloatField(null=True) #Auto genrated filed based on split logic
    manual_split=models.FloatField(null=True)   #manual split based on the PIC changes
    previous_split=models.FloatField(null=True) #previous Quarter split
    split_type=models.CharField(max_length=255,null=True) #Type of the current split use this to generate Standard Cost
    approval_flag=models.CharField(max_length=255,null=True) #level of approval
    approval_status_PIC=models.CharField(max_length=255,null=True) #approval status PIC
    approval_status_Manager=models.CharField(max_length=255,null=True)  #approval status Manager
    approval_status_Director=models.CharField(max_length=255,null=True) #approval status Director
    approval_status=models.CharField(max_length=255,null=True) #overall All Approval Status
    split_comments=models.TextField(null=True) #overall Manual Split Comments
    PIC_accept_reject_comments=models.TextField(null=True) #PIC accept or reject Comments
    approval1_comments=models.TextField(null=True) #accept or reject Comments
    approval2_comments=models.TextField(null=True) #accept or reject Comments
    std_cost=models.FloatField(null=True)   #Standard Cost of the CPN
    CM_comments_on_Justifing_price=models.TextField(null=True,default=' ')  #CM comments on Justifing price
    Supplier_Distributor_name_from_cm=models.TextField(null=True) #CM comments on Justifing price
    CM_Notes_on_Supplier=models.TextField(null=True) #CM Notes on Supplier
    ##for ony cm
    CM_Manufacturer=models.TextField(null=True) #form field(cm)
    CM_mpn=models.TextField(null=True) #form field(cm)
    CM_buyer=models.TextField(null=True) #form field(cm)
    CM_qty_std_source=models.TextField(null=True,default=' ') #form field(cm)
    ###for master priceing
    po_delivery = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    new_po_price = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    current_final_std_cost = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    current_updated_std_cost = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    current_qtr_decision = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    approve_reject_std_price = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    cm_approve_reject = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    arista_pic_approve_reject = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    bp_team_approve_reject = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    standard_price_q1 = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    arista_pic_updated_data_name = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    cm_updated_data_name = models.CharField(max_length=255, blank=True, null=True)  ##Not in use for any logic(Moved to Master Pricing)
    due_date = models.DateField(null=True) ##Due date for the Supplier or distributor


    ####comments
    BP_team_Approve_Reject_Comments = models.TextField(null=True)  ##Not in use for any logic(Moved to Master Pricing)
    Arista_PIC_Comments_to_CM=models.TextField(null=True)  ##Not in use for any logic(Moved to Master Pricing)
    Arista_BP_Comments=models.TextField(null=True)  ##Not in use for any logic(Moved to Master Pricing)
    CM_Additional_Notes_on_Supplier_distributor=models.TextField(null=True)  ##Not in use for any logic(Moved to Master Pricing)
    CM_PO_Delivery_Remarks=models.TextField(null=True)  ##Not in use for any logic(Moved to Master Pricing)
    ####award letter
    notified=models.BooleanField(default=False,null=True) ##If Split Award is sent to supplier or not
    notified_status=models.CharField(max_length=255, null=True) ##Split Award notified_status
    last_notified_on=models.DateTimeField(null=True) ##Split Award notified sent time
    Shareable=models.BooleanField(default=True) ##Split Award notified sent time

    #######for validation variables
    val_Inco_Term=[None,"CFR","CIF","CIP","CPT","DAF","DAP","DAT","DDP","DDU","DEQ","DES","EXG","EXW","FAS","FCA","FH","FOB","FOC","FOR","FOT","FRD","HC",'N/A' ]
    val_Life_Cycle=[None,"-","EOL","Active","Obsolete"]
    val_NCNR=[None,'-','Yes','No']
    val_PO_Delivery=['PO','Delivery']
    val_soft_hard_tool=[None,'-','Soft Tool','Hard Tool','Hybrid tool']
    val_Region=[None,"-","Taiwan","Hungary","Guadalajara",'Penang']
    val_Geo=[None,"-","APC","EMA","MEM"]
    objects = DataFrameManager()

    def save(self,user=None,Quote=False, *args, **kwargs):
        '''
        Overloaded Save()
        here we check some criteria before we save the instance

        '''
        ##############Pre SAVE##############
        if self.id:
            '''Create data for history'''
            data=RFX.objects.get(id=self.id)
            old_data=model_to_dict(data)

            new=False
            # del old_data['modified_on']
        else:
            old_data={}
            new=True
        if Quote:
            '''If this from supplier,fetch their deatils and create data for `Quoted_by` field'''
            suppliers=suppliers_detail.objects.filter(Email=user.email)
            if suppliers:
                user_type='Distributor' if suppliers[0].Distributor else 'Supplier'
                distri_name=f", {suppliers[0].Distributor}" if suppliers[0].Distributor else ''
            else:
                user_type=user.groups.first() and user.groups.first().name
                if not user_type:
                    user_type='Arista'
                distri_name=''
            self.Quoted_by=f'''Name: {user.first_name}{distri_name}, email: {user.email}, Type:{user_type}, Date: {timezone.localtime(timezone.now()).strftime('%m/%d/%Y, %H:%M:%S')}'''
            
        PO_Delivery=self.val_PO_Delivery
        soft_hard_tool=self.val_soft_hard_tool
        if self.Freight_cost:
            '''Check if this is valid float or int field and raise error based on the errors'''
            try:self.Freight_cost=round(float(self.Freight_cost),5)
            except:raise ValueError('Invalid Data for Freight cost')
        else :
            self.Freight_cost=None
        self.Part_Number=self.portfolio.Number
        self.Mfr_Part_Number=self.portfolio.Mfr_Part_Number
        self.Mfr_Name=self.portfolio.Mfr_Name
        self.Team=self.portfolio.Team
        if Quote:
            if not self.sent_to=='cm' and not self.Item_Price==None:
                if not (self.Inco_Term in self.val_Inco_Term):
                    '''Check if this is valid based on the predefined values'''
                    raise ValueError('Invalid Data for Inco Term')
        #if not (self.Life_Cycle in self.val_Life_Cycle or  self.Life_Cycle==None):
        #    '''Check if this is valid based on the predefined values'''
        #    raise ValueError('Invalid Data for Lifecycle_Phase')
        if not (self.NCNR in self.val_NCNR or  self.NCNR==None):
            '''Check if this is valid based on the predefined values'''
            raise ValueError('Invalid Data for NCNR')
        if not (self.PO_Delivery in PO_Delivery or  self.PO_Delivery==None):
            '''Check if this is valid based on the predefined values'''
            raise ValueError('Invalid Data for PO or Delivery')
        if not (self.soft_hard_tool in soft_hard_tool or  self.soft_hard_tool==None):
            '''Check if this is valid based on the predefined values'''
            raise ValueError('Invalid Data for soft tool or hard_tool')
        if not self.Item_Price==None:
            '''Check if this is valid float or int field and raise error based on the errors'''
            print('Item Price',self.Item_Price)
            try:self.Item_Price=round(float(self.Item_Price),5)
            except:raise ValueError('Invalid data for Item Price')
            if Quote:negative_validator(self.Item_Price,message='Item Price')
        if self.MOQ!=None:
            '''Check if this is valid based on the predefined values'''
            try:self.MOQ=int(self.MOQ)
            except:raise ValueError('Invalid data for MOQ')
            if Quote:negative_validator(self.MOQ,message='MOQ')
        if self.Lead_Time!=None:
            '''Check if this is valid float or int field and raise error based on the errors'''
            try:self.Lead_Time=int(self.Lead_Time)
            except:raise ValueError('Invalid data for Lead_Time')
            if Quote:negative_validator(self.Lead_Time,message='Lead Time')
        self.cm=self.portfolio.cm
        if self.Quote_Type=="Global":
            self.Region='No Need'
            self.Geo='No Need'
        elif self.Quote_Type=="Regional" :
            if not (self.Region in self.val_Region or self.Region== None):
                '''Check if this is valid based on the predefined values'''
                raise ValueError('Invalid Data for Region')
            if not (self.Geo in self.val_Geo or self.Geo==None):
                '''Check if this is valid based on the predefined values'''
                raise ValueError('Invalid Data for Geo ')
        if not self.RFX_id:
            '''Create RFX_id based on the the below condition give which is self explanatory'''
            self.RFX_id = f'''RFX_{self.sent_quater}_{self.quarter}_{self.cm}_{self.Mfr_Name}_{self.Mfr_Part_Number}_{self.Part_Number}_{self.Team}_to_{self.sent_to}'''
        print(self.quote_is_writable and has_permission(user,"Supplier"))
        if (not self.quote_is_writable) and has_permission(user,"Supplier"):
            '''check if the quote is open and if not just raise error'''
            raise PermissionError('You have No permission to quote')
     
        if self.Item_Price==None and self.Quote_status!='No BID':
            self.Quote_status='Non Quoted'
        if self.Quote_status=='No BID':
            print('####No bid#####')
            '''set quote as NO Bid and empty the fields'''
            self.suggested_split=None
            self.std_cost=None
            self.split_type=None
            
            ###Resetting to Automated split for all parts
            RFX.objects.filter(
                Part_Number=self.Part_Number,
                cm=self.cm,
                sent_quater=self.sent_quater,
            ).update(split_type='Automated',manual_split=None)
            
        if self.std_cost:
            '''Converting std_cost to float safer side'''
            print('self.std_cost',self.std_cost)
            try:
                self.std_cost=float(self.std_cost)
            except:
                self.std_cost=None
        from CMT import masterprice_helper
        if self.portfolio.Ownership=='Arista':
            '''for Customer part we make some calculation for po_delivery based on the count of po and delivery
             If count of delivery is greater than deivery than delivery will be returned else PO
            '''
            self.po_delivery=masterprice_helper.get_po_delivery_calc(self.id)
        else:
            self.po_delivery=self.PO_Delivery
        ###acessing the original function and save them using super class with current post save calculation 
        super(RFX, self).save(*args, **kwargs) 
        ####################POST SAVE######################
        data=RFX.objects.get(id=self.id)
        ###get the newly created objects
        if not self.quote_freeze or self.suggested_split==None :
            if data.Quote_status=='Quoted' or data.Quote_status=='No BID' :
                print('split applied')
                # if data.Team=='GSM Team':
                ####Call the Suggested Split funtion to set the Suggested slit if quoted
                Apply_split(data.Part_Number,data.Team,data.cm,data.sent_to)
        new_data=model_to_dict(data)
        if not new:
            ###if this is not a newly created instace then save the old values to history data based on the changes values
            if not (old_data==new_data and old_data['Quote_status']=='Non Quoted'):
                data_old,data_new=compare_values_dict(old_data,new_data)
                create_history(model_name='RFX',model_id=data,data_dict=str(old_data),comment=f'Changed values :{data_new}',user=user)