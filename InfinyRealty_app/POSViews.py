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
from django.db.models import Sum
from django.utils.datastructures import MultiValueDictKeyError
import hashlib
import json
import pyodbc
import urllib.parse as urlparse
import calendar
import datetime
import sys
import math
import numbers
from decimal import Decimal
import paho.mqtt.client as mqtt
from PIL import Image
import model.model as model
import util.xputil as util
import service.xpyunservice as service
import formatter.note_formatter as formatter
#import win32com.shell.shell as shell
#import pythoncom


from zenPOS_app.models import Roster, Users, UserInfo, Teams, Tabs, Categories, SubCategories, PageView, Sessions, Officers, Holiday, Focussubtypes, Focusgroup, Venues, Rooms, AccessRights, LoginHist
from zenPOS_app.models import Times, Tables, Bookings, Members, Shops, CodeDetails, Printer, PrinterLogs, DineIns, Orders, OrderItems, OrderLogs, OrderNumbers, OrderItemDetails, Invoices, InvoicePayments, InvoiceSnapshots, ProductDetails, Products
from zenPOS_app.models import ESCPOSManager
from django.conf import settings

def order(request):
    if not request.session.get('username'): return HttpResponseRedirect('/login')
    shop_code = request.session.get('default_shop_code')
    if shop_code == "" or shop_code is None:
        shop_code = request.session.get('team')
    shop_list = Shops.objects.using('zenpos').filter(status=1)

    product_category_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=2, status=1)
    unit_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=9, status=1)
    dim_sum_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=7, status=1)
    period_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=1, status=1)
    product_list = Products.objects.using('zenpos').filter(status=1).filter(product_type__in=["P", "M", "C", "W"])
    product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)
    taste_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=11, status=1)
    printer_list = Printer.objects.using('zenpos').filter(status=1)
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
    table_dinein_list = cursor.fetchall()
    today = datetime.datetime.now()

    accessid = 45
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('zensystem').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='zensystem')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        #"user_loginid": loginid,
        "user_shop": shop_code,
        "product_category_list": product_category_list,
        "unit_list": unit_list,
        "taste_list": taste_list,
        "dim_sum_list": dim_sum_list,
        "period_list": period_list,
        "product_status_list": product_status_list,
        "product_list": product_list,
        "printer_list": printer_list,
        "table_dinein_list": table_dinein_list,
        "shop_list": shop_list,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "today": today,
    }
    return render(request, "pos_template/order.html", context)

