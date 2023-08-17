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
# from InputDB.models import *

# class top_component_data(BaseDatatableView):
#     model=SGD_JBE_component_ss_team
#     max_display_length=20000
#     columns=[
#         "Contract_Mfr",
#         "quarter",
#         "APN",
#         "Arista_PIC",
#         "Ownership",
#         "Part_Desc",
#         "Annual_demand",
#         "CPN",
#         "total_OH",
#         "quarter_demand_1",
#         "quarter_demand_2",
#         "quarter_demand_3",
#         "quarter_demand_4",
#         "quarter_std_1",
#         "quarter_std_2",
#         "Part",
#         "Delta_std",
#         "quarter_demand_1_x_quarter_std_1",
#         "quarter_demand_2_x_quarter_std_1",
#         "quarter_demand_3_x_quarter_std_1",
#         "quarter_demand_4_x_quarter_std_1",
#         "Delta_demand",
#         "Delta_Demand_x_quarter_std_1",
#         "Delta_Demand_x_Delta_std",
#         "quarter_demand_mapper",
#         "quarter_std_mapper",
#     ]
#     def paging(self,qs):
#         if self.pre_camel_case_notation:
#             limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
#             start = int(self._querydict.get('iDisplayStart', 0))
#         else:
#             limit = min(int(self._querydict.get('length', 20)), self.max_display_length)
#             start = int(self._querydict.get('start', 0))

#         # if pagination is disabled ("paging": false)
#         if limit == -1:
#             return qs

#         offset = start + limit
#         print(limit)

#         return qs[start:offset]

#     def get_initial_queryset(self):
#         filter=self.request.GET.get('filter')
#         team=self.request.GET.get('team')
#         print(filter)
#         print(team)
#         if filter=='Sanmina' and team=='GSM':
#             print('##1')
#             data=SGD_JBE_component_ss_team.objects.filter(Contract_Mfr='Sanmina')
#         elif filter=='Jabil' and team=='GSM':
#             data=SGD_JBE_component_ss_team.objects.filter(Contract_Mfr='Jabil')
#             print('##2')
#         elif filter=='Sanmina' and team=='CMM':
#             data=SGD_JBE_component_cmm_team.objects.filter(Contract_Mfr='Sanmina')
#             print('##3')
#         elif filter=='Jabil' and team=='CMM':
#             data=SGD_JBE_component_cmm_team.objects.filter(Contract_Mfr='Jabil')
#             print('##4')
#         else:
#             data=SGD_JBE_component_ss_team.objects.none()
#         return data

#     # def filter_queryset(self,qs):
#     #     return qs
#     def prepare_results(self, qs):
#         # prepare list with output column data
#         print(qs)
#         # queryset is already paginated here
#         json_data = []
#         for item in qs:
#             json_data.append(
#                 {
#                     "Contract_Mfr":item.Contract_Mfr,
#                     "quarter":item.quarter,
#                     "APN":item.APN,
#                     "Arista_PIC":item.Arista_PIC,
#                     "Ownership":item.Ownership,
#                     "Part_Desc":item.Part_Desc,
#                     "Annual_demand":item.Annual_demand,
#                     "CPN":item.CPN,
#                     "total_OH":item.total_OH,
#                     "quarter_demand_1":item.quarter_demand_1,
#                     "quarter_demand_2":item.quarter_demand_2,
#                     "quarter_demand_3":item.quarter_demand_3,
#                     "quarter_demand_4":item.quarter_demand_4,
#                     "quarter_std_1":item.quarter_std_1,
#                     "quarter_std_2":item.quarter_std_2,
#                     "Part":item.Part,
#                     "Delta_std":item.Delta_std,
#                     "quarter_demand_1_x_quarter_std_1":item.quarter_demand_1_x_quarter_std_1,
#                     "quarter_demand_2_x_quarter_std_1":item.quarter_demand_2_x_quarter_std_1,
#                     "quarter_demand_3_x_quarter_std_1":item.quarter_demand_3_x_quarter_std_1,
#                     "quarter_demand_4_x_quarter_std_1":item.quarter_demand_4_x_quarter_std_1,
#                     "Delta_demand":item.Delta_demand,
#                     "Delta_Demand_x_quarter_std_1":item.Delta_Demand_x_quarter_std_1,
#                     "Delta_Demand_x_Delta_std":item.Delta_Demand_x_Delta_std,
#                     "quarter_demand_mapper":item.quarter_demand_mapper,
#                     "quarter_std_mapper":item.quarter_std_mapper,

