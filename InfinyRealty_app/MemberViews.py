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
from datetime import timedelta
import os
import sys
import hashlib
from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks
from InfinyRealty_app.models import AccessRights, QAIPFunction, PageView, Customers, CodeDetails
from InfinyRealty_app.models import Printer
from django.conf import settings

def member(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')

    accessid = 5152
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
    return render(request, "member_template/member.html", context)

@csrf_exempt
def member_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    team = request.POST.get('team')
    member_id = request.POST.get('member_id')
    if member_id is None:
        member_id = ""
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    user_member_id = member_id

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
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
    if action == "member_list":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblMember "  \
              "where (1 = case when '' = ? then 1 when join_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when join_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when member_id = ? then 1 else 0 end)  " \
              "order by join_date desc"
        params = (start_date, start_date, end_date, end_date, member_id, member_id)
        cursor.execute(sql, params)
        member_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_member_id": member_id,
            "member_list": member_list,
            "sql": sql,
        }
    if action == "member_active":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblMember "  \
              "where (1 = case when '' = ? then 1 when join_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when join_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when member_id = ? then 1 else 0 end)  " \
              "order by join_date desc"
        params = (start_date, start_date, end_date, end_date, member_id, member_id)
        cursor.execute(sql, params)
        member_active_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_team": team,
            "user_member_id": member_id,
            "member_active_list": member_active_list,
            "sql": sql,
        }
    return render(request, "member_template/member_response.html", context)

def customerNote(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    TeamList = Teams.objects.using('infinyrealty').exclude(teamdesc="admin").order_by('sequence')
    offer_type_list = CodeDetails.objects.using('infinyrealty').filter(code_id=10).order_by('sequence')
    usage_list = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 5168
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
        "offer_type_list": offer_type_list,
        "usage_list": usage_list,
    }
    return render(request, "member_template/customerNote.html", context)

@csrf_exempt
def customerNote_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    customer_id = request.POST.get('customer_id')
    if customer_id is None:
        customer_id = ""
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    user_customer_id = customer_id

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
        }
    if action == "customer_list":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblCustomer "  \
              "where (1 = case when '' = ? then 1 when create_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when create_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when customer_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (start_date, start_date, end_date, end_date, customer_id, customer_id)
        cursor.execute(sql, params)
        customer_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_customer_id": customer_id,
            "customer_list": customer_list,
            "start_date": start_date,
            "end_date": end_date,
            "sql": sql,
        }
    if action == "customer_info":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "select * from tblCustomer "  \
              "where (1 = case when '' = ? then 1 when customer_id = ? then 1 else 0 end)  " \
              "order by create_date desc"
        params = (customer_id, customer_id)
        cursor.execute(sql, params)
        customer_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        offer_type = request.POST.get('offer_type')
        sellingprice_from = request.POST.get('sellingprice_from')
        sellingprice_to = request.POST.get('sellingprice_to')
        rent_from = request.POST.get('rent_from')
        rent_to = request.POST.get('rent_to')
        if sellingprice_from == "None" or sellingprice_from is None:
            sellingprice_from = 0.00
        if sellingprice_to == "None" or sellingprice_to is None:
            sellingprice_to = 0.00
        if rent_from == "None" or rent_from is None:
            rent_from = 0.00
        if rent_to == "None" or rent_to is None:
            rent_to = 0.00


        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "exec spPropertyListRecommend '', '', '',N'"+offer_type+"',"+str(sellingprice_from)+","+str(sellingprice_to)+","+str(rent_from)+","+str(rent_to)+""
        cursor.execute("exec spPropertyListRecommend '', '', '',N'"+offer_type+"','"+str(sellingprice_from)+"','"+str(sellingprice_to)+"','"+str(rent_from)+"','"+str(rent_to)+"'")
        #call_sp = """EXEC spPropertyListRecommend @offer_type = N'{}', @sellingprice_from = {}, @sellingprice_to = {}, @rent_from = {}, @rent_to = {}.format(offer_type, sellingprice_from, sellingprice_to, rent_from, rent_to"""
        #cursor.execute(call_sp)
        property_recommend_list = cursor.fetchall()

        context = {
            "action": action,
            "user_customer_id": customer_id,
            "customer_list": customer_list,
            "property_recommend_list": property_recommend_list,
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
    return render(request, "member_template/customerNote_response.html", context)

@csrf_exempt
def customerNote_save(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    customer_id = request.POST.get('customer_id')
    customer_name = request.POST.get('customer_name')
    email = request.POST.get('email')
    phone_area_code = request.POST.get('phone_area_code')
    phone_number = request.POST.get('phone_number')
    industry = request.POST.get('industry')
    usage = request.POST.get('usage')
    area_from = request.POST.get('area_from')
    area_to = request.POST.get('area_to')
    offer_type = request.POST.get('offer_type')
    sellingprice_from = request.POST.get('sellingprice_from')
    sellingprice_to = request.POST.get('sellingprice_to')
    rent_from = request.POST.get('rent_from')
    rent_to = request.POST.get('rent_to')
    remarks = request.POST.get('remarks')
    status = request.POST.get('status')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    if action == "add" or action == "edit" or action == "delete":
        try:
            if action == "add":
                customer = Customers()
                customer.create_date = datetime_str
                customer.login_id = request.session.get('loginid')
            else:
                customer = Customers.objects.using('infinyrealty').get(customer_id=customer_id)
            customer.customer_name = customer_name
            customer.email = email
            customer.phone_area_code = phone_area_code
            customer.phone_number = phone_number
            customer.industry = industry
            customer.usage = usage
            customer.area_from = None if (area_from == "" or area_from == "0") else area_from
            customer.area_to = None if (area_to == "" or area_to == "0") else area_to
            customer.offer_type = offer_type
            if sellingprice_from == "" or sellingprice_from == "0":
                customer.sellingprice_from = None
            else:
                customer.sellingprice_from = sellingprice_from
            if sellingprice_to == "" or sellingprice_to == "0":
                customer.sellingprice_to = None
            else:
                customer.sellingprice_to = sellingprice_to
            if rent_from == "" or rent_from == "0":
                customer.rent_from = None
            else:
                customer.rent_from = rent_from
            if rent_to == "" or rent_to == "0":
                customer.rent_to = None
            else:
                customer.rent_to = rent_to
            customer.remarks = remarks
            customer.modify_date = datetime_str
            customer.status = status
            if action == "add" or action == "edit": customer.save(using='infinyrealty')
            if action == "delete": customer.delete()
            messages.success(request, "New Customer was created successfully.")
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