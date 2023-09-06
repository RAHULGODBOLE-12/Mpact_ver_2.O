from django_datatables_view.base_datatable_view import BaseDatatableView
from portfolio.models import *
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse,JsonResponse
from django import forms
import  openpyxl
import operator
from functools import reduce
from Slate_CMT.templatetags.cmt_helper import *
from django.db.models import Q, F, FloatField, ExpressionWrapper, Sum
import os
from django.conf import settings
from rfx.models import *
from InputDB.models import *


class Portfolio_data(BaseDatatableView):
    model=Portfolio
    columns=[
            "Number",
            "cm",
            "Ownership",
            "Arista_PIC",
            'commodity',
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
            'Arista_pic_comment',
            'bp_comment',
            "LT",
            "MOQ",
            "Quarter",
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
            "rfq_sent_flag_supplier",
            "rfq_sent_flag_cm",
            "rfq_sent_flag_distributor",
            "rfq_sent_distributor",
        ]

    def get_initial_queryset(self):
        team_name=self.request.GET.get('team')
        filters=self.request.GET.get('filter')
        if team_name=='GSM Team' and ( has_permission(self.request.user,'Super User') or  self.request.user in User.objects.filter(groups=Group.objects.get(name='GSM Team')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='GSM Manager')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or self.request.user.is_superuser):
            f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
            l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
            team_member_list=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
            data=Portfolio.objects.filter(Team="GSM Team",Quarter=Current_quarter())

        else:
            data=Portfolio.objects.none()
        return data.order_by('Number')

    def filter_queryset(self, qs):
        team_name=self.request.GET.get('team')
        filters=self.request.GET.get('filter')
        """ If search['value'] is provided then filter all searchable columns using filter_method (istartswith
            by default).

            Automatic filtering only works for Datatables 1.10+. For older versions override this method
        """
        columns = self._columns
        if not self.pre_camel_case_notation:
            # get global search value
            search = self._querydict.get('search[value]', None)
            q = Q()
            filter_method = 'icontains'
            for col_no, col in enumerate(self.columns_data):
                # apply global search to all searchable columns
                if search and col['searchable']:
                    try:
                        q |= Q(**{'{0}__{1}'.format(columns[col_no].replace('.', '__'), filter_method): search.strip()})
                    except :
                        print(col)
                        LOGGER.error("LOG_MESSAGE", exc_info=1)

                # column specific filter
                if col['search.value']:
                    print(col['search.value'])
                    dicts={
                        '{0}__{1}'.format(columns[col_no].replace('.', '__'), filter_method): col['search.value'].strip()}
                    print(dicts)
                    qs = qs.filter(**dicts)

            qs = qs.filter(q)
        if self.request.GET.get('table_filter_tab')=='his_parts':
            if self.request.user.is_superuser or has_permission(self.request.user,'Super User'):
                qs=qs.filter(offcycle=False)
            else:
                qs=qs.filter(Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}').filter(offcycle=False)
        if self.request.GET.get('table_filter_tab')=='his_parts_offcycle':
            if self.request.user.is_superuser or has_permission(self.request.user,'Super User'):
                qs=qs.filter(offcycle=True)
                print(qs)
            else:
                qs=qs.filter(Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}').filter(offcycle=True)
        if self.request.GET.get('table_filter_tab')=='all':
            if self.request.user.is_superuser or has_permission(self.request.user,'Super User'):
                qs=qs.filter(offcycle=False)
            else:
                qs=qs.filter(offcycle=False)
        if self.request.GET.get('table_regional_filter_tab')=='Global':
            print('ssksks')
            qs=qs.filter(Q(cm__contains='Global'))

        elif self.request.GET.get('table_regional_filter_tab')!='Global':
            print('slssls')
            qs=qs.filter(~Q(cm__contains='Global'))

        if filters=='excel':
                qs=qs.filter(id__in=self.request.session['filter_excel_portfolio'])
        if self.request.GET.get('advance_filter')=="true":
                qs=qs.filter(id__in=self.request.session['advance_filter_portfolio'])


        if self.request.GET.get('check_box_all_flag')=='true':
            if self.request.user.is_superuser or has_permission(self.request.user,'Super User'):
                data_id=qs.exclude(rfq_sent_flag_supplier='Quote Raised').values_list('id',flat=True)
            else:
                data_id=qs.exclude(rfq_sent_flag_supplier='Quote Raised').filter(Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}').values_list('id',flat=True)
            self.request.session['Check_box_portfolio']=list(data_id)
        self.request.session['Check_box_portfolio']=list(qs.exclude(rfq_sent_flag_supplier='Quote Raised').filter(id__in=self.request.session['Check_box_portfolio']).values_list('id',flat=True) )
        if self.request.GET.get('check_box_all_flag')=='false':
            self.request.session['Check_box_portfolio']=[]

        ########always at bottom###########
        if self.request.GET.get('download')=="true":
            pass
            # df=qs.to_dataframe()
            # del df['id']
            # df.to_excel( os.path.join(settings.BASE_DIR,f"Reports/portfolio_filtered/{get_Next_quarter()[0]} Portfolio_filtered {self.request.user.id}.xlsx"),index=False)
        self.request.session['current_filtered_portfolio']=list(qs.values_list('id',flat=True))
        ##########end########
        return qs

    def prepare_results(self, qs):
        team_name=self.request.GET.get('team')
        user=self.request.GET.get('user')
        try:
            check_list= self.request.session['Check_box_portfolio']
        except:
            check_list=[]
            LOGGER.error("LOG_MESSAGE", exc_info=1)
                        
            
        check_list= check_list if check_list is not None else []
        # his_parts=Portfolio.objects.filter(Arista_PIC__icontains=f'{self.request.first_name} {self.request.last_name}').value_list('id',flat=True)
        rfx_send=RFX.objects.filter()

        json_data = []
        for item in qs:
            q=['SGD','JPE','FGN','HBG','JSJ','JMX','Global']
            
            query = reduce(operator.or_, (Q(RFX_id__icontains = f"{cm}_{item.Mfr_Name}_{item.Mfr_Part_Number}_{item.Number}_{item.Team}_to_{self.request.GET.get('to_rfx')}") for cm in [item.cm]))
            query1 = reduce(operator.or_, (Q(RFX_id__icontains = f"{cm}_{item.Mfr_Name}_{item.Mfr_Part_Number}_{item.Number}_{item.Team}") for cm in [item.cm]))
            query2 = reduce(operator.or_, (Q(RFX_id__icontains = f"{cm}_{item.Mfr_Name}_{item.Mfr_Part_Number}_{item.Number}_{item.Team}_to_distributor_to_") for cm in [item.cm]))
            global_check = RFX.objects.filter(sent_quater=Current_quarter(),Part_Number=item.Number,Team=item.Team,cm__in=['Global'] if item.cm!='Global' else ['JPE','SGD','FGN','HBG','JSJ','JMX']).exists()
            his_part=Portfolio.objects.filter(Q(Arista_PIC__icontains=f'{self.request.user.first_name} {self.request.user.last_name}')&Q(id=item.id)).exists() or self.request.user.is_superuser
            checkbox=[
            (f'''{"checked" if item.id in check_list else "" }''' if his_part else None) if not (RFX.objects.filter(quarter=get_Next_quarter()[0],sent_quater=Current_quarter()).exclude(sent_to='cm').filter(query).exists() or RFX.objects.filter(quarter=get_Next_quarter()[0],sent_quater=Current_quarter()).exclude(sent_to='cm').filter(query1).exists() or RFX.objects.filter(quarter=get_Next_quarter()[0],sent_quater=Current_quarter()).exclude(sent_to='cm').filter(query2).exists() )  else 'Rfx_sent',
            item.id,
            global_check,
            'Global' if item.cm != 'Global' else 'Regional',
            find_partial_quote(item),
            his_part ]
            # checkbox=[(f'''{"checked" if item.id in check_list else "" }''' if his_part else None) if not (RFX.objects.filter(sent_quater=Current_quarter()).exclude(sent_to='cm').filter(query).exists() or RFX.objects.filter(sent_quater=Current_quarter()).exclude(sent_to='cm').filter(query1).exists() or RFX.objects.filter(sent_quater=Current_quarter()).exclude(sent_to='cm').filter(query2).exists() )  else 'Rfx_sent',item.id,global_check,'Global' if item.cm != 'Global' else 'Regional',find_partial_quote(item),his_part ]
            json_data.append(
                {
                'Checkbox':checkbox,
                "Number":item.Number,
                "id":item.id,
                "cm":item.cm,
                'commodity':item.commodity,
                "Lifecycle_Phase":item.Lifecycle_Phase,
                "Rev":item.Rev,
                "Mfr_Name":item.Mfr_Name,
                "Mfr_Part_Lifecycle_Phase":item.Mfr_Part_Lifecycle_Phase,
                "Mfr_Part_Number":item.Mfr_Part_Number,
                "Qualification_Status":item.Qualification_Status,
                "cm_Part_Number":item.cm_Part_Number,
                "Arista_Part_Number":item.Arista_Part_Number,
                "Cust_consign":item.Cust_consign,
                "Parts_controlled_by":item.Parts_controlled_by,
                "Item_Desc":item.Item_Desc,
                "LT":item.LT,
                "MOQ":item.MOQ,
                "Original_PO_Delivery_sent_by_Mexico":item.Original_PO_Delivery_sent_by_Mexico,
                "cm_Quantity_Buffer_On_Hand":item.cm_Quantity_Buffer_On_Hand,
                "cm_Quantity_On_Hand_CS_Inv":item.cm_Quantity_On_Hand_CS_Inv,
                "Open_PO_due_in_this_quarter":item.Open_PO_due_in_this_quarter,
                "Open_PO_due_in_next_quarter":item.Open_PO_due_in_next_quarter,
                "Delivery_Based_Total_OH_sum_OPO_this_quarter":item.Delivery_Based_Total_OH_sum_OPO_this_quarter,
                "PO_Based_Total_OH_sum_OPO":item.PO_Based_Total_OH_sum_OPO,
                "CQ_ARIS_FQ_sum_1_SANM_Demand":item.CQ_ARIS_FQ_sum_1_SANM_Demand,
                "CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand":item.CQ_sum_1_ARIS_FQ_sum_2_SANM_Demand,
                "CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand":item.CQ_sum_2_ARIS_FQ_sum_3_SANM_Demand,
                "CQ_sum_3_ARIS_FQ_SANM_Demand":item.CQ_sum_3_ARIS_FQ_SANM_Demand,
                "Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista":item.Delta_OH_and_Open_PO_DD_CQ_sum_CQ_sum_1_Arista,
                "ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std":item.ARIS_CQ_SANM_FQ_sum_1_unit_price_USD_Current_std,
                "CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD":item.CQ_sum_1_ARIS_FQ_sum_2_SANM_unit_price_USD,
                "Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1":item.Delta_ARIS_CQ_sum_1_SANM_FQ_sum_2_vs_ARIS_CQ_SANM_FQ_sum_1,
                "Blended_AVG_PO_Receipt_Price":item.Blended_AVG_PO_Receipt_Price,
                "Ownership":item.Ownership,
                "Arista_PIC":item.Arista_PIC,
                "rfq_sent_flag_supplier":item.rfq_sent_flag_supplier,
                "rfq_sent_flag_cm":item.rfq_sent_flag_cm,
                "rfq_sent_flag_distributor":item.rfq_sent_flag_distributor,
                "rfq_sent_distributor":item.rfq_sent_distributor,
                "Arista_pic_comment":item.Arista_pic_comment,
                "bp_comment":item.bp_comment,
                "refreshed_comment":item.refreshed_comment,
                "refreshed_on":item.refreshed_on,
                "created_on":item.created_on,
                "Quarter":item.Quarter,
                "sgd_jpe_cost":item.sgd_jpe_cost,
                }
            )
        
        return json_data