#                 }
#             )
#         return json_data
# class Refreshed_top_component_JPE_SGD_data(BaseDatatableView):
#     model=Refreshed_top_component_JPE_SGD
#     columns=[
#         "APN",
#         "Ownership",
#         "Arista_PIC",
#         "Part_Desc",
#         "PO_or_Delivery",
#         "CM_Buffer_On_Hand",
#         "CM_Quantity_On_Hand_sum_CS_Inv",
#         "Open_PO_due_in_Q",
#         "Open_PO_due_in_Q1",
#         "Delivery_Based_Total_OH_sum_OPO",
#         "PO_Based_Total_OH_sum_OPO",
#         "Q0_Demand",
#         "Q1_Demand",
#         "Q2_Demand",
#         "Q3_Demand",
#         "Delta_Demand",
#         "quarter_std_2",
#         "quarter_std_1",
#         "Delta_std",
#         "quarter_demand_2_x_quarter_std_1",
#         "quarter_demand_3_x_quarter_std_1",
#         "quarter_demand_4_x_quarter_std_1",
#         "Delta_Demand_x_quarter_std_1",
#         "Delta_Demand_x_Delta_std",
#         "Delta_Demand_x_Delta_std_per",
#         "quarter_demand_1_x_quarter_std_1",
#         "Annual_Demand",
#         "quarter",
#         "Team",
#         "Contract_Mfr",
#     ]


#     def get_initial_queryset(self):
#         filter=self.request.GET.get('filter')
#         team=self.request.GET.get('team')
#         print(filter)
#         print(team)
#         if filter=='Sanmina' and team=='GSM':
#             print('##1')
#             data=self.model.objects.filter(Contract_Mfr='Sanmina').filter(Team=team).filter(quarter=Current_quarter())
#         elif filter=='Jabil' and team=='GSM':
#             data=self.model.objects.filter(Contract_Mfr='Jabil').filter(Team=team).filter(quarter=Current_quarter())
#             print('##2')
#         elif filter=='Sanmina' and team=='CMM':
#             data=self.model.objects.filter(Contract_Mfr='Sanmina').filter(Team=team).filter(quarter=Current_quarter())
#             print('##3')
#         elif filter=='Jabil' and team=='CMM':
#             data=self.model.objects.filter(Contract_Mfr='Jabil').filter(Team=team).filter(quarter=Current_quarter())
#             print('##4')
#         else:
#             data=self.model.objects.none()
#         return data

