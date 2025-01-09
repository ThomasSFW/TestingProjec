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
from django.db.models import Max
import json
import pyodbc
import requests
import datetime
import os
import hashlib
import random
import string
from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks, Focusgroup, Focussubtypes
from InfinyRealty_app.models import PageView, CodeDetails, Contents, ContentDetails

from django.conf import settings

def common(request):
    #if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 45
    request.session['accessid'] = accessid
    #users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='infinyrealty')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_team": team,
        "usagelist": UsageList,
    }
    return render(request, "web_template/common.html", context)

def about_main(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    content_list = Contents.objects.using('infinyrealty').filter(status=1).order_by('sequence')
    content_detail_list = ContentDetails.objects.using('infinyrealty').filter(content_id=1).order_by('sequence')
    content_id = 1

    accessid = 5162
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
        "user_content_id": content_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "content_list": content_list,
        "content_detail_list": content_detail_list,
    }
    return render(request, "content_template/about_main.html", context)

@csrf_exempt
def about_main_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    content_id = str(request.POST.get('content_id'))
    user_content_id = content_id

    if action == "content_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblContentDetail where (1 = case when '"+content_id+"' = '' then 1 when content_id = '"+content_id+"' then 1 else 0 end) and status = 1")
        content_detail_list = cursor.fetchall()

        context = {
            "action": action,
            "user_content_id": user_content_id,
            "content_detail_list": content_detail_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            content_detail_id = request.POST.get('content_detail_id')
            content_id = request.POST.get('content_id')
            content_detail_name = request.POST.get('content_detail_name')
            content_detail_name_s = request.POST.get('content_detail_name_s')
            content_detail_name_e = request.POST.get('content_detail_name_e')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    contentdetail = ContentDetails()
                else:
                    contentdetail = ContentDetails.objects.using('infinyrealty').get(content_detail_id=content_detail_id)
                contentdetail.content_id = content_id
                contentdetail.content_detail_name = content_detail_name
                contentdetail.content_detail_name_s = content_detail_name_s
                contentdetail.content_detail_name_e = content_detail_name_e
                contentdetail.sequence = sequence
                contentdetail.status = status
                contentdetail.modify_date = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    contentdetail.delete(using='infinyrealty')
                else:
                    contentdetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)

    return render(request, "content_template/about_main_response.html", context)

def terms_main(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    content_list = Contents.objects.using('infinyrealty').filter(status=1).order_by('sequence')
    content_detail_list = ContentDetails.objects.using('infinyrealty').filter(content_id=2).order_by('sequence')
    content_id = 2

    accessid = 5159
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
        "user_content_id": content_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "content_list": content_list,
        "content_detail_list": content_detail_list,
    }
    return render(request, "content_template/terms_main.html", context)

@csrf_exempt
def terms_main_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    content_id = str(request.POST.get('content_id'))
    user_content_id = content_id

    if action == "content_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblContentDetail where (1 = case when '"+content_id+"' = '' then 1 when content_id = '"+content_id+"' then 1 else 0 end) and status = 1")
        content_detail_list = cursor.fetchall()

        context = {
            "action": action,
            "user_content_id": user_content_id,
            "content_detail_list": content_detail_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            content_detail_id = request.POST.get('content_detail_id')
            content_id = request.POST.get('content_id')
            content_detail_name = request.POST.get('content_detail_name')
            content_detail_name_s = request.POST.get('content_detail_name_s')
            content_detail_name_e = request.POST.get('content_detail_name_e')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    contentdetail = ContentDetails()
                else:
                    contentdetail = ContentDetails.objects.using('infinyrealty').get(content_detail_id=content_detail_id)
                contentdetail.content_id = content_id
                contentdetail.content_detail_name = content_detail_name
                contentdetail.content_detail_name_s = content_detail_name_s
                contentdetail.content_detail_name_e = content_detail_name_e
                contentdetail.sequence = sequence
                contentdetail.status = status
                contentdetail.modify_date = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    contentdetail.delete(using='infinyrealty')
                else:
                    contentdetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)

    return render(request, "content_template/terms_main_response.html", context)

def disclaimer_main(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    content_list = Contents.objects.using('infinyrealty').filter(status=1).order_by('sequence')
    content_detail_list = ContentDetails.objects.using('infinyrealty').filter(content_id=3).order_by('sequence')
    content_id = 3

    accessid = 5160
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
        "user_content_id": content_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "content_list": content_list,
        "content_detail_list": content_detail_list,
    }
    return render(request, "content_template/disclaimer_main.html", context)

@csrf_exempt
def disclaimer_main_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    content_id = str(request.POST.get('content_id'))
    user_content_id = content_id

    if action == "content_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblContentDetail where (1 = case when '"+content_id+"' = '' then 1 when content_id = '"+content_id+"' then 1 else 0 end) and status = 1")
        content_detail_list = cursor.fetchall()

        context = {
            "action": action,
            "user_content_id": user_content_id,
            "content_detail_list": content_detail_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            content_detail_id = request.POST.get('content_detail_id')
            content_id = request.POST.get('content_id')
            content_detail_name = request.POST.get('content_detail_name')
            content_detail_name_s = request.POST.get('content_detail_name_s')
            content_detail_name_e = request.POST.get('content_detail_name_e')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    contentdetail = ContentDetails()
                else:
                    contentdetail = ContentDetails.objects.using('infinyrealty').get(content_detail_id=content_detail_id)
                contentdetail.content_id = content_id
                contentdetail.content_detail_name = content_detail_name
                contentdetail.content_detail_name_s = content_detail_name_s
                contentdetail.content_detail_name_e = content_detail_name_e
                contentdetail.sequence = sequence
                contentdetail.status = status
                contentdetail.modify_date = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    contentdetail.delete(using='infinyrealty')
                else:
                    contentdetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)

    return render(request, "content_template/disclaimer_main_response.html", context)

def privacy_main(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    content_list = Contents.objects.using('infinyrealty').filter(status=1).order_by('sequence')
    content_detail_list = ContentDetails.objects.using('infinyrealty').filter(content_id=4).order_by('sequence')
    content_id = 4

    accessid = 5161
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
        "user_content_id": content_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "content_list": content_list,
        "content_detail_list": content_detail_list,
    }
    return render(request, "content_template/privacy_main.html", context)

@csrf_exempt
def privacy_main_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    content_id = str(request.POST.get('content_id'))
    user_content_id = content_id

    if action == "content_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblContentDetail where (1 = case when '"+content_id+"' = '' then 1 when content_id = '"+content_id+"' then 1 else 0 end) and status = 1")
        content_detail_list = cursor.fetchall()

        context = {
            "action": action,
            "user_content_id": user_content_id,
            "content_detail_list": content_detail_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            content_detail_id = request.POST.get('content_detail_id')
            content_id = request.POST.get('content_id')
            content_detail_name = request.POST.get('content_detail_name')
            content_detail_name_s = request.POST.get('content_detail_name_s')
            content_detail_name_e = request.POST.get('content_detail_name_e')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    contentdetail = ContentDetails()
                else:
                    contentdetail = ContentDetails.objects.using('infinyrealty').get(content_detail_id=content_detail_id)
                contentdetail.content_id = content_id
                contentdetail.content_detail_name = content_detail_name
                contentdetail.content_detail_name_s = content_detail_name_s
                contentdetail.content_detail_name_e = content_detail_name_e
                contentdetail.sequence = sequence
                contentdetail.status = status
                contentdetail.modify_date = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    contentdetail.delete(using='infinyrealty')
                else:
                    contentdetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)

    return render(request, "content_template/privacy_main_response.html", context)

def news_main(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    today = datetime.datetime.now()

    content_list = Contents.objects.using('infinyrealty').filter(status=1).order_by('sequence')
    content_detail_list = ContentDetails.objects.using('infinyrealty').filter(content_id=1).order_by('sequence')
    content_id = 5

    accessid = 5167
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
        "user_content_id": content_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "content_list": content_list,
        "content_detail_list": content_detail_list,
        "today": today,
    }
    return render(request, "content_template/news_main.html", context)

@csrf_exempt
def news_main_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    content_id = str(request.POST.get('content_id'))
    user_content_id = content_id

    if action == "content_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblContentDetail where (1 = case when '"+content_id+"' = '' then 1 when content_id = '"+content_id+"' then 1 else 0 end) and status = 1")
        content_detail_list = cursor.fetchall()

        context = {
            "action": action,
            "user_content_id": user_content_id,
            "content_detail_list": content_detail_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            create_date = request.POST.get('create_date')
            content_detail_id = request.POST.get('content_detail_id')
            content_id = request.POST.get('content_id')
            content_detail_title = request.POST.get('content_detail_title')
            content_detail_title_s = request.POST.get('content_detail_title_s')
            content_detail_title_e = request.POST.get('content_detail_title_e')
            content_detail_name = request.POST.get('content_detail_name')
            content_detail_name_s = request.POST.get('content_detail_name_s')
            content_detail_name_e = request.POST.get('content_detail_name_e')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    contentdetail = ContentDetails()
                    contentdetail.create_date = create_date
                else:
                    contentdetail = ContentDetails.objects.using('infinyrealty').get(content_detail_id=content_detail_id)
                contentdetail.content_id = content_id
                contentdetail.content_detail_title = content_detail_title
                contentdetail.content_detail_title_s = content_detail_title_s
                contentdetail.content_detail_title_e = content_detail_title_e
                contentdetail.content_detail_name = content_detail_name
                contentdetail.content_detail_name_s = content_detail_name_s
                contentdetail.content_detail_name_e = content_detail_name_e
                contentdetail.sequence = sequence
                contentdetail.status = status
                contentdetail.modify_date = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    contentdetail.delete(using='infinyrealty')
                else:
                    contentdetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)

    return render(request, "content_template/news_main_response.html", context)

def account(request):
    #if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 45
    request.session['accessid'] = accessid
    #users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='infinyrealty')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_team": team,

        "usagelist": UsageList,
    }
    return render(request, "web_template/account.html", context)

def property_show(request):
    #if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 45
    request.session['accessid'] = accessid
    #users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='infinyrealty')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_team": team,

        "usagelist": UsageList,
    }
    return render(request, "web_template/property_show1.html", context)

def search_result(request):
    #if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 45
    request.session['accessid'] = accessid
    #users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='infinyrealty')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_team": team,

        "usagelist": UsageList,
    }
    return render(request, "web_template/search_result.html", context)

def contact(request):
    #if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 45
    request.session['accessid'] = accessid
    #users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='infinyrealty')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_team": team,

        "usagelist": UsageList,
    }
    return render(request, "web_template/contact.html", context)

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

