from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
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
from datetime import timedelta
import os
import sys
import hashlib
from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks
from InfinyRealty_app.models import AccessRights, QAIPFunction, PageView, VisitTour, VisitTourForm, CodeDetails
from django.conf import settings

def visitTour(request):
    if not request.session.get('loginid'): return redirect('login')
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')

    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')

    accessid = 5173
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
        "teamlist": TeamList,
    }
    return render(request, "visit_tour_template/index.html", context)

@csrf_exempt
def visitTourResponse(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')

    if action == "menutab":
        context = {
            "action": action,
            # "start_date": start_date,
            # "end_date": end_date,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblMember")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }

    if action == "visit_tour_list":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = f"""
            SELECT * FROM tblVisitTour ORDER BY create_date DESC
        """
        params = ()
        cursor.execute(sql, params)
        visit_tour_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        visit_tour_form = VisitTourForm.objects.using('infinyrealty').get(id=1)

        context = {
            "action": action,
            "visit_tour_form": visit_tour_form,
            "visit_tour_list": visit_tour_list,
        }
    return render(request, "visit_tour_template/visit_tour_response.html", context)

    
@csrf_exempt
def visitTourForm_save(request):
    if not request.session.get('loginid'): return redirect('login')

    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    action = request.POST.get('action')
    id = request.POST.get('id')
    title = request.POST.get('title')
    title_sc = request.POST.get('title_sc')
    title_en = request.POST.get('title_en')
    desc = request.POST.get('desc')
    desc_sc = request.POST.get('desc_sc')
    desc_en = request.POST.get('desc_en')
    date_min = request.POST.get('date_min')
    date_max = request.POST.get('date_max')
    time = request.POST.get('time')
    
    try:
        
        visitTourForm = VisitTourForm.objects.using('infinyrealty').get(id=id)
        visitTourForm.modifydate = datetime_str
        visitTourForm.title = title
        visitTourForm.title_sc = title_sc
        visitTourForm.title_en = title_en
        visitTourForm.desc = desc
        visitTourForm.desc_sc = desc_sc
        visitTourForm.desc_en = desc_en
        visitTourForm.date_min = date_min
        visitTourForm.date_max = date_max
        visitTourForm.time = time
        visitTourForm.save(using='infinyrealty')
        return HttpResponse("Success")
        
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

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

def hash_password(password):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Convert the password to bytes and hash it
    sha256_hash.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = sha256_hash.hexdigest()

    return hashed_password