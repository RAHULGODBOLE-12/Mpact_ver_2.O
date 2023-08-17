# Generated by Django 4.1.1 on 2023-08-15 10:10

import Slate_CMT.templatetags.cmt_helper
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('portfolio', '0002_logger_portfolio'),
    ]

    operations = [
        migrations.CreateModel(
            name='RFX',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RFX_id', models.CharField(max_length=255, null=True, unique=True)),
                ('quarter', models.CharField(max_length=255, null=True)),
                ('sent_to', models.CharField(max_length=255, null=True)),
                ('Part_Number', models.CharField(max_length=255, null=True)),
                ('Mfr_Part_Number', models.CharField(max_length=255, null=True)),
                ('Mfr_Name', models.CharField(max_length=255, null=True)),
                ('cm', models.CharField(max_length=255, null=True)),
                ('Arista_pic_comment', models.CharField(max_length=255, null=True)),
                ('Item_Price', models.FloatField(null=True)),
                ('Lead_Time', models.IntegerField(null=True)),
                ('MOQ', models.IntegerField(null=True)),
                ('List', models.CharField(default=' ', max_length=255, null=True)),
                ('tarrif', models.CharField(default=' ', max_length=255, null=True)),
                ('COO', models.CharField(max_length=255, null=True)),
                ('Inco_Term', models.CharField(default='-', max_length=255, null=True)),
                ('MPQ', models.IntegerField(null=True)),
                ('Assembly_cost', models.FloatField(null=True)),
                ('Freight_cost', models.FloatField(null=True)),
                ('Masked_Price', models.FloatField(null=True)),
                ('Quote_Type', models.CharField(max_length=255, null=True)),
                ('Region', models.CharField(default='-', max_length=255, null=True)),
                ('Geo', models.CharField(default='-', max_length=255, null=True)),
                ('Life_Cycle', models.CharField(default='-', max_length=255, null=True)),
                ('Comments', models.TextField(default=' ', max_length=1000, null=True)),
                ('Quote_status', models.CharField(default='Non Quoted', max_length=255, null=True)),
                ('sent_quater', models.CharField(default=Slate_CMT.templatetags.cmt_helper.Current_quarter, max_length=255, null=True)),
                ('Quoted_by', models.CharField(max_length=255, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('quote_is_writable', models.BooleanField(default=True)),
                ('quote_freeze', models.BooleanField(default=False)),
                ('NCNR', models.CharField(default='-', max_length=255, null=True)),
                ('Team', models.CharField(max_length=255, null=True)),
                ('PO_Delivery', models.CharField(max_length=255, null=True)),
                ('soft_hard_tool', models.CharField(default='-', max_length=255, null=True)),
                ('suggested_split', models.FloatField(null=True)),
                ('manual_split', models.FloatField(null=True)),
                ('previous_split', models.FloatField(null=True)),
                ('split_type', models.CharField(max_length=255, null=True)),
                ('approval_flag', models.CharField(max_length=255, null=True)),
                ('approval_status_PIC', models.CharField(max_length=255, null=True)),
                ('approval_status_Manager', models.CharField(max_length=255, null=True)),
                ('approval_status_Director', models.CharField(max_length=255, null=True)),
                ('approval_status', models.CharField(max_length=255, null=True)),
                ('split_comments', models.TextField(null=True)),
                ('PIC_accept_reject_comments', models.TextField(null=True)),
                ('approval1_comments', models.TextField(null=True)),
                ('approval2_comments', models.TextField(null=True)),
                ('std_cost', models.FloatField(null=True)),
                ('CM_comments_on_Justifing_price', models.TextField(default=' ', null=True)),
                ('Supplier_Distributor_name_from_cm', models.TextField(null=True)),
                ('CM_Notes_on_Supplier', models.TextField(null=True)),
                ('CM_Manufacturer', models.TextField(null=True)),
                ('CM_mpn', models.TextField(null=True)),
                ('CM_buyer', models.TextField(null=True)),
                ('CM_qty_std_source', models.TextField(default=' ', null=True)),
                ('po_delivery', models.CharField(blank=True, max_length=255, null=True)),
                ('new_po_price', models.CharField(blank=True, max_length=255, null=True)),
                ('current_final_std_cost', models.CharField(blank=True, max_length=255, null=True)),
                ('current_updated_std_cost', models.CharField(blank=True, max_length=255, null=True)),
                ('current_qtr_decision', models.CharField(blank=True, max_length=255, null=True)),
                ('approve_reject_std_price', models.CharField(blank=True, max_length=255, null=True)),
                ('cm_approve_reject', models.CharField(blank=True, max_length=255, null=True)),
                ('arista_pic_approve_reject', models.CharField(blank=True, max_length=255, null=True)),
                ('bp_team_approve_reject', models.CharField(blank=True, max_length=255, null=True)),
                ('standard_price_q1', models.CharField(blank=True, max_length=255, null=True)),
                ('arista_pic_updated_data_name', models.CharField(blank=True, max_length=255, null=True)),
                ('cm_updated_data_name', models.CharField(blank=True, max_length=255, null=True)),
                ('due_date', models.DateField(null=True)),
                ('BP_team_Approve_Reject_Comments', models.TextField(null=True)),
                ('Arista_PIC_Comments_to_CM', models.TextField(null=True)),
                ('Arista_BP_Comments', models.TextField(null=True)),
                ('CM_Additional_Notes_on_Supplier_distributor', models.TextField(null=True)),
                ('CM_PO_Delivery_Remarks', models.TextField(null=True)),
                ('notified', models.BooleanField(default=False, null=True)),
                ('notified_status', models.CharField(max_length=255, null=True)),
                ('last_notified_on', models.DateTimeField(null=True)),
                ('Shareable', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('portfolio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='portfolio.portfolio')),
            ],
        ),
    ]
