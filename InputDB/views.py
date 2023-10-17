from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,Group
from django.http import HttpResponse, Http404
from portfolio.models import *
from InputDB.models import *
from django.http import JsonResponse,HttpResponse
from Slate_CMT.templatetags.cmt_helper import *
import re
from django.conf import settings
from io import BytesIO
import pandas as pd
from django.db.models import Q
from django_pandas.io import read_frame
import numpy as np
import openpyxl
import os
import csv
from django.db.models import Count
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
import mimetypes

# Create your views here.
def import_top_bom_gsm(request):
    path = "/home/iness/Desktop"
    os.chdir(path)
    data = pd.read_excel('Q320TopBomSGD.xlsx')
    row_iter = data.iterrows()
    objs = [
        InputdbTopBomGsm(
            oem_part_number=row['OEM Part Number'],
            oem_part_number_xx=row['OEM Part Number XX'],
            tla=row['TLA#'],
            sanminapn=row['SanminaPN'],
            rev=row['Rev'],
            description=row['Description'],
            program_name=row['Program Name'],
            product_family=row['Product Family'],
            #direct_material_cost=row['Direct Material Cost'],
            file_type="Base File",
            mva=row['MVA'],
            comments=row['Comments'],
            quarter="Q3-2020",
            #refreshed_by=request.user.id,
        )
        for index, row in row_iter
    ]
    InputdbTopBomGsm.objects.using('inputdb').bulk_create(objs)

    topbom = InputdbTopBomGsm.objects.using('inputdb').all()
    return render(request, "portfolio/topbom/topbom_gsm.html", context={'topbom': topbom})


def import_top_bom_cmm(request):
    path = "/home/iness/Desktop"
    os.chdir(path)
    data = pd.read_excel('JPE Top Bom_RFQ Q320.xlsx')
    row_iter = data.iterrows()
    objs = [
        InputdbTopBomCmm(
            family=row['Family'],
            #model=row['Model'],
            product_sku=row['Product SKU #'],
            assembly_sku=row['TLA Part Numbers'],
            amparts=row['TLA Part Numbers'].replace("ASASY","ASY"),
            tla_number=row['TLA'],
            tla_number_excld_rev=row['Arista Part Numbers'],
            assembly_description=row['Assembly Descriptions'],
            file_type="Base File",
            quarter="Q3-2020",
            #refreshed_by=request.user.id,
        )
        for index, row in row_iter
    ]
    InputdbTopBomCmm.objects.using('inputdb').bulk_create(objs)

    topbom = InputdbTopBomCmm.objects.using('inputdb').all()
    return render(request, "portfolio/topbom/topbom_cmm.html", context={'topbom': topbom})


def top_bom_quarterwise(request,team):
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    if team == "SGD":
        #.exclude(Q(cq_demand__in=[0,None]) & Q(animin=0))
        basefile=InputdbTopBomGsm.objects.using('inputdb').filter(file_type='Base File')
        prodfile = InputdbTopBomGsm.objects.using('inputdb').raw("SELECT *, (`cq_demand` + `animin`) as totaldemand  FROM `InputDB_top_bom_gsm` WHERE `notes` = 'Part Added'")
        npifile = InputdbTopBomGsm.objects.using('inputdb').filter(npi_notes='Part Added').exclude(npi_demands__isnull=True)
        #print(npifile)
        currentsscenarioid = basefile[0].scenarioid
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).exists():
            scedate = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).only('scenariodate')[:1].get()
            scedate=scedate.scenariodate
        else:
            scedate = None
        return render(request, "portfolio/topbom/components/prevqtr_topbom_sgd.html", context={'basefile': basefile, 'prodfile': prodfile, 'npifile':npifile,'scedate':scedate})
    elif team == "JPE":
        #.exclude(Q(animin=0) & Q(cq_demand__in=[0,None]))
        basefile=InputdbTopBomCmm.objects.using('inputdb').filter(file_type='Base File')
        prodfile = InputdbTopBomCmm.objects.using('inputdb').raw("SELECT *, (`cq_demand` + `animin`) as totaldemand  FROM `InputDB_top_bom_cmm` WHERE `notes` = 'Part Added'")
        npifile = InputdbTopBomCmm.objects.using('inputdb').filter(npi_notes='Part Added').exclude(npi_demands__isnull=True)
        #print(npifile)
        currentsscenarioid = basefile[0].scenarioid
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).exists():
            scedate = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).only('scenariodate')[:1].get()
            scedate=scedate.scenariodate
        else:
            scedate = None
        return render(request, "portfolio/topbom/components/prevqtr_topbom_jpe.html", context={'basefile': basefile, 'prodfile': prodfile, 'npifile':npifile,'scedate':scedate})
    elif team == "FGN":
        basefile=InputdbTopBomFgn.objects.using('inputdb').filter(file_type='Base File')
        prodfile = InputdbTopBomFgn.objects.using('inputdb').raw("SELECT *, (`cq_demand` + `animin`) as totaldemand  FROM `InputDB_top_bom_fgn` WHERE `notes` = 'Part Added'")
        npifile = InputdbTopBomFgn.objects.using('inputdb').filter(npi_notes='Part Added').exclude(npi_demands__isnull=True)
        currentsscenarioid = basefile[0].scenarioid
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).exists():
            scedate = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).only('scenariodate')[:1].get()
            scedate=scedate.scenariodate
        else:
            scedate = None
        return render(request, "portfolio/topbom/components/prevqtr_topbom_fgn.html", context={'basefile': basefile, 'prodfile': prodfile, 'npifile':npifile,'scedate':scedate})
@login_required
def top_bom(request,team):
    scenariodate=VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT `id`, `scenarioDate`,`forecastScenarioID` FROM `vw_fact_Latest_Production_forecast_iness` GROUP BY `scenarioDate` ORDER BY `vw_fact_Latest_Production_forecast_iness`.`scenarioDate`  DESC LIMIT 4")
    #print(scenariodate)
    reportdate=VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT `id`, `ReportDate` FROM `vw_fact_npiforecast_buildschedule_iness` GROUP BY `ReportDate` ORDER BY `vw_fact_npiforecast_buildschedule_iness`.`ReportDate`  DESC LIMIT 4")
    #print(reportdate)
    if team == 'SGD':
        if InputdbTopBomGsm.objects.using('inputdb').only('scenarioid','status').exists():
            currentsscenario = InputdbTopBomGsm.objects.using('inputdb').only('scenarioid','status')[:1].get()
            currentsscenarioid = currentsscenario.scenarioid
            status = currentsscenario.status
        else:
            currentsscenarioid = 0
            status = "None"
        prevqtrs=InputdbTopBomGsmHistory.objects.using('inputdb').raw("SELECT `id`, `quarter` FROM `InputDB_top_bom_gsm_history` GROUP BY `quarter` ORDER BY `InputDB_top_bom_gsm_history`.`quarter`  DESC LIMIT 8")
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).exists():
            CSdate = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).only('scenariodate')[:1].get()
            CSdate = CSdate.scenariodate
        else:
            CSdate = None
        eolparts = InputdbTopBomGsm.objects.using('inputdb').filter(part_lifecycle='EOL')
        return render(request, "portfolio/topbom/topbom_gsm.html", context={'scenariodate': scenariodate, 'CSdate': CSdate,'reportdate':reportdate,'status':status,'prevqtrs':prevqtrs,'eolparts':eolparts})
    elif team == 'JPE':
        if InputdbTopBomCmm.objects.using('inputdb').only('scenarioid','status').exists():
            currentsscenario = InputdbTopBomCmm.objects.using('inputdb').only('scenarioid','status')[:1].get()
            currentsscenarioid = currentsscenario.scenarioid
            status = currentsscenario.status
        else:
            currentsscenarioid = 0
            status = "None"
        prevqtrs=InputdbTopBomCmmHistory.objects.using('inputdb').raw("SELECT `id`, `quarter` FROM `InputDB_top_bom_cmm_history` GROUP BY `quarter` ORDER BY `InputDB_top_bom_cmm_history`.`quarter`  DESC LIMIT 8")
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).exists():
            CSdate = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).only('scenariodate')[:1].get()
            CSdate = CSdate.scenariodate
        else:
            CSdate = None
        eolparts = InputdbTopBomCmm.objects.using('inputdb').filter(part_lifecycle='EOL')
        return render(request, "portfolio/topbom/topbom_cmm.html", context={'scenariodate': scenariodate, 'CSdate': CSdate,'reportdate':reportdate,'status':status,'prevqtrs':prevqtrs,'eolparts':eolparts})
    elif team == 'FGN':
        if InputdbTopBomFgn.objects.using('inputdb').only('scenarioid','status').exists():
            currentsscenario = InputdbTopBomFgn.objects.using('inputdb').only('scenarioid','status')[:1].get()
            currentsscenarioid = currentsscenario.scenarioid
            status = currentsscenario.status
        else:
            currentsscenarioid = 0
            status = "None"
        prevqtrs=InputdbTopBomFgnHistory.objects.using('inputdb').raw("SELECT `id`, `quarter` FROM `InputDB_top_bom_fgn_history` GROUP BY `quarter` ORDER BY `InputDB_top_bom_fgn_history`.`quarter`  DESC LIMIT 8")
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).exists():
            CSdate = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(forecastscenarioid=currentsscenarioid).only('scenariodate')[:1].get()
            CSdate = CSdate.scenariodate
        else:
            CSdate = None
        eolparts = InputdbTopBomFgn.objects.using('inputdb').filter(part_lifecycle='EOL')
        return render(request, "portfolio/topbom/topbom_fgn.html", context={'scenariodate': scenariodate, 'CSdate': CSdate,'reportdate':reportdate,'status':status,'prevqtrs':prevqtrs,'eolparts':eolparts})
    
    else:
        return redirect('home')

def top_bom_refresh(request):
    scenarioid = request.POST.get('scenarioid')
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    prev_qtr = InputdbTopBomGsm.objects.using('inputdb').only('tla','oem_part_number','id')
    OEM = list(prev_qtr.values_list('oem_part_number', flat=True).distinct())
    TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
    for qtr in prev_qtr:
        print(qtr.tla)
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(aristapartnumber=qtr.oem_part_number).filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid).filter(name='SGD').exists():
            forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'SGD' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ qtr.oem_part_number +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
            for demand in forecastdemand:
                e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
                e.scenarioid = scenarioid
                e.cq_demand = demand.TotDemand
                e.animin = demand.backlog
                e.notes = 'No change & Demand updated'
                e.save(using='inputdb')
        else:
            e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
            e.scenarioid = scenarioid
            e.cq_demand = None
            e.notes = 'Part Unavailable'
            e.save(using='inputdb')
    print("Forecast No change & Demand updated")
    forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(name='SGD').exclude(aristapartnumber__in=OEM).exclude(aristapartnumber='TBD').filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid)
    demands=list(forecastdemand.values_list('aristapartnumber', flat=True).distinct())
    for demand in demands:
        print(demand)
        forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'SGD' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ demand +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
        for forecast in forecastdemand:
            if AmpartMfrRev.objects.using('inputdb').filter(ampart__icontains=demand).exists():
                Agile = AmpartMfrRev.objects.using('inputdb').filter(ampart__icontains=demand)[:1].get()
                topbom = InputdbTopBomGsm(
                        oem_part_number=demand,
                        oem_part_number_xx=str(demand)+'-XX',
                        sanminapn='LFARI'+demand,
                        rev=Agile.ampart_rev,
                        description=Agile.ampart_desc,
                        refreshed_by=request.user.id,
                        cq_demand = forecast.TotDemand,
                        animin = forecast.backlog,
                        notes="Part Added",
                    )
                topbom.save(using="inputdb")
            else:
                topbom = InputdbTopBomGsm(
                        oem_part_number=demand,
                        oem_part_number_xx=str(demand)+'-XX',
                        sanminapn='LFARI'+demand,
                        refreshed_by=request.user.id,
                        cq_demand = forecast.TotDemand,
                        animin = forecast.backlog,
                        notes="Part Added",
                    )
                topbom.save(using="inputdb")

    topbom = InputdbTopBomGsm.objects.using('inputdb').exclude(cq_demand='0').all()
    return render(request, "portfolio/topbom/components/prevqtr_topbom_sgd.html", context={'topbom': topbom})


def top_bom_refresh_fgn(request):
    scenarioid = request.POST.get('scenarioid')
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    prev_qtr = InputdbTopBomFgn.objects.using('inputdb').only('tla','oem_part_number','id')
    OEM = list(prev_qtr.values_list('oem_part_number', flat=True).distinct())
    TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
    for qtr in prev_qtr:
        print(qtr.tla)
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(aristapartnumber=qtr.oem_part_number).filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid).filter(name='FGN').exists():
            forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'FGN' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ qtr.oem_part_number +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
            for demand in forecastdemand:
                e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
                e.scenarioid = scenarioid
                e.cq_demand = demand.TotDemand
                e.animin = demand.backlog
                e.notes = 'No change & Demand updated'
                e.save(using='inputdb')
        else:
            e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
            e.scenarioid = scenarioid
            e.cq_demand = None
            e.notes = 'Part Unavailable'
            e.save(using='inputdb')
    print("Forecast No change & Demand updated")
    forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(name='FGN').exclude(aristapartnumber__in=OEM).exclude(aristapartnumber='TBD').filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid)
    demands=list(forecastdemand.values_list('aristapartnumber', flat=True).distinct())
    for demand in demands:
        print(demand)
        forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'FGN' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ demand +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
        for forecast in forecastdemand:
            if AmpartMfrRev.objects.using('inputdb').filter(ampart__icontains=demand).exists():
                Agile = AmpartMfrRev.objects.using('inputdb').filter(ampart__icontains=demand)[:1].get()
                topbom = InputdbTopBomFgn(
                        oem_part_number=demand,
                        oem_part_number_xx=str(demand)+'-XX',
                        flexpn='ARI-'+demand,
                        rev=Agile.ampart_rev,
                        description=Agile.ampart_desc,
                        refreshed_by=request.user.id,
                        cq_demand = forecast.TotDemand,
                        animin = forecast.backlog,
                        notes="Part Added",
                    )
                topbom.save(using="inputdb")
            else:
                topbom = InputdbTopBomFgn(
                        oem_part_number=demand,
                        oem_part_number_xx=str(demand)+'-XX',
                        flexpn='ARI-'+demand,
                        refreshed_by=request.user.id,
                        cq_demand = forecast.TotDemand,
                        animin = forecast.backlog,
                        notes="Part Added",
                    )
                topbom.save(using="inputdb")

    topbom = InputdbTopBomFgn.objects.using('inputdb').exclude(cq_demand='0').all()
    return render(request, "portfolio/topbom/components/prevqtr_topbom_fgn.html", context={'topbom': topbom})



