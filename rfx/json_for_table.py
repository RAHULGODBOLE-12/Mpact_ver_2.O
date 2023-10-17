from django_datatables_view.base_datatable_view import BaseDatatableView
from rfx.models import *
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse,JsonResponse
from django import forms
import  openpyxl 
from Slate_CMT.templatetags.cmt_helper import *
from django.db.models import Q
import os
from django.conf import settings


class Analysis_data(BaseDatatableView):
    model=RFX 
    columns=[
                "id",
                "quarter",
                "sent_to",
                "Part_Number",
                "Mfr_Part_Number",
                "Mfr_Name",
                "cm",
                "Arista_pic_comment",
                "Item_Price",
                "Lead_Time",
                "MOQ",
                "List",
                "tarrif",
                "COO",
                "Inco_Term",
                "MPQ",
                "Assembly_cost",
                "Freight_cost",
                "Masked_Price",
                "Quote_Type",
                "Region",
                "Geo",
                "Life_Cycle",
                "Comments",
                "Quote_status",
                "sent_quater",
                "portfolio__cm",
                "portfolio__Number",
                "portfolio__Lifecycle_Phase",
                "portfolio__commodity",
                "portfolio__Rev",
                "portfolio__Mfr_Name",
                "portfolio__Mfr_Part_Lifecycle_Phase",
                "portfolio__Mfr_Part_Number",
                "portfolio__Qualification_Status",
                "portfolio__cm_Part_Number",
                "portfolio__Arista_Part_Number",
                "portfolio__Cust_consign",
                "portfolio__Parts_controlled_by",
                "portfolio__Item_Desc",
                "portfolio__LT",
                "portfolio__MOQ",
                "portfolio__Original_PO_Delivery_sent_by_Mexico",
                "portfolio__cm_Quantity_Buffer_On_Hand",
                "portfolio__cm_Quantity_On_Hand_CS_Inv",
                "portfolio__Open_PO_due_in_this_quarter",
                "portfolio__Open_PO_due_in_next_quarter",
                "portfolio__Delivery_Based_Total_OH_sum_OPO_this_quarter",
                "portfolio__PO_Based_Total_OH_sum_OPO",
                "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand",
                "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand",
                "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand",
                "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand",
                "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista",
                "portfolio__ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std",
                "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD",
                "portfolio__Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1",
                "portfolio__Blended_AVG_PO_Receipt_Price",
                "portfolio__Ownership",
                "portfolio__Arista_PIC",
                "portfolio__Team",
                "portfolio__Arista_pic_comment",
                "portfolio__offcycle",
                "portfolio__bp_comment",
                "portfolio__created_by__username",
                "portfolio__bp_comment",
                "portfolio__refreshed_comment",
                "created_by__username",
                "Quoted_by",
                "modified_on",
                "created_on",
                "quote_is_writable",
                "quote_freeze",
                "NCNR",
                "Team",
                "PO_Delivery",
                "soft_hard_tool",
                "suggested_split",
                "manual_split",
                "previous_split",
                "split_type",
                "approval_flag",
                "approval_status_PIC",
                "approval_status_Manager",
                "approval_status_Director",
                "approval_status",
                "split_comments",
                "approval1_comments",
                "approval2_comments",
                "std_cost",
                "CM_comments_on_Justifing_price",
                "Supplier_Distributor_name_from_cm",
                "CM_Notes_on_Supplier",
                "CM_Manufacturer",
                "CM_mpn",
                "CM_buyer",
                "CM_qty_std_source",
                "po_delivery",
                "new_po_price",
        ]

    def get_initial_queryset(self):
        team_name=self.request.GET.get('team')
        filters=self.request.GET.get('filter')
        #print(self.request.user.username)
        if team_name=='GSM Team' :
            initial=RFX.objects.filter(Q(portfolio__Team='GSM Team')&Q(quarter__in=get_Next_quarter(q=3,this_quarter=True))&Q(sent_quater=Current_quarter()))
            if has_permission(self.request.user,'Super User') or self.request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='BP Team')) or self.request.user.is_superuser:
                #print('into super user')
                data=initial
            elif self.request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')):
                #print(self.request.user.username)
                
                data=initial.filter(portfolio__Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}')
            else:
                data=RFX.objects.none()

        elif team_name=='CMM Team':
            initial=RFX.objects.exclude(sent_to='cm').filter(Q(portfolio__Team='CMM Team')&Q(quarter__in=get_Next_quarter(q=3,this_quarter=True))&Q(sent_quater=Current_quarter()))
            if has_permission(self.request.user,'Super User') or self.request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='BP Team')) or self.request.user.is_superuser:
                data=initial
            elif self.request.user in User.objects.filter(groups=Group.objects.get(name='CMM Team')):
                data=initial.filter(portfolio__Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}')
            else:
                data=RFX.objects.none()
        else:
            data=RFX.objects.none()
        self.request.session['his_analysis']=list(data.values_list('id',flat=True))
        # self.request.session['current_filtered_RFX']=list(data.values_list('id',flat=True))
        return data.filter(~Q(RFX_id=None)).filter(quarter__in=get_Next_quarter(q=1,this_quarter=True)).order_by('Part_Number','Mfr_Name')

    def filter_queryset(self, qs):
        team_name=self.request.GET.get('team')
        filters=self.request.GET.get('filter')
        columns = self._columns
        if not self.pre_camel_case_notation:
            # get global search value
            search = self._querydict.get('search[value]', None)
            q = Q()
            filter_method = 'icontains'
            for col_no, col in enumerate(self.columns_data):
                if search:
                    #print(search,columns[col_no])
                    try:
                        q |= Q(**{'{0}__{1}'.format(columns[col_no].replace('.', '__'), filter_method): search})
                    except :

                        print(col)
            qs = qs.filter(q)
        #print(self.request.GET['table_filter_tab'])
        if self.request.GET['table_filter_tab']=='his_parts':
            qs=qs.filter(portfolio__Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}')

        if filters=='excel':
                qs=qs.filter(id__in=self.request.session['filter_excel_RFX'])
                #print(qs)
        if self.request.GET['advance_filter']=="true":
                qs=qs.filter(id__in=self.request.session['advance_filter_RFX'])
        
        
        if self.request.GET.get('check_box_all_flag')=='true':
            if self.request.user.is_superuser:
                data_id=qs.values_list('id',flat=True) 
            else:
                data_id=qs.filter(portfolio__Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}').values_list('id',flat=True) 
            self.request.session['Check_box_analysis']=list(data_id)
        self.request.session['Check_box_analysis']=list(qs.filter(id__in=self.request.session['Check_box_analysis']).values_list('id',flat=True) )
        if self.request.GET.get('check_box_all_flag')=='false':
            self.request.session['Check_box_analysis']=[]
            
        ########always at bottom###########
        if self.request.GET['download']=="true":
            pass
            # df=qs.to_dataframe()
            # del df['id']
            # df.to_excel(os.path.join(settings.BASE_DIR,f"Reports/RFX_filtered/{get_Next_quarter()[0]} RFX_filtered {self.request.user.id}.xlsx"),index=False)
        ##########end########
        self.request.session['current_filtered_RFX']=list(qs.values_list('id',flat=True))
        return qs
    
    def prepare_results(self, qs):
        team_name=self.request.GET.get('team')
        user=self.request.GET.get('user')
        try:check_list= self.request.session['Check_box_analysis']
        except:check_list=[]
        check_list= check_list if check_list is not None else []
        # his_parts=RFX.objects.filter(portfolio__Arista_PIC__icontains=f'{self.request.first_name} {self.request.last_name}').value_list('id',flat=True)
        json_data = []
        for item in qs:
            json_data.append(
                {
                'Checkbox':[f'''{"checked" if item.id in check_list else ""}''',item.id],
                "id":item.id,
                "RFX_id":item.RFX_id,
                "quarter":item.quarter,
                "sent_to":item.sent_to,
                "Part_Number":item.Part_Number,
                "Mfr_Name":item.Mfr_Name,
                "Mfr_Part_Number":item.Mfr_Part_Number,
                "cm":item.cm,
                "Team":item.Team,
                "Item_Price":item.Item_Price,
                "Lead_Time":item.Lead_Time,
                "MOQ":item.MOQ,
                "List":item.List,
                "tarrif":item.tarrif,
                "COO":item.COO,
                "Inco_Term":item.Inco_Term,
                "NCNR":item.NCNR,
                "MPQ":item.MPQ,
                "Assembly_cost":item.Assembly_cost,
                "Freight_cost":item.Freight_cost,
                "Masked_Price":item.Masked_Price,
                "Quote_Type":item.Quote_Type,
                "Region":item.Region,
                "Geo":item.Geo,
                "Life_Cycle":item.Life_Cycle,
                "Comments":item.Comments,
                "Quote_status":item.Quote_status,
                "portfolio__Lifecycle_Phase":item.portfolio.Lifecycle_Phase,
                "portfolio__commodity":item.portfolio.commodity,
                "portfolio__Rev":item.portfolio.Rev,
                "portfolio__Mfr_Part_Lifecycle_Phase":item.portfolio.Mfr_Part_Lifecycle_Phase,
                "portfolio__Qualification_Status":item.portfolio.Qualification_Status,
                "portfolio__Cust_consign":item.portfolio.Cust_consign,
                "portfolio__Parts_controlled_by":item.portfolio.Parts_controlled_by,
                "portfolio__Item_Desc":item.portfolio.Item_Desc,
                "portfolio__Original_PO_Delivery_sent_by_Mexico":item.portfolio.Original_PO_Delivery_sent_by_Mexico,
                "portfolio__Sanmina_Quantity_Buffer_On_Hand":item.portfolio.cm_Quantity_Buffer_On_Hand,
                "portfolio__Sanmina_Quantity_On_Hand_CS_Inv":item.portfolio.cm_Quantity_On_Hand_CS_Inv,
                "portfolio__Open_PO_due_in_this_quarter":item.portfolio.Open_PO_due_in_this_quarter,
                "portfolio__Open_PO_due_in_next_quarter":item.portfolio.Open_PO_due_in_next_quarter,
                "portfolio__Delivery_Based_Total_OH_sum_OPO_this_quarter":item.portfolio.Delivery_Based_Total_OH_sum_OPO_this_quarter,
                "portfolio__PO_Based_Total_OH_sum_OPO":item.portfolio.PO_Based_Total_OH_sum_OPO,
                "portfolio__CQ_ARIS_FQ_sum_1_SANM_Demand":item.portfolio.CQ_ARIS_FQ_sum_1_SANM_Demand,
                "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":item.portfolio.CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand,
                "portfolio__CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand":item.portfolio.CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand,
                "portfolio__CQ_sum_3_ARIS_FQ_SANM_Demand":item.portfolio.CQ_sum_3_ARIS_FQ_SANM_Demand,
                "portfolio__Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista":item.portfolio.Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista,
                "portfolio__ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std":item.portfolio.ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std,
                "portfolio__CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD":item.portfolio.CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD,
                "portfolio__Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1":item.portfolio.Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1,
                "portfolio__Blended_AVG_PO_Receipt_Price":item.portfolio.Blended_AVG_PO_Receipt_Price,
                "portfolio__Ownership":item.portfolio.Ownership,
                "portfolio__Arista_PIC":item.portfolio.Arista_PIC,
                "portfolio__Team":item.portfolio.Team,
                "created_by":item.created_by.username if item.created_by!=None else '' ,
                "Quoted_by":item.Quoted_by,
                "modified_on":item.modified_on,
                "created_on":item.created_on,
                "quote_is_writable":item.quote_is_writable,
                "suggested_split":item.suggested_split,
                "manual_split":item.manual_split,
                "previous_split":item.previous_split,
                "split_type":item.split_type,
                "approval_flag":item.approval_flag,
                "approval_status_PIC":('your approval' if str(item.approval_status_PIC).lower()=='Approval pending'.lower() else ("your reject" if item.approval_status_PIC =='Approved' else item.approval_status_PIC ) ) if self.request.user.first_name in item.portfolio.Arista_PIC else item.approval_status_PIC,
                "approval_status_Manager":('your approval' if str(item.approval_status_Manager).lower()=='Approval pending'.lower() else item.approval_status_Manager ) if his_role(self.request.user,'Manager')=='Manager' else item.approval_status_Manager,
                "approval_status_Director":('your approval' if str(item.approval_status_Director).lower()=='Approval pending'.lower() else item.approval_status_Director ) if his_role(self.request.user,'Director')=='Director' else item.approval_status_Director,
                "approval_status":item.approval_status,
                "split_comments":item.split_comments,
                "approval1_comments":item.approval1_comments,
                "approval2_comments":item.approval2_comments,
                "Arista_pic_comment":item.portfolio.Arista_pic_comment,
                "bp_comment":item.portfolio.bp_comment,
                "offcycle":item.portfolio.offcycle,
                "std_cost":item.std_cost,
                "quote_freeze":item.quote_freeze,
                "CM_Manufacturer":item.CM_Manufacturer,
                "Supplier_Distributor_name_from_cm":item.Supplier_Distributor_name_from_cm,
                "CM_mpn":item.CM_mpn,
                "CM_buyer":item.CM_buyer,
                "CM_qty_std_source":item.CM_qty_std_source,
                "approval_status_cmm_team":'your approval' if item.approval_status!='Approved' else item.approval_status ,
                "cm_jpe_Item_Price":get_cm_price(item,'JPE',quarter=item.quarter,field='Item_Price'),
                "cm_jpe_Lead_Time":get_cm_price(item,'JPE',quarter=item.quarter,field='Lead_Time'),
                "cm_jpe_MOQ":get_cm_price(item,'JPE',quarter=item.quarter,field='MOQ'),
                "cm_sgd_Item_Price":get_cm_price(item,'SGD',quarter=item.quarter,field='Item_Price'),
                "cm_sgd_Lead_Time":get_cm_price(item,'SGD',quarter=item.quarter,field='Lead_Time'),
                "cm_sgd_MOQ":get_cm_price(item,'SGD',quarter=item.quarter,field='MOQ'),
                "cm_fgn_Item_Price":get_cm_price(item,'FGN',quarter=item.quarter,field='Item_Price'),
                "cm_fgn_Lead_Time":get_cm_price(item,'FGN',quarter=item.quarter,field='Lead_Time'),
                "cm_fgn_MOQ":get_cm_price(item,'FGN',quarter=item.quarter,field='MOQ'),
                "cm_hbg_Item_Price":get_cm_price(item,'HBG',quarter=item.quarter,field='Item_Price'),
                "cm_hbg_Lead_Time":get_cm_price(item,'HBG',quarter=item.quarter,field='Lead_Time'),
                "cm_hbg_MOQ":get_cm_price(item,'HBG',quarter=item.quarter,field='MOQ'),
                "cm_jsj_Item_Price":get_cm_price(item,'JSJ',quarter=item.quarter,field='Item_Price'),
                "cm_jsj_Lead_Time":get_cm_price(item,'JSJ',quarter=item.quarter,field='Lead_Time'),
                "cm_jsj_MOQ":get_cm_price(item,'JSJ',quarter=item.quarter,field='MOQ'),
                "cm_jmx_Item_Price":get_cm_price(item,'JMX',quarter=item.quarter,field='Item_Price'),
                "cm_jmx_Lead_Time":get_cm_price(item,'JMX',quarter=item.quarter,field='Lead_Time'),
                "cm_jmx_MOQ":get_cm_price(item,'JMX',quarter=item.quarter,field='MOQ'),
                "soft_hard_tool":item.soft_hard_tool,
                "sent_quater":item.sent_quater,
                "PO_Delivery":item.PO_Delivery,
                "po_delivery":item.po_delivery,
                "portfolio__cm_Part_Number":item.portfolio.cm_Part_Number,
                "PIC_accept_reject_comments":item.PIC_accept_reject_comments,
                "portfolio__sgd_jpe_cost":item.portfolio.sgd_jpe_cost,
                "Shareable":item.Shareable,
                } 
            )
        return json_data
    
