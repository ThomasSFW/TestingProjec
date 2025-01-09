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
from django.core.files.storage import default_storage
import json
import pyodbc
import requests
import datetime
import os
import hashlib
import random
import string
import paho.mqtt.client as mqtt
from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks, Focusgroup, Focussubtypes
from InfinyRealty_app.models import AccessRights, QAIPFunction, PageView
from InfinyRealty_app.models import Printer
from InfinyRealty_app.models import ESCPOSManager
from django.conf import settings

def sidebar(request):
    if not request.session.get('username'): return redirect('login')
    MenuTabs = Tabs.objects.using('infinyrealty').filter(isenabled=1).order_by('sequence')
    MenuCategories = Categories.objects.using('infinyrealty').filter(isenabled=1).order_by('sequence')
    MenuSubCategories = SubCategories.objects.using('infinyrealty').filter(isenabled=1).order_by('sequence')

    cnxn1 = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=schoolmaster')
    cursor1 = cnxn1.cursor()
    cursor1.execute("select * from V_UserAccessRight where username = '" + request.session.get('username') + "'")
    sUserAccessRight = cursor1.fetchall()
    useraccessfunctionlist = []
    for w in sUserAccessRight:
        try:
            useraccessfunctionlist.append({'functionid': w.FunctionID})
        except Exception as e:
            useraccessfunctionlist = [1, 2, 3]

    context = {
        "AccessID": 20,
        "menutabs": MenuTabs,
        "menucategories": MenuCategories,
        "menusubcategories": MenuSubCategories,
        "useraccessright": sUserAccessRight,
        "useraccessfunctionlist": useraccessfunctionlist
    }
    return render(request, "common_template/base_template.html", context)


def sidebar1(request):
    MenuTabs = Tabs.objects.using('infinyrealty').filter(isenabled=1).order_by('sequence')
    MenuCategories = Categories.objects.using('infinyrealty').filter(isenabled=1).order_by('sequence')
    MenuSubCategories = SubCategories.objects.using('infinyrealty').filter(isenabled=1).order_by('sequence')

    context = {
        "AccessID": 20,
        "menutabs": MenuTabs,
        "menucategories": MenuCategories,
        "menusubcategories": MenuSubCategories
    }

    context.update(sidebar)

    return render(request, "common_template/base_template.html", context)

def userList(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    team = request.session.get('team')
    users = Users.objects.using('infinyrealty')
    TeamList = Teams.objects.using('infinyrealty').order_by('sequence')
    RankList = Ranks.objects.using('infinyrealty').order_by('sequence')

    accessid = 11
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
        "user_team": team,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
        "ranklist": RankList,
    }
    return render(request, "system_template/userList.html", context)