def top_bom_refresh_jpe(request):
    scenarioid = request.POST.get('scenarioid')
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    prev_qtr = InputdbTopBomCmm.objects.using('inputdb').only('amparts','tla_number_excld_rev','id')
    OEM = list(prev_qtr.values_list('tla_number_excld_rev', flat=True).distinct())
    TLA = list(prev_qtr.values_list('amparts', flat=True).distinct())
    for qtr in prev_qtr:
        print(qtr.amparts)
        if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(aristapartnumber=qtr.tla_number_excld_rev).filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid).filter(name='JPE').exists():
            forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'JPE' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ qtr.tla_number_excld_rev +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
            for demand in forecastdemand:
                e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
                e.scenarioid = scenarioid
                e.cq_demand = demand.TotDemand
                e.animin = demand.backlog
                e.notes = 'No change & Demand updated'
                e.save(using='inputdb')
        else:
            e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
            e.scenarioid = scenarioid
            e.cq_demand = None
            e.notes = 'Part Unavailable'
            e.save(using='inputdb')
    print("Forecast No change & Demand updated")
    forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(name='SGD').exclude(aristapartnumber__in=OEM).exclude(aristapartnumber='TBD').filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid)
    demands=list(forecastdemand.values_list('aristapartnumber', flat=True).distinct())
    for demand in demands:
        print(demand)
        forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'JPE' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ demand +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
        for forecast in forecastdemand:
            if AmpartMfrRev.objects.using('inputdb').filter(ampart__icontains=demand).exists():
                Agile = AmpartMfrRev.objects.using('inputdb').filter(ampart__icontains=demand)[:1].get()
                topbom = InputdbTopBomCmm(
                    tla_number_excld_rev=demand,
                    tla_number=str(demand)+'-XX',
                    amparts=demand,
                    assembly_sku='AS'+demand,
                    rev=Agile.ampart_rev,
                    assembly_description=Agile.ampart_desc,
                    cq_demand = forecast.TotDemand,
                    animin = forecast.backlog,
                    refreshed_by=request.user.id,
                    notes="Part Added",
                )
                topbom.save(using="inputdb")
            else:
                topbom = InputdbTopBomCmm(
                    tla_number_excld_rev=demand,
                    tla_number=str(demand)+'-XX',
                    amparts=demand,
                    assembly_sku='AS'+demand,
                    cq_demand = forecast.TotDemand,
                    animin = forecast.backlog,
                    refreshed_by=request.user.id,
                    notes="Part Added",
                )
                topbom.save(using="inputdb")

    topbom = InputdbTopBomCmm.objects.using('inputdb').exclude(cq_demand='0').all()
    return render(request, "portfolio/topbom/components/prevqtr_topbom_sgd.html", context={'topbom': topbom})

def npi_refresh_sgd(request):
    reportid = request.POST.get('reportdate')
    reportdate=VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').get(id=reportid)
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    print(reportdate.reportdate)
    prev_qtr = InputdbTopBomGsm.objects.using('inputdb').only('tla','oem_part_number','id')
    TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
    for qtr in prev_qtr:
        print(qtr.tla)
        if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='SGD').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').filter(buykit=qtr.tla).filter(reportdate=reportdate.reportdate).exists():
            print('found for',qtr.tla)
            npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'SGD' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ qtr.tla +"'")
            for npidemand in npiforecast:
                e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
                e.npi_demands = npidemand.TotQty
                e.npi_notes = 'No change & Demand updated'
                e.npi_reportdate = reportdate.reportdate
                e.save(using='inputdb')
        else:
            e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
            e.npi_notes = 'Part Unavailable'
            e.npi_reportdate = reportdate.reportdate
            e.save(using='inputdb')
    print('demand updated')
    if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='SGD').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA).exists():
        npiforecast = VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='SGD').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA)
        npis = list(npiforecast.values_list('buykit', flat=True).distinct())
        for npi in npis:
            print(npi)
            npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'SGD' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ npi +"'")
            for npidemand in npiforecast:
                if AmpartMfrRev.objects.using('inputdb').filter(ampart=npi).exists():
                    Agile = AmpartMfrRev.objects.using('inputdb').filter(ampart=npi)[:1].get()
                    topbom = InputdbTopBomGsm(
                            oem_part_number=npi,
                            oem_part_number_xx=str(npi)+'-XX',
                            sanminapn='LFARI'+npi,
                            rev=Agile.ampart_rev,
                            description=Agile.ampart_desc,
                            npi_reportdate = str(reportdate.reportdate),
                            refreshed_by=request.user.id,
                            npi_demands = npidemand.TotQty,
                            npi_notes="Part Added",
                        )
                    topbom.save(using="inputdb")
                else:
                    topbom = InputdbTopBomGsm(
                            oem_part_number=npi,
                            oem_part_number_xx=str(npi)+'-XX',
                            sanminapn='LFARI'+npi,
                            npi_reportdate = str(reportdate.reportdate),
                            refreshed_by=request.user.id,
                            npi_demands = npidemand.TotQty,
                            npi_notes="Part Added",
                        )
                    topbom.save(using="inputdb")


    topbom = InputdbTopBomGsm.objects.using('inputdb').exclude(cq_demand='0').all()
    return render(request, "portfolio/topbom/components/prevqtr_topbom_sgd.html", context={'topbom': topbom})


def npi_refresh_fgn(request):
    reportid = request.POST.get('reportdate')
    reportdate=VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').get(id=reportid)
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    print(reportdate.reportdate)
    prev_qtr = InputdbTopBomFgn.objects.using('inputdb').only('tla','oem_part_number','id')
    TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
    for qtr in prev_qtr:
        print(qtr.tla)
        if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='SGD').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').filter(buykit=qtr.tla).filter(reportdate=reportdate.reportdate).exists():
            print('found for',qtr.tla)
            npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'SGD' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ qtr.tla +"'")
            for npidemand in npiforecast:
                e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
                e.npi_demands = npidemand.TotQty
                e.npi_notes = 'No change & Demand updated'
                e.npi_reportdate = reportdate.reportdate
                e.save(using='inputdb')
        else:
            e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
            e.npi_notes = 'Part Unavailable'
            e.npi_reportdate = reportdate.reportdate
            e.save(using='inputdb')
    print('demand updated')
    if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='FGN').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA).exists():
        npiforecast = VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='FGN').\
            filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).\
                filter(buykit__startswith='ARI-').exclude(buykit__in=TLA)
        npis = list(npiforecast.values_list('buykit', flat=True).distinct())
        for npi in npis:
            print(npi)
            npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'FGN' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ARI-%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ npi +"'")
            for npidemand in npiforecast:
                if AmpartMfrRev.objects.using('inputdb').filter(ampart=npi).exists():
                    Agile = AmpartMfrRev.objects.using('inputdb').filter(ampart=npi)[:1].get()
                    topbom = InputdbTopBomFgn(
                            oem_part_number=npi,
                            oem_part_number_xx=str(npi)+'-XX',
                            flexpn='ARI-'+npi,
                            rev=Agile.ampart_rev,
                            description=Agile.ampart_desc,
                            npi_reportdate = str(reportdate.reportdate),
                            refreshed_by=request.user.id,
                            npi_demands = npidemand.TotQty,
                            npi_notes="Part Added",
                        )
                    topbom.save(using="inputdb")
                else:
                    topbom = InputdbTopBomFgn(
                            oem_part_number=npi,
                            oem_part_number_xx=str(npi)+'-XX',
                            flexpn='ARI-'+npi,
                            npi_reportdate = str(reportdate.reportdate),
                            refreshed_by=request.user.id,
                            npi_demands = npidemand.TotQty,
                            npi_notes="Part Added",
                        )
                    topbom.save(using="inputdb")


    topbom = InputdbTopBomFgn.objects.using('inputdb').exclude(cq_demand='0').all()
    return render(request, "portfolio/topbom/components/prevqtr_topbom_fgn.html", context={'topbom': topbom})


def npi_refresh_jpe(request):
    reportid = request.POST.get('reportdate')
    reportdate=VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').get(id=reportid)
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    print(reportdate.reportdate)
    prev_qtr = InputdbTopBomCmm.objects.using('inputdb').only('amparts','tla_number_excld_rev','id')
    TLA = list(prev_qtr.values_list('amparts', flat=True).distinct())
    for qtr in prev_qtr:
        print(qtr.amparts)
        if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='JPE').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT', 'PPLT']).filter(buykit__startswith='ASY').filter(buykit=qtr.amparts).filter(reportdate=reportdate.reportdate).exists():
            print('found for',qtr.amparts)
            npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'JPE' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT', 'PPLT') AND `buykit` = '"+ qtr.amparts +"'")
            for npidemand in npiforecast:
                e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
                e.npi_demands = npidemand.TotQty
                e.npi_notes = 'No change & Demand updated'
                e.npi_reportdate = reportdate.reportdate
                e.save(using='inputdb')
        else:
            e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
            e.npi_notes = 'Part Unavailable'
            e.npi_reportdate = reportdate.reportdate
            e.save(using='inputdb')
    print('demand updated')
    if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='JPE').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT', 'PPLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA).exists():
        npiforecast = VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='JPE').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT', 'PPLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA)
        npis = list(npiforecast.values_list('buykit', flat=True).distinct())
        for npi in npis:
            print(npi)
            npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'JPE' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT', 'PPLT') AND `buykit` = '"+ npi +"'")
            for npidemand in npiforecast:
                if AmpartMfrRev.objects.using('inputdb').filter(ampart=npi).exists():
                    Agile = AmpartMfrRev.objects.using('inputdb').filter(ampart=npi)[:1].get()
                    topbom = InputdbTopBomCmm(
                            tla_number_excld_rev=npi,
                            tla_number=str(npi)+'-XX',
                            amparts=npi,
                            assembly_sku='AS'+npi,
                            rev=Agile.ampart_rev,
                            assembly_description=Agile.ampart_desc,
                            npi_reportdate = str(reportdate.reportdate),
                            npi_demands = npidemand.TotQty,
                            refreshed_by=request.user.id,
                            notes="Part Added",
                        )
                    topbom.save(using="inputdb")
                else:
                    topbom = InputdbTopBomCmm(
                            tla_number_excld_rev=npi,
                            tla_number=str(npi)+'-XX',
                            amparts=npi,
                            assembly_sku='AS'+npi,
                            npi_reportdate = str(reportdate.reportdate),
                            npi_demands = npidemand.TotQty,
                            refreshed_by=request.user.id,
                            notes="Part Added",
                        )
                    topbom.save(using="inputdb")


    topbom = InputdbTopBomCmm.objects.using('inputdb').exclude(cq_demand='0').all()
    return render(request, "portfolio/topbom/components/prevqtr_topbom_sgd.html", context={'topbom': topbom})


def delete_sgd_part(request,id):
    sgd = InputdbTopBomGsm.objects.using('inputdb').get(id=id)
    sgd.delete()
    return redirect('Top_BOM','SGD')

def delete_jpe_part(request,id):
    jpe = InputdbTopBomCmm.objects.using('inputdb').get(id=id)
    jpe.delete()
    return redirect('Top_BOM','JPE')

def delete_fgn_part(request,id):
    fgn = InputdbTopBomFgn.objects.using('inputdb').get(id=id)
    fgn.delete()
    return redirect('Top_BOM','FGN')

def compare_agile_sgd_basefile(request):

    topbomsgd=InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Base File")
    for topbom in topbomsgd:
        if topbom.tla == None:
            if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=topbom.oem_part_number).exists():
                partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT DISTINCT(`ampart_release_date`),`ID`,`AMPart`,`ampart_rev`,`ampart_lifecycle`,`ampart_description`, `ampart_release_date`, `updateddate`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ topbom.oem_part_number +"%%' ORDER BY `ampart_release_date`  DESC LIMIT 1")
                for part in partdata:
                    print(part.ampart)
                    e = InputdbTopBomGsm.objects.using('inputdb').get(id=topbom.id)
                    e.refreshed_rev = part.ampart_rev
                    e.release_date = part.ampart_release_date
                    e.refreshed_date = part.updateddate
                    e.part_lifecycle = part.ampart_lifecycle
                    e.description = part.ampart_description
                    if topbom.rev == part.ampart_rev:
                        e.agile_notes = 'No change in Rev'
                    else:
                        e.agile_notes = 'Rev Updated'
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomGsm.objects.using('inputdb').get(id=topbom.id)
                e.agile_notes = 'Part Unavailable'
                e.save(using='inputdb')
        else:
            if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=topbom.tla).exists():
                partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT DISTINCT(`ampart_release_date`),`ID`,`AMPart`,`ampart_rev`,`ampart_lifecycle`,`ampart_description`, `ampart_release_date`, `updateddate`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ topbom.tla +"' ORDER BY `ampart_release_date`  DESC LIMIT 1")
                for part in partdata:
                    print(part.ampart)
                    e = InputdbTopBomGsm.objects.using('inputdb').get(id=topbom.id)
                    e.refreshed_rev = part.ampart_rev
                    e.part_lifecycle = part.ampart_lifecycle
                    e.description = part.ampart_description
                    e.release_date = part.ampart_release_date
                    e.refreshed_date = part.updateddate
                    if topbom.rev == part.ampart_rev:
                        e.agile_notes = 'No change in Rev'
                    else:
                        e.agile_notes = 'Rev Updated'
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomGsm.objects.using('inputdb').get(id=topbom.id)
                e.agile_notes = 'Part Unavailable'
                e.save(using='inputdb')

    return redirect('Top_BOM_Qtr_Data','SGD')

def compare_agile_jpe_basefile(request):

    topbomsgd=InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Base File")
    for topbom in topbomsgd:
        if topbom.tla_number == None:
            if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=topbom.tla_number_excld_rev).exists():
                partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT DISTINCT(`ampart_release_date`),`ID`,`AMPart`,`ampart_rev`,`ampart_lifecycle`,`ampart_description`, `ampart_release_date`, `updateddate`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ topbom.tla_number_excld_rev +"%%' ORDER BY `ampart_release_date`  DESC LIMIT 1")
                for part in partdata:
                    print(part.ampart)
                    e = InputdbTopBomCmm.objects.using('inputdb').get(id=topbom.id)
                    e.refreshed_rev = part.ampart_rev
                    e.part_lifecycle = part.ampart_lifecycle
                    e.assembly_description = part.ampart_description
                    e.release_date = part.ampart_release_date
                    e.refreshed_date = part.updateddate
                    if topbom.rev == part.ampart_rev:
                        e.agile_notes = 'No change in Rev'
                    else:
                        e.agile_notes = 'Rev Updated'
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomCmm.objects.using('inputdb').get(id=topbom.id)
                e.agile_notes = 'Part Unavailable'
                e.save(using='inputdb')
        else:

            if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=topbom.tla_number).exists():
                partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT DISTINCT(`ampart_release_date`),`ID`,`AMPart`,`ampart_rev`,`ampart_lifecycle`,`ampart_description`, `ampart_release_date`, `updateddate`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ topbom.tla_number +"' ORDER BY `ampart_release_date`  DESC LIMIT 1")
                for part in partdata:
                    print(part.ampart)
                    e = InputdbTopBomCmm.objects.using('inputdb').get(id=topbom.id)
                    e.refreshed_rev = part.ampart_rev
                    e.part_lifecycle = part.ampart_lifecycle
                    e.assembly_description = part.ampart_description
                    e.release_date = part.ampart_release_date
                    e.refreshed_date = part.updateddate
                    if topbom.rev == part.ampart_rev:
                        e.agile_notes = 'No change in Rev'
                    else:
                        e.agile_notes = 'Rev Updated'
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomCmm.objects.using('inputdb').get(id=topbom.id)
                e.agile_notes = 'Part Unavailable'
                e.save(using='inputdb')

    return redirect('Top_BOM_Qtr_Data','JPE')


