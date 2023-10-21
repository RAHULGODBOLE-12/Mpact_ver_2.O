
from django.db import models
from django.forms.models import model_to_dict
from django_pandas.managers import DataFrameManager
from portfolio.models import Portfolio
from Slate_CMT.templatetags.cmt_helper import *
from django.db.models import Q
from django.contrib.auth.models import User,Group
from django.utils import timezone
from Supplier.models import suppliers_detail
from Slate_CMT.templatetags.masterprice_helper import *

###Split helper

def split_set(data=[{'id':None,'Item_Price':None,'Mfr_Name':None}]):
    '''
    --Suggested Split Logic--
    This will allocate the split for the MPN based on predefined formulas:
    this will return the id of rfx and split assigned with flag(used to decide the level of approval )
    * We Will consider only 3 parts based on the least Item_price
    1 Quote per APN:
        100% is the split value
    2 Quote per APN:
        delta=((greatest_Item_Price-lowerst_Item_Price)/lowerst_Item_Price)*100
        if delta is greater or equal to 3:Returns 50% for each
        if delta between 3 to 5:Returns 60% for lowest and 40% to greatest
        if delta greater than 5:Returns 80% for lowest and 20% to greatest
    3> Quote per APN:
        *Condiders only Least 3 Quotes
        Consider:v1 as lowest price,v2 as normal priceand v3 as greatest price
        delta1=((v2-v1)/v2)*100
        delta2=((v3-v1)/v3)*100
        if delta1<=3 and delta2<=3:
            return v1:34%,v2:33%,v3:33%
        elif 3<delta1<=5 and 3<delta2<=5:
            return v1:45%,v2:35%,v3:20%
        elif delta1>5 and delta2>5:
            return v1:80%,v2:20%,v3:0%
        elif delta1<=3 and 3<delta2<=5:
            return v1:40%,v2:40%,v3:20%
           
        elif 3<delta1<=5 and delta2>5:
            return v1:60%,v2:40%,v3:0%

        elif delta1<=3 and delta2>5:
            return v1:60%,v2:40%,v3:0%
        else :
            Undefined
    '''
    split=[]
    data_all=data.copy()
    data=data[:3]


    if len(data)==1:
        split.append({'id':data[0]['id'],'split':100,'flag':10})
        # send_logger_tele(f'''Single {data[0]['Mfr_Name']}''')

    elif len(data)==2:
        delta1=((data[1]['Item_Price']-data[0]['Item_Price'])/data[1]['Item_Price'])*100
        # send_logger_tele(f'''{delta1} Delta1 2''')
        print(delta1)
        if delta1<=3:
            split.append({'id':data[0]['id'],'split':50,'flag':10})
            split.append({'id':data[1]['id'],'split':50,'flag':10})
        elif 3<delta1<=5:
            split.append({'id':data[0]['id'],'split':60,'flag':10})
            split.append({'id':data[1]['id'],'split':40,'flag':20})
        elif delta1>5:
            split.append({'id':data[0]['id'],'split':80,'flag':10})
            split.append({'id':data[1]['id'],'split':20,'flag':30})
    elif len(data)==3:
        delta1=((data[1]['Item_Price']-data[0]['Item_Price'])/data[1]['Item_Price'])*100
        delta2=((data[2]['Item_Price']-data[0]['Item_Price'])/data[2]['Item_Price'])*100
        # # send_logger_tele(f'''lower {data[0]['Mfr_Name']}
        #                 {delta1} Delta1 3 {data[0]['Mfr_Name']}
        #                 {delta2} Delta2 3 {data[1]['Mfr_Name']}''')
        if delta1<=3 and delta2<=3:
            split.append({'id':data[0]['id'],'split':34,'flag':10})
            split.append({'id':data[1]['id'],'split':33,'flag':10})
            split.append({'id':data[2]['id'],'split':33,'flag':10})
        elif 3<delta1<=5 and 3<delta2<=5:
            split.append({'id':data[0]['id'],'split':45,'flag':10})
            split.append({'id':data[1]['id'],'split':35,'flag':20})
            split.append({'id':data[2]['id'],'split':20,'flag':20})
        elif delta1>5 and delta2>5:
            split.append({'id':data[0]['id'],'split':80,'flag':10})
            split.append({'id':data[1]['id'],'split':20,'flag':30})
            split.append({'id':data[2]['id'],'split':0,'flag':30})
        elif delta1<=3 and 3<delta2<=5:
            split.append({'id':data[0]['id'],'split':40,'flag':10})
            split.append({'id':data[1]['id'],'split':40,'flag':10})
            split.append({'id':data[2]['id'],'split':20,'flag':20})
        elif 3<delta1<=5 and delta2>5:
            split.append({'id':data[0]['id'],'split':60,'flag':10})
            split.append({'id':data[1]['id'],'split':40,'flag':20})
            split.append({'id':data[2]['id'],'split':0,'flag':30})
        elif delta1<=3 and delta2>5:
            split.append({'id':data[0]['id'],'split':60,'flag':10})
            split.append({'id':data[1]['id'],'split':40,'flag':10})
            split.append({'id':data[2]['id'],'split':0,'flag':30})
        else :
            print('No condition occurred')
            print(delta1,delta2)
            print(data)
            split=[]
        for x in data_all[3:]:
            split.append({'id':x['id'],'split':0,'flag':30})
    # send_logger_tele(str(split))
    return split