@csrf_exempt
def order_response(request):
    if not request.session.get('username'): return HttpResponseRedirect('/login')
    action = request.POST.get('action')
    shop_code = request.POST.get('shop_code')
    display = request.POST.get('display')
    today = datetime.datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    code_id = "2"
    if request.session.get('show_currency') == "1":
        currency = "MOP"
    else:
        currency = "$"

    def round_down_to_decimals(number, decimals):
        factor = 10 ** decimals
        return math.floor(number * factor) / factor

    if action == "menutab":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        dishes_list = cursor.fetchall()

        context = {
            "action": action,
            "dishes_list": dishes_list,
            "sql": sql,
            "user_shop_code": shop_code,
            "user_display": display,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '"+shop_code+"', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "order_selection":
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M")
        date_str = datetime_dt.strftime("%Y-%m-%d")

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_TakeawayDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' order by order_date desc")
        takeaway_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_DeliveryDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' order by order_date desc")
        delivery_dinein_list = cursor.fetchall()
        order_type_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=10, status=1).order_by('sequence')
        table_list = Tables.objects.using('zenpos').filter(shop_code=shop_code, status=1)

        context = {
            "action": action,
            "order_type_list": order_type_list,
            "table_dinein_list": table_dinein_list,
            "takeaway_dinein_list": takeaway_dinein_list,
            "delivery_dinein_list": delivery_dinein_list,
            "today_datetime": datetime_str,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }

    if action == "table_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code= '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        context = {
            "action": action,
            "table_dinein_list": table_dinein_list,
            "currency": currency,
        }

    if action == 'event_list':
        SelectDate = request.POST.get('selectdate', None)
        StartDate = request.POST.get('startdate', None)
        EndDate = request.POST.get('enddate', None)
        SelectTeam = request.POST.get('team', None)
        SelectRoom = request.POST.get('room', None)
        if (SelectTeam == 'None'): SelectTeam = ''
        if (SelectRoom == 'None'): SelectRoom = ''

        StartDate = datetime.date(int(StartDate[0:4]), int(StartDate[5:7]), int(StartDate[8:10]))
        EndDate = datetime.date(int(EndDate[0:4]), int(EndDate[5:7]), int(EndDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(start_date=SelectDate).order_by('start_date')
        RoomList = Rooms.objects.using('zensystem').filter(isactive=1)
        TimeList = Times.objects.using('zensystem').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','"+ SelectTeam + "','"+ SelectRoom + "', '1'")
        eventlist = cursor.fetchall()

        #EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')
        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
            "currency": currency,
        }

    if action == 'latest_order':
        try:
            # Retrieve the latest order based on the 'created_at' field (or another relevant field)
            latest_order = Orders.objects.using('zenpos').order_by('-order_date').first()  # Change 'created_at' to your actual timestamp field

            if latest_order:
                latest_order_id = latest_order.order_id  # Access the latest order_id
                dinein = DineIns.objects.using('zenpos').filter(order_id=latest_order_id)
                if dinein:
                    latest_status = dinein[0].status
                else:
                    latest_status = 1
                return JsonResponse({
                    'order_id': latest_order.order_id,
                    'order_number': latest_order.order_number,
                    'order_status': latest_status
                })
            else:
                return HttpResponse('No orders found')

        except Exception as e:
            return JsonResponse({'message': 'Failed to retrieve latest order. Error: {}'.format(e)}, status=500)

    if action == 'select_order':
        SelectDate = request.POST.get('selectdate', None)
        StartDate = request.POST.get('startdate', None)
        EndDate = request.POST.get('enddate', None)
        SelectTeam = request.POST.get('team', None)
        SelectRoom = request.POST.get('room', None)
        if (SelectTeam == 'None'): SelectTeam = ''
        if (SelectRoom == 'None'): SelectRoom = ''

        StartDate = datetime.date(int(StartDate[0:4]), int(StartDate[5:7]), int(StartDate[8:10]))
        EndDate = datetime.date(int(EndDate[0:4]), int(EndDate[5:7]), int(EndDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(
            start_date=SelectDate).order_by('start_date')
        RoomList = Rooms.objects.using('zensystem').filter(isactive=1)
        TimeList = Times.objects.using('zensystem').filter(isactive=1)

        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '" + StartDate.strftime('%Y-%m-%d') + "','" + EndDate.strftime(
            '%Y-%m-%d') + "','" + SelectTeam + "','" + SelectRoom + "', '1'")
        eventlist = cursor.fetchall()

        # EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')
        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
            "currency": currency,
        }
    if action == 'order_item_list':
        order_id = request.POST.get('order_id')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        invoice_payment_list = cursor.fetchall()

        if order_cost_list:
            order_item_status = order_cost_list[0].status
            order_total_quantity_cart = order_cost_list[0].total_quantity_cart
            order_total_quantity_order = order_cost_list[0].total_quantity_order
            order_total_quantity_discount = order_cost_list[0].total_quantity_discount
            order_total_quantity = order_cost_list[0].total_quantity
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = order_cost_list[0].total_cost_order
            order_total_cost_discount = order_cost_list[0].total_cost_discount
            order_total_cost = order_cost_list[0].total_cost
        else:
            order_total_quantity_cart = 0
            order_total_quantity_order = 0
            order_total_quantity_discount = 0
            order_total_quantity = 0
            order_total_cost_cart = 0
            order_total_cost_order = 0
            order_total_cost_discount = 0
            order_total_cost = 0

        context = {
            "action": action,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_quantity_cart": order_total_quantity_cart,
            "order_total_quantity_order": order_total_quantity_order,
            "order_total_quantity_discount": order_total_quantity_discount,
            "order_total_quantity": order_total_quantity,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost_discount": order_total_cost_discount,
            "order_total_cost": order_total_cost,
            "order_item_detail_list": order_item_detail_list,
            "invoice_payment_list": invoice_payment_list,
            "currency": currency,
        }
    if action == 'order_operation':
        order_id = request.POST.get('order_id')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        if order_cost_list:
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = order_cost_list[0].total_cost_order
            order_total_cost_discount = order_cost_list[0].total_cost_discount
            order_total_cost = order_cost_list[0].total_cost

        context = {
            "action": action,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost_discount": order_total_cost_discount,
            "order_total_cost": order_total_cost,
            "currency": currency,
        }
    if action == 'order_cart_list':
        order_id = request.POST.get('order_id')
        display_type = request.POST.get('type')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        invoice_payment_list = cursor.fetchall()

        if order_cost_list:
            order_total_quantity_cart = order_cost_list[0].total_quantity_cart
            order_total_quantity_order = order_cost_list[0].total_quantity_order
            order_total_quantity_discount = order_cost_list[0].total_quantity_discount
            order_total_quantity = order_cost_list[0].total_quantity
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = order_cost_list[0].total_cost_order
            order_total_cost_discount = order_cost_list[0].total_cost_discount
            order_total_cost = order_cost_list[0].total_cost
        else:
            order_total_quantity_cart = 0
            order_total_quantity_order = 0
            order_total_quantity_discount = 0
            order_total_quantity = 0
            order_total_cost_cart = 0
            order_total_cost_order = 0
            order_total_cost_discount = 0
            order_total_cost = 0
        taste_list = CodeDetails.objects.using('zenpos').filter(shop_code="east", code_id=11, status=1)

        context = {
            "action": action,
            "display_type": display_type,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_quantity_cart": order_total_quantity_cart,
            "order_total_quantity_order": order_total_quantity_order,
            "order_total_quantity_discount": order_total_quantity_discount,
            "order_total_quantity": order_total_quantity,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost_discount": order_total_cost_discount,
            "order_total_cost": order_total_cost,
            "order_item_detail_list": order_item_detail_list,
            "invoice_payment_list": invoice_payment_list,
            "taste_list": taste_list,
            "currency": currency,
        }

    if action == "product_extra_list":
        product_id = request.POST.get('product_id')
        type = request.POST.get('type')
        product_list = Products.objects.using('zenpos').get(product_id=product_id)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductDetail_Group where product_id = "+product_id)
        product_detail_group = cursor.fetchall()
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductDetail_Item where status = 1 and product_id = "+product_id)
        product_detail_item = cursor.fetchall()
        context = {
            "action": action,
            "product_list": product_list,
            "product_detail_group": product_detail_group,
            "product_detail_item": product_detail_item,
            "currency": currency,
        }

    if action == "product_input_list":
        product_id = request.POST.get('product_id')
        type = request.POST.get('type')
        product_list = Products.objects.using('zenpos').get(product_id=product_id)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        sql = "select * from V_ProductDetail_Group where product_id = "+product_id
        cursor.execute("select * from V_ProductDetail_Group where product_id = "+product_id)
        product_detail_group = cursor.fetchall()
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductDetail_Item where status = 1 and product_id = "+product_id)
        product_detail_item = cursor.fetchall()
        context = {
            "action": action,
            "product_list": product_list,
            "product_detail_group": product_detail_group,
            "product_detail_item": product_detail_item,
            "currency": currency,
            "sql": sql,
        }

    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductCategory_Count")
        product_category_list = cursor.fetchall()

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }
    if "view_" in action:
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        code_key = action.replace("view_", "")
        cursor.execute("select * from V_ProductCategory_List where code_key = '"+code_key+"'")
        product_category_list = cursor.fetchall()
        cursor.execute("select * from tblCodeDetail where code_key = '"+code_key+"' and shop_code = '"+shop_code+"' and code_id = 2")
        product_category = cursor.fetchall()

        if product_category_list:
            product_category_name = product_category_list[0].code_detail_name
        else:
            if product_category:
                product_category_name = product_category[0].code_detail_name
            else:
                product_category_name = ""
        product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "product_status_list": product_status_list,
            "product_category_name": product_category_name,
            "user_shop_code": shop_code,
            "user_category": code_key,
            "user_display": display,
            "currency": currency,
        }

    if action == "product_search":
        product_code = request.POST.get('product_code')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        #sql = "select * from V_ProductCategory_List where product_code like N'%"+str(product_code)+"%' and shop_code = '"+shop_code+"'"
        #cursor.execute("select * from V_ProductCategory_List where product_code like N'%"+str(product_code)+"%' or bar_code like N'"+str(product_code)+"' or product_name like N'%"+str(product_code)+"%' and shop_code = '"+shop_code+"'")
        if len(product_code) == 10:
            sql = "select * from V_ProductCategory_List where product_code = N'"+str(product_code)+"'"
        if len(product_code) == 13:
            sql = "select * from V_ProductCategory_List where bar_code = N'"+str(product_code)+"'"
        if len(product_code) != 10 and len(product_code) != 13:
            sql = "select * from V_ProductCategory_List where product_name like N'%"+str(product_code)+"%' or bar_code like N'%"+str(product_code)+"%' or product_code like N'%"+str(product_code)+"%'"
        cursor.execute(sql)
        product_category_list = cursor.fetchall()

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "user_shop_code": shop_code,
            "user_display": display,
            "user_keyword": product_code,
            "currency": currency,
            "sql": sql,
        }

    if action == "add_dinein":
        username = request.POST.get('username')
        booking_id = request.POST.get('booking_id')
        member_id = request.POST.get('member_id')
        order_id = request.POST.get('order_id')
        member_number = request.POST.get('member_number')
        number_guests = request.POST.get('number_guests')
        table_key = request.POST.get('table_key')
        shop_code = request.POST.get('shop_code')

        order_type = request.POST.get('order_type')

        try:
            if action == "add_dinein" or action == "confirm_guest":
                dinein = DineIns()
            else:
                dinein = DineIns.objects.using('zenpos').get(dinein_id=dinein_id)

            # Add other data fields
            try:
                table = Tables.objects.using('zenpos').filter(table_key=table_key)
                dinein.table_id = table[0].table_id
            except:
                dinein.table_id = 0
            table_id = dinein.table_id
            try:
                member = Members.objects.using('zenpos').filter(member_number=member_number)
                dinein.member_id = member[0].member_id
            except:
                dinein.member_id = 0
            member_id = dinein.member_id
            try:
                order = Orders()
                order.member_id = member_id
                order.order_number = getOrderNumber()
                order.order_type = order_type
                order.order_date = today
                if shop_code == "east":
                    order.service_charge = 10
                    order.tea_charge = 10
                    order.other_charge = 20
                    order.special_discount = 0
                else:
                    order.service_charge = 0
                    order.tea_charge = 0
                    order.other_charge = 0
                    order.special_discount = 0
                order.loginid = request.session.get('loginid')
                order.save(using='zenpos')
                #dinein.order_id = Orders.objects.using('zenpos').aggregate(Max('order_id'))['order_id__max'] + 1
                dinein.order_id = order.order_id
                dinein.order_number = order.order_number
                order_id = order.order_id
            except:
                dinein.order_id = 0

            dinein.booking_id = booking_id
            dinein.shop_code = shop_code
            dinein.number_guests = number_guests
            dinein.table_key = table_key
            dinein.member_number = member_number
            dinein.in_date = today
            dinein.status = 1
            dinein.loginid = request.session.get('loginid')
            dinein.save(using='zenpos')

            if int(booking_id) > 0:
                booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
                booking.show_status = 1
                booking.loginid = request.session.get('loginid')
                booking.save(using='zenpos')

        except Exception as e:
            return JsonResponse({'message': 'Update record failed1. Error: {}'.format(e)}, status=500)
        return HttpResponse(order_id)

    if action == "add_takeaway":
        username = request.POST.get('username')
        booking_id = request.POST.get('booking_id')
        member_id = request.POST.get('member_id')
        order_id = request.POST.get('order_id')
        member_number = request.POST.get('member_number')
        number_guests = request.POST.get('number_guests')
        table_key = "T888"
        shop_code = request.POST.get('shop_code')

        order_type = request.POST.get('order_type')

        try:
            if action == "add_takeaway":
                dinein = DineIns()
            else:
                dinein = DineIns.objects.using('zenpos').get(dinein_id=dinein_id)

            # Add other data fields
            try:
                table = Tables.objects.using('zenpos').filter(table_key=table_key)
                dinein.table_id = table[0].table_id
            except:
                dinein.table_id = 0
            table_id = dinein.table_id
            try:
                member = Members.objects.using('zenpos').filter(member_number=member_number)
                dinein.member_id = member[0].member_id
            except:
                dinein.member_id = 0
            member_id = dinein.member_id
            try:
                order = Orders()
                order.member_id = member_id
                order.order_number = getOrderNumber()
                order.order_type = order_type
                order.order_date = today
                order.kitchen_status = 0
                order.service_charge = 0
                order.tea_charge = 0
                order.other_charge = 0
                order.special_discount = 0
                order.loginid = request.session.get('loginid')
                order.save(using='zenpos')
                #dinein.order_id = Orders.objects.using('zenpos').aggregate(Max('order_id'))['order_id__max'] + 1
                dinein.order_id = order.order_id
                dinein.order_number = order.order_number
            except:
                dinein.order_id = 0

            dinein.booking_id = booking_id
            dinein.shop_code = shop_code
            dinein.number_guests = number_guests
            dinein.table_key = order_type+dinein.order_number
            dinein.member_number = member_number
            dinein.in_date = today
            dinein.status = 1
            dinein.loginid = request.session.get('loginid')
            dinein.save(using='zenpos')

            if int(booking_id) > 0:
                booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
                booking.show_status = 1
                booking.loginid = request.session.get('loginid')
                booking.save(using='zenpos')

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
            return JsonResponse({'message': 'Error: {}'. str(e) }, status=500)
            #return JsonResponse({'message': 'Update record failed1. Error: {}'.format(e)}, status=500)
        return JsonResponse({
            'order_id': dinein.order_id,
            'order_number': dinein.order_number
        })
        #return HttpResponse(dinein.order_id)

    if action == "add_delivery":
        username = request.POST.get('username')
        booking_id = request.POST.get('booking_id')
        member_id = request.POST.get('member_id')
        order_id = request.POST.get('order_id')
        member_number = request.POST.get('member_number')
        number_guests = request.POST.get('number_guests')
        table_key = "D888"
        shop_code = request.POST.get('shop_code')

        order_type = request.POST.get('order_type')

        try:
            if action == "add_delivery":
                dinein = DineIns()
            else:
                dinein = DineIns.objects.using('zenpos').get(dinein_id=dinein_id)

            # Add other data fields
            try:
                table = Tables.objects.using('zenpos').filter(table_key=table_key)
                dinein.table_id = table[0].table_id
            except:
                dinein.table_id = 0
            table_id = dinein.table_id
            try:
                member = Members.objects.using('zenpos').filter(member_number=member_number)
                dinein.member_id = member[0].member_id
            except:
                dinein.member_id = 0
            member_id = dinein.member_id
            try:
                order = Orders()
                order.member_id = member_id
                order.order_number = getOrderNumber()
                order.order_type = order_type
                order.order_date = today
                order.kitchen_status = 0
                order.service_charge = 0
                order.tea_charge = 0
                order.other_charge = 0
                order.special_discount = 0
                order.loginid = request.session.get('loginid')
                order.save(using='zenpos')
                #dinein.order_id = Orders.objects.using('zenpos').aggregate(Max('order_id'))['order_id__max'] + 1
                dinein.order_id = order.order_id
                dinein.order_number = order.order_number
            except:
                dinein.order_id = 0

            dinein.booking_id = booking_id
            dinein.shop_code = shop_code
            dinein.number_guests = number_guests
            dinein.table_key = order_type+dinein.order_number
            dinein.member_number = member_number
            dinein.in_date = today
            dinein.status = 1
            dinein.loginid = request.session.get('loginid')
            dinein.save(using='zenpos')

            if int(booking_id) > 0:
                booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
                booking.show_status = 1
                booking.loginid = request.session.get('loginid')
                booking.save(using='zenpos')

        except Exception as e:
            return JsonResponse({'message': 'Update record failed1. Error: {}'.format(e)}, status=500)
        return JsonResponse({
            'order_id': dinein.order_id,
            'order_number': dinein.order_number
        })

    if action == "update_order_setting":
        order_id = request.POST.get('order_id')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        order_item_type = request.POST.get('order_item_type')
        order_sequence = 0
        status = 0
        order_number = request.POST.get('order_number')
        product_name = request.POST.get('product_name')
        product_name_e = request.POST.get('product_name_e')
        selling_price = request.POST.get('selling_price')
        product_description = request.POST.get('product_description')

        try:
            if Orders.objects.using('zenpos').filter(order_id=order_id).exists():
                order = Orders.objects.using('zenpos').get(order_id=order_id)
                if "服務費" in product_name:
                    order.service_charge = selling_price
                if "茶位" in product_name:
                    order.tea_charge = selling_price
                if "醬介" in product_name:
                    order.other_charge = selling_price
                if "經理" in product_name:
                    order.special_discount = selling_price
                order.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "add_item" or action == "update_item" or action == "add_input":
        shop_code = request.POST.get('shop_code')
        order_id = request.POST.get('order_id')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        order_item_type = request.POST.get('order_item_type')
        order_sequence = 0
        status = 0
        order_number = request.POST.get('order_number')
        product_name = request.POST.get('product_name')
        product_name_e = request.POST.get('product_name_e')
        selling_price = request.POST.get('selling_price')
        selling_price_user = request.POST.get('selling_price')
        product_description = request.POST.get('product_description')
        product_type = request.POST.get('product_type')
        add_taste = request.POST.get('add_taste')

        if product_type == "S":
            # 買一送一
            if selling_price == "0.00" and product_name == "買一送一":
                total_free_price = 0
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P']).order_by('selling_price')
                item_count = orderitem.count()
                free_count = int(item_count / 2)
                counter = 0
                if orderitem:
                    for u in orderitem:
                        counter += 1
                        if counter <= free_count:
                            total_free_price = total_free_price + u.selling_price * u.quantity
                            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                            if orderitemdetail:
                                for v in orderitemdetail:
                                    total_free_price = total_free_price + v.selling_price
                selling_price = total_free_price * -1
                #cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
                #cursor = cnxn.cursor()
                #cursor.execute("select * from V_OrderItem_Cost_List where order_id = " + str(order_id) + " and product_type = 'M'")
                #order_item_cost_list = cursor.fetchall()

                #selling_price_list = []
                #total_free_price = 0
                #for item in order_item_cost_list:
                #    quantity = item.quantity  # Get the quantity of the item
                #    selling_price = item.selling_price
                #    total_extra_selling_price = item.total_extra_selling_price  # Get the selling price of the item
                #    selling_price_list.extend([selling_price + total_extra_selling_price] * quantity)
                # number_of_items = len(selling_price_list)
                #selling_price_list.sort()
                #for i in range(0, len(selling_price_list) - 1, 2):
                #    total_free_price += selling_price_list[i]

                #selling_price = total_free_price * -1
            # 全單免費
            if selling_price == "0.00" and product_name == "全單免費":
                total_free_price = 0
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                if orderitem:
                    for u in orderitem:
                        total_free_price = total_free_price + u.selling_price * u.quantity
                        orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                        if orderitemdetail:
                            for v in orderitemdetail:
                                total_free_price = total_free_price + v.selling_price * u.quantity
                selling_price = total_free_price * -1
            # 員工優惠(10%) and 十一75折
            if product_name == "員工優惠(10%)" or product_name == "十一75折" or product_name == "理工優惠(5%)" or product_name == "經理優惠(15%)":
                total_free_price = 0
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                if orderitem:
                    for u in orderitem:
                        total_free_price = total_free_price + u.selling_price * u.quantity
                        orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                        if orderitemdetail:
                            for v in orderitemdetail:
                                total_free_price = total_free_price + v.selling_price * u.quantity
                selling_price_final = (float(total_free_price) * float(selling_price) / 100)
                selling_price_rounded = round_down_to_decimals(selling_price_final, 1)
                selling_price = selling_price_rounded
            # 經理簽單
            if product_name == "經理簽單":
                product_name = "經理簽單" + "("+str(selling_price_user)+"%)"
            # 新張期內減兩蚊, TH 住戶優惠, VIP 優惠
            if selling_price == "-2.00" and product_name == "TH 住戶優惠" or product_name == "VIP 優惠":
                total_free_price = 0
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P']).order_by('selling_price')
                if orderitem:
                    for u in orderitem:
                        total_free_price = total_free_price + (2 * u.quantity)
                selling_price = total_free_price * -1
            # 新張期內減兩蚊, TH 住戶優惠, CS 員工優惠, Infiny 員工優惠, VIP 優惠
            if selling_price == "-2.00" and product_name == "新張期內減兩蚊" or product_name == "CS 員工優惠" or product_name == "Infiny 員工優惠":
                total_free_price = 2
                selling_price = total_free_price * -1

        try:
            if product_type == "P":
                if OrderItems.objects.using('zenpos').filter(order_id=order_id,product_id=product_id,status=0).exists():
                    orderitem = OrderItems.objects.using('zenpos').get(order_id=order_id, product_id=product_id, status=0)
                    if action != "update_item":
                        orderitem.quantity = int(orderitem.quantity) + int(quantity)
                    else:
                        orderitem.quantity = int(orderitem.quantity)
                else:
                    orderitem = OrderItems()
                    orderitem.quantity = quantity
            else:
                if action == "update_item":
                    if OrderItems.objects.using('zenpos').filter(order_id=order_id,product_id=product_id,status=0).exists():
                        orderitem = OrderItems.objects.using('zenpos').get(order_id=order_id, product_id=product_id, status=0)
                        orderitem.quantity = int(orderitem.quantity)
                else:
                    orderitem = OrderItems()
                    orderitem.quantity = quantity

            orderitem.order_id = order_id
            orderitem.product_id = product_id
            orderitem.product_sale_type = 'S'
            orderitem.order_item_date = order_item_date
            orderitem.order_item_type = order_item_type
            orderitem.order_sequence = order_sequence
            orderitem.status = status
            orderitem.order_number = order_number
            orderitem.product_name = product_name
            orderitem.product_name_e = product_name_e
            orderitem.selling_price = selling_price
            orderitem.product_description = product_description
            orderitem.product_type = product_type
            orderitem.loginid = request.session.get('loginid')
            if orderitem.quantity == 0:
                orderitem.delete(using='zenpos')
            else:
                orderitem.save(using='zenpos')

            if add_taste != "":
                if OrderItemDetails.objects.using('zenpos').filter(order_item_id=orderitem.order_item_id).exists():
                    orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=orderitem.order_item_id)
                    orderitemdetail.delete()

                #taste_add_list = add_taste[:-1].split(',')
                taste_add_list = add_taste.split(',')
                index = 0

                for taste_add_value in taste_add_list:
                    orderitemdetail = OrderItemDetails()
                    orderitemdetail.order_item_id = orderitem.order_item_id
                    orderitemdetail.item_id = index + 1
                    #taste_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_detail_id=taste_add_value, status=1)
                    productdetail = ProductDetails.objects.using('zenpos').filter(product_id=product_id, code_detail_id=taste_add_value, status=1)
                    if productdetail:
                        orderitemdetail.code_detail_id = productdetail[0].code_detail_id
                        orderitemdetail.code_detail_name = productdetail[0].product_detail_name
                        orderitemdetail.selling_price = productdetail[0].selling_price
                    else:
                        orderitemdetail.code_detail_id = 0
                        orderitemdetail.code_detail_name = ""
                        orderitemdetail.selling_price = 0
                    orderitemdetail.status = 1
                    orderitemdetail.loginid = request.session.get('loginid')
                    orderitemdetail.save(using='zenpos')
                    index += 1
        except Exception as e:
            return JsonResponse({'message': 'Update add item failed. Error: {}'.format(e)}, status=500)

        # Recalculate product_type "S"
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type='S').exists():
                orderitem_update = OrderItems.objects.using('zenpos').get(order_id=order_id, product_type='S')

                # 買一送一
                if orderitem_update.product_name == "買一送一":
                    #total_free_price = 0
                    #orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type='M').order_by('selling_price')
                    #item_count = orderitem.count()
                    #free_count = int(item_count / 2)
                    #counter = 0
                    #if orderitem:
                    #    for u in orderitem:
                    #        counter += 1
                    #        if counter <= free_count:
                    #            total_free_price = total_free_price + u.selling_price * u.quantity
                    #            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(
                    #                order_item_id=u.order_item_id)
                    #            if orderitemdetail:
                    #                for v in orderitemdetail:
                    #                    total_free_price = total_free_price + v.selling_price
                    #selling_price = total_free_price * -1
                    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
                    cursor = cnxn.cursor()
                    cursor.execute("select * from V_OrderItem_Cost_List where order_id = " + str(order_id) + " and (product_type = 'M' or product_type = 'P')")
                    order_item_cost_list = cursor.fetchall()

                    selling_price_list = []
                    total_free_price = 0
                    for item in order_item_cost_list:
                        quantity = item.quantity  # Get the quantity of the item
                        selling_price = item.selling_price
                        total_extra_selling_price = item.total_extra_selling_price# Get the selling price of the item
                        selling_price_list.extend([selling_price+total_extra_selling_price] * quantity)
                    # number_of_items = len(selling_price_list)
                    selling_price_list.sort()
                    for i in range(0, len(selling_price_list)-1,2):
                        total_free_price += selling_price_list[i]

                    selling_price = total_free_price * -1
                # 一杯免費
                if orderitem_update.product_name == "一杯免費":
                    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
                    cursor = cnxn.cursor()
                    cursor.execute("select * from V_OrderItem_Cost_List where order_id = " + str(order_id) + " and (product_type = 'M' or product_type = 'P')")
                    order_item_cost_list = cursor.fetchall()

                    selling_price_list = []
                    total_free_price = 0
                    for item in order_item_cost_list:
                        quantity = item.quantity  # Get the quantity of the item
                        selling_price = item.selling_price
                        total_extra_selling_price = item.total_extra_selling_price# Get the selling price of the item
                        selling_price_list.extend([selling_price+total_extra_selling_price] * quantity)
                    # number_of_items = len(selling_price_list)
                    selling_price_list.sort()
                    if selling_price_list:
                        total_free_price += selling_price_list[0]
                    else:
                        total_free_price = 0

                    selling_price = total_free_price * -1
                # 全單免費
                if orderitem_update.product_name == "全單免費":
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + u.selling_price * u.quantity
                            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                            if orderitemdetail:
                                for v in orderitemdetail:
                                    total_free_price = total_free_price + v.selling_price * u.quantity
                    selling_price = total_free_price * -1
                # 員工優惠(10%) and 十一75折
                if orderitem_update.product_name == "員工優惠(10%)" or orderitem_update.product_name == "十一75折" or orderitem_update.product_name == "理工優惠(5%)" or orderitem_update.product_name == "經理優惠(15%)":
                    product = Products.objects.using('zenpos').filter(shop_code=shop_code, product_id=orderitem_update.product_id, status=1)
                    if product:
                        selling_price_original = product[0].selling_price
                    else:
                        selling_price_original = 0
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + u.selling_price * u.quantity
                            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                            if orderitemdetail:
                                for v in orderitemdetail:
                                    total_free_price = total_free_price + v.selling_price * u.quantity
                    selling_price_final = (float(total_free_price) * float(selling_price_original) / 100)
                    selling_price_rounded = round_down_to_decimals(selling_price_final, 1)
                    selling_price = selling_price_rounded
                # 經理簽單
                if "經理簽單" in orderitem_update.product_name:
                    selling_price_original = selling_price_user
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + u.selling_price * u.quantity
                            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                            if orderitemdetail:
                                for v in orderitemdetail:
                                    total_free_price = total_free_price + v.selling_price * u.quantity
                    selling_price_final = (float(total_free_price) * float(selling_price_original) / 100)
                    selling_price_rounded = round_down_to_decimals(selling_price_final, 1)
                    selling_price = selling_price_rounded
                # TH 住戶優惠, VIP 優惠
                if selling_price == "-2.00" and orderitem_update.product_name == "TH 住戶優惠" or orderitem_update.product_name == "VIP 優惠":
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P']).order_by('selling_price')
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + (2 * u.quantity)
                    selling_price = total_free_price * -1
                # 新張期內減兩蚊, CS 員工優惠, Infiny 員工優惠
                if selling_price == "-2.00" and orderitem_update.product_name == "新張期內減兩蚊" or orderitem_update.product_name == "CS 員工優惠" or orderitem_update.product_name == "Infiny 員工優惠":
                    total_free_price = 2
                    selling_price = total_free_price * -1

                if orderitem_update.product_name == "買一送一" or orderitem_update.product_name == "一杯免費" or orderitem_update.product_name == "全單免費" or orderitem_update.product_name == "員工優惠(10%)" or orderitem_update.product_name == "十一75折" or orderitem_update.product_name == "理工優惠(5%)" or orderitem_update.product_name == "經理優惠(15%)" or "經理簽單" in orderitem_update.product_name or orderitem_update.product_name == "新張期內減兩蚊" or orderitem_update.product_name == "TH 住戶優惠" or orderitem_update.product_name == "CS 員工優惠" or orderitem_update.product_name == "Infiny 員工優惠" or orderitem_update.product_name == "VIP 優惠":
                    orderitem_update.selling_price = selling_price
                    orderitem_update.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)


        return HttpResponse('Update Success')

    if action == "add_cart":
        order_item_id = request.POST.get('order_item_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        order_item_type = request.POST.get('order_item_type')
        product_name = request.POST.get('product_name')
        selling_price = request.POST.get('selling_price')
        selling_price_user = request.POST.get('selling_price')
        shop_code = request.POST.get('shop_code')
        status = 0
        try:
            if OrderItems.objects.using('zenpos').filter(order_item_id=order_item_id).exists():
                orderitem = OrderItems.objects.using('zenpos').get(order_item_id=order_item_id)
                orderitem.order_item_type = order_item_type
                orderitem.quantity = int(orderitem.quantity) + int(quantity)
                orderitem.selling_price = selling_price
                orderitem.order_item_date = order_item_date
                orderitem.loginid = request.session.get('loginid')
                order_id = orderitem.order_id
            if orderitem.quantity == 0:
                orderitem.delete(using='zenpos')
            else:
                orderitem.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

        # Recalculate product_type "S"
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type='S').exists():
                orderitem_update = OrderItems.objects.using('zenpos').get(order_id=order_id, product_type='S')

                # 買一送一
                if orderitem_update.product_name == "買一送一":
                    #total_free_price = 0
                    #orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type='M').order_by('selling_price')
                    #item_count = orderitem.count()
                    #free_count = int(item_count / 2)

                    #counter = 0
                    #if orderitem:
                    #    for u in orderitem:
                    #        counter += 1
                    #        if counter <= free_count:
                    #            total_free_price = total_free_price + u.selling_price * u.quantity
                    #            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                    #            if orderitemdetail:
                    #                for v in orderitemdetail:
                    #                    total_free_price = total_free_price + v.selling_price
                    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
                    cursor = cnxn.cursor()
                    cursor.execute("select * from V_OrderItem_Cost_List where order_id = " + str(order_id) + " and (product_type = 'M' or product_type = 'P')")
                    order_item_cost_list = cursor.fetchall()

                    selling_price_list = []
                    total_free_price = 0
                    for item in order_item_cost_list:
                        quantity = item.quantity  # Get the quantity of the item
                        selling_price = item.selling_price
                        total_extra_selling_price = item.total_extra_selling_price# Get the selling price of the item
                        selling_price_list.extend([selling_price+total_extra_selling_price] * quantity)
                    # number_of_items = len(selling_price_list)
                    selling_price_list.sort()
                    for i in range(0, len(selling_price_list)-1,2):
                        total_free_price += selling_price_list[i]

                    selling_price = total_free_price * -1
                # 一杯免費
                if orderitem_update.product_name == "一杯免費":
                    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
                    cursor = cnxn.cursor()
                    cursor.execute("select * from V_OrderItem_Cost_List where order_id = " + str(order_id) + " and (product_type = 'M' or product_type = 'P')")
                    order_item_cost_list = cursor.fetchall()

                    selling_price_list = []
                    total_free_price = 0
                    for item in order_item_cost_list:
                        quantity = item.quantity  # Get the quantity of the item
                        selling_price = item.selling_price
                        total_extra_selling_price = item.total_extra_selling_price# Get the selling price of the item
                        selling_price_list.extend([selling_price+total_extra_selling_price] * quantity)
                    # number_of_items = len(selling_price_list)
                    selling_price_list.sort()
                    if selling_price_list:
                        total_free_price += selling_price_list[0]
                    else:
                        total_free_price = 0

                    selling_price = total_free_price * -1
                # 全單免費
                if orderitem_update.product_name == "全單免費":
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + u.selling_price * u.quantity
                            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                            if orderitemdetail:
                                for v in orderitemdetail:
                                    total_free_price = total_free_price + v.selling_price * u.quantity
                    selling_price = total_free_price * -1
                # 員工優惠(10%) and 十一75折
                if orderitem_update.product_name == "員工優惠(10%)" or orderitem_update.product_name == "十一75折" or orderitem_update.product_name == "理工優惠(5%)" or orderitem_update.product_name == "經理優惠(15%)" or orderitem_update.product_name == "經理簽單":
                    product = Products.objects.using('zenpos').filter(shop_code=shop_code, product_id=orderitem_update.product_id, status=1)
                    if product:
                        selling_price_original = product[0].selling_price
                    else:
                        selling_price_original = 0
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + u.selling_price * u.quantity
                            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                            if orderitemdetail:
                                for v in orderitemdetail:
                                    total_free_price = total_free_price + v.selling_price * u.quantity
                    selling_price_final = (float(total_free_price) * float(selling_price_original) / 100)
                    selling_price_rounded = round_down_to_decimals(selling_price_final, 1)
                    selling_price = selling_price_rounded
                # 經理簽單
                if "經理簽單" in orderitem_update.product_name:
                    start_index = orderitem_update.product_name.find("(") + 1
                    end_index = orderitem_update.product_name.find("%)")
                    selling_price_user = orderitem_update.product_name[start_index:end_index]
                    selling_price_original = selling_price_user
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P'])
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + u.selling_price * u.quantity
                            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=u.order_item_id)
                            if orderitemdetail:
                                for v in orderitemdetail:
                                    total_free_price = total_free_price + v.selling_price * u.quantity
                    selling_price_final = (float(total_free_price) * float(selling_price_original) / 100)
                    selling_price_rounded = round_down_to_decimals(selling_price_final, 1)
                    selling_price = selling_price_rounded
                # TH 住戶優惠, VIP 優惠
                if selling_price == "-2.00" and orderitem_update.product_name == "TH 住戶優惠" or orderitem_update.product_name == "VIP 優惠":
                    total_free_price = 0
                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type__in=['M', 'P']).order_by('selling_price')
                    if orderitem:
                        for u in orderitem:
                            total_free_price = total_free_price + (2 * u.quantity)
                    selling_price = total_free_price * -1
                # 新張期內減兩蚊, CS 員工優惠, Infiny 員工優惠,
                if selling_price == "-2.00" and orderitem_update.product_name == "新張期內減兩蚊" or orderitem_update.product_name == "CS 員工優惠" or orderitem_update.product_name == "Infiny 員工優惠":
                    total_free_price = 2
                    selling_price = total_free_price * -1

                if orderitem_update.product_name == "買一送一" or orderitem_update.product_name == "一杯免費" or orderitem_update.product_name == "全單免費" or orderitem_update.product_name == "員工優惠(10%)" or orderitem_update.product_name == "十一75折" or orderitem_update.product_name == "理工優惠(5%)" or orderitem_update.product_name == "經理優惠(15%)" or "經理簽單" in orderitem_update.product_name or orderitem_update.product_name == "新張期內減兩蚊" or orderitem_update.product_name == "TH 住戶優惠" or orderitem_update.product_name == "CS 員工優惠" or orderitem_update.product_name == "Infiny 員工優惠" or orderitem_update.product_name == "VIP 優惠":
                    orderitem_update.selling_price = selling_price
                    orderitem_update.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

        return HttpResponse('Update Success')

    if action == "add_taste":
        order_item_id = request.POST.get('order_item_id')
        item_taste = str(request.POST.get('item_taste'))
        item_taste_array = item_taste.split(",")
        status = request.POST.get('status')
        quantity = request.POST.get('quantity')

        try:
            if action == "add_taste":
                orderitemdetail = OrderItemDetails()
            else:
                orderitemdetail = OrderItemDetails.objects.using('zenpos').get(order_item_id=order_item_id)
            for w in item_taste_array:
                orderitemdetail.order_item_id = order_item_id
                orderitemdetail.item_id = 1
                orderitemdetail.code_key = w
                orderitemdetail.code_detail_name = w
                orderitemdetail.status = status
                orderitemdetail.loginid = request.session.get('loginid')
                if quantity == 0:
                    orderitemdetail.delete(using='zenpos')
                else:
                    orderitemdetail.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "remove_taste":
        order_item_id = request.POST.get('order_item_id')
        try:
            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=order_item_id)
            orderitemdetail.delete()
        except Exception as e:
            return JsonResponse({'message': 'aaUpdate record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "password_checking":
        password_approval = request.POST.get('password_approval')
        try:
            hashed_password = hash_password(password_approval)
            users = Users.objects.using('zensystem').filter(team=request.session.get('team')).filter(password=hashed_password).filter(isactive=1)
            if users:
                return HttpResponse('Checking Success')
            else:
                return HttpResponse('Checking Fail')

        except Exception as e:
            return JsonResponse({'message': 'Checking record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Checking Success')

    if action == "cancel_order":
        order_id = request.POST.get('order_id')
        remarks = request.POST.get('remark')
        #out_date = today
        status = 0
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').filter(order_id=order_id,status=3)
                dinein.update(status=status)
        except Exception as e:
            return JsonResponse({'message': '1Update record failed. Error: {}'.format(e)}, status=500)

        try:
            if Invoices.objects.using('zenpos').filter(order_id=order_id).exists():
                invoice = Invoices.objects.using('zenpos').filter(order_id=order_id)
                invoice_id = invoice[0].invoice_id
                invoice.update(status=status,remarks=remarks)
        except Exception as e:
            return JsonResponse({'message': '2Update record failed. Error: {}'.format(e)}, status=500)

        try:
            if InvoicePayments.objects.using('zenpos').filter(invoice_id=invoice_id).exists():
                invoicepayment = InvoicePayments.objects.using('zenpos').filter(invoice_id=invoice_id, status=1)
                invoicepayment.update(status=status)
        except Exception as e:
            return JsonResponse({'message': '3Update record failed. Error: {}'.format(e)}, status=500)

        return HttpResponse('Update Success')

    if action == "cancel_payment":
        order_id = request.POST.get('order_id')
        #out_date = today
        status = 1
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').filter(order_id=order_id,status=2)
                dinein.update(status=status)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

        order_id = request.POST.get('order_id')
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=1)
                orderitem.update(status=0)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

        return HttpResponse('Update Success')

    if action == "confirm_payment":
        order_id = request.POST.get('order_id')
        #out_date = today
        status = 2
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').filter(order_id=order_id,status=1)
                dinein.update(status=status)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "confirm_cart":
        order_id = request.POST.get('order_id')
        order_item_date = today
        status = 1
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                try:
                    order_sequence_max = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=1).aggregate(Max('order_sequence'))['order_sequence__max'] + 1
                except:
                    order_sequence_max = 1
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=0)
                orderitem.update(order_item_date=order_item_date, order_sequence=order_sequence_max, status=status, loginid=request.session.get('loginid'))
                #printOrder(request)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "confirm_cart_payment":
        order_id = request.POST.get('order_id')
        order_item_date = today
        #out_date = today
        #Confirm Order Item First
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                try:
                    order_sequence_max = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=1).aggregate(Max('order_sequence'))['order_sequence__max'] + 1
                except:
                    order_sequence_max = 1
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=0)
                orderitem.update(order_item_date=order_item_date, order_sequence=order_sequence_max, status=1, loginid=request.session.get('loginid'))
                #printOrder(request)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

        status = 2
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').filter(order_id=order_id,status=1)
                dinein.update(status=status)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "payment_cart_list":
        order_id = request.POST.get('order_id')
        payment_method_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=6, status=1)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        invoice_payment_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        if order_cost_list:
            order_type = order_dinein_list[0].order_type
            order_number = order_dinein_list[0].order_number
            number_guests = order_dinein_list[0].number_guests
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            if order_cost_list[0].total_cost_order != "NULL":
                order_total_cost_order = order_cost_list[0].total_cost_order
            else:
                order_total_cost_order = 0
            if order_cost_list[0].total_cost_discount != "NULL":
                order_total_cost_discount = (order_cost_list[0].total_cost_discount)
            else:
                order_total_cost_discount = 0
            order_total_cost = order_cost_list[0].total_cost
            tea_charge = int(number_guests) * order_item_list[0].tea_charge
            other_charge = order_item_list[0].other_charge
            service_charge = (order_total_cost_order + tea_charge + other_charge) * (order_item_list[0].service_charge / 100)
            if order_type == "T" or order_type == "D" or order_type == "O":
                order_total_cost_final = order_total_cost_order + order_total_cost_discount
            else:
                order_total_cost_final = order_total_cost_order + tea_charge + service_charge
            special_discount = order_total_cost_final * (order_item_list[0].special_discount / 100)
            order_total_cost_final = order_total_cost_final * ((100 - order_item_list[0].special_discount) / 100)

        if invoice_payment_list:
            for u in invoice_payment_list:
                order_total_cost_final = order_total_cost_final - u.receivable_amount

        context = {
            "action": action,
            "payment_method_list": payment_method_list,
            "display_type": "2",
            "shop_code": shop_code,
            "order_number": order_number,
            "order_type": order_type,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost_discount": order_total_cost_discount,
            "order_total_cost": order_total_cost,
            "order_item_detail_list": order_item_detail_list,
            "invoice_payment_list": invoice_payment_list,
            "service_charge": service_charge,
            "tea_charge": tea_charge,
            "other_charge": other_charge,
            "special_discount": special_discount,
            "number_guests": number_guests,
            "order_total_cost_final": order_total_cost_final,
            "currency": currency,
            "today": today,
        }

    if action == "settle_payment":
        order_id = request.POST.get('order_id')
        order_status = request.POST.get('order_status')
        # order_status = 2 - Partial Payment
        # order_status = 3 - Complete Payment
        status = order_status
        out_date = today
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")

        # get order number first
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').get(order_id=order_id,status=2)
                order_number = dinein.order_number
        except Exception as e:
            return JsonResponse({'message': 'Get order number fail! Order ID is '+order_id+'. Error: {}'.format(e)}, status=500)

        shop_code = request.POST.get('shop_code')
        member_id = request.POST.get('member_id')
        booking_id = request.POST.get('booking_id')
        payment_sequence = request.POST.get('payment_sequence')
        invoice_number = "E"+datetime_str+order_number
        invoice_type = request.POST.get('invoice_type')
        currency = request.POST.get('currency')
        invoice_amount = request.POST.get('invoice_amount')
        outstanding_amount = request.POST.get('outstanding_amount')

        payment_method = request.POST.get('payment_method')
        currency = request.POST.get('currency')
        receivable_amount = request.POST.get('receivable_amount')
        change_amount = request.POST.get('change_amount')
        tips_amount = request.POST.get('tips_amount')
        transaction_reference = request.POST.get('transaction_reference')

        #payment_method_2 = request.POST.get('payment_method_2')
        #receivable_amount_2 = request.POST.get('receivable_amount_2')
        #transaction_reference_2 = request.POST.get('transaction_reference_2')

        # get invoice ID first if exist
        try:
            if Invoices.objects.using('zenpos').filter(order_id=order_id).exists():
                invoice = Invoices.objects.using('zenpos').get(order_id=order_id)
                invoice_id = invoice.invoice_id
            else:
                invoice_id = 0
        except Exception as e:
            return JsonResponse({'message': 'Get order number fail! Order ID is '+order_id+'. Error: {}'.format(e)}, status=500)

        invoice_date = out_date
        status = 1
        member_id = 0
        booking_id = 0
        invoice_type = "2"
        try:
            if Invoices.objects.using('zenpos').filter(invoice_id=invoice_id).exists():
                invoice = Invoices.objects.using('zenpos').get(invoice_id=invoice_id)
            else:
                invoice = Invoices()

            if payment_sequence == "1":
                invoice.shop_code = shop_code
                invoice.order_id = order_id
                invoice.member_id = member_id
                invoice.booking_id = booking_id
                invoice.invoice_number = invoice_number
                invoice.invoice_type = invoice_type
                invoice.invoice_amount = invoice_amount
                invoice.outstanding_amount = outstanding_amount
                invoice.tips_amount = tips_amount

                invoice.payment_method = payment_method
                invoice.transaction_reference = transaction_reference
                invoice.receivable_amount = receivable_amount
                invoice.invoice_date = invoice_date
            else:
                invoice.outstanding_amount = outstanding_amount
                invoice.payment_method_2 = payment_method
                invoice.receivable_amount_2 = receivable_amount
                invoice.transaction_reference_2 = transaction_reference

            if outstanding_amount > "0":
                invoice_status = 0
            else:
                invoice_status = 1
            invoice.status = invoice_status
            invoice.loginid = request.session.get('loginid')
            invoice.save(using='zenpos')

            invoicepayment = InvoicePayments()
            invoicepayment.invoice_id = invoice.invoice_id
            invoicepayment.payment_sequence = payment_sequence
            invoicepayment.payment_method = payment_method
            invoicepayment.currency = currency
            invoicepayment.receivable_amount = receivable_amount
            invoicepayment.change_amount = change_amount
            invoicepayment.tips_amount = tips_amount
            invoicepayment.transaction_reference = str(transaction_reference)
            invoicepayment.transaction_date = today
            invoicepayment.status = status
            invoicepayment.loginid = request.session.get('loginid')
            invoicepayment.save(using='zenpos')

        except Exception as e:
            #exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            #line_number = exception_traceback.tb_lineno
            #return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
            #return JsonResponse({'message': 'Error: {}'. str(e) }, status=500)
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

        orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id)
        try:
            for item in orderitem:
                product_id = item.product_id
                item_quantity = item.quantity
                product = Products.objects.using('zenpos').get(product_id=product_id)
                if product:
                    if product.product_type == "P":
                        number_of_stock = int(product.stock) - int(item_quantity)
                        product.stock = number_of_stock
                        product.save(using='zenpos')
                    if int(product.capacity) != 1 and product.product_type == "M" and product.product_group_id != 0:
                        product_group = Products.objects.using('zenpos').get(product_id=product.product_group_id)
                        number_of_capacity = int(product_group.remain_capacity) - int(product.capacity) * int(item_quantity)
                        product_group.remain_capacity = number_of_capacity
                        product_group.save(using='zenpos')

        except Exception as e:
            return JsonResponse({'message': 'Order ID:'+order_id+'|Product Group ID: Update product quantity failed. Error: {}'.format(e)}, status=500)

        # Complete the order
        if outstanding_amount > "0":
            status = 2
        else:
            status = 3
            orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type='M')
            item_count = orderitem.count()
            if item_count == 0:
                kitchen_date = today
                kitchen_status = 1
                try:
                    if Orders.objects.using('zenpos').filter(order_id=order_id).exists():
                        order = Orders.objects.using('zenpos').get(order_id=order_id, kitchen_status=0)
                        order.kitchen_date = kitchen_date
                        order.kitchen_status = kitchen_status
                        order.save(using='zenpos')
                except Exception as e:
                    return JsonResponse({'message': 'xx'+order_id+'Update kitchen status failed. Error: {}'.format(e)}, status=500)
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').get(order_id=order_id,status=2)
                order_number = dinein.order_number
                dinein = DineIns.objects.using('zenpos').filter(order_id=order_id,status=2)
                dinein.update(out_date=out_date, status=status)
        except Exception as e:
            return JsonResponse({'message': 'xx'+order_id+'Update record failed. Error: {}'.format(e)}, status=500)

        return HttpResponse('Update Success')

    if action == "settle_payment_ref":
        order_id = request.POST.get('order_id')
        order_status = request.POST.get('order_status')
        # order_status = 2 - Partial Payment
        # order_status = 3 - Complete Payment
        status = order_status
        out_date = today
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")

        # get order number first
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').get(order_id=order_id,status=2)
                order_number = dinein.order_number
        except Exception as e:
            return JsonResponse({'message': 'Get order number fail! Order ID is '+order_id+'. Error: {}'.format(e)}, status=500)

        shop_code = request.POST.get('shop_code')
        member_id = request.POST.get('member_id')
        booking_id = request.POST.get('booking_id')
        payment_sequence = request.POST.get('payment_sequence')
        invoice_number = "E"+datetime_str+order_number
        invoice_type = request.POST.get('invoice_type')
        currency = request.POST.get('currency')
        invoice_amount = request.POST.get('invoice_amount')
        outstanding_amount = request.POST.get('outstanding_amount')

        payment_method = request.POST.get('payment_method')
        currency = request.POST.get('currency')
        receivable_amount = request.POST.get('receivable_amount')
        change_amount = request.POST.get('change_amount')
        tips_amount = request.POST.get('tips_amount')
        transaction_reference = request.POST.get('transaction_reference')

        #payment_method_2 = request.POST.get('payment_method_2')
        #receivable_amount_2 = request.POST.get('receivable_amount_2')
        #transaction_reference_2 = request.POST.get('transaction_reference_2')

        # get invoice ID first if exist
        try:
            if Invoices.objects.using('zenpos').filter(order_id=order_id).exists():
                invoice = Invoices.objects.using('zenpos').get(order_id=order_id)
                invoice_id = invoice.invoice_id
            else:
                invoice_id = 0
        except Exception as e:
            return JsonResponse({'message': 'Get order number fail! Order ID is '+order_id+'. Error: {}'.format(e)}, status=500)

        invoice_date = out_date
        status = 1
        member_id = 0
        booking_id = 0
        invoice_type = "1"
        try:
            if Invoices.objects.using('zenpos').filter(invoice_id=invoice_id).exists():
                invoice = Invoices.objects.using('zenpos').get(invoice_id=invoice_id)
            else:
                invoice = Invoices()

            if payment_sequence == "1":
                invoice.shop_code = shop_code
                invoice.order_id = order_id
                invoice.member_id = member_id
                invoice.booking_id = booking_id
                invoice.invoice_number = invoice_number
                invoice.invoice_type = invoice_type
                invoice.invoice_amount = invoice_amount
                invoice.outstanding_amount = outstanding_amount
                invoice.tips_amount = tips_amount

                invoice.payment_method = payment_method
                invoice.transaction_reference = transaction_reference
                invoice.receivable_amount = receivable_amount
                invoice.invoice_date = invoice_date
            else:
                invoice.outstanding_amount = outstanding_amount
                invoice.payment_method_2 = payment_method
                invoice.receivable_amount_2 = receivable_amount
                invoice.transaction_reference_2 = transaction_reference

            if outstanding_amount > "0":
                invoice_status = 0
            else:
                invoice_status = 1
            invoice.status = invoice_status
            invoice.loginid = request.session.get('loginid')
            invoice.save(using='zenpos')

            invoicepayment = InvoicePayments()
            invoicepayment.invoice_id = invoice.invoice_id
            invoicepayment.payment_sequence = payment_sequence
            invoicepayment.payment_method = payment_method
            invoicepayment.currency = currency
            invoicepayment.receivable_amount = receivable_amount
            invoicepayment.change_amount = change_amount
            invoicepayment.tips_amount = tips_amount
            invoicepayment.transaction_reference = str(transaction_reference)
            invoicepayment.transaction_date = today
            invoicepayment.status = status
            invoicepayment.loginid = request.session.get('loginid')
            invoicepayment.save(using='zenpos')

        except Exception as e:
            #exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            #line_number = exception_traceback.tb_lineno
            #return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
            #return JsonResponse({'message': 'Error: {}'. str(e) }, status=500)
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

        orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id)
        try:
            for item in orderitem:
                product_id = item.product_id
                item_quantity = item.quantity
                product = Products.objects.using('zenpos').get(product_id=product_id)
                if product.product_type == "P":
                    number_of_stock = int(product.stock) - int(item_quantity)
                    product.stock = number_of_stock
                    product.save(using='zenpos')
                if int(product.capacity) != 1 and product.product_type == "M":
                    product_group = Products.objects.using('zenpos').get(product_id=product.product_group_id)
                    number_of_capacity = int(product_group.remain_capacity) - int(product.capacity) * int(item_quantity)
                    product_group.remain_capacity = number_of_capacity
                    product_group.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'xx'+order_id+'Update product quantity failed. Error: {}'.format(e)}, status=500)

        # Complete the order
        if outstanding_amount > "0":
            status = 2
        else:
            status = 3
            orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type='M')
            item_count = orderitem.count()
            if item_count == 0:
                kitchen_date = today
                kitchen_status = 1
                try:
                    if Orders.objects.using('zenpos').filter(order_id=order_id).exists():
                        order = Orders.objects.using('zenpos').get(order_id=order_id, kitchen_status=0)
                        order.kitchen_date = kitchen_date
                        order.kitchen_status = kitchen_status
                        order.save(using='zenpos')
                except Exception as e:
                    return JsonResponse({'message': 'xx'+order_id+'Update kitchen status failed. Error: {}'.format(e)}, status=500)
        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').get(order_id=order_id,status=2)
                order_number = dinein.order_number
                dinein = DineIns.objects.using('zenpos').filter(order_id=order_id,status=2)
                dinein.update(out_date=out_date, status=status)
        except Exception as e:
            return JsonResponse({'message': 'xx'+order_id+'Update record failed. Error: {}'.format(e)}, status=500)

        return HttpResponse('Update Success')

    if action == "back_to_cart":
        order_id = request.POST.get('order_id')
        try:
            #if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
            #    dinein = DineIns.objects.using('zenpos').get(order_id=order_id,status=2)
            #    dinein.update(status=1)

            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=1)
                orderitem.update(status=0)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "reset_cart":
        order_id = request.POST.get('order_id')
        order_item_date = today
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=0)
                orderitem.delete()
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "print_receipt":
        order_id = request.POST.get('order_id')
        print_type = request.POST.get('print_type')
        try:
            #printer_return = printOrderLogo(request, order_id, print_type)
            if request.session.get('default_shop_code') == "tiffanylife":
                printer_return = printOrderItemReceipt_XPrinter(request, order_id, print_type)
            else:
                printer_return = printOrderItemReceipt(request, order_id, print_type)
        except Exception as e:
            return JsonResponse({'message': 'Print failed. Error: {}'.format(e)}, status=500)
        return HttpResponse(' '+str(printer_return)+' Order ID:'+str(order_id))

    if action == "print_label":
        order_id = request.POST.get('order_id')
        print_type = request.POST.get('print_type')
        try:
            printer_return = printOrderItemLabel(request, order_id, print_type)
        except Exception as e:
            return JsonResponse({'message': 'Print failed. Error: {}'.format(e)}, status=500)
        return HttpResponse(' '+str(printer_return)+' Order ID:'+str(order_id))

    if action == "print_label_paper":
        order_id = request.POST.get('order_id')
        print_type = request.POST.get('print_type')
        try:
            printer_return = printOrderItemLabelPaper(request, order_id, print_type)
        except Exception as e:
            return JsonResponse({'message': 'Print failed. Error: {}'.format(e)}, status=500)
        return HttpResponse(' '+str(printer_return)+' Order ID:'+str(order_id))

    if action == "print_order":
        order_id = request.POST.get('order_id')
        print_type = request.POST.get('print_type')
        try:
            if request.session.get('default_shop_code') == "tiffanylife":
                printer_return = printOrderItemReceipt_XPrinter(request, order_id, print_type)
            else:
                printer_return = printOrderItemAll(request, order_id, print_type)
        except Exception as e:
            return JsonResponse({'message': 'Print failed. Error: {}'.format(e)}, status=500)
        return HttpResponse(' '+str(printer_return)+' Order ID:'+str(order_id))

    if action == "print_cart":
        order_id = request.POST.get('order_id')
        try:
            printOrderItemCost(request, order_id)
        except Exception as e:
            return JsonResponse({'message': 'Print failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Print Success')

    if action == "reprint_cart":
        order_id = request.POST.get('order_id')
        table_key = request.POST.get('table_key')
        order_number = request.POST.get('order_number')
        product_name = request.POST.get('product_name')
        quantity = request.POST.get('quantity')
        order_item_type = request.POST.get('order_item_type')
        try:
            printOrderItem(request, table_key, order_number, product_name, quantity, order_item_type)
        except Exception as e:
            return JsonResponse({'message': 'Print failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Print Success')

    if action == "change_guest":
        order_id = request.POST.get('order_id')
        table_id = request.POST.get('table_id')
        table_key = request.POST.get('table_key')
        change_number_guests = request.POST.get('change_number_guests')

        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                try:
                    dinein = DineIns.objects.using('zenpos').get(order_id=order_id)
                    dinein.number_guests = change_number_guests
                    dinein.loginid = request.session.get('loginid')
                    dinein.save(using='zenpos')
                except:
                    return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "change_table":
        order_id = request.POST.get('order_id')
        table_id = request.POST.get('table_id')
        table_key = request.POST.get('table_key')
        change_table_key = request.POST.get('change_table_key')

        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                try:
                    dinein = DineIns.objects.using('zenpos').get(order_id=order_id)
                    table = Tables.objects.using('zenpos').filter(table_key=change_table_key)
                    dinein.table_id = table[0].table_id
                    dinein.table_key = change_table_key
                    dinein.save(using='zenpos')
                except:
                    return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "merge_table":
        order_id = request.POST.get('order_id')
        table_id = request.POST.get('table_id')
        table_key = request.POST.get('table_key')
        change_table_key = request.POST.get('change_table_key')
        change_order_id = request.POST.get('change_order_id')

        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                try:
                    dinein = DineIns.objects.using('zenpos').get(order_id=order_id)
                    dinein.status = 4
                    dinein.save(using='zenpos')

                    orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id)
                    order_sequence_max = OrderItems.objects.using('zenpos').filter(order_id=order_id, status=1).aggregate(Max('order_sequence'))['order_sequence__max'] + 1

                    for item in orderitem:
                        OrderItems.objects.using('zenpos').create(
                            order_id=change_order_id,
                            product_id=item.product_id,
                            quantity=item.quantity,
                            order_item_date=item.order_item_date,
                            order_item_type=3,
                            order_sequence=order_sequence_max,
                            status=item.status,
                            order_number=item.order_number,
                            product_name=item.product_name,
                            product_name_e=item.product_name_e,
                            selling_price=item.selling_price,
                            product_description=item.product_description,
                            product_type=item.product_type,
                            loginid=request.session.get('loginid'),
                        )
                except:
                    return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "check_product_type":
        order_id = request.POST.get('order_id')
        try:
            orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_type='S')
            item_count = orderitem.count()
            if item_count > 0:
                return HttpResponse(item_count)
            else:
                return HttpResponse(0)  # Adjusted response for clarity
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

    if action == "check_stock_inventory":
        order_id = request.POST.get('order_id')
        product_id = request.POST.get('product_id')
        try:
            product = Products.objects.using('zenpos').get(product_id=product_id)
            if product.product_type == "P":
                number_of_stock = int(product.stock)
                orderitem_sum = OrderItems.objects.using('zenpos').filter(order_id=order_id, product_id=product_id).aggregate(total_quantity=Sum('quantity'))
                number_of_stock_in_cart = orderitem_sum['total_quantity'] or 0
                if number_of_stock >= number_of_stock_in_cart + 1:
                    return HttpResponse("available")
                else:
                    return HttpResponse("out_of_stock")
            return HttpResponse("no_record")
        except Exception as e:
            return JsonResponse({'message': 'check stock inventory failed. Error: {}'.format(e)}, status=500)

    if action == "check_total_cost":
        order_id = request.POST.get('order_id')
        try:
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
            cursor = cnxn.cursor()
            cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
            order_cost_list = cursor.fetchall()
            if order_cost_list:
                total_cost = order_cost_list[0].total_cost
            else:
                total_cost = 10
            if total_cost > 0:
                return HttpResponse(total_cost)
            else:
                return HttpResponse(0)  # Adjusted response for clarity
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

    if action == "check_order_type_exist":
        order_type = request.POST.get('order_type')
        try:
            dinein = DineIns.objects.using('zenpos').filter(in_date__gt=today_str, status__in=[1, 2]).order_by('-in_date')
            dinein_count = dinein.count()
            if dinein_count > 0:
                if Orders.objects.using('zenpos').filter(order_id=dinein[0].order_id, order_type=order_type).exists():
                    return HttpResponse(1)
                else:
                    return HttpResponse(0)
            else:
                return HttpResponse(0)  # Adjusted response for clarity
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)

    if action == "check_table_available":
        table_key = request.POST.get('table_key')
        try:
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
            cursor = cnxn.cursor()
            cursor.execute("select * from V_TableDinein_List where table_key = '" + table_key + "'")
            table_dinein_list = cursor.fetchall()
            if table_dinein_list:
                if table_dinein_list[0].dinein_id is None:
                    return HttpResponse('Yes')
                else:
                    return HttpResponse('No')
            else:
                return HttpResponse('Fail')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
    return render(request, "pos_template/order_response.html", context)