def compare_agile_fgn_basefile(request):

    topbomfgn=InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Base File")
    for topbom in topbomfgn:
        if topbom.tla == None:
            if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=topbom.oem_part_number).exists():
                partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT DISTINCT(`ampart_release_date`),`ID`,`AMPart`,`ampart_rev`,`ampart_lifecycle`,`ampart_description`, `ampart_release_date`, `updateddate`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ topbom.oem_part_number +"%%' ORDER BY `ampart_release_date`  DESC LIMIT 1")
                for part in partdata:
                    print(part.ampart)
                    e = InputdbTopBomFgn.objects.using('inputdb').get(id=topbom.id)
                    e.refreshed_rev = part.ampart_rev
                    e.release_date = part.ampart_release_date
                    e.refreshed_date = part.updateddate
                    e.part_lifecycle = part.ampart_lifecycle
                    e.description = part.ampart_description
                    if topbom.rev == part.ampart_rev:
                        e.agile_notes = 'No change in Rev'
                    else:
                        e.agile_notes = 'Rev Updated'
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomFgn.objects.using('inputdb').get(id=topbom.id)
                e.agile_notes = 'Part Unavailable'
                e.save(using='inputdb')
        else:
            if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=topbom.tla).exists():
                partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT DISTINCT(`ampart_release_date`),`ID`,`AMPart`,`ampart_rev`,`ampart_lifecycle`,`ampart_description`, `ampart_release_date`, `updateddate`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ topbom.tla +"' ORDER BY `ampart_release_date`  DESC LIMIT 1")
                for part in partdata:
                    print(part.ampart)
                    e = InputdbTopBomFgn.objects.using('inputdb').get(id=topbom.id)
                    e.refreshed_rev = part.ampart_rev
                    e.part_lifecycle = part.ampart_lifecycle
                    e.description = part.ampart_description
                    e.release_date = part.ampart_release_date
                    e.refreshed_date = part.updateddate
                    if topbom.rev == part.ampart_rev:
                        e.agile_notes = 'No change in Rev'
                    else:
                        e.agile_notes = 'Rev Updated'
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomFgn.objects.using('inputdb').get(id=topbom.id)
                e.agile_notes = 'Part Unavailable'
                e.save(using='inputdb')

    return redirect('Top_BOM_Qtr_Data','FGN')


def npischedule(request):
    path = "/home/iness/Desktop"
    os.chdir(path)
    data = pd.read_excel('npiforecast.xlsx')
    row_iter = data.iterrows()
    for index, row in row_iter:
        fact=VwFactNpiforecastBuildscheduleIness(
            id=row['id'],
            program=row['program'],
            build=row['build'],
            qty=row['qty'],
            config=row['config'],
            cmbuild=row['cmbuild'],
            buykit=row['buykit'],
            status=row['status'],
            cm=row['cm'],
            fabturnship=row['fabturnship'],
            pcbfabout=row['pcbfabout'],
            absrdue=row['absrdue'],
            buildstart=row['buildstart'],
            pcafirstoffandormechasystart=row['pcafirstoffandormechasystart'],
            buildfinish=row['buildfinish'],
            testrequirements=row['testrequirements'],
            buildnotes=row['buildnotes'],
            chipvers=row['chipvers'],
            materialsnotes=row['materialsnotes'],
            pm=row['pm'],
            hw=row['hw'],
            npieelec=row['npieelec'],
            diags=row['diags'],
            mechde=row['mechDe'],
            npiemech=row['npiemech'],
            scmm=row['scmm'],
            mfgtesteng=row['mfgTestEng'],
            family=row['family'],
            reportdate=row['ReportDate'],
        )
        fact.save(using="inputdb")
        print("1 row inserted",row['id'])

    return HttpResponse("Success")

def historical_data(request):
    files=request.FILES['SGD_file']
    data = pd.read_excel(files)
    print(data.columns)
    is_arista = data['controlBy'] == "Arista"
    is_sam = data['controlBy'] == "Sanmina"
    AristaParts = data[is_arista]
    SanminaParts = data[is_sam]
    row_iter = AristaParts.iterrows()
    for index, row in row_iter :
        supplier_name = row['arista_supplier_name']
        if str(supplier_name) != 'NaN' and str(supplier_name) != 'nan':
            suplierlist = re.split('/', str(row["arista_supplier_name"]))
            print(suplierlist)
            loop = 0
            for supplier in suplierlist:
                sup = re.split('\$', supplier)
                if row["arista_moq"] != 'NaN':
                    arista_moq = re.split('/', str(row["arista_moq"]))
                    if len(arista_moq) >= (loop + 1):
                        moq = arista_moq[loop]
                    else:
                        moq = ""
                else:
                    moq = ""

                if row["arista_lead_time"] != 'NaN':
                    arista_lead_time = re.split('/', str(row["arista_lead_time"]))
                    if len(arista_lead_time) >= (loop + 1):
                        leadtime = arista_lead_time[loop]
                    else:
                        leadtime = ""
                else:
                    leadtime = ""
                if (str(row["arista_supplier_mpn"]) != 'NaN' and str(row["arista_supplier_mpn"]) != 'nam'):
                    arista_mpn = re.split('/', str(row["arista_supplier_mpn"]))
                    if len(arista_mpn) >= (loop + 1):
                        mpn = arista_mpn[loop]
                    else:
                        mpn = ""
                else:
                    mpn = ""

                if (str(row["arista_st_ht"]) != 'NaN' and str(row["arista_st_ht"]) != 'nam'):
                    arista_lt_ht = re.split('/', str(row["arista_st_ht"]))
                    if len(arista_lt_ht) >= (loop + 1):
                        lt_ht = arista_lt_ht[loop]
                    else:
                        lt_ht = ""
                else:
                    lt_ht = ""

                if len(sup) > 1:
                    std_cost = re.split(' ', sup[1])
                    if len(std_cost) > 1:
                        sup_split = std_cost[1]
                    else:
                        sup_split = ""
                    std_cost_sup = std_cost[0]
                else:
                    std_cost_sup = ""
                    sup_split = ""

                loop = loop + 1
                sgd = InputdbSgdHistory(
                    cm_partno=row["cm_partno"],
                    arista_partno=row["arista_partno"],
                    consign_partno=row["consign_partno"],
                    controlby=row["controlBy"],
                    item_desc=row["item_desc"],
                    lt=row["LT"],
                    moq=row["MOQ"],
                    po_delivery=row["po_delivery"],
                    basedate="Q1-2021",
                    buffer_oh=row["buffer_oh"],
                    oh_plus_csinv=row["oh_plus_csinv"],
                    openpo_prev_qtr=row["openPO_prev_qtr"],
                    openpo_current_qtr=row["openPO_current_qtr"],
                    total_oh_delivery_based=row["total_oh_delivery_based"],
                    po_based_total_oh_opo=row["po_based_total_oh_opo"],
                    prev_qtr_demand=row["prev_qtr_demand"],
                    current_qtr_demand=row["current_qtr_demand"],
                    next_qtr_demand=row["next_qtr_demand"],
                    next_qtr_1_demand=row["next_qtr_1_demand"],
                    delta_op_opo=row["delta_op_opo"],
                    current_std_price=row["current_std_price"],
                    forecast_std_price=row["forecast_std_price"],
                    blended_avg_po_price=row["blended_avg_po_price"],
                    new_po_price=row["new_po_price"],
                    is_arista_recomented=row["is_arista_recomented"],
                    arista_std_price=row["arista_std_price"],
                    arista_supplier_name=row["arista_supplier_name"],
                    arista_sup_name=sup[0],
                    arista_sup_std_cost=std_cost_sup,
                    arista_sup_split=sup_split,
                    arista_moq=moq,
                    arista_lead_time=leadtime,
                    arista_supplier_mpn=mpn,
                    arista_ncnr=row["arista_ncnr"],
                    arista_st_ht=lt_ht,
                    arista_part_ownership=row["arista_part_ownership"],
                    arista_pic=row["arista_pic"],
                    sanmina_quoted_price=row["sanmina_quoted_price"],
                    sanmina_mfg=row["sanmina_mfg"],
                    sanmina_mpn=row["sanmina_mpn"],
                    sanmina_advise_moq=row["sanmina_advise_moq"],
                    sanmina_advise_lt=row["sanmina_advise_lt"],
                    sanmina_ncnr=row["sanmina_ncnr"],
                    sanmina_splits=row["sanmina_splits"],
                    sanmina_suppliers=row["sanmina_suppliers"],
                )
                sgd.save(using="inputdb")
                print('1 Arista row updated', sup[0])
        else:
            sgd = InputdbSgdHistory(
                cm_partno=row["cm_partno"],
                arista_partno=row["arista_partno"],
                consign_partno=row["consign_partno"],
                controlby=row["controlBy"],
                item_desc=row["item_desc"],
                lt=row["LT"],
                moq=row["MOQ"],
                po_delivery=row["po_delivery"],
                basedate="Q1-2021",
                buffer_oh=row["buffer_oh"],
                oh_plus_csinv=row["oh_plus_csinv"],
                openpo_prev_qtr=row["openPO_prev_qtr"],
                openpo_current_qtr=row["openPO_current_qtr"],
                total_oh_delivery_based=row["total_oh_delivery_based"],
                po_based_total_oh_opo=row["po_based_total_oh_opo"],
                prev_qtr_demand=row["prev_qtr_demand"],
                current_qtr_demand=row["current_qtr_demand"],
                next_qtr_demand=row["next_qtr_demand"],
                next_qtr_1_demand=row["next_qtr_1_demand"],
                delta_op_opo=row["delta_op_opo"],
                current_std_price=row["current_std_price"],
                forecast_std_price=row["forecast_std_price"],
                blended_avg_po_price=row["blended_avg_po_price"],
                new_po_price=row["new_po_price"],
                is_arista_recomented=row["is_arista_recomented"],
                arista_std_price=row["arista_std_price"],
                arista_supplier_name=row["arista_supplier_name"],
                arista_moq=row["arista_moq"],
                arista_lead_time=row["arista_lead_time"],
                arista_supplier_mpn=row["arista_supplier_mpn"],
                arista_ncnr=row["arista_ncnr"],
                arista_st_ht=row["arista_st_ht"],
                arista_part_ownership=row["arista_part_ownership"],
                arista_pic=row["arista_pic"],
                sanmina_quoted_price=row["sanmina_quoted_price"],
                sanmina_mfg=row["sanmina_mfg"],
                sanmina_mpn=row["sanmina_mpn"],
                sanmina_advise_moq=row["sanmina_advise_moq"],
                sanmina_advise_lt=row["sanmina_advise_lt"],
                sanmina_ncnr=row["sanmina_ncnr"],
                sanmina_splits=row["sanmina_splits"],
                sanmina_suppliers=row["sanmina_suppliers"],
            )
            sgd.save(using="inputdb")
            print('1 null row updated', row["arista_partno"])
    row_iter = SanminaParts.iterrows()
    for index, row in row_iter:
        supplier_name = row['sanmina_mfg']
        print(supplier_name)
        if str(supplier_name) != 'NaN' and str(supplier_name) != 'nan':
            suplierlist = re.split('/', str(row["sanmina_mfg"]))
            loop = 0
            for supplier in suplierlist:
                if row["sanmina_mpn"] != 'NaN':
                    san_mpn = re.split('/', str(row["sanmina_mpn"]))
                    if len(san_mpn) >= (loop + 1):
                        mpn = san_mpn[loop]
                    else:
                        mpn = ""
                else:
                    mpn = ""

                if row["sanmina_advise_moq"] != 'NaN':
                    san_moq = re.split('/', str(row["sanmina_advise_moq"]))
                    if len(san_moq) >= (loop + 1):
                        moq = san_moq[loop]
                    else:
                        moq = ""
                else:
                    moq = ""

                if row["sanmina_advise_lt"] != 'NaN':
                    san_lt = re.split('/', str(row["sanmina_advise_lt"]))
                    if len(san_lt) >= (loop + 1):
                        leadtime = san_lt[loop]
                    else:
                        leadtime = ""
                else:
                    leadtime = ""

                if row["sanmina_splits"] != 'NaN':
                    san_split = re.split('/', str(row["sanmina_splits"]))
                    if len(san_split) >= (loop + 1):
                        split = san_split[loop]
                    else:
                        split = ""
                else:
                    split = ""

                if row["sanmina_suppliers"] != 'NaN':
                    san_sup = re.split('/', str(row["sanmina_suppliers"]))
                    if len(san_sup) >= (loop + 1):
                        san_supplier = san_sup[loop]
                    else:
                        san_supplier = ""
                else:
                    san_supplier = ""
                loop = loop + 1
                sgd = InputdbSgdHistory(
                    cm_partno=row["cm_partno"],
                    arista_partno=row["arista_partno"],
                    consign_partno=row["consign_partno"],
                    controlby=row["controlBy"],
                    item_desc=row["item_desc"],
                    lt=row["LT"],
                    moq=row["MOQ"],
                    po_delivery=row["po_delivery"],
                    basedate="Q1-20210",
                    buffer_oh=row["buffer_oh"],
                    oh_plus_csinv=row["oh_plus_csinv"],
                    openpo_prev_qtr=row["openPO_prev_qtr"],
                    openpo_current_qtr=row["openPO_current_qtr"],
                    total_oh_delivery_based=row["total_oh_delivery_based"],
                    po_based_total_oh_opo=row["po_based_total_oh_opo"],
                    prev_qtr_demand=row["prev_qtr_demand"],
                    current_qtr_demand=row["current_qtr_demand"],
                    next_qtr_demand=row["next_qtr_demand"],
                    next_qtr_1_demand=row["next_qtr_1_demand"],
                    delta_op_opo=row["delta_op_opo"],
                    current_std_price=row["current_std_price"],
                    forecast_std_price=row["forecast_std_price"],
                    blended_avg_po_price=row["blended_avg_po_price"],
                    new_po_price=row["new_po_price"],
                    is_arista_recomented=row["is_arista_recomented"],
                    arista_std_price=row["arista_std_price"],
                    arista_supplier_name=row["arista_supplier_name"],
                    arista_moq=row["arista_moq"],
                    arista_lead_time=row["arista_lead_time"],
                    arista_supplier_mpn=row["arista_supplier_mpn"],
                    arista_ncnr=row["arista_ncnr"],
                    arista_st_ht=row["arista_st_ht"],
                    arista_part_ownership=row["arista_part_ownership"],
                    arista_pic=row["arista_pic"],
                    sanmina_quoted_price=row["sanmina_quoted_price"],
                    sanmina_mfg=supplier,
                    sanmina_mpn=mpn,
                    sanmina_advise_moq=moq,
                    sanmina_advise_lt=leadtime,
                    sanmina_ncnr=row["sanmina_ncnr"],
                    sanmina_splits=split,
                    sanmina_suppliers=san_supplier,
                )
                sgd.save(using="inputdb")
                print('1 Sanmina row updated', supplier)
        else:
            sgd = InputdbSgdHistory(
                cm_partno=row["cm_partno"],
                arista_partno=row["arista_partno"],
                consign_partno=row["consign_partno"],
                controlby=row["controlBy"],
                item_desc=row["item_desc"],
                lt=row["LT"],
                moq=row["MOQ"],
                po_delivery=row["po_delivery"],
                basedate="Q1-2021",
                buffer_oh=row["buffer_oh"],
                oh_plus_csinv=row["oh_plus_csinv"],
                openpo_prev_qtr=row["openPO_prev_qtr"],
                openpo_current_qtr=row["openPO_current_qtr"],
                total_oh_delivery_based=row["total_oh_delivery_based"],
                po_based_total_oh_opo=row["po_based_total_oh_opo"],
                prev_qtr_demand=row["prev_qtr_demand"],
                current_qtr_demand=row["current_qtr_demand"],
                next_qtr_demand=row["next_qtr_demand"],
                next_qtr_1_demand=row["next_qtr_1_demand"],
                delta_op_opo=row["delta_op_opo"],
                current_std_price=row["current_std_price"],
                forecast_std_price=row["forecast_std_price"],
                blended_avg_po_price=row["blended_avg_po_price"],
                new_po_price=row["new_po_price"],
                is_arista_recomented=row["is_arista_recomented"],
                arista_std_price=row["arista_std_price"],
                arista_supplier_name=row["arista_supplier_name"],
                arista_moq=row["arista_moq"],
                arista_lead_time=row["arista_lead_time"],
                arista_supplier_mpn=row["arista_supplier_mpn"],
                arista_ncnr=row["arista_ncnr"],
                arista_st_ht=row["arista_st_ht"],
                arista_part_ownership=row["arista_part_ownership"],
                arista_pic=row["arista_pic"],
                sanmina_quoted_price=row["sanmina_quoted_price"],
                sanmina_mfg=row["sanmina_mfg"],
                sanmina_mpn=row["sanmina_mpn"],
                sanmina_advise_moq=row["sanmina_advise_moq"],
                sanmina_advise_lt=row["sanmina_advise_lt"],
                sanmina_ncnr=row["sanmina_ncnr"],
                sanmina_splits=row["sanmina_splits"],
                sanmina_suppliers=row["sanmina_suppliers"],
            )
            sgd.save(using="inputdb")
            print('1 null row updated', row["arista_partno"])

    return HttpResponse("Success")


