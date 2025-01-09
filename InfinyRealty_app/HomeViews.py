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
from django.utils.datastructures import MultiValueDictKeyError
import json
import pyodbc
import urllib.parse as urlparse
import calendar
import datetime
import sys

from InfinyRealty_app.models import Roster, Users, UserInfo, Teams, Tabs, Categories, SubCategories, PageView, Sessions, Officers, Holiday, Focussubtypes, Focusgroup, Venues, Times, Bookings, Rooms, AccessRights, LoginHist, PropertyHighlights
from .forms import CheckRosterForm
from django.conf import settings

def home(request):
    if not request.session.get('loginid'): return redirect('login')
    request.session['httpreferer1'] = request.META.get('HTTP_REFERER')
    accessid = 1
    request.session['accessid'] = accessid
    if request.session.get('rent_view_page_size') is None: request.session['rent_view_page_size'] = 10
    if request.session.get('sell_view_page_size') is None: request.session['sell_view_page_size'] = 10
    if request.session.get('rentsell_view_page_size') is None: request.session['rentsell_view_page_size'] = 10

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select top 10 * from V_PropertyFullListHighlight where offertype = N'放售' and (HighlightType = 'sell' or Highlight is NULL) order by modifydate desc"
    cursor.execute(sql)
    property_sell_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select top 10 * from V_PropertyFullListHighlight where offertype = N'放租' and (HighlightType = 'rent' or Highlight is NULL) order by modifydate desc"
    cursor.execute(sql)
    property_rent_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select top 10 * from V_PropertyFullListHighlight where offertype = N'租售' and (HighlightType = 'sell' or HighlightType = 'rent' or Highlight is NULL) order by modifydate desc"
    cursor.execute(sql)
    property_rentsell_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select top 10 * from V_PropertyFullListHighlight where offertype = N'連租約售' and (HighlightType = 'sell' or HighlightType = 'rent' or Highlight is NULL) order by modifydate desc"
    cursor.execute(sql)
    property_rentsell_tenant_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select top 20 * from V_PropertyFollow order by followdate desc"
    cursor.execute(sql)
    property_follow_list = cursor.fetchall()

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
        "property_sell_view_list": property_sell_view_list,
        "property_rent_view_list": property_rent_view_list,
        "property_rentsell_view_list": property_rentsell_view_list,
        "property_rentsell_tenant_view_list": property_rentsell_tenant_view_list,
        "property_follow_list": property_follow_list,
    }
    return render(request, "home_template/home.html", context)

@csrf_exempt
def home_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    core = request.POST.get('core')
    sessionUsername = request.session.get('username')
    sessionLoginID = request.session.get('loginid')

    if action == 'qaip_function_list':
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPAccessRight  '" + str(sessionUsername) + "','" + str(core) + "'")
        functionList = cursor.fetchall()

        context = {
            "action": action,
            "core": core,
            "sessionusername": sessionUsername,
            "functionlist": functionList,
        }

    if action == "add_highlight":
        property_id = request.POST.get('property_id')
        flag = request.POST.get('flag')

        try:
            if PropertyHighlights.objects.using('infinyrealty').filter(propertyid=property_id,highlighttype=flag).exists():
                propertyhighlight = PropertyHighlights.objects.using('infinyrealty').get(propertyid=property_id,highlighttype=flag)
                propertyhighlight.delete()
            else:
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                propertyhighlight = PropertyHighlights()
                propertyhighlight.highlighttype = flag
                propertyhighlight.propertyid = property_id
                propertyhighlight.loginid = request.session.get('loginid')
                propertyhighlight.createdate = datetime_str
                propertyhighlight.isapprove = 1
                propertyhighlight.ismain = 1
                propertyhighlight.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "rent_view_page_size":
        request.session['rent_view_page_size'] = request.session.get("rent_view_page_size") + 10
        return HttpResponse("Success")
    if action == "sell_view_page_size":
        request.session['sell_view_page_size'] = request.session.get("sell_view_page_size") + 10
        return HttpResponse("Success")
    if action == "rentsell_view_page_size":
        request.session['rentsell_view_page_size'] = request.session.get("rentsell_view_page_size") + 10
        return HttpResponse("Success")

    return render(request, "home_template/home_response.html", context)

def outDated(request):
    if not request.session.get('loginid'): return redirect('login')
    request.session['httpreferer1'] = request.META.get('HTTP_REFERER')
    accessid = 1
    request.session['accessid'] = accessid
    if request.session.get('rent_view_page_size') is None: request.session['rent_view_page_size'] = 10
    if request.session.get('sell_view_page_size') is None: request.session['sell_view_page_size'] = 10
    if request.session.get('rentsell_view_page_size') is None: request.session['rentsell_view_page_size'] = 10

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select * from V_PropertyFullListHighlight where offertype = N'放售' and (HighlightType = 'sell' or Highlight is NULL) AND modifydate < DATEADD(DAY, -30, GETDATE()) order by modifydate desc"
    cursor.execute(sql)
    property_sell_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select * from V_PropertyFullListHighlight where offertype = N'放租' and (HighlightType = 'rent' or Highlight is NULL) AND modifydate < DATEADD(DAY, -30, GETDATE()) order by modifydate desc"
    cursor.execute(sql)
    property_rent_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select * from V_PropertyFullListHighlight where offertype = N'租售' and (HighlightType = 'sell' or HighlightType = 'rent' or Highlight is NULL) AND modifydate < DATEADD(DAY, -30, GETDATE()) order by modifydate desc"
    cursor.execute(sql)
    property_rentsell_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select * from V_PropertyFullListHighlight where offertype = N'連租約售' and (HighlightType = 'sell' or HighlightType = 'rent' or Highlight is NULL) AND modifydate < DATEADD(DAY, -30, GETDATE()) order by modifydate desc"
    cursor.execute(sql)
    property_rentsell_tenant_view_list = cursor.fetchall()

    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "select top 20 * from V_PropertyFollow order by followdate desc"
    cursor.execute(sql)
    property_follow_list = cursor.fetchall()

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
        "property_sell_view_list": property_sell_view_list,
        "property_rent_view_list": property_rent_view_list,
        "property_rentsell_view_list": property_rentsell_view_list,
        "property_rentsell_tenant_view_list": property_rentsell_tenant_view_list,
        "property_follow_list": property_follow_list,
    }
    return render(request, "home_template/outDated.html", context)

def home3(request):
    if not request.session.get('loginid'): return redirect('login')
    request.session['httpreferer1'] = request.META.get('HTTP_REFERER')
    accessid = 1
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
    return render(request, "home_template/home2.html", context)

@csrf_exempt
def home_response_3(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    core = request.POST.get('core')
    sessionUsername = request.session.get('username')
    sessionLoginID = request.session.get('loginid')

    if action == 'qaip_function_list':
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spSQPAccessRight  '" + str(sessionUsername) + "','" + str(core) + "'")
        functionList = cursor.fetchall()

        context = {
            "action": action,
            "core": core,
            "sessionusername": sessionUsername,
            "functionlist": functionList,
        }

    return render(request, "home_template/home_response_2.html", context)

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