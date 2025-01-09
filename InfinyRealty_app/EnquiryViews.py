from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db.models import Q
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
import os, fnmatch
import math
import numbers
import calendar
import datetime
from django.conf import settings
from django import template
import glob
import sys

register = template.Library()

from InfinyRealty_app.models import ESRschools, InspectorAllocation, QAI, Focusgroup, Focustype, Focussubtypes, CustomUser, Staffs
from InfinyRealty_app.models import Tabs, Categories, SubCategories, PageView, Users, Teams, Ranks, Schools, Schooltypes, Sessions, Districts, Financetypes, SSBs, Curriculumtypes, ESRschoolsER
from InfinyRealty_app.models import SchoolRelatedInfo, Schoolrelatedprogramme, Schoolrelatedncs, Schoolfinancereport, Schoolsct, Schoolmoireport, Areascore2008, SSPA, SchoolDevelopmentPlan
from InfinyRealty_app.models import LogItems, LogCategories, LogCommTypes, LogPriority, LogProblemTypes, LogEnquiryResponses, LogStatus, LogSubCategories, LogTypes, LogReport, SvaisUsers
from InfinyRealty_app.models import Entrusts, Propertys, Enquirys, CodeDetails, MortgageRefers

def entrustMain(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    accessid = 5163
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='infinyrealty')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/entrustMain.html", context)

@csrf_exempt
def entrustMain_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    entrust_id = request.POST.get('entrust_id')
    if entrust_id is None:
        entrust_id = ""
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    user_entrust_id = entrust_id

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
        }
    if action == "entrust_list":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblEntrust "  \
              "where (1 = case when '' = ? then 1 when create_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when create_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when entrust_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (start_date, start_date, end_date, end_date, entrust_id, entrust_id)
        cursor.execute(sql, params)
        entrust_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_entrust_id": entrust_id,
            "entrust_list": entrust_list,
            "sql": sql,
        }
    if action == "entrust_info":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblEntrust "  \
              "where (1 = case when '' = ? then 1 when entrust_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (entrust_id, entrust_id)
        cursor.execute(sql, params)
        entrust_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_entrust_id": entrust_id,
            "entrust_list": entrust_list,
            "sql": sql,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    return render(request, "enquiry_template/entrustMain_response.html", context)

@csrf_exempt
def entrustMain_save(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    entrust_id = request.POST.get('entrust_id')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    if action == "edit" or action == "delete":
        followup_info = request.POST.get('followup_info')
        followup_user = request.POST.get('followup_user')
        status = request.POST.get('status')
        try:
            entrust = Entrusts.objects.using('infinyrealty').get(entrust_id=entrust_id)
            entrust.modify_date = datetime_str
            entrust.followup_info = followup_info
            entrust.followup_user = followup_user
            entrust.status = status
            if action == "edit": entrust.save(using='infinyrealty')
            if action == "delete": entrust.delete()
            messages.success(request, "New Entrust was created successfully.")
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        
def mortgageRefer(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    accessid = 5164
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='infinyrealty')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/mortgageRefer.html", context)

@csrf_exempt
def mortgageRefer_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    mortgage_refer_id = request.POST.get('mortgage_refer_id')
    if mortgage_refer_id is None:
        mortgage_refer_id = ""
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    user_mortgage_refer_id = mortgage_refer_id

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
        }
    if action == "mortgagerefer_list":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblMortgageRefer "  \
              "where (1 = case when '' = ? then 1 when create_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when create_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when mortgage_refer_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (start_date, start_date, end_date, end_date, mortgage_refer_id, mortgage_refer_id)
        cursor.execute(sql, params)
        mortgagerefer_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_mortgage_refer_id": mortgage_refer_id,
            "mortgagerefer_list": mortgagerefer_list,
            "sql": sql,
        }
    if action == "mortgagerefer_info":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblMortgageRefer "  \
              "where (1 = case when '' = ? then 1 when mortgage_refer_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (mortgage_refer_id, mortgage_refer_id)
        cursor.execute(sql, params)
        mortgagerefer_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_mortgage_refer_id": user_mortgage_refer_id,
            "mortgagerefer_list": mortgagerefer_list,
            "sql": sql,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    return render(request, "enquiry_template/mortgageRefer_response.html", context)

@csrf_exempt
def mortgageRefer_save(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    mortgage_refer_id = request.POST.get('mortgage_refer_id')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    if action == "edit" or action == "delete":
        followup_user = request.POST.get('followup_user')
        status = request.POST.get('status')
        try:
            mortgagerefer = MortgageRefers.objects.using('infinyrealty').get(mortgage_refer_id=mortgage_refer_id)
            mortgagerefer.modify_date = datetime_str
            mortgagerefer.followup_user = followup_user
            mortgagerefer.status = status
            if action == "edit": mortgagerefer.save(using='infinyrealty')
            if action == "delete": mortgagerefer.delete()
            messages.success(request, "New Entrust was created successfully.")
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

def onlineEnquiry(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    accessid = 5166
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='infinyrealty')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/onlineEnquiry.html", context)

@csrf_exempt
def onlineEnquiry_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    contact_id = request.POST.get('contact_id')
    if contact_id is None:
        contact_id = ""
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    user_contact_id = contact_id

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
        }
    if action == "contact_list":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_Enquiry "  \
              "where (1 = case when '' = ? then 1 when create_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when create_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when contact_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (start_date, start_date, end_date, end_date, contact_id, contact_id)
        cursor.execute(sql, params)
        contact_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_contact_id": contact_id,
            "contact_list": contact_list,
            "sql": sql,
        }
    if action == "contact_info":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_Enquiry "  \
              "where (1 = case when '' = ? then 1 when contact_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (contact_id, contact_id)
        cursor.execute(sql, params)
        contact_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_contact_id": contact_id,
            "contact_list": contact_list,
            "sql": sql,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "edit" or action == "delete":
        status = request.POST.get('status')
        try:
            if action == "add":
                entrust = Entrusts()
                entrust.create_date = datetime_str
            else:
                entrust = Entrusts.objects.using('infinyrealty').get(entrust_id=entrust_id)
                entrust.modify_date = datetime_str
            entrust.status = status
            if action == "add" or action == "edit": entrust.save(using='infinyrealty')
            if action == "delete": entrust.delete()
            messages.success(request, "New Entrust was created successfully.")
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    return render(request, "enquiry_template/onlineEnquiry_response.html", context)

@csrf_exempt
def onlineEnquiry_save(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    contact_id = request.POST.get('contact_id')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    if action == "edit" or action == "delete":
        followup_user = request.POST.get('followup_user')
        status = request.POST.get('status')
        try:
            enquiry = Enquirys.objects.using('infinyrealty').get(contact_id=contact_id)
            enquiry.modify_date = datetime_str
            enquiry.followup_user = followup_user
            enquiry.status = status
            if action == "edit": enquiry.save(using='infinyrealty')
            if action == "delete": enquiry.delete()
            messages.success(request, "New enquiry was created successfully.")
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

def propertyEnquiry(request, selectType = None):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')

    accessid = 5165
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='infinyrealty')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "possession_list": possession_list,
        "selecttype": selectType,
    }
    return render(request, "enquiry_template/propertyEnquiry.html", context)

@csrf_exempt
def propertyEnquiry_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    property_id = request.POST.get('property_id')
    if property_id is None:
        property_id = ""
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    user_property_id = property_id
    possession = request.POST.get('possession')
    select_type = request.POST.get('select_type')

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
            "select_type": select_type,
        }
    if action == "property_sell_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",  None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_PropertyFullListHighlight where offertype = N'放售' and possession <> N'已售' and (HighlightType = 'sell' or Highlight is NULL) order by modifydate desc"
        cursor.execute(sql)
        property_sell_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_property_id": property_id,
            "property_sell_view_list": property_sell_view_list,
            "sql": sql,
        }
    if action == "property_rent_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",  None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_PropertyFullListHighlight where offertype = N'放租' and (HighlightType = 'rent' or Highlight is NULL) order by modifydate desc"
        cursor.execute(sql)
        property_rent_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_property_id": property_id,
            "property_rent_view_list": property_rent_view_list,
            "sql": sql,
        }
    if action == "property_rentsell_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",  None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_PropertyFullListHighlight where offertype = N'租售' and (HighlightType = 'sell' or HighlightType = 'rent' or Highlight is NULL) order by modifydate desc"
        cursor.execute(sql)
        property_rentsell_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_property_id": property_id,
            "property_rentsell_view_list": property_rentsell_view_list,
            "sql": sql,
        }
    if action == "property_rentsell_tenant_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",  None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        # sql = "select * from V_PropertyFullListHighlight where offertype = N'連租約售' and (HighlightType = 'sell' or HighlightType = 'rent' or Highlight is NULL) order by modifydate desc"
        sql = "select * from V_PropertyFullListHighlight where offertype = N'放售' and possession <> N'連租約' and (HighlightType = 'sell' or HighlightType = 'rent' or Highlight is NULL) order by modifydate desc"
        cursor.execute(sql)
        property_rentsell_tenant_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_property_id": property_id,
            "property_rentsell_tenant_view_list": property_rentsell_tenant_view_list,
            "sql": sql,
        }
    if action == "property_full_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",  None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_PropertyFullListHighlight order by modifydate desc"
        cursor.execute(sql)
        property_full_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_property_id": property_id,
            "property_full_view_list": property_full_view_list,
            "sql": sql,
        }
    if action == "property_info":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_PropertyFullList where propertyid = '" + str(property_id) + "' order by modifydate desc"
        cursor.execute(sql)
        property_list = cursor.fetchall()

        context = {
            "action": action,
            "user_property_id": property_id,
            "property_list": property_list,
            "sql": sql,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    return render(request, "enquiry_template/propertyEnquiry_response.html", context)

@csrf_exempt
def propertyEnquiry_save(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    property_id = request.POST.get('property_id')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    if action == "edit" or action == "delete":
        followup_user = request.POST.get('followup_user')
        possession = request.POST.get('possession')
        try:
            property = Propertys.objects.using('infinyrealty').get(propertyid=property_id)
            property.modify_date = datetime_str
            property.followup_user = followup_user
            property.possession = possession
            if action == "edit": property.save(using='infinyrealty')
            if action == "delete": property.delete()
            messages.success(request, "New property was created successfully.")
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

@csrf_exempt
def schoolContact_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    pagetype = request.POST.get('pagetype')
    schoolid = request.POST.get('schoolid')
    schools = Schools.objects.using('schoolmaster').filter(schoolid=schoolid)
    try:
        schoolname = schools[0].schoolnamee + "<br>" + schools[0].schoolnamec
        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypeid=schools[0].schooltypeid)
    except:
        schoolname = ""
        schooltypes = ""

    if action == "school_contact":
        try:
            url = schools[0].urlprofile
            parsed = urlparse.urlparse(url)
            pic_id = urlparse.parse_qs(parsed.query)['sch_id']
        except:
            pic_id = "1"
        context = {
            "action": action,
            "schoolid": schoolid,
            "schoolname": schoolname,
            "schooltypes": schooltypes[0].schooltypeid,
            "urlprofile": schools[0].urlprofile,
            "pagetype": pagetype,
            "pic_id": pic_id,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
        }
    if pagetype == "#schoolcontact":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SCHOOL_LIST where schoolid = '" + schoolid + "'")
        esdaschools = cursor.fetchall()
        schools = Schools.objects.using('schoolmaster').filter(schoolid=schoolid)
        schooldevelopmentplan = SchoolDevelopmentPlan.objects.using('schoolmaster').filter(schoolid=schoolid)
        schooldevelopmentcycle = "N"
        for v in schooldevelopmentplan:
            if v.sdpscrn_a != 'N': schooldevelopmentcycle = v.sdpscrn_a
            if v.sdpscrn_b != 'N': schooldevelopmentcycle = v.sdpscrn_b
            if v.sdpscrn_c != 'N': schooldevelopmentcycle = v.sdpscrn_c
            if v.sdpscrn_d != 'N': schooldevelopmentcycle = v.sdpscrn_d
            if v.sdpscrn_e != 'N': schooldevelopmentcycle = v.sdpscrn_e
            if v.sdpscrn_f != 'N': schooldevelopmentcycle = v.sdpscrn_f
        if schooldevelopmentcycle == "N":
            schooldevelopmentplan = SchoolDevelopmentPlan.objects.using('schoolmaster').filter(schoolid__startswith=schoolid[:6])
            for v in schooldevelopmentplan:
                if v.sdpscrn_a != 'N': schooldevelopmentcycle = v.sdpscrn_a
                if v.sdpscrn_b != 'N': schooldevelopmentcycle = v.sdpscrn_b
                if v.sdpscrn_c != 'N': schooldevelopmentcycle = v.sdpscrn_c
                if v.sdpscrn_d != 'N': schooldevelopmentcycle = v.sdpscrn_d
                if v.sdpscrn_e != 'N': schooldevelopmentcycle = v.sdpscrn_e
                if v.sdpscrn_f != 'N': schooldevelopmentcycle = v.sdpscrn_f

        cursor2 = cnxn.cursor()
        cursor2.execute("select * from SYS_INFO")
        systeminfo = cursor2.fetchall()
        for w in systeminfo:
            if w.INFO_KEY == "SPV": LatestProgramVersion = w.INFO_VALUE
            if w.INFO_KEY == "SDV": LatestDataVersion = w.INFO_VALUE

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "schools": schools,
            "esdaschools": esdaschools,
            "LatestProgramVersion": LatestProgramVersion,
            "LatestDataVersion": LatestDataVersion,
            "schooldevelopmentcycle": schooldevelopmentcycle,
        }
    if pagetype == "#systemlog":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SCHOOL_PROGRAM_UPDATE_LOG where schoolid = '" + schoolid + "'")
        schoollogs = cursor.fetchall()

        cursor2 = cnxn.cursor()
        cursor2.execute("select * from VIEW_SCHOOL_LOGIN_AUDIT_LOG where SCRN = '" + schoolid + "' order by OPERATION_TIME desc")
        schoolloginlogs = cursor2.fetchall()
        cursor2 = cnxn.cursor()
        cursor2.execute("select * from SYS_INFO")
        systeminfo = cursor2.fetchall()
        for w in systeminfo:
            if w.INFO_KEY == "SPV": LatestProgramVersion = w.INFO_VALUE
            if w.INFO_KEY == "SDV": LatestDataVersion = w.INFO_VALUE

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "schoollogs": schoollogs,
            "schoolloginlogs": schoolloginlogs,
            "LatestProgramVersion": LatestProgramVersion,
            "LatestDataVersion": LatestDataVersion,
        }
    if pagetype == "#enquirylog":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=enquirylog')
        cursor = cnxn.cursor()
        cursor.execute("exec spLogItemsSchool '" + schoolid + "'")
        LogEnquiryList = cursor.fetchall()

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "logenquirylist": LogEnquiryList,
        }

    if pagetype == "#ssedata":
        #SSE Data
        cnxn1=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=schoolmaster')
        cursor1 = cnxn1.cursor()
        cursor1.execute("select oldschoolid as schoolid from schoolmaster..tblschoolhistory where schoolid = '"+str(schoolid)+"' union select schoolid from schoolmaster..tblschool where schoolid like left('"+str(schoolid)+"',11)+'%'")
        cursor1.execute("select schoolid,esryear from sqp..tblESRSchools where schoolid in (select oldschoolid as schoolid from schoolmaster..tblschoolhistory where schoolid = '"+str(schoolid)+"' union select schoolid from schoolmaster..tblschool where schoolid like left('"+str(schoolid)+"',11)+'%')")
        sSSEData = cursor1.fetchall()
        cnxn2=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=schoolmaster')
        cursor2 = cnxn2.cursor()
        cursor2.execute("select distinct(esryear) as year from sqp..tblESRSchools order by year")
        sSSEDataYear = cursor2.fetchall()

        subfolder_list = []
        sse_filename_list = []
        for w in sSSEData:
            #path = "E:\\QAIP_INSP_REPORT\\SDC\\"+w.focusYear+"\\"+w.schoolid
            root = getattr(settings, "PATH_INSP_REPORT", None) + "SDC"
            try:
                for path, subdirs, files in os.walk(root):
                    for name in files:
                        if w.schoolid in name:
                            sYear = path.replace('\\'+w.schoolid,'')
                            sYear = sYear.replace(root.rstrip()+'\\','')
                            if sYear == w.esryear:
                                inspection = "Yes"
                            else:
                                inspection = "No"
                            if len(sYear) == 4 and name not in sse_filename_list:
                                subfolder_list.append({'schoolid': w.schoolid, 'year': sYear, 'esrYear': w.esryear, 'path': path, 'subfolder': subdirs, 'inspection': inspection, 'filename': name})
                                sse_filename_list.append(name)
            except Exception as e:
                sSQL = 'N/A'
        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "sse_filename_list":sse_filename_list,
            "ssedata": sSSEData,
            "subfolder_list": subfolder_list,
        }

    if pagetype == "#datasubmission":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SCHOOL_DATA_SUBMISSION where schoolid = '" + schoolid + "'")
        schooldatasubmissions = cursor.fetchall()

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "schooldatasubmissions": schooldatasubmissions,
        }

    if pagetype == "#postsurvey":
        #Post Survey Data
        cnxn1=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=valueadded')
        cursor1 = cnxn1.cursor()
        cursor1.execute("exec spVASchool_InspHistory_new '"+str(schoolid)+"'")
        sInspectionHistory = cursor1.fetchall()

        cnxn1=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_ESDA_QA_HOST", None)+';UID='+getattr(settings, "AUTH_ESDA_QA_USER", None)+';PWD='+getattr(settings, "AUTH_ESDA_QA_PASSWORD", None)+';Database=ESDA_QA')
        cursor1 = cnxn1.cursor()
        cursor1.execute("select * from VIEW_ONLINE_SURVEY_LIST where SCRN like SUBSTRING('" + str(schoolid) + "',1,6)+'%' order by YEAR_NAME DESC")
        sPostSurveyData = cursor1.fetchall()

        esrschools = ESRschools.objects.using('sqp').filter(schoolid=schoolid).filter(esryear=request.session.get('year')).order_by('-esryear')
        if esrschools:
            isInspection = 1
        else:
            isInspection = 0
        post_filename_list = []
        code = ""
        listing = ""
        for w in sPostSurveyData:
            for v in sInspectionHistory:
                if v.schoolID.strip()[:6] == w.SCRN.strip()[:6] and v.focusYear.strip() == w.YEAR_NAME[:4].strip():
                    code = v.focusCode
                    break
                else:
                    code = ""
            #return HttpResponse(test)
            path = getattr(settings, "PATH_INSP_REPORT", None)+w.SURVEY_TYPE+"\\"+w.YEAR_NAME[:4]+"\\"+code+"_"+w.SCRN+"\\SCH"
            path1 = getattr(settings, "PATH_INSP_REPORT", None)+w.SURVEY_TYPE+"\\"+w.YEAR_NAME[:4]+"\\*"+code+"_"+w.SCRN[:6]+"*\\SCH"
            path_list = str(glob.glob(path1))
            path_list = path_list.replace("['", "")
            path_list = path_list.replace("']", "")
            schoolid_list = path_list[-17:]
            schoolid_list = schoolid_list[:12]
            listing = listing + path_list + "<br>"

            #return HttpResponse(path)
            try:
                file_list = fnmatch.filter(os.listdir(path_list), '*.xls*')
                file_list = file_list + fnmatch.filter(os.listdir(path_list), '*,doc*')
                file_list = file_list + fnmatch.filter(os.listdir(path_list), '*.pdf')
            except Exception as e:
                file_list = 'N/A'
            if w.SCRN:
                post_filename_list.append({'insptype':w.SURVEY_TYPE,'year':w.YEAR_NAME[:4],'code':code,'schoolid':w.SCRN,'filename':file_list})
        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "post_filename_list":post_filename_list,
            "postsurveydata": sPostSurveyData,
            "file_list": post_filename_list,
            "isInspection": isInspection,
            "listing": listing,
            "schoolid_list": schoolid_list,
        }

    if pagetype == "#whole":
        context = {
            "tmpost": tmpost,
            "pagetype": pagetype,
            "schoolid": schoolid,
            "year": year,
            "insptype": insptype,
            "loginid": loginid,
            "schooltypeid": schools[0].schooltypeid,
            "schooltypedesc": schooltypes[0].schooltypedesc,
        }
    return render(request, "enquiry_template/schoolContact_response.html", context)