def deliveryCall(request):
    #if not request.session.get('username'): return redirect('login')
    shop_code = request.POST.get('shop_code')
    shop_code = "fortunetea"
    if shop_code == "" or shop_code is None:
        shop_code = request.session.get('team')

    shop_list = Shops.objects.using('zenpos').filter(status=1)
    if shop_list and shop_code == "admin":
        shop_code = shop_list[0].shop_code

    product_category_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=2, status=1)
    unit_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=9, status=1)
    dim_sum_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=7, status=1)
    period_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=1, status=1)
    product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)
    taste_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=11, status=1)
    printer_list = Printer.objects.using('zenpos').filter(status=1)
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
    table_dinein_list = cursor.fetchall()
    today = datetime.datetime.now()

    #accessid = 45
    #request.session['accessid'] = accessid
    #cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
    #cursor_menu = cnxn_menu.cursor()
    #cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    #menuItem = cursor_menu.fetchall()
    #cursor_menu.execute("select * from V_UserAccessRight where username = '"+str(request.session.get('username'))+"'")
    #menuList = cursor_menu.fetchall()
    #users = Users.objects.using('zensystem').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='zensystem')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        #"user_loginid": loginid,
        "user_shop": shop_code,
        "product_category_list": product_category_list,
        "unit_list": unit_list,
        "taste_list": taste_list,
        "dim_sum_list": dim_sum_list,
        "period_list": period_list,
        "product_status_list": product_status_list,
        "printer_list": printer_list,
        "table_dinein_list": table_dinein_list,
        "shop_list": shop_list,
    }
    return render(request, "pos_template/deliveryCall.html", context)

@csrf_exempt
def deliveryCall_response(request):
    #if not request.session.get('username'): return HttpResponseRedirect('/login')
    action = request.POST.get('action')
    shop_code = request.POST.get('shop_code')
    display = request.POST.get('display')
    today = datetime.datetime.now()
    code_id = "2"
    if request.session.get('show_currency') == "0":
        currency = "$"
    else:
        currency = "MOP"

    if action == "menutab":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        dishes_list = cursor.fetchall()

        context = {
            "action": action,
            "dishes_list": dishes_list,
            "sql": sql,
            "user_shop_code": shop_code,
            "user_display": display,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '"+shop_code+"', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "order_selection":
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M")
        date_str = datetime_dt.strftime("%Y-%m-%d")

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_TakeawayDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' order by order_date desc")
        takeaway_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_TakeawayDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' and datediff(minute, kitchen_date, GETDATE()) < 5 order by order_date desc")
        takeaway_dinein_completed_list = cursor.fetchall()
        cursor.execute("select * from V_DeliveryDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' order by order_date desc")
        delivery_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_DeliveryDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' and datediff(minute, kitchen_date, GETDATE()) < 5 order by order_date desc")
        delivery_dinein_completed_list = cursor.fetchall()
        order_type_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=10, status=1).order_by('sequence')
        order_type_delivery_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=10, code_key='D', status=1)
        table_list = Tables.objects.using('zenpos').filter(shop_code=shop_code, status=1)

        context = {
            "action": action,
            "order_type_list": order_type_list,
            "order_type_delivery_list": order_type_delivery_list,
            "table_dinein_list": table_dinein_list,
            "takeaway_dinein_list": takeaway_dinein_list,
            "takeaway_dinein_completed_list": takeaway_dinein_completed_list,
            "delivery_dinein_list": delivery_dinein_list,
            "delivery_dinein_completed_list": delivery_dinein_completed_list,
            "today_datetime": datetime_str,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }

    if action == "table_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code= '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        context = {
            "action": action,
            "table_dinein_list": table_dinein_list,
            "currency": currency,
        }

    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductCategory_Count")
        product_category_list = cursor.fetchall()

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }
    if "view_" in action:
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        code_key = action.replace("view_", "")
        cursor.execute("select * from V_ProductCategory_List where code_key = '"+code_key+"'")
        product_category_list = cursor.fetchall()
        cursor.execute("select * from tblCodeDetail where code_key = '"+code_key+"' and shop_code = '"+shop_code+"' and code_id = 2")
        product_category = cursor.fetchall()

        if product_category_list:
            product_category_name = product_category_list[0].code_detail_name
        else:
            if product_category:
                product_category_name = product_category[0].code_detail_name
            else:
                product_category_name = ""
        product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "product_status_list": product_status_list,
            "product_category_name": product_category_name,
            "user_shop_code": shop_code,
            "user_category": code_key,
            "user_display": display,
            "currency": currency,
        }
    return render(request, "pos_template/deliveryCall_response.html", context)

def deliveryCall_vertical(request):
    #if not request.session.get('username'): return redirect('login')
    shop_code = request.POST.get('shop_code')
    shop_code = "fortunetea"
    if shop_code == "" or shop_code is None:
        shop_code = request.session.get('team')

    shop_list = Shops.objects.using('zenpos').filter(status=1)
    if shop_list and shop_code == "admin":
        shop_code = shop_list[0].shop_code

    product_category_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=2, status=1)
    unit_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=9, status=1)
    dim_sum_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=7, status=1)
    period_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=1, status=1)
    product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)
    taste_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=11, status=1)
    printer_list = Printer.objects.using('zenpos').filter(status=1)
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
    table_dinein_list = cursor.fetchall()
    today = datetime.datetime.now()

    #accessid = 45
    #request.session['accessid'] = accessid
    #cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
    #cursor_menu = cnxn_menu.cursor()
    #cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    #menuItem = cursor_menu.fetchall()
    #cursor_menu.execute("select * from V_UserAccessRight where username = '"+str(request.session.get('username'))+"'")
    #menuList = cursor_menu.fetchall()
    #users = Users.objects.using('zensystem').get(username=request.session.get('username'),isactive=1)
    #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #users.save(using='zensystem')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        #"user_loginid": loginid,
        "user_shop": shop_code,
        "product_category_list": product_category_list,
        "unit_list": unit_list,
        "taste_list": taste_list,
        "dim_sum_list": dim_sum_list,
        "period_list": period_list,
        "product_status_list": product_status_list,
        "printer_list": printer_list,
        "table_dinein_list": table_dinein_list,
        "shop_list": shop_list,
    }
    return render(request, "pos_template/deliveryCall_vertical.html", context)

