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
import json
import pyodbc
import urllib.parse as urlparse
import requests
import urllib.request
import shutil
import os, fnmatch
import math
import numbers
import datetime
import socket
from django.conf import settings
from django import template
import sys
import zipfile
import subprocess
from django.http import HttpResponse
from django.db.models import Max
import time
import paho.mqtt.client as mqtt
from PIL import ImageDraw
from PIL import Image, ImageEnhance
from PIL import ImageFont
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import TimeoutError as TimeoutException
#import win32com.shell.shell as shell
#import pythoncom

register = template.Library()

from InfinyRealty_app.models import ESRschools, InspectorAllocation, QAI, Focusgroup, Focustype, Focussubtypes, CustomUser, Staffs
from InfinyRealty_app.models import Tabs, Categories, SubCategories, PageView, Users, Teams, Ranks, Schools, Schooltypes, Sessions, Districts, Financetypes, ESRschoolsER, Officers
from InfinyRealty_app.models import SchoolInspReport
from InfinyRealty_app.models import Shops, Codes, CodeDetails, Tables, PropertyUsages, PropertyFiles, TransactionRecords
from InfinyRealty_app.models import ESCPOSManager

def shopList(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')

    accessid = 5150
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
    }
    return render(request, "maintenance_template/shopList.html", context)

@csrf_exempt
def shopList_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    user_team = team

    if action == "shop_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblShop where (1 = case when '"+team+"' = '' then 1 when shop_code = '"+team+"' then 1 else 0 end)")
        sql = "select * from tblShop where (1 = case when '"+team+"' = '' then 1 when shop_code = '"+team+"' then 1 else 0 end)"
        shop_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "shop_list": shop_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            #try:
            #    file = request.FILES['file']
            #except Exception as e:
            #    action = action
            action = action
            shop_id = request.POST.get('shop_id')
            shop_name = request.POST.get('shop_name')
            shop_name_e = request.POST.get('shop_name_e')
            shop_address = request.POST.get('shop_address')
            phone_area_code = request.POST.get('phone_area_code')
            phone_number = request.POST.get('phone_number')
            fax_area_code = request.POST.get('fax_area_code')
            fax_number = request.POST.get('fax_number')
            opening_hours = request.POST.get('opening_hours')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                #try:
                #    path = getattr(settings, "PATH_OTHER", None) + "USERICON" + "\\" + shop_id
                #    if not os.path.exists(path):
                #        os.makedirs(path)
                #    path = os.path.join(path, file.name)
                #    with open(path, 'wb') as destination:
                #        for chunk in file.chunks():
                #            destination.write(chunk)
                #except Exception as e:
                #    loginid = loginid
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    shop = Shops()
                    shop.shop_id = shop.objects.using('infinyrealty').aggregate(Max('shop_id'))['shop_id__max'] + 1
                else:
                    if action == "delete":
                        shop = Shops.objects.using('infinyrealty').get(shop_id=shop_id)
                    else:
                        shop = Shops.objects.using('infinyrealty').get(shop_id=shop_id)
                        shop.shop_id = shop_id
                shop.shop_name = shop_name
                shop.shop_name_e = shop_name_e
                shop.shop_address = shop_address
                shop.phone_area_code = phone_area_code
                shop.phone_number = phone_number
                shop.fax_area_code = fax_area_code
                shop.fax_number = fax_number
                shop.opening_hours = opening_hours
                shop.status = status
                shop.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    shop.delete(using='infinyrealty')
                else:
                    shop.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            recordid = request.POST.get('recordid')
            loginid = request.POST.get('loginid')
            username = request.POST.get('username')
            loginnamedesc = request.POST.get('loginnamedesc')
            email = request.POST.get('email')
            team = request.POST.get('team')
            rank = request.POST.get('rank')
            isactive = request.POST.get('isactive')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "USERICON" + "\\" + loginid
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    loginid = loginid

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/shopList_response.html", context)


def tableSetting(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    if team == "admin": team = ""
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')

    accessid = 5145
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
    }
    return render(request, "maintenance_template/tableSetting.html", context)