@csrf_exempt
def schoolKPM_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    pagetype = request.POST.get('pagetype')
    schoolid = request.POST.get('schoolid')
    schools = Schools.objects.using('schoolmaster').filter(schoolid=schoolid)
    schoolname = schools[0].schoolnamee + "<br>" + schools[0].schoolnamec
    schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypeid=schools[0].schooltypeid)
    school_id = request.POST.get('school_id')
    yearname = request.POST.get('yearname')
    version = request.POST.get('version')
    schoollevel = request.POST.get('schoollevel')

    if action == "school_kpm":
        url = schools[0].urlprofile
        parsed = urlparse.urlparse(url)
        try:
            pic_id = urlparse.parse_qs(parsed.query)['sch_id']
        except:
            pic_id = "1"
        context = {
            "action": action,
            "schoolid": schoolid,
            "schoolname": schoolname,
            "schooltypes": schooltypes[0].schooltypeid,
            "urlprofile": schools[0].urlprofile,
            "pagetype": pagetype,
            "pic_id": pic_id,
            "school_id": school_id,
            "yearname": yearname,
            "version": version,
            "schoollevel": schoollevel,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
        }
    if pagetype == "#schoolkpm":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_KPM_ITEM_NAME where YEAR_NAME = '" + yearname + "' AND VERSION = '" + version + "' AND SCHOOL_LEVEL = '" + schoollevel + "'")
        #cursor.execute("select * from VIEW_KPM_SCHOOL_RESULT where YEAR_NAME = '" + yearname + "' AND VERSION = '" + version + "' AND SCHOOL_LEVEL = '" + schoollevel + "' AND SCHOOL_ID = '" + school_id + "'")
        sql = "select * from VIEW_KPM_SCHOOL_RESULT where YEAR_NAME = '" + yearname + "' AND VERSION = '" + version + "' AND SCHOOL_LEVEL = '" + schoollevel + "' AND SCHOOL_ID = '" + school_id + "'"
        kpmitemname = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_KPM_SCHOOL_RESULT where YEAR_NAME = '" + yearname + "' AND VERSION = '" + version + "' AND SCHOOL_LEVEL = '" + schoollevel + "' AND SCHOOL_ID = '" + school_id + "'")
        kpmitemresult = cursor.fetchall()

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "yearname": yearname,
            "version": version,
            "kpmitemname": kpmitemname,
            "kpmitemresult": kpmitemresult,
            "sql": sql,
        }
    if pagetype == "#schoolshs":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from SHS where YEAR_NAME = '" + yearname + "' AND VERSION = '" + version + "' AND SCHOOL_LEVEL = '" + schoollevel + "'")
        shsitemname = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SHS_SCHOOL_RESULT where YEAR_NAME = '" + yearname + "' AND VERSION = '" + version + "' AND SCHOOL_LEVEL = '" + schoollevel + "' AND SCHOOL_ID = '" + school_id + "'")
        shsitemcount = cursor.fetchall()

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "yearname": yearname,
            "version": version,
            "shsitemname": shsitemname,
            "shsitemcount": shsitemcount,
        }
    if pagetype == "#schoolapaso":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_APASO_SCHOOL_RESULT where YEAR_NAME = '" + yearname + "' AND VERSION = '" + version + "' AND SCHOOL_LEVEL = '" + schoollevel + "' AND SCHOOL_ID = '" + school_id + "'")
        apasoitemname = cursor.fetchall()

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "yearname": yearname,
            "version": version,
            "apasoitemname": apasoitemname,
        }
    if pagetype == "#systemlog":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SCHOOL_PROGRAM_UPDATE_LOG where schoolid = '" + schoolid + "'")
        schoollogs = cursor.fetchall()

        cursor2 = cnxn.cursor()
        cursor2.execute("select * from VIEW_SCHOOL_LOGIN_AUDIT_LOG where SCRN = '" + schoolid + "' order by OPERATION_TIME desc")
        schoolloginlogs = cursor2.fetchall()
        cursor2 = cnxn.cursor()
        cursor2.execute("select * from SYS_INFO")
        systeminfo = cursor2.fetchall()
        for w in systeminfo:
            if w.INFO_KEY == "SPV": LatestProgramVersion = w.INFO_VALUE
            if w.INFO_KEY == "SDV": LatestDataVersion = w.INFO_VALUE

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "schoollogs": schoollogs,
            "schoolloginlogs": schoolloginlogs,
            "LatestProgramVersion": LatestProgramVersion,
            "LatestDataVersion": LatestDataVersion,
        }
    if pagetype == "#enquirylog":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=enquirylog')
        cursor = cnxn.cursor()
        cursor.execute("exec spLogItemsSchool '" + schoolid + "'")
        LogEnquiryList = cursor.fetchall()

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "logenquirylist": LogEnquiryList,
        }

    if pagetype == "#ssedata":
        #SSE Data
        cnxn1=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=schoolmaster')
        cursor1 = cnxn1.cursor()
        cursor1.execute("select oldschoolid as schoolid from schoolmaster..tblschoolhistory where schoolid = '"+str(schoolid)+"' union select schoolid from schoolmaster..tblschool where schoolid like left('"+str(schoolid)+"',11)+'%'")
        cursor1.execute("select schoolid,esryear from sqp..tblESRSchools where schoolid in (select oldschoolid as schoolid from schoolmaster..tblschoolhistory where schoolid = '"+str(schoolid)+"' union select schoolid from schoolmaster..tblschool where schoolid like left('"+str(schoolid)+"',11)+'%')")
        sSSEData = cursor1.fetchall()
        cnxn2=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=schoolmaster')
        cursor2 = cnxn2.cursor()
        cursor2.execute("select distinct(esryear) as year from sqp..tblESRSchools order by year")
        sSSEDataYear = cursor2.fetchall()

        subfolder_list = []
        sse_filename_list = []
        for w in sSSEData:
            #path = "E:\\QAIP_INSP_REPORT\\SDC\\"+w.focusYear+"\\"+w.schoolid
            root = getattr(settings, "PATH_INSP_REPORT", None) + "SDC"
            try:
                for path, subdirs, files in os.walk(root):
                    for name in files:
                        if w.schoolid in name:
                            sYear = path.replace('\\'+w.schoolid,'')
                            sYear = sYear.replace(root.rstrip()+'\\','')
                            if sYear == w.esryear:
                                inspection = "Yes"
                            else:
                                inspection = "No"
                            if len(sYear) == 4 and name not in sse_filename_list:
                                subfolder_list.append({'schoolid': w.schoolid, 'year': sYear, 'esrYear': w.esryear, 'path': path, 'subfolder': subdirs, 'inspection': inspection, 'filename': name})
                                sse_filename_list.append(name)
            except Exception as e:
                sSQL = 'N/A'
        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "sse_filename_list":sse_filename_list,
            "ssedata": sSSEData,
            "subfolder_list": subfolder_list,
        }

    if pagetype == "#datasubmission":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SCHOOL_DATA_SUBMISSION where schoolid = '" + schoolid + "'")
        schooldatasubmissions = cursor.fetchall()

        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "schooldatasubmissions": schooldatasubmissions,
        }

    if pagetype == "#postsurvey":
        #Post Survey Data
        cnxn1=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=valueadded')
        cursor1 = cnxn1.cursor()
        cursor1.execute("exec spVASchool_InspHistory_new '"+str(schoolid)+"'")
        sInspectionHistory = cursor1.fetchall()

        cnxn1=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_ESDA_QA_HOST", None)+';UID='+getattr(settings, "AUTH_ESDA_QA_USER", None)+';PWD='+getattr(settings, "AUTH_ESDA_QA_PASSWORD", None)+';Database=ESDA_QA')
        cursor1 = cnxn1.cursor()
        cursor1.execute("select * from VIEW_ONLINE_SURVEY_LIST where SCRN like SUBSTRING('" + str(schoolid) + "',1,6)+'%' order by YEAR_NAME DESC")
        sPostSurveyData = cursor1.fetchall()

        esrschools = ESRschools.objects.using('sqp').filter(schoolid=schoolid).filter(esryear=request.session.get('year')).order_by('-esryear')
        if esrschools:
            isInspection = 1
        else:
            isInspection = 0
        post_filename_list = []
        code = ""
        listing = ""
        for w in sPostSurveyData:
            for v in sInspectionHistory:
                if v.schoolID.strip()[:6] == w.SCRN.strip()[:6] and v.focusYear.strip() == w.YEAR_NAME[:4].strip():
                    code = v.focusCode
                    break
                else:
                    code = ""
            #return HttpResponse(test)
            path = getattr(settings, "PATH_INSP_REPORT", None)+w.SURVEY_TYPE+"\\"+w.YEAR_NAME[:4]+"\\"+code+"_"+w.SCRN+"\\SCH"
            path1 = getattr(settings, "PATH_INSP_REPORT", None)+w.SURVEY_TYPE+"\\"+w.YEAR_NAME[:4]+"\\*"+code+"_"+w.SCRN[:6]+"*\\SCH"
            path_list = str(glob.glob(path1))
            path_list = path_list.replace("['", "")
            path_list = path_list.replace("']", "")
            schoolid_list = path_list[-17:]
            schoolid_list = schoolid_list[:12]
            listing = listing + path_list + "<br>"

            #return HttpResponse(path)
            try:
                file_list = fnmatch.filter(os.listdir(path_list), '*.xls*')
                file_list = file_list + fnmatch.filter(os.listdir(path_list), '*,doc*')
                file_list = file_list + fnmatch.filter(os.listdir(path_list), '*.pdf')
            except Exception as e:
                file_list = 'N/A'
            if w.SCRN:
                post_filename_list.append({'insptype':w.SURVEY_TYPE,'year':w.YEAR_NAME[:4],'code':code,'schoolid':w.SCRN,'filename':file_list})
        context = {
            "pagetype": pagetype,
            "schoolid": schoolid,
            "post_filename_list":post_filename_list,
            "postsurveydata": sPostSurveyData,
            "file_list": post_filename_list,
            "isInspection": isInspection,
            "listing": listing,
            "schoolid_list": schoolid_list,
        }
    return render(request, "enquiry_template/schoolKPM_response.html", context)