@csrf_exempt
def deliveryCall_response_vertical(request):
    #if not request.session.get('username'): return HttpResponseRedirect('/login')
    action = request.POST.get('action')
    shop_code = request.POST.get('shop_code')
    display = request.POST.get('display')
    today = datetime.datetime.now()
    code_id = "2"
    if request.session.get('show_currency') == "0":
        currency = "$"
    else:
        currency = "MOP"

    if action == "menutab":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        dishes_list = cursor.fetchall()

        context = {
            "action": action,
            "dishes_list": dishes_list,
            "sql": sql,
            "user_shop_code": shop_code,
            "user_display": display,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '"+shop_code+"', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "order_selection":
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M")
        date_str = datetime_dt.strftime("%Y-%m-%d")

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_TakeawayDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' order by order_date desc")
        takeaway_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_TakeawayDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' and datediff(minute, kitchen_date, GETDATE()) < 5 order by order_date desc")
        takeaway_dinein_completed_list = cursor.fetchall()
        cursor.execute("select * from V_DeliveryDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' order by order_date desc")
        delivery_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_DeliveryDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' and datediff(minute, kitchen_date, GETDATE()) < 5 order by order_date desc")
        delivery_dinein_completed_list = cursor.fetchall()
        order_type_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=10, status=1).order_by('sequence')
        table_list = Tables.objects.using('zenpos').filter(shop_code=shop_code, status=1)

        context = {
            "action": action,
            "order_type_list": order_type_list,
            "table_dinein_list": table_dinein_list,
            "takeaway_dinein_list": takeaway_dinein_list,
            "takeaway_dinein_completed_list": takeaway_dinein_completed_list,
            "delivery_dinein_list": delivery_dinein_list,
            "delivery_dinein_completed_list": delivery_dinein_completed_list,
            "today_datetime": datetime_str,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }

    if action == "table_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code= '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        context = {
            "action": action,
            "table_dinein_list": table_dinein_list,
            "currency": currency,
        }

    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductCategory_Count")
        product_category_list = cursor.fetchall()

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }
    if "view_" in action:
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        code_key = action.replace("view_", "")
        cursor.execute("select * from V_ProductCategory_List where code_key = '"+code_key+"'")
        product_category_list = cursor.fetchall()
        cursor.execute("select * from tblCodeDetail where code_key = '"+code_key+"' and shop_code = '"+shop_code+"' and code_id = 2")
        product_category = cursor.fetchall()

        if product_category_list:
            product_category_name = product_category_list[0].code_detail_name
        else:
            if product_category:
                product_category_name = product_category[0].code_detail_name
            else:
                product_category_name = ""
        product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "product_status_list": product_status_list,
            "product_category_name": product_category_name,
            "user_shop_code": shop_code,
            "user_category": code_key,
            "user_display": display,
            "currency": currency,
        }
    return render(request, "pos_template/deliveryCall_response_vertical.html", context)

def kitchenDisplay(request):
    if not request.session.get('username'): return HttpResponseRedirect('/login')
    shop_code = request.POST.get('shop_code')
    if shop_code == "" or shop_code is None:
        shop_code = request.session.get('team')

    shop_list = Shops.objects.using('zenpos').filter(status=1)
    if shop_list and shop_code == "admin":
        shop_code = shop_list[0].shop_code

    product_category_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=2, status=1)
    unit_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=9, status=1)
    dim_sum_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=7, status=1)
    period_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=1, status=1)
    product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)
    taste_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=11, status=1)
    printer_list = Printer.objects.using('zenpos').filter(status=1)
    cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
    table_dinein_list = cursor.fetchall()
    today = datetime.datetime.now()

    accessid = 45
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('zensystem').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='zensystem')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        #"user_loginid": loginid,
        "user_shop": shop_code,
        "product_category_list": product_category_list,
        "unit_list": unit_list,
        "taste_list": taste_list,
        "dim_sum_list": dim_sum_list,
        "period_list": period_list,
        "product_status_list": product_status_list,
        "printer_list": printer_list,
        "table_dinein_list": table_dinein_list,
        "shop_list": shop_list,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "today": today,
    }
    return render(request, "pos_template/kitchenDisplay.html", context)

@csrf_exempt
def kitchenDisplay_response(request):
    if not request.session.get('username'): return HttpResponseRedirect('/login')
    action = request.POST.get('action')
    shop_code = request.POST.get('shop_code')
    display = request.POST.get('display')
    today = datetime.datetime.now()
    code_id = "2"
    if request.session.get('show_currency') == "0":
        currency = "$"
    else:
        currency = "MOP"

    if action == "menutab":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        dishes_list = cursor.fetchall()

        context = {
            "action": action,
            "dishes_list": dishes_list,
            "sql": sql,
            "user_shop_code": shop_code,
            "user_display": display,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '"+shop_code+"', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "order_category":
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M")
        date_str = datetime_dt.strftime("%Y-%m-%d")

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_TakeawayDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' and status = '3' order by order_date desc")
        takeaway_dinein_list = cursor.fetchall()
        for u in takeaway_dinein_list:
            cursor.execute("select * from V_OrderItem_List where order_id= '" + str(u.order_id) + "'")
            u.order_item_list = cursor.fetchall()
            for x in u.order_item_list:
                cursor.execute("select * from V_OrderItemDetail_List where order_item_id= '" + str(x.order_item_id) + "'")
                u.order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_DeliveryDinein_List where shop_code= '"+shop_code+"' and order_date >= '"+date_str+"' and status = '3' order by order_date desc")
        delivery_dinein_list = cursor.fetchall()
        for u in delivery_dinein_list:
            cursor.execute("select * from V_OrderItem_List where order_id= '" + str(u.order_id) + "'")
            u.order_item_list = cursor.fetchall()
            for x in u.order_item_list:
                cursor.execute("select * from V_OrderItemDetail_List where order_item_id= '" + str(x.order_item_id) + "'")
                u.order_item_detail_list = cursor.fetchall()

        order_type_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=10, status=1).order_by('sequence')
        table_list = Tables.objects.using('zenpos').filter(shop_code=shop_code, status=1)

        context = {
            "action": action,
            "order_type_list": order_type_list,
            "table_dinein_list": table_dinein_list,
            "takeaway_dinein_list": takeaway_dinein_list,
            "delivery_dinein_list": delivery_dinein_list,
            "today_datetime": datetime_str,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }

    if action == "table_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code= '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        context = {
            "action": action,
            "table_dinein_list": table_dinein_list,
            "currency": currency,
        }

    if action == 'event_list':
        SelectDate = request.POST.get('selectdate', None)
        StartDate = request.POST.get('startdate', None)
        EndDate = request.POST.get('enddate', None)
        SelectTeam = request.POST.get('team', None)
        SelectRoom = request.POST.get('room', None)
        if (SelectTeam == 'None'): SelectTeam = ''
        if (SelectRoom == 'None'): SelectRoom = ''

        StartDate = datetime.date(int(StartDate[0:4]), int(StartDate[5:7]), int(StartDate[8:10]))
        EndDate = datetime.date(int(EndDate[0:4]), int(EndDate[5:7]), int(EndDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(start_date=SelectDate).order_by('start_date')
        RoomList = Rooms.objects.using('zensystem').filter(isactive=1)
        TimeList = Times.objects.using('zensystem').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','"+ SelectTeam + "','"+ SelectRoom + "', '1'")
        eventlist = cursor.fetchall()

        #EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')
        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
            "currency": currency,
        }

    if action == 'select_order':
        SelectDate = request.POST.get('selectdate', None)
        StartDate = request.POST.get('startdate', None)
        EndDate = request.POST.get('enddate', None)
        SelectTeam = request.POST.get('team', None)
        SelectRoom = request.POST.get('room', None)
        if (SelectTeam == 'None'): SelectTeam = ''
        if (SelectRoom == 'None'): SelectRoom = ''

        StartDate = datetime.date(int(StartDate[0:4]), int(StartDate[5:7]), int(StartDate[8:10]))
        EndDate = datetime.date(int(EndDate[0:4]), int(EndDate[5:7]), int(EndDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(
            start_date=SelectDate).order_by('start_date')
        RoomList = Rooms.objects.using('zensystem').filter(isactive=1)
        TimeList = Times.objects.using('zensystem').filter(isactive=1)

        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '" + StartDate.strftime('%Y-%m-%d') + "','" + EndDate.strftime(
            '%Y-%m-%d') + "','" + SelectTeam + "','" + SelectRoom + "', '1'")
        eventlist = cursor.fetchall()

        # EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')
        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
            "currency": currency,
        }
    if action == 'order_item_list':
        order_id = request.POST.get('order_id')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        if order_cost_list:
            order_total_quantity_cart = order_cost_list[0].total_quantity_cart
            order_total_quantity_order = order_cost_list[0].total_quantity_order
            order_total_quantity = order_cost_list[0].total_quantity
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = order_cost_list[0].total_cost_order
            order_total_cost = order_cost_list[0].total_cost
        else:
            order_total_quantity_cart = 0
            order_total_quantity_order = 0
            order_total_quantity = 0
            order_total_cost_cart = 0
            order_total_cost_order = 0
            order_total_cost = 0

        context = {
            "action": action,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_quantity_cart": order_total_quantity_cart,
            "order_total_quantity_order": order_total_quantity_order,
            "order_total_quantity": order_total_quantity,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost": order_total_cost,
            "order_item_detail_list": order_item_detail_list,
            "currency": currency,
        }
    if action == 'order_operation':
        order_id = request.POST.get('order_id')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        if order_cost_list:
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = order_cost_list[0].total_cost_order
            order_total_cost = order_cost_list[0].total_cost

        context = {
            "action": action,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost": order_total_cost,
            "currency": currency,
        }
    if action == 'order_cart_list':
        order_id = request.POST.get('order_id')
        display_type = request.POST.get('type')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        if order_cost_list:
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = order_cost_list[0].total_cost_order
            order_total_cost = order_cost_list[0].total_cost
        taste_list = CodeDetails.objects.using('zenpos').filter(shop_code="east", code_id=11, status=1)

        context = {
            "action": action,
            "display_type": display_type,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost": order_total_cost,
            "order_item_detail_list": order_item_detail_list,
            "taste_list": taste_list,
            "currency": currency,
        }

    if action == "product_extra_list":
        product_id = request.POST.get('product_id')
        type = request.POST.get('type')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductDetail_Group where product_id = "+product_id)
        product_detail_group = cursor.fetchall()
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductDetail_Item where product_id = "+product_id)
        product_detail_item = cursor.fetchall()
        context = {
            "action": action,
            "product_detail_group": product_detail_group,
            "product_detail_item": product_detail_item,
            "currency": currency,
        }

    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductCategory_Count")
        product_category_list = cursor.fetchall()

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
        }
    if "view_" in action:
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        code_key = action.replace("view_", "")
        cursor.execute("select * from V_ProductCategory_List where code_key = '"+code_key+"'")
        product_category_list = cursor.fetchall()
        cursor.execute("select * from tblCodeDetail where code_key = '"+code_key+"' and shop_code = '"+shop_code+"' and code_id = 2")
        product_category = cursor.fetchall()

        if product_category_list:
            product_category_name = product_category_list[0].code_detail_name
        else:
            if product_category:
                product_category_name = product_category[0].code_detail_name
            else:
                product_category_name = ""
        product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "product_status_list": product_status_list,
            "product_category_name": product_category_name,
            "user_shop_code": shop_code,
            "user_category": code_key,
            "user_display": display,
            "currency": currency,
        }

    if action == "product_search":
        product_code = request.POST.get('product_code')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        sql = "select * from V_ProductCategory_List where product_code = N'"+str(product_code)+"' or product_code = N'"+str(product_code)+"'"
        #cursor.execute("select * from V_ProductCategory_List where product_code like N'%"+str(product_code)+"%' or bar_code like N'"+str(product_code)+"' or product_name like N'%"+str(product_code)+"%'")
        cursor.execute(sql)
        #cursor.execute("select * from V_ProductCategory_List where product_code like N'%"+str(product_code)+"%'")
        product_category_list = cursor.fetchall()

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "user_shop_code": shop_code,
            "user_display": display,
            "currency": currency,
            "sql": sql,
        }

    if action == "add_dinein":
        username = request.POST.get('username')
        booking_id = request.POST.get('booking_id')
        member_id = request.POST.get('member_id')
        order_id = request.POST.get('order_id')
        member_number = request.POST.get('member_number')
        number_guests = request.POST.get('number_guests')
        table_key = request.POST.get('table_key')
        shop_code = request.POST.get('shop_code')

        order_type = request.POST.get('order_type')

        try:
            if action == "add_dinein" or action == "confirm_guest":
                dinein = DineIns()
            else:
                dinein = DineIns.objects.using('zenpos').get(dinein_id=dinein_id)

            # Add other data fields
            try:
                table = Tables.objects.using('zenpos').filter(table_key=table_key)
                dinein.table_id = table[0].table_id
            except:
                dinein.table_id = 0
            table_id = dinein.table_id
            try:
                member = Members.objects.using('zenpos').filter(member_number=member_number)
                dinein.member_id = member[0].member_id
            except:
                dinein.member_id = 0
            member_id = dinein.member_id
            try:
                order = Orders()
                order.member_id = member_id
                order.order_number = getOrderNumber()
                order.order_type = order_type
                order.order_date = today
                if shop_code == "east":
                    order.service_charge = 10
                    order.tea_charge = 10
                    order.other_charge = 20
                    order.special_discount = 0
                else:
                    order.service_charge = 0
                    order.tea_charge = 0
                    order.other_charge = 0
                    order.special_discount = 0
                order.loginid = request.session.get('loginid')
                order.save(using='zenpos')
                #dinein.order_id = Orders.objects.using('zenpos').aggregate(Max('order_id'))['order_id__max'] + 1
                dinein.order_id = order.order_id
                dinein.order_number = order.order_number
                order_id = order.order_id
            except:
                dinein.order_id = 0

            dinein.booking_id = booking_id
            dinein.shop_code = shop_code
            dinein.number_guests = number_guests
            dinein.table_key = table_key
            dinein.member_number = member_number
            dinein.in_date = today
            dinein.status = 1
            dinein.loginid = request.session.get('loginid')
            dinein.save(using='zenpos')

            if int(booking_id) > 0:
                booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
                booking.show_status = 1
                booking.loginid = request.session.get('loginid')
                booking.save(using='zenpos')

        except Exception as e:
            return JsonResponse({'message': 'Update record failed1. Error: {}'.format(e)}, status=500)
        return HttpResponse(order_id)

    if action == "add_takeaway":
        username = request.POST.get('username')
        booking_id = request.POST.get('booking_id')
        member_id = request.POST.get('member_id')
        order_id = request.POST.get('order_id')
        member_number = request.POST.get('member_number')
        number_guests = request.POST.get('number_guests')
        table_key = "T888"
        shop_code = request.POST.get('shop_code')

        order_type = request.POST.get('order_type')

        try:
            if action == "add_takeaway":
                dinein = DineIns()
            else:
                dinein = DineIns.objects.using('zenpos').get(dinein_id=dinein_id)

            # Add other data fields
            try:
                table = Tables.objects.using('zenpos').filter(table_key=table_key)
                dinein.table_id = table[0].table_id
            except:
                dinein.table_id = 0
            table_id = dinein.table_id
            try:
                member = Members.objects.using('zenpos').filter(member_number=member_number)
                dinein.member_id = member[0].member_id
            except:
                dinein.member_id = 0
            member_id = dinein.member_id
            try:
                order = Orders()
                order.member_id = member_id
                order.order_number = getOrderNumber()
                order.order_type = order_type
                order.order_date = today

                order.service_charge = 0
                order.tea_charge = 0
                order.other_charge = 0
                order.special_discount = 0
                order.loginid = request.session.get('loginid')
                order.save(using='zenpos')
                #dinein.order_id = Orders.objects.using('zenpos').aggregate(Max('order_id'))['order_id__max'] + 1
                dinein.order_id = order.order_id
                dinein.order_number = order.order_number
            except:
                dinein.order_id = 0

            dinein.booking_id = booking_id
            dinein.shop_code = shop_code
            dinein.number_guests = number_guests
            dinein.table_key = "T"+dinein.order_number
            dinein.member_number = member_number
            dinein.in_date = today
            dinein.status = 1
            dinein.loginid = request.session.get('loginid')
            dinein.save(using='zenpos')

            if int(booking_id) > 0:
                booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
                booking.show_status = 1
                booking.loginid = request.session.get('loginid')
                booking.save(using='zenpos')

        except Exception as e:
            return JsonResponse({'message': 'Update record failed1. Error: {}'.format(e)}, status=500)
        return HttpResponse(dinein.order_id)

    if action == "update_order_setting":
        order_id = request.POST.get('order_id')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        order_item_type = request.POST.get('order_item_type')
        order_sequence = 0
        status = 0
        order_number = request.POST.get('order_number')
        product_name = request.POST.get('product_name')
        product_name_e = request.POST.get('product_name_e')
        selling_price = request.POST.get('selling_price')
        product_description = request.POST.get('product_description')

        try:
            if Orders.objects.using('zenpos').filter(order_id=order_id).exists():
                order = Orders.objects.using('zenpos').get(order_id=order_id)
                if "服務費" in product_name:
                    order.service_charge = selling_price
                if "茶位" in product_name:
                    order.tea_charge = selling_price
                if "醬介" in product_name:
                    order.other_charge = selling_price
                if "經理" in product_name:
                    order.special_discount = selling_price
                order.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "add_item":
        shop_code = request.POST.get('shop_code')
        order_id = request.POST.get('order_id')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        order_item_type = request.POST.get('order_item_type')
        order_sequence = 0
        status = 0
        order_number = request.POST.get('order_number')
        product_name = request.POST.get('product_name')
        product_name_e = request.POST.get('product_name_e')
        selling_price = request.POST.get('selling_price')
        product_description = request.POST.get('product_description')
        add_taste = request.POST.get('add_taste')

        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id,product_id=product_id,status=0).exists():
                orderitem = OrderItems.objects.using('zenpos').get(order_id=order_id, product_id=product_id, status=0)
                orderitem.quantity = int(orderitem.quantity) + int(quantity)
            else:
                orderitem = OrderItems()
                orderitem.quantity = quantity

            orderitem.order_id = order_id
            orderitem.product_id = product_id
            orderitem.product_sale_type = 'S'
            orderitem.order_item_date = order_item_date
            orderitem.order_item_type = order_item_type
            orderitem.order_sequence = order_sequence
            orderitem.status = status
            orderitem.order_number = order_number
            orderitem.product_name = product_name
            orderitem.product_name_e = product_name_e
            orderitem.selling_price = selling_price
            orderitem.product_description = product_description
            orderitem.loginid = request.session.get('loginid')
            if orderitem.quantity == 0:
                orderitem.delete(using='zenpos')
            else:
                orderitem.save(using='zenpos')

            if add_taste != "":
                if OrderItemDetails.objects.using('zenpos').filter(order_item_id=orderitem.order_item_id).exists():
                    orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=orderitem.order_item_id)
                    orderitemdetail.delete()

                taste_add_list = add_taste[:-1].split(',')
                index = 0

                for taste_add_value in taste_add_list:
                    orderitemdetail = OrderItemDetails()
                    orderitemdetail.order_item_id = orderitem.order_item_id
                    orderitemdetail.item_id = index + 1
                    #taste_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_detail_id=taste_add_value, status=1)
                    productdetail = ProductDetails.objects.using('zenpos').filter(product_id=product_id, code_detail_id=taste_add_value, status=1)
                    if productdetail:
                        orderitemdetail.code_detail_id = productdetail[0].code_detail_id
                        orderitemdetail.code_detail_name = productdetail[0].product_detail_name
                        orderitemdetail.selling_price = productdetail[0].selling_price
                    orderitemdetail.status = 1
                    orderitemdetail.loginid = request.session.get('loginid')
                    orderitemdetail.save(using='zenpos')
                    index += 1

        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "add_cart":
        order_item_id = request.POST.get('order_item_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        order_item_type = request.POST.get('order_item_type')
        product_name = request.POST.get('product_name')
        selling_price = request.POST.get('selling_price')
        status = 0
        try:
            if OrderItems.objects.using('zenpos').filter(order_item_id=order_item_id).exists():
                orderitem = OrderItems.objects.using('zenpos').get(order_item_id=order_item_id)
                orderitem.order_item_type = order_item_type
                orderitem.quantity = int(orderitem.quantity) + int(quantity)
                orderitem.selling_price = selling_price
                orderitem.order_item_date = order_item_date
                orderitem.loginid = request.session.get('loginid')
            if orderitem.quantity == 0:
                orderitem.delete(using='zenpos')
            else:
                orderitem.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "add_taste":
        order_item_id = request.POST.get('order_item_id')
        item_taste = str(request.POST.get('item_taste'))
        item_taste_array = item_taste.split(",")
        status = request.POST.get('status')
        quantity = request.POST.get('quantity')

        try:
            if action == "add_taste":
                orderitemdetail = OrderItemDetails()
            else:
                orderitemdetail = OrderItemDetails.objects.using('zenpos').get(order_item_id=order_item_id)
            for w in item_taste_array:
                orderitemdetail.order_item_id = order_item_id
                orderitemdetail.item_id = 1
                orderitemdetail.code_key = w
                orderitemdetail.code_detail_name = w
                orderitemdetail.status = status
                orderitemdetail.loginid = request.session.get('loginid')
                if quantity == 0:
                    orderitemdetail.delete(using='zenpos')
                else:
                    orderitemdetail.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "remove_taste":
        order_item_id = request.POST.get('order_item_id')
        try:
            orderitemdetail = OrderItemDetails.objects.using('zenpos').filter(order_item_id=order_item_id)
            orderitemdetail.delete()
        except Exception as e:
            return JsonResponse({'message': 'aaUpdate record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "password_checking":
        password_approval = request.POST.get('password_approval')
        try:
            hashed_password = hash_password(password_approval)
            users = Users.objects.using('zensystem').filter(team=request.session.get('team')).filter(password=hashed_password).filter(isactive=1)
            if users:
                return HttpResponse('Checking Success')
            else:
                return HttpResponse('Checking Fail')

        except Exception as e:
            return JsonResponse({'message': 'Checking record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Checking Success')

    if action == "settle_kitchen":
        order_id = request.POST.get('order_id')
        kitchen_date = today
        status = 1
        try:
            if Orders.objects.using('zenpos').filter(order_id=order_id).exists():
                order = Orders.objects.using('zenpos').get(order_id=order_id,kitchen_status=0)
                order.kitchen_date = kitchen_date
                order.kitchen_status = status
                order.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "back_to_cart":
        order_id = request.POST.get('order_id')
        try:
            #if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
            #    dinein = DineIns.objects.using('zenpos').get(order_id=order_id,status=2)
            #    dinein.update(status=1)

            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=1)
                orderitem.update(status=0)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "reset_cart":
        order_id = request.POST.get('order_id')
        order_item_date = today
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=0)
                orderitem.delete()
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')
    return render(request, "pos_template/kitchenDisplay_response.html", context)

def booking(request):
    if not request.session.get('username'): return redirect('login')
    today = date.today()
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d")

    TeamList = Teams.objects.using('zensystem').exclude(teamdesc="admin").order_by('sequence')
    VenueList = []
    RoomList = Tables.objects.using('zenpos').filter(status=1)
    TimeList = Times.objects.using('zenpos').filter(isactive=1)

    PostList = Users.objects.using('zensystem').filter(team="east")

    SelectTeam = "east"

    accessid = 21
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('zensystem').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='zensystem')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "today": datetime_str,      
        "venuelist": VenueList,
        "teamlist": TeamList,
        "postlist": PostList,
        "roomlist": RoomList,
        "timelist": TimeList,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "user_selectteam": SelectTeam,
    }

    return render(request, "pos_template/booking.html", context)