def std_generator(datas):
    '''
    Standard Cost Generator for CPN:
    This will sum up every(Iterate) parts MPN's Item_price*split(manual or suggested)/100
    and return the summed value  rounded by 5 decimals
    '''
    std_cost=0
    for part in datas:
        data=RFX.objects.get(id=part.id)
        print(data.Item_Price)
        qs=RFX.objects.filter(Quote_status='Quoted',sent_to=data.sent_to,sent_quater=data.sent_quater,quarter=data.quarter,Part_Number=data.Part_Number,cm=data.cm)
        if qs.filter(split_type='Manual').exists():
            std_cost+=float(data.Item_Price)*(float(data.manual_split or 0)/100)
            if qs.filter(split_type='Automated').exists():
                qs.update(split_type='Manual')
        else:
            std_cost+=float(data.Item_Price)*(float(data.suggested_split)/100)
    for part in datas:
        data=RFX.objects.filter(id=part.id)
        data.update(std_cost=round(std_cost,5))
    print('std_cost final',std_cost)
    return round(std_cost,5) 

def std_generator_bulk(datas_in):
    '''
    Standard Cost Generator for CPN(BULK Process):
    This will sum up every(Iterate) parts MPN's Item_price*split(manual or suggested)/100
    and return the summed value  rounded by 5 decimals
    '''
    for rq in datas_in:
        std_cost=0
        datas=RFX.objects.filter(
            quarter=rq.quarter,
            Part_Number=rq.Part_Number,
            cm=rq.cm,
            sent_to=rq.sent_to,
            Quote_status='Quoted',
            )
        for part in datas:
            data=RFX.objects.get(id=part.id)
            if  datas.filter(split_type='Manual').exists():
                if datas.filter(split_type='Automated').exists():
                    datas.update(split_type='Manual')
                try:std_cost+=float(data.Item_Price)*(float(data.manual_split or 0)/100)
                except:std_cost+=0
            else:
                try:std_cost+=float(data.Item_Price)*(float(data.suggested_split)/100)
                except:std_cost+=0
           
        for part in datas:
            data=RFX.objects.filter(id=part.id)
            data.update(std_cost=round(std_cost,5))
    return True
        

