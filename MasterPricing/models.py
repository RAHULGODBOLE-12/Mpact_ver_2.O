from django.db import models
from django_pandas.managers import DataFrameManager
from portfolio.models import Portfolio
from rfx.models import *
from django_pandas.managers import DataFrameManager
# Create your models here.
from django.contrib.auth.models import User,Group

from django.core.mail import EmailMessage
from email.utils import make_msgid
import email
from django.core.mail import message
from django.template.loader import get_template
from django.conf import settings
from pytz import timezone
from datetime import timedelta
import datetime
from rfx.models import *

class MPTemplate(models.Model):
    cm_partno = models.CharField(max_length=100, blank=True, null=True)
    arista_partno = models.CharField(max_length=50, blank=True, null=True)
    consign_partno = models.CharField(max_length=50, blank=True, null=True)
    controlby = models.CharField(max_length=50, blank=True, null=True)
    arista_pic = models.CharField(max_length=50, blank=True, null=True)
    item_desc = models.CharField(max_length=300, blank=True, null=True)
    po_delivery = models.CharField(max_length=50, blank=True, null=True)
    qty_buffer_oh = models.CharField(max_length=50, blank=True, null=True)
    oh_plus_cs_inv = models.CharField(max_length=50, blank=True, null=True)
    openpo_current_qtr = models.CharField(max_length=50, blank=True, null=True)
    openpo_next_qtr = models.CharField(max_length=50, blank=True, null=True)
    po_based_total_oh_opo = models.CharField(max_length=50, blank=True, null=True)
    delivery_based_total_oh_opo = models.CharField(max_length=50, blank=True, null=True)
    prev_qtr_demand = models.CharField(max_length=50, blank=True, null=True)
    current_qtr_demand = models.CharField(max_length=50, blank=True, null=True)
    next_qtr_demand = models.CharField(max_length=50, blank=True, null=True)
    next_qtr_1_demand = models.CharField(max_length=50, blank=True, null=True)
    netdemand_po_delivery_based = models.CharField(max_length=50, blank=True, null=True)
    damage_coverage = models.CharField(max_length=50, blank=True, null=True)
    current_final_std_cost = models.CharField(max_length=50, blank=True, null=True)
    current_updated_std_cost = models.CharField(max_length=50, blank=True, null=True)
    current_qtr_decision = models.CharField(max_length=50, blank=True, null=True)
    current_qtr_arista_pic_comments = models.CharField(max_length=1000, blank=True, null=True)
    current_qtr_cm_comments = models.CharField(max_length=1000, blank=True, null=True)
    quote_qtr_price_value_history = models.CharField(max_length=50, blank=True, null=True)
    who_when_why = models.CharField(max_length=1000, blank=True, null=True)
    price_delta = models.CharField(max_length=50, blank=True, null=True)
    blended_avg_po_price = models.CharField(max_length=50, blank=True, null=True)
    new_po_price = models.CharField(max_length=50, blank=True, null=True)
    approve_reject_std_price = models.CharField(max_length=50, blank=True, null=True)
    cm_approve_reject = models.CharField(max_length=50, blank=True, null=True)
    arista_pic_approve_reject = models.CharField(max_length=50, blank=True, null=True)
    bp_team_approve_reject = models.CharField(max_length=50, blank=True, null=True)
    standard_price_q1 = models.CharField(max_length=50, blank=True, null=True)
    mfr_name_q1 = models.CharField(max_length=200, blank=True, null=True)
    mpn_q1 = models.CharField(max_length=100, blank=True, null=True)
    revision_q1 = models.CharField(max_length=50, blank=True, null=True)
    lifecycle_phase_q1 = models.CharField(max_length=50, blank=True, null=True)
    qual_status_q1 = models.CharField(max_length=50, blank=True, null=True)
    quoted_price_q1 = models.CharField(max_length=50, blank=True, null=True)
    split_q1 = models.CharField(max_length=50, blank=True, null=True)
    mfr_lt_q1 = models.CharField(max_length=50, blank=True, null=True)
    mfr_moq_q1 = models.CharField(max_length=50, blank=True, null=True)
    ncnr_q1 = models.CharField(max_length=50, blank=True, null=True)
    coo_q1 = models.CharField(max_length=50, blank=True, null=True)
    inco_terms_q1 = models.CharField(max_length=50, blank=True, null=True)
    mpn_level_po_delivery_q1 = models.CharField(max_length=50, blank=True, null=True)
    soft_hard_tool_q1 = models.CharField(max_length=50, blank=True, null=True)
    freight_cost_q1 = models.CharField(max_length=50, blank=True, null=True)
    supplier_comments_for_quote_q1 = models.CharField(max_length=1000, blank=True, null=True)
    arista_pic_comments_for_quote_q1 = models.CharField(max_length=1000, blank=True, null=True)
    quoted_by_arista = models.CharField(max_length=200, blank=True, null=True)
    cm_mfr_name_q1 = models.CharField(max_length=200, blank=True, null=True)
    cm_mpn_q1 = models.CharField(max_length=100, blank=True, null=True)
    cm_revision_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_lifecycle_phase_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_qual_status_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_quoted_price_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_moq_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_lt_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_ncnr_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_coo_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_inco_terms_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_freight_cost_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_mpn_level_po_delivery_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_soft_hard_tool_q1 = models.CharField(max_length=50, blank=True, null=True)
    cm_comments_on_justifing_price_q1 = models.CharField(max_length=1000, blank=True, null=True)
    sup_disti_name_from_cm_q1 = models.CharField(max_length=200, blank=True, null=True)
    cm_aditional_notes_q1 = models.CharField(max_length=1000, blank=True, null=True)
    cm_arista_pic_comments_q1 = models.CharField(max_length=1000, blank=True, null=True)
    cm_quoted_by = models.CharField(max_length=200, blank=True, null=True)
    ownership  = models.CharField(max_length=50, blank=True, null=True)
    quarter  = models.CharField(max_length=50, blank=True, null=True)
    cm  = models.CharField(max_length=50, blank=True, null=True)
    sent_to = models.CharField(max_length=50,null=True)
    List = models.CharField(max_length=50,null=True)
    tarrif = models.CharField(max_length=50,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    objects = DataFrameManager()

class master_temp(models.Model):
    lift_logic = models.CharField(max_length=50,null=True)
    quarter = models.CharField(max_length=50,null=True)
    user_modified=models.ForeignKey(User,on_delete= models.CASCADE,null=True)
    Team = models.CharField(max_length=50,null=True)
    
class EmailNotification(models.Model):
    """
    This model stores email notified data
    """
    Arista_Part_Number = models.CharField(max_length=255,default=None)
    Mfr_Part_Number = models.CharField(max_length=255,null=True)
    Mfr_Name = models.CharField(max_length=255,default=None,null=True)
    Arista_PIC = models.CharField(max_length=255,default=None)
    team = models.CharField(max_length=255,default=None)
    cm  = models.CharField(max_length=50, null=True,default=None)

    logged_in_user_group  = models.CharField(max_length=255, null=True,default=None)

    sent_to = models.CharField(max_length=255,default=None)
    ownership  = models.CharField(max_length=50, blank=True, null=True)
    current_qtr_decision = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.TextField(default=None,null=True)
    created_at = models.TextField(default=None,null=True)
    is_email_sent = models.BooleanField(default=False)
    to = models.TextField(default=None,null=True)
    bp_email = models.TextField(default=None,null=True)
    sgd_cm_email = models.TextField(default=None,null=True)
    jpe_cm_email = models.TextField(default=None,null=True)
    gsm_manager_email = models.TextField(default=None,null=True)
    rfx_id = models.CharField(max_length=255,default=None,null=True)
    current_url  = models.CharField(max_length=255,default=None,null=True)
    fgn_cm_email = models.TextField(default=None,null=True)
    hbg_cm_email = models.TextField(default=None,null=True)
    jsj_cm_email = models.TextField(default=None,null=True)
    jmx_cm_email = models.TextField(default=None,null=True)


from django.db import connection
conn=connection.cursor()
Processing_list_MP_trigger='''
CREATE OR REPLACE FUNCTION create_Processing_list_MP() RETURNS trigger AS
$$
declare
   	partcount INT;
BEGIN
    
    IF (TG_OP = 'DELETE') THEN
		select count(*) into partcount from "rfx_rfx" where "Part_Number"=old."Part_Number" AND "cm"=old."cm" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter";
		/*IF (partcount=0) THEN
			IF (old."cm"='Global') THEN
					DELETE from "MasterPricing_mp_download_table" WHERE "Part_Number"=old."Part_Number" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter" AND "CM_download"='SGD' ;
					DELETE from "MasterPricing_mp_download_table" WHERE "Part_Number"=old."Part_Number" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter" AND "CM_download"='JPE' ;
					DELETE from "MasterPricing_mp_download_table" WHERE "Part_Number"=old."Part_Number" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter" AND "CM_download"='FGN' ;
					DELETE from "MasterPricing_mp_download_table" WHERE "Part_Number"=old."Part_Number" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter" AND "CM_download"='HBG' ;
					DELETE from "MasterPricing_mp_download_table" WHERE "Part_Number"=old."Part_Number" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter" AND "CM_download"='JSJ' ;
					DELETE from "MasterPricing_mp_download_table" WHERE "Part_Number"=old."Part_Number" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter" AND "CM_download"='JMX' ;
			ELSE 
				DELETE from "MasterPricing_mp_download_table" WHERE "Part_Number"=old."Part_Number" AND "sent_quater"=old."sent_quater" AND "quarter" = old."quarter" AND "CM_download"=old."cm" ;
			END if;
		END if;*/
		
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Part_Number",'SGD');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Part_Number",'JPE');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Part_Number",'FGN');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Part_Number",'HBG');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Part_Number",'JSJ');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Part_Number",'JMX');
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Part_Number",'SGD');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Part_Number",'JPE');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Part_Number",'FGN');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Part_Number",'HBG');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Part_Number",'JSJ');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Part_Number",'JMX');
        RETURN NEW;
    END IF;
EXCEPTION
		when others then
		RETURN NEW;
END;
$$
LANGUAGE plpgsql;
'''

Processing_list_MP_trigger_trigger=''' 
CREATE  TRIGGER create_Processing_list_MP_trigger
AFTER INSERT OR UPDATE OR DELETE ON  rfx_rfx FOR EACH ROW EXECUTE PROCEDURE create_Processing_list_MP();
'''
Processing_list_MP_trigger_portfolio='''
CREATE OR REPLACE FUNCTION create_Processing_list_MP_portfolio() RETURNS trigger AS
$$
declare
BEGIN
    
    IF (TG_OP = 'DELETE') THEN
		
		
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Arista_Part_Number",'SGD');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Arista_Part_Number",'JPE');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Arista_Part_Number",'FGN');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Arista_Part_Number",'HBG');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Arista_Part_Number",'JSJ');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(old."Arista_Part_Number",'JMX');
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Arista_Part_Number",'SGD');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Arista_Part_Number",'JPE');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Arista_Part_Number",'FGN');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Arista_Part_Number",'HBG');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Arista_Part_Number",'JSJ');
        INSERT INTO "MasterPricing_processing_list_mp" ("Part_Number","cm") VALUES(new."Arista_Part_Number",'JMX');
        RETURN NEW;
    END IF;
EXCEPTION
		when others then
		RETURN NEW;
END;
$$
LANGUAGE plpgsql;
'''
Processing_list_MP_trigger_portfolio_trigger='''
CREATE TRIGGER create_Processing_list_MP_portfolio_trigger
AFTER INSERT OR UPDATE OR DELETE ON  portfolio_portfolio FOR EACH ROW EXECUTE PROCEDURE create_Processing_list_MP_portfolio();
'''

try:
    conn.execute(Processing_list_MP_trigger)
    print('function created')
    conn.execute(Processing_list_MP_trigger_trigger)
    print('Trigger created')
except Exception as e:
    print(e)
try:
    conn.execute(Processing_list_MP_trigger_portfolio)
    print('function created')
    conn.execute(Processing_list_MP_trigger_portfolio_trigger)
    print('Trigger created')
except Exception as e:
    print(e)


class Processing_list_MP(models.Model):
   
    Part_Number=models.TextField(null=False)
    cm=models.TextField(null=False)
    # class Meta:
    #     unique_together = ('Part_Number', 'cm')
    

class MP_download_table(models.Model):
    portfolio_cm_Part_Number=models.TextField(default=None,null=True)
    Part_Number=models.TextField(default=None,null=True)
    portfolio_Cust_consign=models.TextField(default=None,null=True)
    po_delivery=models.TextField(default=None,null=True)
    CM_PO_Delivery_Remarks=models.TextField(default=None,null=True)
    cm_Quantity_Buffer_On_Hand=models.TextField(default=None,null=True)
    cm_Quantity_On_Hand_CS_Inv=models.TextField(default=None,null=True)
    Open_PO_due_in_this_quarter=models.TextField(default=None,null=True)
    Open_PO_due_in_next_quarter=models.TextField(default=None,null=True)
    Delivery_Based_Total_OH_sum_OPO_this_quarter=models.TextField(default=None,null=True)
    PO_Based_Total_OH_sum_OPO=models.TextField(default=None,null=True)
    CQ_ARIS_FQ_sum_1_SANM_Demand=models.TextField(default=None,null=True)
    CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand=models.TextField(default=None,null=True)
    CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand=models.TextField(default=None,null=True)
    CQ_sum_3_ARIS_FQ_SANM_Demand=models.TextField(default=None,null=True)
    Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista=models.TextField(default=None,null=True)
    Demand_Coverage=models.TextField(default=None,null=True)
    current_final_std_cost=models.TextField(default=None,null=True)
    sent_quater=models.TextField(default=None,null=True)
    standard_price_q1=models.TextField(default=None,null=True)
    quarter=models.TextField(default=None,null=True)
    delta_std_previous_std=models.TextField(default=None,null=True)
    delta_std_previous_std_per=models.TextField(default=None,null=True)
    portfolio_Blended_AVG_PO_Receipt_Price=models.TextField(default=None,null=True)
    new_po_price=models.TextField(default=None,null=True)
    approve_reject_std_price=models.TextField(default=None,null=True)
    cm_approve_reject=models.TextField(default=None,null=True)
    arista_pic_approve_reject=models.TextField(default=None,null=True)
    BP_team_Approve_Reject_Comments=models.TextField(default=None,null=True)
    current_qtr_decision=models.TextField(default=None,null=True)
    arista_pic_updated_data_name=models.TextField(default=None,null=True)
    portfolio_Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista_previous=models.TextField(db_column='portfolio_Delta_OH_and_Ope_previous',default=None,null=True)
    standard_price_q1_previous=models.TextField(default=None,null=True)
    current_qtr_decision_previous=models.TextField(default=None,null=True)
    arista_pic_approve_reject_previous=models.TextField(default=None,null=True)
    cm_approve_reject_previous=models.TextField(default=None,null=True)
    BP_team_Approve_Reject_Comments_previous=models.TextField(default=None,null=True)
    CM_Additional_Notes_on_Supplier_distributor_previous=models.TextField(default=None,null=True)
    std_cost=models.TextField(default=None,null=True)
    Mfr_Name=models.TextField(default=None,null=True)
    sent_to=models.TextField(default=None,null=True)
    portfolio_Item_Desc=models.TextField(default=None,null=True)
    Item_Price=models.TextField(default=None,null=True)
    portfolio_Qualification_Status=models.TextField(default=None,null=True)
    PO_Delivery=models.TextField(default=None,null=True)
    MOQ=models.TextField(default=None,null=True)
    Lead_Time=models.TextField(default=None,null=True)
    portfolio_Mfr_Part_Number=models.TextField(default=None,null=True)
    NCNR=models.TextField(default=None,null=True)
    COO=models.TextField(default=None,null=True)
    Inco_Term=models.TextField(default=None,null=True)
    Freight_cost=models.TextField(default=None,null=True)
    Comments=models.TextField(default=None,null=True)
    soft_hard_tool=models.TextField(default=None,null=True)
    portfolio_Rev=models.TextField(default=None,null=True)
    portfolio_Lifecycle_Phase=models.TextField(default=None,null=True)
    split=models.TextField(default=None,null=True)
    portfolio_Ownership=models.TextField(default=None,null=True)
    portfolio_Arista_PIC=models.TextField(default=None,null=True)
    Arista_pic_comment=models.TextField(default=None,null=True)
    Arista_PIC_Comments_to_CM=models.TextField(default=None,null=True)
    Arista_BP_Comments=models.TextField(default=None,null=True)
    Quoted_by=models.TextField(default=None,null=True)
    cm_updated_data_name=models.TextField(default=None,null=True)
    CM_price=models.TextField(default=None,null=True)
    CM_Manufacturer=models.TextField(default=None,null=True)
    CM_Supplier_Distributor_name_from_cm=models.TextField(default=None,null=True)
    CM_po_delivery=models.TextField(default=None,null=True)
    CM_mpn=models.TextField(default=None,null=True)
    CM_MOQ=models.TextField(default=None,null=True)
    CM_Lead_Time=models.TextField(default=None,null=True)
    CM_NCNR=models.TextField(default=None,null=True)
    CM_tarrif=models.TextField(default=None,null=True)
    CM_List=models.TextField(default=None,null=True)
    CM_qty_std_source=models.TextField(default=None,null=True)
    CM_comments=models.TextField(default=None,null=True)
    CM_Additional_Notes_on_Supplier_distributor=models.TextField(default=None,null=True)
    CM_buyer=models.TextField(default=None,null=True)
    CM_download=models.TextField(default=None,null=True)
    CM_Quoted_by=models.TextField(default=None,null=True)
    pic_approval_timestamp=models.DateTimeField(null=True)
    modified_by=models.DateTimeField(auto_now=True)
    go_with_pic_price=models.TextField(null=True)

    Quarter=models.TextField(default=Current_quarter)
    objects=DataFrameManager()

    @property
    def reset_descion(self):
        logic_BP,created=master_temp.objects.get_or_create(Team='BP Team',quarter=Current_quarter())
        unlock=not logic_BP.lift_logic=='enable'
        print(unlock)
        if unlock:
            print("Inside Unlock")
            self.current_qtr_decision=None
            self.approve_reject_std_price=None
            self.standard_price_q1=None
            self.new_po_price=None
            self.go_with_pic_price=None
            self.save()
            if self.portfolio_Arista_PIC:
                try:
                    print("in reset decision >>>>>>>>>>>>>>", self.portfolio_Arista_PIC)
                    to_mail_id=User.objects.filter(first_name__icontains=self.portfolio_Arista_PIC.split('/')[0].split(' ')[0],last_name__icontains=self.portfolio_Arista_PIC.split('/')[0].split(' ')[-1]).values_list('email',flat=True)

                    today = datetime.datetime.now()
                    current_date = today.strftime("%m-%d-%Y, %H:%M:%S")

                    notification = EmailNotification(
                            Arista_Part_Number=self.Part_Number,
                            updated_by='-',
                            Mfr_Part_Number=self.portfolio_Mfr_Part_Number,
                            Arista_PIC=self.portfolio_Arista_PIC.split('/')[0],
                            to='[]',
                            bp_email='-',
                            team='GSM Team' if self.portfolio_Ownership == 'Arista' else 'CMM Team',
                            cm=self.CM_download,
                            sent_to=self.sent_to,
                            created_at=current_date,
                            sgd_cm_email = '-',
                            jpe_cm_email = '-',
                            ownership=self.portfolio_Ownership,
                            current_qtr_decision='Reset Decision',
                            current_url=settings.SERVER_TYPE,
                            rfx_id='-',
                            Mfr_Name='-',
                            logged_in_user_group='-'
                            )
                    notification.save()
                    LOGGER.info(f'[Master Pricing] Master Pricing descion rested successfully,mail send to {self.portfolio_Arista_PIC},{to_mail_id}')
                except Exception as e:
                    print(e)
                    LOGGER.error("LOG MESSAGE:", exc_info=1 )
            return True
        else:
            print("Inside Locked")
            self.approve_reject_std_price=None
            self.save()
            return False

    def __str__(self):
        return f''' Part_Number:{self.Part_Number},po_delivery:{self.po_delivery},standard_price_q1_previous:{self.standard_price_q1_previous},std_cost:{self.std_cost},CM_download:{self.CM_download}'''
    class Meta:
        unique_together = ('Part_Number', 'Quarter','CM_download')