@csrf_exempt
def userList_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = request.POST.get('team')
    rank = request.POST.get('rank')
    user_team = team
    user_rank = rank

    if action == "user_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_Login where (1 = case when '"+team+"' = '' then 1 when team = '"+team+"' then 1 else 0 end) and (1 = case when '"+rank+"' = '' then 1 when rank = '"+rank+"' then 1 else 0 end)")
        user_list = cursor.fetchall()
        context = {
            "action": action,
            "user_team": user_team,
            "user_rank": user_rank,
            "user_list": user_list,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '"+team+"', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            try:
                file = request.FILES['file']
            except Exception as e:
                action = action
            recordid = request.POST.get('recordid')
            loginid = request.POST.get('loginid')
            username = request.POST.get('username')
            password = request.POST.get('password')
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
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                if action == "add":
                    user = Users()
                    user.loginid = Users.objects.using('infinyrealty').aggregate(Max('loginid'))['loginid__max'] + 1
                    user.logincount = 0
                    user.groupid = 1
                    user.createdate = datetime_str
                else:
                    if action == "delete":
                        user = Users.objects.using('infinyrealty').get(id=recordid)
                    else:
                        user = Users.objects.using('infinyrealty').get(id=recordid)
                        user.loginid = loginid
                user.username = username
                if action != "delete":
                    hashed_password = hash_password(password)
                    user.password = hashed_password
                user.loginnamedesc = loginnamedesc
                user.email = email
                user.team = team
                user.rank = rank
                user.isactive = isactive
                user.modifydate = datetime_str
                #schoolinspreport.reportfilename = file.name
                #schoolinspreport.loginid = request.session.get('loginid')
                #schoolinspreport.reportfolder = code + "_" + schoolid
                #schoolinspreport.save(using='schoolmaster')
                if action == "delete":
                    user.delete(using='infinyrealty')
                else:
                    user.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "update":
        if request.method == 'POST':
            loginid = request.POST.get('loginid')
            username = request.POST.get('username')
            oldpassword = request.POST.get('oldpassword')
            newpassword = request.POST.get('newpassword')
            loginnamedesc = request.POST.get('loginnamedesc')
            email = request.POST.get('email')
            try:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                user = Users.objects.using('infinyrealty').get(loginid=loginid)
                user.loginid = loginid
                user.username = username
                hashed_oldpassword = hash_password(oldpassword)
                if newpassword != "":
                    hashed_newpassword = hash_password(newpassword)
                    user.password = hashed_newpassword
                user.loginnamedesc = loginnamedesc
                user.email = email
                #user.isactive = 1
                user.modifydate = datetime_str
                if request.session.get('hashed_password') == hashed_oldpassword:
                    user.save(using='infinyrealty')
                    if newpassword != "":
                        request.session['hashed_password'] = hashed_newpassword
                        request.session['loginnamedesc'] = loginnamedesc
                        request.session['email'] = email
                    return HttpResponse("The record was updated successfully.")
                else:
                    return HttpResponse("The old password is not correct.")
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
                #return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
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
    return render(request, "system_template/userList_response.html", context)

def systemTab(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    accessid = 14
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
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "system_template/systemTab.html", context)

@csrf_exempt
def systemTab_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    recordid = request.POST.get('recordid')

    if action == "systemtab_list":
        tabs = Tabs.objects.using('infinyrealty').all().order_by('sequence')
        context = {
            "action": action,
            "tabs": tabs,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            tabid = request.POST.get('tabid')
            tabname = request.POST.get('tabname')
            url = request.POST.get('url')
            sequence = request.POST.get('sequence')
            iconclass = request.POST.get('iconclass')
            isactive = request.POST.get('isactive')
            try:
                if action == "add":
                    tab = Tabs()
                else:
                    tab = Tabs.objects.using('infinyrealty').get(tabid=tabid)
                tab.tabname = tabname
                tab.url = url
                tab.sequence = sequence
                tab.iconclass = iconclass
                tab.isenabled = isactive
                if action == "delete":
                    tab.delete(using='infinyrealty')
                else:
                    tab.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "system_template/systemTab_response.html", context)

def category(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    tabs = Tabs.objects.using('infinyrealty').all().order_by('sequence')
    categories = Categories.objects.using('infinyrealty').all().order_by('sequence')

    accessid = 16
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
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "tabs": tabs,
        "user_tabid": "1",
        "urltypes": categories[0].URLTypes,
    }
    return render(request, "system_template/category.html", context)

@csrf_exempt
def category_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    recordid = request.POST.get('recordid')

    if action == "category_list":
        tabs = Tabs.objects.using('infinyrealty').all().order_by('sequence')
        categories = Categories.objects.using('infinyrealty').all().order_by('sequence')
        context = {
            "action": action,
            "tabs": tabs,
            "categories": categories,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            catid = request.POST.get('catid')
            tabid = request.POST.get('tabid')
            categoryname = request.POST.get('categoryname')
            url = request.POST.get('url')
            urltype = request.POST.get('urltype')
            sequence = request.POST.get('sequence')
            iconclass = request.POST.get('iconclass')
            isactive = request.POST.get('isactive')

            try:
                if action == "add":
                    category = Categories()
                else:
                    category = Categories.objects.using('infinyrealty').get(catid=catid)
                tab = Tabs.objects.using('infinyrealty').get(tabid=tabid)
                category.catname = categoryname
                category.tabid = tab
                category.url = url
                category.urltype = urltype
                category.sequence = sequence
                category.iconclass = iconclass
                category.isenabled = isactive
                if action == "delete":
                    category.delete(using='infinyrealty')
                else:
                    category.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "system_template/category_response.html", context)

def subCategory(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    categories = Categories.objects.using('infinyrealty').all().order_by('sequence')
    subcategories = SubCategories.objects.using('infinyrealty').all().order_by('sequence')

    accessid = 17
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
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "categories": categories,
        "urltypes": subcategories[0].URLTypes,
    }
    return render(request, "system_template/subCategory.html", context)

@csrf_exempt
def subCategory_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    recordid = request.POST.get('recordid')

    if action == "subcategory_list":
        tabs = Tabs.objects.using('infinyrealty').all().order_by('sequence')
        categories = Categories.objects.using('infinyrealty').all().order_by('sequence')
        subcategories = SubCategories.objects.using('infinyrealty').select_related('catid', 'catid__tabid').order_by('sequence')

        context = {
            "action": action,
            "tabs": tabs,
            "categories": categories,
            "subcategories": subcategories,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            catid = request.POST.get('catid')
            subcatid = request.POST.get('subcatid')
            subcategoryname = request.POST.get('subcategoryname')
            url = request.POST.get('url')
            urlnew = request.POST.get('urlnew')
            urltype = request.POST.get('urltype')
            sequence = request.POST.get('sequence')
            iconclass = request.POST.get('iconclass')
            iscore = request.POST.get('iscore')
            isready = request.POST.get('isready')
            status = request.POST.get('status')

            try:
                if action == "add":
                    subcategory = SubCategories()
                else:
                    subcategory = SubCategories.objects.using('infinyrealty').get(subcatid=subcatid)
                category = Categories.objects.using('infinyrealty').get(catid=catid)
                subcategory.subcatname = subcategoryname
                subcategory.catid = category
                subcategory.url = url
                subcategory.urlnew = urlnew
                subcategory.urltype = urltype
                subcategory.sequence = sequence
                subcategory.iconclass = iconclass
                subcategory.iscore = iscore
                subcategory.isready = isready
                subcategory.isenabled = status
                if action == "delete":
                    subcategory.delete(using='infinyrealty')
                    functions = QAIPFunction.objects.using('infinyrealty').get(subcatid=subcatid)
                    functions.delete(using='infinyrealty')
                else:
                    subcategory.save(using='infinyrealty')
                if action == "add":
                    subcategory = SubCategories.objects.using('infinyrealty').last()
                    functions = QAIPFunction()
                    if subcategory is not None:
                        functions.subcatid = subcategory.subcatid
                    functions.functionname = "Access this page"
                    functions.sequence = 0
                    functions.isenabled = 1
                    functions.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "system_template/subCategory_response.html", context)

def userLog(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')
    TeamList = Teams.objects.using('infinyrealty').order_by('sequence')

    accessid = 46
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
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
    }
    return render(request, "system_template/userLog.html", context)

@csrf_exempt
def userLog_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = request.POST.get('team')
    if team == "admin": team = "east"
    loginid = request.POST.get('loginid')
    start_date = request.POST.get('start_date')
    end_date = str(request.POST.get('end_date')) + " 23:59:59"

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
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
    if action == "login_log":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_login_log "  \
              "where (1 = case when '' = ? then 1 when lastLogin >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when lastLogin <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by lastLogin desc"
        params = (start_date, start_date, end_date, end_date, team, team, loginid, loginid)
        cursor.execute(sql, params)
        login_log_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "login_log_list": login_log_list,
            "sql": sql,
        }
    if action == "active_log":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_login "  \
              "where (1 = case when '' = ? then 1 when activeDate >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when activeDate <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by activeDate desc"
        params = (start_date, start_date, end_date, end_date, team, team, loginid, loginid)
        cursor.execute(sql, params)
        active_log_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "active_log_list": active_log_list,
            "sql": sql,
        }
    if action == "visit_log":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_login_PageView "  \
              "where (1 = case when '' = ? then 1 when logdatetime >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when logdatetime <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by logdatetime desc"
        params = (start_date, start_date, end_date, end_date, team, team, loginid, loginid)
        cursor.execute(sql, params)
        visit_log_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "visit_log_list": visit_log_list,
            "sql": sql,
        }
    if action == "action_log":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_UserAccessLog "  \
              "where (1 = case when '' = ? then 1 when logdatetime >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when logdatetime <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by logdatetime desc"
        params = (start_date, start_date, end_date, end_date, team, team, loginid, loginid)
        cursor.execute(sql, params)
        action_log_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "action_log_list": action_log_list,
            "sql": sql,
        }
    return render(request, "system_template/userLog_response.html", context)

def accessRight(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')
    if team == "":
        team = "admin"

    TeamList = Teams.objects.using('infinyrealty').order_by('sequence')

    accessid = 3125
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
        "user_team": team,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "teamlist": TeamList,
    }
    return render(request, "system_template/accessRight.html", context)

@csrf_exempt
def accessRight_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = request.POST.get('team')
    loginid = request.POST.get('loginid')
    today = datetime.datetime.now()

    if action == "menutab":
        context = {
            "action": action,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '"+team+"', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "user_view":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_login "  \
              "where isActive = 1 "  \
              "and (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by team_sequence, rank_sequence, username"
        params = (team, team, loginid, loginid)
        cursor.execute(sql, params)
        user_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "user_view_list": user_view_list,
            "today": today,
            "sql": sql,
        }
    if action == "access_control":
        team = request.POST.get('team')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_login "  \
              "where isActive = 1 "  \
              "and (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by team_sequence, rank_sequence, username"
        params = (team, team, loginid, loginid)
        cursor.execute(sql, params)
        user_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_FunctionList " \
              "order by tab_sequence, cat_sequence, subcat_sequence, subcatid, function_sequence"
        cursor.execute(sql)
        function_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "user_view_list": user_view_list,
            "function_list": function_list,
            "sql": sql,
        }
    if action == "access_control_update":
        team = request.POST.get('team')
        access_data_add = request.POST.get('access_data_add')
        access_data_delete = request.POST.get('access_data_delete')
        if access_data_add != "":
            items = access_data_add.strip().split(";")
            for item in items:
                if item:
                    parts = item.split(",")
                    username = parts[0]
                    functionid = parts[1]
                    try:
                        accessright = AccessRights.objects.using('infinyrealty').get(team=team,username=username,functionid=functionid)
                        #accessright.username = username
                        #accessright.functionid = functionid
                        accessright.approved = 0
                        accessright.save(using='infinyrealty')
                    except AccessRights.DoesNotExist:
                        accessright = AccessRights()
                        accessright.id = AccessRights.objects.using('infinyrealty').aggregate(Max('id'))['id__max'] + 1
                        accessright.username = username
                        accessright.functionid = functionid
                        accessright.team = team
                        accessright.approved = 0
                        accessright.lastupdated = today
                        accessright.expireddate = '1900-01-01'
                        accessright.save(using='infinyrealty')
                    except Exception as e:
                        return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
                        #accessright.approved = 0
        if access_data_delete != "":
            items = access_data_delete.strip().split(";")
            for item in items:
                if item:
                    parts = item.split(",")
                    username = parts[0]
                    functionid = parts[1]
                    try:
                        accessright = AccessRights.objects.using('infinyrealty').get(team=team,username=username,functionid=functionid)
                        #accessright.post = post
                        #accessright.functionid = functionid
                        #accessright.approved = 0
                        accessright.delete(using='infinyrealty')
                    except Exception as e:
                        return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
                        #accessright.approved = 0
        return HttpResponse('Update Success')
    if action == "request_review":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_UserAccessRight where approved = 0")
        userapproveright_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "userapproveright_list": userapproveright_list,
        }
    if action == "request_review_update":
        team = request.POST.get('team')
        username = request.POST.get('username')
        functionid = request.POST.get('functionid')
        if team == "":
            team = request.session.get('team')

        try:
            accessright = AccessRights.objects.using('infinyrealty').get(team=team,username=username,functionid=functionid)
            #accessright.post = post
            #accessright.functionid = functionid
            accessright.approved = 1
            accessright.save(using='infinyrealty')
        except AccessRights.DoesNotExist:
            accessright = AccessRights()
            accessright.id = AccessRights.objects.using('infinyrealty').aggregate(Max('id'))['id__max'] + 1
            accessright.username = username
            accessright.functionid = functionid
            accessright.team = team
            accessright.approved = 0
            accessright.lastupdated = today
            accessright.expireddate = '1900-01-01'
            accessright.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "function_main":
        if team == "":
            team = request.session.get('team')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_login "  \
              "where (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by team_sequence, rank_sequence"
        params = (team, team, loginid, loginid)
        cursor.execute(sql, params)
        user_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_FunctionList " \
              "order by tab_sequence, cat_sequence, subcat_sequence, subcatid, function_sequence"
        cursor.execute(sql)
        function_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "user_view_list": user_view_list,
            "function_list": function_list,
            "sql": sql,
        }
    if action == "access_list":
        team = request.POST.get('team')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_login "  \
              "where isActive = 1 "  \
              "and (1 = case when '' = ? then 1 when team = ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when loginid = ? then 1 else 0 end)  " \
              "order by team_sequence, rank_sequence, username"
        params = (team, team, loginid, loginid)
        cursor.execute(sql, params)
        user_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from V_FunctionList " \
              "order by tab_sequence, cat_sequence, subcat_sequence, subcatid, function_sequence"
        cursor.execute(sql)
        function_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_loginid": loginid,
            "user_view_list": user_view_list,
            "function_list": function_list,
            "sql": sql,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            functionid = request.POST.get('functionid')
            subcatid = request.POST.get('subcatid')
            functionname = request.POST.get('functionname')
            sequence = request.POST.get('sequence')
            isactive = request.POST.get('isactive')

            try:
                if action == "add":
                    functions = QAIPFunction()
                else:
                    functions = QAIPFunction.objects.using('infinyrealty').get(functionid=functionid)
                functions.subcatid = subcatid
                functions.functionname = functionname
                functions.sequence = sequence
                functions.isenabled = isactive
                if action == "delete":
                    functions.delete(using='infinyrealty')
                else:
                    functions.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "system_template/accessRight_response.html", context)