def Apply_split(APN,Team,cm,sent_to):
    '''
    Suggested Split
    Here we deside wether we need to consider the Qual Values or IPQ parts
    * if we have Qualified parts then we don't consider IPQ else we consider IPQ if not Qualified parts are there
    * This parts are send to split_set fuc and returns the split based on a predefined logic.
    * Standard Cost as been set based on the logic in std_generator function
    '''
    print('Apply_split')
    quarter=get_Next_quarter(q=3,this_quarter=True)
    for q in quarter:
        
        datas=RFX.objects.filter(Team=Team).filter(~Q(RFX_id=None) & Q(sent_quater=Current_quarter()) & Q(cm=cm) &Q(quarter=q)).filter(Part_Number=APN).filter(Quote_status='Quoted',portfolio__Qualification_Status='Qualified').order_by('Item_Price')
        # datas_flag=RFX.objects.filter(Team=Team).filter(~Q(RFX_id=None) & Q(sent_quater=Current_quarter()) & Q(cm=cm) &Q(quarter=q)).filter(Part_Number=APN).filter(portfolio__Qualification_Status='Qualified').order_by('Item_Price')
        all_qual=False
        if not datas.exists():
            datas=RFX.objects.filter(Team=Team).filter(~Q(RFX_id=None) & Q(sent_quater=Current_quarter()) & Q(cm=cm) &Q(quarter=q)).filter(Part_Number=APN).filter(Quote_status='Quoted').exclude(portfolio__Qualification_Status='Qualified').order_by('Item_Price')
            all_qual=True
        else:
            pass
            # RFX.objects.filter(Team=Team).filter(~Q(RFX_id=None) & Q(sent_quater=Current_quarter()) & Q(cm=cm) &Q(quarter=q)).filter(Part_Number=APN).filter(Quote_status='Quoted').filter(portfolio__Qualification_Status='In Process Qual').order_by('Item_Price').update(suggested_split=0)
        ###top 3 mfr divider
     
        mfr_top_3=list(datas.values('id','Item_Price','Mfr_Name','portfolio__Qualification_Status'))
        splits=split_set(mfr_top_3)
        if all_qual==False:
            ipq=RFX.objects.filter(Team=Team).filter(~Q(RFX_id=None) & Q(sent_quater=Current_quarter()) & Q(cm=cm) &Q(quarter=q)).filter(Part_Number=APN,Quote_status='Quoted').exclude(portfolio__Qualification_Status='Qualified').order_by('Item_Price')
            # ipq=RFX.objects.filter(Team=Team).filter(~Q(RFX_id=None) & Q(sent_quater=Current_quarter()) & Q(cm=cm) &Q(quarter=q)).filter(Part_Number=APN).filter(Quote_status='Quoted').filter(portfolio__Qualification_Status='In Process Qual').order_by('Item_Price')
            ipq=ipq.values('id','Item_Price','Mfr_Name','portfolio__Qualification_Status')
            for x in ipq:
                splits.append({'id':x['id'],'split':0,'flag':30})

        print('splits',splits)
        for_std=[]
        for split in splits:
            print('Split sets')
            data=RFX.objects.filter(id=split['id'])
            for_std.append(split['id'])
            print(datas.values_list('split_type',flat=True))
            if not 'Manual' in datas.values_list('split_type',flat=True) :

                data.update(
                suggested_split=split['split'],
                split_type='Automated',
                approval_flag=split['flag'],
                manual_split=0
                )
                if data.filter(Team__icontains='CMM Team').count():
                    return None
                if split['flag']==10 and split['split']!=0:
                    data.update(approval_status_PIC='Approval Pending',
                    approval_status_Manager='Approval No Need',
                    approval_status_Director='Approval No Need',
                    approval_status='PIC Approval Pending'
                    )
                elif split['flag']==20 and split['split']!=0:
                    data.update(approval_status_PIC='Approval Pending',
                    approval_status_Manager='Approval Pending PIC',
                    approval_status_Director='Approval No Need',
                    approval_status='PIC Approval Pending')
                elif split['flag']==30 and split['split']!=0:
                    data.update(approval_status_PIC='Approval Pending',
                    approval_status_Manager='Approval Pending PIC',
                    approval_status_Director='Approval Pending Manager',
                    approval_status='PIC Approval Pending')
                else :
                    data.update(
                    suggested_split=split['split'],
                    split_type='Automated',
                    manual_split=0
                    )
                    data.update(approval_status_PIC='Approval Pending',
                    approval_status_Manager='Approval No Need',
                    approval_status_Director='Approval No Need',
                    approval_status='PIC Approval Pending')
            else :
                data.update(
                suggested_split=split['split'],
                approval_flag=split['flag'],
                split_type='Manual',
                manual_split=0 if data[0].manual_split==None else data[0].manual_split,
                )
                if data[0].approval_status_PIC != 'Approved':
                    data.update(approval_status_PIC='Approval Pending')
        std=std_generator(RFX.objects.filter(id__in=for_std))
        