@csrf_exempt
def booking_response(request, year='None'):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    SelectDate = request.POST.get('selectdate', None)
    StartDate = request.POST.get('startdate', None)
    EndDate = request.POST.get('enddate', None)
    SelectTeam = request.POST.get('team', None)
    SelectRoom = request.POST.get('room', None)
    if (SelectTeam == 'None'): SelectTeam = ''
    if (SelectRoom == 'None'): SelectRoom = ''
    IsActive = '1'

    if action == 'event_list':
        StartDate = datetime.date(int(StartDate[0:4]), int(StartDate[5:7]), int(StartDate[8:10]))
        EndDate = datetime.date(int(EndDate[0:4]), int(EndDate[5:7]), int(EndDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(start_date=SelectDate).order_by('start_date')
        RoomList = Tables.objects.using('zensystem').filter(status=IsActive).filter(shop_code=SelectTeam)
        TimeList = Times.objects.using('zensystem').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','"+ SelectTeam + "','"+ SelectRoom + "', '" + IsActive + "'")
        eventlist = cursor.fetchall()

        #EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')
        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,            
            "enddate": EndDate,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
        }
    if action == 'calendar_table_list':
        today = datetime.datetime.now()
        #StartDate = SelectDate[0:4]+'-'+SelectDate[5:7]+'-01'
        #EndDate = SelectDate[0:4]+'-'+SelectDate[5:7]+'-30'
        StartDate = datetime.date(int(SelectDate[0:4]), int(SelectDate[5:7]), int("01"))
        EndDate = datetime.date(int(SelectDate[0:4]), int(SelectDate[5:7]), int(calendar.monthrange(StartDate.year, StartDate.month)[1]))
        if SelectTeam != "":
            RoomList = Tables.objects.using('zenpos').filter(status=IsActive).filter(shop_code=SelectTeam)
        else:
            RoomList = Tables.objects.using('zenpos').filter(status=IsActive)
        TimeList = Times.objects.using('zenpos').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '" + SelectTeam + "','1'")
        team_list = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','"+ SelectTeam + "','"+ SelectRoom + "', '" + IsActive + "'")
        EventList = cursor.fetchall()
        #EventList = []
        #EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')[:100]
        Holidays = Holiday.objects.using('zensystem').filter(holidaydate__gte=StartDate).filter(holidaydate__lte=EndDate).order_by('holidaydate')
        HolidayList = []
        for holiday in Holidays:
            HolidayList.append(holiday.holidaydate.strftime('%Y-%m-%d'))
        DateRangeList = [StartDate + timedelta(days=x) for x in range((EndDate - StartDate).days + 1)]

        context = {
            "action": action,
            "eventlist": EventList,
            "holidaylist": HolidayList,
            "daterangelist": DateRangeList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "today": today,
            "range": range(2),
            "num_of_days": range(30),
            "team_list": team_list,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
        }
    if action == 'calendar_list':
        today = datetime.datetime.now()
        #StartDate = SelectDate[0:4]+'-'+SelectDate[5:7]+'-01'
        #EndDate = SelectDate[0:4]+'-'+SelectDate[5:7]+'-30'
        StartDate = datetime.date(int(SelectDate[0:4]), int(SelectDate[5:7]), int("01"))
        EndDate = datetime.date(int(SelectDate[0:4]), int(SelectDate[5:7]), int(calendar.monthrange(StartDate.year, StartDate.month)[1]))
        RoomList = Tables.objects.using('zenpos').filter(status=IsActive).filter(shop_code=SelectTeam)
        TimeList = Times.objects.using('zenpos').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '" + SelectTeam + "','1'")
        team_list = cursor.fetchall()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        #cursor.execute("exec spQABookingList '" + str(year) + "','"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','','"+ SelectRoom + "', '" + IsActive + "'")
        #EventList = cursor.fetchall()
        EventList = []
        #EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')[:100]
        Holidays = Holiday.objects.using('zensystem').filter(holidaydate__gte=StartDate).filter(holidaydate__lte=EndDate).order_by('holidaydate')
        HolidayList = []
        for holiday in Holidays:
            HolidayList.append(holiday.holidaydate.strftime('%Y-%m-%d'))
        DateRangeList = [StartDate + timedelta(days=x) for x in range((EndDate - StartDate).days + 1)]

        context = {
            "action": action,
            "eventlist": EventList,
            "holidaylist": HolidayList,
            "daterangelist": DateRangeList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "today": today,
            "range": range(2),
            "num_of_days": range(30),
            "team_list": team_list,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
        }
    if action == 'booking_list':
        StartDate = datetime.date(int(SelectDate[0:4]), int(SelectDate[5:7]), int(SelectDate[8:10]))
        EndDate = datetime.date(int(SelectDate[0:4]), int(SelectDate[5:7]), int(SelectDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(start_date=SelectDate).order_by('-time')
        TimeList = Times.objects.using('zenpos').filter(status=IsActive).filter(shop_code=SelectTeam)
        RoomList = Rooms.objects.using('zenpos').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        #cursor.execute("exec spBookingList '2024-04-01','2024-04-01','','V1', '1'")
        cursor.execute("exec spBookingList '"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','','"+ SelectRoom + "', '" + IsActive + "'")
        sql = "exec spBookingList '"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','','"+ SelectRoom + "', '" + IsActive + "'"
        eventlist = cursor.fetchall()

        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "timelist": TimeList,
            "roomlist": RoomList,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
            "sql": sql,
        }
    if action == 'latest_list':
        today = datetime.datetime.now()

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingLatestList '"+ today.strftime('%Y-%m-%d') + "','"+ SelectTeam + "','"+ SelectRoom + "', '" + IsActive + "'")
        eventlist = cursor.fetchall()[0:20]

        context = {
            "action": action,
            "eventlist": eventlist,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
        }
    return render(request, "pos_template/booking_response.html", context)

@csrf_exempt
def booking_save(request):
    if not request.session.get('username'): return redirect('login')
    booking_id = request.POST.get('booking_id')
    shop_code = str(request.POST.get('shop_code'))
    action = str(request.POST.get('action'))
    table_key = request.POST.get('table_key')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    booking_time = request.POST.get('booking_time')
    if booking_time < "1800":
        time = "1100"
    else:
        time = "1800"
    number_guests = request.POST.get('number_guests')
    member_number = request.POST.get('member_number')
    customer_name = request.POST.get('customer_name')
    gender = request.POST.get('gender')
    phone_area_code = request.POST.get('phone_area_code')
    phone_number = request.POST.get('phone_number')
    type = request.POST.get('type')
    remarks = request.POST.get('remarks')
    username = request.POST.get('username')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    try:
        if action == "add":
            booking = Bookings()
            booking.booking_status = 1
            booking.deposit_status = 0
            booking.confirm_status = 0
            booking.show_status = 0
            booking.createdate = datetime_str
            booking.modifydate = datetime_str
        else:
            booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
            booking.modifydate = datetime_str
        booking.shop_code = shop_code
        booking.table_key = table_key
        booking.start_date = start_date + " " + booking_time[:2] + ":" + booking_time[-2:] + ":00"
        booking.end_date = end_date + " 23:59:59"
        booking.time = time
        booking.booking_time = booking_time
        booking.number_guests = number_guests
        booking.member_number = member_number
        booking.customer_name = customer_name
        booking.gender = gender
        booking.phone_area_code = phone_area_code
        booking.phone_number = phone_number
        booking.type = type
        booking.remarks = remarks
        booking.username = username
        booking.loginid = request.session.get('loginid')
        if action == "add": booking.createdate = datetime_str
        if action == "add" or action == "edit": booking.save(using='zenpos')
        if action == "delete": booking.delete()
        shop_code = "east"
        memberAddStatus = memberAdd(member_number, customer_name, gender, phone_area_code, phone_number, shop_code)
        messages.success(request, "New room booking was created successfully.")
        return HttpResponse("True" + action + memberAddStatus)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

def payment(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')
    shop_code = request.session.get('shop_code')
    if shop_code == "admin": shop_code = "east"

    shop_list = Shops.objects.using('zenpos').filter(status=1)
    product_category_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=2, status=1)
    unit_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=9, status=1)
    dim_sum_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=7, status=1)
    period_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=1, status=1)
    product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)
    printer_list = Printer.objects.using('zenpos').filter(status=1)
    payment_method_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=6, status=1)

    accessid = 22
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('zensystem').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='zensystem')
    pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_shop_code": shop_code,
        "product_category_list": product_category_list,
        "unit_list": unit_list,
        "dim_sum_list": dim_sum_list,
        "period_list": period_list,
        "product_status_list": product_status_list,
        "printer_list": printer_list,
        "payment_method_list": payment_method_list,
        "shop_list": shop_list,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
    }
    return render(request, "pos_template/payment.html", context)

@csrf_exempt
def payment_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    shop_code = request.POST.get('shop_code')
    if shop_code == "admin": shop_code = "east"
    display = request.POST.get('display')
    today = datetime.datetime.now()
    code_id = "2"

    if action == "menutab":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1")
        sql = "select * from tblCodeDetail where (1 = case when '"+shop_code+"' = '' then 1 when shop_code = '"+shop_code+"' then 1 else 0 end) and (1 = case when '"+code_id+"' = '' then 1 when code_id = '"+code_id+"' then 1 else 0 end) and status = 1"
        dishes_list = cursor.fetchall()

        context = {
            "action": action,
            "dishes_list": dishes_list,
            "sql": sql,
            "user_display": display,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '"+shop_code+"', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "order_selection":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_TableDinein_List where shop_code = '"+shop_code+"'")
        table_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_TakeawayDinein_List where shop_code= '"+shop_code+"'")
        takeaway_dinein_list = cursor.fetchall()
        order_type_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=10, status=1).order_by('sequence')
        table_list = Tables.objects.using('zenpos').filter(shop_code=shop_code, status=1)
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M")
        time_str = datetime_dt.strftime("%H:%M")

        context = {
            "action": action,
            "order_type_list": order_type_list,
            "table_dinein_list": table_dinein_list,
            "takeaway_dinein_list": takeaway_dinein_list,
            "today_datetime": datetime_str,
            "today_time": time_str,
            "user_shop_code": team,
            "user_display": display,
        }

    if action == 'event_list':
        SelectDate = request.POST.get('selectdate', None)
        StartDate = request.POST.get('startdate', None)
        EndDate = request.POST.get('enddate', None)
        SelectTeam = request.POST.get('team', None)
        SelectRoom = request.POST.get('room', None)
        if (SelectTeam == 'None'): SelectTeam = ''
        if (SelectRoom == 'None'): SelectRoom = ''

        StartDate = datetime.date(int(StartDate[0:4]), int(StartDate[5:7]), int(StartDate[8:10]))
        EndDate = datetime.date(int(EndDate[0:4]), int(EndDate[5:7]), int(EndDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(start_date=SelectDate).order_by('start_date')
        RoomList = Rooms.objects.using('zensystem').filter(isactive=1)
        TimeList = Times.objects.using('zensystem').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '"+ StartDate.strftime('%Y-%m-%d') + "','"+ EndDate.strftime('%Y-%m-%d') + "','"+ SelectTeam + "','"+ SelectRoom + "', '1'")
        eventlist = cursor.fetchall()

        #EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')
        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
        }

    if action == 'select_order':
        SelectDate = request.POST.get('selectdate', None)
        StartDate = request.POST.get('startdate', None)
        EndDate = request.POST.get('enddate', None)
        SelectTeam = request.POST.get('team', None)
        SelectRoom = request.POST.get('room', None)
        if (SelectTeam == 'None'): SelectTeam = ''
        if (SelectRoom == 'None'): SelectRoom = ''

        StartDate = datetime.date(int(StartDate[0:4]), int(StartDate[5:7]), int(StartDate[8:10]))
        EndDate = datetime.date(int(EndDate[0:4]), int(EndDate[5:7]), int(EndDate[8:10]))
        BookingList = Bookings.objects.using('zenpos').filter(table_key=SelectRoom).filter(
            start_date=SelectDate).order_by('start_date')
        RoomList = Rooms.objects.using('zensystem').filter(isactive=1)
        TimeList = Times.objects.using('zensystem').filter(isactive=1)

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spBookingList '" + StartDate.strftime('%Y-%m-%d') + "','" + EndDate.strftime('%Y-%m-%d') + "','" + SelectTeam + "','" + SelectRoom + "', '1'")
        eventlist = cursor.fetchall()

        # EventList = Officers.objects.using('officeadmin').filter(start_date__gte=StartDate).filter(end_date__lte=EndDate).order_by('start_date')
        context = {
            "action": action,
            "eventlist": eventlist,
            "bookinglist": BookingList,
            "roomlist": RoomList,
            "timelist": TimeList,
            "startdate": StartDate,
            "enddate": EndDate,
            "user_shop_code": SelectTeam,
            "user_room": SelectRoom,
        }
    if action == 'order_item_list':
        order_id = request.POST.get('order_id')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        if order_cost_list:
            order_type = order_dinein_list[0].order_type
            number_guests = order_dinein_list[0].number_guests
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            if order_cost_list[0].total_cost_order != "NULL":
                order_total_cost_order = int(order_cost_list[0].total_cost_order)
            else:
                order_total_cost_order = 0
            order_total_cost = order_cost_list[0].total_cost
            tea_charge = int(number_guests) * order_item_list[0].tea_charge
            other_charge = order_item_list[0].other_charge
            service_charge = (order_total_cost_order + tea_charge + other_charge) * (order_item_list[0].service_charge / 100)
            if order_type == "T":
                order_total_cost_final = order_total_cost_order
            else:
                order_total_cost_final = order_total_cost_order + tea_charge + service_charge
            special_discount = order_total_cost_final * (order_item_list[0].special_discount / 100)
            order_total_cost_final = order_total_cost_final * ((100 - order_item_list[0].special_discount) / 100)

        context = {
            "action": action,
            "order_type": order_type,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost": order_total_cost,
            "service_charge": service_charge,
            "tea_charge": tea_charge,
            "other_charge": other_charge,
            "special_discount": special_discount,
            "number_guests": number_guests,
            "order_total_cost_final": order_total_cost_final,
        }
    if action == 'order_operation':
        order_id = request.POST.get('order_id')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        if order_cost_list:
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = order_cost_list[0].total_cost_order
            order_total_cost = order_cost_list[0].total_cost

        context = {
            "action": action,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost": order_total_cost,
        }
    if action == 'order_cart_list':
        order_id = request.POST.get('order_id')
        display_type = request.POST.get('type')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        if order_cost_list:
            number_guests = order_dinein_list[0].number_guests
            order_type = order_dinein_list[0].order_type
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = int(order_cost_list[0].total_cost_order)
            order_total_cost = order_cost_list[0].total_cost
            tea_charge = int(number_guests) * order_item_list[0].tea_charge
            other_charge = order_item_list[0].other_charge
            service_charge = (order_total_cost_order + tea_charge + other_charge) * (order_item_list[0].service_charge / 100)
            if order_type == "T":
                order_total_cost_final = order_total_cost_order
            else:
                order_total_cost_final = order_total_cost_order + tea_charge + service_charge
            special_discount = order_total_cost_final * (order_item_list[0].special_discount / 100)
            order_total_cost_final = order_total_cost_final * ((100 - order_item_list[0].special_discount) / 100)
        payment_method_list = CodeDetails.objects.using('zenpos').filter(shop_code="east", code_id=6, status=1)

        context = {
            "action": action,
            "order_type": order_type,
            "display_type": display_type,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost": order_total_cost,
            "service_charge": service_charge,
            "tea_charge": tea_charge,
            "other_charge": other_charge,
            "special_discount": special_discount,
            "number_guests": number_guests,
            "order_total_cost_final": order_total_cost_final,
            "payment_method_list": payment_method_list,
        }
    if action == 'payment_cart_list':
        order_id = request.POST.get('order_id')
        display_type = request.POST.get('type')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("exec spOrderItemList " + order_id)
        order_item_list = cursor.fetchall()
        cursor.execute("exec spOrderDineinList " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        if order_cost_list:
            number_guests = order_dinein_list[0].number_guests
            order_type = order_dinein_list[0].order_type
            order_total_cost_cart = order_cost_list[0].total_cost_cart
            order_total_cost_order = int(order_cost_list[0].total_cost_order)
            order_total_cost = order_cost_list[0].total_cost
            tea_charge = int(number_guests) * order_item_list[0].tea_charge
            other_charge = order_item_list[0].other_charge
            service_charge = (order_total_cost_order + tea_charge + other_charge) * (order_item_list[0].service_charge / 100)
            if order_type == "T":
                order_total_cost_final = order_total_cost_order
            else:
                order_total_cost_final = order_total_cost_order + tea_charge + service_charge
            special_discount = order_total_cost_final * (order_item_list[0].special_discount / 100)
            order_total_cost_final = order_total_cost_final * ((100 - order_item_list[0].special_discount) / 100)
        payment_method_list = CodeDetails.objects.using('zenpos').filter(shop_code="east", code_id=6, status=1)

        context = {
            "action": action,
            "order_type": order_type,
            "display_type": display_type,
            "order_item_list": order_item_list,
            "order_dinein_list": order_dinein_list,
            "order_cost_list": order_cost_list,
            "order_total_cost_cart": order_total_cost_cart,
            "order_total_cost_order": order_total_cost_order,
            "order_total_cost": order_total_cost,
            "service_charge": service_charge,
            "tea_charge": tea_charge,
            "other_charge": other_charge,
            "special_discount": special_discount,
            "number_guests": number_guests,
            "order_total_cost_final": order_total_cost_final,
            "payment_method_list": payment_method_list,
        }
    if action == "overview":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_ProductCategory_Count")
        product_category_list = cursor.fetchall()

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "user_shop_code": team,
            "user_display": display,
        }
    if "view_" in action:
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        code_key = action.replace("view_", "")
        cursor.execute("select top 50 * from V_ProductCategory_List where code_key = '"+code_key+"'")
        product_category_list = cursor.fetchall()
        product_status_list = CodeDetails.objects.using('zenpos').filter(shop_code=shop_code, code_id=4, status=1)

        context = {
            "action": action,
            "product_category_list": product_category_list,
            "product_status_list": product_status_list,
            "product_category_name": product_category_list[0].code_detail_name,
            "user_shop_code": team,
            "user_display": display,
        }

    if action == "add_dinein":
        username = request.POST.get('username')
        booking_id = request.POST.get('booking_id')
        member_id = request.POST.get('member_id')
        order_id = request.POST.get('order_id')
        member_number = request.POST.get('member_number')
        number_guests = request.POST.get('number_guests')
        table_key = request.POST.get('table_key')
        shop_code = request.POST.get('shop_code')

        order_type = request.POST.get('order_type')

        try:
            if action == "add_dinein":
                dinein = DineIns()
            else:
                dinein = DineIns.objects.using('zenpos').get(dinein_id=dinein_id)

            # Add other data fields
            try:
                table = Tables.objects.using('zenpos').filter(table_key=table_key)
                dinein.table_id = table[0].table_id
            except:
                dinein.table_id = 0
            table_id = dinein.table_id
            try:
                member = Members.objects.using('zenpos').filter(member_number=member_number)
                dinein.member_id = member[0].member_id
            except:
                dinein.member_id = 0
            member_id = dinein.member_id
            try:
                order = Orders()
                order.member_id = member_id
                order.order_number = getOrderNumber()
                order.order_type = order_type
                order.order_date = today
                if shop_code == "east":
                    order.service_charge = 10
                    order.tea_charge = 10
                    order.other_charge = 20
                    order.special_discount = 0
                else:
                    order.service_charge = 0
                    order.tea_charge = 0
                    order.other_charge = 0
                    order.special_discount = 0
                order.save(using='zenpos')
                #dinein.order_id = Orders.objects.using('zenpos').aggregate(Max('order_id'))['order_id__max'] + 1
                dinein.order_id = order.order_id
                dinein.order_number = order.order_number
            except:
                dinein.order_id = 0

            dinein.booking_id = booking_id
            dinein.shop_code = shop_code
            dinein.number_guests = number_guests
            dinein.table_key = table_key
            dinein.member_number = member_number
            dinein.in_date = today
            dinein.status = 1
            dinein.save(using='zenpos')

            if int(booking_id) > 0:
                booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
                booking.show_status = 1
                booking.save(using='zenpos')

        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse(dinein.order_id)

    if action == "add_item":
        shop_code = request.POST.get('shop_code')
        order_id = request.POST.get('order_id')
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        status = 0
        order_number = request.POST.get('order_number')
        product_name = request.POST.get('product_name')
        product_name_e = request.POST.get('product_name_e')
        selling_price = request.POST.get('selling_price')
        product_description = request.POST.get('product_description')

        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id,product_id=product_id,status=0).exists():
                orderitem = OrderItems.objects.using('zenpos').get(order_id=order_id, product_id=product_id, status=0)
                orderitem.quantity = int(orderitem.quantity) + int(quantity)
            else:
                orderitem = OrderItems()
                orderitem.quantity = quantity

            orderitem.order_id = order_id
            orderitem.product_id = product_id
            orderitem.product_sale_type = 'S'
            orderitem.order_item_date = order_item_date
            orderitem.status = status
            orderitem.order_number = order_number
            orderitem.product_name = product_name
            orderitem.product_name_e = product_name_e
            orderitem.selling_price = selling_price
            orderitem.product_description = product_description
            if orderitem.quantity == 0:
                orderitem.delete(using='zenpos')
            else:
                orderitem.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "add_cart":
        order_item_id = request.POST.get('order_item_id')
        quantity = request.POST.get('quantity')
        order_item_date = today
        product_name = request.POST.get('product_name')
        selling_price = request.POST.get('selling_price')
        status = 0
        try:
            if OrderItems.objects.using('zenpos').filter(order_item_id=order_item_id).exists():
                orderitem = OrderItems.objects.using('zenpos').get(order_item_id=order_item_id)
                orderitem.quantity = int(orderitem.quantity) + int(quantity)
                orderitem.selling_price = selling_price
                orderitem.order_item_date = order_item_date
            if orderitem.quantity == 0:
                orderitem.delete(using='zenpos')
            else:
                orderitem.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "confirm_cart":
        order_id = request.POST.get('order_id')
        order_item_date = today
        status = 1
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                order_sequence_max = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=1).aggregate(Max('order_sequence'))['order_sequence__max'] + 1
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=0)
                orderitem.update(order_item_date=order_item_date, order_sequence=4, status=status)
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "confirm_cart_payment":
        order_id = request.POST.get('order_id')
        context = {
            "action": action,

        }

    if action == "reset_cart":
        order_id = request.POST.get('order_id')
        order_item_date = today
        try:
            if OrderItems.objects.using('zenpos').filter(order_id=order_id).exists():
                orderitem = OrderItems.objects.using('zenpos').filter(order_id=order_id,status=0)
                orderitem.delete()
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "settle_payment":
        order_id = request.POST.get('order_id')
        status = 3
        out_date = today
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")

        try:
            if DineIns.objects.using('zenpos').filter(order_id=order_id).exists():
                dinein = DineIns.objects.using('zenpos').get(order_id=order_id,status=2)
                order_number = dinein.order_number
                dinein = DineIns.objects.using('zenpos').filter(order_id=order_id,status=2)
                dinein.update(out_date=out_date, status=status)
        except Exception as e:
            return JsonResponse({'message': 'xxUpdate record failed. Error: {}'.format(e)}, status=500)

        shop_code = request.POST.get('shop_code')
        member_id = request.POST.get('member_id')
        booking_id = request.POST.get('booking_id')
        invoice_number = "E"+datetime_str+order_number
        invoice_type = request.POST.get('invoice_type')
        invoice_amount = request.POST.get('invoice_amount')
        tips_amount = request.POST.get('tips_amount')
        payment_method = request.POST.get('payment_method')
        receivable_amount = request.POST.get('receivable_amount')
        transaction_reference = request.POST.get('transaction_reference')
        payment_method_2 = request.POST.get('payment_method_2')
        receivable_amount_2 = request.POST.get('receivable_amount_2')
        transaction_reference_2 = request.POST.get('transaction_reference_2')
        invoice_date = out_date
        status = 1
        member_id = 0
        booking_id = 0
        invoice_type = "2"
        try:
            invoice = Invoices()
            invoice.shop_code = shop_code
            invoice.order_id = order_id
            invoice.member_id = member_id
            invoice.booking_id = booking_id
            invoice.invoice_number = invoice_number
            invoice.invoice_type = invoice_type
            invoice.payment_method = payment_method
            invoice.transaction_reference = transaction_reference
            invoice.invoice_amount = invoice_amount
            invoice.tips_amount = tips_amount
            invoice.receivable_amount = receivable_amount
            invoice.payment_method_2 = payment_method_2
            invoice.receivable_amount_2 = receivable_amount_2
            invoice.transaction_reference_2 = transaction_reference_2
            invoice.invoice_date = today
            invoice.status = status
            invoice.loginid = request.session.get('loginid')
            invoice.save(using='zenpos')
        except Exception as e:
            return JsonResponse({'message': 'xxUpdate record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    if action == "check_table_available":
        table_key = request.POST.get('table_key')
        try:
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr( settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
            cursor = cnxn.cursor()
            cursor.execute("select * from V_TableDinein_List where table_key = '" + table_key + "'")
            table_dinein_list = cursor.fetchall()
            if table_dinein_list:
                if table_dinein_list[0].dinein_id is None:
                    return HttpResponse('Yes')
                else:
                    return HttpResponse('No')
            else:
                return HttpResponse('Fail')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
    return render(request, "pos_template/payment_response.html", context)

@csrf_exempt
def order_save(request):
    if not request.session.get('username'): return redirect('login')
    booking_id = request.POST.get('booking_id')
    action = str(request.POST.get('action'))
    table_key = request.POST.get('table_key')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    booking_time = request.POST.get('booking_time')
    if booking_time < "1800":
        time = "1100"
    else:
        time = "1800"
    number_guests = request.POST.get('number_guests')
    member_number = request.POST.get('member_number')
    customer_name = request.POST.get('customer_name')
    gender = request.POST.get('gender')
    phone_area_code = request.POST.get('phone_area_code')
    phone_number = request.POST.get('phone_number')
    type = request.POST.get('type')
    remarks = request.POST.get('remarks')
    username = request.POST.get('username')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    try:
        if action == "add":
            booking = Bookings()
            booking.booking_status = 1
            booking.deposit_status = 0
            booking.confirm_status = 0
            booking.show_status = 0
            booking.createdate = datetime_str
            booking.modifydate = datetime_str
        else:
            booking = Bookings.objects.using('zenpos').get(booking_id=booking_id)
            booking.modifydate = datetime_str
        booking.table_key = table_key
        booking.start_date = start_date + " " + booking_time[:2] + ":" + booking_time[-2:] + ":00"
        booking.end_date = end_date + " 23:59:59"
        booking.time = time
        booking.booking_time = booking_time
        booking.number_guests = number_guests
        booking.member_number = member_number
        booking.customer_name = customer_name
        booking.gender = gender
        booking.phone_area_code = phone_area_code
        booking.phone_number = phone_number
        booking.type = type
        booking.remarks = remarks
        booking.username = username
        if action == "add": booking.createdate = datetime_str
        if action == "add" or action == "edit": booking.save(using='zenpos')
        if action == "delete": booking.delete()
        #if action == "add":
        memberAddStatus = memberAdd(member_number, customer_name, gender, phone_area_code, phone_number)
        messages.success(request, "New room booking was created successfully.")
        return HttpResponse("True" + action + memberAddStatus)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

def memberAdd(member_number, member_name, gender, area_code, phone_number, shop_code):
    if not Members.objects.using('zenpos').filter(member_number=member_number).exists():
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
        member = Members()
        member.member_number = member_number
        member.member_name = member_name
        member.gender = gender
        member.phone_area_code = area_code
        member.phone_number = phone_number
        member.join_date = datetime_str
        member.modify_date = datetime_str
        member.shop_code = shop_code
        member.status = 1
        member.save(using='zenpos')
        return "Success"
    else:
        return "Member number already exists"

def orderLogAdd(order_item_id, order_id, product_id, quantity, order_item_date, order_item_type, order_sequence, status, order_number, product_name, product_name_e, selling_price, product_description, shop_code):
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    orderlog = OrderLogs()
    orderlog.order_item_id = order_item_id
    orderlog.order_id = order_id
    orderlog.product_id = product_id
    orderlog.quantity = quantity
    orderlog.order_item_date = order_item_date
    orderlog.order_item_type = order_item_type
    orderlog.order_sequence = order_sequence
    orderlog.status = status
    orderlog.order_number = order_number
    orderlog.product_name = product_name
    orderlog.product_name_e = product_name_e
    orderlog.selling_price = selling_price
    orderlog.product_description = product_description
    orderlog.order_log_date = datetime_str
    orderlog.shop_code = shop_code
    orderlog.loginid = request.session.get('loginid')
    orderlog.save(using='zenpos')
    return "Success"

def transaction(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')
    ShopList = Shops.objects.using('zenpos').filter(status=1)
    shop_code = request.session.get('team')

    accessid = 109
    request.session['accessid'] = accessid
    cnxn_menu=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
    cursor_menu = cnxn_menu.cursor()
    cursor_menu.execute("exec spSQPGetMenuItem " + str(accessid))
    menuItem = cursor_menu.fetchall()
    cursor_menu.execute("select * from V_UserAccessRight where username = '"+request.session.get('username')+"'")
    menuList = cursor_menu.fetchall()
    users = Users.objects.using('zensystem').get(username=request.session.get('username'),isactive=1)
    users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    users.save(using='zensystem')
    #pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_shop_code": shop_code,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "shoplist": ShopList,
    }
    return render(request, "pos_template/transaction.html", context)

@csrf_exempt
def transaction_response(request):
    if not request.session.get('username'): return redirect('login')
    action = request.POST.get('action')
    shop_code = request.POST.get('shop_code')
    loginid = request.POST.get('loginid')
    start_date = str(request.POST.get('start_date'))
    end_date = str(request.POST.get('end_date'))
    if str(request.POST.get('end_date')) == "":
        end_date = str(request.POST.get('start_date')) + " 23:59:59"
    else:
        end_date = str(request.POST.get('end_date')) + " 23:59:59"

    if action == "menutab":
        context = {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zensystem')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "userlist": user_list,
        }
    if action == "invoice_record":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        sql = "select * from V_Invoice_List "  \
              "where (1 = case when '' = ? then 1 when invoice_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when invoice_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when shop_code = ? then 1 else 0 end)  " \
              "order by invoice_date desc"
        params = (start_date, start_date, end_date, end_date, shop_code, shop_code)
        cursor.execute(sql, params)
        invoice_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_shop_code": shop_code,
            "user_loginid": loginid,
            "invoice_list": invoice_list,
            "sql": sql,
        }
    if action == "invoice_daily":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        sql = "select * from V_Invoice_Daily_List "  \
              "where (1 = case when '' = ? then 1 when invoice_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when invoice_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when shop_code = ? then 1 else 0 end)  " \
              "order by invoice_date desc"
        params = (start_date, start_date, end_date, end_date, shop_code, shop_code)
        cursor.execute(sql, params)
        invoice_daily_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_shop_code": shop_code,
            "user_loginid": loginid,
            "invoice_daily_list": invoice_daily_list,
            "sql": sql,
        }
    if action == "invoice_snapshot":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        sql = "select * from V_Invoice_Snapshot_List "  \
              "where (1 = case when '' = ? then 1 when invoice_date >= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when invoice_date <= ? then 1 else 0 end)  " \
              "and (1 = case when '' = ? then 1 when shop_code = ? then 1 else 0 end)  " \
              "order by invoice_date desc"
        params = (start_date, start_date, end_date, end_date, shop_code, shop_code)
        cursor.execute(sql, params)
        invoice_snapshot_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_shop_code": shop_code,
            "user_loginid": loginid,
            "invoice_snapshot_list": invoice_snapshot_list,
            "sql": sql,
        }
    if action == "take_snapshot":
        sql = "success"
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=zenpos')
        cursor = cnxn.cursor()
        sql = "select top 1 * from V_Invoice_Daily_List order by invoice_date desc"
        #params = (start_date, start_date, end_date, end_date, team, team)
        cursor.execute(sql)
        invoice_daily_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        try:
            for w in invoice_daily_list:
                snapshot = InvoiceSnapshots()
                snapshot.snapshot_date = datetime_str
                snapshot.invoice_date = w.invoice_date
                snapshot.daily_amount = w.daily_amount
                snapshot.total_tips = w.total_tips
                snapshot.total_receivable = w.total_receivable
                snapshot.visa_count = w.visa_count
                snapshot.master_count = w.master_count
                snapshot.cash_count = w.cash_count
                snapshot.alipay_count = w.alipay_count
                snapshot.wechatpay_count = w.wechatpay_count
                snapshot.unionpay_count = w.unionpay_count
                snapshot.banktransfer_count = w.banktransfer_count
                snapshot.wallet_count = w.wallet_count
                snapshot.shop_code = w.shop_code
                snapshot.loginid = request.session.get('loginid')
                snapshot.save(using='zenpos')
                return HttpResponse('Update Success')
        except Exception as e:
            return JsonResponse({'message': 'Update record failed. Error: {}'.format(e)}, status=500)
        return HttpResponse('Update Success')

    return render(request, "pos_template/transaction_response.html", context)