#     # def filter_queryset(self,qs):
#     #     return qs
#     def prepare_results(self, qs):
#         # prepare list with output column data
#         print(qs)
#         # queryset is already paginated here
#         json_data = []
#         for item in qs:
#             json_data.append(
#                 {
#                     "APN":item.APN,
#                     "Ownership":item.Ownership,
#                     "Arista_PIC":item.Arista_PIC,
#                     "Part_Desc":item.Part_Desc,
#                     "PO_or_Delivery":item.PO_or_Delivery,
#                     "CM_Buffer_On_Hand":item.CM_Buffer_On_Hand,
#                     "CM_Quantity_On_Hand_sum_CS_Inv":item.CM_Quantity_On_Hand_sum_CS_Inv,
#                     "Open_PO_due_in_Q":item.Open_PO_due_in_Q,
#                     "Open_PO_due_in_Q1":item.Open_PO_due_in_Q1,
#                     "Delivery_Based_Total_OH_sum_OPO":item.Delivery_Based_Total_OH_sum_OPO,
#                     "PO_Based_Total_OH_sum_OPO":item.PO_Based_Total_OH_sum_OPO,
#                     "Q0_Demand":item.Q0_Demand,
#                     "Q1_Demand":item.Q1_Demand,
#                     "Q2_Demand":item.Q2_Demand,
#                     "Q3_Demand":item.Q3_Demand,
#                     "Delta_Demand":item.Delta_Demand,
#                     "quarter_std_2":item.quarter_std_2,
#                     "quarter_std_1":item.quarter_std_1,
#                     "Delta_std":item.Delta_std,
#                     "quarter_demand_2_x_quarter_std_1":item.quarter_demand_2_x_quarter_std_1,
#                     "quarter_demand_3_x_quarter_std_1":item.quarter_demand_3_x_quarter_std_1,
#                     "quarter_demand_4_x_quarter_std_1":item.quarter_demand_4_x_quarter_std_1,
#                     "Delta_Demand_x_quarter_std_1":item.Delta_Demand_x_quarter_std_1,
#                     "Delta_Demand_x_Delta_std":item.Delta_Demand_x_Delta_std,
#                     "Delta_Demand_x_Delta_std_per":item.Delta_Demand_x_Delta_std_per,
#                     "quarter_demand_1_x_quarter_std_1":item.quarter_demand_1_x_quarter_std_1,
#                     "Annual_Demand":item.Annual_Demand,
#                     "quarter":item.quarter,
#                     "Team":item.Team,
#                     "Contract_Mfr":item.Contract_Mfr,
#                 }
#             )
#         return json_data

# class Refreshed_top_component_Global_component_data(BaseDatatableView):
#     model=Refreshed_top_component_Global_component
#     columns=[
#         "quarter",
#         "Team",
#         "APN",
#         "Part_Desc",
#         "Ownership_JPE",
#         "Arista_PIC_JPE",
#         "PO_or_Delivery_JPE",
#         "CM_Buffer_On_Hand_JPE",
#         "CM_Quantity_On_Hand_sum_CS_Inv_JPE",
#         "Open_PO_due_in_Q_JPE",
#         "Open_PO_due_in_Q1_JPE",
#         "Delivery_Based_Total_OH_sum_OPO_JPE",
#         "PO_Based_Total_OH_sum_OPO_JPE",
#         "Q0_Demand_JPE",
#         "Q1_Demand_JPE",
#         "Q2_Demand_JPE",
#         "Q3_Demand_JPE",
#         "Annual_Demand_JPE",
#         "Delta_Demand_JPE",
#         "quarter_std_1_JPE",
#         "Delta_Demand_x_quarter_std_1_JPE",
#         "Ownership_SGD",
#         "Arista_PIC_SGD",
#         "PO_or_Delivery_SGD",
#         "CM_Buffer_On_Hand_SGD",
#         "CM_Quantity_On_Hand_sum_CS_Inv_SGD",
#         "Open_PO_due_in_Q_SGD",
#         "Open_PO_due_in_Q1_SGD",
#         "Delivery_Based_Total_OH_sum_OPO_SGD",
#         "PO_Based_Total_OH_sum_OPO_SGD",
#         "Q0_Demand_SGD",
#         "Q1_Demand_SGD",
#         "Q2_Demand_SGD",
#         "Q3_Demand_SGD",
#         "Annual_Demand_SGD",
#         "Delta_Demand_SGD",
#         "Delta_std_SGD",
#         "quarter_std_1_SGD",
#         "Delta_Demand_x_quarter_std_1_SGD",
#         "Global_Annual_Demand_SGD",
#         "Global_Spend_SGD",
#         "Global_Spend_Percentage_SGD",
#     ]
#     def paging(self,qs):
#         if self.pre_camel_case_notation:
#             limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
#             start = int(self._querydict.get('iDisplayStart', 0))
#         else:
#             limit = min(int(self._querydict.get('length', 20)), self.max_display_length)
#             start = int(self._querydict.get('start', 0))

#         # if pagination is disabled ("paging": false)
#         if limit == -1:
#             return qs

#         offset = start + limit
#         print(limit)