class Split_award(models.Model):
    ''' 
    This is a Model
    Which have the value for Supplier allocated split
    '''
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    share_award=models.BooleanField(default=False)
    share_time=models.DateTimeField(auto_now=True)
       

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
    val_COO=[None,"Mexico","China","USA","Vietnam","Indonesia","Malasiya","Philippines","Austria","Taiwan","Hungary","Singapore","Japan","Hong Kong","Korea","Thailand","Morocco","Germany","India","New Zealand","Texas","FR","DE","CR","SUZHOU","CN","N/A"]
    val_Life_Cycle=[None,"-","EOL","Active","Obsolete"]
    val_NCNR=[None,'-','Yes','No']
    val_PO_Delivery=['PO','Delivery']
    val_soft_hard_tool=[None,'-','Soft Tool','Hard Tool','Hybrid tool']
    val_Region=[None,"-","Taiwan","Hungary","Guadalajara",'Penang']
    val_Geo=[None,"-","APC","EMA","MEM"]
    objects = DataFrameManager()

    @property
    def award_debug(self):
        '''This will return final Split decided for this instance of RFX,This def is for internal'''
        from MasterPricing.models import MP_download_table,master_temp
        logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
        user=User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name=self.portfolio.Arista_PIC.split('/')[0])
        if logic_BP.lift_logic=='enable':
            if user:
                pic=user[0]
                award,created=Split_award.objects.get_or_create(user=pic) 
                if award.share_award and self.Shareable and self.portfolio.Team=='GSM Team':
                    if self.approval_status=='Approved':
                        if self.portfolio.cm=='Global':
                            MP_data = MP_download_table.objects.filter(Quarter=Current_quarter()).filter(Part_Number=self.Part_Number).filter(current_qtr_decision__isnull=False)
                            if MP_data.exists():
                                if self.split_type=='Manual':
                                    return self.manual_split,self.manual_split
                                else:
                                    return self.suggested_split,self.suggested_split
                            else:
                                return 'Descion pending in MP (Global)',None
                                # return None
                                    
                        else:
                            MP_data = MP_download_table.objects.filter(Quarter=Current_quarter()).filter(Part_Number=self.Part_Number).filter(current_qtr_decision__isnull=False,CM_download=self.cm)
                            if MP_data.exists():
                                if self.split_type=='Manual':
                                    return self.manual_split,self.manual_split
                                else:
                                    return self.suggested_split,self.suggested_split
                            else:
                                return f'Descion pending in MP ({self.cm})',None
                                # return None
                    else:
                        return 'PIC Approval Pending',None
                else:
                    return 'PIC Not Shared',None
                    # return None
            else:
                return 'PIC Name is not valid',None
                # return None
        else:
            return 'Mp need to lock',None
            # return None
    @property
    def award(self):
        '''This will return final Split decided for this instance of RFX,This def is for only Supplier'''
        debug,split=self.award_debug
        return split
    @property
    def award_pid(self):
        '''This will return final Split decided for this instance of RFX,This def is for only Customer'''
        debug,split=self.award_debug
        return debug



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
        if not (self.Life_Cycle in self.val_Life_Cycle or  self.Life_Cycle==None):
            '''Check if this is valid based on the predefined values'''
            raise ValueError('Invalid Data for Lifecycle_Phase')
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

        if self.portfolio.Ownership=='Arista':
            '''for Customer part we make some calculation for po_delivery based on the count of po and delivery
             If count of delivery is greater than deivery than delivery will be returned else PO
            '''
            self.po_delivery=get_po_delivery_calc(self.id)
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


class send_fx_queue_logger(models.Model):
    to_create_count=models.IntegerField(null=True)
    Created_count=models.IntegerField(null=True)
    created_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_on=models.DateTimeField(auto_now=True)
    modified_on=models.DateTimeField(auto_now_add=True)
    error=models.TextField(max_length=1000,default='No Error')
    def __str__(self):
        return f'''to_create_count: {self.to_create_count}   Created_count: {self.Created_count}   created_by: {self.created_by} Error: {False if self.error == 'No Error' else True }'''

def create_history(model_name=None,model_id=None,key=None,data_dict=None,value=None,comment=None,user=None):
    '''This will create the history of the rfx based on the data dict'''
    if model_name=='RFX':
        instance=Master_history_rfx(model_id=model_id,data_dict=data_dict,comment=comment,modified_by=user)
        instance.save()
        return instance

class Master_history_rfx(models.Model):
    '''This table stores all the changes which made in RFX Table'''
    model_id=models.ForeignKey(RFX,on_delete=models.CASCADE,null=True)
    key=models.CharField(max_length=255,null=False)
    value=models.CharField(max_length=255,null=False)
    data_dict=models.TextField(null=False)
    def _convert_to_dict(self):
        return eval(self.data_dict)
    data_dict_as_dict = property(_convert_to_dict)
    comment=models.TextField(null=False)
    modified_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,editable=False)
    modified_by_email=models.EmailField(null=True)
    modified_on=models.DateTimeField(auto_now=True,null=False)  

    def save(self,user=None, *args, **kwargs):
        if not user==None:
            self.modified_by=user
            self.modified_by_email=user.email
        super(Master_history_rfx, self).save(*args, **kwargs) 

