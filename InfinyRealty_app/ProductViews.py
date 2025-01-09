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
from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks, Focusgroup, Focussubtypes
from InfinyRealty_app.models import AccessRights, QAIPFunction, PageView
from InfinyRealty_app.models import Printer, CodeDetails, Shops, Foods
from django.conf import settings

def dishes(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')
    if team == "admin": team = "east"

    shop_list = Shops.objects.using('zenpos').filter(status=1)
    food_category_list = CodeDetails.objects.using('zenpos').filter(shop=team, code_id=2, status=1)
    unit_list = CodeDetails.objects.using('zenpos').filter(shop=team, code_id=9, status=1)
    taste_list = CodeDetails.objects.using('zenpos').filter(shop=team, code_id=11, status=1)
    food_sub_category_list = CodeDetails.objects.using('zenpos').filter(shop=team, code_id=7, status=1)
    period_list = CodeDetails.objects.using('zenpos').filter(shop=team, code_id=1, status=1)
    food_status_list = CodeDetails.objects.using('zenpos').filter(shop=team, code_id=4, status=1)
    printer_list = Printer.objects.using('infinyrealty').filter(status=1)

    accessid = 76
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
        "user_shop": team,
        "food_category_list": food_category_list,
        "unit_list": unit_list,
        "taste_list": taste_list,
        "food_sub_category_list": food_sub_category_list,
        "period_list": period_list,
        "food_status_list": food_status_list,
        "printer_list": printer_list,
        "shop_list": shop_list,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "product_template/dishes.html", context)

@csrf_exempt
def dishes_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    team = request.POST.get('team')
    if team == "admin": team = "east"
    display = request.POST.get('display')
    today = datetime.datetime.now()
    code_id = "2"

    if action == "menutab":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+team+"' = '' then 1 when shop = '"+team+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        dishes_list = cursor.fetchall()

        context = {
            "action": action,
            "dishes_list": dishes_list,
            "sql": sql,
            "user_display": display,
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
    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_FoodCategory_Count")
        food_category_list = cursor.fetchall()

        context = {
            "action": action,
            "food_category_list": food_category_list,
            "user_team": team,
            "user_display": display,
        }
    if "view_" in action:
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        code_key = action.replace("view_", "")
        cursor.execute("select * from V_FoodCategory_List where code_key = '"+code_key+"'")
        food_category_list = cursor.fetchall()
        food_status_list = CodeDetails.objects.using('zenpos').filter(shop=team, code_id=4, status=1)

        context = {
            "action": action,
            "food_category_list": food_category_list,
            "food_status_list": food_status_list,
            "user_team": team,
            "user_category": code_key,
            "user_display": display,
        }

    if action == "add" or action == "edit" or action == "delete":
        if request.method == 'POST':
            food_id = request.POST.get('food_id')
            food_name = request.POST.get('food_name')
            food_name_e = request.POST.get('food_name_e')
            food_description = request.POST.get('food_description')
            food_photo = request.POST.get('food_photo')
            selling_price = request.POST.get('selling_price')
            unit = request.POST.get('unit')
            shop_code = request.POST.get('shop_code')
            food_group_id = 0
            food_category = request.POST.get('food_category')
            food_sub_category = request.POST.get('food_sub_category')
            taste = request.POST.get('taste')
            print_location = request.POST.get('print_location')
            period = request.POST.get('period')
            show_menu = request.POST.get('show_menu')
            food_status = request.POST.get('food_status')
            value_type = request.POST.get('value_type')
            east_b5_charge = request.POST.get('east_b5_charge')
            east_a5_charge = request.POST.get('east_a5_charge')
            coffee_b5_charge = request.POST.get('coffee_b5_charge')
            coffee_a5_charge = request.POST.get('coffee_a5_charge')
            status = request.POST.get('status')

            try:
                if action == "add":
                    food = Foods()
                else:
                    food = Foods.objects.using('zenpos').get(food_id=food_id)
                food.food_name = food_name
                food.food_name_e = food_name_e
                food.food_description = food_description
                food.food_photo = food_photo
                food.selling_price = selling_price
                food.unit = unit
                food.shop_code = shop_code
                food.food_group_id = food_group_id
                food.food_category = food_category
                food.food_sub_category = food_sub_category
                food.taste = taste
                food.print_location = print_location
                food.period = period
                food.show_menu = show_menu
                food.food_status = food_status
                food.value_type = value_type
                food.display_on_receipt = 1
                food.internal = 0
                food.east_b5_charge = east_b5_charge
                food.east_a5_charge = east_a5_charge
                food.coffee_b5_charge = coffee_b5_charge
                food.coffee_a5_charge = coffee_a5_charge
                food.status = status
                food.loginid = request.session.get('loginid')
                if action == "delete":
                    food.delete(using='zenpos')
                else:
                    food.save(using='zenpos')
                return JsonResponse({'message': 'The record was updated successfully.'})
            except Exception as e:
                return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)
    return render(request, "product_template/dishes_response.html", context)

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