#         return qs[start:offset]

#     def get_initial_queryset(self):
#         filter=self.request.GET.get('filter')
#         team=self.request.GET.get('team')
#         user=self.request.GET.get('user')
#         print(filter)
#         print(team)
#         if team=='GSM' and user=='ALL':
#             data=self.model.objects.filter(Team='GSM').order_by("Global_Spend_Percentage")
#         elif team=='CMM' and user=='ALL':
#             data=self.model.objects.filter(Team='CMM').order_by("Global_Spend_Percentage")
#         elif team=='CMM':
#             data=self.model.objects.filter(Q(Team__startswith=f'''CMM_{user}''')).order_by("Global_Spend_Percentage")
#             print(user)
#         elif team=='GSM':
#             data=self.model.objects.filter(Q(Team__startswith=f'''GSM_{user}''') ).order_by("Global_Spend_Percentage")
#         return data

#     def prepare_results(self, qs):

#         json_data = []
#         for item in qs:
#             json_data.append(
#                 {
#             "quarter":item.quarter,
#             "Team":item.Team,
#             "APN":item.APN,
#             "Part_Desc":item.Part_Desc,
#             "Ownership_JPE":item.Ownership_JPE,
#             "Arista_PIC_JPE":item.Arista_PIC_JPE,
#             "PO_or_Delivery_JPE":item.PO_or_Delivery_JPE,
#             "CM_Buffer_On_Hand_JPE":item.CM_Buffer_On_Hand_JPE,
#             "CM_Quantity_On_Hand_sum_CS_Inv_JPE":item.CM_Quantity_On_Hand_sum_CS_Inv_JPE,
#             "Open_PO_due_in_Q_JPE":item.Open_PO_due_in_Q_JPE,
#             "Open_PO_due_in_Q1_JPE":item.Open_PO_due_in_Q1_JPE,
#             "Delivery_Based_Total_OH_sum_OPO_JPE":item.Delivery_Based_Total_OH_sum_OPO_JPE,
#             "PO_Based_Total_OH_sum_OPO_JPE":item.PO_Based_Total_OH_sum_OPO_JPE,
#             "Q0_Demand_JPE":item.Q0_Demand_JPE,
#             "Q1_Demand_JPE":item.Q1_Demand_JPE,
#             "Q2_Demand_JPE":item.Q2_Demand_JPE,
#             "Q3_Demand_JPE":item.Q3_Demand_JPE,
#             "Annual_Demand_JPE":item.Annual_Demand_JPE,
#             "Delta_Demand_JPE":item.Delta_Demand_JPE,
#             "quarter_std_1_JPE":item.quarter_std_1_JPE,
#             "Delta_Demand_x_quarter_std_1_JPE":item.Delta_Demand_x_quarter_std_1_JPE,
#             "Ownership_SGD":item.Ownership_SGD,
#             "Arista_PIC_SGD":item.Arista_PIC_SGD,
#             "PO_or_Delivery_SGD":item.PO_or_Delivery_SGD,
#             "CM_Buffer_On_Hand_SGD":item.CM_Buffer_On_Hand_SGD,
#             "CM_Quantity_On_Hand_sum_CS_Inv_SGD":item.CM_Quantity_On_Hand_sum_CS_Inv_SGD,
#             "Open_PO_due_in_Q_SGD":item.Open_PO_due_in_Q_SGD,
#             "Open_PO_due_in_Q1_SGD":item.Open_PO_due_in_Q1_SGD,
#             "Delivery_Based_Total_OH_sum_OPO_SGD":item.Delivery_Based_Total_OH_sum_OPO_SGD,
#             "PO_Based_Total_OH_sum_OPO_SGD":item.PO_Based_Total_OH_sum_OPO_SGD,
#             "Q0_Demand_SGD":item.Q0_Demand_SGD,
#             "Q1_Demand_SGD":item.Q1_Demand_SGD,
#             "Q2_Demand_SGD":item.Q2_Demand_SGD,
#             "Q3_Demand_SGD":item.Q3_Demand_SGD,
#             "Annual_Demand_SGD":item.Annual_Demand_SGD,
#             "Delta_Demand_SGD":item.Delta_Demand_SGD,
#             "Delta_std_SGD":item.Delta_std_SGD,
#             "quarter_std_1_SGD":item.quarter_std_1_SGD,
#             "Delta_Demand_x_quarter_std_1_SGD":item.Delta_Demand_x_quarter_std_1_SGD,
#             "Global_Annual_Demand_SGD":item.Global_Annual_Demand_SGD,
#             "Global_Spend_SGD":item.Global_Spend_SGD,
#             "Global_Spend_Percentage_SGD":item.Global_Spend_Percentage_SGD,
#                 }
#             )
#         return json_data

# class top_component_global_data(BaseDatatableView):
#     model=Top_Global_component
#     max_display_length=20000
#     columns=[
#         "APN",
#         "Part_Desc",
#         "Ownership_JPE",
#         "Arista_PIC_JPE",
#         "total_OH_JPE",
#         "Annual_demand_JPE",
#         "Delta_demand_JPE",
#         "quarter_std_1_JPE",
#         "Delta_Demand_multiply_x_quarter_std_1_JPE",
#         "Ownership_SGD",
#         "Arista_PIC_SGD",
#         "total_OH_SGD",
#         "Annual_demand_SGD",
#         "Delta_demand_SGD",
#         "quarter_std_1_SGD",
#         "quarter_demand_1_x_quarter_std_1_SGD",
#         "Global_Annual_Demand",
#         "Global_Spend",
#         "Global_Spend_Percentage",
#         "quarter",
#         "Team",
#     ]
#     def paging(self,qs):
#         if self.pre_camel_case_notation:
#             limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
#             start = int(self._querydict.get('iDisplayStart', 0))
#         else:
#             limit = min(int(self._querydict.get('length', 200000)), self.max_display_length)
#             start = int(self._querydict.get('start', 0))

#         # if pagination is disabled ("paging": false)
#         if limit == -1:
#             return qs

#         offset = start + limit

#         return qs[start:offset]

#     def get_initial_queryset(self):
#         team_name=self.request.GET.get('team')
#         user=self.request.GET.get('user')
#         print(filter)
#         if team_name=='GSM' and user=='ALL':
#             data=Top_Global_component.objects.filter(Team='GSM').order_by("Global_Spend_Percentage")
#         elif team_name=='CMM' and user=='ALL':
#             data=Top_Global_component.objects.filter(Team='CMM').order_by("Global_Spend_Percentage")
#         elif team_name=='CMM':
#             data=Top_Global_component.objects.filter(Q(Team__startswith=f'''CMM_{user}''')).order_by("Global_Spend_Percentage")
#             print(user)
#         elif team_name=='GSM':
#             data=Top_Global_component.objects.filter(Q(Team__startswith=f'''SS_{user}''') ).order_by("Global_Spend_Percentage")
#         return data

#     # def filter_queryset(self,qs):
#     #     return qs
#     def prepare_results(self, qs):
#         # prepare list with output column data
#         # queryset is already paginated here
#         team_name=self.request.GET.get('team')
#         user=self.request.GET.get('user')
#         json_data = []