def top_bom_addpart_sgd(request):
    singleup = InputdbTopBomGsm(
        oem_part_number=request.POST.get('oem_part_number'),
        oem_part_number_xx=request.POST.get('oem_part_number_xx'),
        tla=request.POST.get('tla'),
        sanminapn=request.POST.get('sanminapn'),
        rev=request.POST.get('rev'),
        description=request.POST.get('description'),
        program_name=request.POST.get('program_name'),
        product_family=request.POST.get('product_family'),
        direct_material_cost=request.POST.get('direct_material_cost'),
        unit_price=request.POST.get('unit_price'),
        comments=request.POST.get('comments'),
        cq_demand=request.POST.get('cq_demand'),
        notes=request.POST.get('notes'),
        npi_notes=request.POST.get('npi_notes'),
    )
    singleup.save(using='inputdb')
    return redirect('Top_BOM', 'SGD')


def top_bom_addpart_jpe(request):
    singleupload = InputdbTopBomCmm(
        family=request.POST.get('family'),
        model=request.POST.get('model'),
        product_sku=request.POST.get('product_sku'),
        assembly_sku=request.POST.get('assembly_sku'),
        tla_number=request.POST.get('tla_number'),
        tla_number_excld_rev=request.POST.get('tla_number_excld_rev'),
        assembly_description=request.POST.get('assembly_description'),
        animin=request.POST.get('animin'),
        cq_demand=request.POST.get('cq_demand'),
        notes=request.POST.get('notes'),
        npi_notes=request.POST.get('npi_notes'),
    )
    singleupload.save(using='inputdb')
    return redirect('Top_BOM', 'JPE')



def top_bom_addpart_fgn(request):
    singleup = InputdbTopBomFgn(
        oem_part_number=request.POST.get('oem_part_number'),
        oem_part_number_xx=request.POST.get('oem_part_number_xx'),
        tla=request.POST.get('tla'),
        flexpn=request.POST.get('flexpn'),
        rev=request.POST.get('rev'),
        description=request.POST.get('description'),
        program_name=request.POST.get('program_name'),
        product_family=request.POST.get('product_family'),
        direct_material_cost=request.POST.get('direct_material_cost'),
        unit_price=request.POST.get('unit_price'),
        comments=request.POST.get('comments'),
        cq_demand=request.POST.get('cq_demand'),
        notes=request.POST.get('notes'),
        npi_notes=request.POST.get('npi_notes'),
    )
    singleup.save(using='inputdb')
    return redirect('Top_BOM', 'FGN')





def bulkupload_sgd(request):
    if request.method=="POST":
        model=Portfolio
        xlx=request.FILES['Upload_Excel']
        data=pd.read_excel(xlx)
        row_iter = data.iterrows()
        objs = [
			InputdbTopBomGsm(
				oem_part_number=row['OEM Part Number'],
				oem_part_number_xx=row['OEM Part Number XX'],
				tla=row['TLA'],
				sanminapn=row['SanminaPN'],
				rev=row['REV'],
				#refreshed_rev=row['Refreshed REV'],
				#part_lifecycle=row['Lifecycle'],
				description=row['Description'],
				program_name=row['Program Name'],
				product_family=row['Product Family'],
				mva=row['MVA'],
				comments=row['Comments'],
				#animin= row['ANI Min'],
				#cq_demand =row['Prod. Forecast Demand'],
    			#scenarioid=row['Prod. Forecast Scenario Date'],
				#npi_reportdate=row['NPI Forecast Report Date'],
				#npi_demands=row['NPI Demand Qty.'],
				#notes =row['Production Forecaste Notes'],
    			#npi_notes =row['NPI Forecaste Note'],
				#agile_notes =row['Agile Notes'],
			)
			for index, row in row_iter
		]
        InputdbTopBomGsm.objects.using('inputdb').bulk_create(objs)
        topbom = InputdbTopBomGsm.objects.using('inputdb').all()
    return redirect('Top_BOM', 'SGD')

def bulkupload_jpe(request):
    if request.method=="POST":
        model=Portfolio
        xlx=request.FILES['Upload_Excel']
        data=pd.read_excel(xlx)
        row_iter = data.iterrows()
        objs = [
            InputdbTopBomCmm(
                family=row['Family'],
                model=row['Model'],
                product_sku=row['Product SKU'],
                assembly_sku=row['Assembly SKU'],
                tla_number=row['TLA Number'],
                tla_number_excld_rev=row['TLA Number(excld revised)'],
                assembly_description=row['Assembly Description'],
                #animin=row['ANI Min'],
                #cq_demand=row['Prod. Forecast Demand'],
                #scenarioid=row['Prod. Forecast Scenario Date'],
                #npi_reportdate=row['NPI Forecast Report Date'],
                #npi_demands=row['NPI Demand Qty.'],
                #notes=row['Production Forecast Notes'],
                #npi_notes=row['NPI Forecast Note'],
                #agile_notes =row['Agile Notes'],
            )
            for index, row in row_iter
        ]
        InputdbTopBomCmm.objects.using('inputdb').bulk_create(objs)
        topbom = InputdbTopBomCmm.objects.using('inputdb').all()
        print('uploaded')
    return redirect('Top_BOM', 'JPE')

def bulkupload_fgn(request):
    if request.method == "POST":
        model=Portfolio
        xlx=request.FILES['Upload_Excel']
        data=pd.read_excel(xlx)
        row_iter = data.iterrows()
        objs = [
			InputdbTopBomFgn(
				oem_part_number=row['OEM Part Number'],
				oem_part_number_xx=row['OEM Part Number XX'],
				tla=row['TLA#'],
				flexpn=row['Flex PN'],
				rev=row['Rev'],
				#refreshed_rev=row['Refreshed REV'],
				#part_lifecycle=row['Lifecycle'],
				description=row['Description'],
				program_name=row['Program Name'],
				product_family=row['Product Family'],
				mva=row['MVA '],
				comments=row['Comments'],
				
			)
			for index, row in row_iter
		]
        InputdbTopBomFgn.objects.using('inputdb').bulk_create(objs)
        topbom = InputdbTopBomFgn.objects.using('inputdb').all()
    return redirect('Top_BOM', 'FGN')

def new_basefile_sgd(request):
    if request.method=="POST":
        currentqtr=Current_quarter()
        InputdbTopBomGsmHistory.objects.using('inputdb').filter(quarter=currentqtr).delete()
        update = InputdbTopBomGsm.objects.using('inputdb').all()
        print(update)
        InputdbTopBomGsmHistory.objects.using('inputdb').bulk_create(update)
        xlx=request.FILES['Upload_Excel']
        data=pd.read_excel(xlx)
        data.dropna(subset=[
        'OEM Part Number',
        'OEM Part Number XX',
        'TLA',
        'SanminaPN',
        ],inplace=True,how='all')
        row_iter = data.iterrows()
        objs = [
			InputdbTopBomGsm(
				oem_part_number=row['OEM Part Number'],
				oem_part_number_xx=row['OEM Part Number XX'],
				tla=row['TLA'],
				sanminapn=row['SanminaPN'],
				rev=row['Rev'],
				description=row['Description'],
				program_name=row['Program Name'],
				product_family=row['Product Family'],
				mva=row['MVA'],
				comments=row['Comments'],
                file_type = "Base File"
			)
			for index, row in row_iter
		]

        InputdbTopBomGsm.objects.using('inputdb').filter(quarter=currentqtr).delete()
        InputdbTopBomGsm.objects.using('inputdb').bulk_create(objs)
        topbom = InputdbTopBomGsm.objects.using('inputdb').all()
    return redirect('Top_BOM', 'SGD')

def new_basefile_jpe(request):
    if request.method=="POST":
        currentqtr=Current_quarter()
        InputdbTopBomCmmHistory.objects.using('inputdb').filter(quarter=currentqtr).delete()
        update = InputdbTopBomCmm.objects.using('inputdb').all()
        print(update)
        InputdbTopBomCmmHistory.objects.using('inputdb').bulk_create(update)
        xlx=request.FILES['Upload_Excel']
        data=pd.read_excel(xlx)
        data.dropna(subset=[
        'TLA Part Numbers',
        'Arista Part Numbers',
        'Arista Part Numbers (excld revised)',
        'Assembly Description',],inplace=True,how='all')
        row_iter = data.iterrows()

        objs = [
			InputdbTopBomCmm(
				family=row['Family'],
                #model=row['Model'],
                rev=row['Rev'],
                product_sku=row['Product SKU'],
                assembly_sku=row['TLA Part Numbers'],
                amparts=row['TLA Part Numbers'].replace("ASASY","ASY"),
                tla_number=row['Arista Part Numbers'],
                tla_number_excld_rev=row['Arista Part Numbers (excld revised)'],
                assembly_description=row['Assembly Description'],
                file_type = "Base File"
			)
			for index, row in row_iter
		]

        InputdbTopBomCmm.objects.using('inputdb').filter(quarter=currentqtr).delete()
        InputdbTopBomCmm.objects.using('inputdb').bulk_create(objs)
        topbom = InputdbTopBomCmm.objects.using('inputdb').all()
    return redirect('Top_BOM', 'JPE')



def new_basefile_fgn(request):
    if request.method=="POST":
        currentqtr=Current_quarter()
        InputdbTopBomFgnHistory.objects.using('inputdb').filter(quarter=currentqtr).delete()
        update = InputdbTopBomFgn.objects.using('inputdb').all()
        print(update)
        InputdbTopBomFgnHistory.objects.using('inputdb').bulk_create(update)
        xlx=request.FILES['Upload_Excel']
        data=pd.read_excel(xlx)
        data.dropna(subset=[
        'OEM Part Number',
        'OEM Part Number XX',
        'TLA#',
        'Flex PN',
        ],inplace=True,how='all')
        row_iter = data.iterrows()
        objs = [
			InputdbTopBomFgn(
				oem_part_number=row['OEM Part Number'],
				oem_part_number_xx=row['OEM Part Number XX'],
				tla=row['TLA#'],
				flexpn=row['Flex PN'],
				rev=row['Rev'],
				description=row['Description'],
				program_name=row['Program Name'],
				product_family=row['Product Family'],
				mva=row['MVA '],
				comments=row['Comments'],
                file_type = "Base File"
			)
			for index, row in row_iter
		]

        InputdbTopBomFgn.objects.using('inputdb').filter(quarter=currentqtr).delete()
        InputdbTopBomFgn.objects.using('inputdb').bulk_create(objs)
        topbom = InputdbTopBomFgn.objects.using('inputdb').all()
    return redirect('Top_BOM', 'FGN')



def refresh_base_file_prod_forecast(request,team):
    scenarioid = request.POST.get('scenarioid')
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    print('top bom qtr',request.POST.get('quarter'))
    print(start_end[0])
    print(start_end[1])
    if team == 'SGD':
        prev_qtr = InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        if InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Production Forecast Part").exists():
            InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Production Forecast Part").delete()
        OEM = list(prev_qtr.values_list('oem_part_number', flat=True).distinct())
        TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
        for qtr in prev_qtr:
            print(qtr.tla)
            if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(aristapartnumber=qtr.oem_part_number).filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid).filter(name='SGD').exists():
                forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'SGD' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ qtr.oem_part_number +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
                for demand in forecastdemand:
                    e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
                    e.scenarioid = scenarioid
                    e.cq_demand = demand.TotDemand
                    e.animin = demand.backlog
                    e.notes = 'No change & Demand updated'
                    e.refreshed_by = request.user.id
                    e.prod_refreshed_on = datetime.datetime.now()
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
                e.scenarioid = scenarioid
                e.cq_demand = None
                e.refreshed_by = request.user.id
                e.prod_refreshed_on = datetime.datetime.now()
                e.notes = 'Part Unavailable'
                e.save(using='inputdb')
        print("Forecast No change & Demand updated")
        return redirect('Top_BOM_Qtr_Data','SGD')
    elif team == 'JPE':
        prev_qtr = InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Base File").only('amparts','tla_number_excld_rev','id')
        if InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Production Forecast Part").exists():
            InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Production Forecast Part").delete()
        OEM = list(prev_qtr.values_list('tla_number_excld_rev', flat=True).distinct())
        TLA = list(prev_qtr.values_list('amparts', flat=True).distinct())
        for qtr in prev_qtr:
            print(qtr.amparts)
            if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(aristapartnumber=qtr.tla_number_excld_rev).filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid).filter(name='JPE').exists():
                forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'JPE' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ qtr.tla_number_excld_rev +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
                for demand in forecastdemand:
                    e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
                    e.scenarioid = scenarioid
                    e.cq_demand = demand.TotDemand
                    e.animin = demand.backlog
                    e.refreshed_by = request.user.id
                    e.prod_refreshed_on = datetime.datetime.now()
                    e.notes = 'No change & Demand updated'
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
                e.scenarioid = scenarioid
                e.cq_demand = None
                e.refreshed_by = request.user.id
                e.prod_refreshed_on = datetime.datetime.now()
                e.notes = 'Part Unavailable'
                e.save(using='inputdb')
        print("Forecast No change & Demand updated")
        return redirect('Top_BOM_Qtr_Data','JPE')
    elif team == 'FGN':
        prev_qtr = InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        if InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Production Forecast Part").exists():
            InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Production Forecast Part").delete()
        OEM = list(prev_qtr.values_list('oem_part_number', flat=True).distinct())
        TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
        for qtr in prev_qtr:
            print(qtr.tla)
            if VwFactLatestProductionForecastIness.objects.using('inputdb').filter(aristapartnumber=qtr.oem_part_number).filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid).filter(name='SGD').exists():
                forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'SGD' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ qtr.oem_part_number +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
                for demand in forecastdemand:
                    e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
                    e.scenarioid = scenarioid
                    e.cq_demand = demand.TotDemand
                    e.animin = demand.backlog
                    e.notes = 'No change & Demand updated'
                    e.refreshed_by = request.user.id
                    e.prod_refreshed_on = datetime.datetime.now()
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
                e.scenarioid = scenarioid
                e.cq_demand = None
                e.refreshed_by = request.user.id
                e.prod_refreshed_on = datetime.datetime.now()
                e.notes = 'Part Unavailable'
                e.save(using='inputdb')
        print("Forecast No change & Demand updated")
        return redirect('Top_BOM_Qtr_Data','FGN')
    