class LockAccessEmailNotification(models.Model):
    """
    This model stores email notified data
    """
    Arista_Part_Number = models.CharField(max_length=255,default=None,null=True)
    Mfr_Part_Number = models.CharField(max_length=255,null=True)
    Mfr_Name = models.CharField(max_length=255,default=None,null=True)
    Arista_PIC = models.CharField(max_length=255,default=None,null=True)
    team = models.CharField(max_length=255,default=None,null=True)
    cm  = models.CharField(max_length=50, null=True,default=None)
    sent_to = models.CharField(max_length=255,default=None,null=True)
    lock_status = models.BooleanField(default=False,null=True)
    status_updated_by = models.TextField(default=None,null=True)
    created_at = models.TextField(default=None,null=True)
    is_email_sent = models.BooleanField(default=False,null=True)
    to = models.TextField(default=None,null=True)
    supplier_email = models.TextField(default=None,null=True)
    sgd_cm_email = models.TextField(default=None,null=True)
    jpe_cm_email = models.TextField(default=None,null=True)
    fgn_cm_email = models.TextField(default=None,null=True)
    hbg_cm_email = models.TextField(default=None,null=True)
    jsj_cm_email = models.TextField(default=None,null=True)
    jmx_cm_email = models.TextField(default=None,null=True)
    rfx_id = models.CharField(max_length=255,default=None,null=True)
    current_url  = models.CharField(max_length=255,default=None,null=True)
    logged_in_user_group  = models.CharField(max_length=255, null=True,default=None)
    
    

class RfqCountData(models.Model):
    """
    This model stores email notified data
    """
    Arista_Part_Number = models.CharField(max_length=255,default=None,null=True)
    Mfr_Part_Number = models.CharField(max_length=255,null=True)
    Mfr_Name = models.CharField(max_length=255,default=None,null=True)
    Arista_PIC = models.CharField(max_length=255,default=None,null=True)
    team = models.CharField(max_length=255,default=None,null=True)
    Total_ARISTA_Part_Count  = models.CharField(max_length=255, null=True,default=None)
    Total_Part_Count = models.CharField(max_length=255,default=None,null=True)
    RFQ_Initiated = models.CharField(max_length=255,default=None,null=True)
    RFQ_NOT_Initiated = models.CharField(max_length=255,default=None,null=True)
    Quoted = models.CharField(max_length=255,default=None,null=True)
    Non_Quoted = models.CharField(max_length=255,default=None,null=True)
    No_BID = models.CharField(max_length=255,default=None,null=True)
    Locked = models.CharField(max_length=255,default=None,null=True)
    Unlocked = models.CharField(max_length=255,default=None,null=True)
    Award_Set = models.CharField(max_length=255,default=None,null=True)
    commodity = models.CharField(max_length=255,default=None,null=True)
    Not_To_Award = models.CharField(max_length=255,default=None,null=True)
    dtmLastUpdate = models.DateTimeField(auto_now=True,null=False)  
    LastUpdatedBy = models.CharField(max_length=255,default=None,null=True)
    Chart_Name = models.CharField(max_length=255,default=None,null=True)
    Remarks = models.TextField(default=None,null=True)
    DevRemarks = models.TextField(default=None,null=True)
    Deleted = models.CharField(max_length=255,default=None,null=True)


class predefined_filter(models.Model):
    'predefined_filter table is to store the filter excel which the user save as predefined'
    name=models.CharField(max_length=255,null=True)
    data=models.TextField(default='No Error')
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True)

class Split_award(models.Model):
    ''' 
    This is a Model
    Which have the value for Supplier allocated split
    '''
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    share_award=models.BooleanField(default=False)
    share_time=models.DateTimeField(auto_now=True)

class CM_Quotes(models.Model):
    """
    This model stores CMM Team Quotes Details
    """
    rfq_id=models.CharField(max_length=255,default=None,null=True)
    Item_Price=models.FloatField(null=True)
    Lead_Time=models.IntegerField(null=True)
    MOQ=models.IntegerField(null=True)
    List=models.CharField(max_length=255,null=True,default=' ')
    tarrif=models.CharField(max_length=255,null=True,default=' ')
    NCNR=models.CharField(max_length=255,null=True,default='-')
    PO_Delivery=models.CharField(max_length=255,null=True)
    suggested_split=models.FloatField(null=True)
    arista_suggested=models.FloatField(null=True)
    manual_split=models.FloatField(null=True)
    std_cost=models.FloatField(null=True)
    CM_comments=models.TextField(null=True,default=' ')
    arista_comments=models.TextField(null=True,default='')
    Supplier_Distributor_name_from_cm=models.TextField(null=True)
    CM_Manufacturer=models.TextField(null=True)
    CM_mpn=models.TextField(null=True)
    split_type=models.CharField(max_length=255,null=True,default='Automated')
    Quote_status=models.CharField(max_length=255,null=True,default='Non Quoted')