#         for item in qs:
#             json_data.append(
#                 {
#                     "APN":item.APN,
#                     "Part_Desc":item.Part_Desc,
#                     "Ownership_JPE":item.Ownership_JPE,
#                     "Arista_PIC_JPE":item.Arista_PIC_JPE,
#                     "total_OH_JPE":item.total_OH_JPE,
#                     "Annual_demand_JPE":item.Annual_demand_JPE,
#                     "Delta_demand_JPE":item.Delta_demand_JPE,
#                     "quarter_std_1_JPE":item.quarter_std_1_JPE,
#                     "Delta_Demand_multiply_x_quarter_std_1_JPE":item.Delta_Demand_multiply_x_quarter_std_1_JPE,
#                     "Ownership_SGD":item.Ownership_SGD,
#                     "Arista_PIC_SGD":item.Arista_PIC_SGD,
#                     "total_OH_SGD":item.total_OH_SGD,
#                     "Annual_demand_SGD":item.Annual_demand_SGD,
#                     "Delta_demand_SGD":item.Delta_demand_SGD,
#                     "quarter_std_1_SGD":item.quarter_std_1_SGD,
#                     "quarter_demand_1_x_quarter_std_1_SGD":item.quarter_demand_1_x_quarter_std_1_SGD,
#                     "Global_Annual_Demand":item.Global_Annual_Demand,
#                     "Global_Spend":item.Global_Spend,
#                     "Global_Spend_Percentage":"%.3f %%"%float(0 if item.Global_Spend_Percentage ==None else item.Global_Spend_Percentage*100),
#                     "quarter":item.quarter,
#                     "Team":item.Team,
#                 }
#             )
#         return json_data