def listToString(instr):
    # initialize empty string
    emptystr = ""
    # string traversal using for loop
    for ele in instr:
        emptystr += ele
    return emptystr

@csrf_exempt
def school_report(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    schoolid = request.POST.get('schoolid')

    schools = Schools.objects.using('schoolmaster').filter(schoolid=schoolid)

    #Inspection History
    cnxn1=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=valueadded')
    cursor1 = cnxn1.cursor()
    cursor1.execute("exec spVASchool_InspHistory_new '"+str(schoolid)+"'")
    sInspectionHistory = cursor1.fetchall()

    #file = open(os.path.join(settings.MEDIA_ROOT, 'E:\\QAIP_INSP_REPORT'))
    filename_list = []
    for w in sInspectionHistory:
        path = getattr(settings, "PATH_INSP_REPORT", None)+w.InspType+"\\"+w.focusYear+"\\"+w.focusCode+"_"+w.schoolID+"\\REPORT"
        try:
            file_list = os.listdir(path)
        except Exception as e:
            file_list = 'N/A'
        filename_list.append({'insptype':w.InspType,'focusyear':w.focusYear,'focuscode':w.focusCode,'schoolid':w.schoolID,'filename':file_list})

    context = {
        "action": action,
        "schoolid": schoolid,
        "schools": schools,
        "schoolnamee": schools[0].schoolnamee,
        "schoolnamec": schools[0].schoolnamec,
        "inspectionhistory": sInspectionHistory,
        "filename_list":filename_list,
    }
    return render(request, "enquiry_template/schoolReport_response.html", context)

@csrf_exempt
def logEnquiry(request, year='None', SelectTeam='None', SelectKLA='None', eventtype='None'):
    if not request.session.get('post'): return redirect('')
    year = currentschoolyear()
    if (SelectTeam == 'None'): SelectTeam = ''
    if (SelectKLA == 'None'): SelectKLA = ''
    if (eventtype == 'None'): eventtype = '2'
    IsActive = '1'
        
    sessionPost = request.session.get('post')
    sessionLoginID = request.session.get('loginid')
    logitems = LogItems.objects.using('enquirylog')[:100]
    logcategories = LogCategories.objects.using('enquirylog').order_by('logtypeid').distinct()
    logcommtypes = LogCommTypes.objects.using('enquirylog')   
    logstatus = LogStatus.objects.using('enquirylog')
    logsubcategories = LogSubCategories.objects.using('enquirylog')
    logtypes = LogTypes.objects.using('enquirylog').order_by('sequence')
    logreport = LogReport.objects.using('enquirylog')
    SchoolList = Schools.objects.using('schoolmaster').filter(isactive=1)
    AccountList = Users.objects.using('sqp').filter(year=year).filter(team=SelectTeam).filter(isactive=1).distinct()
    TeamList = Teams.objects.using('sqp').order_by('sequence')
    today = date.today().strftime("%Y-%m-%d") 
    StartDate = request.POST.get('startdate', currentschoolyear()+'-09-01')
    EndDate = request.POST.get('enddate', today)
    action = request.POST.get('action')    
    
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
    cursor = cnxn.cursor()
    cursor.execute("exec spQATeamList '" + str(year) + "','','', '1'")
    PostList = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=enquirylog')
    cursor = cnxn.cursor()
    cursor.execute("exec spLogRecCountTypeStatus '" + StartDate + "','" + EndDate + "'")
    LogRecCountStatus = cursor.fetchall()

    userList = []
    for w in PostList:
        if {'PostDesc': w.PostDesc, 'PostVar': w.PostVar, 'LoginNameDesc': w.LoginNameDesc, 'LoginID': w.LoginID,
            'Rank': w.Rank, 'rank_sequence': w.rank_sequence, 'Team': w.Team,
            'team_sequence': w.team_sequence} not in userList:
            userList.append(
                {'PostDesc': w.PostDesc, 'PostVar': w.PostVar, 'LoginNameDesc': w.LoginNameDesc, 'LoginID': w.LoginID,
                 'Rank': w.Rank, 'rank_sequence': w.rank_sequence, 'Team': w.Team, 'team_sequence': w.team_sequence})

    if action == "logenquiry_list":   
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=enquirylog')
        cursor = cnxn.cursor()           
        cursor.execute("exec spLogItemSelect '"+ StartDate + "','"+ EndDate + "'")        
        LogEnquiryList = cursor.fetchall()
        if logenquirylist.objects.get(schoolid = " "):
            schoolid = logenquirylist.objects.filter(schoolname="contactschool").only("schoolid") 

        context = {
            "action": action,
            "logenquirylist": LogEnquiryList,            
            "startdate": StartDate,
            "enddate": EndDate    
        }
        
    accessid = 48
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
        "logreccountstatus": LogRecCountStatus,
        "accountlist": AccountList,
        "teamlist": TeamList,
        "postlist": PostList,
        "userlist": userList,
        "logitems": logitems,        
        "logcategories": logcategories,
        "logcommtypes": logcommtypes,        
        "logstatus": logstatus,
        "logsubcategories": logsubcategories,
        "logtypes": logtypes,
        "logreport": logreport,  
        "schoollist": SchoolList,
        "sessionpost": sessionPost,
        "sessionloginid": sessionLoginID,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/logEnquiry.html", context)

@csrf_exempt
def logEnquiry_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    today = date.today().strftime("%Y-%m-%d")     
    StartDate = request.POST.get('startdate')
    EndDate = request.POST.get('enddate')
    LogItemID = request.POST.get('logitemid')

    if action == "logenquiry_list":        
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=enquirylog')
        cursor = cnxn.cursor()           
        cursor.execute("exec spLogItemSelect '"+ StartDate + "','"+ EndDate + "'")        
        LogEnquiryList = cursor.fetchall()

        context = {
            "action": action,
            "logenquirylist": LogEnquiryList,            
            "startdate": StartDate,
            "enddate": EndDate
        }
    if action == "logenquiry_response_list":        
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=enquirylog')
        cursor = cnxn.cursor()           
        cursor.execute("exec spLogResponse '"+ LogItemID + "'")       
        LogResponseList = cursor.fetchall()
        
        context = {
            "action": action,
            "logresponselist": LogResponseList,
            "logitemid": LogItemID            
        }
    if action == "category_list":
        logtypeid = request.POST.get('logtypeid')
        logcategoryid = request.POST.get('logcategoryid')
        logsubcategoryid = request.POST.get('logsubcategoryid')
        logcategories = LogCategories.objects.using('enquirylog').filter(logtypeid=logtypeid).order_by('ordering')
        
        context = {
            "action": action,
            "logcategories": logcategories,
            "user_logcategory": logcategoryid,
            "user_logsubcategory": logsubcategoryid
        }
    if action == "subcategory_list":
        logcategoryid = request.POST.get('logcategoryid')
        logsubcategoryid = request.POST.get('logsubcategoryid')
        logsubcategories = LogSubCategories.objects.using('enquirylog').filter(logcategoryid=logcategoryid).order_by('ordering')
        
        context = {
            "action": action,
            "logsubcategories": logsubcategories,
            "user_logsubcategory": logsubcategoryid
        }
    if action == "logschool_list":
        contactschool = request.POST.get('contactschool')
        schoolid = request.POST.get('schoolid')
        SchoolList = Schools.objects.using('enquirylog').filter(schoolid=schoolid).order_by('ordering')

        context = {
            "action": action,
            "schoollist": SchoolList,
            "user_schoolid": schoolid
        }
    if action == "get_schoolname":
        schoolname = request.POST.get('schoolname')
        if schoolname == "":
            return HttpResponse(schoolname)
        schools = Schools.objects.using('schoolmaster').filter(schoolnamee=schoolname)
        if schools:
            schoolname_return = schools[0].schoolnamec
        else:
            schools = Schools.objects.using('schoolmaster').filter(schoolnamec=schoolname)
            if schools:
                schoolname_return = schools[0].schoolnamee
            else:
                schoolname_return = schoolname
        return HttpResponse(schoolname_return)
    return render(request, "enquiry_template/logEnquiry_response.html", context)

@csrf_exempt
def logEnquiry_save(request):
    if not request.session.get('post'): return redirect('')
    action = str(request.POST.get('action'))
    logitemid = request.POST.get('logitemid')    		
    logtypeid = str(request.POST.get("logtypeid"))
    logcategoryid = request.POST.get("logcategoryid")
    logsubcategoryid = request.POST.get("logsubcategoryid")
    logitemdate = request.POST.get("logitemdate")
    schoolid = request.POST.get("schoolid")
    contactschool = request.POST.get("contactschool")
    contactname = request.POST.get("contactname")
    contactemail = request.POST.get("contactemail")
    contactphone = request.POST.get("contactphone")
    logitmd = request.POST.get("logitmd")
    logcommtypeid = request.POST.get("logcommtypeid")
    logitemdesc = request.POST.get("logitemdesc")
    statusid = str(request.POST.get("statusid"))
    logstaffid = request.POST.get("logstaffid")
    createdate = request.POST.get("createdate")    
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")    
    
    try:
        if action == "add":
            logitem = LogItems()
        else:
            logitem = LogItems.objects.using('enquirylog').get(logitemid=logitemid)
        if logcategoryid == "":
            logcategoryid = 0
        if logsubcategoryid == "":
            logsubcategoryid = 0
        logitem.logtypeid_id = logtypeid
        logitem.logitemdesc = logitemdesc
        logitem.logitemdate = logitemdate
        logitem.contactname = contactname
        logitem.contactemail = contactemail
        logitem.contactschool = contactschool
        logitem.contactphone = contactphone
        logitem.logitmd = logitmd
        logitem.statusid_id = statusid
        logitem.logcommtypeid_id = logcommtypeid
        logitem.logstaffid = logstaffid        
        logitem.logcategoryid = logcategoryid
        logitem.logsubcategoryid = logsubcategoryid
        logitem.modifydate = datetime_str
        logitem.schoolid = schoolid
        if contactschool == "": logitem.schoolid = ""
        if action == "add": logitem.createdate = datetime_str
        if action == "add" or action == "edit": logitem.save(using='enquirylog')
        if action == "delete": logitem.delete(using='enquirylog')           
        messages.success(request, "New log enquiry was created successfully.")
        return HttpResponse("True")
    except:       
        return HttpResponse("False\n" + action + "\n" + logtypeid + "\n" + logcategoryid + "\n" + logsubcategoryid + "\n" + logitemdate + "\n" + schoolid + "\n" + contactschool + "\n" + contactname + "\n" + contactemail + "\n" + contactphone + "\n" + logcommtypeid + "\n" + logitemdesc + "\n" + statusid)

@csrf_exempt
def logEnquiryResponse_save(request):
    if not request.session.get('post'): return redirect('')
    action = str(request.POST.get('action'))
    logresponseid = request.POST.get("logresponseid")
    logitemid = request.POST.get("logitemid")
    logresponsedesc = request.POST.get("logresponsedesc")        
    logresponsestaffid = request.POST.get("logstaffid")
    logresponsedate = request.POST.get("logresponsedate")         
    logresponsecommtypeid = request.POST.get("logcommtypeid")
    
    try:
        if action == "add":
            logresponseitem = LogEnquiryResponses()
        else:
            logresponseitem = LogEnquiryResponses.objects.using('enquirylog').get(logresponseid=logresponseid)
            
        logresponseitem.logitemid_id = logitemid
        logresponseitem.logresponseid = logresponseid
        logresponseitem.logresponsedesc = logresponsedesc
        logresponseitem.logstaffid = logresponsestaffid
        logresponseitem.logresponsedate = logresponsedate
        logresponseitem.logcommtypeid_id = logresponsecommtypeid
        if action == "add": logresponseitem.save(using='enquirylog')
        if action == "delete": logresponseitem.delete(using='enquirylog')
        messages.success(request, "New response log of enquiry was created successfully.")
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False" +action + "\n" +str(e)+ "\n" + logitemid + "\n" +logresponsedesc+ "\n" + logresponsestaffid + "\n" + logresponsedate + "\n" + logresponsecommtypeid)

@csrf_exempt
def problemLog(request, year='None', SelectTeam='None'):
    if not request.session.get('post'): return redirect('')
    year = currentschoolyear()

    sessionPost = request.session.get('post')
    sessionLoginID = request.session.get('loginid')
    logitems = LogItems.objects.using('enquirylog')[:100]
    logcategories = LogCategories.objects.using('enquirylog').order_by('logtypeid').distinct()
    logcommtypes = LogCommTypes.objects.using('enquirylog')
    logpriority = LogPriority.objects.using('enquirylog')
    logproblemtypes = LogProblemTypes.objects.using('enquirylog')
    logstatus = LogStatus.objects.using('enquirylog')
    logsubcategories = LogSubCategories.objects.using('enquirylog')
    logtypes = LogTypes.objects.using('enquirylog').order_by('sequence')
    logreport = LogReport.objects.using('enquirylog')
    SchoolList = Schools.objects.using('schoolmaster').filter(isactive=1)
    AccountList = Users.objects.using('sqp').filter(year=year).filter(team=SelectTeam).filter(isactive=1).distinct()
    TeamList = Teams.objects.using('sqp').order_by('sequence')
    today = date.today().strftime("%Y-%m-%d")
    StartDate = request.POST.get('startdate', '2021-09-01')
    EndDate = request.POST.get('enddate', today)
    action = request.POST.get('action')

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
    cursor = cnxn.cursor()
    cursor.execute("exec spQATeamList '" + str(year) + "','','', '1'")
    PostList = cursor.fetchall()

    if action == "logenquiry_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=enquirylog')
        cursor = cnxn.cursor()
        cursor.execute("exec spLogItemSelect '" + StartDate + "','" + EndDate + "'")
        LogEnquiryList = cursor.fetchall()
        if logenquirylist.objects.get(schoolid=" "):
            schoolid = logenquirylist.objects.filter(schoolname="contactschool").only("schoolid")

        context = {
            "action": action,
            "logenquirylist": LogEnquiryList,
            "startdate": StartDate,
            "enddate": EndDate
        }

    accessid = 5141
    request.session['accessid'] = accessid
    cnxn_menu = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST",
                                                                                          None) + ';UID=' + getattr(
        settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD",
                                                              None) + ';Database=qadind')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where post = '" + request.session.get('post') + "'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('sqp').get(postdesc=request.session.get('post'), year=currentschoolyear(), isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='sqp')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('post'),request.session.get('post_org'))
    context = {
        "accountlist": AccountList,
        "teamlist": TeamList,
        "postlist": PostList,
        "logitems": logitems,
        "logcategories": logcategories,
        "logcommtypes": logcommtypes,
        "logpriority": logpriority,
        "logproblemtypes": logproblemtypes,
        "logstatus": logstatus,
        "logsubcategories": logsubcategories,
        "logtypes": logtypes,
        "logreport": logreport,
        "schoollist": SchoolList,
        "sessionpost": sessionPost,
        "sessionloginid": sessionLoginID,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/problemLog.html", context)


@csrf_exempt
def problemLog_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    today = date.today().strftime("%Y-%m-%d")
    StartDate = request.POST.get('startdate')
    EndDate = request.POST.get('enddate')
    LogItemID = request.POST.get('logitemid')

    if action == "logenquiry_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=enquirylog')
        cursor = cnxn.cursor()
        cursor.execute("exec spLogItemSelect '" + StartDate + "','" + EndDate + "'")
        LogEnquiryList = cursor.fetchall()

        context = {
            "action": action,
            "logenquirylist": LogEnquiryList,
            "startdate": StartDate,
            "enddate": EndDate
        }
    if action == "logenquiry_response_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=enquirylog')
        cursor = cnxn.cursor()
        cursor.execute("exec spLogResponse '" + LogItemID + "'")
        LogResponseList = cursor.fetchall()

        context = {
            "action": action,
            "logresponselist": LogResponseList,
            "logitemid": LogItemID
        }
    if action == "category_list":
        logtypeid = request.POST.get('logtypeid')
        logcategoryid = request.POST.get('logcategoryid')
        logcategories = LogCategories.objects.using('enquirylog').filter(logtypeid=logtypeid).order_by('ordering')

        context = {
            "action": action,
            "logcategories": logcategories,
            "user_logcategory": logcategoryid
        }
    if action == "subcategory_list":
        logcategoryid = request.POST.get('logcategoryid')
        logsubcategoryid = request.POST.get('logsubcategoryid')
        logsubcategories = LogSubCategories.objects.using('enquirylog').filter(logcategoryid=logcategoryid).order_by(
            'ordering')

        context = {
            "action": action,
            "logsubcategories": logsubcategories,
            "user_logsubcategory": logsubcategoryid
        }
    if action == "priority_list":
        logpriorityid = request.POST.get('logpriorityid')
        logpriority = LogPriority.objects.using('enquirylog').order_by('ordering')

        context = {
            "action": action,
            "logpriority": logpriority,
            "user_logpriority": logpriorityid
        }
    if action == "logschool_list":
        contactschool = request.POST.get('contactschool')
        schoolid = request.POST.get('schoolid')
        SchoolList = Schools.objects.using('enquirylog').filter(schoolid=schoolid).order_by('ordering')

        context = {
            "action": action,
            "schoollist": SchoolList,
            "user_schoolid": schoolid
        }
    if action == "get_schoolname":
        schoolname = request.POST.get('schoolname')
        if schoolname == "":
            return HttpResponse(schoolname)
        schools = Schools.objects.using('schoolmaster').filter(schoolnamee=schoolname)
        if schools:
            schoolname_return = schools[0].schoolnamec
        else:
            schools = Schools.objects.using('schoolmaster').filter(schoolnamec=schoolname)
            if schools:
                schoolname_return = schools[0].schoolnamee
            else:
                schoolname_return = schoolname
        return HttpResponse(schoolname_return)

    if action == "add" or action == "edit":
        logitemid = request.POST.get('logitemid')
        logtypeid = str(request.POST.get("logtypeid"))
        logcategoryid = request.POST.get("logcategoryid")
        logsubcategoryid = request.POST.get("logsubcategoryid")
        logitemdate = request.POST.get("logitemdate")
        schoolid = request.POST.get("schoolid")
        contactschool = request.POST.get("contactschool")
        contactname = request.POST.get("contactname")
        contactemail = request.POST.get("contactemail")
        contactphone = request.POST.get("contactphone")
        logcommtypeid = request.POST.get("logcommtypeid")
        logitemsubject = request.POST.get("logitemsubject")
        logitemdesc = request.POST.get("logitemdesc")
        statusid = str(request.POST.get("statusid"))
        logstaffid = request.POST.get("logstaffid")
        createdate = request.POST.get("createdate")
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

        try:
            if action == "add":
                logitem = LogItems()
            else:
                logitem = LogItems.objects.using('enquirylog').get(logitemid=logitemid)
            if logcategoryid == "":
                logcategoryid = 0
            if logsubcategoryid == "":
                logsubcategoryid = 0
            logitem.logtypeid_id = logtypeid
            logitem.logitemsubject = logitemsubject
            logitem.logitemdesc = logitemdesc
            logitem.logitemdate = logitemdate
            logitem.contactname = contactname
            logitem.contactemail = contactemail
            logitem.contactschool = contactschool
            logitem.contactphone = contactphone
            logitem.statusid_id = statusid
            logitem.logcommtypeid_id = logcommtypeid
            logitem.logstaffid = logstaffid
            logitem.logcategoryid = logcategoryid
            logitem.logsubcategoryid = logsubcategoryid
            logitem.modifydate = datetime_str
            logitem.schoolid = schoolid
            if contactschool == "": logitem.schoolid = ""
            if action == "add": logitem.createdate = datetime_str
            if action == "add" or action == "edit": logitem.save(using='enquirylog')
            if action == "delete": logitem.delete(using='enquirylog')
            messages.success(request, "New Problem Log record was created successfully.")
            return HttpResponse("True")
        except:
            return HttpResponse(
                "False\n" + action + "\n" + logtypeid + "\n" + logcategoryid + "\n" + logsubcategoryid + "\n" + logitemdate + "\n" + schoolid + "\n" + contactschool + "\n" + contactname + "\n" + contactemail + "\n" + contactphone + "\n" + logcommtypeid + "\n" + logitemdesc + "\n" + statusid)

    return render(request, "enquiry_template/problemLog_response.html", context)

def downloadfile(request, insptype, year, code, schoolid):
    if not request.session.get('post'): return redirect('')
    #file_path = os.path.join('E:\\QAIP_INSP_REPORT\\FI\\2019\\1TB39_190586000133\\REPORT', 'EP03 HKFYG Lee Shau Kee Primary School.docx')
    #path = "E:\\QAIP_INSP_REPORT\\FI\\2020\\2TB22_115347000123\\REPORT"
    path = getattr(settings, "PATH_INSP_REPORT", None)+insptype+"\\"+year+"\\"+code+"_"+schoolid+"\\REPORT"
    file_list = os.listdir(path)
    file_single = []
    for filelist in file_list:
        file_single.append(filelist)
    #file_path = os.path.join('E:\\QAIP_INSP_REPORT\\FI\\2019\\1TB39_190586000133\\REPORT', 'EP03 HKFYG Lee Shau Kee Primary School.docx')
    #file_path = os.path.join('E:\\QAIP_INSP_REPORT\\FI\\2020\\2TB22_115347000123\\REPORT', '2TB22 AD and FDPOHL Leung Sing Tak School.docx')
    file_path = os.path.join(path, str(filelist))

    if filelist != "":
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response

def downloadfile2(request, insptype, year, schoolid, filename):
    if not request.session.get('post'): return redirect('')
    path = getattr(settings, "PATH_INSP_REPORT", None)+insptype+"\\"+year+"\\"+schoolid
    file_list = os.listdir(path)
    #file_single = []
    #for filelist in file_list:
    #    file_single.append(filelist)
    file_path = os.path.join(path, filename)

    if file_path != "":
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response

def downloadfilename(request, insptype, year, code, schoolid):
    if not request.session.get('post'): return redirect('')
    path = getattr(settings, "PATH_INSP_REPORT", None)+insptype+"\\"+year+"\\"+code+"_"+schoolid+"\\REPORT"
    file_list = os.listdir(path)
    file_single = []
    for filelist in file_list:
        file_single.append(filelist)
    return filelist

def svaisLoginPwd(request):        
    if not request.session.get('post'): return redirect('')
    svaisusers = SvaisUsers.objects.using('mvcsavis')
    districts1 = Districts.objects.using('schoolmaster')
    
    accessid = 37
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
        "districts1": districts1,     
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/svaisLoginPwd.html", context)

@csrf_exempt
def svaisLoginPwd_response(request):
    if not request.session.get('post'): return redirect('')
    svaisusers = SvaisUsers.objects.using('mvcsvais')
    cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_SVAIS_HOST", None)+';UID='+getattr(settings, "AUTH_SVAIS_USER", None)+';PWD='+getattr(settings, "AUTH_SVAIS_PASSWORD", None)+';Database=mvcsvais')
    cursor = cnxn.cursor()
    cursor.execute("exec sp_SchoolUserInfo ''")
    svaisusers = cursor.fetchall()
    
    districts1 = Districts.objects.using('schoolmaster')

    accessid = 37
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
        "districts1": districts1,
        "svaisusers": svaisusers,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/svaisLoginPwd_response.html", context)

@csrf_exempt
def svaisfLostPwd_response(request, schoolid):
    if not request.session.get('post'): return redirect('')
    svaisusers = SvaisUsers.objects.using('mvcsvais').filter(schoolid=schoolid)
    accessid = 37
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=qadind')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where post = '"+request.session.get('post')+"'")
    menuList = cursor_menu.fetchall()

    context = {
        "svaisusers": svaisusers,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/svaisLoginPwd_letterOfLostPwd.html", context)


def esdaReg(request):
    if not request.session.get('post'): return redirect('')
    schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
    sessions = Sessions.objects.using('schoolmaster')
    districts = Districts.objects.using('schoolmaster')
    financetypes = Financetypes.objects.using('schoolmaster')
    curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
    ssbs = SSBs.objects.using('schoolmaster')

    accessid = 70
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
        "schooltypes": schooltypes,
        "sessions": sessions,
        "districts": districts,
        "financetypes": financetypes,
        "ssbs": ssbs,
        "curriculumtypes": curriculumtypes,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/esdaReg.html", context)

@csrf_exempt
def esdaReg_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    status = request.POST.get('status')
    displaymode = request.POST.get('displaymode')

    if action == "school_list":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SCHOOL_LIST order by SCHOOL_ID")
        schools = cursor.fetchall()
        cursor2 = cnxn.cursor()
        cursor2.execute("select * from SYS_INFO")
        systeminfo = cursor2.fetchall()
        for w in systeminfo:
            if w.INFO_KEY == "SPV": LatestProgramVersion = w.INFO_VALUE
            if w.INFO_KEY == "SDV": LatestDataVersion = w.INFO_VALUE

        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
        sessions = Sessions.objects.using('schoolmaster')
        districts = Districts.objects.using('schoolmaster')
        financetypes = Financetypes.objects.using('schoolmaster')
        curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
        ssbs = SSBs.objects.using('schoolmaster')

        context = {
            "action": action,
            "displaymode": displaymode,
            "schools": schools,
            "schooltypes": schooltypes,
            "sessions": sessions,
            "districts": districts,
            "financetypes": financetypes,
            "curriculumtypes": curriculumtypes,
            "ssbs": ssbs,
            "LatestProgramVersion": LatestProgramVersion,
            "LatestDataVersion": LatestDataVersion,
        }
    return render(request, "enquiry_template/esdaReg_response.html", context)

def esdaClientVersion(request):
    if not request.session.get('post'): return redirect('')
    schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
    sessions = Sessions.objects.using('schoolmaster')
    districts = Districts.objects.using('schoolmaster')
    financetypes = Financetypes.objects.using('schoolmaster')
    curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
    ssbs = SSBs.objects.using('schoolmaster')

    accessid = 91
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
        "schooltypes": schooltypes,
        "sessions": sessions,
        "districts": districts,
        "financetypes": financetypes,
        "ssbs": ssbs,
        "curriculumtypes": curriculumtypes,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/esdaClientVersion.html", context)

@csrf_exempt
def esdaClientVersion_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    status = request.POST.get('status')
    displaymode = request.POST.get('displaymode')

    if action == "school_list":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("select * from VIEW_SCHOOL_LIST where programversion <> '' order by SCHOOL_ID")
        schools = cursor.fetchall()
        cursor2 = cnxn.cursor()
        cursor2.execute("select * from SYS_INFO")
        systeminfo = cursor2.fetchall()
        for w in systeminfo:
            if w.INFO_KEY == "SPV": LatestProgramVersion = w.INFO_VALUE
            if w.INFO_KEY == "SDV": LatestDataVersion = w.INFO_VALUE
        cursor3 = cnxn.cursor()
        cursor3.execute("select * from VIEW_SCHOOL_PROGRAM_VERSION where programversion <> ''")
        programversions = cursor3.fetchall()
        cursor4 = cnxn.cursor()
        cursor4.execute("select * from VIEW_SCHOOL_DATA_VERSION where dataversion <> ''")
        dataversions = cursor4.fetchall()

        LatestCount = 0
        LatestTotalCount = 0
        LatestNotCount = 0
        LatestDataCount = 0
        LatestDataNotCount = 0
        OldCount = 0
        OldTotalCount = 0
        OldNotCount = 0
        for w in programversions:
            if w.programversion == LatestProgramVersion: LatestCount = w.count
            if w.programversion != LatestProgramVersion and str(w.programversion) >= "v5.0.0": LatestNotCount = LatestNotCount + w.count
            if str(w.programversion) >= "v5.0.0": LatestTotalCount = LatestTotalCount + w.count
            if str(w.programversion) < "v5.0.0": OldTotalCount = OldTotalCount + w.count
            if str(w.programversion) == "4.5.7": OldCount = w.count
            if str(w.programversion) < "4.5.7": OldNotCount = OldNotCount + w.count

        for w in dataversions:
            if w.dataversion == LatestDataVersion: LatestDataCount = w.count
            if w.dataversion != LatestDataVersion and str(w.dataversion) >= "v2.0.0": LatestDataNotCount = LatestDataNotCount + w.count

        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
        sessions = Sessions.objects.using('schoolmaster')
        districts = Districts.objects.using('schoolmaster')
        financetypes = Financetypes.objects.using('schoolmaster')
        curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
        ssbs = SSBs.objects.using('schoolmaster')

        context = {
            "action": action,
            "displaymode": displaymode,
            "schools": schools,
            "systeminfo": systeminfo,
            "LatestProgramVersion": LatestProgramVersion,
            "LatestDataVersion": LatestDataVersion,
            "LatestCount": LatestCount,
            "LatestTotalCount": LatestTotalCount,
            "LatestNotCount": LatestNotCount,
            "LatestDataCount": LatestDataCount,
            "LatestDataNotCount": LatestDataNotCount,
            "OldCount": OldCount,
            "OldTotalCount": OldTotalCount,
            "OldNotCount": OldNotCount,
            "programversions": programversions,
            "dataversions": dataversions,
            "schooltypes": schooltypes,
            "sessions": sessions,
            "districts": districts,
            "financetypes": financetypes,
            "curriculumtypes": curriculumtypes,
            "ssbs": ssbs,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
        }
    if action == "program_updated_list":
        # School Data (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor2 = cnxn.cursor()
        cursor2.execute("select * from SYS_INFO")
        systeminfo = cursor2.fetchall()
        for w in systeminfo:
            if w.INFO_KEY == "SPV": LatestProgramVersion = w.INFO_VALUE
            if w.INFO_KEY == "SDV": LatestDataVersion = w.INFO_VALUE
        cursor3 = cnxn.cursor()
        cursor3.execute("select top 100 * from VIEW_SCHOOL_PROGRAM_UPDATE_LOG order by operationtime desc")
        programversions = cursor3.fetchall()

        context = {
            "action": action,
            "displaymode": displaymode,
            "programversions": programversions,
            "LatestProgramVersion": LatestProgramVersion,
            "LatestDataVersion": LatestDataVersion,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
        }
    if action == "school_contact":

        context = {
            "action": action,
            "displaymode": displaymode,
            "programversions": programversions,
            "LatestProgramVersion": LatestProgramVersion,
            "LatestDataVersion": LatestDataVersion,
        }

    return render(request, "enquiry_template/esdaClientVersion_response.html", context)

def dataSubmission(request):
    if not request.session.get('post'): return redirect('')
    year = currentschoolyear()
    schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
    years = ESRschools.objects.using('sqp').filter(insptype='ESR').order_by('-esryear').values('esryear').distinct()
    financetypes = Financetypes.objects.using('schoolmaster')
    curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
    ssbs = SSBs.objects.using('schoolmaster')
    # Latest School Data Submission (QA)
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
    cursor = cnxn.cursor()
    cursor.execute("exec SP_DATA_SUBMISSION_SCHOOL '','2022-09-01','2023-08-31'")
    schoolLatestSubmitList = cursor.fetchmany(10)
    # School Data Submission by year (QA)
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
    cursor = cnxn.cursor()
    cursor.execute("select * from VIEW_SCHOOL_DATA_SUBMISSION_SCHOOL_VERSION_COUNT")
    schoolCountList = cursor.fetchall()
    # School Data Submission by financial  QA)
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
    cursor = cnxn.cursor()
    cursor.execute("select * from VIEW_SCHOOL_DATA_SUBMISSION_SCHOOL_VERSION_FINANCIAL_COUNT")
    schoolFinancialCountList = cursor.fetchall()

    accessid = 5143
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
        "schooltypes": schooltypes,
        "year": year,
        "years": years,
        "financetypes": financetypes,
        "ssbs": ssbs,
        "curriculumtypes": curriculumtypes,
        "schoollatestsubmitlist": schoolLatestSubmitList,
        "schoolcountlist": schoolCountList,
        "schoolfinancialcountlist": schoolFinancialCountList,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/dataSubmission.html", context)

@csrf_exempt
def dataSubmission_response(request):
    if not request.session.get('post'): return redirect('')
    year = request.POST.get('year')
    year1 = int(year)+1
    action = request.POST.get('action')
    displaymode = request.POST.get('displaymode')

    if action == "school_list":
        # Latest School Data Submission (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("exec SP_DATA_SUBMISSION_SCHOOL '','"+year+"-09-01','"+str(year1)+"-08-31'")
        schoolSubmitlist = cursor.fetchall()

        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
        sessions = Sessions.objects.using('schoolmaster')
        districts = Districts.objects.using('schoolmaster')
        financetypes = Financetypes.objects.using('schoolmaster')
        curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
        ssbs = SSBs.objects.using('schoolmaster')

        context = {
            "action": action,
            "displaymode": displaymode,
            "schoolsubmitlist": schoolSubmitlist,
            "schooltypes": schooltypes,
            "sessions": sessions,
            "districts": districts,
            "financetypes": financetypes,
            "curriculumtypes": curriculumtypes,
            "ssbs": ssbs,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
        }
    return render(request, "enquiry_template/dataSubmission_response.html", context)

def kpmSubmission(request):
    if not request.session.get('post'): return redirect('')
    year = request.POST.get('year')
    schoollevel = request.GET.get('schoollevel')
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr(settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
    cursor = cnxn.cursor()
    cursor.execute("SELECT years from VIEW_SCHOOL_DATA_SUBMISSION_YEAR GROUP BY years ORDER BY years DESC")
    years = cursor.fetchall()

    action = request.POST.get('action')

    accessid = 5146
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
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/kpmSubmission.html", context)

@csrf_exempt
def kpmSubmission_response(request):
    if not request.session.get('post'): return redirect('')
    year = request.POST.get('year')
    year1 = int(year)+1
    action = request.POST.get('action')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    schoollevel = request.POST.get('schoollevel')
    reporttype = request.POST.get('reporttype')
    status = request.POST.get('status')
    displaymode = request.POST.get('displaymode')

    if action == "menutab":
        context = {
            "action": action,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "reporttype": reporttype,
            "status": status,
            "displaymode": displaymode,
        }
    if action == "kpmsubmission":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_LIST_NEW_ESDA_COUNT")
        schoolESDACount = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_NEW_ESDA_COUNT WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        schoolSubmitCount = cursor.fetchall()

        # Latest School Data Submission (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        sql = "SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'"
        schoolSubmitlist = cursor.fetchall()

        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
        sessions = Sessions.objects.using('schoolmaster')
        districts = Districts.objects.using('schoolmaster')
        financetypes = Financetypes.objects.using('schoolmaster')
        curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
        ssbs = SSBs.objects.using('schoolmaster')

        context = {
            "action": action,
            "displaymode": displaymode,
            "schoolesdacount": schoolESDACount,
            "schoolsubmitcount": schoolSubmitCount,
            "schoolsubmitlist": schoolSubmitlist,
            "schooltypes": schooltypes,
            "sessions": sessions,
            "districts": districts,
            "financetypes": financetypes,
            "curriculumtypes": curriculumtypes,
            "ssbs": ssbs,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
            "sql": sql,
        }
    if action == "district":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_SCHOOL_DISTRICT_COUNT WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        schoolDistrictCount = cursor.fetchall()
        cursor.execute("exec SP_DATA_SUBMISSION_SCHOOL_LEVEL '','P','"+str(year)+"-"+str(year1-2000)+"'")
        schoolDistrictPrimaryCount = cursor.fetchall()
        cursor.execute("exec SP_DATA_SUBMISSION_SCHOOL_LEVEL '','S','"+str(year)+"-"+str(year1-2000)+"'")
        schoolDistrictSecondaryCount = cursor.fetchall()
        cursor.execute("exec SP_DATA_SUBMISSION_SCHOOL_LEVEL '','SP','"+str(year)+"-"+str(year1-2000)+"'")
        schoolDistrictSpecialCount = cursor.fetchall()

        #cursor.execute("exec SP_SCHOOL_LIST_DATA_SUBMISSION '"+str(year)+"-"+str(year1-2000)+"',''")

        cursor.execute("SELECT * from VIEW_SCHOOL_LIST_DISTRICT_COUNT")
        schoolDistrictTotalCount = cursor.fetchall()

        context = {
            "action": action,
            "displaymode": displaymode,
            "schooldistrictcount": schoolDistrictCount,
            "schooldistrictprimarycount": schoolDistrictPrimaryCount,
            "schooldistrictsecondarycount": schoolDistrictSecondaryCount,
            "schooldistrictspecialcount": schoolDistrictSpecialCount,
            "schooldistricttotalcount": schoolDistrictTotalCount,
        }
    if action == "districtdetail":
        yearname = request.POST.get('yearname')
        district = request.POST.get('district')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("exec SP_SCHOOL_LIST_DATA_SUBMISSION '"+str(year)+"-"+str(year1-2000)+"','','" + district + "'")
        schoolDistrict = cursor.fetchall()
        cursor.execute("SELECT CODE_CNAME FROM SYS_CODE WHERE (CODE_TYPE = 1010) and CODE_KEY = '" + district + "'")
        DistrictName = cursor.fetchall()
        sql = "exec SP_SCHOOL_LIST_DATA_SUBMISSION '"+str(year)+"-"+str(year1-2000)+"','','" + district + "'"
        try:
            if DistrictName:
                districtname = DistrictName[0].CODE_CNAME
            else:
                districtname = "所有地區"
        except:
            districtname = ""

        context = {
            "action": action,
            "displaymode": displaymode,
            "district": district,
            "districtname": districtname,
            "schooldistrict": schoolDistrict,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
            "sql": sql
        }
    if action == "kpmcontent":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_LIST_NEW_ESDA_COUNT")
        schoolESDACount = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_NEW_ESDA_COUNT WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        schoolSubmitCount = cursor.fetchall()

        # Latest School Data Submission (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP_KPM WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        sql = "SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP_KPM WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'"
        schoolSubmitlist = cursor.fetchall()

        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
        sessions = Sessions.objects.using('schoolmaster')
        districts = Districts.objects.using('schoolmaster')
        financetypes = Financetypes.objects.using('schoolmaster')
        curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
        ssbs = SSBs.objects.using('schoolmaster')

        context = {
            "action": action,
            "displaymode": displaymode,
            "schoolesdacount": schoolESDACount,
            "schoolsubmitcount": schoolSubmitCount,
            "schoolsubmitlist": schoolSubmitlist,
            "schooltypes": schooltypes,
            "sessions": sessions,
            "districts": districts,
            "financetypes": financetypes,
            "curriculumtypes": curriculumtypes,
            "ssbs": ssbs,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
            "sql": sql,
        }
    if action == "shscontent":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_LIST_NEW_ESDA_COUNT")
        schoolESDACount = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_NEW_ESDA_COUNT WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        schoolSubmitCount = cursor.fetchall()

        # Latest School Data Submission (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP_SHS WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        sql = "SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP_SHS WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'"
        schoolSubmitlist = cursor.fetchall()

        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
        sessions = Sessions.objects.using('schoolmaster')
        districts = Districts.objects.using('schoolmaster')
        financetypes = Financetypes.objects.using('schoolmaster')
        curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
        ssbs = SSBs.objects.using('schoolmaster')

        context = {
            "action": action,
            "displaymode": displaymode,
            "schoolesdacount": schoolESDACount,
            "schoolsubmitcount": schoolSubmitCount,
            "schoolsubmitlist": schoolSubmitlist,
            "schooltypes": schooltypes,
            "sessions": sessions,
            "districts": districts,
            "financetypes": financetypes,
            "curriculumtypes": curriculumtypes,
            "ssbs": ssbs,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
            "sql": sql,
        }
    if action == "apasocontent":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_LIST_NEW_ESDA_COUNT")
        schoolESDACount = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_NEW_ESDA_COUNT WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        schoolSubmitCount = cursor.fetchall()

        # Latest School Data Submission (QA)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP_APASO WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'")
        sql = "SELECT * from VIEW_SCHOOL_DATA_SUBMISSION_GROUP_APASO WHERE YEAR_NAME = '"+str(year)+"-"+str(year1-2000)+"'"
        schoolSubmitlist = cursor.fetchall()

        schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypemainflag=True).order_by('sequence')
        sessions = Sessions.objects.using('schoolmaster')
        districts = Districts.objects.using('schoolmaster')
        financetypes = Financetypes.objects.using('schoolmaster')
        curriculumtypes = Curriculumtypes.objects.using('schoolmaster')
        ssbs = SSBs.objects.using('schoolmaster')

        context = {
            "action": action,
            "displaymode": displaymode,
            "schoolesdacount": schoolESDACount,
            "schoolsubmitcount": schoolSubmitCount,
            "schoolsubmitlist": schoolSubmitlist,
            "schooltypes": schooltypes,
            "sessions": sessions,
            "districts": districts,
            "financetypes": financetypes,
            "curriculumtypes": curriculumtypes,
            "ssbs": ssbs,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
            "sql": sql,
        }
    return render(request, "enquiry_template/kpmSubmission_response.html", context)

def postESR(request):
    if not request.session.get('post'): return redirect('')
    years = ESRschools.objects.using('sqp').order_by('-esryear').values('esryear').distinct()
    year = years[0]['esryear']

    accessid = 38
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
        "years": years,
        "user_year": year,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/postESR.html", context)

@csrf_exempt
def postESR_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    loginid = request.POST.get('loginid')
    if loginid == 0:
        loginid = ""
    user_year = year
    user_loginid = loginid

    if action == "inspection_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_PostSurvey_withDate 'ESR'," + str(year) + ",'" + str(loginid) + "'")
        inspection_list = cursor.fetchall()
        teammember_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                # Post Survey Data
                cnxn1 = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr(settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
                cursor1 = cnxn1.cursor()
                cursor1.execute("select * from VIEW_ONLINE_SURVEY_LIST where SCRN = '" + str(w.SchoolID) + "' and SUBSTRING(YEAR_NAME,1,4) = '" + str(w.esrYear) + "' order by YEAR_NAME DESC")
                postsurveydata_list = cursor1.fetchall()
                file_list = 'N/A'
                error_msg = ''
                if postsurveydata_list:
                    for v in postsurveydata_list:
                        path = getattr(settings, "PATH_INSP_REPORT", None) + w.InspType + "\\" + w.esrYear + "\\" + w.code + "_" + w.SchoolID + "\\SCH"
                        try:
                            file_list = fnmatch.filter(os.listdir(path), '*.xls*')
                            file_list = file_list + fnmatch.filter(os.listdir(path), '*,doc*')
                            file_list = file_list + fnmatch.filter(os.listdir(path), '*.pdf')
                        except Exception as e:
                            os.makedirs(path)
                            error_msg = str(e)
                #teammember_list.append({'schoolid': w.SchoolID, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'esrStartDate': w.esrStartDate, 'postsurveydatas': postsurveydata_list})
                teammember_list.append({'schoolid': w.SchoolID,'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'postsurveydatas': postsurveydata_list, 'file_list': file_list, 'error_msg': error_msg})
                if w.schoolID2 != "NULL" and "EX" not in w.code:
                    # Post Survey Data
                    cnxn1 = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr(settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
                    cursor1 = cnxn1.cursor()
                    cursor1.execute("select * from VIEW_ONLINE_SURVEY_LIST where SCRN = '" + str(w.schoolID2) + "' and SUBSTRING(YEAR_NAME,1,4) = '" + str(w.esrYear) + "' order by YEAR_NAME DESC")
                    postsurveydata_list = cursor1.fetchall()
                    file_list = 'N/A'
                    error_msg = ''
                    if postsurveydata_list:
                        for v in postsurveydata_list:
                            path = getattr(settings, "PATH_INSP_REPORT", None) + w.InspType + "\\" + w.esrYear + "\\" + w.code + "_" + w.schoolID2 + "\\SCH"
                            try:
                                file_list = fnmatch.filter(os.listdir(path), '*.xls*')
                                file_list = file_list + fnmatch.filter(os.listdir(path), '*,doc*')
                                file_list = file_list + fnmatch.filter(os.listdir(path), '*.pdf')
                            except Exception as e:
                                os.makedirs(path)
                                error_msg = str(e)
                    teammember_list.append({'schoolid': w.schoolID2, 'schoolid2': w.SchoolID, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'postsurveydatas': postsurveydata_list, 'file_list': file_list, 'error_msg': error_msg})

            except Exception as e:
                 sSQL = 'N/A'

        context = {
            "action": action,
            "user_year": user_year,
            "user_loginid": user_loginid,
            "teammember_list": teammember_list,
            "sql": sSQL,
        }
    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "loginid": loginid,
            "user_year": user_year,
            "user_loginid": user_loginid,
            "team_list": team_list,
        }
    return render(request, "enquiry_template/postESR_response.html", context)

def postFI(request):
    if not request.session.get('post'): return redirect('')
    years = ESRschools.objects.using('sqp').order_by('-esryear').values('esryear').distinct()
    year = years[0]['esryear']

    accessid = 3127
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
        "years": years,
        "user_year": year,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/postFI.html", context)

@csrf_exempt
def postFI_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    loginid = request.POST.get('loginid')
    inspectiontype = request.POST.get('inspectiontype')
    if loginid == 0:
        loginid = ""
    user_year = year
    user_loginid = loginid
    user_inspectiontype = inspectiontype

    if action == "inspection_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_PostSurvey_withDate 'FI'," + str(year) + ",'" + str(loginid) + "'")
        inspection_list = cursor.fetchall()
        teammember_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                # Post Survey Data
                cnxn1 = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr(settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
                cursor1 = cnxn1.cursor()
                cursor1.execute("select * from VIEW_ONLINE_SURVEY_LIST where SCRN like SUBSTRING('" + str(w.SchoolID) + "',1,6)+'%' and SUBSTRING(YEAR_NAME,1,4) = '" + str(w.esrYear) + "' order by YEAR_NAME DESC")
                postsurveydata_list = cursor1.fetchall()
                file_list = 'N/A'
                error_msg = ''
                if postsurveydata_list:
                    for v in postsurveydata_list:
                        path = getattr(settings, "PATH_INSP_REPORT", None) + w.InspType + "\\" + w.esrYear + "\\" + w.code + "_" + w.SchoolID + "\\SCH"
                        try:
                            file_list = fnmatch.filter(os.listdir(path), '*.xls*')
                            file_list = file_list + fnmatch.filter(os.listdir(path), '*,doc*')
                            file_list = file_list + fnmatch.filter(os.listdir(path), '*.pdf')
                        except Exception as e:
                            os.makedirs(path)
                            error_msg = str(e)
                if not w.code in "TB":
                    teammember_list.append({'schoolid': w.SchoolID, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'postsurveydatas': postsurveydata_list, 'file_list': file_list, 'error_msg': error_msg})
            except Exception as e:
                 sSQL = 'N/A'

        context = {
            "action": action,
            "user_year": user_year,
            "user_loginid": user_loginid,
            "user_inspectiontype": user_inspectiontype,
            "teammember_list": teammember_list,
            "sql": sSQL,
        }
    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "loginid": loginid,
            "user_loginid": loginid,
            "team_list": team_list,
        }
    return render(request, "enquiry_template/postFI_response.html", context)


def postSurveyPassword(request):
    if not request.session.get('post'): return redirect('')
    where_clause = {
        'esryear__gte': 2021
    }
    years = ESRschools.objects.using('sqp').filter(**where_clause).order_by('-esryear').values('esryear').distinct()
    year = years[0]['esryear']

    accessid = 5142
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
        "years": years,
        "user_year": year,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/postSurveyPassword.html", context)

@csrf_exempt
def postSurveyPassword_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    loginid = request.POST.get('loginid')
    inspectiontype = request.POST.get('inspectiontype')
    if loginid == 0:
        loginid = ""
    user_year = year
    user_loginid = loginid
    user_inspectiontype = inspectiontype

    if action == "inspection_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_withDate '" + str(inspectiontype) + "'," + str(year) + ",'" + str(loginid) + "'")
        inspection_list = cursor.fetchall()
        teammember_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                # Post Survey Data
                cnxn1 = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr(settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
                cursor1 = cnxn1.cursor()
                cursor1.execute("select * from VIEW_ONLINE_SURVEY_PASSWORD where SCRN = '" + str(w.SchoolID) + "' and SUBSTRING(YEAR_NAME,1,4) = '" + str(w.esrYear) + "' order by YEAR_NAME DESC")
                postsurveydata_list = cursor1.fetchall()
                file_list = 'N/A'
                error_msg = ''
                tb_index = w.code.find('TB')
                if tb_index == -1:
                    teammember_list.append({'schoolid': w.SchoolID, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'postsurveydatas': postsurveydata_list, 'error_msg': error_msg})
            except Exception as e:
                 sSQL = 'N/A'

        context = {
            "action": action,
            "user_year": user_year,
            "user_loginid": user_loginid,
            "user_inspectiontype": user_inspectiontype,
            "teammember_list": teammember_list,
            "sql": sSQL,
        }
    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "loginid": loginid,
            "user_loginid": loginid,
            "team_list": team_list,
        }
    return render(request, "enquiry_template/postSurveyPassword_response.html", context)

def postSurveyReportEnquiry(request):
    if not request.session.get('post'): return redirect('')
    years = ESRschools.objects.using('sqp').order_by('-esryear').values('esryear').distinct()
    year = years[0]['esryear']

    accessid = 121
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
        "years": years,
        "user_year": year,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/postSurveyReportEnquiry.html", context)

@csrf_exempt
def postSurveyReportEnquiry_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    loginid = request.POST.get('loginid')
    inspectiontype = request.POST.get('inspectiontype')
    status = request.POST.get('status')
    if loginid == 0:
        loginid = ""
    user_year = year
    user_loginid = loginid
    user_inspectiontype = inspectiontype
    user_status = status

    if action == "inspection_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_QAIP_HOST", None) + ';UID=' + getattr(settings, "AUTH_QAIP_USER", None) + ';PWD=' + getattr(settings, "AUTH_QAIP_PASSWORD", None) + ';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spInspectionFiles_Sort_PostSurvey_withDate '" + str(inspectiontype) + "'," + str(year) + ",'" + str(loginid) + "'")
        inspection_list = cursor.fetchall()
        teammember_list = []
        sSQL = ''
        for w in inspection_list:
            try:
                # Post Survey Data
                cnxn1 = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr(settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
                cursor1 = cnxn1.cursor()
                cursor1.execute("select * from VIEW_ONLINE_SURVEY_LIST where SCRN = '" + str(w.SchoolID) + "' and SUBSTRING(YEAR_NAME,1,4) = '" + str(w.esrYear) + "' order by YEAR_NAME DESC")
                postsurveydata_list = cursor1.fetchall()
                file_list = 'N/A'
                error_msg = ''
                if postsurveydata_list:
                    for v in postsurveydata_list:
                        path = getattr(settings, "PATH_INSP_REPORT", None) + w.InspType + "\\" + w.esrYear + "\\" + w.code + "_" + w.SchoolID + "\\SCH"
                        try:
                            file_list = fnmatch.filter(os.listdir(path), '*.xls*')
                            file_list = file_list + fnmatch.filter(os.listdir(path), '*,doc*')
                            file_list = file_list + fnmatch.filter(os.listdir(path), '*.pdf')
                        except Exception as e:
                            os.makedirs(path)
                            error_msg = str(e)
                #teammember_list.append({'schoolid': w.SchoolID, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'esrStartDate': w.esrStartDate, 'postsurveydatas': postsurveydata_list})
                teammember_list.append({'schoolid': w.SchoolID,'schoolid2': w.schoolID2, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'postsurveydatas': postsurveydata_list, 'file_list': file_list, 'error_msg': error_msg})
                if w.schoolID2 != "NULL" and "EX" not in w.code:
                    # Post Survey Data
                    cnxn1 = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr(settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
                    cursor1 = cnxn1.cursor()
                    cursor1.execute("select * from VIEW_ONLINE_SURVEY_LIST where SCRN = '" + str(w.schoolID2) + "' and SUBSTRING(YEAR_NAME,1,4) = '" + str(w.esrYear) + "' order by YEAR_NAME DESC")
                    postsurveydata_list = cursor1.fetchall()
                    file_list = 'N/A'
                    error_msg = ''
                    if postsurveydata_list:
                        for v in postsurveydata_list:
                            path = getattr(settings, "PATH_INSP_REPORT",
                                           None) + w.InspType + "\\" + w.esrYear + "\\" + w.code + "_" + w.schoolID2 + "\\SCH"
                            try:
                                file_list = fnmatch.filter(os.listdir(path), '*.xls*')
                                file_list = file_list + fnmatch.filter(os.listdir(path), '*,doc*')
                                file_list = file_list + fnmatch.filter(os.listdir(path), '*.pdf')
                            except Exception as e:
                                os.makedirs(path)
                                error_msg = str(e)
                    teammember_list.append({'schoolid': w.schoolID2, 'schoolid2': w.SchoolID, 'code': w.code, 'esryear': w.esrYear, 'schoolNameE': w.schoolNameE, 'schoolNameC': w.schoolNameC, 'InspType': w.InspType, 'LoginNameDesc': w.LoginNameDesc, 'PostDesc': w.PostDesc, 'esrStartDate': w.esrStartDate, 'esrEndDate': w.esrEndDate, 'postsurveydatas': postsurveydata_list, 'file_list': file_list, 'error_msg': error_msg})

            except Exception as e:
                 sSQL = 'N/A'

        context = {
            "action": action,
            "user_year": user_year,
            "user_loginid": user_loginid,
            "user_inspectiontype": user_inspectiontype,
            "user_status": user_status,
            "teammember_list": teammember_list,
            "sql": sSQL,
        }
    if action == "team_list":
        team_list = []
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPESRSchoolTeamList '" + str(year) + "', '', ''")
        team_list = cursor.fetchall()

        context = {
            "action": action,
            "loginid": loginid,
            "user_loginid": loginid,
            "team_list": team_list,
        }
    return render(request, "enquiry_template/postSurveyReportEnquiry_response.html", context)


@csrf_exempt
def sdpInfo(request):
    if not request.session.get('post'): return redirect('')
    years = ESRschools.objects.using('sqp').filter(insptype='ESR').order_by('-esryear').values('esryear').distinct()
    schoollevel = request.GET.get('schoollevel')
    action = request.POST.get('action')

    accessid = 120
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('post'),request.session.get('post_org'))
    context = {
        "action": action,
        "years": years,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "enquiry_template/sdpInfo.html", context)


@csrf_exempt
def sdpInfo_response(request):
    if not request.session.get('post'): return redirect('')
    action = request.POST.get('action')
    year = request.POST.get('year')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    schoollevel = request.POST.get('schoollevel')
    inspectiontype = request.POST.get('inspectiontype')
    displaymode = request.POST.get('displaymode')

    if action == "menutab":
        context = {
            "action": action,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "displaymode": displaymode,
        }
    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionList_School_Count where year_name = '"+year+"'")
        schoolCountList = cursor.fetchall()


        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=sqp')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_InpsectionType_School_Count where year_name = '"+year+"'")
        insptypeschoolCountList = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=lofform')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_LOFForm_InspType_Outstanding where year_name = '"+year+"'")
        LOFInspTypeOutstandingCountList = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=schoolmaster')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_School_Development_Cycle_SchoolType_List")
        schoolSDCCountList = cursor.fetchall()

        selected_year = int(year) - 1999
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=schoolmaster')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_School_Development_Cycle_District_List where year_digits = '" +str(selected_year)+ "'")
        schoolSDCDistrictCountList = cursor.fetchall()

        context = {
            "action": action,
            "selectedyear": year,
            "selectedyearend": int(year)-1999,
            "year": year,
            "start_date": start_date,
            "end_date": end_date,
            "schoollevel": schoollevel,
            "inspectiontype": inspectiontype,
            "displaymode": displaymode,
            "schoolcountlist": schoolCountList,
            "schoolsdccountlist": schoolSDCCountList,
            "schoolsdcdistrictcountlist": schoolSDCDistrictCountList,
            "insptypeschoolCountList": insptypeschoolCountList,
            "lofinsptypeoutstandingcountlist": LOFInspTypeOutstandingCountList,
        }
    if action == "report":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_QAIP_HOST", None)+';UID='+getattr(settings, "AUTH_QAIP_USER", None)+';PWD='+getattr(settings, "AUTH_QAIP_PASSWORD", None)+';Database=schoolmaster')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_School_Development_Cycle_Full_List")
        schools = cursor.fetchall()
        selected_year = int(year) - 1999
        selectedsdcyear = "/" + str(selected_year)

        context = {
            "action": action,
            "schools": schools,
            "displaymode": displaymode,
            "selectedyear": year,
            "selectedsdcyear": selectedsdcyear,
            "url_school_profile_primary": getattr(settings, "URL_SCHOOL_PROFILE_PRIMARY", None),
            "url_school_profile_secondary": getattr(settings, "URL_SCHOOL_PROFILE_SECONDARY", None),
            "url_school_profile_special": getattr(settings, "URL_SCHOOL_PROFILE_SPECIAL", None),
        }
    return render(request, "enquiry_template/sdpInfo_response.html", context)

def pageviewlog(accessid, loginid, username, post_org):
    pageview = PageView()
    pageview.loginid = loginid
    pageview.username = username
    pageview.logdatetime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    pageview.subcatid = accessid
    subcategory = SubCategories.objects.using('infinyrealty').get(subcatid=accessid)
    pageview.pagename = subcategory.subcatname
    pageview.logintype = "Live"
    pageview.save(using='infinyrealty')