def printOrderLogo(request, order_id, print_type):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_code = shop_list[0].shop_code
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = getattr(settings, "PRINTER_LOCATION_CODE", None)
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id
        printer_id = printer_list[0].printer_id
        printer_name = printer_list[0].printer_name

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = ""
    qos = 1

    # connected the MQTT SERVER
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                return JsonResponse({'message': 'Success to connect: {}'.format(rc)}, status=500)
            else:
                print("Failed to connect to MQTT,Return code %d\n ", rc)
                return JsonResponse({'message': 'Failed to connect to MQTT,Return code: {}'.format(rc)}, status=500)

        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.username_pw_set(username, password)
        client.connect(broker_address, port, qos)
        return client

    def on_message(client, userdata, msg):
        print(f"Received Message:{message.payload.decode()}")
        received_message = message.payload.decode("utf-8")
        parts = received_message.split(";")
        if parts[0] == "3":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "printer get ticket."
            printerlog.save(using='zenpos')
            print("printer get ticket")
        elif parts[0] == "4":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "printer printed success."
            printerlog.save(using='zenpos')
            print("printer printed success")
        elif parts[0] == "5":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "ticket over time,pls try again."
            printerlog.save(using='zenpos')
            print("ticket over time,pls try again")
        else:
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "don't know the stauts:."
            printerlog.save(using='zenpos')
            print("don't know the stauts:")

        print(f"Received message on {msg.topic}: {msg.payload.decode()}")
        # Check the status of the print job
        if msg.topic == STATUS_TOPIC:
            status_message = msg.payload.decode()
            # Check for success or error in the status message
            if "success" in status_message:
                # Add printer log when request to print
                printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                printerlog.printer_printed = 1
                printerlog.log_detail = printerlog.log_detail + "/" + "Receipt printed successfully."
                printerlog.save(using='zenpos')
                print("Receipt printed successfully.")
            elif "error" in status_message:
                printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                printerlog.printer_printed = 2
                printerlog.log_detail = printerlog.log_detail + "/" + "Receipt printed successfully."
                printerlog.save(using='zenpos')
                print("Error printing receipt.")

    try:
        # publsh the manager to printer
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_OrderDinein_List where order_id = " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDinein_List where order_id = " + order_id)
        order_item_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        order_payment_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemTotalItem_List where order_id = " + order_id)
        order_item_total_list = cursor.fetchall()

        if order_item_dinein_list:
            client = connect_mqtt()
            esc_comm = ESCPOSManager()
            #esc_comm.add_command(b"\x1B\x40")
            #esc_comm.add_command(b"\x1C\x26\x1B\x39\x03")
            esc_comm.Prefix_command()
            esc_comm.add_command(b"\x1C\x26\x1B\x39\x01")

            esc_comm.set_alignment("center")
            esc_comm.add_command(b"\x1C\x70\x01")
            #esc_comm.add_command(bytes([255, 152, 48, 50, 0])
            #esc_comm.print_nv_image(image_number=0)

            esc_comm.set_alignment("center")
            esc_comm.set_font_size(128)
            shop_name = "福茶〈澳門〉"
            esc_comm.print_text(shop_name + "\n")
            esc_comm.feed_lines(1)
            esc_comm.set_alignment("center")
            esc_comm.set_font_size(128)
            table = "單號："
            order_date = "訂單時間："
            staff = "負責職員："

            table_key = order_item_dinein_list[0].table_key
            order_key = str(order_dinein_list[0].order_date)[:19]
            staff_key = order_dinein_list[0].LoginNameDesc
            esc_comm.set_alignment("left")
            if print_type == "reprint":
                print_type_text = " (重印)"
            else:
                print_type_text = ""
            line = table + table_key + print_type_text
            esc_comm.print_text(line + "\n")
            esc_comm.feed_lines(5)
            esc_comm.cut_paper()

            esc_data = esc_comm.send_command()
            client.publish(topic, esc_data)

            client.disconnect()
            return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs

def printOrderItemReceipt(request, order_id, print_type):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_code = shop_list[0].shop_code
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = getattr(settings, "PRINTER_LOCATION_CODE", None)
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id
        printer_id = printer_list[0].printer_id
        printer_name = printer_list[0].printer_name

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = ""
    qos = 1
    printer_log_id = 0

    # connected the MQTT SERVER
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                return JsonResponse({'message': 'Success to connect: {}'.format(rc)}, status=500)
            else:
                print("Failed to connect to MQTT,Return code %d\n ", rc)
                return JsonResponse({'message': 'Failed to connect to MQTT,Return code: {}'.format(rc)}, status=500)

        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.username_pw_set(username, password)
        client.connect(broker_address, port, qos)
        return client

    def on_message(client, userdata, msg):
        print(f"Received Message:{message.payload.decode()}")
        received_message = message.payload.decode("utf-8")
        parts = received_message.split(";")
        printer_log_id = 176
        if parts[0] == "3":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "printer get ticket."
            printerlog.save(using='zenpos')
            print("printer get ticket")
        elif parts[0] == "4":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "printer printed success."
            printerlog.save(using='zenpos')
            print("printer printed success")
        elif parts[0] == "5":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "ticket over time,pls try again."
            printerlog.save(using='zenpos')
            print("ticket over time,pls try again")
        else:
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "don't know the stauts:."
            printerlog.save(using='zenpos')
            print("don't know the stauts:")

        print(f"Received message on {msg.topic}: {msg.payload.decode()}")
        # Check the status of the print job
        if msg.topic == STATUS_TOPIC:
            status_message = msg.payload.decode()
            # Check for success or error in the status message
            if "success" in status_message:
                # Add printer log when request to print
                printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                printerlog.printer_printed = 1
                printerlog.log_detail = printerlog.log_detail + "/" + "Receipt printed successfully."
                printerlog.save(using='zenpos')
                print("Receipt printed successfully.")
            elif "error" in status_message:
                printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                printerlog.printer_printed = 2
                printerlog.log_detail = printerlog.log_detail + "/" + "Receipt printed successfully."
                printerlog.save(using='zenpos')
                print("Error printing receipt.")

    try:
        # publsh the manager to printer
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_OrderDinein_List where order_id = " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDinein_List where order_id = " + order_id)
        order_item_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        order_payment_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemTotalItem_List where order_id = " + order_id)
        order_item_total_list = cursor.fetchall()

        if order_item_dinein_list:
            client = connect_mqtt()
            esc_comm = ESCPOSManager()
            #esc_comm.add_command(b"\x1B\x40")
            #esc_comm.add_command(b"\x1C\x26\x1B\x39\x03")
            esc_comm.Prefix_command()
            esc_comm.set_alignment("center")
            esc_comm.add_command(b"\x1C\x26\x1B\x39\x01")
            esc_comm.set_font_size(128)
            esc_comm.add_command(b"\x1C\x70\x01")
            shop_name = " 福茶〈澳門〉 "
            esc_comm.print_text(shop_name + "\n")
            esc_comm.feed_lines(1)
            esc_comm.set_alignment("center")
            esc_comm.set_font_size(128)
            table = "單號："
            order_date = "訂單時間："
            staff = "負責職員："

            table_key = order_item_dinein_list[0].table_key
            order_key = str(order_dinein_list[0].order_date)[:19]
            staff_key = order_dinein_list[0].LoginNameDesc
            esc_comm.set_alignment("left")
            if print_type == "reprint":
                print_type_text = " (重印)"
            else:
                print_type_text = ""
            line = table + table_key + print_type_text
            esc_comm.print_text(line + "\n")

            esc_comm.set_font_size(13)
            line = order_date + order_key
            esc_comm.print_text(line + "\n")
            line = staff + staff_key
            esc_comm.print_text(line + "\n")

            # Create Printer Log Header
            printerlog = PrinterLogs()
            datetime_dt = datetime.datetime.today()
            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
            printerlog.printer_id = printer_id
            printerlog.order_id = order_id
            printerlog.order_item_id = 0
            printerlog.order_date = str(order_dinein_list[0].order_date)
            printerlog.table_key = table_key
            printerlog.print_type = print_type
            printerlog.log_title = "Receipt Reprinting - " + table_key
            printerlog.apps_sent = 1
            printerlog.location_code = location_code
            printerlog.sent_datetime = datetime_str
            printerlog.save(using='zenpos')
            printer_log_id = printerlog.printer_log_id

            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.log_detail = esc_comm.heartbeat_check()
            printerlog.save(using='zenpos')

            esc_comm.feed_lines(1)
            esc_comm.set_font_size(13)
            space = "   "
            quantity = "數量"
            item = "項目"
            unit_price = "單價($)"
            selling_price = "金額($)"

            line = f"{quantity:<4}{space:<0}{item:<0}{space:<10}     {unit_price:>7}  {selling_price:<7}"
            esc_comm.print_text(line + "\n")
            esc_comm.print_text("----------------------------------------------" + "\n")
            esc_comm.set_alignment("left")
            max_product_name_length = max(len(item.product_name.encode('BIG5')) for item in order_item_dinein_list)
            max_quantity_length = max(len(str(item.quantity)) for item in order_item_dinein_list)
            for w in order_item_dinein_list:
                if w.order_item_type == 2:
                    takeaway = " ﹝外賣﹞"
                else:
                    takeaway = ""
                product_name = w.product_name + takeaway
                product_name_len = int(len(product_name.encode('BIG5')))
                product_name_space = abs(int(20 - len(product_name.encode('BIG5'))))
                quantity = str(w.quantity)
                order_item_date = w.order_item_date.strftime("%H:%M")
                unit_price = str(w.selling_price)
                selling_price = w.quantity * w.selling_price
                selling_price = str(selling_price)
                order_item_id = w.order_item_id

                line = f"{quantity:>3} {space:<2} {product_name:<0} {space:>{product_name_space}} {unit_price:>7}  {selling_price:>7}"
                esc_comm.print_text(line + "\n")

                for v in order_item_detail_list:
                    if v.order_item_id == order_item_id:
                        quantity_detail = ""
                        code_detail_name = "- " + v.code_detail_name
                        code_detail_name_len = int(len(code_detail_name.encode('BIG5')))
                        code_detail_name_space = abs(int(20 - len(code_detail_name.encode('BIG5'))))
                        unit_price = str(v.selling_price)
                        selling_price = str(w.quantity * v.selling_price)
                        line = f"{quantity_detail:<3} {space:<2} {code_detail_name:<0} {space:>{code_detail_name_space}} {unit_price:>7}  {selling_price:>7}"
                        esc_comm.print_text(line + "\n")
            esc_comm.print_text("----------------------------------------------" + "\n")
            sub_total = "小計($)"
            discount_total = "優惠($)"
            grand_total = "總計($)"
            sub_total_value = order_cost_list[0].total_cost_order
            discount_total_value = order_cost_list[0].total_cost_discount
            grand_total_value = order_cost_list[0].total_cost

            line = f"{sub_total:<10} {space:>24} {sub_total_value:>8}"
            esc_comm.print_text(line + "\n")
            line = f"{discount_total:<10} {space:>24} {discount_total_value:>8}"
            esc_comm.print_text(line + "\n")
            esc_comm.print_text("==============================================" + "\n")
            line = f"{grand_total:<10} {space:>24} {grand_total_value:>8}"
            esc_comm.print_text(line + "\n")

            esc_comm.feed_lines(1)

            for x in order_payment_list:
                esc_comm.set_font_size(13)
                payment_method_text = "付款方法   ："
                transaction_date_text = "交易日期   ："
                receivable_amount_text = "實收金額($)："
                change_amount_text = "找回金額($)："
                total_amount_text = "總計金額($)："
                remark_text = "訂單備註   ："
                payment_method = x.payment_method
                receivable_amount = x.receivable_amount
                change_amount = x.change_amount
                transaction_reference = x.transaction_reference
                transaction_date = x.transaction_date.strftime("%Y-%m-%d %H:%M")
                line = f"{payment_method_text:<1}{payment_method:<10}"
                esc_comm.print_text(line + "\n")
                line = f"{transaction_date_text:<1}{transaction_date:<20}"
                esc_comm.print_text(line + "\n")
                line = f"{receivable_amount_text:<1}{receivable_amount:>5}"
                esc_comm.print_text(line + "\n")
                if payment_method == "現金":
                    line = f"{change_amount_text:<1}{change_amount:>5}"
                    esc_comm.print_text(line + "\n")
                line = f"{total_amount_text:<1}{grand_total_value:>5}"
                esc_comm.print_text(line + "\n")
                if transaction_reference != "":
                    line = f"{remark_text:<1}{transaction_reference:<20}"
                    esc_comm.print_text(line + "\n")
            print_location_text = "列印位置   ："
            line = f"{print_location_text:<1}{printer_name:<10}"
            esc_comm.print_text(line + "\n")
            reprint_text = "重印日期   ："
            line = f"{reprint_text:<1}{datetime_str:<20}"
            esc_comm.print_text(line + "\n")

            esc_comm.feed_lines(5)
            #esc_comm.add_command(b"\x1B\x6D")
            esc_comm.cut_paper()

            esc_data = esc_comm.send_command()
            client.publish(topic, esc_data)
            client.on_message = on_message
            client.subscribe("printer/status")
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            datetime_dt = datetime.datetime.today()
            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
            printerlog.printer_received = 1
            printerlog.received_datetime = datetime_str
            printerlog.log_detail = printerlog.log_detail
            printerlog.save(using='zenpos')
            client.subscribe("PrintSuccess")

            client.disconnect()
            return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs

def printOrderItemLabel(request, order_id, print_type):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_code = shop_list[0].shop_code
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = getattr(settings, "PRINTER_LOCATION_CODE", None)
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id
        printer_id = printer_list[0].printer_id
        printer_name = printer_list[0].printer_name

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = ""
    qos = 1

    # connected the MQTT SERVER
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                return JsonResponse({'message': 'Success to connect: {}'.format(rc)}, status=500)
            else:
                print("Failed to connect to MQTT,Return code %d\n ", rc)
                return JsonResponse({'message': 'Failed to connect to MQTT,Return code: {}'.format(rc)}, status=500)

        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.username_pw_set(username, password)
        client.connect(broker_address, port, qos)
        return client

    try:
        # publsh the manager to printer
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_OrderDinein_List where order_id = " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDinein_List where order_id = " + order_id)
        order_item_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        order_payment_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemTotalItem_List where order_id = " + order_id)
        order_item_total_list = cursor.fetchall()

        if order_item_dinein_list:
            # Print Kitchen Label
            print_item_receipt_flag = "Y"
            print_item_label_flag = "Y"

            if print_item_receipt_flag == "Y" and print_item_label_flag == "Y":

                location_code = getattr(settings, "LABEL_LOCATION_CODE", None)
                printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

                if printer_list:
                    topic_2 = printer_list[0].printer_client_id
                    printer_id = printer_list[0].printer_id
                    printer_name = printer_list[0].printer_name

                client_2 = connect_mqtt()
                esc_comm_2 = ESCPOSManager()

                current_item = 0
                for w in order_item_dinein_list:
                    table_key = order_item_dinein_list[0].table_key
                    order_key = w.order_item_date.strftime("%H:%M")
                    product_type = w.product_type

                    if product_type == "M":
                        product_name = w.product_name
                        quantity = str(w.quantity)
                        order_item_date = w.order_item_date.strftime("%H:%M")
                        unit_price = w.selling_price
                        order_item_id = w.order_item_id
                        basic_counter = 0
                        more_counter = 0
                        basic_additional = ""
                        more_additional_1 = ""
                        more_additional_2 = ""
                        more_additional_3 = ""
                        more_additional_4 = ""
                        more_additional_5 = ""
                        more_additional_6 = ""

                        for v in order_item_detail_list:
                            if v.order_item_id == order_item_id:
                                if v.code_id == "11" or v.code_id == "12" or v.code_id == "15":
                                    basic_counter = basic_counter + 1
                                    if basic_counter == 1:
                                        basic_additional = "- " + v.code_detail_name
                                    else:
                                        basic_additional = basic_additional + " / " + v.code_detail_name
                                else:
                                    if v.code_detail_name != "第一份配料免費":
                                        more_counter = more_counter + 1
                                        if more_counter == 1: more_additional_1 = "- " + v.code_detail_name
                                        if more_counter == 2: more_additional_2 = "- " + v.code_detail_name
                                        if more_counter == 3: more_additional_3 = "- " + v.code_detail_name
                                        if more_counter == 4: more_additional_4 = "- " + v.code_detail_name
                                        if more_counter == 5: more_additional_5 = "- " + v.code_detail_name
                                        if more_counter == 6: more_additional_6 = "- " + v.code_detail_name

                        for y in range(w.quantity):
                            current_item = current_item + 1
                            # Create Printer Log Header
                            printerlog = PrinterLogs()
                            table_key = order_item_dinein_list[0].table_key
                            order_key = str(order_dinein_list[0].order_date)[:19]
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            datetime_time_str = datetime_dt.strftime("%H:%M")
                            printerlog.printer_id = printer_id
                            printerlog.order_id = order_id
                            printerlog.order_item_id = order_item_id
                            printerlog.order_date = str(order_dinein_list[0].order_date)
                            printerlog.table_key = table_key
                            printerlog.print_type = print_type
                            printerlog.log_title = "Label Reprinting - " + table_key + " - " + product_name
                            printerlog.apps_sent = 1
                            printerlog.location_code = location_code
                            printerlog.sent_datetime = datetime_str
                            printerlog.save(using='zenpos')
                            printer_log_id = printerlog.printer_log_id

                            total_item_text = str(current_item) + "/" + str(order_item_total_list[0].total_items)
                            # TSPL commands
                            tspl_command = f"""
                                SIZE 40 mm, 30 mm
                                GAP 2 mm, 0 mm
                                CLS
                                DIRECTION 1
                                TEXT 20, 10, "TSS24.BF2", 0, 1.5, 1.5, "單號：{table_key} 時間：{datetime_time_str}"
                                TEXT 20, 40, "TSS24.BF2", 0, 1.5, 1.5, "{product_name}"
                                TEXT 20, 70, "TSS24.BF2", 0, 1.5, 1.5, "{basic_additional}"
                                TEXT 20, 100, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_1}"
                                TEXT 20, 130, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_2}"
                                TEXT 20, 160, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_3}"
                                TEXT 20, 190, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_4}"
                                TEXT 240, 190, "TSS24.BF2", 0, 1.5, 1.5, "{total_item_text}"
                                PRINT 1, 1
                            """
                            #print(tspl_command)
                            #client_2.publish(topic_2, tspl_command)
                            # ZPL commands
                            zpl_command = """
                            ^XA
                            ^MNY
                            ^XZ
                            """
                            client_2.publish(topic_2, zpl_command)

                            zpl_command = f"""
                            ^XA
                            ^PQ1
                            ^PR2,0
                            ^CI28
                            ^PW240
                            ^LL320
                            ^FO00,00^A0N,25,25^FD單號：{table_key}    時間：{datetime_time_str}^FS
                            ^FO00,30^A0N,25,25^FD{product_name}^FS
                            ^FO00,60^A0N,25,25^FD{basic_additional}^FS
                            ^FO00,90^A0N,25,25^FD{more_additional_1}^FS
                            ^FO00,120^A0N,25,25^FD{more_additional_2}^FS
                            ^FO00,150^A0N,25,25^FD{more_additional_3}^FS
                            ^FO00,180^A0N,25,25^FD{more_additional_4}^FS
                            ^FO240,180^A0N,25,25^FD{total_item_text}^FS
                            ^XZ
                            """
                            #print(zpl_command)
                            client_2.publish(topic_2, zpl_command)

                            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                            printerlog.log_detail = esc_comm_2.heartbeat_check()
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            printerlog.printer_received = 1
                            printerlog.received_datetime = datetime_str
                            printerlog.save(using='zenpos')

                            #esc_data_2 = esc_comm_2.send_command()
                            #client_2.publish(topic_2, esc_data_2)
                            #print(tspl_command)
                            #client_2.publish(topic_2, tspl_command)
                client_2.disconnect()
            return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs

def printOrderItemLabelPaper(request, order_id, print_type):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_code = shop_list[0].shop_code
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = getattr(settings, "PRINTER_LOCATION_CODE", None)
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id
        printer_id = printer_list[0].printer_id
        printer_name = printer_list[0].printer_name

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = ""
    qos = 1

    # connected the MQTT SERVER
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                return JsonResponse({'message': 'Success to connect: {}'.format(rc)}, status=500)
            else:
                print("Failed to connect to MQTT,Return code %d\n ", rc)
                return JsonResponse({'message': 'Failed to connect to MQTT,Return code: {}'.format(rc)}, status=500)

        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.username_pw_set(username, password)
        client.connect(broker_address, port, qos)
        return client

    try:
        # publsh the manager to printer
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_OrderDinein_List where order_id = " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDinein_List where order_id = " + order_id)
        order_item_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        order_payment_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemTotalItem_List where order_id = " + order_id)
        order_item_total_list = cursor.fetchall()

        if order_item_dinein_list:
            client = connect_mqtt()
            esc_comm = ESCPOSManager()
            #esc_comm.add_command(b"\x1B\x40")
            #esc_comm.add_command(b"\x1C\x26\x1B\x39\x03")
            esc_comm.Prefix_command()
            esc_comm.add_command(b"\x1C\x26\x1B\x39\x01")

            # Print Kitchen Ticket
            print_item_receipt_flag = "Y"
            print_item_label_flag = "S"

            if print_item_receipt_flag == "Y" and print_item_label_flag == "S":

                current_item = 0
                for w in order_item_dinein_list:
                    table_key = order_item_dinein_list[0].table_key
                    order_key = w.order_item_date.strftime("%H:%M")
                    product_type = w.product_type

                    if product_type == "M":
                        product_name = w.product_name
                        quantity = str(w.quantity)
                        order_item_date = w.order_item_date.strftime("%H:%M")
                        unit_price = w.selling_price
                        order_item_id = w.order_item_id
                        basic_counter = 0
                        more_counter = 0
                        basic_additional = ""
                        more_additional_1 = ""
                        more_additional_2 = ""
                        more_additional_3 = ""
                        more_additional_4 = ""
                        more_additional_5 = ""
                        more_additional_6 = ""

                        for v in order_item_detail_list:
                            if v.order_item_id == order_item_id:
                                if v.code_id == "11" or v.code_id == "12" or v.code_id == "15":
                                    basic_counter = basic_counter + 1
                                    if basic_counter == 1:
                                        basic_additional = "- " + v.code_detail_name
                                    else:
                                        basic_additional = basic_additional + " / " + v.code_detail_name
                                else:
                                    if v.code_detail_name != "第一份配料免費":
                                        more_counter = more_counter + 1
                                        if more_counter == 1: more_additional_1 = "- " + v.code_detail_name
                                        if more_counter == 2: more_additional_2 = "- " + v.code_detail_name
                                        if more_counter == 3: more_additional_3 = "- " + v.code_detail_name
                                        if more_counter == 4: more_additional_4 = "- " + v.code_detail_name
                                        if more_counter == 5: more_additional_5 = "- " + v.code_detail_name
                                        if more_counter == 6: more_additional_6 = "- " + v.code_detail_name

                        for y in range(w.quantity):
                            current_item = current_item + 1
                            # Create Printer Log Header
                            printerlog = PrinterLogs()
                            table_key = order_item_dinein_list[0].table_key
                            order_key = str(order_dinein_list[0].order_date)[:19]
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            datetime_time_str = datetime_dt.strftime("%H:%M")
                            printerlog.printer_id = printer_id
                            printerlog.order_id = order_id
                            printerlog.order_item_id = order_item_id
                            printerlog.order_date = str(order_dinein_list[0].order_date)
                            printerlog.table_key = table_key
                            printerlog.print_type = print_type
                            printerlog.log_title = "Label Paper Reprinting - " + table_key + " - " + product_name
                            printerlog.apps_sent = 1
                            printerlog.location_code = location_code
                            printerlog.sent_datetime = datetime_str
                            printerlog.save(using='zenpos')
                            printer_log_id = printerlog.printer_log_id

                            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                            printerlog.log_detail = esc_comm.heartbeat_check()
                            printerlog.save(using='zenpos')
                            total_item_text = str(current_item) + "/" + str(order_item_total_list[0].total_items)

                            line = f"單號：{table_key:<0}   時間：{datetime_time_str:<0}"
                            esc_comm.print_text(line + "\n")
                            line = f"{product_name:<0}"
                            esc_comm.print_text(line + "\n")
                            if basic_additional != "":
                                line = f"{basic_additional:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_1 != "":
                                line = f"{more_additional_1:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_2 != "":
                                line = f"{more_additional_2:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_3 != "":
                                line = f"{more_additional_3:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_4 != "":
                                line = f"{more_additional_4:<0}"
                                esc_comm.print_text(line + "\n")
                            if total_item_text != "":
                                line = f"                     {total_item_text:<0}"
                                esc_comm.print_text(line + "\n")
                            esc_comm.feed_lines(5)
                            esc_comm.add_command(b"\x1B\x6D")
                            #esc_comm.print_text("---------------------------" + "\n")

            esc_data = esc_comm.send_command()
            client.publish(topic, esc_data)

            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.log_detail = esc_comm.heartbeat_check()
            datetime_dt = datetime.datetime.today()
            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
            printerlog.printer_received = 1
            printerlog.received_datetime = datetime_str
            printerlog.save(using='zenpos')

            client.disconnect()

            return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs


def get_first_n_chars(input_string, n):
    count = 0
    result = []

    for char in input_string:
        # Count each Chinese character as 2
        if '\u4e00' <= char <= '\u9fff':  # Range for common Chinese characters
            count += 2
        else:
            count += 1

        result.append(char)

        # Stop if we reach or exceed the desired length
        if count >= n:
            break

    return ''.join(result)

def convert_big5(input_string):
    try:
        new_string = input_string.encode('BIG5')
        return new_string
    except Exception as e:
        return input_string
    return input_string

def printOrderItemReceipt_XPrinter(request, order_id, print_type):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_code = shop_list[0].shop_code
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = getattr(settings, "PRINTER_LOCATION_CODE", None)
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id
        printer_id = printer_list[0].printer_id
        printer_name = printer_list[0].printer_name
        printer_serial_number = printer_list[0].printer_serial_number

    try:
        # publsh the manager to printer
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_OrderDinein_List where order_id = " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDinein_List where order_id = " + order_id)
        order_item_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        order_payment_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemTotalItem_List where order_id = " + order_id)
        order_item_total_list = cursor.fetchall()

        if order_item_dinein_list:
            USER_NAME = getattr(settings, "XPRINTER_USER_NAME", None)
            USER_KEY = getattr(settings, "XPRINTER_USER_KEY", None)
            OK_PRINTER_SN = printer_serial_number

            printContent = ""
            printContent = printContent + f"<C><IMG></IMG></C>"
            shop_name = "向太生活空間"
            #printContent = printContent + f"<C><B>{shop_name}<BR><BR></B></C>"
            datetime_dt = datetime.datetime.today()
            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
            table_key = order_item_dinein_list[0].table_key
            invoice_key = order_payment_list[0].invoice_number
            order_key = str(order_dinein_list[0].order_date)[:19]
            staff_key = order_dinein_list[0].username
            if print_type == "reprint":
                print_type_text = " (重印)"
            else:
                print_type_text = ""
            printContent = printContent + f"<BR>"
            printContent = printContent + f"<B>單號：{table_key}{print_type_text}</B><BR>訂單號碼：{invoice_key}<BR>訂單時間：{order_key}<BR>負責職員：{staff_key}<BR><BR>"


            # Create Printer Log Header
            printerlog = PrinterLogs()
            datetime_dt = datetime.datetime.today()
            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
            printerlog.printer_id = printer_id
            printerlog.order_id = order_id
            printerlog.order_item_id = 0
            printerlog.order_date = str(order_dinein_list[0].order_date)
            printerlog.table_key = table_key
            printerlog.print_type = print_type
            printerlog.log_title = "Receipt Printing - " + table_key
            printerlog.apps_sent = 1
            printerlog.location_code = location_code
            printerlog.sent_datetime = datetime_str
            printerlog.save(using='zenpos')
            printer_log_id = printerlog.printer_log_id

            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.save(using='zenpos')

            printContent = printContent + f"數量  項目                      單價($)  金額($)<BR>"
            printContent = printContent + f"------------------------------------------------"
            max_quantity_length = max(len(str(item.quantity)) for item in order_item_dinein_list)
            max_product_name_length = max(len(convert_big5(item.product_name)) for item in order_item_dinein_list)

            #printContent = printContent + "<TABLE col=""10,10,12,10"" w=1 h=1 b=1 lh=68><tr>AAA<td>1<td>52.00</tr><tr>BB<td>1<td>48.00</tr><tr>CC<td>1<td>95.00</tr></TABLE>"
            #printContent = printContent + "<TABLE col=""10,10,12"" w=1 h=1 b=1 lh=68><tr>彌蔆陷(溫棣)樓昹圖<td>    1爺<td>52.00</tr><tr>啞憐<td>    1爺<td>48.00</tr><tr>旮凝尥塑<td> 1爺(湮)<td>95.00</tr></TABLE>"

            printContent = printContent + f"""<TABLE col="3,3,24,9,9" w=1 h=1 b=1 lh=80>
            """

            #printContent = printContent + f"<TABLE col=""10,10,12"" w=1 h=1 b=1 lh=68><tr>AAAA<td>1<td>52.00</tr><tr>BB<td>2<td>48.00</tr><tr>CC<td>1<td>95.00</tr></TABLE>"
            for w in order_item_dinein_list:
                if w.order_item_type == 2:
                    takeaway = " ﹝外賣﹞"
                else:
                    takeaway = ""
                product_name = w.product_name + takeaway
                product_name_ch = get_first_n_chars(product_name, 22)
                product_name_len = int(len(convert_big5(product_name)))
                product_name_len_ch = int(len(convert_big5(product_name_ch)))
                if product_name_len > 25:
                    product_name_space = 0
                else:
                    product_name_space = abs(int(25 - product_name_len))
                if product_name_len_ch == 24:
                    product_name_space = 1
                product_code = w.product_code
                product_name_space_text = "                              "[:product_name_space]
                quantity = str(w.quantity)
                quantity_space = abs(int(3-len(quantity)))
                quantity_space_text = "                              "[:quantity_space]
                order_item_date = w.order_item_date.strftime("%H:%M")
                unit_price = str(w.selling_price)
                unit_price_space = abs(int(9-len(unit_price)))
                unit_price_space_text = "                              "[:unit_price_space]
                selling_price = w.quantity * w.selling_price
                selling_price = str(selling_price)
                selling_price_space = abs(int(9-len(selling_price)))
                selling_price_space_text = "                              "[:selling_price_space]
                order_item_id = w.order_item_id

                #printContent = printContent + f'<TABLE>'
                #printContent = printContent + f"</TABLE>"
                #printContent = printContent + f"<R>  {quantity}</R>    <L>{product_name}</L>             <R>{unit_price}</R>   <R>{selling_price}</R><BR>"
                # 1st row
                #printContent = printContent + f"  {quantity} {product_name_len_ch}  {product_name_len}{product_name_ch}{product_name_space}{unit_price_space}{unit_price}{selling_price_space}{selling_price}<BR>"
                #printContent = printContent + f"  {quantity}   {get_first_n_chars(product_name, 22)}{product_name_space}{unit_price_space}{unit_price}{selling_price_space}{selling_price}<BR>"
                #printContent = printContent + f"  {quantity}   {product_name_ch}{product_name_space_text}{unit_price_space_text}{unit_price}{selling_price_space_text}{selling_price}<BR>"

                #printContent = printContent + f"""
                #    <tr><R>{quantity}</R><td><L>{product_name}</L><td><R>{unit_price}</R><td><R>{selling_price}</R></tr>
                #"""
                printContent = printContent + f"""
                    <tr>{quantity_space_text}{quantity}<td>   <td>{product_name}<td>{unit_price_space_text}{unit_price}<td>{selling_price}</tr>
                """
                printContent = printContent + f"""
                    <tr>   <td>   <td>{product_code}      <td>       <td>       </tr>
                """

                # 2nd row
                #if product_name_len > 23:
                #    product_name_2 = product_name.replace(get_first_n_chars(product_name, 22), "")
                #    product_name_len = product_name_len - 23
                #    printContent = printContent + f"      {product_name_2}<BR>"

                for v in order_item_detail_list:
                    if v.order_item_id == order_item_id:
                        quantity_detail = ""
                        code_detail_name = "- " + v.code_detail_name
                        code_detail_name_len = int(len(code_detail_name.encode('BIG5')))
                        code_detail_name_space = abs(int(20 - len(code_detail_name.encode('BIG5'))))
                        unit_price = str(v.selling_price)
                        selling_price = str(w.quantity * v.selling_price)
                        printContent = printContent + f"<R>  {quantity_detail} {code_detail_name}{unit_price}{selling_price}<BR>"
                        #line = f"{quantity_detail:<3} {space:<2} {code_detail_name:<0} {space:>{code_detail_name_space}} {unit_price:>7}  {selling_price:>7}"

            printContent = printContent + f"""</TABLE>"""

            printContent = printContent + f"------------------------------------------------<BR>"
            sub_total = "小計($)"
            discount_total = "優惠($)"
            grand_total = "總計($)"
            sub_total_value = str(order_cost_list[0].total_cost_order)
            sub_total_value_space = abs(int(9 - len(sub_total_value)))
            sub_total_value_space_text = "                              "[:sub_total_value_space]
            discount_total_value = str(order_cost_list[0].total_cost_discount)
            discount_total_value_space = abs(int(9 - len(discount_total_value)))
            discount_total_value_space_text = "                              "[:discount_total_value_space]
            grand_total_value = str(order_cost_list[0].total_cost)
            grand_total_value_space = abs(int(9 - len(grand_total_value)))
            grand_total_value_space_text = "                              "[:grand_total_value_space]
            printContent = printContent + f"{sub_total}<R>{sub_total_value_space_text}{sub_total_value}<BR></R>"
            printContent = printContent + f"{discount_total}<R>{discount_total_value_space_text}{discount_total_value}<BR></R>"
            printContent = printContent + f"================================================<BR>"
            printContent = printContent + f"{grand_total}<R>{grand_total_value_space_text}{grand_total_value}<BR></R>"
            printContent = printContent + '<BR>'

            for x in order_payment_list:
                payment_method_text = "付款方法   ："
                transaction_date_text = "交易日期   ："
                receivable_amount_text = "實收金額($)："
                change_amount_text = "找回金額($)："
                total_amount_text = "總計金額($)："
                remark_text = "訂單備註   ："
                payment_method = x.payment_method
                receivable_amount = str(x.receivable_amount)
                change_amount = str(x.change_amount)
                transaction_reference = x.transaction_reference
                transaction_date = x.transaction_date.strftime("%Y-%m-%d %H:%M")
                printContent = printContent + f"<L>{payment_method_text}{payment_method}<BR></L>"
                printContent = printContent + f"<L>{transaction_date_text}{transaction_date}<BR></L>"
                printContent = printContent + f"<L>{receivable_amount_text}{receivable_amount}<BR></L>"
                if payment_method == "現金":
                    change_amount_space = abs(int(len(receivable_amount) - len(change_amount)))
                    change_amount_space_text = "                              "[:change_amount_space]
                    printContent = printContent + f"<L>{change_amount_text}{change_amount_space_text}{change_amount}<BR></L>"
                #printContent = printContent + f"<L>{total_amount_text}{grand_total_value}<BR></L>"
                if transaction_reference != "":
                    printContent = printContent + f"<L>{remark_text}{transaction_reference}<BR></L>"
            print_location_text = "列印位置   ："
            printContent = printContent + f"<L>{print_location_text}{printer_name}<BR></L>"
            reprint_text = "重印日期   ："
            printContent = printContent + f"<L>{reprint_text}{datetime_str}<BR></L>"

            request = model.PrintRequest(USER_NAME, USER_KEY)

            # *必填*：打印机编号
            request.sn = OK_PRINTER_SN
            request.generateSign()

            # *必填*：打印内容,不能超过12K
            request.content = printContent

            # 打印份数，默认为1
            request.copies = 1

            # 声音播放模式，0 为取消订单模式，1 为静音模式，2 为来单播放模式，3为有用户申请退单了。默认为 2 来单播放模式
            request.voice = 2

            # 打印模式：
            # 值为 0 或不指定则会检查打印机是否在线，如果不在线 则不生成打印订单，直接返回设备不在线状态码；如果在线则生成打印订单，并返回打印订单号。
            # 值为 1不检查打印机是否在线，直接生成打印订单，并返回打印订单号。如果打印机不在线，订单将缓存在打印队列中，打印机正常在线时会自动打印。
            request.mode = 0

            result = service.xpYunPrint(request)
            #print(result.httpStatusCode)
            #print(result.content)
            #print(result.content.code)
            #print(result.content.msg)
            #print(result.content.data)

            return "Print Success"+str(result.content.code) + result.content.msg # Return success message
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        return "Error printing: line no. " + str(line_number) + ": " + str(e)  # Return error message if an exception occurs