def printer(request, year='None'):
    if not request.session.get('username'): return redirect('login')

    accessid = 89
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
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "system_template/printer.html", context)

@csrf_exempt
def printer_response(request):
    if not request.session.get('username'): return redirect('doLogin')
    action = request.POST.get('action')
    #recordid = request.POST.get('recordid')

    if action == "printer_list":
        printers = Printer.objects.using('infinyrealty').all()
        for w in printers:
            if test_printer_mqtt_connection(w.printer_client_id):
                exec("%s = '1'" % ('w.conn_status'))
            #if test_printer_connection(w.ip_address, w.port):
            #    exec("%s = '1'" % ('w.conn_status'))

        context = {
            "action": action,
            "printers": printers,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            printer_id = request.POST.get('printer_id')
            printer_name = request.POST.get('printer_name')
            printer_model = request.POST.get('printer_model')
            printer_client_id = request.POST.get('printer_client_id')
            printer_serial_number = request.POST.get('printer_serial_number')
            ip_address = request.POST.get('ip_address')
            port = request.POST.get('port')
            location_code = request.POST.get('location_code')
            location = request.POST.get('location')
            location_level = request.POST.get('location_level')
            status = request.POST.get('status')
            try:
                if action == "add":
                    printer = Printer()
                else:
                    printer = Printer.objects.using('infinyrealty').get(printer_id=printer_id)
                printer.printer_name = printer_name
                printer.printer_model = printer_model
                printer.printer_client_id = printer_client_id
                printer.printer_serial_number = printer_serial_number
                printer.ip_address = ip_address
                printer.port = port
                printer.location_code = location_code
                printer.location = location
                printer.location_level = location_level
                printer.status = status
                if action == "delete":
                    printer.delete(using='infinyrealty')
                else:
                    printer.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    if action == "print_test":
        printer_name = str(request.POST.get('printer_name'))
        ip_address = str(request.POST.get('ip_address'))
        port = int(request.POST.get('port'))

        print_to_network_printer(ip_address, port, printer_name)
        context = {
            "action": action,
            "printer_name": printer_name,
            "ip_address": ip_address,
            "port": port,
        }
    if action == "print_test_mqtt2":
        printer_name = str(request.POST.get('printer_name'))
        ip_address = str(request.POST.get('ip_address'))
        port = int(request.POST.get('port'))

        broker_address = "20.2.87.158"  # mqtt address
        port = 1883  # mqtt port
        topic = "Prn240701220D2E280B0000F414D281134D"  # mqtt topic
        username = ""
        password = ""
        client_id = ""
        qos = 1

        def on_connect(client, userdate, flags, rc):
            # print("connected with result code"+str(rc))
            clinet.username_pw_set(username, password)
            client.subscribe(topic)

        def on_message(client, userdata, message):
            print(f"Received Message:{message.payload.decode()}")
            received_message = message.payload.decode("utf-8")

        clinet = mqtt.Client()
        clinet.on_connect = on_connect
        clinet.on_message = on_message
        try:
            clinet.connect(broker_address, port, qos)
            clinet.loop_forever()
        except KeyboardInterrupt:
            print("Disconnecting....")
            clinet.disconnect()
        except Exception as e:
            print("An error occurred:", str(e))
            clinet.disconnect()

        context = {
            "action": action,
            "printer_name": printer_name,
            "ip_address": ip_address,
            "port": port,
        }
    if action == "print_test_mqtt":
        printer_name = str(request.POST.get('printer_name'))
        ip_address = str(request.POST.get('ip_address'))

        # MQTT broker configuration
        broker = "20.2.87.158"
        port = 1883
        username = ""
        password = ""

        # Callback function for when the client is connected
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT broker")
            client.subscribe("heartbeat")  # Subscribe to a topic upon connection

        # Callback function for when a message is received
        def on_message(client, userdata, msg):
            print("Received message: " + msg.payload.decode())

        # Create the MQTT client and set the callback functions
        print("mqtt.Client")
        client = mqtt.Client()
        client.username_pw_set(username, password)  # Set username and password if required
        client.on_connect = on_connect
        client.on_message = on_message

        # Connect to the MQTT broker
        client.connect(broker, port)

        # Start the MQTT loop (this function handles network communication and callbacks)
        client.loop_start()

        # Publish a message to the topic
        topic = "Prn240701220D2E280B0000F414D281134D"
        message = "Hello, MQTT!1"
        client.publish(topic, message)

        #print_to_network_printer(ip_address, port, printer_name)
        context = {
            "action": action,
            "printer_name": printer_name,
            "ip_address": ip_address,
        }
    return render(request, "system_template/printer_response.html", context)

def printer2(request):
    if not request.session.get('username'): return redirect('login')

    accessid = 14
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    menuItem = []
    #cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    #menuList = cursor_menu.fetchall()
    menuList = []
    #users = Users.objects.using('sqp').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='sqp')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "system_template/printer2.html", context)

@csrf_exempt
def printer_response_2(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    recordid = request.POST.get('recordid')

    if action == "printer_list":
        printers = Printer.objects.using("infinyrealty")
        context = {
            "action": action,
            "printers": printers,
        }
    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            printer_id = request.POST.get('printer_id')
            tabname = request.POST.get('tabname')
            url = request.POST.get('url')
            sequence = request.POST.get('sequence')
            iconclass = request.POST.get('iconclass')
            isactive = request.POST.get('isactive')
            try:
                if action == "add":
                    printer = Printers()
                else:
                    printer = Printers.objects.using('infinyrealty').get(printer_id=printer_id)
                printer.tabname = tabname
                printer.url = url
                printer.sequence = sequence
                printer.iconclass = iconclass
                printer.isenabled = isactive
                if action == "delete":
                    printer.delete(using='infinyrealty')
                else:
                    printer.save(using='infinyrealty')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "system_template/printer_response_2.html", context)

def pageviewlog(accessid, loginid, username, username_org):
    pageview = PageView()
    pageview.loginid = loginid
    pageview.username = username
    pageview.logdatetime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    pageview.subcatid = accessid
    subcategory = SubCategories.objects.using('infinyrealty').get(subcatid=accessid)
    pageview.pagename = subcategory.subcatname
    if username != username_org and username_org != "":
        pageview.logintype = "Demo"
    else:
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

def hash_password(password):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Convert the password to bytes and hash it
    sha256_hash.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = sha256_hash.hexdigest()

    return hashed_password


def test_printer_mqtt_connection(topic):

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = "Z"
    qos = 2

    def on_connect(client, userdate, flags, rc):
        # print("connected with result code"+str(rc))
        clinet.username_pw_set(username, password)
        client.subscribe(topic)

    def on_message(client, userdata, message):
        print(f"Received Message:{message.payload.decode()}")
        received_message = message.payload.decode("utf-8")

    clinet = mqtt.Client("printer_subscriber")
    clinet.on_connect = on_connect
    clinet.on_message = on_message
    try:
        clinet.connect(broker_address, port, qos)
        clinet.loop_forever()
    except KeyboardInterrupt:
        print("Disconnecting....")
        clinet.disconnect()
    except Exception as e:
        print("An error occurred:", str(e))
        clinet.disconnect()


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

    try:
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
        return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs