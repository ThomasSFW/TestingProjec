from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db.backends import utils
from django.core import serializers
from django.db import connections
from datetime import date, timedelta
import json
import pyodbc
import urllib.parse as urlparse
import requests
import urllib.request
import shutil
import os
import math
import numbers
import calendar
import datetime
from django.conf import settings
from django import template
import sys

register = template.Library()

from InfinyRealty_app.models import Users, LofForms, LofKLA, LofKLASubjects, LofFormOverall, LofFormOverall_2019_SPC
from InfinyRealty_app.models import ESRschools, Focussubtypes, ESRForms, KLAForms, EformPage
from InfinyRealty_app.models import Tabs, Categories, SubCategories, PageView

def PIRating(request):
    if not request.session.get('post'): return redirect('')
    year = request.POST.get('year')
    schoollevel = request.GET.get('schoollevel')
    years = ESRschools.objects.using('sqp').filter(insptype='ESR').order_by('-esryear').values('esryear').distinct()
    if years:
        year = years[0]['esryear']
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=focus')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_FocusSubType_Year where focusYear = '" + year + "'")
    focussubtypes = cursor.fetchall()
    #focussubtypes = Focussubtypes.objects.using('focus').order_by('sequence')

    action = request.POST.get('action')

    accessid = 114
    request.session['accessid'] = accessid
    cnxn_menu = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=qadind')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where post = '" + request.session.get('post') + "'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('sqp').get(postdesc=request.session.get('post'), year=currentschoolyear(), isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='sqp')
    pageviewlog(accessid, request.session.get('loginid'), request.session.get('post'), request.session.get('post_org'))
    context = {
        "action": action,
        "years": years,
        "focussubtypes": focussubtypes,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "report_template/PIRating.html", context)

@csrf_exempt
def PIRating_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    schoollevel = request.POST.get('schoollevel')
    inspectiontype = request.POST.get('inspectiontype')
    subject = request.POST.get('subject')
    focustype = request.POST.get('focustype')
    reporttype = request.POST.get('reporttype')
    part = request.POST.get('part')
    loginid = request.POST.get('loginid')
    status = request.POST.get('status')
    displaymode = request.POST.get('displaymode')
    if focustype == "":
        focustype = 1

    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "user_year": year,
            "team_list": team_list,
        }

    if action == "subject_list":
        subject_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=focus')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_FocusSubType_Year where focusYear = '" + str(year) + "'")
        subject_list = cursor.fetchall()

        context = {
            "action": action,
            "user_year": year,
            "subject_list": subject_list,
        }

    if action == "menutab":
        context = {
            "action": action,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionList_SchoolType_School_Count where year_name = '" + year + "'")
        schoolTypeCountList = cursor.fetchall()
        cursor.execute("select * from V_InpsectionList_FocusType_School_Count where year_name = '" + year + "' order by sequence")
        focusTypeCountList = cursor.fetchall()

        context = {
            "action": action,
            "selectedyear": year,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
            "schooltypecountlist": schoolTypeCountList,
            "focustypecountlist": focusTypeCountList,
        }
    if action == "report":
        eformpage = EformPage.objects.using('esrform').filter(year=year, formpage="supp_note_b_form", part="parta", pagebase=2, pageid__in=['a','a11','a12','a13']).order_by('sequence')
        eformpage_distinct = []
        seen_page_ids = set()
        for u in eformpage:
            temp_id = u.pageid+u.readtable
            if temp_id not in seen_page_ids:
                eformpage_distinct.append(u)
                seen_page_ids.add(temp_id)
        eformpage = eformpage_distinct
        context = {
            "action": action,
            "eformpage": eformpage,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "supp_note_b_form":
        pagetype = request.POST.get('pagetype')
        tabname = request.POST.get('tabname')
        dbName = request.POST.get('dbname').lower()
        tableName = request.POST.get('tablename').lower()

        strWhereFieldName = "esrFormID"
        if dbName == "esrform": strWhereFieldName = "esrFormID"
        if dbName == "klaform": strWhereFieldName = "klaFormID"
        if dbName == "focus": strWhereFieldName = "schoolID"
        if dbName == "cr": strWhereFieldName = "esrFormID"
        if dbName == "sqp": strWhereFieldName = "schoolID"
        if dbName == "esrform" and tableName == "tblFIE05": strWhereFieldName = "schoolID"
        if dbName == "schoolmaster": strWhereFieldName = "sdpFormID"

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate_SDP_Info '"+inspectiontype+"'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        report_list = []
        data_list = []
        field_list = []
        formid_list = []

        if reporttype == "raw":
            for z in "123678":
                if pagetype == "#a2"+str(z):
                    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=schoolmaster')
                    cursor = cnxn.cursor()
                    cursor.execute("getStructure_2019_WITHSDP 'SDP0"+str(z)+"', 'A', 2, 'SDP', 2014")
                    field_list = cursor.fetchall()

            sSQL = ""
            sql1 = ""
            readtable = ""
            debug = focustype
            for w in inspection_list:
                try:
                    checked = 1
                    show_all = "Y"
                    formid = ""
                    if dbName == "esrform": formid = w.SchoolID + w.esrYear
                    if dbName == "klaform": formid = w.SchoolID + w.esrYear
                    if dbName == "focus": formid = w.SchoolID + w.esrYear
                    if dbName == "cr": formid = w.SchoolID + w.esrYear
                    insptype = w.InspType
                    schooltype = w.schoolTypeID
                    if w.InspType == "ESR" and w.code[:2] == "EX":
                        schooltype = "SP"
                    if w.InspType == "FI" and w.code[:1] == "3":
                        schooltype = "SP"
                    if w.InspType == "ESR":
                        esrform = ESRForms.objects.using('esrform').filter(esrformid=formid)
                        formstatus = esrform.first().status if esrform.exists() else None
                    if w.InspType == "FI":
                        klaform = KLAForms.objects.using('klaform').filter(klaformid=formid)
                        formstatus = klaform.first().status if klaform.exists() else None

                    if checked == 1:
                        if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                            checked = 0
                        if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                            checked = 0
                    if schoollevel != "" and checked == 1:
                        if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                            checked = 0
                        if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                            checked = 0
                        if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                            checked = 0
                    if inspectiontype != "" and checked == 1:
                        if w.InspType != inspectiontype:
                            checked = 0
                    if subject != "99" and checked == 1:
                        if str(w.subcode) != subject:
                            checked = 0
                        if str(w.focusTypeID) != focustype:
                            checked = 0
                    if part >= "partc" and checked == 1:
                        if w.InspType  == "ESR":
                            checked = 0
                    if part == "partc" and checked == 1:
                        if str(w.focusTypeID) != "1":
                            checked = 0
                    if part == "partd" and checked == 1:
                        if str(w.focusTypeID) != "34":
                            checked = 0
                    if part == "parte" and checked == 1:
                        if str(w.focusTypeID) != "36":
                            checked = 0
                    if part == "partf" and checked == 1:
                        if str(w.focusTypeID) != "38":
                            checked = 0
                    if loginid != "" and checked == 1:
                        if str(w.LoginID) != loginid:
                            checked = 0
                    if status != "" and checked == 1:
                        if str(formstatus) != status:
                            checked = 0
                    if displaymode == "1" and w.SchoolID[:1] == "9":
                        checked = 0
                    if displaymode == "2" and w.SchoolID[:1] != "9":
                        checked = 0
                    if checked == 1:
                        field_length = 0
                        if pagetype == "#a" or pagetype == "#a2":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                            cursor = cnxn.cursor()
                            cursor.execute("exec spC12InfoInsp '" + formid + "','" + insptype + "'")
                            data_list = cursor.fetchall()
                            show_all = "Y"
                        if pagetype == "#a11":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
                            cursor = cnxn.cursor()
                            cursor.execute("select * from V_Inspection_PI_Rating where schoolid = '" + w.SchoolID + "' and esryear = '" + str(year) + "'")
                            data_list = cursor.fetchall()
                            show_all = "Y"
                        if pagetype == "#a12" or pagetype == "#a13":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select * from " + tableName + " where esrformid = '" + formid + "'")
                            data_list = cursor.fetchall()
                            #data_list = [record for record in data_list if all(field is not None and field != '' for field in record[1:5])]
                            show_all = "N"
                        if data_list and show_all == "N" or show_all == "Y":
                            report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'SchoolType': schooltype, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus, 'endofsdp': w.endOfSdp, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
                except Exception as e:
                    sSQL = 'N/A'
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno
                    sSQL = "Error linexx "+str(line_number)+": "+str(e)+sSQL

        context = {
            "action": action,
            "report_list": report_list,
            "formid_list": formid_list,
            "tabname": tabname,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
            "pagetype": pagetype,
            "field_list": field_list,
        }
    if action == "schoollist":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate '"+inspectiontype+"'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        report_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                checked = 1
                if w.InspType == "ESR":
                    esrform = ESRForms.objects.using('esrform').filter(esrformid=w.SchoolID + w.esrYear)
                    formstatus = esrform.first().status if esrform.exists() else None
                if w.InspType == "FI":
                    klaform = KLAForms.objects.using('klaform').filter(klaformid=w.SchoolID + w.esrYear)
                    formstatus = klaform.first().status if klaform.exists() else None
                if checked == 1:
                    if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                        checked = 0
                    if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                        checked = 0
                if schoollevel != "" and checked == 1:
                    if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                        checked = 0
                    if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                        checked = 0
                    if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                        checked = 0
                if inspectiontype != "" and checked == 1:
                    if w.InspType != inspectiontype:
                        checked = 0
                if subject != "99" and checked == 1:
                    if str(w.subcode) != subject:
                        checked = 0
                    if str(w.focusTypeID) != focustype:
                        checked = 0
                if part >= "partc" and checked == 1:
                    if w.InspType == "ESR":
                        checked = 0
                if part == "partc" and checked == 1:
                    if str(w.focusTypeID) != "1":
                        checked = 0
                if part == "partd" and checked == 1:
                    if str(w.focusTypeID) != "34":
                        checked = 0
                if part == "parte" and checked == 1:
                    if str(w.focusTypeID) != "36":
                        checked = 0
                if part == "partf" and checked == 1:
                    if str(w.focusTypeID) != "38":
                        checked = 0
                if loginid != "" and checked == 1:
                    if str(w.LoginID) != loginid:
                        checked = 0
                if status != "" and checked == 1:
                    if str(formstatus) != status:
                        checked = 0
                if displaymode == "1" and w.SchoolID[:1] == "9":
                    checked = 0
                if displaymode == "2" and w.SchoolID[:1] != "9":
                    checked = 0
                if checked == 1:
                    report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus})
            except Exception as e:
                sSQL = 'N/A'
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                sSQL = "Error line "+str(line_number)+": "+str(e)

        context = {
            "action": action,
            "displaymode": displaymode,
            "report_list": report_list,
            "sql": sSQL,
        }
    return render(request, "report_template/PIRating_response.html", context)

def PIRatingGeneral(request):
    if not request.session.get('post'): return redirect('')
    year = request.POST.get('year')
    schoollevel = request.GET.get('schoollevel')
    years = ESRschools.objects.using('sqp').filter(insptype='ESR').order_by('-esryear').values('esryear').distinct()
    if years:
        year = years[0]['esryear']
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=focus')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_FocusSubType_Year where focusYear = '" + year + "'")
    focussubtypes = cursor.fetchall()
    #focussubtypes = Focussubtypes.objects.using('focus').order_by('sequence')

    action = request.POST.get('action')

    accessid = 124
    request.session['accessid'] = accessid
    cnxn_menu = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=qadind')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where post = '" + request.session.get('post') + "'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('sqp').get(postdesc=request.session.get('post'), year=currentschoolyear(), isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='sqp')
    pageviewlog(accessid, request.session.get('loginid'), request.session.get('post'), request.session.get('post_org'))
    context = {
        "action": action,
        "years": years,
        "focussubtypes": focussubtypes,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "report_template/PIRatingGeneral.html", context)

@csrf_exempt
def PIRatingGeneral_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    schoollevel = request.POST.get('schoollevel')
    inspectiontype = request.POST.get('inspectiontype')
    subject = request.POST.get('subject')
    focustype = request.POST.get('focustype')
    reporttype = request.POST.get('reporttype')
    part = request.POST.get('part')
    loginid = request.POST.get('loginid')
    status = request.POST.get('status')
    displaymode = request.POST.get('displaymode')
    if focustype == "":
        focustype = 1

    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "user_year": year,
            "team_list": team_list,
        }

    if action == "subject_list":
        subject_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=focus')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_FocusSubType_Year where focusYear = '" + str(year) + "'")
        subject_list = cursor.fetchall()

        context = {
            "action": action,
            "user_year": year,
            "subject_list": subject_list,
        }

    if action == "menutab":
        context = {
            "action": action,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "pirating":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate 'ESR'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        report_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                checked = 1
                if w.InspType == "ESR":
                    esrform = ESRForms.objects.using('esrform').filter(esrformid=w.SchoolID + w.esrYear)
                    formstatus = esrform.first().status if esrform.exists() else None
                if w.InspType == "FI":
                    klaform = KLAForms.objects.using('klaform').filter(klaformid=w.SchoolID + w.esrYear)
                    formstatus = klaform.first().status if klaform.exists() else None
                if checked == 1:
                    if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                        checked = 0
                    if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                        checked = 0
                if schoollevel != "" and checked == 1:
                    if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                        checked = 0
                    if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                        checked = 0
                if inspectiontype != "" and checked == 1:
                    if w.InspType != inspectiontype:
                        checked = 0
                if subject != "99" and checked == 1:
                    if str(w.subcode) != subject:
                        checked = 0
                    if str(w.focusTypeID) != focustype:
                        checked = 0
                if part >= "partc" and checked == 1:
                    if w.InspType == "ESR":
                        checked = 0
                if part == "partc" and checked == 1:
                    if str(w.focusTypeID) != "1":
                        checked = 0
                if part == "partd" and checked == 1:
                    if str(w.focusTypeID) != "34":
                        checked = 0
                if part == "parte" and checked == 1:
                    if str(w.focusTypeID) != "36":
                        checked = 0
                if part == "partf" and checked == 1:
                    if str(w.focusTypeID) != "38":
                        checked = 0
                if loginid != "" and checked == 1:
                    if str(w.LoginID) != loginid:
                        checked = 0
                if status != "" and checked == 1:
                    if str(formstatus) != status:
                        checked = 0
                if displaymode == "1" and w.SchoolID[:1] == "9":
                    checked = 0
                if displaymode == "2" and w.SchoolID[:1] != "9":
                    checked = 0
                if w.code[:2] == "EP":
                    school_level = "P"
                if w.code[:2] == "ES":
                    school_level = "S"
                if w.code[:2] == "EX":
                    school_level = "SP"
                if checked == 1:
                    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
                    cursor = cnxn.cursor()
                    cursor.execute("select * from V_Inspection_PI_Rating where schoolid = '" + w.SchoolID + "' and esryear = '" + str(w.esrYear) + "'")
                    sql1 = "select * from V_Inspection_PI_Rating where schoolid = '" + w.SchoolID + "' and esryear = '" + str(w.esrYear) + "'"
                    data_list = cursor.fetchall()
                    if data_list:
                        report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'schoollevel': school_level, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus, 'sql1': sql1, 'datalist': data_list})
            except Exception as e:
                sSQL = 'N/A'
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                sSQL = "Error line "+str(line_number)+": "+str(e)

        context = {
            "action": action,
            "selectedyear": year,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
            "report_list": report_list,
        }
    if action == "report":
        eformpage = EformPage.objects.using('esrform').filter(year=year, formpage="supp_note_b_form", part="parta", pagebase=2, pageid__in=['a','a11']).order_by('sequence')
        eformpage_distinct = []
        seen_page_ids = set()
        for u in eformpage:
            temp_id = u.pageid+u.readtable
            if temp_id not in seen_page_ids:
                eformpage_distinct.append(u)
                seen_page_ids.add(temp_id)
        eformpage = eformpage_distinct
        context = {
            "action": action,
            "eformpage": eformpage,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "supp_note_b_form":
        pagetype = request.POST.get('pagetype')
        tabname = request.POST.get('tabname')
        dbName = request.POST.get('dbname').lower()
        tableName = request.POST.get('tablename').lower()

        strWhereFieldName = "esrFormID"
        if dbName == "esrform": strWhereFieldName = "esrFormID"
        if dbName == "klaform": strWhereFieldName = "klaFormID"
        if dbName == "focus": strWhereFieldName = "schoolID"
        if dbName == "cr": strWhereFieldName = "esrFormID"
        if dbName == "sqp": strWhereFieldName = "schoolID"
        if dbName == "esrform" and tableName == "tblFIE05": strWhereFieldName = "schoolID"
        if dbName == "schoolmaster": strWhereFieldName = "sdpFormID"

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate_SDP_Info '"+inspectiontype+"'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        report_list = []
        data_list = []
        field_list = []
        formid_list = []

        if reporttype == "raw":
            sSQL = ""
            sql1 = ""
            readtable = ""
            debug = focustype
            for w in inspection_list:
                try:
                    checked = 1
                    show_all = "Y"
                    formid = ""
                    if dbName == "esrform": formid = w.SchoolID + w.esrYear
                    if dbName == "klaform": formid = w.SchoolID + w.esrYear
                    if dbName == "focus": formid = w.SchoolID + w.esrYear
                    if dbName == "cr": formid = w.SchoolID + w.esrYear
                    insptype = w.InspType
                    schooltype = w.schoolTypeID
                    if w.InspType == "ESR" and w.code[:2] == "EX":
                        schooltype = "SP"
                    if w.InspType == "FI" and w.code[:1] == "3":
                        schooltype = "SP"
                    if w.InspType == "ESR":
                        esrform = ESRForms.objects.using('esrform').filter(esrformid=formid)
                        formstatus = esrform.first().status if esrform.exists() else None
                    if w.InspType == "FI":
                        klaform = KLAForms.objects.using('klaform').filter(klaformid=formid)
                        formstatus = klaform.first().status if klaform.exists() else None

                    if checked == 1:
                        if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                            checked = 0
                        if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                            checked = 0
                    if schoollevel != "" and checked == 1:
                        if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                            checked = 0
                        if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                            checked = 0
                        if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                            checked = 0
                    if inspectiontype != "" and checked == 1:
                        if w.InspType != inspectiontype:
                            checked = 0
                    if subject != "99" and checked == 1:
                        if str(w.subcode) != subject:
                            checked = 0
                        if str(w.focusTypeID) != focustype:
                            checked = 0
                    if part >= "partc" and checked == 1:
                        if w.InspType  == "ESR":
                            checked = 0
                    if part == "partc" and checked == 1:
                        if str(w.focusTypeID) != "1":
                            checked = 0
                    if part == "partd" and checked == 1:
                        if str(w.focusTypeID) != "34":
                            checked = 0
                    if part == "parte" and checked == 1:
                        if str(w.focusTypeID) != "36":
                            checked = 0
                    if part == "partf" and checked == 1:
                        if str(w.focusTypeID) != "38":
                            checked = 0
                    if loginid != "" and checked == 1:
                        if str(w.LoginID) != loginid:
                            checked = 0
                    if status != "" and checked == 1:
                        if str(formstatus) != status:
                            checked = 0
                    if displaymode == "1" and w.SchoolID[:1] == "9":
                        checked = 0
                    if displaymode == "2" and w.SchoolID[:1] != "9":
                        checked = 0
                    if checked == 1:
                        field_length = 0
                        if pagetype == "#a" or pagetype == "#a2":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                            cursor = cnxn.cursor()
                            cursor.execute("exec spC12InfoInsp '" + formid + "','" + insptype + "'")
                            data_list = cursor.fetchall()
                            show_all = "Y"
                        if pagetype == "#a11":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
                            cursor = cnxn.cursor()
                            cursor.execute("select * from V_Inspection_PI_Rating where schoolid = '" + w.SchoolID + "' and esryear = '" + str(year) + "'")
                            data_list = cursor.fetchall()
                            show_all = "Y"
                        if data_list and show_all == "N" or show_all == "Y":
                            report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'SchoolType': schooltype, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus, 'endofsdp': w.endOfSdp, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
                except Exception as e:
                    sSQL = 'N/A'
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno
                    sSQL = "Error linexx "+str(line_number)+": "+str(e)+sSQL

        context = {
            "action": action,
            "report_list": report_list,
            "formid_list": formid_list,
            "tabname": tabname,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
            "pagetype": pagetype,
            "field_list": field_list,
        }
    if action == "schoollist":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate '"+inspectiontype+"'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        report_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                checked = 1
                if w.InspType == "ESR":
                    esrform = ESRForms.objects.using('esrform').filter(esrformid=w.SchoolID + w.esrYear)
                    formstatus = esrform.first().status if esrform.exists() else None
                if w.InspType == "FI":
                    klaform = KLAForms.objects.using('klaform').filter(klaformid=w.SchoolID + w.esrYear)
                    formstatus = klaform.first().status if klaform.exists() else None
                if checked == 1:
                    if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                        checked = 0
                    if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                        checked = 0
                if schoollevel != "" and checked == 1:
                    if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                        checked = 0
                    if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                        checked = 0
                    if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                        checked = 0
                if inspectiontype != "" and checked == 1:
                    if w.InspType != inspectiontype:
                        checked = 0
                if subject != "99" and checked == 1:
                    if str(w.subcode) != subject:
                        checked = 0
                    if str(w.focusTypeID) != focustype:
                        checked = 0
                if part >= "partc" and checked == 1:
                    if w.InspType == "ESR":
                        checked = 0
                if part == "partc" and checked == 1:
                    if str(w.focusTypeID) != "1":
                        checked = 0
                if part == "partd" and checked == 1:
                    if str(w.focusTypeID) != "34":
                        checked = 0
                if part == "parte" and checked == 1:
                    if str(w.focusTypeID) != "36":
                        checked = 0
                if part == "partf" and checked == 1:
                    if str(w.focusTypeID) != "38":
                        checked = 0
                if loginid != "" and checked == 1:
                    if str(w.LoginID) != loginid:
                        checked = 0
                if status != "" and checked == 1:
                    if str(formstatus) != status:
                        checked = 0
                if displaymode == "1" and w.SchoolID[:1] == "9":
                    checked = 0
                if displaymode == "2" and w.SchoolID[:1] != "9":
                    checked = 0
                if checked == 1:
                    report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus})
            except Exception as e:
                sSQL = 'N/A'
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                sSQL = "Error line "+str(line_number)+": "+str(e)

        context = {
            "action": action,
            "displaymode": displaymode,
            "report_list": report_list,
            "sql": sSQL,
        }
    return render(request, "report_template/PIRatingGeneral_response.html", context)

@csrf_exempt
def lofSummary(request):
    if not request.session.get('post'): return redirect('')
    lofyear = request.POST.get('lofyear')
    schoollevel = request.GET.get('schoollevel')
    years = LofForms.objects.using('lofform').filter(lofformyear__gt=2007).order_by('-lofformyear').values('lofformyear').distinct()    
    LofKLAList = LofKLA.objects.using('lofform').order_by('ordering')
    action = request.POST.get('action')
           
    accessid = 115               
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=qadind')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where post = '"+request.session.get('post')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('sqp').get(postdesc=request.session.get('post'),year=currentschoolyear(),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='sqp')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('post'),request.session.get('post_org'))
    context = {
        "action": action,
        "years": years,        
        "lofklalist": LofKLAList,        
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "report_template/lofsummary.html", context)

@csrf_exempt    
def lofSummary_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    lofyear = request.POST.get('lofyear')    
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    schoollevel = request.POST.get('schoollevel')
    inspectiontype = request.POST.get('inspectiontype') 
    inspectortype = request.POST.get('inspectortype')
    klaid = request.POST.get('klaid')
    subject = request.POST.get('subject') 
    teachingmode = request.POST.get('teachingmode')
    displaymode = request.POST.get('displaymode')    
    klatext = request.POST.get('klatext')

    if action == "lofklasubject_list":
        LofKLASubjectList = LofForms.objects.using('lofform').filter(klaid=klaid).filter(lofformyear=lofyear).order_by('subject').values('subject').distinct()
        context = {
            "action": action,            
            "lofklasubjectlist": LofKLASubjectList
        }
    if action == "lofmenutab":
        context = {
            "action": action,
            "lofyear": lofyear,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "inspectortype": inspectortype,
            "klaid": klaid,
            "subject": subject,
            "teachingmode": teachingmode,
            "displaymode": displaymode,
        }
    if action == "lofoverview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=lofform')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_LOFForm_SchoolType_Lesson_Upload where year_name = '"+lofyear+"'")
        schoolLOFCountList = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionList_School_Count where year_name = '"+lofyear+"'")
        schoolCountList = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=lofform')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_LOFForm_Outstanding where year_name = '"+lofyear+"'")
        LOFOutstandingCountList = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionType_School_Count where year_name = '"+lofyear+"'")
        insptypeschoolCountList = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=lofform')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_LOFForm_InspType_Outstanding where year_name = '"+lofyear+"'")
        LOFInspTypeOutstandingCountList = cursor.fetchall()


        context = {
            "action": action,
            "selectedyear": lofyear,
            "lofyear": lofyear,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "inspectortype": inspectortype,
            "klaid": klaid,
            "subject": subject,
            "teachingmode": teachingmode,
            "displaymode": displaymode,
            "schoolcountlist": schoolCountList,
            "schoollofcountlist": schoolLOFCountList,
            "lofoutstandingcountlist": LOFOutstandingCountList,
            "insptypeschoolCountList": insptypeschoolCountList,
            "lofinsptypeoutstandingcountlist": LOFInspTypeOutstandingCountList,
        }
    if action == "lofreport":
        params = {'year_' + lofyear: 1}
        if schoollevel == "3":
            if displaymode == "1" or displaymode == "2" :
                LofFormOverallList = LofFormOverall_2019_SPC.objects.using('lofform').filter(**params).filter(displaytypeid__in=['5']).order_by('id')
            else:
                LofFormOverallList = LofFormOverall_2019_SPC.objects.using('lofform').filter(**params).filter(displaytypeid__in=['1','5']).order_by('id')
        else:
            if displaymode == "1" or displaymode == "2" :
                LofFormOverallList = LofFormOverall.objects.using('lofform').filter(**params).filter(displaytypeid__in=['5']).order_by('id')
            else:
                LofFormOverallList = LofFormOverall.objects.using('lofform').filter(**params).filter(displaytypeid__in=['1','5']).order_by('id')

        schoolyeartemp = int(lofyear)+1
        schoolyeartemp = str(schoolyeartemp)        
        LofFormsSchoolYear =  lofyear + '/' + schoolyeartemp
        
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=lofform')
        cursor = cnxn.cursor()
        
        sSQL = 'N/A'
        
        lofoverallresult_list = [i for i in range(1)]
        lofoverallresult_sum = []
        lof_chk = [[]]
        lof_list = []
        code_temp = ''
        pSQL = ""
        LofFormsDataCountKS1 = 0
        LofFormsDataCountKS2 = 0
        LofFormsDataCountKS3 = 0
        LofFormsDataCountKS4 = 0
        LofFormsDataCountALL = 0
        learningall = 0
        sSQL = ""
        
        for w in LofFormOverallList:
            try:
                if schoollevel == "3":
                    sSQL = "<br><br>exec spLOFCountAverageBySchool_2019_SPC_2022 '"+str(w.lofid)+"','"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+schoollevel+"','"+inspectiontype+"','"+inspectortype+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"','"+str(displaymode)+"'"
                    cursor.execute("exec spLOFCountAverageBySchool_2019_SPC_2022 '"+str(w.lofid)+"','"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+schoollevel+"','"+inspectiontype+"','"+inspectortype+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"','"+str(displaymode)+"'")
                else:
                    sSQL = "<br><br>exec spLOFCountAverageBySchool2022 '"+str(w.lofid)+"','"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+schoollevel+"','"+inspectiontype+"','"+inspectortype+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"','"+str(displaymode)+"'"
                    cursor.execute("exec spLOFCountAverageBySchool2022 '"+str(w.lofid)+"','"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+schoollevel+"','"+inspectiontype+"','"+inspectortype+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"','"+str(displaymode)+"'")
                lofoverallresult = cursor.fetchall()
                sSQL = sSQL + str(w.lofid)

                def zero_div(x, y):
                    try:
                        return x / y
                    except ZeroDivisionError:
                        return 0

                if bool(lofoverallresult):
                    if w.displaytypeid == 5:
                        lof_chk = [[0 for i in range(5)] for i in range(5)]

                        if len(lofoverallresult) != 0:
                            for x in range(len(lofoverallresult)):
                                if lofoverallresult[x][1] is not None:
                                    lof_chk[lofoverallresult[x][0]][lofoverallresult[x][1]] = lofoverallresult[x][2]

                        LofFormsDataCountKS1 = lof_chk[1][4] + lof_chk[1][3] + lof_chk[1][2] + lof_chk[1][1]
                        LofFormsDataCountKS2 = lof_chk[2][4] + lof_chk[2][3] + lof_chk[2][2] + lof_chk[2][1]
                        LofFormsDataCountKS3 = lof_chk[3][4] + lof_chk[3][3] + lof_chk[3][2] + lof_chk[3][1]
                        LofFormsDataCountKS4 = lof_chk[4][4] + lof_chk[4][3] + lof_chk[4][2] + lof_chk[4][1]
                        LofFormsDataCountALL = LofFormsDataCountKS1+LofFormsDataCountKS2+LofFormsDataCountKS3+LofFormsDataCountKS4

                        teachingsum_count4 = lof_chk[1][4] + lof_chk[2][4] + lof_chk[3][4] + lof_chk[4][4]
                        teachingsum_count3 = lof_chk[1][3] + lof_chk[2][3] + lof_chk[3][3] + lof_chk[4][3]
                        teachingsum_count2 = lof_chk[1][2] + lof_chk[2][2] + lof_chk[3][2] + lof_chk[4][2]
                        teachingsum_count1 = lof_chk[1][1] + lof_chk[2][1] + lof_chk[3][1] + lof_chk[4][1]
                        teachingsum_countks1 = lof_chk[1][4] + lof_chk[1][3] + lof_chk[1][2] + lof_chk[1][1]
                        teachingsum_countks2 = lof_chk[2][4] + lof_chk[2][3] + lof_chk[2][2] + lof_chk[2][1]
                        teachingsum_countks3 = lof_chk[3][4] + lof_chk[3][3] + lof_chk[3][2] + lof_chk[3][1]
                        teachingsum_countks4 = lof_chk[4][4] + lof_chk[4][3] + lof_chk[4][2] + lof_chk[4][1]
                        lofoverallresult_sum = [teachingsum_count4,teachingsum_count3,teachingsum_count2,teachingsum_count1]


                        teachingsum_4ks1 = zero_div(lof_chk[1][4],teachingsum_countks1)
                        teachingsum_4ks2 = zero_div(lof_chk[2][4],teachingsum_countks2)
                        teachingsum_4ks3 = zero_div(lof_chk[3][4],teachingsum_countks3)
                        teachingsum_4ks4 = zero_div(lof_chk[4][4],teachingsum_countks4)
                        teachingsum_3ks1 = zero_div(lof_chk[1][3],teachingsum_countks1)
                        teachingsum_3ks2 = zero_div(lof_chk[2][3],teachingsum_countks2)
                        teachingsum_3ks3 = zero_div(lof_chk[3][3],teachingsum_countks3)
                        teachingsum_3ks4 = zero_div(lof_chk[4][3],teachingsum_countks4)
                        teachingsum_2ks1 = zero_div(lof_chk[1][2],teachingsum_countks1)
                        teachingsum_2ks2 = zero_div(lof_chk[2][2],teachingsum_countks2)
                        teachingsum_2ks3 = zero_div(lof_chk[3][2],teachingsum_countks3)
                        teachingsum_2ks4 = zero_div(lof_chk[4][2],teachingsum_countks4)
                        teachingsum_1ks1 = zero_div(lof_chk[1][1],teachingsum_countks1)
                        teachingsum_1ks2 = zero_div(lof_chk[2][1],teachingsum_countks2)
                        teachingsum_1ks3 = zero_div(lof_chk[3][1],teachingsum_countks3)
                        teachingsum_1ks4 = zero_div(lof_chk[4][1],teachingsum_countks4)
                        teachingsum_count = teachingsum_count4+teachingsum_count3+teachingsum_count2+teachingsum_count1
                        teachingsum_4 = zero_div(teachingsum_count4,teachingsum_count)
                        teachingsum_3 = zero_div(teachingsum_count3,teachingsum_count)
                        teachingsum_2 = zero_div(teachingsum_count2,teachingsum_count)
                        teachingsum_1 = zero_div(teachingsum_count1,teachingsum_count)

                        teachingtotal_ks1 = (4*lof_chk[1][4])+(3*lof_chk[1][3])+(2*lof_chk[1][2])+(1*lof_chk[1][1])
                        teachingavg_ks1 = zero_div(teachingtotal_ks1,teachingsum_countks1)
                        teachingtotal_ks2 = (4*lof_chk[2][4])+(3*lof_chk[2][3])+(2*lof_chk[2][2])+(1*lof_chk[2][1])
                        teachingavg_ks2 = zero_div(teachingtotal_ks2,teachingsum_countks2)
                        teachingtotal_ks3 = (4*lof_chk[3][4])+(3*lof_chk[3][3])+(2*lof_chk[3][2])+(1*lof_chk[3][1])
                        teachingavg_ks3 = zero_div(teachingtotal_ks3,teachingsum_countks3)
                        teachingtotal_ks4 = (4*lof_chk[4][4])+(3*lof_chk[4][3])+(2*lof_chk[4][2])+(1*lof_chk[4][1])
                        teachingavg_ks4 = zero_div(teachingtotal_ks4,teachingsum_countks4)
                        teachingscore_all = ((4*teachingsum_count4)+(3*teachingsum_count3)+(2*teachingsum_count2)+(1*teachingsum_count1))
                        teachingsum_all = teachingsum_count4+teachingsum_count3+teachingsum_count2+teachingsum_count1
                        teachingavg_all = zero_div(teachingscore_all,teachingsum_all)
                        lofoverallresult_list.append({'lofid':w.lofid, 'descc':w.descc, 'desce':w.desce, 'displaytypeid':w.displaytypeid, 'lofoverallresult':lofoverallresult, 'lof_chk':lof_chk, 'lofoverallresult_sum':lofoverallresult_sum, 'teachingsum_4ks1':teachingsum_4ks1, 'teachingsum_4ks2':teachingsum_4ks2, 'teachingsum_4ks3':teachingsum_4ks3, 'teachingsum_4ks4':teachingsum_4ks4, 'teachingsum_3ks1':teachingsum_3ks1, 'teachingsum_3ks2':teachingsum_3ks2, 'teachingsum_3ks3':teachingsum_3ks3, 'teachingsum_3ks4':teachingsum_3ks4, 'teachingsum_2ks1':teachingsum_2ks1, 'teachingsum_2ks2':teachingsum_2ks2, 'teachingsum_2ks3':teachingsum_2ks3, 'teachingsum_2ks4':teachingsum_2ks4, 'teachingsum_1ks1':teachingsum_1ks1, 'teachingsum_1ks2':teachingsum_1ks2, 'teachingsum_1ks3':teachingsum_1ks3, 'teachingsum_1ks4':teachingsum_1ks4, 'teachingsum_4':teachingsum_4, 'teachingsum_3':teachingsum_3, 'teachingsum_2':teachingsum_2, 'teachingsum_1': teachingsum_1, 'teachingavg_ks1':teachingavg_ks1, 'teachingavg_ks2':teachingavg_ks2, 'teachingavg_ks3':teachingavg_ks3, 'teachingavg_ks4':teachingavg_ks4, 'teachingavg_all':teachingavg_all})
                    else:
                        lof_chk = [[0 for i in range(5)] for i in range(5)]

                        if len(lofoverallresult) != 0:
                            for x in range(len(lofoverallresult)):
                                if lofoverallresult[x][1] is not None:
                                    lof_chk[lofoverallresult[x][0]][lofoverallresult[x][1]] = lofoverallresult[x][2]

                        learningall = lof_chk[1][1]+lof_chk[2][1]+lof_chk[3][1]+lof_chk[4][1]
                        learningavg_ks1 = zero_div(lof_chk[1][1],LofFormsDataCountKS1)
                        learningavg_ks2 = zero_div(lof_chk[2][1],LofFormsDataCountKS2)
                        learningavg_ks3 = zero_div(lof_chk[3][1],LofFormsDataCountKS3)
                        learningavg_ks4 = zero_div(lof_chk[4][1],LofFormsDataCountKS4)
                        learningavg_all = zero_div(learningall,LofFormsDataCountALL)
                        lofoverallresult_list.append({'lofid':w.lofid, 'descc':w.descc, 'desce':w.desce, 'displaytypeid':w.displaytypeid, 'lofoverallresult':lofoverallresult, 'lof_chk':lof_chk, 'learningavg_ks1':learningavg_ks1, 'learningavg_ks2':learningavg_ks2, 'learningavg_ks3':learningavg_ks3, 'learningavg_ks4':learningavg_ks4,'learningall':learningall,'learningavg_all':learningavg_all})
                else:
                    lof_chk = [[0 for i in range(5)] for i in range(5)]
                    lofoverallresult_list.append({'lofid': w.lofid, 'descc': w.descc, 'desce': w.desce, 'displaytypeid': w.displaytypeid, 'lofoverallresult': lofoverallresult, 'lof_chk': lof_chk, 'learningavg_ks1': 0, 'learningavg_ks2': 0, 'learningavg_ks3': 0, 'learningavg_ks4': 0, 'learningall': 0, 'learningavg_all': 0})

                    #return HttpResponse("No Record Found")
            except Exception as e:
                sSQL = sSQL
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                return HttpResponse("Error line "+str(line_number)+": "+str(e)+w.lofid+ sSQL)
        context = {
            "action": action,
            "lofformschoolyear": LofFormsSchoolYear,
            "lofformoveralllist": LofFormOverallList,            
            "lofformsdatacountks1": LofFormsDataCountKS1,
            "lofformsdatacountks2": LofFormsDataCountKS2,
            "lofformsdatacountks3": LofFormsDataCountKS3,
            "lofformsdatacountks4": LofFormsDataCountKS4,
            "lofformsdatacountall": LofFormsDataCountALL,
            "lofoverallresult_list": lofoverallresult_list,
            "subject": subject,
            "displaymode": displaymode,
            "klatext": klatext,
            "sql": sSQL,
        }
    if action == "lofschoollist":
        lof_list = []
        code_temp = ''
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=lofform')
        cursor = cnxn.cursor()
        if schoollevel == "3":
            cursor.execute("exec spLOFSummary_RelatedSchool_2019_SPC_2022 '"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+str(schoollevel)+"','"+str(inspectiontype)+"','"+str(inspectortype)+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"'")
            sSQL = "exec spLOFSummary_RelatedSchool_2019_SPC_2022 '"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+str(schoollevel)+"','"+str(inspectiontype)+"','"+str(inspectortype)+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"'"
        else:
            cursor.execute("exec spLOFSummary_RelatedSchool2022 '"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+str(schoollevel)+"','"+str(inspectiontype)+"','"+str(inspectortype)+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"'")
            sSQL = "exec spLOFSummary_RelatedSchool2022 '"+str(lofyear)+"','"+str(start_date)+"','"+str(end_date)+"','"+str(schoollevel)+"','"+str(inspectiontype)+"','"+str(inspectortype)+"','"+str(klaid)+"',N'"+str(subject)+"','"+str(teachingmode)+"'"
        lof_list_temp = cursor.fetchall()
        LofKLAList = LofKLA.objects.using('lofform').filter(klaid=klaid)

        for x in lof_list_temp:
            if x.code == code_temp:
                lof_list.pop()
            if str(klaid) == "99":
                lof_list.append({'code': x.code, 'schoolNameC': x.schoolNameC, 'schoolNameE': x.schoolNameE,
                                 'SchoolType': x.SchoolType, 'esrStartDate': x.esrStartDate, 'esrEndDate': x.esrEndDate,
                                 'lofFormCount': x.lofFormCount, 'remark': x.remark, 'klaid': klaid,
                                 'lesson_count': x.lesson_count})
            else:
                if "1"+LofKLAList[0].subfocustypeid in x.code or "2"+LofKLAList[0].subfocustypeid in x.code or "FFU" in x.code or x.InspType == "ESR":
                    lof_list.append({'code':x.code, 'schoolNameC':x.schoolNameC, 'schoolNameE':x.schoolNameE, 'SchoolType':x.SchoolType, 'esrStartDate':x.esrStartDate, 'esrEndDate':x.esrEndDate, 'lofFormCount':x.lofFormCount, 'remark':x.remark, 'klaid':klaid, 'lesson_count':x.lesson_count})
            code_temp = x.code


        cursor.execute("exec spLOFCountAverageBySchool '"+str(start_date)+"','"+str(end_date)+"','"+str(inspectiontype)+"','"+schoollevel+"'")
        lof_list2 = cursor.fetchall()
        context = {
            "action": action,
            "lof_list": lof_list,
            "lof_list2": lof_list2,
            "klaid": klaid,
            "subject": subject,
            "displaymode": displaymode,
            "klatext": klatext,
            "sql": sSQL,
        }
    if action == "lofstatistic":

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=lofform')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_LOFForm_SchoolType_Lesson_Upload")
        schoolLOFCountList = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionList_School_Count")
        schoolCountList = cursor.fetchall()

        context = {
            "action": action,
            "lofyear": lofyear,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "inspectortype": inspectortype,
            "klaid": klaid,
            "subject": subject,
            "teachingmode": teachingmode,
            "displaymode": displaymode,
            "schoolcountlist": schoolCountList,
            "schoollofcountlist": schoolLOFCountList,
        }
    return render(request, "report_template/lofsummary_response.html", context)

def formBReport(request):
    if not request.session.get('post'): return redirect('')
    year = request.POST.get('year')
    schoollevel = request.GET.get('schoollevel')
    years = ESRschools.objects.using('sqp').filter(insptype='ESR').order_by('-esryear').values('esryear').distinct()
    if years:
        year = years[0]['esryear']
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=focus')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_FocusSubType_Year where focusYear = '" + year + "'")
    focussubtypes = cursor.fetchall()
    #focussubtypes = Focussubtypes.objects.using('focus').order_by('sequence')

    action = request.POST.get('action')

    accessid = 125
    request.session['accessid'] = accessid
    cnxn_menu = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=qadind')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where post = '" + request.session.get('post') + "'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('sqp').get(postdesc=request.session.get('post'), year=currentschoolyear(), isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='sqp')
    pageviewlog(accessid, request.session.get('loginid'), request.session.get('post'), request.session.get('post_org'))
    context = {
        "action": action,
        "years": years,
        "focussubtypes": focussubtypes,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "report_template/formBReport.html", context)

@csrf_exempt
def formBReport_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    schoollevel = request.POST.get('schoollevel')
    inspectiontype = request.POST.get('inspectiontype')
    subject = request.POST.get('subject')
    focustype = request.POST.get('focustype')
    reporttype = request.POST.get('reporttype')
    part = request.POST.get('part')
    loginid = request.POST.get('loginid')
    status = request.POST.get('status')
    displaymode = request.POST.get('displaymode')
    if focustype == "":
        focustype = 1

    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "user_year": year,
            "team_list": team_list,
        }

    if action == "subject_list":
        subject_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=focus')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_FocusSubType_Year where focusYear = '" + str(year) + "'")
        subject_list = cursor.fetchall()

        context = {
            "action": action,
            "user_year": year,
            "subject_list": subject_list,
        }

    if action == "menutab":
        context = {
            "action": action,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionList_SchoolType_School_Count where year_name = '" + year + "'")
        schoolTypeCountList = cursor.fetchall()
        cursor.execute("select * from V_InpsectionList_FocusType_School_Count where year_name = '" + year + "' order by sequence")
        focusTypeCountList = cursor.fetchall()

        context = {
            "action": action,
            "selectedyear": year,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
            "schooltypecountlist": schoolTypeCountList,
            "focustypecountlist": focusTypeCountList,
        }
    if action == "report":
        if inspectiontype == "":
            #eformpage = EformPage.objects.using('esrform').filter(year=year, insptype__in=["ESR", "FI", "CR", "SR"], formpage="supp_note_b_form", part=part, pagebase=2).order_by('sequence')
            if part == "partc":
                eformpage = EformPage.objects.using('esrform').filter(year=year, formpage="supp_note_b_form", part=part, pagebase=2, pageid__lt="c3").order_by('sequence')
            else:
                eformpage = EformPage.objects.using('esrform').filter(year=year, formpage="supp_note_b_form", part=part, pagebase=2).order_by('sequence')
            #duplicate_page_ids = eformpage.values('pageid').annotate(count=Count('pageid')).filter(count__gt=1).values_list('pageid', flat=True)
            #eformpage.filter(pageid__in=duplicate_page_ids).delete()
            #eformpage.order_by('sequence')
        elif inspectiontype == "ESR" or inspectiontype == "CR":
            eformpage = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype, formpage="supp_note_b_form", part=part, pagebase=2).order_by('sequence')
        else:
            if subject == "99":
                eformpage = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype, formpage="supp_note_b_form", part=part, pagebase=2, schooltypeid="A", pageid__lt="c3").order_by('sequence')
            else:
                if subject == "MA":
                    eformpage = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype, formpage="supp_note_b_form", part=part, pagebase=2, focustypeid=focustype, subfocustypeid=subject, schooltypeid__in=['P','S','A']).order_by('sequence')
                else:
                    eformpage = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype, formpage="supp_note_b_form", part=part, pagebase=2, focustypeid=focustype, subfocustypeid=subject, schooltypeid="A").order_by('sequence')
        eformpage_distinct = []
        seen_page_ids = set()
        for u in eformpage:
            temp_id = u.pageid+u.readtable
            if temp_id not in seen_page_ids:
                eformpage_distinct.append(u)
                seen_page_ids.add(temp_id)
        eformpage = eformpage_distinct
        context = {
            "action": action,
            "eformpage": eformpage,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "supp_note_b_form":
        pagetype = request.POST.get('pagetype')
        tabname = request.POST.get('tabname')
        dbName = request.POST.get('dbname').lower()
        tableName = request.POST.get('tablename').lower()

        strWhereFieldName = "esrFormID"
        if dbName == "esrform": strWhereFieldName = "esrFormID"
        if dbName == "klaform": strWhereFieldName = "klaFormID"
        if dbName == "focus": strWhereFieldName = "schoolID"
        if dbName == "cr": strWhereFieldName = "esrFormID"
        if dbName == "sqp": strWhereFieldName = "schoolID"
        if dbName == "esrform" and tableName == "tblFIE05": strWhereFieldName = "schoolID"
        if dbName == "schoolmaster": strWhereFieldName = "sdpFormID"

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate_SDP_Info '"+inspectiontype+"'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        report_list = []
        data_list = []
        field_list = []
        formid_list = []

        if reporttype == "raw":
            for z in "123678":
                if pagetype == "#a2"+str(z):
                    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=schoolmaster')
                    cursor = cnxn.cursor()
                    cursor.execute("getStructure_2019_WITHSDP 'SDP0"+str(z)+"', 'A', 2, 'SDP', 2014")
                    field_list = cursor.fetchall()
            if pagetype == "#a311" or pagetype == "#a312" or pagetype == "#a313" or pagetype == "#a314":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                cursor = cnxn.cursor()
                if pagetype == "#a311": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030101', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#a312": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030102', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#a313": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030104', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#a314": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030105', 'A', 2, 'X', '', "+str(year))
                field_list = cursor.fetchall()
            if pagetype == "#b1" or pagetype == "#b2" or pagetype == "#b3" or pagetype == "#b4" or pagetype == "#b5" or pagetype == "#b6" or pagetype == "#b7" or pagetype == "#b8" or pagetype == "#b9" or pagetype == "#b10" or pagetype == "#b110" or pagetype == "#b12" or pagetype == "#b13" or pagetype == "#b14" or pagetype == "#b15":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                cursor = cnxn.cursor()
                if subject != "MA":
                    cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR040101', 'A', 2, 'X', 'X', "+str(year))
                else:
                    cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR040101', 'A', 2, 'X', 'X', "+str(year))
                field_list = cursor.fetchall()
            if pagetype == "#b11" or pagetype == "#b21" or pagetype == "#b41" or pagetype == "#b41" or pagetype == "#b51" or pagetype == "#b61" or pagetype == "#b62" or pagetype == "#b71" or pagetype == "#b81" or pagetype == "#b101" or pagetype == "#b111" or pagetype == "#b131" or pagetype == "#b141" or pagetype == "#b151":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                cursor = cnxn.cursor()
                if pagetype == "#b11": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR09', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b21": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR17', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b41": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR10', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b51": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR11', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b61": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR12', 'A', 1, 'X', '', "+str(year))
                if pagetype == "#b62": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR18', 'A', 1, 'X', '', "+str(year))
                if pagetype == "#b71": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR13', 'A', 1, 'X', '', "+str(year))
                if pagetype == "#b81": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR14', 'A', 1, 'X', '', "+str(year))
                if pagetype == "#b101": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR15', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b111": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR16', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b131": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR19', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b141": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR20', 'A', 2, 'X', '', "+str(year))
                if pagetype == "#b151": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR21', 'A', 2, 'X', '', "+str(year))
                field_list = cursor.fetchall()
            if pagetype == "#c":
                if subject == "MA":
                    field_list = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype,formpage="supp_note_b_form", part=part,pagebase=2, focustypeid=focustype,subfocustypeid=subject, schooltypeid__in=['P','S','A']).exclude(pageid__in=['c', 'c1', 'c12', 'c2']).order_by('sequence')
                else:
                    field_list = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype,formpage="supp_note_b_form", part=part,pagebase=2, focustypeid=focustype,subfocustypeid=subject,schooltypeid="A").exclude(pageid__in=['c', 'c1', 'c12', 'c2']).order_by('sequence')
            if pagetype == "#c1" or pagetype == "#c12" or pagetype == "#c2":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=klaform')
                cursor = cnxn.cursor()
                if pagetype == "#c1": cursor.execute("getStructure_FORM_LEVEL_DATA 'C1201', 'A', 3, 'X', '', 'C12', "+str(year))
                if pagetype == "#c12": cursor.execute("getStructure_FORM_LEVEL_DATA 'C1202', 'A', 3, 'X', '', 'C12', "+str(year))
                if pagetype == "#c2": cursor.execute("getStructure_FORM_LEVEL_DATA 'C1202', 'A', 4, 'X', '', 'C1202', "+str(year))
                field_list = cursor.fetchall()
            if pagetype[:3] == "#c3":
                tableArray = tableName.split("_")
                readtable = tableArray[1]
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=klaform')
                cursor = cnxn.cursor()
                if subject == "C": part = "CHI"
                if subject == "E": part = "ENG"
                if subject == "MA": part = "MATH"
                if subject == "SC": part = "SCI"
                if subject == "TE": part = "TE"
                if subject == "PH": part = "PSHE"
                if subject == "AR": part = "ART"
                if subject == "PE": part = "PE"
                if subject == "GS": part = "GS"
                if subject == "LS": part = "LS"
                if subject == "CS": part = "CS"
                schooltype = "A"
                if subject == "TE": schooltype = "S"
                if subject == "MA": schooltype = "S"
                if subject == "MA":
                    cursor.execute("getStructure_FORM_LEVEL_DATA '"+readtable+"', '"+schooltype+"', 1, 'X', '', '"+part+"S', "+str(year))
                else:
                    cursor.execute("getStructure_FORM_LEVEL_DATA '"+readtable+"', '"+schooltype+"', 1, 'X', '', '"+part+"', "+str(year))
                field_list = cursor.fetchall()
            if pagetype[:2] == "#d":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=klaform')
                cursor = cnxn.cursor()
                part = "TBSS"
                tableArray = tableName.split("_")
                readtable = tableArray[2]
                readtable = "TB0" + readtable.replace('d', '')
                cursor.execute("getStructure_FORM_LEVEL_DATA '"+readtable+"', 'A', 1, 'X', '', '"+part+"', "+str(year))
                field_list = cursor.fetchall()
            if pagetype[:2] == "#e":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=klaform')
                cursor = cnxn.cursor()
                part = "TBIKP"
                tableArray = tableName.split("_")
                readtable = tableArray[2]
                readtable = "TB0" + readtable.replace('e', '')
                cursor.execute("getStructure_FORM_LEVEL_DATA '"+readtable+"', 'A', 1, 'X', '', '"+part+"', "+str(year))
                field_list = cursor.fetchall()
            if pagetype[:2] == "#f":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=klaform')
                cursor = cnxn.cursor()
                part = "TBNE"
                tableArray = tableName.split("_")
                readtable = tableArray[2]
                if readtable.replace('f','') > "1":
                    readtable = "TB11010"+str(int(readtable.replace('f',''))+1)
                else:
                    readtable = "TB11010" + readtable.replace('f', '')
                cursor.execute("getStructure_FORM_LEVEL_DATA '"+readtable+"', 'A', 1, 'X', '', '"+part+"', "+str(year))
                field_list = cursor.fetchall()

            sSQL = ""
            sql1 = ""
            readtable = ""
            debug = focustype
            for w in inspection_list:
                try:
                    checked = 1
                    show_all = "Y"
                    formid = ""
                    if dbName == "esrform": formid = w.SchoolID + w.esrYear
                    if dbName == "klaform": formid = w.SchoolID + w.esrYear
                    if dbName == "focus": formid = w.SchoolID + w.esrYear
                    if dbName == "cr": formid = w.SchoolID + w.esrYear
                    insptype = w.InspType
                    schooltype = w.schoolTypeID
                    if w.InspType == "ESR" and w.code[:2] == "EX":
                        schooltype = "SP"
                    if w.InspType == "FI" and w.code[:1] == "3":
                        schooltype = "SP"
                    if w.InspType == "ESR":
                        esrform = ESRForms.objects.using('esrform').filter(esrformid=formid)
                        formstatus = esrform.first().status if esrform.exists() else None
                    if w.InspType == "FI":
                        klaform = KLAForms.objects.using('klaform').filter(klaformid=formid)
                        formstatus = klaform.first().status if klaform.exists() else None

                    if checked == 1:
                        if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                            checked = 0
                        if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                            checked = 0
                    if schoollevel != "" and checked == 1:
                        if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                            checked = 0
                        if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                            checked = 0
                        if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                            checked = 0
                    if inspectiontype != "" and checked == 1:
                        if w.InspType != inspectiontype:
                            checked = 0
                    if subject != "99" and checked == 1:
                        if str(w.subcode) != subject:
                            checked = 0
                        if str(w.focusTypeID) != focustype:
                            checked = 0
                    if part >= "partc" and checked == 1:
                        if w.InspType  == "ESR":
                            checked = 0
                    if part == "partc" and checked == 1:
                        if str(w.focusTypeID) != "1":
                            checked = 0
                    if part == "partd" and checked == 1:
                        if str(w.focusTypeID) != "34":
                            checked = 0
                    if part == "parte" and checked == 1:
                        if str(w.focusTypeID) != "36":
                            checked = 0
                    if part == "partf" and checked == 1:
                        if str(w.focusTypeID) != "38":
                            checked = 0
                    if loginid != "" and checked == 1:
                        if str(w.LoginID) != loginid:
                            checked = 0
                    if status != "" and checked == 1:
                        if str(formstatus) != status:
                            checked = 0
                    if displaymode == "1" and w.SchoolID[:1] == "9":
                        checked = 0
                    if displaymode == "2" and w.SchoolID[:1] != "9":
                        checked = 0
                    if checked == 1:
                        field_length = 0
                        if pagetype == "#a" or pagetype == "#a2":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                            cursor = cnxn.cursor()
                            cursor.execute("exec spC12InfoInsp '" + formid + "','" + insptype + "'")
                            data_list = cursor.fetchall()
                            show_all = "Y"
                        if pagetype == "#a11":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
                            cursor = cnxn.cursor()
                            cursor.execute("select * from V_Inspection_PI_Rating where schoolid = '" + w.SchoolID + "' and esryear = '" + str(year) + "'")
                            data_list = cursor.fetchall()
                            show_all = "Y"
                        if pagetype == "#a12" or pagetype == "#a13":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select * from " + tableName + " where esrformid = '" + formid + "'")
                            data_list = cursor.fetchall()
                            #data_list = [record for record in data_list if all(field is not None and field != '' for field in record[1:5])]
                            show_all = "N"
                        if pagetype == "#a21" or pagetype == "#a22" or pagetype == "#a23" or pagetype == "#a26" or pagetype == "#a27" or pagetype == "#a28":
                            field_string = ""
                            for y in field_list:
                                field_string = field_string + y.levelID + ","
                            field_length = len(field_list)
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select top 1 " + field_string[:-1] + " from " + tableName + " where sdpformid = '" + w.SchoolID + "' order by sdptype desc")
                            data_list = cursor.fetchall()
                            sSQL = "select " + field_string[:-1] + " from " + tableName + " where sdpformid = '" + w.SchoolID + "'"
                            show_all = "Y"
                        if pagetype == "#a311" or pagetype == "#a312" or pagetype == "#a313" or pagetype == "#a314":
                            field_string = ""
                            field_type = ""
                            for y in field_list:
                                field_string = field_string + y.levelID + ","
                            field_length = len(field_list)
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select " + field_string[:-1] + " from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                            data_list = cursor.fetchall()
                            show_all = "N"
                        if pagetype == "#b":
                            debug = pagetype
                            field_string = ""
                            field_type = ""
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select * from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                            data_list = cursor.fetchall()
                            temp_list = []
                            BE1 = '0'
                            BE2 = '0'
                            BE3 = '0'
                            BE4 = '0'
                            BE5 = '0'
                            BE6 = '0'
                            BE7 = '0'
                            BE8 = '0'
                            BE9 = '0'
                            BE10 = '0'
                            BE11 = '0'
                            BE12 = '0'
                            BE13 = '0'
                            BE14 = '0'
                            BE15 = '0'
                            for z in data_list:
                                for x in range(1, 12):
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0A'): BE1 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0B'): BE2 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0C'): BE3 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0D'): BE4 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0E'): BE5 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0F'): BE6 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0G'): BE7 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0H'): BE8 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0I'): BE9 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0J'): BE10 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0K'): BE11 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0L'): BE12 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0M'): BE13 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0N'): BE14 = 1
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0O'): BE15 = 1
                            temp_list.append({'BE1':BE1, 'BE2':BE2, 'BE3':BE3, 'BE4':BE4, 'BE5':BE5, 'BE6':BE6, 'BE7':BE7, 'BE8':BE8, 'BE9':BE9, 'BE10':BE10, 'BE11':BE11, 'BE12':BE12, 'BE13':BE13, 'BE14':BE14, 'BE15':BE15})
                            data_list = temp_list
                            sSQL = "select * from " + tableName + " where esrformid = '" + formid + "'"
                            show_all = "Y"
                        if pagetype == "#b1" or pagetype == "#b2" or pagetype == "#b3" or pagetype == "#b4" or pagetype == "#b5" or pagetype == "#b6" or pagetype == "#b7" or pagetype == "#b8" or pagetype == "#b9" or pagetype == "#b10" or pagetype == "#b110" or pagetype == "#b12" or pagetype == "#b13" or pagetype == "#b14" or pagetype == "#b15":
                            field_string = ""
                            field_type = ""
                            for y in field_list[1:]:
                                field_string = field_string + y.levelID + ","
                            field_length = len(field_list)
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select * from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                            data_list = cursor.fetchall()
                            BEreport = pagetype.replace('#b', '')
                            temp_list = []
                            for z in data_list:
                                BErecord = ""
                                for x in range(1, 12):
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0A') and BEreport == '1': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0B') and BEreport == '2': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0C') and BEreport == '3': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0D') and BEreport == '4': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0E') and BEreport == '5': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0F') and BEreport == '6': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0G') and BEreport == '7': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0H') and BEreport == '8': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0I') and BEreport == '9': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0J') and BEreport == '10': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0K') and BEreport == '110': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0L') and BEreport == '12': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0M') and BEreport == '13': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0N') and BEreport == '14': BErecord = 'ESR0401' + str(x).zfill(2)
                                    if eval('z.ESR0401' + str(x).zfill(2) + '0O') and BEreport == '15': BErecord = 'ESR0401' + str(x).zfill(2)
                                field_string = field_string.replace('ESR040101', BErecord)
                            #temp_list.append({'BE1':BE1, 'BE2':BE2, 'BE3':BE3, 'BE4':BE4, 'BE5':BE5, 'BE6':BE6, 'BE7':BE7, 'BE8':BE8, 'BE9':BE9, 'BE10':BE10, 'BE11':BE11, 'BE12':BE12, 'BE13':BE13, 'BE14':BE14, 'BE15':BE15})
                            #data_list = temp_list
                            if BErecord == "":
                                data_list = []
                            else:
                                cursor.execute("select " + field_string[:-1] + " from " + tableName + " where esrformid = '" + formid + "'")
                                data_list = cursor.fetchall()
                                sql1 = sql1 + "select " + field_string[:-1] + " from " + tableName + " where esrformid = '" + formid + "'<br>"
                            show_all = "N"
                        if pagetype == "#b11" or pagetype == "#b21" or pagetype == "#b41" or pagetype == "#b51" or pagetype == "#b61" or pagetype == "#b62" or pagetype == "#b71" or pagetype == "#b81" or pagetype == "#b101" or pagetype == "#b111" or pagetype == "#b131" or pagetype == "#b141" or pagetype == "#b151":
                            field_string = ""
                            field_type = ""
                            for y in field_list:
                                field_string = field_string + y.levelID + ","
                            field_length = len(field_list)
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select " + field_string[:-1] + " from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                            data_list = cursor.fetchall()
                            sSQL = "select " + field_string[:-1] + " from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'"
                            show_all = "N"
                        if pagetype == "#c" or pagetype[:2] == "#d" or pagetype[:2] == "#e" or pagetype[:2] == "#f":
                            debug = pagetype
                            field_string = ""
                            field_type = ""
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select * from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                            data_list = cursor.fetchall()
                            temp_list = []
                            count = 0
                            variable_list = {}
                            for z in field_list:
                                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + z.readdb)
                                cursor = cnxn.cursor()
                                cursor.execute("select * from " + z.readtable + " where " + strWhereFieldName + " = '" + formid + "'")
                                data_list = cursor.fetchall()
                                number_of_records = len(data_list)
                                count = count + 1
                                variable_list['CD' + str(count)] = number_of_records
                            temp_list.append(variable_list)
                            data_list = temp_list
                            show_all = "Y"
                        if pagetype == "#c1" or pagetype == "#c12" or pagetype == "#c2":
                            field_string = ""
                            field_type = ""
                            for y in field_list:
                                field_string = field_string + y.levelID + ","
                            field_length = len(field_list)
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select " + field_string[:-1] + " from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                            data_list = cursor.fetchall()
                            sql1 = "select " + field_string[:-1] + " from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'"
                            show_all = "N"
                        if pagetype[:3] == "#c3" or pagetype[:3] == "#e1":
                            field_string = ""
                            field_type = ""
                            for y in field_list:
                                field_string = field_string + y.levelID + ","
                            field_length = len(field_list)
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database='+dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select " + field_string[:-1] + " from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                            data_list = cursor.fetchall()
                            sql1 = "select " + field_string[:-1] + " from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'"
                            show_all = "N"

                        #cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName.lower())
                        #cursor = cnxn.cursor()
                        #cursor.execute("select * from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'")
                        #sql1 = "select * from " + tableName + " where " + strWhereFieldName + " = '" + formid + "'"
                        #data_list = cursor.fetchall()
                        if data_list and show_all == "N" or show_all == "Y":
                            report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'SchoolType': schooltype, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus, 'endofsdp': w.endOfSdp, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
                except Exception as e:
                    sSQL = 'N/A'
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno
                    sSQL = "Error linexx "+str(line_number)+": "+str(e)+sSQL

        if reporttype == "pre":
            sSQL = ""
            sql1 = ""
            readtable = ""
            debug = focustype
            for w in inspection_list:
                try:
                    checked = 1
                    show_all = "Y"
                    formid = ""
                    if dbName == "esrform": formid = w.SchoolID + w.esrYear
                    if dbName == "klaform": formid = w.SchoolID + w.esrYear
                    if dbName == "focus": formid = w.SchoolID + w.esrYear
                    if dbName == "cr": formid = w.SchoolID + w.esrYear
                    insptype = w.InspType
                    schooltype = w.schoolTypeID
                    if w.InspType == "ESR" and w.code[:2] == "EX":
                        schooltype = "SP"
                    if w.InspType == "FI" and w.code[:1] == "3":
                        schooltype = "SP"
                    if w.InspType == "ESR":
                        esrform = ESRForms.objects.using('esrform').filter(esrformid=formid)
                        formstatus = esrform.first().status if esrform.exists() else None
                    if w.InspType == "FI":
                        klaform = KLAForms.objects.using('klaform').filter(klaformid=formid)
                        formstatus = klaform.first().status if klaform.exists() else None

                    if checked == 1:
                        if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                            checked = 0
                        if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                            checked = 0
                    if schoollevel != "" and checked == 1:
                        if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                            checked = 0
                        if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                            checked = 0
                        if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                            checked = 0
                        if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                            checked = 0
                    if inspectiontype != "" and checked == 1:
                        if w.InspType != inspectiontype:
                            checked = 0
                    if subject != "99" and checked == 1:
                        if str(w.subcode) != subject:
                            checked = 0
                        if str(w.focusTypeID) != focustype:
                            checked = 0
                    if part >= "partc" and checked == 1:
                        if w.InspType  == "ESR":
                            checked = 0
                    if part == "partc" and checked == 1:
                        if str(w.focusTypeID) != "1":
                            checked = 0
                    if part == "partd" and checked == 1:
                        if str(w.focusTypeID) != "34":
                            checked = 0
                    if part == "parte" and checked == 1:
                        if str(w.focusTypeID) != "36":
                            checked = 0
                    if part == "partf" and checked == 1:
                        if str(w.focusTypeID) != "38":
                            checked = 0
                    if loginid != "" and checked == 1:
                        if str(w.LoginID) != loginid:
                            checked = 0
                    if status != "" and checked == 1:
                        if str(formstatus) != status:
                            checked = 0
                    if displaymode == "1" and w.SchoolID[:1] == "9":
                        checked = 0
                    if displaymode == "2" and w.SchoolID[:1] != "9":
                        checked = 0
                    if checked == 1:
                        formid_list.append(formid)
                        field_length = 0
                        if pagetype == "#a" or pagetype == "#a2":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                            cursor = cnxn.cursor()
                            cursor.execute("exec spC12InfoInsp '" + formid + "','" + insptype + "'")
                            data_list = cursor.fetchall()
                            show_all = "Y"
                            report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'SchoolType': schooltype, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus, 'endofsdp': w.endOfSdp, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
                        if pagetype == "#a11":
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
                            cursor = cnxn.cursor()
                            cursor.execute("select * from V_Inspection_PI_Rating where schoolid = '" + w.SchoolID + "' and esryear = '" + str(year) + "'")
                            data_list = cursor.fetchall()
                            report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'SchoolType': schooltype, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus, 'endofsdp': w.endOfSdp, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
                        if pagetype == "#c":
                            if subject == "MA":
                                field_list = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype, formpage="supp_note_b_form", part=part, pagebase=2, focustypeid=focustype, subfocustypeid=subject, schooltypeid__in=['P', 'S']).exclude(pageid__in=['c', 'c1', 'c12', 'c2']).order_by('sequence')
                            else:
                                field_list = EformPage.objects.using('esrform').filter(year=year, insptype=inspectiontype, formpage="supp_note_b_form", part=part, pagebase=2, focustypeid=focustype, subfocustypeid=subject, schooltypeid="A").exclude(pageid__in=['c', 'c1', 'c12', 'c2']).order_by('sequence')
                            debug = pagetype
                            field_string = ""
                            field_type = ""
                            temp_list = []
                            count = 0
                            variable_list = {}
                            for z in field_list:
                                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr( settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + z.readdb)
                                cursor = cnxn.cursor()
                                cursor.execute("select * from " + z.readtable + " where " + strWhereFieldName + " = '" + formid + "'")
                                data_list = cursor.fetchall()
                                number_of_records = len(data_list)
                                count = count + 1
                                variable_list['CD' + str(count)] = number_of_records
                            temp_list.append(variable_list)
                            data_list = temp_list
                            show_all = "Y"
                            if data_list and show_all == "N" or show_all == "Y":
                                report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'SchoolType': schooltype, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus, 'endofsdp': w.endOfSdp, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
                except Exception as e:
                    sSQL = 'N/A'
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno
                    sSQL = "Error linexx "+str(line_number)+": "+str(e)+sSQL
            if pagetype == "#a12" or pagetype == "#a13" or pagetype == "#a311" or pagetype == "#a312" or pagetype == "#a313" or pagetype == "#a314" or pagetype == "#a314" or pagetype == "#b21" or pagetype == "#b51" or pagetype == "#b61" or pagetype == "#b111" or pagetype == "#b131" or pagetype == "#b141" or pagetype == "#b151":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                cursor = cnxn.cursor()
                if pagetype == "#a12": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR0102', 'A', 2, '', '', "+str(year))
                if pagetype == "#a13": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR0103', 'A', 2, '', '', "+str(year))
                if pagetype == "#a311": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030101', 'A', 1, '', '', "+str(year))
                if pagetype == "#a312": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030102', 'A', 1, '', '', "+str(year))
                if pagetype == "#a313": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030104', 'A', 1, '', '', "+str(year))
                if pagetype == "#a314": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR030105', 'A', 1, '', '', "+str(year))
                if pagetype == "#b21": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR17', 'A', 1, '', '', "+str(year))
                if pagetype == "#b51": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR11', 'A', 1, '', '', "+str(year))
                if pagetype == "#b61": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR12', 'A', 1, '', '', "+str(year))
                if pagetype == "#b111": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR16', 'A', 1, '', '', "+str(year))
                if pagetype == "#b131": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR19', 'A', 1, '', '', "+str(year))
                if pagetype == "#b141": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR20', 'A', 1, '', '', "+str(year))
                if pagetype == "#b151": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR21', 'A', 1, '', '', "+str(year))
                field_list = cursor.fetchall()
                field_length = len(formid_list)
                for y in field_list:
                    data_list = []
                    if y.answerTypeID == 1:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        sql1 = "select SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list
                        data_list = cursor.fetchall()
                    if y.answerTypeID == 2:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        temp_list = cursor.fetchall()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        temp_list = temp_list + cursor.fetchall()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 2 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        data_list = temp_list + cursor.fetchall()
                    if y.answerTypeID == 9:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        cursor.execute("select c.SchoolNameC, c.code, a."+y.levelID+" as value from " + tableName + " a INNER JOIN SQP.dbo.V_InspectionList c ON substring(a.esrFormID,1,12) = c.schoolID and substring(a.esrFormID,13,4) = c.esrYear where " + strWhereFieldName + " in " + formid_list+ " and "+y.levelID+" IS NOT NULL and "+y.levelID+" not like '<p><br></p>'")
                        sql1 = "select "+y.levelID+" from " + tableName + " where " + strWhereFieldName + " in " + formid_list+ " and "+y.levelID+" IS NOT NULL and "+y.levelID+" not like '<p><br></p>'"
                        data_list = cursor.fetchall()
                    report_list.append({'levelid': y.levelID, 'levelbase': y.levelBase, 'fieldnamec': y.levelDescC, 'fieldnamee': y.levelDescE, 'year': y.c12year, 'answertypeid': y.answerTypeID, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
            if pagetype == "#b" or pagetype == "#b1" or pagetype == "#b2" or pagetype == "#b3" or pagetype == "#b4" or pagetype == "#b5" or pagetype == "#b6" or pagetype == "#b7" or pagetype == "#b8" or pagetype == "#b9" or pagetype == "#b10" or pagetype == "#b11" or pagetype == "#b110" or pagetype == "#b12" or pagetype == "#b13" or pagetype == "#b14" or pagetype == "#b15":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=esrform')
                cursor = cnxn.cursor()
                if pagetype in "#b, #b2, #b5, #b6, #b11, #b12, #b13, #b14, #b15": cursor.execute("getStructure_FORM_LEVEL_DATA 'ESR040101', 'A', 2, '', '', "+str(year))
                field_list = cursor.fetchall()
                field_length = len(formid_list)
                number = pagetype.replace("#b","")
                for y in field_list:
                    data_list = []
                    temp_list = []
                    total_temp = 0
                    total_value_temp = 0
                    count_1_temp = 0
                    count_0_temp = 0
                    BElevelidAll = ""
                    for z in range(1,13):
                        if number == "":
                            BElevelid = "''"
                        else:
                            letter = chr(ord('A') + int(number) - 1)
                            BElevelid = "ESR0401" + str(z).zfill(2) + "0" + letter
                        levelid_temp = y.levelID
                        levelid = levelid_temp.replace("ESR040101","ESR0401"+str(z).zfill(2))
                        #levelid = levelid_temp
                        if y.answerTypeID == 1:
                            #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                            formid_list = str(formid_list).replace("[","(").replace("]",")")
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                            cursor = cnxn.cursor()
                            if number == "":
                                BElevelidAll = "ESR0401" + str(z).zfill(2) + "0A = 1 or ESR0401" + str(z).zfill(2) + "0B = 1 or ESR0401" + str(z).zfill(2) + "0C = 1 or ESR0401" + str(z).zfill(2) + "0D = 1 or ESR0401" + str(z).zfill(2) + "0E = 1 or ESR0401" + str(z).zfill(2) + "0F = 1 or ESR0401" + str(z).zfill(2) + "0G = 1 or ESR0401" + str(z).zfill(2) + "0H = 1 or ESR0401" + str(z).zfill(2) + "0I = 1 or ESR0401" + str(z).zfill(2) + "0J = 1 or ESR0401" + str(z).zfill(2) + "0K = 1 or ESR0401" + str(z).zfill(2) + "0L = 1 or ESR0401" + str(z).zfill(2) + "0M = 1 or ESR0401" + str(z).zfill(2) + "0N = 1 or ESR0401" + str(z).zfill(2) + "0O = 1"
                                cursor.execute("select COUNT(*) AS total, COUNT(" + levelid + ") AS total_value, ISNULL(SUM(CASE WHEN " + levelid + " = 1 THEN 1 ELSE 0 END),0) AS count_1, ISNULL(SUM(CASE WHEN " + levelid + " IS NULL or " + levelid + " = 0 THEN 1 ELSE 0 END), 0) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list + " and (" + BElevelidAll + ")")
                            else:
                                cursor.execute("select COUNT(*) AS total, COUNT("+levelid+") AS total_value, ISNULL(SUM(CASE WHEN "+levelid+" = 1 THEN 1 ELSE 0 END),0) AS count_1, ISNULL(SUM(CASE WHEN "+levelid+" IS NULL or "+levelid+" = 0 THEN 1 ELSE 0 END), 0) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list + " and " + BElevelid + " = 1")
                            sql1 = "select COUNT(*) AS total, COUNT("+levelid+") AS total_value, SUM(CASE WHEN "+levelid+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+levelid+" IS NULL or "+levelid+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list + " and " + BElevelid + " = 1"
                            temp_list = cursor.fetchall()
                            for t in temp_list:
                                total_temp = total_temp + t.total
                                total_value_temp = total_value_temp + t.total_value
                                count_1_temp = count_1_temp + t.count_1 if t.count_1 is not None else 0
                                count_0_temp = count_0_temp + t.count_0 if t.count_0 is not None else 0
                            if z == 12: data_list.append({'total':total_temp,'total_value':total_value_temp,'count_1':count_1_temp,'count_0':count_0_temp})
                        if y.answerTypeID == 9:
                            #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                            formid_list = str(formid_list).replace("[","(").replace("]",")")
                            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                            cursor = cnxn.cursor()
                            cursor.execute("select c.SchoolNameC, c.code, a." + levelid + " as value, " + BElevelid + " as be from " + tableName + " a INNER JOIN SQP.dbo.V_InspectionList c ON substring(a.esrFormID,1,12) = c.schoolID and substring(a.esrFormID,13,4) = c.esrYear where " + strWhereFieldName + " in " + formid_list + " and " + levelid + " IS NOT NULL and " + levelid + " not like '<p><br></p>'")
                            sql1 = "select c.SchoolNameC, c.code, a."+levelid+" as value, a."+BElevelid+" as be from " + tableName + " a INNER JOIN SQP.dbo.V_InspectionList c ON substring(a.esrFormID,1,12) = c.schoolID and substring(a.esrFormID,13,4) = c.esrYear where " + strWhereFieldName + " in " + formid_list+ " and "+levelid+" IS NOT NULL and "+levelid+" not like '<p><br></p>'"
                            temp_list = cursor.fetchall()
                            data_list = data_list + temp_list
                            #data_list = cursor.fetchall()
                    report_list.append({'levelid': y.levelID, 'levelbase': y.levelBase, 'fieldnamec': y.levelDescC, 'fieldnamee': y.levelDescE, 'year': y.c12year, 'answertypeid': y.answerTypeID, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
            if pagetype == "#c1" or pagetype == "#c12" or pagetype == "#c2":
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=klaform')
                cursor = cnxn.cursor()
                if pagetype == "#c1": cursor.execute("getStructure_FORM_LEVEL_DATA 'C1201', 'A', 1, '', '', 'C12', "+str(year))
                if pagetype == "#c12": cursor.execute("getStructure_FORM_LEVEL_DATA 'C1202', 'A', 3, '', '', 'C12', "+str(year))
                if pagetype == "#c2": cursor.execute("getStructure_FORM_LEVEL_DATA 'C1202', 'A', 4, '', '', 'C1202', "+str(year))
                field_list = cursor.fetchall()
                field_length = len(formid_list)
                for y in field_list:
                    data_list = []
                    if y.answerTypeID == 1:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        sql1 = "select SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list
                        data_list = cursor.fetchall()
                    if y.answerTypeID == 4:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        for w in range(4, 0, -1):
                            sql1 = "select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = " + str(w) + " THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list
                            cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = " + str(w) + " THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                            temp_list = (cursor.fetchall())
                            data_list.append(temp_list)
                    if y.answerTypeID == 9:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        sql1 = "select c.SchoolNameC, c.code, a."+y.levelID+" as value from " + tableName + " a INNER JOIN SQP.dbo.V_InspectionList c ON substring(a.klaFormID,1,12) = c.schoolID and substring(a.klaFormID,13,4) = c.esrYear where " + strWhereFieldName + " in " + formid_list+ " and "+y.levelID+" IS NOT NULL and "+y.levelID+" not like '<p><br></p>'"
                        cursor.execute("select c.SchoolNameC, c.code, a."+y.levelID+" as value from " + tableName + " a INNER JOIN SQP.dbo.V_InspectionList c ON substring(a.klaFormID,1,12) = c.schoolID and substring(a.klaFormID,13,4) = c.esrYear where " + strWhereFieldName + " in " + formid_list+ " and "+y.levelID+" IS NOT NULL and "+y.levelID+" not like '<p><br></p>'")
                        data_list = cursor.fetchall()
                    report_list.append({'levelid': y.levelID, 'levelbase': y.levelBase, 'fieldnamec': y.levelDescC, 'fieldnamee': y.levelDescE, 'year': y.klayear, 'answertypeid': y.answerTypeID, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
            if pagetype[:3] == "#c3" or pagetype[:2] == "#f":
                tableArray = tableName.split("_")
                readtable = tableArray[1]
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=klaform')
                cursor = cnxn.cursor()
                if subject == "C": part = "CHI"
                if subject == "E": part = "ENG"
                if subject == "MA": part = "MATH"
                if subject == "SC": part = "SCI"
                if subject == "TE": part = "TE"
                if subject == "PH": part = "PSHE"
                if subject == "AR": part = "ART"
                if subject == "PE": part = "PE"
                if subject == "GS": part = "GS"
                if subject == "LS": part = "LS"
                if subject == "CS": part = "CS"
                schooltype = "A"
                if subject == "TE": schooltype = "S"
                if subject == "MA": schooltype = "S"
                if subject == "MA":
                    cursor.execute("getStructure_FORM_LEVEL_DATA '"+readtable+"', '"+schooltype+"', 1, '', '', '"+part+"S', "+str(year))
                else:
                    cursor.execute("getStructure_FORM_LEVEL_DATA '"+readtable+"', '"+schooltype+"', 1, '', '', '"+part+"', "+str(year))
                field_list = cursor.fetchall()
                field_length = len(formid_list)
                for y in field_list:
                    data_list = []
                    temp_list = []
                    if y.answerTypeID == 1:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        sql1 = "select SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list
                        data_list = cursor.fetchall()
                    if y.answerTypeID == 2:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        temp_list = cursor.fetchall()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 1 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        temp_list = temp_list + cursor.fetchall()
                        cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = 2 THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                        data_list = temp_list + cursor.fetchall()
                    if y.answerTypeID == 4:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        for w in range(4, 0, -1):
                            sql1 = "select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = " + str(w) + " THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list
                            cursor.execute("select COUNT(*) AS total, COUNT("+y.levelID+") AS total_value, SUM(CASE WHEN "+y.levelID+" = " + str(w) + " THEN 1 ELSE 0 END) AS count_1, SUM(CASE WHEN "+y.levelID+" = 0 or "+y.levelID+" = 0 THEN 1 ELSE 0 END) AS count_0 from " + tableName + " where " + strWhereFieldName + " in " + formid_list)
                            temp_list = (cursor.fetchall())
                            data_list.append(temp_list)
                    if y.answerTypeID == 9:
                        #sql1 = "select count("+y.levelID+") from " + tableName + " where " + strWhereFieldName + " in " + convertlt(formid_list)
                        formid_list = str(formid_list).replace("[","(").replace("]",")")
                        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=' + dbName)
                        cursor = cnxn.cursor()
                        sql1 = "select c.SchoolNameC, c.code, a."+y.levelID+" as value from " + tableName + " a INNER JOIN SQP.dbo.V_InspectionList c ON substring(a.klaFormID,1,12) = c.schoolID and substring(a.klaFormID,13,4) = c.esrYear where " + strWhereFieldName + " in " + formid_list+ " and "+y.levelID+" IS NOT NULL and "+y.levelID+" not like '<p><br></p>'"
                        cursor.execute("select c.SchoolNameC, c.code, a."+y.levelID+" as value from " + tableName + " a INNER JOIN SQP.dbo.V_InspectionList c ON substring(a.klaFormID,1,12) = c.schoolID and substring(a.klaFormID,13,4) = c.esrYear where " + strWhereFieldName + " in " + formid_list+ " and "+y.levelID+" IS NOT NULL and "+y.levelID+" not like '<p><br></p>'")
                        data_list = cursor.fetchall()
                    report_list.append({'levelid': y.levelID, 'levelbase': y.levelBase, 'fieldnamec': y.levelDescC, 'fieldnamee': y.levelDescE, 'year': y.klayear, 'answertypeid': y.answerTypeID, 'sql1': sql1, 'datalist': data_list, 'fieldlength': int(field_length)})
        context = {
            "action": action,
            "report_list": report_list,
            "formid_list": formid_list,
            "tabname": tabname,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
            "pagetype": pagetype,
            "field_list": field_list,
        }
    if action == "schoollist":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate '"+inspectiontype+"'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        report_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                checked = 1
                if w.InspType == "ESR":
                    esrform = ESRForms.objects.using('esrform').filter(esrformid=w.SchoolID + w.esrYear)
                    formstatus = esrform.first().status if esrform.exists() else None
                if w.InspType == "FI":
                    klaform = KLAForms.objects.using('klaform').filter(klaformid=w.SchoolID + w.esrYear)
                    formstatus = klaform.first().status if klaform.exists() else None
                if checked == 1:
                    if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                        checked = 0
                    if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                        checked = 0
                if schoollevel != "" and checked == 1:
                    if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                        checked = 0
                    if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                        checked = 0
                    if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                        checked = 0
                if inspectiontype != "" and checked == 1:
                    if w.InspType != inspectiontype:
                        checked = 0
                if subject != "99" and checked == 1:
                    if str(w.subcode) != subject:
                        checked = 0
                    if str(w.focusTypeID) != focustype:
                        checked = 0
                if part >= "partc" and checked == 1:
                    if w.InspType == "ESR":
                        checked = 0
                if part == "partc" and checked == 1:
                    if str(w.focusTypeID) != "1":
                        checked = 0
                if part == "partd" and checked == 1:
                    if str(w.focusTypeID) != "34":
                        checked = 0
                if part == "parte" and checked == 1:
                    if str(w.focusTypeID) != "36":
                        checked = 0
                if part == "partf" and checked == 1:
                    if str(w.focusTypeID) != "38":
                        checked = 0
                if loginid != "" and checked == 1:
                    if str(w.LoginID) != loginid:
                        checked = 0
                if status != "" and checked == 1:
                    if str(formstatus) != status:
                        checked = 0
                if displaymode == "1" and w.SchoolID[:1] == "9":
                    checked = 0
                if displaymode == "2" and w.SchoolID[:1] != "9":
                    checked = 0
                if checked == 1:
                    report_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus})
            except Exception as e:
                sSQL = 'N/A'
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                sSQL = "Error line "+str(line_number)+": "+str(e)

        context = {
            "action": action,
            "displaymode": displaymode,
            "report_list": report_list,
            "sql": sSQL,
        }
    return render(request, "report_template/formBReport_response.html", context)

def convertlt(list):
    return tuple(list)

def inspectionStatReport(request):
    if not request.session.get('post'): return redirect('')
    year = request.POST.get('year')
    schoollevel = request.GET.get('schoollevel')
    years = ESRschools.objects.using('sqp').filter(insptype='ESR').order_by('-esryear').values('esryear').distinct()
    if years:
        year = years[0]['esryear']
    focussubtypes = Focussubtypes.objects.using('focus').order_by('sequence')

    action = request.POST.get('action')

    accessid = 4132
    request.session['accessid'] = accessid
    cnxn_menu = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=qadind')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where post = '" + request.session.get('post') + "'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('sqp').get(postdesc=request.session.get('post'), year=currentschoolyear(), isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='sqp')
    pageviewlog(accessid, request.session.get('loginid'), request.session.get('post'), request.session.get('post_org'))
    context = {
        "action": action,
        "years": years,
        "focussubtypes": focussubtypes,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "report_template/inspectionStatReport.html", context)

@csrf_exempt
def inspectionStatReport_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    schoollevel = request.POST.get('schoollevel')
    inspectiontype = request.POST.get('inspectiontype')
    subject = request.POST.get('subject')
    focustype = request.POST.get('focustype')
    reporttype = request.POST.get('reporttype')
    part = request.POST.get('part')
    loginid = request.POST.get('loginid')
    status = request.POST.get('status')
    displaymode = request.POST.get('displaymode')

    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "user_year": year,
            "team_list": team_list,
        }

    if action == "menutab":
        context = {
            "action": action,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionList_SchoolType_School_Count where year_name = '" + year + "'")
        schoolTypeCountList = cursor.fetchall()
        cursor.execute("select * from V_InpsectionList_FocusType_School_Count where year_name = '" + year + "' order by sequence")
        focusTypeCountList = cursor.fetchall()

        context = {
            "action": action,
            "selectedyear": year,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "subject": subject,
            "focustype": focustype,
            "reporttype": reporttype,
            "part": part,
            "loginid": loginid,
            "status": status,
            "displaymode": displaymode,
            "schooltypecountlist": schoolTypeCountList,
            "focustypecountlist": focusTypeCountList,
        }
    if action == "schoollist":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate '"+inspectiontype+"'," + str(year) + ",''")
        inspection_list = cursor.fetchall()
        teammember_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                checked = 1
                if w.InspType == "ESR":
                    esrform = ESRForms.objects.using('esrform').filter(esrformid=w.SchoolID + w.esrYear)
                    formstatus = esrform.first().status if esrform.exists() else None
                if w.InspType == "FI":
                    klaform = KLAForms.objects.using('klaform').filter(klaformid=w.SchoolID + w.esrYear)
                    formstatus = klaform.first().status if klaform.exists() else None
                if checked == 1:
                    if start_date > str(w.esrStartDate) and start_date > str(w.esrEndDate):
                        checked = 0
                    if end_date < str(w.esrStartDate) and end_date < str(w.esrEndDate):
                        checked = 0
                if schoollevel != "" and checked == 1:
                    if schoollevel == "PS" and w.InspType == "ESR" and w.code[:2] == "EX":
                        checked = 0
                    if schoollevel == "PS" and w.InspType == "FI" and w.code[:1] == "3":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "ESR" and w.code[:2] != "EX":
                        checked = 0
                    if schoollevel == "SP" and w.InspType == "FI" and w.code[:1] != "3":
                        checked = 0
                    if w.schoolTypeID != schoollevel and schoollevel != "PS" and schoollevel != "SP":
                        checked = 0
                if inspectiontype != "" and checked == 1:
                    if w.InspType != inspectiontype:
                        checked = 0
                if subject != "99" and checked == 1:
                    if str(w.subcode) != subject:
                        checked = 0
                    if str(w.focusTypeID) != focustype:
                        checked = 0
                if loginid != "" and checked == 1:
                    if str(w.LoginID) != loginid:
                        checked = 0
                if status != "" and checked == 1:
                    if str(formstatus) != status:
                        checked = 0
                if displaymode == "1" and w.SchoolID[:1] == "9":
                    checked = 0
                if displaymode == "2" and w.SchoolID[:1] != "9":
                    checked = 0
                if checked == 1:
                    teammember_list.append({'schoolid': w.SchoolID, 'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'status': formstatus})
            except Exception as e:
                sSQL = 'N/A'
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                sSQL = "Error line "+str(line_number)+": "+str(e)

        context = {
            "action": action,
            "displaymode": displaymode,
            "teammember_list": teammember_list,
            "sql": sSQL,
        }
    return render(request, "report_template/inspectionStatReport_response.html", context)

def currentschoolyear():
    try:
        years = Users.objects.using('sqp').order_by('-year').values('year').distinct()
        value = years[0]['year']
        return value
    except:
        return ""

def pageviewlog(accessid, loginid, post, post_org):
    pageview = PageView()
    pageview.loginid = loginid
    pageview.postdesc = post
    pageview.logdatetime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    pageview.year = currentschoolyear()
    pageview.subcatid = accessid
    subcategory = SubCategories.objects.using('qadind').get(subcatid=accessid)
    pageview.pagename = subcategory.subcatname
    if post != post_org and post_org != "":
        pageview.logintype = "Demo"
    else:
        pageview.logintype = "Live"
    pageview.save(using='sqp')