class Portfolio_data(BaseDatatableView):
    model=Portfolio
    columns=[
            "Number",
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

        # if team_name=='CMM Team' and ( has_permission(self.request.user,'Super User') or self.request.user in User.objects.filter(groups=Group.objects.get(name='CMM Team')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='CMM Manager')) or self.request.user in User.objects.filter(groups=Group.objects.get(name='Director')) or self.request.user.is_superuser):
        #     f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
        #     l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
        #     team_member_list=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
        #     data=Portfolio.objects.filter(Team='CMM Team',Quarter=Current_quarter())

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
            qs=qs.filter(Q(cm__contains='Global'))

        elif self.request.GET.get('table_regional_filter_tab')!='Global':
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
        print('jhgc',qs)
        return qs

    def prepare_results(self, qs):
        print('jsjsj')
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

# class top_component_data_new(BaseDatatableView):
#     #model=SGD_JBE_component_ss_team
#     max_display_length=20000
#     columns=[
#         "contract_mfr",
#         "quarter",
#         "apn",
#         "Arista_PIC",
#         "Ownership",
#         "Part_Desc",
#         "Annual_demand",
#         "cpn",
#         "total_OH",
#         "quarter_demand_1",
#         "quarter_demand_2",
#         "quarter_demand_3",
#         "quarter_demand_4",
#         "quarter_std_1",
#         "quarter_std_2",
#         "Part",
#         "Delta_std",
#         "quarter_demand_1_x_quarter_std_1",
#         "quarter_demand_2_x_quarter_std_1",
#         "quarter_demand_3_x_quarter_std_1",
#         "quarter_demand_4_x_quarter_std_1",
#         "Delta_demand",
#         "Delta_Demand_x_quarter_std_1",
#         "Delta_Demand_x_Delta_std",
#         "quarter_demand_mapper",
#         "quarter_std_mapper",
#     ]
#     def paging(self,qs):
#         if self.pre_camel_case_notation:
#             limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
#             start = int(self._querydict.get('iDisplayStart', 0))
#         else:
#             limit = min(int(self._querydict.get('length', 20)), self.max_display_length)
#             start = int(self._querydict.get('start', 0))

#         # if pagination is disabled ("paging": false)
#         if limit == -1:
#             return qs

#         offset = start + limit
#         print(limit)

#         return qs[start:offset]

#     def get_initial_queryset(self):
#         filter=self.request.GET.get('filter')
#         team=self.request.GET.get('team')
#         print(filter)
#         print(team)
#         if filter=='Sanmina' and team=='GSM':
#             print('##1')
#             data=TopComponentSgd.objects.using('inputdb').filter(team='GSM Team')
#         elif filter=='Jabil' and team=='GSM':
#             data=TopComponentJpe.objects.using('inputdb').filter(team='GSM Team')
#             print('##2')
#         elif filter=='Sanmina' and team=='CMM':
#             data=TopComponentSgd.objects.using('inputdb').filter(team='CMM Team')
#             print('##3')
#         elif filter=='Jabil' and team=='CMM':
#             data=TopComponentJpe.objects.using('inputdb').filter(team='CMM Team')
#             print('##4')
#         elif filter=='Sanmina' and team=='Unassigned':
#             data=TopComponentSgd.objects.using('inputdb').filter(team__isnull=True)
#             print('##5')
#         elif filter=='Jabil' and team=='Unassigned':
#             data=TopComponentJpe.objects.using('inputdb').filter(team__isnull=True)
#             print('##6')
#         else:
#             data=TopComponentSgd.objects.using('inputdb').none()
#         return data

#     # def filter_queryset(self,qs):
#     #     return qs
#     def prepare_results(self, qs):
#         # prepare list with output column data
#         print(qs)
#         # queryset is already paginated here
#         json_data = []
#         for item in qs:
#             json_data.append(
#                 {
#                     "Contract_Mfr":item.contract_mfr,
#                     "quarter":item.quarter,
#                     "APN":item.apn,
#                     "Arista_PIC":item.arista_pic,
#                     "Ownership":item.ownership,
#                     "Part_Desc":item.part_desc,
#                     "Annual_demand":item.annual_demand,
#                     "CPN":item.cpn,
#                     "total_OH":item.total_oh,
#                     "quarter_demand_1":item.q0_demand,
#                     "quarter_demand_2":item.q1_demand,
#                     "quarter_demand_3":item.q2_demand,
#                     "quarter_demand_4":item.q3_demand,
#                     "quarter_std_1":item.quarter_std_1,
#                     "quarter_std_2":item.quarter_std_2,
#                     #"Part":item.part,
#                     "Delta_std":item.delta_std,
#                     "quarter_demand_1_x_quarter_std_1":item.delta_demand_x_quarter_std_1,
#                     "quarter_demand_2_x_quarter_std_1":item.delta_demand_2_x_quarter_std_1,
#                     "quarter_demand_3_x_quarter_std_1":item.delta_demand_3_x_quarter_std_1,
#                     "quarter_demand_4_x_quarter_std_1":item.delta_demand_4_x_quarter_std_1,
#                     "Delta_demand":item.delta_demand,
#                     "Delta_Demand_x_quarter_std_1":item.delta_demand_x_delta_std,
#                     "Delta_Demand_x_Delta_std":item.delta_demand_x_delta_std_per,
#                     #"quarter_demand_mapper":item.quarter_demand_mapper,
#                     #"quarter_std_mapper":item.quarter_std_mapper,

#                 }
#             )
#         return json_data


# class top_component_global_data_new(BaseDatatableView):
#     model=TopComponentGlobal
#     max_display_length=20000
#     columns=[
#         "apn",
#         "jpepic",
#         "cm",
#         "globalspend",
#         "jpedelta",
#         "jpedemand",
#         "jpeoh",
#         "jpeowner",
#         "jpestd",
#         "part_desc",
#         "sgdpic",
#         "sgddelta",
#         "sgddemand",
#         "sgdoh",
#         "sgdowner",
#         "sgdstd",
#         "sgddemand",
#         "jpedemand",
#         "globalspend",
#         #"globalspend_percent",
#         #"quarter",
#         #"Team",
#     ]
#     def paging(self,qs):
#         if self.pre_camel_case_notation:
#             limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
#             start = int(self._querydict.get('iDisplayStart', 0))
#         else:
#             limit = min(int(self._querydict.get('length', 200000)), self.max_display_length)
#             start = int(self._querydict.get('start', 0))

#         # if pagination is disabled ("paging": false)
#         if limit == -1:
#             return qs

#         offset = start + limit

#         return qs[start:offset]

#     def get_initial_queryset(self):
#         team_name=self.request.GET.get('team')
#         user=self.request.GET.get('user')
#         print('user data',user)
#         print(filter)
#         f_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('first_name',flat=True)
#         l_name=User.objects.filter(groups=Group.objects.get(name='GSM Team')).values_list('last_name',flat=True)
#         gsm_team=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
#         f_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('first_name',flat=True)
#         l_name=User.objects.filter(groups=Group.objects.get(name='GSM Manager')).values_list('last_name',flat=True)
#         gsm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
#         gsm_team.extend(gsm_manager)
#         #print('GSM Team',gsm_team)
#         l_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('last_name',flat=True)
#         f_name=User.objects.filter(groups=Group.objects.get(name='CMM Team')).values_list('first_name',flat=True)
#         cmm_team=[f'''{list(f_name)[x]} {list(l_name)[x]}''' for x in range(len(f_name)) ]
#         f_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('first_name',flat=True)
#         l_name=User.objects.filter(groups=Group.objects.get(name='CMM Manager')).values_list('last_name',flat=True)
#         cmm_manager=[f'''{(list(f_name)[x])} {list(l_name)[x]}''' for x in range(len(f_name)) ]
#         cmm_team.extend(cmm_manager)
#         if team_name=='GSM' and user=='ALL':
#             data=TopComponentGlobal.objects.using('inputdb').filter(Q(sgdpic__in=gsm_team)|Q(jpepic__in=gsm_team)).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())).order_by("globalspend")
#         elif team_name=='CMM' and user=='ALL':
#             data=TopComponentGlobal.objects.using('inputdb').filter(Q(sgdpic__in=cmm_team)|Q(jpepic__in=cmm_team)).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())).order_by("globalspend")
#         elif team_name=='CMM':
#             userdetails=User.objects.get(id=user)
#             data=TopComponentGlobal.objects.using('inputdb').filter(Q(jpepic=userdetails.first_name + ' ' + userdetails.last_name) | Q(sgdpic=userdetails.first_name + ' ' + userdetails.last_name)).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())).order_by("globalspend")
#         elif team_name=='GSM':
#             userdetails=User.objects.get(id=user)
#             data=TopComponentGlobal.objects.using('inputdb').filter(Q(sgdpic=userdetails.first_name + ' ' + userdetails.last_name)  | Q(sgdpic=userdetails.first_name + ' ' + userdetails.last_name)).annotate(globalspend=ExpressionWrapper((F('jpedemand') * F('jpestd')) + (F('sgddemand') * F('sgdstd')), output_field=FloatField())).order_by("globalspend")
#         return data

#     # def filter_queryset(self,qs):
#     #     return qs
#     def prepare_results(self, qs):
#         # prepare list with output column data
#         # queryset is already paginated here
#         team_name=self.request.GET.get('team')
#         user=self.request.GET.get('user')
#         json_data = []
#         totalspend=qs.aggregate(total_spend=Sum('globalspend'))
#         for item in qs:
#             json_data.append(
#                 {
#                     "APN":item.apn,
#                     "Part_Desc":item.part_desc,
#                     "Ownership_JPE":item.jpeowner,
#                     "Arista_PIC_JPE":item.jpepic,
#                     "total_OH_JPE":item.jpeoh,
#                     "Annual_demand_JPE":item.jpedemand,
#                     "Delta_demand_JPE":item.jpedelta,
#                     "quarter_std_1_JPE":item.jpestd,
#                     "Delta_Demand_multiply_x_quarter_std_1_JPE":item.jpedemand * item.jpestd,
#                     "Ownership_SGD":item.sgdowner,
#                     "Arista_PIC_SGD":item.sgdpic,
#                     "total_OH_SGD":item.sgdoh,
#                     "Annual_demand_SGD":item.sgddemand,
#                     "Delta_demand_SGD":item.sgddelta,
#                     "quarter_std_1_SGD":item.sgdstd,
#                     "quarter_demand_1_x_quarter_std_1_SGD":item.sgddemand * item.sgdstd,
#                     "Global_Annual_Demand":item.sgddemand + item.jpedemand,
#                     "Global_Spend":item.globalspend,
#                     #"Global_Spend_Percentage":"%.3f %%"%float(0 if item.globalspend_percent == None else item.globalspend_percent),
#                     "Global_Spend_Percentage": "%.3f %%"%float(0 if totalspend['total_spend'] == 0 else (item.globalspend*100) / totalspend['total_spend']),
#                     #"quarter":item.quarter,
#                     #"Team":item.Team,
#                 }
#             )
#         return json_data