def printOrderItemAll(request, order_id, print_type):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_code = shop_list[0].shop_code
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = getattr(settings, "PRINTER_LOCATION_CODE", None)
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id
        printer_id = printer_list[0].printer_id
        printer_name = printer_list[0].printer_name

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = "Receipt_Printer"
    qos = 2

    # connected the MQTT SERVER
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                return JsonResponse({'message': 'Success to connect: {}'.format(rc)}, status=500)
            else:
                print("Failed to connect to MQTT,Return code %d\n ", rc)
                return JsonResponse({'message': 'Failed to connect to MQTT,Return code: {}'.format(rc)}, status=500)

        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.username_pw_set(username, password)
        client.connect(broker_address, port, qos)
        return client

    def on_message(client, userdata, msg):
        print(f"Received Message:{message.payload.decode()}")
        received_message = message.payload.decode("utf-8")
        parts = received_message.split(";")
        if parts[0] == "3":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "printer get ticket."
            printerlog.save(using='zenpos')
            print("printer get ticket")
        elif parts[0] == "4":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "printer printed success."
            printerlog.save(using='zenpos')
            print("printer printed success")
        elif parts[0] == "5":
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "ticket over time,pls try again."
            printerlog.save(using='zenpos')
            print("ticket over time,pls try again")
        else:
            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.printer_printed = 1
            printerlog.log_detail = printerlog.log_detail + "/" + "don't know the stauts:."
            printerlog.save(using='zenpos')
            print("don't know the stauts:")

        print(f"Received message on {msg.topic}: {msg.payload.decode()}")
        # Check the status of the print job
        if msg.topic == STATUS_TOPIC:
            status_message = msg.payload.decode()
            # Check for success or error in the status message
            if "success" in status_message:
                # Add printer log when request to print
                printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                printerlog.printer_printed = 1
                printerlog.log_detail = printerlog.log_detail + "/" + "Receipt printed successfully."
                printerlog.save(using='zenpos')
                print("Receipt printed successfully.")
            elif "error" in status_message:
                printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                printerlog.printer_printed = 2
                printerlog.log_detail = printerlog.log_detail + "/" + "Receipt printed successfully."
                printerlog.save(using='zenpos')
                print("Error printing receipt.")

    try:
        # publsh the manager to printer
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_OrderDinein_List where order_id = " + order_id)
        order_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDinein_List where order_id = " + order_id)
        order_item_dinein_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemDetail_List where order_id = " + order_id)
        order_item_detail_list = cursor.fetchall()
        cursor.execute("select * from V_Order_Cost_List where order_id = " + order_id)
        order_cost_list = cursor.fetchall()
        cursor.execute("select * from V_Invoice_List where order_id = " + order_id)
        order_payment_list = cursor.fetchall()
        cursor.execute("select * from V_OrderItemTotalItem_List where order_id = " + order_id)
        order_item_total_list = cursor.fetchall()

        if order_item_dinein_list:
            client = connect_mqtt()
            esc_comm = ESCPOSManager()
            #esc_comm.add_command(b"\x1B\x40")
            esc_comm.Prefix_command()
            esc_comm.set_alignment("center")
            esc_comm.add_command(b"\x1C\x26\x1B\x39\x01")
            esc_comm.set_font_size(128)
            esc_comm.add_command(b"\x1C\x70\x01")
            shop_name = " 福茶〈澳門〉 "
            esc_comm.print_text(shop_name + "\n")
            esc_comm.feed_lines(1)
            #esc_comm.set_alignment("center")
            #esc_comm.set_font_size(128)
            table = "單號："
            order_date = "訂單時間："
            staff = "負責職員："

            table_key = order_item_dinein_list[0].table_key
            order_key = str(order_dinein_list[0].order_date)[:19]
            staff_key = order_dinein_list[0].LoginNameDesc
            esc_comm.set_alignment("left")
            if print_type == "reprint":
                print_type_text = " (重印)"
            else:
                print_type_text = ""
            line = table + table_key + print_type_text
            esc_comm.print_text(line + "\n")

            esc_comm.set_font_size(13)
            line = order_date + order_key
            esc_comm.print_text(line + "\n")
            line = staff + staff_key
            esc_comm.print_text(line + "\n")

            # Create Printer Log Header
            printerlog = PrinterLogs()
            datetime_dt = datetime.datetime.today()
            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
            printerlog.printer_id = printer_id
            printerlog.order_id = order_id
            printerlog.order_item_id = 0
            printerlog.order_date = str(order_dinein_list[0].order_date)
            printerlog.table_key = table_key
            printerlog.print_type = print_type
            printerlog.log_title = "Receipt Printing - " + table_key
            printerlog.apps_sent = 1
            printerlog.location_code = location_code
            printerlog.sent_datetime = datetime_str
            printerlog.save(using='zenpos')
            printer_log_id = printerlog.printer_log_id

            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            printerlog.log_detail = esc_comm.heartbeat_check()
            printerlog.save(using='zenpos')

            esc_comm.feed_lines(1)
            esc_comm.set_font_size(13)
            space = "   "
            quantity = "數量"
            item = "項目"
            unit_price = "單價($)"
            selling_price = "金額($)"

            line = f"{quantity:<4}{space:<0}{item:<0}{space:<10}     {unit_price:>7}  {selling_price:<7}"
            esc_comm.print_text(line + "\n")
            esc_comm.print_text("----------------------------------------------" + "\n")
            esc_comm.set_alignment("left")
            max_product_name_length = max(len(item.product_name.encode('BIG5')) for item in order_item_dinein_list)
            max_quantity_length = max(len(str(item.quantity)) for item in order_item_dinein_list)
            for w in order_item_dinein_list:
                if w.order_item_type == 2:
                    takeaway = " ﹝外賣﹞"
                else:
                    takeaway = ""
                product_name = w.product_name + takeaway
                product_name_len = int(len(product_name.encode('BIG5')))
                product_name_space = abs(int(20 - len(product_name.encode('BIG5'))))
                quantity = str(w.quantity)
                order_item_date = w.order_item_date.strftime("%H:%M")
                unit_price = str(w.selling_price)
                selling_price = w.quantity * w.selling_price
                selling_price = str(selling_price)
                order_item_id = w.order_item_id

                line = f"{quantity:>3} {space:<2} {product_name:<0} {space:>{product_name_space}} {unit_price:>7}  {selling_price:>7}"
                esc_comm.print_text(line + "\n")
                for v in order_item_detail_list:
                    if v.order_item_id == order_item_id:
                        quantity_detail = ""
                        code_detail_name = "- " + v.code_detail_name
                        code_detail_name_len = int(len(code_detail_name.encode('BIG5')))
                        code_detail_name_space = abs(int(20 - len(code_detail_name.encode('BIG5'))))
                        unit_price = str(v.selling_price)
                        selling_price = str(w.quantity * v.selling_price)
                        line = f"{quantity_detail:<3} {space:<2} {code_detail_name:<0} {space:>{code_detail_name_space}} {unit_price:>7}  {selling_price:>7}"
                        esc_comm.print_text(line + "\n")
            esc_comm.print_text("----------------------------------------------" + "\n")
            sub_total = "小計($)"
            discount_total = "優惠($)"
            grand_total = "總計($)"
            sub_total_value = order_cost_list[0].total_cost_order
            discount_total_value = order_cost_list[0].total_cost_discount
            grand_total_value = order_cost_list[0].total_cost

            line = f"{sub_total:<10} {space:>24} {sub_total_value:>8}"
            esc_comm.print_text(line + "\n")
            line = f"{discount_total:<10} {space:>24} {discount_total_value:>8}"
            esc_comm.print_text(line + "\n")
            esc_comm.print_text("==============================================" + "\n")
            line = f"{grand_total:<10} {space:>24} {grand_total_value:>8}"
            esc_comm.print_text(line + "\n")

            esc_comm.feed_lines(1)

            for x in order_payment_list:
                esc_comm.set_font_size(13)
                payment_method_text = "付款方法   ："
                transaction_date_text = "交易日期   ："
                receivable_amount_text = "實收金額($)："
                change_amount_text = "找回金額($)："
                total_amount_text = "總計金額($)："
                remark_text = "訂單備註   ："
                payment_method = x.payment_method
                receivable_amount = x.receivable_amount
                change_amount = x.change_amount
                transaction_reference = x.transaction_reference
                transaction_date = x.transaction_date.strftime("%Y-%m-%d %H:%M")
                line = f"{payment_method_text:<1}{payment_method:<10}"
                esc_comm.print_text(line + "\n")
                line = f"{transaction_date_text:<1}{transaction_date:<20}"
                esc_comm.print_text(line + "\n")
                line = f"{receivable_amount_text:<1}{receivable_amount:>5}"
                esc_comm.print_text(line + "\n")
                if payment_method == "現金":
                    line = f"{change_amount_text:<1}{change_amount:>5}"
                    esc_comm.print_text(line + "\n")
                line = f"{total_amount_text:<1}{grand_total_value:>5}"
                esc_comm.print_text(line + "\n")
                if transaction_reference != "":
                    line = f"{remark_text:<1}{transaction_reference:<20}"
                    esc_comm.print_text(line + "\n")
            print_location_text = "列印位置   ："
            line = f"{print_location_text:<1}{printer_name:<10}"
            esc_comm.print_text(line + "\n")

            esc_comm.feed_lines(5)
            #esc_comm.add_command(b"\x1B\x6D")
            esc_comm.cut_paper()

            # Print Kitchen Ticket
            print_item_receipt_flag = "Y"
            print_item_label_flag = "Y"

            if print_item_receipt_flag == "Y" and print_item_label_flag == "N":
                esc_comm.set_font_size(13)
                esc_comm.set_alignment("left")
                for w in order_item_dinein_list:
                    esc_comm.set_font_size(3)
                    esc_comm.set_alignment("left")
                    table = "訂單單號："
                    order_date = "訂單時間："
                    table_key = order_item_dinein_list[0].table_key
                    order_key = w.order_item_date.strftime("%H:%M")
                    product_type = w.product_type

                    if product_type == "M":
                        esc_comm.set_font_size(13)
                        line = table + table_key
                        esc_comm.print_text(line + "\n")
                        line = order_date + order_key
                        esc_comm.print_text(line + "\n")

                        esc_comm.feed_lines(1)
                        space = " "
                        quantity = "數量"
                        item = "項目"
                        unit_price = "單價($)"
                        selling_price = "金額($)"
                        line = f"{quantity:<4}{space:<0}  {item:<0}{space:<10} {unit_price:>10}{space:<3}{selling_price:<10}"
                        esc_comm.print_text(line + "\n")
                        esc_comm.print_text("----------------------------------------------" + "\n")

                        product_name = w.product_name + takeaway
                        product_name_len = int(len(product_name.encode('BIG5')))
                        product_name_space = abs(int(18 - len(product_name.encode('BIG5'))))
                        quantity = str(w.quantity)
                        order_item_date = w.order_item_date.strftime("%H:%M")
                        unit_price = w.selling_price
                        selling_price = w.quantity * w.selling_price
                        selling_price = str(selling_price)
                        order_item_id = w.order_item_id

                        line = f"{quantity:>3} {space:<4} {product_name:<0} {space:>{product_name_space}} {unit_price:>7}  {selling_price:>7}"
                        esc_comm.print_text(line + "\n")
                        for v in order_item_detail_list:
                            if v.order_item_id == order_item_id:
                                quantity_detail = ""
                                code_detail_name = "- " + v.code_detail_name
                                code_detail_name_len = int(len(code_detail_name.encode('BIG5')))
                                code_detail_name_space = abs(int(18 - len(code_detail_name.encode('BIG5'))))
                                unit_price = v.selling_price
                                selling_price = v.selling_price
                                line = f"{quantity_detail:<3} {space:<4} {code_detail_name:<0} {space:>{code_detail_name_space}} {unit_price:>7}  {selling_price:>7}"
                                esc_comm.print_text(line + "\n")
                        esc_comm.feed_lines(5)
                        #esc_comm.add_command(b"\x1B\x6D")
                        esc_comm.cut_paper()

            if print_item_receipt_flag == "Y" and print_item_label_flag == "S":

                current_item = 0
                for w in order_item_dinein_list:
                    table_key = order_item_dinein_list[0].table_key
                    order_key = w.order_item_date.strftime("%H:%M")
                    product_type = w.product_type

                    if product_type == "M":
                        product_name = w.product_name
                        quantity = str(w.quantity)
                        order_item_date = w.order_item_date.strftime("%H:%M")
                        unit_price = w.selling_price
                        order_item_id = w.order_item_id
                        basic_counter = 0
                        more_counter = 0
                        basic_additional = ""
                        more_additional_1 = ""
                        more_additional_2 = ""
                        more_additional_3 = ""
                        more_additional_4 = ""
                        more_additional_5 = ""
                        more_additional_6 = ""

                        for v in order_item_detail_list:
                            if v.order_item_id == order_item_id:
                                if v.code_id == "11" or v.code_id == "12" or v.code_id == "15":
                                    basic_counter = basic_counter + 1
                                    if basic_counter == 1:
                                        basic_additional = "- " + v.code_detail_name
                                    else:
                                        basic_additional = basic_additional + " / " + v.code_detail_name
                                else:
                                    if v.code_detail_name != "第一份配料免費":
                                        more_counter = more_counter + 1
                                        if more_counter == 1: more_additional_1 = "- " + v.code_detail_name
                                        if more_counter == 2: more_additional_2 = "- " + v.code_detail_name
                                        if more_counter == 3: more_additional_3 = "- " + v.code_detail_name
                                        if more_counter == 4: more_additional_4 = "- " + v.code_detail_name
                                        if more_counter == 5: more_additional_5 = "- " + v.code_detail_name
                                        if more_counter == 6: more_additional_6 = "- " + v.code_detail_name

                        for y in range(w.quantity):
                            current_item = current_item + 1
                            total_item_text = str(current_item) + "/" + str(order_item_total_list[0].total_items)

                            line = f"單號：{table_key:<0}   時間：{order_key:<0}"
                            esc_comm.print_text(line + "\n")
                            line = f"{product_name:<0}"
                            esc_comm.print_text(line + "\n")
                            if basic_additional != "":
                                line = f"{basic_additional:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_1 != "":
                                line = f"{more_additional_1:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_2 != "":
                                line = f"{more_additional_2:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_3 != "":
                                line = f"{more_additional_3:<0}"
                                esc_comm.print_text(line + "\n")
                            if more_additional_4 != "":
                                line = f"{more_additional_4:<0}"
                                esc_comm.print_text(line + "\n")
                            if total_item_text != "":
                                line = f"                     {total_item_text:<0}"
                                esc_comm.print_text(line + "\n")
                            esc_comm.print_text("---------------------------" + "\n")

            esc_data = esc_comm.send_command()
            client.publish(topic, esc_data)

            # Add printer log when request to print
            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
            datetime_dt = datetime.datetime.today()
            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
            printerlog.printer_received = 1
            printerlog.received_datetime = datetime_str
            printerlog.save(using='zenpos')

            PRINT_TOPIC = 'printer/print'
            STATUS_TOPIC = 'printer/status'

            client.on_message = on_message
            client.subscribe(STATUS_TOPIC)

            client.disconnect()

            if print_item_receipt_flag == "Y" and print_item_label_flag == "Y":

                location_code = getattr(settings, "LABEL_LOCATION_CODE", None)
                printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

                if printer_list:
                    topic_2 = printer_list[0].printer_client_id
                    printer_id = printer_list[0].printer_id
                    printer_name = printer_list[0].printer_name

                client_2 = connect_mqtt()
                esc_comm_2 = ESCPOSManager()

                current_item = 0
                for w in order_item_dinein_list:
                    table_key = order_item_dinein_list[0].table_key
                    order_key = w.order_item_date.strftime("%H:%M")
                    product_type = w.product_type

                    if product_type == "M":
                        product_name = w.product_name
                        quantity = str(w.quantity)
                        order_item_date = w.order_item_date.strftime("%H:%M")
                        unit_price = w.selling_price
                        order_item_id = w.order_item_id
                        basic_counter = 0
                        more_counter = 0
                        basic_additional = ""
                        more_additional_1 = ""
                        more_additional_2 = ""
                        more_additional_3 = ""
                        more_additional_4 = ""
                        more_additional_5 = ""
                        more_additional_6 = ""

                        for v in order_item_detail_list:
                            if v.order_item_id == order_item_id:
                                if v.code_id == "11" or v.code_id == "12" or v.code_id == "15":
                                    basic_counter = basic_counter + 1
                                    if basic_counter == 1:
                                        basic_additional = "- " + v.code_detail_name
                                    else:
                                        basic_additional = basic_additional + " / " + v.code_detail_name
                                else:
                                    if v.code_detail_name != "第一份配料免費":
                                        more_counter = more_counter + 1
                                        if more_counter == 1: more_additional_1 = "- " + v.code_detail_name
                                        if more_counter == 2: more_additional_2 = "- " + v.code_detail_name
                                        if more_counter == 3: more_additional_3 = "- " + v.code_detail_name
                                        if more_counter == 4: more_additional_4 = "- " + v.code_detail_name
                                        if more_counter == 5: more_additional_5 = "- " + v.code_detail_name
                                        if more_counter == 6: more_additional_6 = "- " + v.code_detail_name

                        for y in range(w.quantity):
                            current_item = current_item + 1
                            # Create Printer Log Header
                            printerlog = PrinterLogs()
                            table_key = order_item_dinein_list[0].table_key
                            order_key = str(order_dinein_list[0].order_date)[:19]
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            datetime_time_str = datetime_dt.strftime("%H:%M")
                            printerlog.printer_id = printer_id
                            printerlog.order_id = order_id
                            printerlog.order_item_id = order_item_id
                            printerlog.order_date = str(order_dinein_list[0].order_date)
                            printerlog.table_key = table_key
                            printerlog.print_type = print_type
                            printerlog.log_title = "Label Printing - " + table_key + " - " + product_name
                            printerlog.apps_sent = 1
                            printerlog.location_code = location_code
                            printerlog.sent_datetime = datetime_str
                            printerlog.save(using='zenpos')
                            printer_log_id = printerlog.printer_log_id

                            total_item_text = str(current_item) + "/" + str(order_item_total_list[0].total_items)
                            # TSPL commands
                            tspl_command = f"""
                                SIZE 40 mm, 30 mm
                                GAP 2 mm, 0 mm
                                CLS
                                DIRECTION 1
                                TEXT 20, 10, "TSS24.BF2", 0, 1.5, 1.5, "單號：{table_key} 時間：{datetime_time_str}"
                                TEXT 20, 40, "TSS24.BF2", 0, 1.5, 1.5, "{product_name}"
                                TEXT 20, 70, "TSS24.BF2", 0, 1.5, 1.5, "{basic_additional}"
                                TEXT 20, 100, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_1}"
                                TEXT 20, 130, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_2}"
                                TEXT 20, 160, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_3}"
                                TEXT 20, 190, "TSS24.BF2", 0, 1.5, 1.5, "{more_additional_4}"
                                PRINT 1, 1
                            """
                            #print(tspl_command)
                            #client_2.publish(topic_2, tspl_command)
                            # ZPL commands
                            #^PW192
                            #^LL272
                            #^PW240
                            #^LL320
                            zpl_command = """
                            ^XA
                            ^MNY
                            ^XZ
                            """
                            client_2.publish(topic_2, zpl_command)

                            zpl_command = f"""
                            ^XA
                            ^PQ1
                            ^PR2,0
                            ^CI28
                            ^PW240
                            ^LL320
                            ^FO00,00^A0N,25,25^FD單號：{table_key}    時間：{datetime_time_str}^FS
                            ^FO00,30^A0N,25,25^FD{product_name}^FS
                            ^FO00,60^A0N,25,25^FD{basic_additional}^FS
                            ^FO00,90^A0N,25,25^FD{more_additional_1}^FS
                            ^FO00,120^A0N,25,25^FD{more_additional_2}^FS
                            ^FO00,150^A0N,25,25^FD{more_additional_3}^FS
                            ^FO00,180^A0N,25,25^FD{more_additional_4}^FS
                            ^FO240,180^A0N,25,25^FD{total_item_text}^FS
                            ^XZ
                            """
                            #print(zpl_command)
                            client_2.publish(topic_2, zpl_command)

                            printerlog = PrinterLogs.objects.using('zenpos').get(printer_log_id=printer_log_id)
                            printerlog.log_detail = esc_comm_2.heartbeat_check()
                            datetime_dt = datetime.datetime.today()
                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                            printerlog.printer_received = 1
                            printerlog.received_datetime = datetime_str
                            printerlog.save(using='zenpos')
                            #esc_data_2 = esc_comm_2.send_command()
                            #client_2.publish(topic_2, esc_data_2)
                            #print(tspl_command)
                            #client_2.publish(topic_2, tspl_command)
                client_2.disconnect()
            return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs

def printOrderItemCost(request, order_id):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = "Z"
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
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

    try:
        # publsh the manager to printer
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=zenpos')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_OrderItemDinein_List where order_id = " + order_id)
        order_item_dinein_list = cursor.fetchall()

        item1 = "原隻笋尖鮮"
        quantity1 = 1
        price1 = "$18.00"

        item2 = "沙爆魚肚醬香鳳爪"+order_id
        quantity2 = 2
        price2 = "$36.00"

        line1 = f"{item1:<26}{quantity1:<8}{price1:<8}"
        line2 = f"{item2:<26}{quantity2:<8}{price2:<8}"

        if order_item_dinein_list:
            table_key = order_item_dinein_list[0].table_key
            client = connect_mqtt()
            esc_comm = ESCPOSManager()
            esc_comm.Prefix_command()  #
            esc_comm.set_alignment("left")
            esc_comm.set_font_size(3)
            esc_comm.print_text(table_key + "\n")
            esc_comm.feed_lines(1)
            esc_comm.set_alignment("center")
            esc_comm.set_font_size(128)
            esc_comm.print_text(shop_name + "\n")
            esc_comm.feed_lines(1)
            esc_comm.set_alignment("left")
            esc_comm.set_font_size(9)
            esc_comm.print_text("地址：" + shop_address + "\n")
            esc_comm.print_text("電話：" + phone_area_code + " " + phone_number + "\n")
            esc_comm.set_font_size(13)
            esc_comm.print_text("------------------------------------------------" + "\n")
            for w in order_item_dinein_list:
                if w.order_item_type == 2:
                    takeaway = " [外賣]"
                else:
                    takeaway = ""
                product_name = w.product_name + takeaway
                quantity = w.quantity
                selling_price = w.quantity * w.selling_price
                selling_price = "$" + str(selling_price)
                line = f"{product_name:<25}{quantity:>5}{selling_price:>10}"
                esc_comm.print_text(line+"\n")
            esc_comm.print_text("------------------------------------------------" + "\n")
            #esc_comm.print_text(line1 + "\n")
            #esc_comm.print_text(line2 + "\n")
            #esc_comm.cut_paper2()
            #esc_comm.feed_lines(1)
            esc_comm.set_alignment("left")
            # esc_comm.print_qr_code("www.hsprinter.com\n")
            esc_comm.cut_paper()
            esc_data = esc_comm.send_command()
            client.publish(topic, esc_data)
            client.disconnect()
            return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs

def printOrderItem(request, location_code, table_key, order_number, product_name, quantity, order_item_type):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = "Z"
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)
    if printer_list:
        topic = printer_list[0].printer_client_id
    table_name = table_key

    # MQTT SERVER Configuration
    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = ""
    qos = 1

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
        esc_comm.set_alignment("right")
        esc_comm.print_text("#"+order_number+"\n")
        esc_comm.feed_lines(1)
        esc_comm.set_alignment("left")
        esc_comm.set_font_size(128)
        esc_comm.print_text(product_name+"\n")
        esc_comm.set_alignment("right")
        esc_comm.print_text(quantity+"\n")
        esc_comm.feed_lines(1)
        esc_comm.set_alignment("left")
        esc_comm.feed_lines(1)
        # esc_comm.print_qr_code("www.hsprinter.com\n")
        esc_data = esc_comm.send_command()
        client.publish(topic, esc_data)
        client.disconnect()
        return "Print Success"  # Return success message
    except Exception as e:
        return "Error printing: " + str(e)  # Return error message if an exception occurs

def printOrder(request):
    if not request.session.get('username'): return redirect('login')
    shop_list = Shops.objects.using('zenpos').filter(status=1)
    shop_name = shop_list[0].shop_name
    shop_address = shop_list[0].shop_address
    phone_area_code = shop_list[0].phone_area_code
    phone_number = shop_list[0].phone_number
    location_code = "Z"
    printer_list = Printer.objects.using('zenpos').filter(status=1).filter(location_code=location_code)

    if printer_list:
        topic = printer_list[0].printer_client_id
    table_name = "M8"

    broker_address = getattr(settings, "BROKER_ADDRESS", None)  # mqtt address
    port = getattr(settings, "BROKER_PORT", None)  # mqtt port
    username = getattr(settings, "BROKER_USERNAME", None)
    password = getattr(settings, "BROKER_PASSWORD", None)
    client_id = ""
    qos = 1

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

def getOrderNumber():
    try:
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d")
        if not OrderNumbers.objects.using('zenpos').filter(order_number_date=datetime_str).exists():
            ordernumber = OrderNumbers()
            ordernumber.order_number_date = datetime_str
            ordernumber.order_counter = 1
            ordernumber.order_number = str(ordernumber.order_counter).zfill(3)
            order_number = ordernumber.order_number
            ordernumber.save(using='zenpos')
        else:
            ordernumber = OrderNumbers.objects.using('zenpos').get(order_number_date=datetime_str)
            ordernumber.order_counter = ordernumber.order_counter + 1
            ordernumber.order_number = str(ordernumber.order_counter).zfill(3)
            order_number = ordernumber.order_number
            ordernumber.save(using='zenpos')
        return order_number
    except Exception as e:
        return JsonResponse({'message': 'Update record failed. Error: {}'.format(str(e))}, status=500)

def pageviewlog(accessid, loginid, username, username_org):
    pageview = PageView()
    pageview.loginid = loginid
    pageview.username = username
    pageview.logdatetime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    pageview.subcatid = accessid
    subcategory = SubCategories.objects.using('zensystem').get(subcatid=accessid)
    pageview.pagename = subcategory.subcatname
    if username != username_org and username_org != "":
        pageview.logintype = "Demo"
    else:
        pageview.logintype = "Live"
    pageview.save(using='zensystem')

def hash_password(password):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Convert the password to bytes and hash it
    sha256_hash.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = sha256_hash.hexdigest()

    return hashed_password