def refresh_base_file_npi_forecast(request,team):
    reportid = request.POST.get('reportdate')
    reportdate=VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').get(id=reportid)
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    if team == "JPE":
        prev_qtr = InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Base File").only('amparts','tla_number_excld_rev','id')
        TLA = list(prev_qtr.values_list('amparts', flat=True).distinct())
        for qtr in prev_qtr:
            print(qtr.amparts)
            if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='JPE').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT', 'PPLT']).filter(buykit__startswith='ASY').filter(buykit=qtr.amparts).filter(reportdate=reportdate.reportdate).exists():
                print('found for',qtr.amparts)
                npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'JPE' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT', 'PPLT') AND `buykit` = '"+ qtr.amparts +"'")
                for npidemand in npiforecast:
                    e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
                    e.npi_demands = npidemand.TotQty
                    e.npi_notes = 'No change & Demand updated'
                    e.refreshed_by = request.user.id
                    e.npi_refreshed_on = datetime.datetime.now()
                    e.npi_reportdate = reportdate.reportdate
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomCmm.objects.using('inputdb').get(id=qtr.id)
                e.npi_notes = 'Part Unavailable'
                e.refreshed_by = request.user.id
                e.npi_refreshed_on = datetime.datetime.now()
                e.npi_reportdate = reportdate.reportdate
                e.save(using='inputdb')
        print('demand updated')

        return redirect('Top_BOM_Qtr_Data','JPE')

    elif team == 'SGD':
        prev_qtr = InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
        for qtr in prev_qtr:
            print(qtr.tla)
            if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='SGD').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').filter(buykit=qtr.tla).filter(reportdate=reportdate.reportdate).exists():
                print('found for',qtr.tla)
                npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'SGD' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ qtr.tla +"'")
                for npidemand in npiforecast:
                    e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
                    e.npi_demands = npidemand.TotQty
                    e.npi_notes = 'No change & Demand updated'
                    e.refreshed_by = request.user.id
                    e.npi_refreshed_on = datetime.datetime.now()
                    e.npi_reportdate = reportdate.reportdate
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomGsm.objects.using('inputdb').get(id=qtr.id)
                e.npi_notes = 'Part Unavailable'
                e.refreshed_by = request.user.id
                e.npi_refreshed_on = datetime.datetime.now()
                e.npi_reportdate = reportdate.reportdate
                e.save(using='inputdb')
        print('demand updated')

        return redirect('Top_BOM_Qtr_Data','SGD')
    
    elif team == 'FGN':
        prev_qtr = InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
        for qtr in prev_qtr:
            print(qtr.tla)
            if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='FGN').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').filter(buykit=qtr.tla).filter(reportdate=reportdate.reportdate).exists():
                print('found for',qtr.tla)
                npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'FGN' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ qtr.tla +"'")
                for npidemand in npiforecast:
                    e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
                    e.npi_demands = npidemand.TotQty
                    e.npi_notes = 'No change & Demand updated'
                    e.refreshed_by = request.user.id
                    e.npi_refreshed_on = datetime.datetime.now()
                    e.npi_reportdate = reportdate.reportdate
                    e.save(using='inputdb')
            else:
                e = InputdbTopBomFgn.objects.using('inputdb').get(id=qtr.id)
                e.npi_notes = 'Part Unavailable'
                e.refreshed_by = request.user.id
                e.npi_refreshed_on = datetime.datetime.now()
                e.npi_reportdate = reportdate.reportdate
                e.save(using='inputdb')
        print('demand updated')

        return redirect('Top_BOM_Qtr_Data','FGN')




def add_parts_production(request,team):
    scenarioid = request.POST.get('scenarioid')
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    print(start_end[0])
    print(start_end[1])
    if team == 'SGD':
        prev_qtr = InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        OEM = list(prev_qtr.values_list('oem_part_number', flat=True).distinct())
        if InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Production Forecast Part").exists():
            InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Production Forecast Part").delete()
        forecastdata = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(name='SGD').exclude(aristapartnumber__in=OEM).exclude(aristapartnumber='TBD').filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid)
        forecast = list(forecastdata.values_list('aristapartnumber', flat=True).distinct())
        for parts in forecast:
            print(parts)
            forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'SGD' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ parts +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
            for demand in forecastdemand:
                if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Production").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Production' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Prototype").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Prototype' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Preliminary").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Preliminary' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="EOL").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'EOL' GROUP BY `ampart_release_date`,`AMPart`,`ampart_rev` ORDER BY `ID`  DESC LIMIT 1")
                else:
                    partdata = None
                if not partdata == None:
                    for data in partdata:
                        print(data.ampart)
                        topbom = InputdbTopBomGsm(
                            oem_part_number=parts,
                            oem_part_number_xx=str(parts)+'-XX',
                            sanminapn='LFARI'+parts,
                            tla=data.ampart,
                            rev=data.ampart_rev,
                            description=data.ampart_description,
                            part_lifecycle=data.ampart_lifecycle,
                            refreshed_by=request.user.id,
                            cq_demand = demand.TotDemand,
                            animin = demand.backlog,
                            scenarioid=scenarioid,
                            notes="Part Added",
                            file_type="Production Forecast Part",
                        )
                        topbom.save(using="inputdb")
                else:
                    print('not found in agile')
                    topbom = InputdbTopBomGsm(
                        oem_part_number=parts,
                        oem_part_number_xx=str(parts)+'-XX',
                        sanminapn='LFARI'+parts,
                        tla=parts,
                        refreshed_by=request.user.id,
                        cq_demand = demand.TotDemand,
                        animin = demand.backlog,
                        scenarioid=scenarioid,
                        notes="Part Added",
                        file_type="Production Forecast Part",
                    )
                    topbom.save(using="inputdb")

        return redirect('Top_BOM_Qtr_Data','SGD')

    elif team == 'JPE':
        prev_qtr = InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Base File").only('amparts','tla_number_excld_rev','id')
        OEM = list(prev_qtr.values_list('tla_number_excld_rev', flat=True).distinct())
        #print(OEM)
        if InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Production Forecast Part").exists():
            InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Production Forecast Part").delete()
        forecastdata = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(name='JPE').exclude(aristapartnumber__in=OEM).exclude(aristapartnumber='TBD').filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid)
        forecast = list(forecastdata.values_list('aristapartnumber', flat=True).distinct())
        for parts in forecast:
            print(parts)
            forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'JPE' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ parts +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
            for demand in forecastdemand:
                if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Production").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Production' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Prototype").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Prototype' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Preliminary").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Preliminary' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="EOL").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'EOL' GROUP BY `ampart_release_date`,`AMPart`,`ampart_rev` ORDER BY `ID`  DESC LIMIT 1")
                else:
                    partdata = None
                if not partdata == None:
                    for data in partdata:
                        print(data.ampart)
                        topbom = InputdbTopBomCmm(
                            tla_number_excld_rev=parts,
                            tla_number=str(parts)+'-XX',
                            assembly_sku='AS'+parts,
                            amparts=data.ampart,
                            rev=data.ampart_rev,
                            assembly_description=data.ampart_description,
                            part_lifecycle=data.ampart_lifecycle,
                            refreshed_by=request.user.id,
                            cq_demand = demand.TotDemand,
                            animin = demand.backlog,
                            scenarioid=scenarioid,
                            notes="Part Added",
                            file_type="Production Forecast Part",
                        )
                        topbom.save(using="inputdb")
                else:
                    print('not found in agile')
                    topbom = InputdbTopBomCmm(
                        tla_number_excld_rev=parts,
                        tla_number=str(parts)+'-XX',
                        assembly_sku='AS'+parts,
                        amparts=parts,
                        refreshed_by=request.user.id,
                        cq_demand = demand.TotDemand,
                        animin = demand.backlog,
                        scenarioid=scenarioid,
                        notes="Part Added",
                        file_type="Production Forecast Part",
                    )
                    topbom.save(using="inputdb")

        return redirect('Top_BOM_Qtr_Data','JPE')
    elif team == 'FGN':
        prev_qtr = InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        OEM = list(prev_qtr.values_list('oem_part_number', flat=True).distinct())
        if InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Production Forecast Part").exists():
            InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Production Forecast Part").delete()
        forecastdata = VwFactLatestProductionForecastIness.objects.using('inputdb').filter(name='FGN').exclude(aristapartnumber__in=OEM).exclude(aristapartnumber='TBD').filter(caldate__range=[start_end[0], start_end[1]]).filter(forecastscenarioid=scenarioid)
        forecast = list(forecastdata.values_list('aristapartnumber', flat=True).distinct())
        for parts in forecast:
            print(parts)
            forecastdemand = VwFactLatestProductionForecastIness.objects.using('inputdb').raw("SELECT *, SUM(`ForecastQty`) as TotDemand FROM `vw_fact_Latest_Production_forecast_iness` WHERE `name` = 'FGN' AND `forecastScenarioID` = '"+ scenarioid +"' AND `aristaPartNumber` = '"+ parts +"' AND `calDate` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"'")
            for demand in forecastdemand:
                if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Production").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Production' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Prototype").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Prototype' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="Preliminary").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'Preliminary' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=parts).filter(ampart_lifecycle="EOL").exists():
                    partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` LIKE '"+ parts +"%%' AND `ampart_lifecycle` = 'EOL' GROUP BY `ampart_release_date`,`AMPart`,`ampart_rev` ORDER BY `ID`  DESC LIMIT 1")
                else:
                    partdata = None
                if not partdata == None:
                    for data in partdata:
                        print(data.ampart)
                        topbom = InputdbTopBomFgn(
                            oem_part_number=parts,
                            oem_part_number_xx=str(parts)+'-XX',
                            flexpn='ARI-'+parts,
                            tla=data.ampart,
                            rev=data.ampart_rev,
                            description=data.ampart_description,
                            part_lifecycle=data.ampart_lifecycle,
                            refreshed_by=request.user.id,
                            cq_demand = demand.TotDemand,
                            animin = demand.backlog,
                            scenarioid=scenarioid,
                            notes="Part Added",
                            file_type="Production Forecast Part",
                        )
                        topbom.save(using="inputdb")
                else:
                    print('not found in agile')
                    topbom = InputdbTopBomFgn(
                        oem_part_number=parts,
                        oem_part_number_xx=str(parts)+'-XX',
                        flexpn='ARI-'+parts,
                        tla=parts,
                        refreshed_by=request.user.id,
                        cq_demand = demand.TotDemand,
                        animin = demand.backlog,
                        scenarioid=scenarioid,
                        notes="Part Added",
                        file_type="Production Forecast Part",
                    )
                    topbom.save(using="inputdb")

        return redirect('Top_BOM_Qtr_Data','FGN')

   

def add_parts_npi(request,team):
    print('NPI Forecast Parts adding')
    reportid = request.POST.get('reportdate')
    reportdate=VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').get(id=reportid)
    start_end = qtr_start_end_manual(request.POST.get('quarter'))
    if team == 'JPE':
        prev_qtr = InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Base File").only('amparts','tla_number_excld_rev','id')
        if InputdbTopBomCmm.objects.using('inputdb').filter(file_type="NPI Forecast Part").exists():
            InputdbTopBomCmm.objects.using('inputdb').filter(file_type="NPI Forecast Part").delete()
        TLA = list(prev_qtr.values_list('amparts', flat=True).distinct())
        if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='JPE').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT', 'PPLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA).exists():
            npiforecast = VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='JPE').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT', 'PPLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA)
            npis = list(npiforecast.values_list('buykit', flat=True).distinct())
            for npi in npis:
                print(npi)
                npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'JPE' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT', 'PPLT') AND `buykit` = '"+ npi +"'")
                for npidemand in npiforecast:
                    if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Production").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Production' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Prototype").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Prototype' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Preliminary").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Preliminary' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="EOL").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'EOL' GROUP BY `ampart_release_date`,`AMPart`,`ampart_rev` ORDER BY `ID`  DESC LIMIT 1")
                    else:
                        partdata = None
                    if not partdata == None:
                        for data in partdata:
                            print(data.ampart)
                            res = npi.rsplit('-', 1)
                            topbom = InputdbTopBomCmm(
                                tla_number_excld_rev=res[0],
                                tla_number=data.ampart,
                                assembly_sku='AS'+res[0],
                                amparts=str(res[0])+'-XX',
                                rev=data.ampart_rev,
                                assembly_description=data.ampart_description,
                                part_lifecycle=data.ampart_lifecycle,
                                refreshed_by=request.user.id,
                                npi_demands = npidemand.TotQty,
                                npi_reportdate = reportdate.reportdate,
                                npi_notes="Part Added",
                                file_type="NPI Forecast Part",
                            )
                            topbom.save(using="inputdb")
                    else:
                        print('not found in agile')
                        res = npi.rsplit('-', 1)
                        topbom = InputdbTopBomCmm(
                            tla_number_excld_rev=res[0],
                            tla_number=npi,
                            assembly_sku='AS'+res[0],
                            amparts=str(res[0])+'-XX',
                            refreshed_by=request.user.id,
                            npi_demands = npidemand.TotQty,
                            npi_reportdate = reportdate.reportdate,
                            npi_notes="Part Added",
                            file_type="NPI Forecast Part",
                        )
                        topbom.save(using="inputdb")
        return redirect('Top_BOM_Qtr_Data','JPE')
    elif team == 'SGD':
        prev_qtr = InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        if InputdbTopBomGsm.objects.using('inputdb').filter(file_type="NPI Forecast Part").exists():
            InputdbTopBomGsm.objects.using('inputdb').filter(file_type="NPI Forecast Part").delete()
        TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
        if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='SGD').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA).exists():
            npiforecast = VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='SGD').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA)
            npis = list(npiforecast.values_list('buykit', flat=True).distinct())
            for npi in npis:
                print(npi)
                npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'SGD' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ npi +"'")
                for npidemand in npiforecast:
                    if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Production").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Production' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Prototype").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Prototype' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Preliminary").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Preliminary' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="EOL").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'EOL' GROUP BY `ampart_release_date`,`AMPart`,`ampart_rev` ORDER BY `ID`  DESC LIMIT 1")
                    else:
                        partdata = None
                    if not partdata == None:
                        for data in partdata:
                            print(data.ampart)
                            res = npi.rsplit('-', 1)
                            topbom = InputdbTopBomGsm(
                                oem_part_number=res[0],
                                oem_part_number_xx=str(res[0])+'-XX',
                                sanminapn='LFARI'+res[0],
                                tla=data.ampart,
                                rev=data.ampart_rev,
                                description=data.ampart_description,
                                part_lifecycle=data.ampart_lifecycle,
                                refreshed_by=request.user.id,
                                npi_demands = npidemand.TotQty,
                                npi_reportdate = reportdate.reportdate,
                                npi_notes="Part Added",
                                file_type="NPI Forecast Part",
                            )
                            topbom.save(using="inputdb")
                    else:
                        print('not found in agile')
                        res = npi.rsplit('-', 1)
                        topbom = InputdbTopBomGsm(
                            oem_part_number=res[0],
                            oem_part_number_xx=str(res[0])+'-XX',
                            sanminapn='LFARI'+res[0],
                            tla=npi,
                            refreshed_by=request.user.id,
                            npi_demands = npidemand.TotQty,
                            npi_reportdate = reportdate.reportdate,
                            npi_notes="Part Added",
                            file_type="NPI Forecast Part",
                        )
                        topbom.save(using="inputdb")
        return redirect('Top_BOM_Qtr_Data','SGD')
    elif team == 'FGN':
        prev_qtr = InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        if InputdbTopBomFgn.objects.using('inputdb').filter(file_type="NPI Forecast Part").exists():
            InputdbTopBomFgn.objects.using('inputdb').filter(file_type="NPI Forecast Part").delete()
        TLA = list(prev_qtr.values_list('tla', flat=True).distinct())
        if VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='FGN').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA).exists():
            npiforecast = VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').filter(cm='FGN').filter(buildstart__range=[start_end[0], start_end[1]]).filter(build__in=['TQA', 'TQB', 'PLT']).filter(buykit__startswith='ASY').exclude(buykit__in=TLA)
            npis = list(npiforecast.values_list('buykit', flat=True).distinct())
            for npi in npis:
                print(npi)
                npiforecast =VwFactNpiforecastBuildscheduleIness.objects.using('inputdb').raw("SELECT *, SUM(`qty`) as TotQty FROM `vw_fact_npiforecast_buildschedule_iness` WHERE `ReportDate` = '"+ str(reportdate.reportdate) +"' AND `cm` = 'FGN' AND `buildstart` BETWEEN '"+ start_end[0] +"' AND '"+ start_end[1] +"' AND `buykit` LIKE 'ASY%%' AND `build` IN ('TQA', 'TQB', 'PLT') AND `buykit` = '"+ npi +"'")
                for npidemand in npiforecast:
                    if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Production").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Production' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Prototype").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Prototype' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="Preliminary").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'Preliminary' GROUP BY `ampart_release_date`,`AMPart` ORDER BY `ampart_release_date` DESC")
                    elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=npi).filter(ampart_lifecycle="EOL").exists():
                        partdata=FactAgilePartnumberIness.objects.using('inputdb').raw("SELECT `ID`, `AMPart`, `ampart_rev`, `ampart_lifecycle`, `ampart_description`, `ampart_release_date`  FROM `fact_Agile_PartNumber_InESS` WHERE `AMPart` = '"+ npi +"' AND `ampart_lifecycle` = 'EOL' GROUP BY `ampart_release_date`,`AMPart`,`ampart_rev` ORDER BY `ID`  DESC LIMIT 1")
                    else:
                        partdata = None
                    if not partdata == None:
                        for data in partdata:
                            print(data.ampart)
                            res = npi.rsplit('-', 1)
                            topbom = InputdbTopBomFgn(
                                oem_part_number=res[0],
                                oem_part_number_xx=str(res[0])+'-XX',
                                flexpn='ARI-'+res[0],
                                tla=data.ampart,
                                rev=data.ampart_rev,
                                description=data.ampart_description,
                                part_lifecycle=data.ampart_lifecycle,
                                refreshed_by=request.user.id,
                                npi_demands = npidemand.TotQty,
                                npi_reportdate = reportdate.reportdate,
                                npi_notes="Part Added",
                                file_type="NPI Forecast Part",
                            )
                            topbom.save(using="inputdb")
                    else:
                        print('not found in agile')
                        res = npi.rsplit('-', 1)
                        topbom = InputdbTopBomFgn(
                            oem_part_number=res[0],
                            oem_part_number_xx=str(res[0])+'-XX',
                            flexpn='ARI-'+res[0],
                            tla=npi,
                            refreshed_by=request.user.id,
                            npi_demands = npidemand.TotQty,
                            npi_reportdate = reportdate.reportdate,
                            npi_notes="Part Added",
                            file_type="NPI Forecast Part",
                        )
                        topbom.save(using="inputdb")
        return redirect('Top_BOM_Qtr_Data','FGN')





def historical_data_jpe(request):

    files=request.FILES['JPE_file']
    data = pd.read_excel(files)
   
    is_arista = data['ownership'] == "Arista"
    is_jabil = data['ownership'] == "Jabil"
    AristaParts = data[is_arista]
    jabilparts = data[is_jabil]
    row_iter = AristaParts.iterrows()
    for index, row in row_iter :
        supplier_name = row['arista_supplier_name_cost_splits']
        if str(supplier_name) != 'NaN' and str(supplier_name) != 'nan':
            suplierlist = re.split('/', str(row["arista_supplier_name_cost_splits"]))
            print(suplierlist)
            loop = 0
            for supplier in suplierlist:
                sup = re.split('\$', supplier)
                if row["moq"] != 'NaN':
                    arista_moq = re.split('/', str(row["moq"]))
                    if len(arista_moq) >= (loop + 1):
                        moq = arista_moq[loop]
                    else:
                        moq = ""
                else:
                    moq = ""

                if row["lt"] != 'NaN':
                    arista_lead_time = re.split('/', str(row["lt"]))
                    if len(arista_lead_time) >= (loop + 1):
                        leadtime = arista_lead_time[loop]
                    else:
                        leadtime = ""
                else:
                    leadtime = ""
                if (str(row["arista_supplier_mpn"]) != 'NaN' and str(row["arista_supplier_mpn"]) != 'nam'):
                    arista_mpn = re.split('/', str(row["arista_supplier_mpn"]))
                    if len(arista_mpn) >= (loop + 1):
                        mpn = arista_mpn[loop]
                    else:
                        mpn = ""
                else:
                    mpn = ""

                if (str(row["arista_st_ht"]) != 'NaN' and str(row["arista_st_ht"]) != 'nam'):
                    arista_lt_ht = re.split('/', str(row["arista_st_ht"]))
                    if len(arista_lt_ht) >= (loop + 1):
                        lt_ht = arista_lt_ht[loop]
                    else:
                        lt_ht = ""
                else:
                    lt_ht = ""

                if len(sup) > 1:
                    std_cost = re.split(' ', sup[1])
                    if len(std_cost) > 1:
                        sup_split = std_cost[1]
                    else:
                        sup_split = ""
                    std_cost_sup = std_cost[0]
                else:
                    std_cost_sup = ""
                    sup_split = ""

                loop = loop + 1
                jpe = InputdbJpeHistory(
                    cm_partno=row['cm_partno'],
                    arista_partno=row['arista_partno'],
                    consign_partno=row['consign_partno'],
                    buyer=row['buyer'],
                    item_desc=row['item_desc'],
                    commodity=row['commodity'],
                    supplier=row['supplier'],
                    mfg=row['mfg'],
                    mpn=row['mpn'],
                    lt=row['lt'],
                    moq=row['moq'],
                    moq_analysis=row['moq_analysis'],
                    po_delivery=row['po_delivery'],
                    remark=row['remark'],
                    jpe_quantity_on_hand=row['jpe_quantity_on_hand'],
                    open_po_due_current_qtr=row['open_po_due_current_qtr'],
                    open_po_due_in_next_qtr=row['open_po_due_in_next_qtr'],
                    total_oh_plus_opo_current_qtr=row['total_oh_plus_opo_current_qtr'],
                    total_oh_plus_opo_current_plus_next_qtr=row['total_oh_plus_opo_current_plus_next_qtr'],
                    cq_demand=row['cq_demand'],
                    cq_plus_1_demand=row['cq_plus_1_demand'],
                    cq_plus_2_demand=row['cq_plus_2_demand'],
                    delta_oh=row['delta_oh'],
                    notes_refreshed_demand=row['notes_refreshed_demand'],
                    new_delta=row['cq_plus_2_demand'],
                    #need_attention=row['need_attention'],
                    #new_next_qtr_demand=row['new_next_qtr_demand'],
                    #new_next_qtr_plus_1_demand=row['new_next_qtr_plus_1_demand'],
                    #new_next_qtr_plus_2_demand=row['new_next_qtr_plus_2_demand'],
                    prev_qtr_unit_price_usd=row['prev_qtr_unit_price_usd'],
                    current_qtr_unit_price_usd=row['current_qtr_unit_price_usd'],
                    approve_or_reject_column_aa_cost=row['approve_or_reject_column_aa_cost'],
                    arista_std_price_current_qtr=row['arista_std_price_current_qtr'],
                    arista_supplier_name_cost_splits=row['arista_supplier_name_cost_splits'],
                    arista_comment_current_qtr=row['arista_comment_current_qtr'],
                    arista_st_ht=lt_ht,
                    arista_advise_moq=moq,
                    arista_advise_lead_time=leadtime,
                    arista_sup_name=sup[0],
                    arista_supplier_mpn=mpn,
                    arista_sup_std_cost=std_cost_sup,
                    arista_sup_split=sup_split,
                    ownership=row['ownership'],
                    arista_pic=row['arista_pic'],
                    remark_actions_for_cmgrs_jpe_cq=row['remark_actions_for_cmgrs_jpe_cq'],
                    delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned=row['delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned'],
                    jpe_remark=row['jpe_remark'],
                    new_jabil_recommended_price_current_qtr=row['new_jabil_recommended_price_current_qtr'],
                    theresa_current_qtr_comments=row['theresa_current_qtr_comments'],
                    jabil_sup_name =row['jabil_sup_name'],
                    jabil_supplier=row['jabil_supplier'],
                    jabil_advise_moq=row['jabil_advise_moq'],
                    jabil_advise_lead_time=row['jabil_advise_lead_time'],
                    jabil_supplier_mpn=row['jabil_supplier_mpn'],
                    jabil_supplier_splits=row['jabil_supplier_splits'],
                    basedate="Q1-2021",
                )
                jpe.save(using="inputdb")
                print('1 Arista row updated', sup[0])
        else:
            jpe = InputdbJpeHistory(
                cm_partno=row['cm_partno'],
                    arista_partno=row['arista_partno'],
                    consign_partno=row['consign_partno'],
                    buyer=row['buyer'],
                    item_desc=row['item_desc'],
                    commodity=row['commodity'],
                    supplier=row['supplier'],
                    mfg=row['mfg'],
                    mpn=row['mpn'],
                    lt=row['lt'],
                    moq=row['moq'],
                    moq_analysis=row['moq_analysis'],
                    po_delivery=row['po_delivery'],
                    remark=row['remark'],
                    jpe_quantity_on_hand=row['jpe_quantity_on_hand'],
                    open_po_due_current_qtr=row['open_po_due_current_qtr'],
                    open_po_due_in_next_qtr=row['open_po_due_in_next_qtr'],
                    total_oh_plus_opo_current_qtr=row['total_oh_plus_opo_current_qtr'],
                    total_oh_plus_opo_current_plus_next_qtr=row['total_oh_plus_opo_current_plus_next_qtr'],
                    cq_demand=row['cq_demand'],
                    cq_plus_1_demand=row['cq_plus_1_demand'],
                    cq_plus_2_demand=row['cq_plus_2_demand'],
                    delta_oh=row['delta_oh'],
                    notes_refreshed_demand=row['notes_refreshed_demand'],
                    new_delta=row['cq_plus_2_demand'],
                    #need_attention=row['need_attention'],
                    #new_next_qtr_demand=row['new_next_qtr_demand'],
                    #new_next_qtr_plus_1_demand=row['new_next_qtr_plus_1_demand'],
                    #new_next_qtr_plus_2_demand=row['new_next_qtr_plus_2_demand'],
                    prev_qtr_unit_price_usd=row['prev_qtr_unit_price_usd'],
                    current_qtr_unit_price_usd=row['current_qtr_unit_price_usd'],
                    approve_or_reject_column_aa_cost=row['approve_or_reject_column_aa_cost'],
                    arista_std_price_current_qtr=row['arista_std_price_current_qtr'],
                    arista_supplier_name_cost_splits=row['arista_supplier_name_cost_splits'],
                    arista_comment_current_qtr=row['arista_comment_current_qtr'],
                    arista_st_ht=row['arista_st_ht'],
                    arista_advise_moq=row['arista_advise_moq'],
                    arista_advise_lead_time=row['arista_advise_lead_time'],
                    #arista_sup_name=row['arista_sup_name'],
                    #arista_supplier_mpn=row['arista_supplier_mpn'],
                    #arista_sup_std_cost=row['arista_sup_std_cost'],
                    #arista_sup_split=row['arista_sup_split'],
                    ownership=row['ownership'],
                    arista_pic=row['arista_pic'],
                    remark_actions_for_cmgrs_jpe_cq=row['remark_actions_for_cmgrs_jpe_cq'],
                    delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned=row['delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned'],
                    jpe_remark=row['jpe_remark'],
                    new_jabil_recommended_price_current_qtr=row['new_jabil_recommended_price_current_qtr'],
                    theresa_current_qtr_comments=row['theresa_current_qtr_comments'],
                    jabil_sup_name =row['jabil_sup_name'],
                    jabil_supplier=row['jabil_supplier'],
                    jabil_advise_moq=row['jabil_advise_moq'],
                    jabil_advise_lead_time=row['jabil_advise_lead_time'],
                    jabil_supplier_mpn=row['jabil_supplier_mpn'],
                    jabil_supplier_splits=row['jabil_supplier_splits'],
                    basedate="Q1-2021",
            )
            jpe.save(using="inputdb")
            print('1 null row updated', row["arista_partno"])
    row_iter = jabilparts.iterrows()
    for index, row in row_iter:
        supplier_name = row['jabil_supplier']
        #print(supplier_name)
        if str(supplier_name) != 'NaN' and str(supplier_name) != 'nan':
            suplierlist = re.split('/', str(row["jabil_supplier"]))
            loop = 0
            print(suplierlist)
            for supplier in suplierlist:
                if row["jabil_supplier_mpn"] != 'NaN':
                    san_mpn = re.split('/', str(row["jabil_supplier_mpn"]))
                    if len(san_mpn) >= (loop + 1):
                        mpn = san_mpn[loop]
                    else:
                        mpn = ""
                else:
                    mpn = ""

                if row["jabil_advise_moq"] != 'NaN':
                    san_moq = re.split('/', str(row["jabil_advise_moq"]))
                    if len(san_moq) >= (loop + 1):
                        moq = san_moq[loop]
                    else:
                        moq = ""
                else:
                    moq = ""

                if row["jabil_advise_lead_time"] != 'NaN':
                    san_lt = re.split('/', str(row["jabil_advise_lead_time"]))
                    if len(san_lt) >= (loop + 1):
                        leadtime = san_lt[loop]
                    else:
                        leadtime = ""
                else:
                    leadtime = ""

                if row["jabil_supplier_splits"] != 'NaN':
                    san_split = re.split('/', str(row["jabil_supplier_splits"]))
                    if len(san_split) >= (loop + 1):
                        split = san_split[loop]
                    else:
                        split = ""
                else:
                    split = ""

                #if row["sanmina_suppliers"] != 'NaN':
                #    san_sup = re.split('/', str(row["sanmina_suppliers"]))
                #    if len(san_sup) >= (loop + 1):
                #        san_supplier = san_sup[loop]
                #    else:
                #        san_supplier = ""
                #else:
                #    san_supplier = ""
                loop = loop + 1
                jpe = InputdbJpeHistory(
                    arista_partno=row['arista_partno'],
                    consign_partno=row['consign_partno'],
                    buyer=row['buyer'],
                    item_desc=row['item_desc'],
                    commodity=row['commodity'],
                    supplier=row['supplier'],
                    mfg=row['mfg'],
                    mpn=row['mpn'],
                    lt=row['lt'],
                    moq=row['moq'],
                    moq_analysis=row['moq_analysis'],
                    po_delivery=row['po_delivery'],
                    remark=row['remark'],
                    jpe_quantity_on_hand=row['jpe_quantity_on_hand'],
                    open_po_due_current_qtr=row['open_po_due_current_qtr'],
                    open_po_due_in_next_qtr=row['open_po_due_in_next_qtr'],
                    total_oh_plus_opo_current_qtr=row['total_oh_plus_opo_current_qtr'],
                    total_oh_plus_opo_current_plus_next_qtr=row['total_oh_plus_opo_current_plus_next_qtr'],
                    cq_demand=row['cq_demand'],
                    cq_plus_1_demand=row['cq_plus_1_demand'],
                    cq_plus_2_demand=row['cq_plus_2_demand'],
                    delta_oh=row['delta_oh'],
                    notes_refreshed_demand=row['notes_refreshed_demand'],
                    new_delta=row['cq_plus_2_demand'],
                    #need_attention=row['need_attention'],
                    #new_next_qtr_demand=row['new_next_qtr_demand'],
                    #new_next_qtr_plus_1_demand=row['new_next_qtr_plus_1_demand'],
                    #new_next_qtr_plus_2_demand=row['new_next_qtr_plus_2_demand'],
                    prev_qtr_unit_price_usd=row['prev_qtr_unit_price_usd'],
                    current_qtr_unit_price_usd=row['current_qtr_unit_price_usd'],
                    approve_or_reject_column_aa_cost=row['approve_or_reject_column_aa_cost'],
                    arista_std_price_current_qtr=row['arista_std_price_current_qtr'],
                    arista_supplier_name_cost_splits=row['arista_supplier_name_cost_splits'],
                    arista_comment_current_qtr=row['arista_comment_current_qtr'],
                    arista_st_ht=row['arista_st_ht'],
                    arista_advise_moq=row['arista_advise_moq'],
                    arista_advise_lead_time=row['arista_advise_lead_time'],
                    #arista_sup_name=row['arista_sup_name'],
                    #arista_supplier_mpn=row['arista_supplier_mpn'],
                    #arista_sup_std_cost=row['arista_sup_std_cost'],
                    #arista_sup_split=row['arista_sup_split'],
                    ownership=row['ownership'],
                    arista_pic=row['arista_pic'],
                    remark_actions_for_cmgrs_jpe_cq=row['remark_actions_for_cmgrs_jpe_cq'],
                    delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned=row['delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned'],
                    jpe_remark=row['jpe_remark'],
                    new_jabil_recommended_price_current_qtr=row['new_jabil_recommended_price_current_qtr'],
                    theresa_current_qtr_comments=row['theresa_current_qtr_comments'],
                    jabil_sup_name =row['jabil_sup_name'],
                    jabil_supplier=supplier,
                    jabil_advise_moq=moq,
                    jabil_advise_lead_time=leadtime,
                    jabil_supplier_mpn=mpn,
                    jabil_supplier_splits=split,
                    basedate="Q1-2021",
                    #sanmina_suppliers=san_supplier,
                )
                jpe.save(using="inputdb")
                print('1 Jabil row updated', supplier)
        else:
            jpe = InputdbJpeHistory(
                arista_partno=row['arista_partno'],
                consign_partno=row['consign_partno'],
                buyer=row['buyer'],
                item_desc=row['item_desc'],
                commodity=row['commodity'],
                supplier=row['supplier'],
                mfg=row['mfg'],
                mpn=row['mpn'],
                lt=row['lt'],
                moq=row['moq'],
                moq_analysis=row['moq_analysis'],
                po_delivery=row['po_delivery'],
                remark=row['remark'],
                jpe_quantity_on_hand=row['jpe_quantity_on_hand'],
                open_po_due_current_qtr=row['open_po_due_current_qtr'],
                open_po_due_in_next_qtr=row['open_po_due_in_next_qtr'],
                total_oh_plus_opo_current_qtr=row['total_oh_plus_opo_current_qtr'],
                total_oh_plus_opo_current_plus_next_qtr=row['total_oh_plus_opo_current_plus_next_qtr'],
                cq_demand=row['cq_demand'],
                cq_plus_1_demand=row['cq_plus_1_demand'],
                cq_plus_2_demand=row['cq_plus_2_demand'],
                delta_oh=row['delta_oh'],
                notes_refreshed_demand=row['notes_refreshed_demand'],
                new_delta=row['cq_plus_2_demand'],
                #need_attention=row['need_attention'],
                #new_next_qtr_demand=row['new_next_qtr_demand'],
                #new_next_qtr_plus_1_demand=row['new_next_qtr_plus_1_demand'],
                #new_next_qtr_plus_2_demand=row['new_next_qtr_plus_2_demand'],
                prev_qtr_unit_price_usd=row['prev_qtr_unit_price_usd'],
                current_qtr_unit_price_usd=row['current_qtr_unit_price_usd'],
                approve_or_reject_column_aa_cost=row['approve_or_reject_column_aa_cost'],
                arista_std_price_current_qtr=row['arista_std_price_current_qtr'],
                arista_supplier_name_cost_splits=row['arista_supplier_name_cost_splits'],
                arista_comment_current_qtr=row['arista_comment_current_qtr'],
                arista_st_ht=row['arista_st_ht'],
                arista_advise_moq=row['arista_advise_moq'],
                arista_advise_lead_time=row['arista_advise_lead_time'],
                #arista_sup_name=row['arista_sup_name'],
                #arista_supplier_mpn=row['arista_supplier_mpn'],
                #arista_sup_std_cost=row['arista_sup_std_cost'],
                #arista_sup_split=row['arista_sup_split'],
                ownership=row['ownership'],
                arista_pic=row['arista_pic'],
                remark_actions_for_cmgrs_jpe_cq=row['remark_actions_for_cmgrs_jpe_cq'],
                delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned=row['delta_of_new_recommend_price_current_vs_prev_arista_jpe_owned'],
                jpe_remark=row['jpe_remark'],
                new_jabil_recommended_price_current_qtr=row['new_jabil_recommended_price_current_qtr'],
                theresa_current_qtr_comments=row['theresa_current_qtr_comments'],
                jabil_sup_name =row['jabil_sup_name'],
                jabil_supplier=row['jabil_supplier'],
                jabil_advise_moq=row['jabil_advise_moq'],
                jabil_advise_lead_time=row['jabil_advise_lead_time'],
                jabil_supplier_mpn=row['jabil_supplier_mpn'],
                jabil_supplier_splits=row['jabil_supplier_splits'],
                basedate="Q1-2021",
            )
            jpe.save(using="inputdb")
            print('1 null row updated', row["arista_partno"])

    return HttpResponse("Success")

def freezetopbom(request,team):
    print('entered freezing')
    currentqtr=Current_quarter()
    if team == 'SGD':
        InputdbTopBomGsm.objects.using('inputdb').update(file_type='Base File',quarter=currentqtr,status="Freezed")
        return redirect('Top_BOM_Qtr_Data','SGD')
    elif team == 'JPE':
        InputdbTopBomCmm.objects.using('inputdb').update(file_type='Base File',quarter=currentqtr,status="Freezed")
        return redirect('Top_BOM_Qtr_Data','JPE')
    elif team == 'FGN':
        InputdbTopBomFgn.objects.using('inputdb').update(file_type='Base File',quarter=currentqtr,status="Freezed")
        return redirect('Top_BOM_Qtr_Data','FGN')

def unfreezetopbom(request,team):
    print('entered freezing')
    currentqtr=Current_quarter()
    if team == 'SGD':
        InputdbTopBomGsm.objects.using('inputdb').update(status="Not Freezed")
        return redirect('Top_BOM_Qtr_Data','SGD')
    elif team == 'JPE':
        InputdbTopBomCmm.objects.using('inputdb').update(status="Not Freezed")
        return redirect('Top_BOM_Qtr_Data','JPE')
    elif team == 'FGN':
        InputdbTopBomFgn.objects.using('inputdb').update(status="Not Freezed")
        return redirect('Top_BOM_Qtr_Data','FGN')

def Download_History(request,team):
    if team == 'SGD':
        qtr=request.POST.get('quarter')
        columns = ['quarter', 'oem_part_number', 'oem_part_number_xx', 'tla', 'sanminapn', 'rev', 'description', 'program_name', 'product_family', 'comments', 'scenarioid', 'npi_reportdate', 'cq_demand', 'notes', 'animin', 'npi_demands', 'npi_notes', 'agile_notes', 'refreshed_by', 'prod_refreshed_on', 'npi_refreshed_on', 'refreshed_rev', 'part_lifecycle', 'release_date', 'refreshed_date']

        alias = ['Quarter', 'OEM Part Number', 'OEM Part Number XX', 'TLA', 'Sanmina PN', 'Rev', 'Description', 'Program Name', 'Product Family','Comments', 'Scenario ID', 'NPI Report Date', 'CQ Demand', 'Notes', 'ANI Min', 'NPI Demands', 'NPI Notes', 'Agile Notes', 'Refreshed By', 'Production Forecast Refreshed On', 'NPI Forecast Refreshed On', 'Refreshed Rev', 'Part Lifecycle', 'Release Date', 'Refreshed Date']
        df=pd.DataFrame(InputdbTopBomGsmHistory.objects.using('inputdb').filter(quarter=qtr).values_list('quarter', 'oem_part_number', 'oem_part_number_xx', 'tla', 'sanminapn', 'rev', 'description', 'program_name', 'product_family', 'comments', 'scenarioid', 'npi_reportdate', 'cq_demand', 'notes', 'animin', 'npi_demands', 'npi_notes', 'agile_notes', 'refreshed_by', 'prod_refreshed_on', 'npi_refreshed_on', 'refreshed_rev', 'part_lifecycle', 'release_date', 'refreshed_date'),columns=columns)
        print(df.head())
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.to_excel(writer,index=False,header=alias,columns=columns)
                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename="{qtr} SGD Top BOM.xlsx"'
                return response
    if team == 'JPE':
        qtr=request.POST.get('quarter')
        columns = ['quarter', 'family', 'model', 'product_sku', 'assembly_sku', 'amparts', 'tla_number', 'tla_number_excld_rev', 'assembly_description', 'rev', 'refreshed_rev', 'part_lifecycle', 'release_date', 'refreshed_date', 'scenarioid', 'npi_reportdate', 'npi_demands', 'animin', 'cq_demand', 'notes', 'npi_notes', 'agile_notes', 'refreshed_by', 'prod_refreshed_on', 'npi_refreshed_on']

        alias = ['Quarter', 'Family', 'Model', 'Product SKU', 'Assembly SKU', 'AMParts', 'TLA Number', 'TLA Number Excld Rev', 'Assembly Description', 'Rev', 'Refreshed Rev', 'Part Lifecycle', 'Release Date', 'Refreshed Date', 'Scenario ID', 'NPI Report Date', 'NPI Demands', 'ANL Min', 'CQ Demand', 'Notes', 'NPI Notes', 'Agile Notes', 'Refreshed By', 'Production Forecast Refreshed On', 'NPI Forecast Refreshed On']
        df=pd.DataFrame(InputdbTopBomCmmHistory.objects.using('inputdb').filter(quarter=qtr).values_list('quarter', 'family', 'model', 'product_sku', 'assembly_sku', 'amparts', 'tla_number', 'tla_number_excld_rev', 'assembly_description', 'rev', 'refreshed_rev', 'part_lifecycle', 'release_date', 'refreshed_date', 'scenarioid', 'npi_reportdate', 'npi_demands', 'animin', 'cq_demand', 'notes', 'npi_notes', 'agile_notes', 'refreshed_by', 'prod_refreshed_on', 'npi_refreshed_on'),columns=columns)
        print(df.head())
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.to_excel(writer,index=False,header=alias,columns=columns)
                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename="{qtr} JPE Top BOM.xlsx"'
                return response
    if team == 'FGN':
        qtr=request.POST.get('quarter')
        columns = ['quarter', 'oem_part_number', 'oem_part_number_xx', 'tla', 'flexpn', 'rev', 'description', 'program_name', 'product_family', 'comments', 'scenarioid', 'npi_reportdate', 'cq_demand', 'notes', 'animin', 'npi_demands', 'npi_notes', 'agile_notes', 'refreshed_by', 'prod_refreshed_on', 'npi_refreshed_on', 'refreshed_rev', 'part_lifecycle', 'release_date', 'refreshed_date']

        alias = ['Quarter', 'OEM Part Number', 'OEM Part Number XX', 'TLA', 'Flex PN', 'Rev', 'Description', 'Program Name', 'Product Family','Comments', 'Scenario ID', 'NPI Report Date', 'CQ Demand', 'Notes', 'ANI Min', 'NPI Demands', 'NPI Notes', 'Agile Notes', 'Refreshed By', 'Production Forecast Refreshed On', 'NPI Forecast Refreshed On', 'Refreshed Rev', 'Part Lifecycle', 'Release Date', 'Refreshed Date']
        df=pd.DataFrame(InputdbTopBomFgnHistory.objects.using('inputdb').filter(quarter=qtr).values_list('quarter', 'oem_part_number', 'oem_part_number_xx', 'tla', 'flexpn', 'rev', 'description', 'program_name', 'product_family', 'comments', 'scenarioid', 'npi_reportdate', 'cq_demand', 'notes', 'animin', 'npi_demands', 'npi_notes', 'agile_notes', 'refreshed_by', 'prod_refreshed_on', 'npi_refreshed_on', 'refreshed_rev', 'part_lifecycle', 'release_date', 'refreshed_date'),columns=columns)
        print(df.head())
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                df.to_excel(writer,index=False,header=alias,columns=columns)
                writer.save()
                response= HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'inline; filename="{qtr} FGN Top BOM.xlsx"'
                return response
    

def Alternate_Parts(request,partno,assy):
    #if team == "SGD":
    #    eolparts = InputdbTopBomGsm.objects.using('inputdb').filter(part_lifecycle='EOL')
    #    return render(request, "portfolio/topbom/components/alternate_parts_sgd.html", context={'eolparts': eolparts})
    #elif team == "JPE":
    #    eolparts = InputdbTopBomCmm.objects.using('inputdb').filter(part_lifecycle='EOL')
    #    return render(request, "portfolio/topbom/components/alternate_parts_jpe.html", context={'eolparts': eolparts})
    alternateparts=FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=assy).filter(ampart_lifecycle__in=['Production','Prototype','Preliminary']).values('ampart','ampart_rev','ampart_lifecycle','ampart_description').order_by('ampart').annotate(dcount=Count('ampart'))
    return render(request, "portfolio/topbom/components/alternate_parts.html", context={'alternateparts': alternateparts,'partno':partno})


def manipulate_excel(request, cm):
    if request.method == 'POST':
        myfile = request.FILES['production_forecast_file_upload']
        quarter = request.POST['quarter']
        print(quarter, myfile)
        df = pd.read_excel(myfile)
        df = df.replace({pd.np.nan: None})
        q1_date_column_list = []
        q1_str_column_list = []
        q2_date_column_list = []
        q2_str_column_list = []
        q3_date_column_list = []
        q3_str_column_list = []
        q4_date_column_list = []
        q4_str_column_list = []
        for i in list(df.columns):
            if type(i) == datetime.datetime and i.strftime("%m") in ['01', '02', '03'] and quarter.split("'")[0].split('Q')[1] == '1' and i.strftime("%Y")[2:] == quarter.split("'")[1] :
                q1_date_column_list.append(i)
                df["sum_of_q1_date_column"] = df[q1_date_column_list].sum(axis=1)
            if type(i) == str and i.split(' ')[0] in ['Jan', 'Feb', 'Mar'] and quarter.split("'")[0].split('Q')[1] == '1' and quarter.split("'")[1] == i.split(' ')[1] :
                q1_str_column_list.append(i)
                df["sum_of_q1_str_column"] = df[q1_str_column_list].sum(axis=1)

            if type(i) == datetime.datetime and i.strftime("%m") in ['04', '05', '06'] and quarter.split("'")[0].split('Q')[1] == '2' and i.strftime("%Y")[2:] == quarter.split("'")[1]:
                q2_date_column_list.append(i)
                df["sum_of_q2_date_column"] = df[q2_date_column_list].sum(axis=1)
            if type(i) == str and i.split(' ')[0] in ['Apr', 'May', 'Jun'] and quarter.split("'")[0].split('Q')[1] == '2' and quarter.split("'")[1] == i.split(' ')[1] :
                q2_str_column_list.append(i)
                df["sum_of_q2_str_column"] = df[q2_str_column_list].sum(axis=1)

            if type(i) == datetime.datetime and i.strftime("%m") in ['07', '08', '09'] and quarter.split("'")[0].split('Q')[1] == '3' and i.strftime("%Y")[2:] == quarter.split("'")[1] :
                q3_date_column_list.append(i)
                df["sum_of_q3_date_column"] =  df[q3_date_column_list].sum(axis=1)

            if type(i) == str and i.split(' ')[0] in ['Jul', 'Aug', 'Sep'] and quarter.split("'")[0].split('Q')[1] == '3' and quarter.split("'")[1] == i.split(' ')[1]:
                q3_str_column_list.append(i)
                df["sum_of_q3_str_column"] = df[q3_str_column_list].sum(axis=1)

            if type(i) == datetime.datetime and i.strftime("%m") in ['10', '11', '12'] and quarter.split("'")[0].split('Q')[1] == '4' and i.strftime("%Y")[2:] == quarter.split("'")[1] :
                q4_date_column_list.append(i)
                df["sum_of_q4_date_column"] = df[q4_date_column_list].sum(axis=1)

            if type(i) == str and i.split(' ')[0] in ['Oct', 'Nov', 'Dec']  and quarter.split("'")[0].split('Q')[1] == '4' and quarter.split("'")[1] == i.split(' ')[1]:
                q4_str_column_list.append(i)
                df["sum_of_q4_str_column"] = df[q4_str_column_list].sum(axis=1)
       
        if "sum_of_q1_date_column" in df and "sum_of_q1_str_column" in df:
            df['Q1 Sum'] = df["sum_of_q1_date_column"] + df["sum_of_q1_str_column"]
        if "sum_of_q1_date_column" in df and "sum_of_q1_str_column" not in df:
            df['Q1 Sum'] = df["sum_of_q1_date_column"]
        if "sum_of_q1_date_column" not in df and "sum_of_q1_str_column" in df:
            df['Q1 Sum'] = df["sum_of_q1_str_column"]
        if "sum_of_q1_date_column" not in df and "sum_of_q1_str_column" not in df:
            pass

        if "sum_of_q2_date_column" in df and "sum_of_q2_str_column" in df:
            df['Q2 Sum'] = df["sum_of_q2_date_column"] + df["sum_of_q2_str_column"]
        if "sum_of_q2_date_column" in df and "sum_of_q2_str_column" not in df:
            df['Q2 Sum'] = df["sum_of_q2_date_column"]
        if "sum_of_q2_date_column" not in df and "sum_of_q2_str_column" in df:
            df['Q2 Sum'] = df["sum_of_q2_str_column"]
        if "sum_of_q2_date_column" not in df and "sum_of_q2_str_column" not in df:
            pass

        if "sum_of_q3_date_column" in df and "sum_of_q3_str_column" in df:
            df['Q3 Sum'] = df["sum_of_q3_date_column"] + df["sum_of_q3_str_column"]
        if "sum_of_q3_date_column" in df and "sum_of_q3_str_column" not in df:
            df['Q3 Sum'] = df["sum_of_q3_date_column"]
        if "sum_of_q3_date_column" not in df and "sum_of_q3_str_column" in df:
            df['Q3 Sum'] = df["sum_of_q3_str_column"]
        if "sum_of_q3_date_column" not in df and "sum_of_q3_str_column" not in df:
            pass

        if "sum_of_q4_date_column" in df and "sum_of_q4_str_column" in df:
            df['Q4 Sum'] = df["sum_of_q4_date_column"] + df["sum_of_q4_str_column"]
        if "sum_of_q4_date_column" in df and "sum_of_q4_str_column" not in df:
            df['Q4 Sum'] = df["sum_of_q4_date_column"]
        if "sum_of_q4_date_column" not in df and "sum_of_q4_str_column" in df:
            df['Q4 Sum'] = df["sum_of_q4_str_column"]
        if "sum_of_q4_date_column" not in df and "sum_of_q4_str_column" not in df:
            pass
        return df


@login_required
def update_production_forecast_part(request, cm):
    df = manipulate_excel(request, cm)
    quarter = request.POST['quarter']
    if cm == 'SGD':
        basefile=InputdbTopBomGsm.objects.using('inputdb').filter(file_type='Base File')
    elif cm == 'JPE':
        basefile=InputdbTopBomCmm.objects.using('inputdb').filter(file_type='Base File')
    elif cm == 'FGN':
        basefile=InputdbTopBomFgn.objects.using('inputdb').filter(file_type='Base File')
    print(cm)
    try:
        qtr = quarter.split("'")[0]
        for i in basefile:
            if cm == 'SGD':
                data = df.loc[df['Arista Part Number'] == i.oem_part_number]
                backlog = data['ANI Backlog'].values[0] if data['ANI Backlog'].size > 0 else None
            elif cm == 'JPE':
                data = df.loc[df['Arista Part Number'] == i.tla_number_excld_rev]
                backlog = data['ANL Backlog'].values[0] if data['ANL Backlog'].size > 0 else None
            elif cm == 'FGN':
                data = df.loc[df['Arista Part Number'] == i.oem_part_number]
                backlog = data['ANI Backlog'].values[0] if data['ANI Backlog'].size > 0 else None

            cq_demand = data[qtr+' Sum'].values[0] if data[qtr+' Sum'].size > 0 else None
            notes = 'No change & Demand updated' if data.size > 0 else 'Part Unavailable'
            if cm == 'SGD':
                InputdbTopBomGsm.objects.using('inputdb').filter(pk=i.id).update(cq_demand=cq_demand, animin=backlog, prod_refreshed_on=datetime.datetime.now(), notes=notes)

            elif cm == 'JPE':
                InputdbTopBomCmm.objects.using('inputdb').filter(pk=i.id).update(cq_demand=cq_demand, animin=backlog, prod_refreshed_on=datetime.datetime.now(), notes=notes)
            
            elif cm == 'FGN':
                InputdbTopBomFgn.objects.using('inputdb').filter(pk=i.id).update(cq_demand=cq_demand, animin=backlog, prod_refreshed_on=datetime.datetime.now(), notes=notes)
        print("file saved")
        return redirect('Top_BOM_Qtr_Data',cm)
    except Exception as e:
        print(e)

@login_required
def add_production_forecast_part(request, cm):
    df = manipulate_excel(request, cm)
    quarter = request.POST['quarter']
    qtr = quarter.split("'")[0]

    if cm == 'SGD':
        oem_part_in_db = InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        oem_part_list = list(oem_part_in_db.values_list('oem_part_number', flat=True).distinct())
        df.drop(df.loc[df['Arista Part Number'].isin(oem_part_list)].index, inplace=True)
    elif cm == 'JPE':
        part_in_db = InputdbTopBomCmm.objects.using('inputdb').filter(file_type="Base File").only('amparts','tla_number_excld_rev','id')
        tla_number_list = list(part_in_db.values_list('tla_number_excld_rev', flat=True).distinct())
        df.drop(df.loc[df['Arista Part Number'].isin(tla_number_list)].index, inplace=True)
    elif cm == 'FGN':
        oem_part_in_db = InputdbTopBomFgn.objects.using('inputdb').filter(file_type="Base File").only('tla','oem_part_number','id')
        oem_part_list = list(oem_part_in_db.values_list('oem_part_number', flat=True).distinct())
        df.drop(df.loc[df['Arista Part Number'].isin(oem_part_list)].index, inplace=True)

    if InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Production Forecast Part").exists():
        InputdbTopBomGsm.objects.using('inputdb').filter(file_type="Production Forecast Part").delete()

    for row in df.itertuples():

        if row[5] != None:
            apn = row[5]
            data = FactAgilePartnumberIness.objects.filter(ampart__icontains=apn).values()
            if len(row[5].split('-')) == 3:
                apn = row[5]
                if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart=apn).filter(ampart_lifecycle__in=["Production", "Prototype", "Preliminary", "EOL"]).exists():
                    part = data.filter(ampart_lifecycle__in=['Production', 'Prototype', 'Preliminary', 'EOL']).annotate(Count('ampart_release_date')).order_by('-ampart_release_date').values('id', 'ampart', 'ampart_rev', 'ampart_lifecycle', 'ampart_description', 'ampart_release_date').using('inputdb')[:1]

                else:
                    part = None

            elif len(row[5].split('-')) == 2:
                apn = row[5]
                if FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=apn).filter(ampart_lifecycle="Production").exists():
                    part = data.filter(ampart_lifecycle='Production').annotate(Count('ampart_release_date')).order_by('-ampart_release_date').values('id', 'ampart', 'ampart_rev', 'ampart_lifecycle', 'ampart_description', 'ampart_release_date').using('inputdb')[:1]

                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=apn).filter(ampart_lifecycle="Prototype").exists():
                    part = data.filter(ampart_lifecycle='Prototype').annotate(Count('ampart_release_date')).order_by('-ampart_release_date').values('id', 'ampart', 'ampart_rev', 'ampart_lifecycle', 'ampart_description', 'ampart_release_date').using('inputdb')[:1]

                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=apn).filter(ampart_lifecycle="Preliminary").exists():
                    part = data.filter(ampart_lifecycle='Preliminary').annotate(Count('ampart_release_date')).order_by('-ampart_release_date').values('id', 'ampart', 'ampart_rev', 'ampart_lifecycle', 'ampart_description', 'ampart_release_date').using('inputdb')[:1]

                elif FactAgilePartnumberIness.objects.using('inputdb').filter(ampart__icontains=apn).filter(ampart_lifecycle="EOL").exists():
                    part = data.filter(ampart_lifecycle='EOL').annotate(Count('ampart_release_date')).order_by('-ampart_release_date').values('id', 'ampart', 'ampart_rev', 'ampart_lifecycle', 'ampart_description', 'ampart_release_date').using('inputdb')[:1]

                else:
                    part = None
            if cm == 'SGD':
                df_len = len(df.columns)
                print(df_len)
                print(row,row[5])
                top_sgd_list = []
                if not part == None:
                    for data in part:
                        topbom = InputdbTopBomGsm(
                        oem_part_number=row[5],
                        oem_part_number_xx=str(row[5])+'-XX',
                        sanminapn='LFARI'+row[5],
                        tla=data['ampart'],
                        rev=data['ampart_rev'],
                        description=data['ampart_description'],
                        part_lifecycle=data['ampart_lifecycle'],
                        refreshed_by=request.user.id,
                        cq_demand=row[df_len],
                        animin=row[8],
                        notes="Part Added",
                        file_type="Production Forecast Part",
                        prod_refreshed_on=datetime.datetime.now()

                        )
                        topbom.save(using='inputdb')
                else:
                    topbom = InputdbTopBomGsm(
                        oem_part_number=row[5],
                        oem_part_number_xx=str(row[5])+'-XX',
                        sanminapn='LFARI'+row[5],
                        tla=row[5],
                        refreshed_by=request.user.id,
                        cq_demand=row[df_len],
                        animin=row[8],
                        notes="Part Added",
                        file_type="Production Forecast Part",
                        prod_refreshed_on=datetime.datetime.now()
                    )
                    topbom.save(using='inputdb')
                return redirect('Top_BOM_Qtr_Data',cm)
            elif cm == 'JPE':
                df_len = len(df.columns)
                print(df_len)
                print(row,row[5])
                top_jpe_list = []
                if not part == None:
                    for data in part:
                        topbom = InputdbTopBomCmm(
                            tla_number_excld_rev=row[5],
                            tla_number=str(row[5])+'-XX',
                            assembly_sku='AS'+row[5],
                            amparts=data['ampart'],
                            rev=data['ampart_rev'],
                            assembly_description=data['ampart_description'],
                            part_lifecycle=data['ampart_lifecycle'],
                            refreshed_by=request.user.id,
                            cq_demand=row[df_len],
                            animin=row[10],
                            notes="Part Added",
                            file_type="Production Forecast Part",
                        )
                        topbom.save(using='inputdb')

                else:
                    topbom = InputdbTopBomCmm(
                        tla_number_excld_rev=row[5],
                        tla_number=str(row[5])+'-XX',
                        assembly_sku='AS'+row[5],
                        amparts=row[5],
                        refreshed_by=request.user.id,
                        cq_demand=row[df_len],
                        animin=row[10],
                        notes="Part Added",
                        file_type="Production Forecast Part",
                    )
                    topbom.save(using="inputdb")
            
                return redirect('Top_BOM_Qtr_Data',cm)
            elif cm == 'FGN':
                df_len = len(df.columns)
                print(df_len)
                print(row,row[5], row[8 ])
                top_sgd_list = []
                if not part == None:
                    for data in part:
                        topbom = InputdbTopBomFgn(
                        oem_part_number=row[5],
                        oem_part_number_xx=str(row[5])+'-XX',
                        flexpn='ARI-'+row[5],
                        tla=data['ampart'],
                        rev=data['ampart_rev'],
                        description=data['ampart_description'],
                        part_lifecycle=data['ampart_lifecycle'],
                        refreshed_by=request.user.id,
                        cq_demand=row[df_len],
                        animin=row[7],
                        notes="Part Added",
                        file_type="Production Forecast Part",
                        prod_refreshed_on=datetime.datetime.now()

                        )
                        topbom.save(using='inputdb')
                else:
                    topbom = InputdbTopBomFgn(
                        oem_part_number=row[5],
                        oem_part_number_xx=str(row[5])+'-XX',
                        flexpn='ARI-'+row[5],
                        tla=row[5],
                        refreshed_by=request.user.id,
                        cq_demand=row[df_len],
                        animin=row[7],
                        notes="Part Added",
                        file_type="Production Forecast Part",
                        prod_refreshed_on=datetime.datetime.now()
                    )
                    topbom.save(using='inputdb')
                return redirect('Top_BOM_Qtr_Data',cm)
            


@login_required
def download_template(request, cm):
    """
    This method downloads SGD/JPE/FGN template files / Instructions files of all three cm's
    """
    if request.method == 'GET':
        if cm == 'SGD':
            download_file = settings.RESOURCES_ROOT+'/topbom/ASForecast_Production_SGD.xlsx'
        elif cm == 'JPE':
            download_file = settings.RESOURCES_ROOT+'/topbom/ASForecast_Production_JPE.xlsx'
        elif cm == 'FGN':
            download_file = settings.RESOURCES_ROOT+'/topbom/ASForecast_Production_FGN.xlsx'

        if cm == 'Instruction': # Here cm as 'instruction' for downloading instruction pdf for all three cm's
            download_file = settings.RESOURCES_ROOT+'/topbom/Instructions/Top Bom -Instruction.docx.pdf'

        file_mimetype = mimetypes.guess_type(download_file)
        file_wrapper = FileWrapper(open(download_file, 'rb'))
        response = HttpResponse(file_wrapper, content_type=file_mimetype)
        response['X-Sendfile'] = download_file
        response['Content-Length'] = os.stat(download_file).st_size
        if cm == 'SGD':
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('ASForecast_Production_SGD.xlsx')
        elif cm == 'JPE':
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('ASForecast_Production_JPE.xlsx')
        elif cm == 'FGN':
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('ASForecast_Production_FGN.xlsx')
        if cm == 'Instruction': # Here cm as 'instruction' for downloading instruction pdf for all three cm's
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('Top Bom -Instruction.docx.pdf')

        return response