def approval_status(flag):
    approval=None
    if flag:
        approval_level,approval_done=str(float(flag)/10).split('.')
        approval_level,approval_done=int(approval_level),int(approval_done)
        #print(flag,approval_level,approval_done)
        if approval_level==3:
            approval=['Director']
        elif approval_level==2:
            approval=['Manager']
        elif approval_level==1:
            approval=['PIC']
        elif approval_level==0:
            approval=['No Need']
        else:
            approval=[]
        ##done
        # if approval_done==3:
        #     approval.append('Director')
        if approval_done==2:
            approval.append('Director')
        elif approval_done==1:
            approval.append('Manager')
        elif approval_done==0:
            approval.append('PIC')
        else:
            pass
        if approval_level==approval_done:
            approval=['Approved','Approved']
        approval.append(flag)
    return approval

def his_role(user,need):
    if user.is_superuser or user in User.objects.filter(groups=Group.objects.get(name='Director')):
        data='Director'
        return data
    elif has_permission(user,'GSM Manager') or has_permission(user,'CMM Manager'):
        data='Manager'
        if need!=data:
            return need if  has_permission(user,need) else data
        return data
    elif has_permission(user,'PIC'):
        data='PIC'
        return data
    

def get_cm_price(rfx,cm,quarter,field):
    q=RFX.objects.filter(Part_Number=rfx.Part_Number,quarter=quarter,cm=cm,sent_to='cm').values()
    if q:
        return q[0][field]
    else:
        return None