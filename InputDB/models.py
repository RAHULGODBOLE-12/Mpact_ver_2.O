'''
from InputDB.models import *
'''
from django.db import models
from django_pandas.managers import DataFrameManager
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class AmpartMfrRev(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    ampart = models.CharField(db_column='AMPart', max_length=30)
    ampart_rev = models.CharField(max_length=30, blank=True, null=True)
    ampart_lifecycle = models.CharField(max_length=30, blank=True, null=True)
    ampart_desc = models.CharField(max_length=300, blank=True, null=True)
    mfr_name = models.CharField(max_length=100, blank=True, null=True)
    mfr_lifecycle_phase = models.CharField(db_column='mfr_Lifecycle_Phase', max_length=20, blank=True, null=True)
    mfr_qualification_status = models.CharField(db_column='mfr_Qualification_Status', max_length=20, blank=True, null=True)
    mfr_part_number = models.CharField(db_column='mfr_PART_NUMBER', max_length=50, blank=True, null=True)
    mfrdescription = models.CharField(max_length=200, blank=True, null=True)
    updateddate = models.DateTimeField()
    objects=DataFrameManager()

    class Meta:
        managed = False
        db_table = 'AMpart_mfr_rev'


# class DimAgileAmpartMfrIness(models.Model):
#     id = models.IntegerField(db_column='ID', primary_key=True)
#     ampart = models.CharField(db_column='AMPart', max_length=30,db_index=True)
#     mfr_name = models.CharField(max_length=100, blank=True, null=True)
#     mfr_lifecycle_phase = models.CharField(db_column='mfr_Lifecycle_Phase', max_length=20, blank=True, null=True)
#     mfr_qualification_status = models.CharField(db_column='mfr_Qualification_Status', max_length=20, blank=True, null=True)
#     mfr_part_number = models.CharField(db_column='mfr_PART_NUMBER', max_length=50, blank=True, null=True)
#     mfrdescription = models.CharField(max_length=200, blank=True, null=True)
#     updateddate = models.DateTimeField()
#     objects=DataFrameManager()
#     class Meta:
#         managed = False
#         db_table = 'Dim_Agile_AMpart_mfr_InESS'

class DimAgileAmpartMfrIness(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    ampart = models.CharField(db_column='AMPart', max_length=30)  # Field name made lowercase.
    ampart_rev = models.CharField(db_column='ampartrev',max_length=10, blank=True, null=True)
    ampart_lifecycle = models.CharField(db_column='ampartlifecycle',max_length=30, blank=True, null=True)
    ampart_desc = models.CharField(db_column='ampartdescription',max_length=300, blank=True, null=True)
    mfr_name = models.CharField(db_column='mfr_name',max_length=100, blank=True, null=True)
    mfr_lifecycle_phase = models.CharField(db_column='mfr_Lifecycle_Phase', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mfr_qualification_status = models.CharField(db_column='mfr_Qualification_Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mfr_part_number = models.CharField(db_column='mfr_PART_NUMBER', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mfrdescription = models.CharField(db_column='mfrdescription',max_length=200, blank=True, null=True)
    updateddate = models.DateTimeField()
    objects=DataFrameManager()

    class Meta:
        managed = False
        db_table = 'Dim_Agile_AMpart_mfr_InESS'
class InputdbJpeHistory(models.Model):
    cm_partno = models.CharField(max_length=50, blank=True, null=True)
    arista_partno = models.CharField(max_length=50, blank=True, null=True)
    consign_partno = models.CharField(max_length=10, blank=True, null=True)
    buyer = models.CharField(max_length=20, blank=True, null=True)
    item_desc = models.CharField(max_length=300, blank=True, null=True)
    commodity = models.CharField(max_length=10, blank=True, null=True)
    supplier = models.CharField(max_length=10, blank=True, null=True)
    mfg = models.CharField(db_column='MFG', max_length=10, blank=True, null=True)
    mpn = models.CharField(db_column='MPN', max_length=20, blank=True, null=True)
    lt = models.CharField(db_column='LT', max_length=20, blank=True, null=True)
    moq = models.CharField(db_column='MOQ', max_length=20, blank=True, null=True)
    moq_analysis = models.CharField(db_column='MOQ_analysis', max_length=20, blank=True, null=True)
    moq_cost = models.CharField(db_column='MOQ_cost', max_length=20, blank=True, null=True)
    po_delivery = models.CharField(max_length=20, blank=True, null=True)
    basedate = models.CharField(max_length=20, blank=True, null=True)
    remark = models.CharField(max_length=20, blank=True, null=True)
    jpe_quantity_on_hand = models.CharField(db_column='JPE_quantity_on_hand', max_length=20, blank=True, null=True)
    open_po_due_current_qtr = models.CharField(db_column='open_PO_due_current_qtr', max_length=20, blank=True, null=True)
    open_po_due_in_next_qtr = models.CharField(db_column='open_PO_due_in_next_qtr', max_length=20, blank=True, null=True)
    total_oh_plus_opo_current_qtr = models.CharField(db_column='total_OH_plus_OPO_current_qtr', max_length=20, blank=True, null=True)
    total_oh_plus_opo_current_plus_next_qtr = models.CharField(db_column='total_OH_plus_OPO_current_plus_next_qtr', max_length=20, blank=True, null=True)
    notes_refreshed_demand = models.CharField(max_length=200, blank=True, null=True)
    cq_demand = models.CharField(max_length=20, blank=True, null=True)
    cq_plus_1_demand = models.CharField(max_length=20, blank=True, null=True)
    cq_plus_2_demand = models.CharField(max_length=20, blank=True, null=True)
    delta_oh = models.CharField(db_column='delta_OH', max_length=20, blank=True, null=True)
    notes_refreshed_demand_updated = models.CharField(max_length=20, blank=True, null=True)
    prev_qtr_unit_price_usd = models.CharField(db_column='prev_qtr_unit_price_USD', max_length=300, blank=True, null=True)
    current_qtr_unit_price_usd = models.CharField(db_column='current_qtr_unit_price_USD', max_length=300, blank=True, null=True)
    delta = models.CharField(max_length=30, blank=True, null=True)
    new_delta = models.CharField(max_length=30, blank=True, null=True)
    need_attention = models.CharField(max_length=30, blank=True, null=True)
    new_next_qtr_demand = models.CharField(max_length=30, db_column='new_next_qtr_Demand', blank=True, null=True)
    new_next_qtr_plus_1_demand = models.CharField(max_length=30, db_column='new_next_qtr_plus_1_Demand', blank=True, null=True)
    new_next_qtr_plus_2_demand = models.CharField(max_length=30, db_column='new_next_qtr_plus_2_Demand', blank=True, null=True)
    theresa_current_qtr_comments = models.CharField(db_column='Theresa_current_qtr_comments', max_length=300, blank=True, null=True)
    new_po_price_and_current_qtr_std_target = models.CharField(db_column='new_PO_price_and_current_qtr_std_target', max_length=20, blank=True, null=True)
    approve_or_reject_column_aa_cost = models.CharField(db_column='approve_or_reject_column_AA_cost', max_length=20, blank=True, null=True)
    arista_std_price_current_qtr = models.CharField(max_length=20, blank=True, null=True)
    arista_supplier_name_cost_splits = models.CharField(max_length=20, blank=True, null=True)
    arista_sup_name = models.CharField(max_length=200, blank=True, null=True)
    arista_advise_moq = models.CharField(db_column='arista_advise_MOQ', max_length=20, blank=True, null=True)
    arista_advise_lead_time = models.CharField(max_length=20, blank=True, null=True)
    arista_supplier_mpn = models.CharField(db_column='arista_supplier_MPN', max_length=20, blank=True, null=True)
    arista_sup_split = models.CharField(max_length=20, blank=True, null=True)
    arista_sup_std_cost = models.CharField(max_length=20, blank=True, null=True)
    arista_comment_current_qtr = models.CharField(max_length=20, blank=True, null=True)
    arista_st_ht = models.CharField(max_length=300, blank=True, null=True)
    ownership = models.CharField(max_length=50, blank=True, null=True)
    arista_pic = models.CharField(db_column='arista_PIC', max_length=50, blank=True, null=True)
    remark_actions_for_cmgrs_jpe_cq = models.CharField(db_column='remark_actions_for_Cmgrs_JPE_CQ', max_length=50, blank=True, null=True)
    delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned = models.CharField(db_column='delta_of_new_recommend_price_current_vs_prev_Arista_JPE_owned', max_length=50, blank=True, null=True)
    jpe_remark = models.CharField(db_column='JPE_remark', max_length=150, blank=True, null=True)
    new_jabil_recommended_price_current_qtr = models.CharField(max_length=50, blank=True, null=True)
    jabil_supplier = models.CharField(max_length=50, blank=True, null=True)
    jabil_sup_name = models.CharField(max_length=200, blank=True, null=True)
    jabil_advise_moq = models.CharField(db_column='jabil_advise_MOQ', max_length=50, blank=True, null=True)
    jabil_advise_lead_time = models.CharField(max_length=50, blank=True, null=True)
    jabil_supplier_mpn = models.CharField(db_column='jabil_supplier_MPN', max_length=50, blank=True, null=True)
    jabil_supplier_splits = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'InputDB_jpe_history'

class InputdbSgdHistory(models.Model):
    cm_partno = models.CharField(max_length=50, blank=True, null=True)
    arista_partno = models.CharField(max_length=50, blank=True, null=True)
    consign_partno = models.CharField(max_length=10, blank=True, null=True)
    controlby = models.CharField(db_column='controlBy', max_length=20, blank=True, null=True)
    item_desc = models.CharField(max_length=300, blank=True, null=True)
    lt = models.CharField(db_column='LT', max_length=10, blank=True, null=True)
    moq = models.CharField(db_column='MOQ', max_length=10, blank=True, null=True)
    po_delivery = models.CharField(max_length=10, blank=True, null=True)
    basedate = models.CharField(max_length=20, blank=True, null=True)
    oh_plus_csinv = models.CharField(max_length=20, blank=True, null=True)
    openpo_prev_qtr = models.CharField(db_column='openPO_prev_qtr', max_length=20, blank=True, null=True)
    openpo_current_qtr = models.CharField(db_column='openPO_current_qtr', max_length=20, blank=True, null=True)
    total_oh_delivery_based = models.CharField(max_length=20, blank=True, null=True)
    po_based_total_oh_opo = models.CharField(max_length=20, blank=True, null=True)
    prev_qtr_demand = models.CharField(max_length=20, blank=True, null=True)
    current_qtr_demand = models.CharField(max_length=20, blank=True, null=True)
    next_qtr_demand = models.CharField(max_length=20, blank=True, null=True)
    next_qtr_1_demand = models.CharField(max_length=20, blank=True, null=True)
    delta_op_opo = models.CharField(max_length=20, blank=True, null=True)
    current_std_price = models.CharField(max_length=20, blank=True, null=True)
    forecast_std_price = models.CharField(max_length=20, blank=True, null=True)
    blended_avg_po_price = models.CharField(max_length=20, blank=True, null=True)
    new_po_price = models.CharField(max_length=20, blank=True, null=True)
    is_arista_recomented = models.CharField(max_length=20, blank=True, null=True)
    arista_std_price = models.CharField(max_length=20, blank=True, null=True)
    arista_supplier_name = models.CharField(max_length=300, blank=True, null=True)
    arista_moq = models.CharField(max_length=20, blank=True, null=True)
    arista_lead_time = models.CharField(max_length=20, blank=True, null=True)
    arista_supplier_mpn = models.CharField(max_length=20, blank=True, null=True)
    arista_ncnr = models.CharField(max_length=20, blank=True, null=True)
    arista_st_ht = models.CharField(max_length=20, blank=True, null=True)
    arista_part_ownership = models.CharField(max_length=20, blank=True, null=True)
    arista_pic = models.CharField(max_length=20, blank=True, null=True)
    sanmina_quoted_price = models.CharField(max_length=20, blank=True, null=True)
    sanmina_mfg = models.CharField(max_length=300, blank=True, null=True)
    sanmina_mpn = models.CharField(max_length=50, blank=True, null=True)
    sanmina_advise_moq = models.CharField(max_length=50, blank=True, null=True)
    sanmina_advise_lt = models.CharField(max_length=50, blank=True, null=True)
    sanmina_ncnr = models.CharField(max_length=50, blank=True, null=True)
    sanmina_splits = models.CharField(max_length=50, blank=True, null=True)
    buffer_oh = models.CharField(max_length=20, blank=True, null=True)
    arista_sup_name = models.CharField(max_length=300, blank=True, null=True)
    arista_sup_split = models.CharField(max_length=300, blank=True, null=True)
    arista_sup_std_cost = models.CharField(max_length=30, blank=True, null=True)
    sanmina_suppliers = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'InputDB_sgd_history'


class InputdbSsjHistory(models.Model):
    cm_partno = models.CharField(max_length=50, blank=True, null=True)
    arista_partno = models.CharField(max_length=50, blank=True, null=True)
    consign_partno = models.CharField(max_length=10, blank=True, null=True)
    controlby = models.CharField(db_column='controlBy', max_length=20, blank=True, null=True)
    item_desc = models.CharField(max_length=300, blank=True, null=True)
    lt = models.CharField(db_column='LT', max_length=10, blank=True, null=True)
    moq = models.CharField(db_column='MOQ', max_length=10, blank=True, null=True)
    po_delivery = models.CharField(max_length=10, blank=True, null=True)
    basedate = models.CharField(max_length=20, blank=True, null=True)
    buffer_oh = models.CharField(max_length=20, blank=True, null=True)
    oh_plus_csinv = models.CharField(max_length=20, blank=True, null=True)
    openpo_prev_qtr = models.CharField(db_column='openPO_prev_qtr', max_length=20, blank=True, null=True)
    openpo_current_qtr = models.CharField(db_column='openPO_current_qtr', max_length=20, blank=True, null=True)
    total_oh_delivery_based = models.CharField(max_length=20, blank=True, null=True)
    po_based_total_oh_opo = models.CharField(max_length=20, blank=True, null=True)
    prev_qtr_demand = models.CharField(max_length=20, blank=True, null=True)
    current_qtr_demand = models.CharField(max_length=20, blank=True, null=True)
    next_qtr_demand = models.CharField(max_length=20, blank=True, null=True)
    next_qtr_1_demand = models.CharField(max_length=20, blank=True, null=True)
    delta_op_opo = models.CharField(max_length=20, blank=True, null=True)
    current_std_price = models.CharField(max_length=20, blank=True, null=True)
    forecast_std_price = models.CharField(max_length=20, blank=True, null=True)
    blended_avg_po_price = models.CharField(max_length=20, blank=True, null=True)
    new_po_price = models.CharField(max_length=20, blank=True, null=True)
    is_arista_recomented = models.CharField(max_length=20, blank=True, null=True)
    arista_std_price = models.CharField(max_length=20, blank=True, null=True)
    arista_supplier_name = models.CharField(max_length=300, blank=True, null=True)
    arista_sup_name = models.CharField(max_length=300, blank=True, null=True)
    arista_sup_std_cost = models.CharField(max_length=30, blank=True, null=True)
    arista_sup_split = models.CharField(max_length=300, blank=True, null=True)
    arista_moq = models.CharField(max_length=20, blank=True, null=True)
    arista_lead_time = models.CharField(max_length=20, blank=True, null=True)
    arista_supplier_mpn = models.CharField(max_length=20, blank=True, null=True)
    arista_ncnr = models.CharField(max_length=20, blank=True, null=True)
    arista_st_ht = models.CharField(max_length=20, blank=True, null=True)
    arista_part_ownership = models.CharField(max_length=20, blank=True, null=True)
    arista_pic = models.CharField(max_length=20, blank=True, null=True)
    sanmina_quoted_price = models.CharField(max_length=20, blank=True, null=True)
    sanmina_mfg = models.CharField(max_length=300, blank=True, null=True)
    sanmina_mpn = models.CharField(max_length=50, blank=True, null=True)
    sanmina_advise_moq = models.CharField(max_length=50, blank=True, null=True)
    sanmina_advise_lt = models.CharField(max_length=50, blank=True, null=True)
    sanmina_ncnr = models.CharField(max_length=50, blank=True, null=True)
    sanmina_suppliers = models.CharField(max_length=150, blank=True, null=True)
    sanmina_splits = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'InputDB_ssj_history'

class InputdbTopBomCmm(models.Model):
    quarter = models.CharField(max_length=10, blank=True, null=True)
    family = models.CharField(db_column='Family', max_length=50, blank=True, null=True)  # Field name made lowercase.
    model = models.CharField(db_column='Model', max_length=50, blank=True, null=True)  # Field name made lowercase.
    product_sku = models.CharField(db_column='Product_SKU', max_length=50, blank=True, null=True)  # Field name made lowercase.
    assembly_sku = models.CharField(db_column='Assembly_SKU', max_length=50, blank=True, null=True)  # Field name made lowercase.
    amparts = models.CharField(max_length=50, blank=True, null=True)
    tla_number = models.CharField(db_column='TLA_Number', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tla_number_excld_rev = models.CharField(db_column='TLA_Number_excld_rev', max_length=30, blank=True, null=True)  # Field name made lowercase.
    assembly_description = models.CharField(db_column='Assembly_Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rev = models.CharField(max_length=11, blank=True, null=True)
    refreshed_rev = models.CharField(max_length=30, blank=True, null=True)
    part_lifecycle = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.CharField(max_length=30, blank=True, null=True)
    refreshed_date = models.CharField(max_length=30, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='Not Freezed')
    scenarioid = models.IntegerField(blank=True, null=True)
    npi_reportdate = models.CharField(max_length=20, blank=True, null=True)
    npi_demands = models.CharField(max_length=20, blank=True, null=True)
    animin = models.CharField(max_length=11, blank=True, null=True)
    cq_demand = models.CharField(max_length=11, blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    npi_notes = models.CharField(max_length=1000, blank=True, null=True)
    agile_notes = models.CharField(max_length=100, blank=True, null=True)
    refreshed_by = models.CharField(max_length=20, blank=True, null=True)
    prod_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    npi_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'InputDB_top_bom_cmm'


class InputdbTopBomCmmHistory(models.Model):
    quarter = models.CharField(max_length=10, blank=True, null=True)
    family = models.CharField(db_column='Family', max_length=50, blank=True, null=True)  # Field name made lowercase.
    model = models.CharField(db_column='Model', max_length=50, blank=True, null=True)  # Field name made lowercase.
    product_sku = models.CharField(db_column='Product_SKU', max_length=50, blank=True, null=True)  # Field name made lowercase.
    assembly_sku = models.CharField(db_column='Assembly_SKU', max_length=50, blank=True, null=True)  # Field name made lowercase.
    amparts = models.CharField(max_length=50, blank=True, null=True)
    tla_number = models.CharField(db_column='TLA_Number', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tla_number_excld_rev = models.CharField(db_column='TLA_Number_excld_rev', max_length=30, blank=True, null=True)  # Field name made lowercase.
    assembly_description = models.CharField(db_column='Assembly_Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rev = models.CharField(max_length=11, blank=True, null=True)
    refreshed_rev = models.CharField(max_length=30, blank=True, null=True)
    part_lifecycle = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.CharField(max_length=30, blank=True, null=True)
    refreshed_date = models.CharField(max_length=30, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    scenarioid = models.IntegerField(blank=True, null=True)
    npi_reportdate = models.CharField(max_length=20, blank=True, null=True)
    npi_demands = models.CharField(max_length=20, blank=True, null=True)
    animin = models.CharField(max_length=11, blank=True, null=True)
    cq_demand = models.CharField(max_length=11, blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    npi_notes = models.CharField(max_length=1000, blank=True, null=True)
    agile_notes = models.CharField(max_length=100, blank=True, null=True)
    refreshed_by = models.CharField(max_length=20, blank=True, null=True)
    prod_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    npi_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'InputDB_top_bom_cmm_history'


class InputdbTopBomGsm(models.Model):
    quarter = models.CharField(max_length=10, blank=True, null=True)
    oem_part_number = models.CharField(max_length=30, blank=True, null=True)
    oem_part_number_xx = models.CharField(max_length=30, blank=True, null=True)
    tla = models.CharField(db_column='TLA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    sanminapn = models.CharField(db_column='SanminaPN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rev = models.CharField(db_column='Rev', max_length=30, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    program_name = models.CharField(max_length=100, blank=True, null=True)
    product_family = models.CharField(max_length=100, blank=True, null=True)
    direct_material_cost = models.CharField(max_length=30, blank=True, null=True)
    mva = models.CharField(max_length=30, blank=True, null=True)
    unit_price = models.CharField(max_length=30, blank=True, null=True)
    comments = models.CharField(max_length=300, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='Not Freezed')
    scenarioid = models.IntegerField(blank=True, null=True)
    npi_reportdate = models.CharField(max_length=20, blank=True, null=True)
    cq_demand = models.CharField(max_length=10, blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    animin = models.CharField(max_length=11, blank=True, null=True)
    npi_demands = models.CharField(max_length=20, blank=True, null=True)
    npi_notes = models.CharField(max_length=1000, blank=True, null=True)
    agile_notes = models.CharField(max_length=100, blank=True, null=True)
    refreshed_by = models.CharField(max_length=20, blank=True, null=True)
    prod_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    npi_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)
    refreshed_rev = models.CharField(max_length=30, blank=True, null=True)
    part_lifecycle = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.CharField(max_length=30, blank=True, null=True)
    refreshed_date = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'InputDB_top_bom_gsm'


class InputdbTopBomGsmHistory(models.Model):
    quarter = models.CharField(max_length=10, blank=True, null=True)
    oem_part_number = models.CharField(max_length=30, blank=True, null=True)
    oem_part_number_xx = models.CharField(max_length=30, blank=True, null=True)
    tla = models.CharField(db_column='TLA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    sanminapn = models.CharField(db_column='SanminaPN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rev = models.CharField(db_column='Rev', max_length=30, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    program_name = models.CharField(max_length=100, blank=True, null=True)
    product_family = models.CharField(max_length=100, blank=True, null=True)
    direct_material_cost = models.CharField(max_length=30, blank=True, null=True)
    mva = models.CharField(max_length=30, blank=True, null=True)
    unit_price = models.CharField(max_length=30, blank=True, null=True)
    comments = models.CharField(max_length=300, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    scenarioid = models.IntegerField(blank=True, null=True)
    npi_reportdate = models.CharField(max_length=20, blank=True, null=True)
    cq_demand = models.CharField(max_length=10, blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    animin = models.CharField(max_length=11, blank=True, null=True)
    npi_demands = models.CharField(max_length=20, blank=True, null=True)
    npi_notes = models.CharField(max_length=1000, blank=True, null=True)
    agile_notes = models.CharField(max_length=100, blank=True, null=True)
    refreshed_by = models.CharField(max_length=20, blank=True, null=True)
    prod_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    npi_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)
    refreshed_rev = models.CharField(max_length=30, blank=True, null=True)
    part_lifecycle = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.CharField(max_length=30, blank=True, null=True)
    refreshed_date = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'InputDB_top_bom_gsm_history'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class FactAgileIness(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    ampart = models.CharField(db_column='AMPart', max_length=30,db_index=True,)
    ampart_rev = models.CharField(max_length=10)
    ampart_lifecycle = models.CharField(max_length=27, blank=True, null=True)
    ampart_release_date = models.DateTimeField(blank=True, null=True)
    ampart_description = models.CharField(max_length=300, blank=True, null=True)
    usedin = models.CharField(db_column='UsedIN', max_length=30, blank=True, null=True)
    used_in_lifecycle = models.CharField(max_length=27, blank=True, null=True)
    used_in_rev = models.CharField(max_length=10, blank=True, null=True)
    at_qty_of = models.DecimalField(db_column='At_Qty_of', max_digits=10, decimal_places=0, blank=True, null=True)
    mfr_name = models.CharField(max_length=100, blank=True, null=True)
    mfr_lifecycle_phase = models.CharField(db_column='mfr_Lifecycle_Phase', max_length=20, blank=True, null=True)
    mfr_qualification_status = models.CharField(db_column='mfr_Qualification_Status', max_length=20, blank=True, null=True)
    mfr_part_number = models.CharField(db_column='mfr_PART_NUMBER', max_length=50, blank=True, null=True)
    mfrdescription = models.CharField(max_length=200, blank=True, null=True)
    updatedate = models.DateField()

    class Meta:
        managed = False
        db_table = 'fact_Agile_InESS'
        unique_together = (('id', 'updatedate'),)


class FactAgilePartnumberIness(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    ampart = models.CharField(db_column='AMPart', max_length=30)
    ampart_rev = models.CharField(max_length=10)
    ampart_lifecycle = models.CharField(max_length=27, blank=True, null=True)
    ampart_release_date = models.CharField(max_length=30, blank=True, null=True)
    ampart_description = models.CharField(max_length=300, blank=True, null=True)
    usedin = models.CharField(db_column='UsedIN', max_length=30, blank=True, null=True)
    used_in_lifecycle = models.CharField(max_length=27, blank=True, null=True)
    used_in_rev = models.CharField(max_length=10, blank=True, null=True)
    qty = models.CharField(db_column='Qty', max_length=20, blank=True, null=True)
    level = models.IntegerField()
    updateddate = models.DateTimeField()
    objects=DataFrameManager()

    class Meta:
        managed = False
        db_table = 'fact_Agile_PartNumber_InESS'


class FactLatestProductionForecastIness(models.Model):
    prodid = models.BigIntegerField(blank=True, null=True)
    forecastscenarioid = models.BigIntegerField(db_column='forecastScenarioID', blank=True, null=True)
    siteid = models.BigIntegerField(db_column='siteID', blank=True, null=True)
    calid = models.BigIntegerField(db_column='calID', blank=True, null=True)
    forecastqty = models.BigIntegerField(db_column='ForecastQty', blank=True, null=True)
    caldate = models.DateField(db_column='calDate', blank=True, null=True)
    netsuiteitem = models.TextField(db_column='netsuiteItem', blank=True, null=True)
    basemodel = models.TextField(blank=True, null=True)
    model = models.TextField(blank=True, null=True)
    aristapartnumber = models.TextField(db_column='aristaPartNumber', blank=True, null=True)
    netsuitefamily = models.TextField(blank=True, null=True)
    scenariodate = models.DateField(db_column='scenarioDate', blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    rollingfourweekdemand = models.BigIntegerField(db_column='rollingFourWeekDemand', blank=True, null=True)
    backlog = models.BigIntegerField(db_column='Backlog', blank=True, null=True)
    globalonhand = models.BigIntegerField(db_column='GlobalOnHand', blank=True, null=True)
    nsbacklog = models.BigIntegerField(db_column='NSBacklog', blank=True, null=True)
    nsglobalonhand = models.BigIntegerField(db_column='nsGlobalOnHand', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fact_Latest_Production_forecast_iness'


class VwFactLatestProductionForecastIness(models.Model):
    prodid = models.BigIntegerField(blank=True, null=True)
    forecastscenarioid = models.BigIntegerField(db_column='forecastScenarioID', blank=True, null=True)
    siteid = models.BigIntegerField(db_column='siteID', blank=True, null=True)
    calid = models.BigIntegerField(db_column='calID', blank=True, null=True)
    forecastqty = models.BigIntegerField(db_column='ForecastQty', blank=True, null=True)
    caldate = models.DateField(db_column='calDate', blank=True, null=True)
    netsuiteitem = models.TextField(db_column='netsuiteItem', blank=True, null=True)
    basemodel = models.TextField(blank=True, null=True)
    model = models.TextField(blank=True, null=True)
    aristapartnumber = models.TextField(db_column='aristaPartNumber', blank=True, null=True)
    netsuitefamily = models.TextField(blank=True, null=True)
    scenariodate = models.DateField(db_column='scenarioDate', blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    rollingfourweekdemand = models.BigIntegerField(db_column='rollingFourWeekDemand', blank=True, null=True)
    backlog = models.BigIntegerField(db_column='Backlog', blank=True, null=True)
    globalonhand = models.BigIntegerField(db_column='GlobalOnHand', blank=True, null=True)
    nsbacklog = models.BigIntegerField(db_column='NSBacklog', blank=True, null=True)
    nsglobalonhand = models.BigIntegerField(db_column='nsGlobalOnHand', blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    appliedanimin = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vw_fact_Latest_Production_forecast_iness'


class VwFactJpeMrpIness(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    buyercode = models.CharField(db_column='BuyerCode', max_length=50)
    origpartcode = models.CharField(db_column='OrigPartCode', max_length=300)
    supplier = models.CharField(db_column='Supplier', max_length=100)
    caldate = models.DateField(db_column='CalDate')
    reportdate = models.DateField(db_column='ReportDate')
    filereceiveddate = models.DateField(db_column='FileReceivedDate')
    mmlt = models.IntegerField(db_column='MMLT')
    clt = models.IntegerField(db_column='CLT')
    moq = models.IntegerField(db_column='MOQ')
    standardprice = models.FloatField(db_column='StandardPrice')
    safetystock = models.IntegerField(db_column='SafetyStock')
    safetyleadtime = models.IntegerField(db_column='SafetyLeadTime')
    lodid = models.IntegerField(db_column='LodID')
    jabilowninventory = models.IntegerField(db_column='JabilOwnInventory')
    consignedinv = models.IntegerField(db_column='ConsignedInv')
    poqty = models.IntegerField(db_column='POQty')
    aristapartnumber = models.CharField(db_column='AristaPartnumber', max_length=50)
    demandqty = models.IntegerField()
    objects=DataFrameManager()
    class Meta:
        managed = False
        db_table = 'vw_fact_jpe_mrp_iness'


class VwFactNpiforecastBuildscheduleIness(models.Model):
    id = models.IntegerField(primary_key=True)
    program = models.CharField(max_length=50)
    build = models.CharField(max_length=25)
    qty = models.IntegerField()
    config = models.CharField(max_length=100)
    cmbuild = models.CharField(max_length=25)
    buykit = models.CharField(max_length=80)
    status = models.CharField(max_length=30)
    cm = models.CharField(max_length=30)
    fabturnship = models.DecimalField(max_digits=10, decimal_places=0)
    pcbfabout = models.DateField()
    absrdue = models.DateField()
    buildstart = models.DateField()
    pcafirstoffandormechasystart = models.DateField()
    buildfinish = models.DateField()
    testrequirements = models.CharField(max_length=500)
    buildnotes = models.CharField(max_length=4000)
    chipvers = models.CharField(max_length=500)
    materialsnotes = models.CharField(max_length=1000)
    pm = models.CharField(max_length=30)
    hw = models.CharField(max_length=30)
    npieelec = models.CharField(max_length=30)
    diags = models.CharField(max_length=30)
    mechde = models.CharField(db_column='mechDe', max_length=30)
    npiemech = models.CharField(max_length=30)
    scmm = models.CharField(max_length=30)
    mfgtesteng = models.CharField(db_column='mfgTestEng', max_length=30)
    family = models.CharField(max_length=30)
    reportdate = models.DateField(db_column='ReportDate')

    class Meta:
        managed = False
        db_table = 'vw_fact_npiforecast_buildschedule_iness'


class VwFactSgdMrpIness(models.Model):
    id = models.IntegerField(primary_key=True)
    buyer = models.CharField(max_length=50)
    part = models.CharField(max_length=30)
    aristapartnumber = models.CharField(db_column='AristaPartNumber', max_length=30)
    partnumbase = models.CharField(db_column='PartNumBase', max_length=30)
    cpn = models.CharField(max_length=300)
    supplier = models.CharField(max_length=100)
    cumlt = models.IntegerField()
    ncnr = models.IntegerField()
    moq = models.IntegerField()
    quotedprice = models.FloatField()
    safetystock = models.IntegerField()
    bufferstock = models.IntegerField()
    bufferpoopenqty = models.IntegerField()
    onhandqty = models.IntegerField()
    consignedinv = models.IntegerField(db_column='Consignedinv')
    vci = models.IntegerField()
    crl = models.IntegerField()
    outp = models.IntegerField()
    openpoopenqty = models.IntegerField()
    past = models.IntegerField()
    demandqty = models.IntegerField()
    caldate = models.DateField(db_column='CalDate')
    createdate = models.DateField(db_column='createDate')
    reportdate = models.DateField(db_column='ReportDate')
    objects=DataFrameManager()

    class Meta:
        managed = False
        db_table = 'vw_fact_sgd_mrp_iness'


class FactSgdMrpByQuarter(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    part = models.CharField(max_length=30)
    quartername = models.CharField(db_column='QuarterName', max_length=50)
    reportdate = models.DateField(db_column='ReportDate')
    qty = models.IntegerField()
    objects=DataFrameManager()
    class Meta:
        managed = False
        db_table = 'fact_sgd_mrp_by_quarter'

class TopComponentJpe(models.Model):
    cpn = models.CharField(db_column='CPN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    apn = models.CharField(db_column='APN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    arista_pic = models.CharField(db_column='Arista_PIC', max_length=200, blank=True, null=True)  # Field name made lowercase.
    ownership = models.CharField(db_column='Ownership', max_length=50, blank=True, null=True)  # Field name made lowercase.
    part_desc = models.TextField(db_column='Part_Desc', blank=True, null=True)  # Field name made lowercase.
    po_or_delivery = models.CharField(db_column='PO_or_Delivery', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cm_buffer_on_hand = models.FloatField(db_column='CM_Buffer_On_Hand', blank=True, null=True)  # Field name made lowercase.
    cs_inv = models.FloatField(db_column='CS_Inv', blank=True, null=True)  # Field name made lowercase.
    open_po = models.FloatField(db_column='Open_PO', blank=True, null=True)  # Field name made lowercase.
    total_oh = models.FloatField(db_column='Total_OH', blank=True, null=True)  # Field name made lowercase.
    q0_demand = models.FloatField(db_column='Q0_Demand', blank=True, null=True)  # Field name made lowercase.
    q1_demand = models.FloatField(db_column='Q1_Demand', blank=True, null=True)  # Field name made lowercase.
    q2_demand = models.FloatField(db_column='Q2_Demand', blank=True, null=True)  # Field name made lowercase.
    q3_demand = models.FloatField(db_column='Q3_Demand', blank=True, null=True)  # Field name made lowercase.
    annual_demand = models.FloatField(db_column='Annual_Demand', blank=True, null=True)  # Field name made lowercase.
    delta_demand = models.FloatField(db_column='Delta_Demand', blank=True, null=True)  # Field name made lowercase.
    quarter_std_1 = models.FloatField(blank=True, null=True)
    quarter_std_2 = models.FloatField(blank=True, null=True)
    delta_std = models.FloatField(db_column='Delta_std', blank=True, null=True)  # Field name made lowercase.
    delta_demand_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_2_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_2_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_3_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_3_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_4_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_4_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_x_delta_std = models.FloatField(db_column='Delta_Demand_x_Delta_std', blank=True, null=True)  # Field name made lowercase.
    delta_demand_x_delta_std_per = models.FloatField(db_column='Delta_Demand_x_Delta_std_per', blank=True, null=True)  # Field name made lowercase.
    quarter = models.CharField(max_length=10, blank=True, null=True)
    qtr_id = models.IntegerField(blank=True, null=True)
    team = models.CharField(db_column='Team', max_length=50, blank=True, null=True)  # Field name made lowercase.
    contract_mfr = models.CharField(db_column='Contract_Mfr', max_length=50, blank=True, null=True)  # Field name made lowercase.
    qtr_col = models.CharField(max_length=100)
    reportdate = models.DateField()

    class Meta:
        managed = False
        db_table = 'top_component_jpe'


class TopComponentSgd(models.Model):
    cpn = models.CharField(db_column='CPN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    apn = models.CharField(db_column='APN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    arista_pic = models.CharField(db_column='Arista_PIC', max_length=200, blank=True, null=True)  # Field name made lowercase.
    ownership = models.CharField(db_column='Ownership', max_length=50, blank=True, null=True)  # Field name made lowercase.
    part_desc = models.TextField(db_column='Part_Desc', blank=True, null=True)  # Field name made lowercase.
    po_or_delivery = models.CharField(db_column='PO_or_Delivery', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cm_buffer_on_hand = models.FloatField(db_column='CM_Buffer_On_Hand', blank=True, null=True)  # Field name made lowercase.
    cs_inv = models.FloatField(db_column='CS_Inv', blank=True, null=True)  # Field name made lowercase.
    open_po = models.FloatField(db_column='Open_PO', blank=True, null=True)  # Field name made lowercase.
    total_oh = models.FloatField(db_column='Total_OH', blank=True, null=True)  # Field name made lowercase.
    q0_demand = models.FloatField(db_column='Q0_Demand', blank=True, null=True)  # Field name made lowercase.
    q1_demand = models.FloatField(db_column='Q1_Demand', blank=True, null=True)  # Field name made lowercase.
    q2_demand = models.FloatField(db_column='Q2_Demand', blank=True, null=True)  # Field name made lowercase.
    q3_demand = models.FloatField(db_column='Q3_Demand', blank=True, null=True)  # Field name made lowercase.
    annual_demand = models.FloatField(db_column='Annual_Demand', blank=True, null=True)  # Field name made lowercase.
    delta_demand = models.FloatField(db_column='Delta_Demand', blank=True, null=True)  # Field name made lowercase.
    quarter_std_1 = models.FloatField(blank=True, null=True)
    quarter_std_2 = models.FloatField(blank=True, null=True)
    delta_std = models.FloatField(db_column='Delta_std', blank=True, null=True)  # Field name made lowercase.
    delta_demand_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_2_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_2_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_3_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_3_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_4_x_quarter_std_1 = models.FloatField(db_column='Delta_Demand_4_x_quarter_std_1', blank=True, null=True)  # Field name made lowercase.
    delta_demand_x_delta_std = models.FloatField(db_column='Delta_Demand_x_Delta_std', blank=True, null=True)  # Field name made lowercase.
    delta_demand_x_delta_std_per = models.FloatField(db_column='Delta_Demand_x_Delta_std_per', blank=True, null=True)  # Field name made lowercase.
    quarter = models.CharField(max_length=10, blank=True, null=True)
    qtr_id = models.IntegerField(blank=True, null=True)
    team = models.CharField(db_column='Team', max_length=50, blank=True, null=True)  # Field name made lowercase.
    contract_mfr = models.CharField(db_column='Contract_Mfr', max_length=50, blank=True, null=True)  # Field name made lowercase.
    qtr_col = models.CharField(max_length=100)
    reportdate = models.DateField()

    class Meta:
        managed = False
        db_table = 'top_component_sgd'

class TopComponentGlobal(models.Model):
    apn = models.CharField(db_column='APN', max_length=50, primary_key=True)
    arista_pic = models.CharField(db_column='Arista_PIC', max_length=200, blank=True, null=True)
    part_desc = models.TextField(db_column='Part_Desc', blank=True, null=True)
    jpepic = models.CharField(max_length=200, blank=True, null=True)
    sgdpic = models.CharField(max_length=200, blank=True, null=True)
    jpeowner = models.CharField(max_length=50, blank=True, null=True)
    sgdowner = models.CharField(max_length=50, blank=True, null=True)
    jpedemand = models.FloatField(default=0)
    sgddemand = models.FloatField(default=0)
    jpeoh = models.FloatField(default=0)
    sgdoh = models.FloatField(default=0)
    jpestd = models.FloatField(default=0)
    sgdstd = models.FloatField(default=0)
    jpedelta = models.FloatField(default=0)
    sgddelta = models.FloatField(default=0)
    cm = models.CharField(max_length=50, blank=True, null=True)
    #globalspend = models.FloatField(blank=True, null=True)
    #globaldemand = models.FloatField(blank=True, null=True)
    #globalspend_percent = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'top_component_global_jpe_sgd'



class InputdbTopBomFgn(models.Model):
    quarter = models.CharField(max_length=10, blank=True, null=True)
    oem_part_number = models.CharField(max_length=30, blank=True, null=True)
    oem_part_number_xx = models.CharField(max_length=30, blank=True, null=True)
    tla = models.CharField(db_column='TLA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    flexpn = models.CharField(db_column='FlexPN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rev = models.CharField(db_column='Rev', max_length=30, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    program_name = models.CharField(max_length=100, blank=True, null=True)
    product_family = models.CharField(max_length=100, blank=True, null=True)
    direct_material_cost = models.CharField(max_length=30, blank=True, null=True)
    mva = models.CharField(max_length=30, blank=True, null=True)
    unit_price = models.CharField(max_length=30, blank=True, null=True)
    comments = models.CharField(max_length=300, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='Not Freezed')
    scenarioid = models.IntegerField(blank=True, null=True)
    npi_reportdate = models.CharField(max_length=20, blank=True, null=True)
    cq_demand = models.CharField(max_length=10, blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    animin = models.CharField(max_length=11, blank=True, null=True)
    npi_demands = models.CharField(max_length=20, blank=True, null=True)
    npi_notes = models.CharField(max_length=1000, blank=True, null=True)
    agile_notes = models.CharField(max_length=100, blank=True, null=True)
    refreshed_by = models.CharField(max_length=20, blank=True, null=True)
    prod_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    npi_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)
    refreshed_rev = models.CharField(max_length=30, blank=True, null=True)
    part_lifecycle = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.CharField(max_length=30, blank=True, null=True)
    refreshed_date = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'InputDB_top_bom_fgn'


class InputdbTopBomFgnHistory(models.Model):
    quarter = models.CharField(max_length=10, blank=True, null=True)
    oem_part_number = models.CharField(max_length=30, blank=True, null=True)
    oem_part_number_xx = models.CharField(max_length=30, blank=True, null=True)
    tla = models.CharField(db_column='TLA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    flexpn = models.CharField(db_column='FlexPN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rev = models.CharField(db_column='Rev', max_length=30, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    program_name = models.CharField(max_length=100, blank=True, null=True)
    product_family = models.CharField(max_length=100, blank=True, null=True)
    direct_material_cost = models.CharField(max_length=30, blank=True, null=True)
    mva = models.CharField(max_length=30, blank=True, null=True)
    unit_price = models.CharField(max_length=30, blank=True, null=True)
    comments = models.CharField(max_length=300, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    scenarioid = models.IntegerField(blank=True, null=True)
    npi_reportdate = models.CharField(max_length=20, blank=True, null=True)
    cq_demand = models.CharField(max_length=10, blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    animin = models.CharField(max_length=11, blank=True, null=True)
    npi_demands = models.CharField(max_length=20, blank=True, null=True)
    npi_notes = models.CharField(max_length=1000, blank=True, null=True)
    agile_notes = models.CharField(max_length=100, blank=True, null=True)
    refreshed_by = models.CharField(max_length=20, blank=True, null=True)
    prod_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    npi_refreshed_on = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)
    refreshed_rev = models.CharField(max_length=30, blank=True, null=True)
    part_lifecycle = models.CharField(max_length=100, blank=True, null=True)
    release_date = models.CharField(max_length=30, blank=True, null=True)
    refreshed_date = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'InputDB_top_bom_fgn_history'