@csrf_exempt
def tableSetting_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    user_team = team

    if action == "table_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblTable where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblTable where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and status = 1"
        table_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "table_list": table_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            shop = request.POST.get('shop')
            table_id = request.POST.get('table_id')
            table_key = request.POST.get('table_key')
            table_name = request.POST.get('table_name')
            table_name_e = request.POST.get('table_name_e')
            table_seat = request.POST.get('table_seat')
            table_shape = request.POST.get('table_shape')
            location = request.POST.get('location')
            time_period = request.POST.get('time_period')
            charge = request.POST.get('charge')
            table_photo = request.POST.get('table_photo')
            table_icon = request.POST.get('table_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "table" + "\\" + table_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    table_id = table_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    table = Tables()
                else:
                    table = Tables.objects.using('infinyrealty').get(table_id=table_id)
                table.shop = shop
                table.table_key = table_key
                table.table_name = table_name
                table.table_name_e = table_name_e
                table.table_seat = table_seat
                table.table_shape = table_shape
                table.location = location
                table.time_period = time_period
                table.charge = charge
                table.table_photo = table_photo
                table.table_icon = table_icon
                table.sequence = sequence
                table.status = status
                #table.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = table + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    table.delete(using='infinyrealty')
                else:
                    table.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "table" + "\\" + table_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    table_id = table_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/tableSetting_response.html", context)

def timePeriod(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    if team == "admin": team = ""
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 1

    accessid = 123
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
        "codelist": CodeList,
    }
    return render(request, "maintenance_template/timePeriod.html", context)

@csrf_exempt
def timePeriod_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    code_id = str(request.POST.get('code_id'))
    user_team = team
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        code_detail_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            shop = request.POST.get('shop')
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            time_period = request.POST.get('time_period')
            charge = request.POST.get('charge')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.shop = shop
                codedetail.code_id = code_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.time_period = time_period
                codedetail.charge = charge
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/timePeriod_response.html", context)

def possession(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 1
    code_parent_id = "0"
    if code_id == 3:
        code_parent_id = "2"
    if code_id == 4:
        code_parent_id = "3"
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from tblCodeDetail where (1 = case when '" + code_parent_id + "' = '0' then 1 when code_id = '" + code_parent_id + "' then 1 else 0 end) and status = 1")
    code_detail_parent_list = cursor.fetchall()

    accessid = 5153
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "codelist": CodeList,
        "code_detail_parent_list": code_detail_parent_list,
    }
    return render(request, "maintenance_template/possession.html", context)

@csrf_exempt
def possession_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    code_id = str(request.POST.get('code_id'))
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        code_detail_list = cursor.fetchall()
        code_parent_id = "0"
        if code_id == "3":
            code_parent_id = "2"
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_parent_id+"' = 0 then 1 when code_parent_id = '"+code_parent_id+"' then 1 else 0 end) and status = 1")
        code_detail_parent_list = cursor.fetchall()

        context = {
            "action": action,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "code_detail_parent_list": code_detail_parent_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_parent_id = request.POST.get('code_parent_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.code_id = code_id
                codedetail.code_parent_id = code_parent_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/possession_response.html", context)

def district(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 2
    code_parent_id = "0"
    if code_id == 3:
        code_parent_id = "2"
    if code_id == 4:
        code_parent_id = "3"
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from tblCodeDetail where (1 = case when '" + code_parent_id + "' = '0' then 1 when code_id = '" + code_parent_id + "' then 1 else 0 end) and status = 1")
    code_detail_parent_list = cursor.fetchall()

    accessid = 4127
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "codelist": CodeList,
        "code_detail_parent_list": code_detail_parent_list,
    }
    return render(request, "maintenance_template/district.html", context)

@csrf_exempt
def district_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    code_id = str(request.POST.get('code_id'))
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        code_detail_list = cursor.fetchall()
        code_parent_id = "0"
        if code_id == "3":
            code_parent_id = "2"
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_parent_id+"' = 0 then 1 when code_parent_id = '"+code_parent_id+"' then 1 else 0 end) and status = 1")
        code_detail_parent_list = cursor.fetchall()

        context = {
            "action": action,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "code_detail_parent_list": code_detail_parent_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_parent_id = request.POST.get('code_parent_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.code_id = code_id
                codedetail.code_parent_id = code_parent_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/district_response.html", context)

def subdistrict(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 3
    code_parent_id = "0"
    if code_id == 3:
        code_parent_id = "2"
    if code_id == 4:
        code_parent_id = "3"
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from tblCodeDetail where (1 = case when '" + code_parent_id + "' = '0' then 1 when code_id = '" + code_parent_id + "' then 1 else 0 end) and status = 1")
    code_detail_parent_list = cursor.fetchall()

    accessid = 90
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "codelist": CodeList,
        "code_detail_parent_list": code_detail_parent_list,
    }
    return render(request, "maintenance_template/subdistrict.html", context)

@csrf_exempt
def subdistrict_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    code_id = str(request.POST.get('code_id'))
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        code_detail_list = cursor.fetchall()
        code_parent_id = "0"
        if code_id == "3":
            code_parent_id = "2"
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_parent_id+"' = 0 then 1 when code_parent_id = '"+code_parent_id+"' then 1 else 0 end) and status = 1")
        code_detail_parent_list = cursor.fetchall()

        context = {
            "action": action,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "code_detail_parent_list": code_detail_parent_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_parent_id = request.POST.get('code_parent_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.code_id = code_id
                codedetail.code_parent_id = code_parent_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/subdistrict_response.html", context)

def street(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 4
    code_parent_id = "0"
    if code_id == 3:
        code_parent_id = "2"
    if code_id == 4:
        code_parent_id = "3"
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from tblCodeDetail where (1 = case when '" + code_parent_id + "' = '0' then 1 when code_id = '" + code_parent_id + "' then 1 else 0 end) and status = 1")
    code_detail_parent_list = cursor.fetchall()

    accessid = 123
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "codelist": CodeList,
        "code_detail_parent_list": code_detail_parent_list,
    }
    return render(request, "maintenance_template/street.html", context)

@csrf_exempt
def street_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    code_id = str(request.POST.get('code_id'))
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        code_detail_list = cursor.fetchall()
        code_parent_id = "0"
        if code_id == "3":
            code_parent_id = "2"
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+code_parent_id+"' = 0 then 1 when code_parent_id = '"+code_parent_id+"' then 1 else 0 end) and status = 1")
        code_detail_parent_list = cursor.fetchall()

        context = {
            "action": action,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "code_detail_parent_list": code_detail_parent_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_parent_id = request.POST.get('code_parent_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.code_id = code_id
                codedetail.code_parent_id = code_parent_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/street_response.html", context)

def usage(request, year='None'):
    if not request.session.get('username'): return redirect('login')

    accessid = 5136
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "maintenance_template/usage.html", context)

@csrf_exempt
def usage_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')

    if action == "usage_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblPropertyUsage")
        usage_list = cursor.fetchall()

        context = {
            "action": action,
            "usage_list": usage_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            usage_id = request.POST.get('usage_id')
            usage_code = request.POST.get('usage_code')
            usage_name = request.POST.get('usage_name')
            usage_name_e = request.POST.get('usage_name_e')
            usage_photo = request.POST.get('usage_photo')
            usage_icon = request.POST.get('usage_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    propertyusage = PropertyUsages()
                else:
                    propertyusage = PropertyUsages.objects.using('infinyrealty').get(usage_id=usage_id)
                propertyusage.usage_code = usage_code
                propertyusage.usage_name = usage_name
                propertyusage.usage_name_e = usage_name_e
                propertyusage.usage_photo = usage_photo
                propertyusage.usage_icon = usage_icon
                propertyusage.sequence = sequence
                propertyusage.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    propertyusage.delete(using='infinyrealty')
                else:
                    propertyusage.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/usage_response.html", context)

def watermark_gen(request):
    if not request.session.get('username'): return redirect('login')

    property_file_list = PropertyFiles.objects.using('infinyrealty').filter(iswatermark=0).order_by('fileid')
    action = "watermark_gen"
    for w in property_file_list:
        filename = w.filename
        filename_extension = os.path.splitext(filename)[1][1:].lower()
        if "jpg" in filename_extension or "jpeg" in filename_extension or "png" in filename_extension:
            if w.filetype == "photo":
                filename = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\" + w.filename
                filename_wm = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\" + w.filename.replace(
                    "." + filename_extension, "-wm." + filename_extension)
            else:
                filename = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename
                filename_wm = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename.replace(
                    "." + filename_extension, "-wm." + filename_extension)
            filename_logo = getattr(settings, "PATH_MAIN", None) + "infinyrealty_logo_high.png"
            watermark_method = 2

            if watermark_method == 1:
                base_image = Image.open(filename)
                watermark_image = Image.open(filename_logo)
                watermark_ratio = 0.1  # 10% of the base image size
                watermark_width, watermark_height = watermark_image.size
                watermark_width = int(watermark_width * watermark_ratio)
                watermark_height = int(watermark_height * watermark_ratio)
                watermark_image = watermark_image.resize((watermark_width, watermark_height), resample=Image.BILINEAR)
                watermark_alpha = watermark_image.getchannel("A")
                watermark_alpha = ImageEnhance.Brightness(watermark_alpha).enhance(0.2)
                watermark_image.putalpha(watermark_alpha)
                base_width, base_height = base_image.size
                watermark_x = (base_width - watermark_width) // 2
                watermark_y = (base_height - watermark_height) // 2
                base_image.paste(watermark_image, (watermark_x, watermark_y), watermark_image)
                base_image.save(filename_wm, exif=base_image.info.get('exif', b''))
            else:
                base_image = Image.open(filename)
                watermark_image = Image.open(filename_logo)
                base_width, base_height = base_image.size
                watermark_width, watermark_height = watermark_image.size
                base_watermark_width = int(base_width * 0.2)
                base_watermark_ratio = base_watermark_width / watermark_width
                base_watermark_height = int(watermark_height * base_watermark_ratio)
                watermark_image = watermark_image.resize((base_watermark_width, base_watermark_height), resample=Image.BILINEAR)
                watermark_alpha = watermark_image.getchannel("A")
                watermark_alpha = ImageEnhance.Brightness(watermark_alpha).enhance(0.2)
                watermark_image.putalpha(watermark_alpha)
                watermark_x = (base_width - base_watermark_width) // 2
                watermark_y = (base_height - base_watermark_height) // 2
                base_image.paste(watermark_image, (watermark_x, watermark_y), watermark_image)
                base_image.save(filename_wm, exif=base_image.info.get('exif', b''))
            try:
                PropertyFiles.objects.using('infinyrealty').filter(fileid=w.fileid).update(iswatermark=1)
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
            except:
                continue

    context = {
        "action": action,
    }
    return render(request, "maintenance_template/systemProcess.html", context)

def transaction_cap(request, transaction_type="None"):
    #request.session['capture_count'] = 0
    #num = int(request.session.get('capture_count')) + 20
    #for type in ["商業","商舗","工業"]:
    #if transaction_type is not None:
    #    transaction_list = list(transaction_type)
    #else:
    transaction_list = ["商業","商舗","工業"]

    for type in transaction_list:
        if type == "商業":
            lengthPage = 7300
        if type == "工業":
            lengthPage = 2000
        if type == "商舗":
            lengthPage = 4200

        for num in range(0, 100, 20):
            if type == "商業":
                url = "https://www.leasinghub.com/zh/office/transactions?limitstart=" + str(num)
            if type == "工業":
                url = "https://www.leasinghub.com/zh/industrial/transactions?limitstart=" + str(num)
            if type == "商舗":
                url = "https://www.leasinghub.com/zh/shop/transactions?limitstart=" + str(num)

            # 使用 Selenium 創建 Chrome 驅動程序
            driver = webdriver.Chrome()

            # 訪問指定網址
            driver.get(url)

            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive.loadable-container")))

            # 使用 BeautifulSoup 解析網頁內容
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 查找具有指定 class 的 div 元素
            table_container_elements = soup.find_all("div", class_="table-responsive loadable-container")

            # 遍歷每個 table-responsive loadable-container 元素,並捕獲其中的內容
            for container in table_container_elements:
                try:
                    # 獲取容器內的表格元素
                    table_elements = container.find_all("table")

                    # 遍歷每個表格元素,並捕獲其中的內容
                    for table in table_elements:
                        # 獲取表格標題
                        table_header = [th.text.strip() for th in table.find_all("th")]

                        # 獲取表格行
                        table_rows = []
                        for tr in table.find_all("tr"):
                            row = [td.text.strip() for td in tr.find_all("td")]
                            if row:
                                table_rows.append(row)

                        for row in table_rows:
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            transactionrecord = TransactionRecords()
                            transactionrecord.transactiondate = row[0]
                            transactionrecord.district = row[1]
                            transactionrecord.propertyname = row[2]
                            transactionrecord.floor = row[3]
                            transactionrecord.approximatearea = row[4]
                            transactionrecord.transactionstatus = row[5]
                            transactionrecord.transactionprice = row[6]
                            transactionrecord.unitprice = row[7]
                            transactionrecord.source = row[8]
                            transactionrecord.usage = type
                            transactionrecord.createdate = datetime_str
                            # 檢查是否已存在相同的記錄
                            if not TransactionRecords.objects.using('infinyrealty').filter(transactiondate=transactionrecord.transactiondate, district=transactionrecord.district, propertyname=transactionrecord.propertyname, approximatearea=transactionrecord.approximatearea, floor=transactionrecord.floor, source=transactionrecord.source, usage=transactionrecord.usage).exists():
                                transactionrecord.save(using='infinyrealty')
                except TimeoutException:
                    continue
    #request.session['capture_count'] = num
    #return redirect('transaction_cap')

    context = {
        "table_rows": table_container_elements,
        "capture": "1",
    }
    return render(request, "maintenance_template/systemProcess.html", context)

def transaction_cap_office(request, transaction_type="None"):
    #request.session['capture_count'] = 0
    #num = int(request.session.get('capture_count')) + 20
    #for type in ["商業","商舗","工業"]:
    #if transaction_type is not None:
    #    transaction_list = list(transaction_type)
    #else:
    transaction_list = ["商業"]

    for type in transaction_list:
        if type == "商業":
            lengthPage = 7300
        if type == "工業":
            lengthPage = 2000
        if type == "商舗":
            lengthPage = 4200

        for num in range(0, 100, 20):
            if type == "商業":
                url = "https://www.leasinghub.com/zh/office/transactions?limitstart=" + str(num)
            if type == "工業":
                url = "https://www.leasinghub.com/zh/industrial/transactions?limitstart=" + str(num)
            if type == "商舗":
                url = "https://www.leasinghub.com/zh/shop/transactions?limitstart=" + str(num)

            # 使用 Selenium 創建 Chrome 驅動程序
            driver = webdriver.Chrome()

            # 訪問指定網址
            driver.get(url)

            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive.loadable-container")))

            # 使用 BeautifulSoup 解析網頁內容
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 查找具有指定 class 的 div 元素
            table_container_elements = soup.find_all("div", class_="table-responsive loadable-container")

            # 遍歷每個 table-responsive loadable-container 元素,並捕獲其中的內容
            for container in table_container_elements:
                try:
                    # 獲取容器內的表格元素
                    table_elements = container.find_all("table")

                    # 遍歷每個表格元素,並捕獲其中的內容
                    for table in table_elements:
                        # 獲取表格標題
                        table_header = [th.text.strip() for th in table.find_all("th")]

                        # 獲取表格行
                        table_rows = []
                        for tr in table.find_all("tr"):
                            row = [td.text.strip() for td in tr.find_all("td")]
                            if row:
                                table_rows.append(row)

                        for row in table_rows:
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            transactionrecord = TransactionRecords()
                            transactionrecord.transactiondate = row[0]
                            transactionrecord.district = row[1]
                            transactionrecord.propertyname = row[2]
                            transactionrecord.floor = row[3]
                            transactionrecord.approximatearea = row[4]
                            transactionrecord.transactionstatus = row[5]
                            transactionrecord.transactionprice = row[6]
                            transactionrecord.unitprice = row[7]
                            transactionrecord.source = row[8]
                            transactionrecord.usage = type
                            transactionrecord.createdate = datetime_str
                            # 檢查是否已存在相同的記錄
                            if not TransactionRecords.objects.using('infinyrealty').filter(transactiondate=transactionrecord.transactiondate, district=transactionrecord.district, propertyname=transactionrecord.propertyname, approximatearea=transactionrecord.approximatearea, floor=transactionrecord.floor, source=transactionrecord.source, usage=transactionrecord.usage).exists():
                                transactionrecord.save(using='infinyrealty')
                except TimeoutException:
                    continue
    #request.session['capture_count'] = num
    #return redirect('transaction_cap')

    context = {
        "table_rows": table_container_elements,
        "capture": "1",
    }
    return render(request, "maintenance_template/systemProcess.html", context)

def transaction_cap_industrial(request, transaction_type="None"):
    #request.session['capture_count'] = 0
    #num = int(request.session.get('capture_count')) + 20
    #for type in ["商業","商舗","工業"]:
    #if transaction_type is not None:
    #    transaction_list = list(transaction_type)
    #else:
    transaction_list = ["工業"]

    for type in transaction_list:
        if type == "商業":
            lengthPage = 7300
        if type == "工業":
            lengthPage = 2000
        if type == "商舗":
            lengthPage = 4200

        for num in range(0, 100, 20):
            if type == "商業":
                url = "https://www.leasinghub.com/zh/office/transactions?limitstart=" + str(num)
            if type == "工業":
                url = "https://www.leasinghub.com/zh/industrial/transactions?limitstart=" + str(num)
            if type == "商舗":
                url = "https://www.leasinghub.com/zh/shop/transactions?limitstart=" + str(num)

            # 使用 Selenium 創建 Chrome 驅動程序
            driver = webdriver.Chrome()

            # 訪問指定網址
            driver.get(url)

            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive.loadable-container")))

            # 使用 BeautifulSoup 解析網頁內容
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 查找具有指定 class 的 div 元素
            table_container_elements = soup.find_all("div", class_="table-responsive loadable-container")

            # 遍歷每個 table-responsive loadable-container 元素,並捕獲其中的內容
            for container in table_container_elements:
                try:
                    # 獲取容器內的表格元素
                    table_elements = container.find_all("table")

                    # 遍歷每個表格元素,並捕獲其中的內容
                    for table in table_elements:
                        # 獲取表格標題
                        table_header = [th.text.strip() for th in table.find_all("th")]

                        # 獲取表格行
                        table_rows = []
                        for tr in table.find_all("tr"):
                            row = [td.text.strip() for td in tr.find_all("td")]
                            if row:
                                table_rows.append(row)

                        for row in table_rows:
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            transactionrecord = TransactionRecords()
                            transactionrecord.transactiondate = row[0]
                            transactionrecord.district = row[1]
                            transactionrecord.propertyname = row[2]
                            transactionrecord.floor = row[3]
                            transactionrecord.approximatearea = row[4]
                            transactionrecord.transactionstatus = row[5]
                            transactionrecord.transactionprice = row[6]
                            transactionrecord.unitprice = row[7]
                            transactionrecord.source = row[8]
                            transactionrecord.usage = type
                            transactionrecord.createdate = datetime_str
                            # 檢查是否已存在相同的記錄
                            if not TransactionRecords.objects.using('infinyrealty').filter(transactiondate=transactionrecord.transactiondate, district=transactionrecord.district, propertyname=transactionrecord.propertyname, approximatearea=transactionrecord.approximatearea, floor=transactionrecord.floor, source=transactionrecord.source, usage=transactionrecord.usage).exists():
                                transactionrecord.save(using='infinyrealty')
                except TimeoutException:
                    continue
    #request.session['capture_count'] = num
    #return redirect('transaction_cap')

    context = {
        "table_rows": table_container_elements,
        "capture": "1",
    }
    return render(request, "maintenance_template/systemProcess.html", context)

def transaction_cap_shop(request, transaction_type="None"):
    #request.session['capture_count'] = 0
    #num = int(request.session.get('capture_count')) + 20
    #for type in ["商業","商舗","工業"]:
    #if transaction_type is not None:
    #    transaction_list = list(transaction_type)
    #else:
    transaction_list = ["商舗"]

    for type in transaction_list:
        if type == "商業":
            lengthPage = 7300
        if type == "工業":
            lengthPage = 2000
        if type == "商舗":
            lengthPage = 4200

        for num in range(0, 100, 20):
            if type == "商業":
                url = "https://www.leasinghub.com/zh/office/transactions?limitstart=" + str(num)
            if type == "工業":
                url = "https://www.leasinghub.com/zh/industrial/transactions?limitstart=" + str(num)
            if type == "商舗":
                url = "https://www.leasinghub.com/zh/shop/transactions?limitstart=" + str(num)

            # 使用 Selenium 創建 Chrome 驅動程序
            driver = webdriver.Chrome()

            # 訪問指定網址
            driver.get(url)

            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive.loadable-container")))

            # 使用 BeautifulSoup 解析網頁內容
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 查找具有指定 class 的 div 元素
            table_container_elements = soup.find_all("div", class_="table-responsive loadable-container")

            # 遍歷每個 table-responsive loadable-container 元素,並捕獲其中的內容
            for container in table_container_elements:
                try:
                    # 獲取容器內的表格元素
                    table_elements = container.find_all("table")

                    # 遍歷每個表格元素,並捕獲其中的內容
                    for table in table_elements:
                        # 獲取表格標題
                        table_header = [th.text.strip() for th in table.find_all("th")]

                        # 獲取表格行
                        table_rows = []
                        for tr in table.find_all("tr"):
                            row = [td.text.strip() for td in tr.find_all("td")]
                            if row:
                                table_rows.append(row)

                        for row in table_rows:
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            transactionrecord = TransactionRecords()
                            transactionrecord.transactiondate = row[0]
                            transactionrecord.district = row[1]
                            transactionrecord.propertyname = row[2]
                            transactionrecord.floor = row[3]
                            transactionrecord.approximatearea = row[4]
                            transactionrecord.transactionstatus = row[5]
                            transactionrecord.transactionprice = row[6]
                            transactionrecord.unitprice = row[7]
                            transactionrecord.source = row[8]
                            transactionrecord.usage = type
                            transactionrecord.createdate = datetime_str
                            # 檢查是否已存在相同的記錄
                            if not TransactionRecords.objects.using('infinyrealty').filter(transactiondate=transactionrecord.transactiondate, district=transactionrecord.district, propertyname=transactionrecord.propertyname, approximatearea=transactionrecord.approximatearea, floor=transactionrecord.floor, source=transactionrecord.source, usage=transactionrecord.usage).exists():
                                transactionrecord.save(using='infinyrealty')
                except TimeoutException:
                    continue
    #request.session['capture_count'] = num
    #return redirect('transaction_cap')

    context = {
        "table_rows": table_container_elements,
        "capture": "1",
    }
    return render(request, "maintenance_template/systemProcess.html", context)

def my_scheduled_task():
    for type in ["商業", "工業", "商舗"]:
        if type == "商業":
            lengthPage = 7300
        if type == "工業":
            lengthPage = 2000
        if type == "商舗":
            lengthPage = 4200

        for num in range(20, 200, 20):
            if type == "商業":
                url = "https://www.leasinghub.com/zh/office/transactions?limitstart=" + str(num)
            if type == "工業":
                url = "https://www.leasinghub.com/zh/industrial/transactions?limitstart=" + str(num)
            if type == "商舗":
                url = "https://www.leasinghub.com/zh/shop/transactions?limitstart=" + str(num)

            # 使用 Selenium 創建 Chrome 驅動程序
            driver = webdriver.Chrome()

            # 訪問指定網址
            driver.get(url)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive.loadable-container")))

            # 使用 BeautifulSoup 解析網頁內容
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 查找具有指定 class 的 div 元素
            table_container_elements = soup.find_all("div", class_="table-responsive loadable-container")

            # 遍歷每個 table-responsive loadable-container 元素,並捕獲其中的內容
            for container in table_container_elements:

                # 獲取容器內的表格元素
                table_elements = container.find_all("table")

                # 遍歷每個表格元素,並捕獲其中的內容
                for table in table_elements:
                    # 獲取表格標題
                    table_header = [th.text.strip() for th in table.find_all("th")]

                    # 獲取表格行
                    table_rows = []
                    for tr in table.find_all("tr"):
                        row = [td.text.strip() for td in tr.find_all("td")]
                        if row:
                            table_rows.append(row)

                    for row in table_rows:
                        transactionrecord = TransactionRecords()
                        transactionrecord.transactiondate = row[0]
                        transactionrecord.district = row[1]
                        transactionrecord.propertyname = row[2]
                        transactionrecord.floor = row[3]
                        transactionrecord.approximatearea = row[4]
                        transactionrecord.transactionstatus = row[5]
                        transactionrecord.transactionprice = row[6]
                        transactionrecord.unitprice = row[7]
                        transactionrecord.source = row[8]
                        transactionrecord.usage = type
                        # 檢查是否已存在相同的記錄
                        if not TransactionRecords.objects.using('infinyrealty').filter(transactiondate=transactionrecord.transactiondate, district=transactionrecord.district, propertyname=transactionrecord.propertyname, floor=transactionrecord.floor, source=transactionrecord.source, usage=transactionrecord.usage).exists():
                            transactionrecord.save(using='infinyrealty')
    pass

def categorySetting(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    if team == "admin": team = ""
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 2

    accessid = 4127
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
        "codelist": CodeList,
    }
    return render(request, "maintenance_template/categorySetting.html", context)

@csrf_exempt
def categorySetting_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    code_id = str(request.POST.get('code_id'))
    user_team = team
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        code_detail_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            shop = request.POST.get('shop')
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            time_period = request.POST.get('time_period')
            charge = request.POST.get('charge')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.shop = shop
                codedetail.code_id = code_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.time_period = time_period
                codedetail.charge = charge
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/categorySetting_response.html", context)

def comboSetting(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    if team == "admin": team = ""
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 3

    accessid = 5136
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
        "codelist": CodeList,
    }
    return render(request, "maintenance_template/comboSetting.html", context)

@csrf_exempt
def comboSetting_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    code_id = str(request.POST.get('code_id'))
    user_team = team
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        code_detail_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            shop = request.POST.get('shop')
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            time_period = request.POST.get('time_period')
            charge = request.POST.get('charge')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.shop = shop
                codedetail.code_id = code_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.time_period = time_period
                codedetail.charge = charge
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/comboSetting_response.html", context)

def tasteSetting(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    if team == "admin": team = ""
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 11

    accessid = 5153
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
        "codelist": CodeList,
    }
    return render(request, "maintenance_template/tasteSetting.html", context)

@csrf_exempt
def tasteSetting_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    code_id = str(request.POST.get('code_id'))
    user_team = team
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        code_detail_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            shop = request.POST.get('shop')
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            time_period = request.POST.get('time_period')
            charge = request.POST.get('charge')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.shop = shop
                codedetail.code_id = code_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.time_period = time_period
                codedetail.charge = charge
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/tasteSetting_response.html", context)

def orderStatus(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    if team == "admin": team = ""
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 4

    accessid = 73
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
        "codelist": CodeList,
    }
    return render(request, "maintenance_template/orderStatus.html", context)

@csrf_exempt
def orderStatus_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    code_id = str(request.POST.get('code_id'))
    user_team = team
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        code_detail_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            shop = request.POST.get('shop')
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            time_period = request.POST.get('time_period')
            charge = request.POST.get('charge')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.shop = shop
                codedetail.code_id = code_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.time_period = time_period
                codedetail.charge = charge
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/orderStatus_response.html", context)

def paymentMethod(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    if team == "admin": team = ""
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')
    CodeList = Codes.objects.using('infinyrealty').order_by('sequence')
    code_id = 6

    accessid = 90
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
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('post_org'))
    context = {
        "user_team": team,
        "user_code_id": code_id,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
        "codelist": CodeList,
    }
    return render(request, "maintenance_template/paymentMethod.html", context)

@csrf_exempt
def paymentMethod_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = str(request.POST.get('team'))
    code_id = str(request.POST.get('code_id'))
    user_team = team
    user_code_id = code_id

    if action == "code_detail_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        code_detail_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "user_code_id": user_code_id,
            "code_detail_list": code_detail_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            shop = request.POST.get('shop')
            code_detail_id = request.POST.get('code_detail_id')
            code_id = request.POST.get('code_id')
            code_key = request.POST.get('code_key')
            code_detail_name = request.POST.get('code_detail_name')
            code_detail_name_e = request.POST.get('code_detail_name_e')
            time_period = request.POST.get('time_period')
            charge = request.POST.get('charge')
            code_detail_photo = request.POST.get('code_detail_photo')
            code_detail_icon = request.POST.get('code_detail_icon')
            sequence = request.POST.get('sequence')
            status = request.POST.get('status')
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    codedetail = CodeDetails()
                else:
                    codedetail = CodeDetails.objects.using('infinyrealty').get(code_detail_id=code_detail_id)
                codedetail.shop = shop
                codedetail.code_id = code_id
                codedetail.code_key = code_key
                codedetail.code_detail_name = code_detail_name
                codedetail.code_detail_name_e = code_detail_name_e
                codedetail.time_period = time_period
                codedetail.charge = charge
                codedetail.code_detail_photo = code_detail_photo
                codedetail.code_detail_icon = code_detail_icon
                codedetail.sequence = sequence
                codedetail.status = status
                #codedetail.createdate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    codedetail.delete(using='infinyrealty')
                else:
                    codedetail.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "upload":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            try:
                # Save the file to a desired location
                # For example:
                try:
                    path = getattr(settings, "PATH_OTHER", None) + "code" + "\\" + code_detail_id
                    if not os.path.exists(path):
                        os.makedirs(path)
                    path = os.path.join(path, file.name)
                    with open(path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    code_detail_id = code_detail_id

                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "maintenance_template/paymentMethod_response.html", context)

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
    file_path_utf8 = os.path.join(path, str(urllib.parse.quote(filelist)))
    #return HttpResponse(file_path)
    if filelist != "":
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application//mssword")
                #response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path) + '; filename*=UTF-8' + os.path.basename(file_path)
                response['Content-Disposition'] = "attachment; filename* = UTF-8''" + os.path.basename(file_path_utf8)
                return response

@csrf_exempt
def uploadfile(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "upload":
            file = request.FILES['file']
            insptype = request.POST.get('insptype')
            schoolyear = request.POST.get('schoolyear')
            code = request.POST.get('code')
            schoolid = request.POST.get('schoolid')
            filename = request.POST.get('filename')
            try:
                # Save the file to a desired location
                # For example:
                path = getattr(settings, "PATH_INSP_REPORT", None) + insptype + "\\" + schoolyear + "\\" + code + "_" + schoolid + "\\" + "REPORT" + "\\" + file.name
                with open(path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                schoolinspreport = SchoolInspReport()
                schoolinspreport.schoolid = schoolid
                schoolinspreport.inspyear = schoolyear
                schoolinspreport.insptype = insptype
                schoolinspreport.reportfilename = file.name
                schoolinspreport.loginid = request.session.get('loginid')
                schoolinspreport.lastuploaddate = datetime_str
                schoolinspreport.reportfolder = code + "_" + schoolid
                schoolinspreport.save(using='schoolmaster')
                return JsonResponse({'message': 'File uploaded successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'File upload failed. Error: {}'.format(str(e))}, status=500)
        else:
            insptype = request.POST.get('insptype')
            schoolyear = request.POST.get('schoolyear')
            code = request.POST.get('code')
            schoolid = request.POST.get('schoolid')
            filename = request.POST.get('filename')
            try:
                path = getattr(settings, "PATH_INSP_REPORT", None) + insptype + "\\" + schoolyear + "\\" + code + "_" + schoolid + "\\" + "REPORT" + "\\" + filename
                fs = FileSystemStorage(location=getattr(settings, "PATH_INSP_REPORT", None))
                path = os.path.join(insptype, schoolyear, code + "_" + schoolid, "REPORT", filename)
                if fs.exists(path):
                    schoolinspreport = SchoolInspReport.objects.using('schoolmaster').get(schoolid=schoolid, inspyear=schoolyear, insptype=insptype, reportfilename=filename)
                    schoolinspreport.delete(using='schoolmaster')
                    fs.delete(path)
                    return JsonResponse({'message': 'File deleted successfully.'})
                else:
                    return JsonResponse({'message': 'File does not exist.'}, status=404)
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                return JsonResponse({'message': 'File deletion failed.'+str(line_number)+': '+str(e)})
    else:
        return JsonResponse({'message': 'File upload failedxx.'})

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

def downloadssezipfile(request, year, schoolid):
    if not request.session.get('post'): return redirect('')
    # Download timetable files
    directory_path = getattr(settings, "PATH_INSP_REPORT", None)+"SDC"+"\\"+year+"\\"+schoolid
    output_path = getattr(settings, "PATH_INSP_REPORT", None)+"SDC"+"\\zip\\"+schoolid+"_"+year+"_SSE.zip"

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory_path))

    with open(output_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application//zip")
        response['Content-Disposition'] = "attachment; filename* = UTF-8''" + os.path.basename(output_path)
        return response
    
def SSEFiles_program(request):
        try:
            executable_path = request.POST.get('executable_path')
            subprocess.Popen([executable_path])
            time.sleep(4)     
            return HttpResponseRedirect('/SSEFiles')
        except Exception as error:
             print("An exception occurred:", error) 

def testingPage(request):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('infinyrealty').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    table_name = "M8"

    broker_address = "20.2.87.158"  # mqtt address
    port = 1883  # mqtt port
    # topic = "Prn220107240B282E0D0000F4B82303A0BE" #mqtt topic
    topic = "Prn240701220D2E280B0000F414D281134D"  # mqtt topic
    username = "zen"
    password = "pos"
    client_id = "Z"
    qos = 2

    # connected the MQTT SERVER
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect to MQTT,Return code %d\n ", rc)

        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.username_pw_set(username, password)
        client.connect(broker_address, port, qos)
        return client

    # publsh the manager to printer
    client = connect_mqtt()
    esc_comm = ESCPOSManager()
    esc_comm.Prefix_command()  #
    esc_comm.set_alignment("left")
    esc_comm.set_font_size(128)
    esc_comm.print_text(table_name+"\n")
    esc_comm.feed_lines(1)
    esc_comm.set_alignment("center")
    esc_comm.set_font_size(128)
    esc_comm.print_text(shop_name+"\n")
    esc_comm.feed_lines(1)
    esc_comm.set_alignment("left")
    esc_comm.set_font_size(9)
    esc_comm.print_text("地址："+shop_address+"\n")
    esc_comm.print_text("電話："+phone_area_code+" "+phone_number+"\n")
    esc_comm.feed_lines(1)
    # esc_comm.print_qr_code("www.hsprinter.com\n")
    esc_data = esc_comm.send_command()
    client.publish(topic, esc_data)
    client.disconnect()


    printer_ip = "192.168.50.72"
    printer_port = "9100"
    #invoice_content = "jackie"
    #test_printer_connection(printer_ip, printer_port)
    #print_to_network_printer(printer_ip, printer_port, invoice_content)
    context = {
        "printer_ip":printer_ip,
        "printer_port": printer_port,
        "shop_name": shop_name,
    }
    return render(request, "maintenance_template/testingPage.html", context)

@csrf_exempt
def testingPage_response(request):
    if not request.session.get('username'): return redirect('login')
    action ="aaa"

    context = {
        "action": action,
    }

    return render(request, "maintenance_template/testingPage_response.html", context)

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

def test_printer_connection(printer_ip, printer_port):
    try:
        # Create a socket connection to the printer
        printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        printer_socket.settimeout(3)  # Set a timeout value for the connection test
        printer_socket.connect((printer_ip, printer_port))

        # Close the socket connection
        printer_socket.close()

        print("Printer connection successful.")
        return True
    except Exception as e:
        print("Printer connection failed:", str(e))
        return False

def print_to_network_printer(printer_ip, printer_port, content):
    try:
        # Create a socket connection to the printer
        printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        printer_socket.connect((printer_ip, printer_port))

        # Send the content to the printer
        printer_socket.sendall(content.encode('utf-8'))

        # Close the socket connection
        printer_socket.close()

        print("Printing successful.")
    except Exception as e:
        print("Printing failed:", str(e))