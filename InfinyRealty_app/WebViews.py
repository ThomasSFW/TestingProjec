from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db.backends import utils
from django.core import serializers
from django.db import connections
from datetime import date, timedelta
from django.db.models import Max
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from django_q.tasks import schedule
import json
import pyodbc
import requests
import datetime
import os
import sys
import hashlib
import random
import string
import urllib.parse

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks, MortgageRefers
from InfinyRealty_app.models import PageView, CodeDetails, ContentDetails, Members, MemberPropertys, Propertys, \
    PropertyFiles, PropertyForeigns, PropertyForeignFiles, Entrusts, Enquirys, VisitTour, VisitTourForm, Interests, \
    TransactionRecords, PropertyListings

from django.conf import settings


def main(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    VacancyList = ContentDetails.objects.using('infinyrealty').filter(content_id=6)
    RentIndexList = ContentDetails.objects.using('infinyrealty').filter(content_id=7)

    WebText = CodeDetails.objects.using('infinyrealty').filter(code_id=13).filter(code_key='MainPage')
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_District_Count")
    district_count_list = cursor.fetchall()
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_SubDistrict_Count")
    subdistrict_count_list = cursor.fetchall()

    request.session['currentpage'] = "main"

    context = {
        "usagelist": UsageList,
        "vacancylist": VacancyList,
        "rentindexlist": RentIndexList,
        "webtext": WebText,
        "district_count_list": district_count_list,
        "subdistrict_count_list": subdistrict_count_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/main.html", context)


@csrf_exempt
def main_response(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.POST.get('loginid')
    today = datetime.datetime.now()
    if action == "change_lang_tc":
        request.session['lang'] = "tc"
        return HttpResponse("Success")
    if action == "change_lang_sc":
        request.session['lang'] = "sc"
        return HttpResponse("Success")
    if action == "change_lang_en":
        request.session['lang'] = "en"
        return HttpResponse("Success")
    if action == "recommend_view":
        usage = request.POST.get('usage')
        offertype = request.POST.get('offertype')
        display = request.POST.get('display')
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None: usage = ""
        if offertype is None: offertype = ""
        if offertype == "":
            displaytype = "recommend"
        else:
            if offertype == "放租":
                displaytype = "rent"
            else:
                displaytype = "sell"

        sql = "exec spPropertyHighlight N'" + usage + "', '" + displaytype + "'"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "property_view_list": property_view_list,
            "display": display,
            "sql": sql,
        }
    if action == "recommend_rent":
        usage = request.POST.get('usage')
        display = request.POST.get('display')
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None: usage == ""
        sql = "exec spPropertyHighlight N'" + usage + "', 'rent'"
        cursor.execute(sql)
        property_rent_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "property_rent_view_list": property_rent_view_list,
            "display": display,
            "sql": sql,
        }
    if action == "index_view":
        usage = request.POST.get('usage')
        display = request.POST.get('display')
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_District_Count where Usage = N'" + usage + "' and District <> ''")
        district_count_list = cursor.fetchall()
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_SubDistrict_Count where Usage = N'" + usage + "' and District <> ''")
        subdistrict_count_list = cursor.fetchall()

        context = {
            "action": action,
            "district_count_list": district_count_list,
            "subdistrict_count_list": subdistrict_count_list,
            "display": display,
        }
    if action == "transaction_record":
        usage = request.POST.get('usage')
        display = request.POST.get('display')
        transaction_record_list = TransactionRecords.objects.using('infinyrealty').filter(usage=usage).filter(
            lang=request.session.get('lang')).order_by('-transactiondate')[:10]

        context = {
            "action": action,
            "transaction_record_list": transaction_record_list,
            "display": display,
        }
    if action == "transaction_page":
        usage = request.POST.get('usage')
        display = request.POST.get('display')
        transaction_record_list = TransactionRecords.objects.using('infinyrealty').filter(usage=usage).filter(
            lang=request.session.get('lang')).order_by('-transactiondate')[:5000]

        context = {
            "action": action,
            "transaction_record_list": transaction_record_list,
            "display": display,
        }
    if action == "property_recommend":
        usage = request.POST.get('usage')
        propertyid = request.POST.get('propertyid')
        usage_list = CodeDetails.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,
                                                                                isapprove=1).order_by('-ismain')

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "newproperty_view":
        usage = request.POST.get('usage')
        offertype = request.POST.get('offertype')
        area = request.POST.get('area')
        dname = request.POST.get('dname')
        pricemin = request.POST.get('pricemin')
        pricemax = request.POST.get('pricemax')
        if dname == "" or dname is None:
            dname = ""
        if pricemin == "" or pricemin is None:
            pricemin = 0
        if pricemax == "" or pricemax is None:
            pricemax = 0
        display = request.POST.get('display')
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if area is None: area = ""
        if dname is None: dname = ""
        if usage is None: usage = ""
        if offertype is None: offertype = ""
        if offertype == "":
            displaytype = "newproperty"
        else:
            if offertype == "放租":
                displaytype = "rent"
            else:
                displaytype = "sell"

        # sql = "exec spNewProperty N'" + area + "',N'" + dname + "','" + str(pricemin) + "','" + str(pricemax) + "'"
        sql = "exec spNewProperty N'" + area + "',N'" + dname + "','" + str(pricemin) + "','" + str(pricemax) + "'"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "property_view_list": property_view_list,
            "display": display,
            "sql": sql,
        }
    if action == "display_mode":
        viewtype = request.POST.get('viewtype')
        request.session['display_mode'] = viewtype
        return HttpResponse("Success")
    if action == "sorting_mode":
        sortingtype = request.POST.get('sortingtype')
        request.session['sorting_mode'] = sortingtype
        return HttpResponse("Success")
    if action == "search":
        search_propertyname = request.POST.get('propertyname')
        search_propertyno = request.POST.get('propertyno')
        search_have_value = request.POST.get('have_value')
        search_usage = request.POST.get('usage')
        search_areacode = request.POST.get('areacode')
        search_offertype = request.POST.get('offertype')
        price_min = request.POST.get('price_min')
        price_max = request.POST.get('price_max')
        unitprice_min = request.POST.get('unitprice_min')
        unitprice_max = request.POST.get('unitprice_max')
        area_min = request.POST.get('area_min')
        area_max = request.POST.get('area_max')
        request.session['search_propertyname'] = search_propertyname
        request.session['search_propertyno'] = search_propertyno
        request.session['search_have_value'] = search_have_value
        request.session['search_usage'] = search_usage
        request.session['search_areacode'] = search_areacode
        request.session['search_offertype'] = search_offertype
        request.session['price_min'] = price_min
        request.session['price_max'] = price_max
        request.session['unitprice_min'] = unitprice_min
        request.session['unitprice_max'] = unitprice_max
        request.session['area_min'] = area_min
        request.session['area_max'] = area_max
        return HttpResponse("Success")
    if action == "search_foreign":
        search_projectname = request.POST.get('projectname')
        search_propertyno = request.POST.get('propertyno')
        search_have_value = request.POST.get('have_value')
        search_usage = request.POST.get('usage')
        search_country = request.POST.get('country')
        search_areacode = request.POST.get('areacode')
        search_offertype = request.POST.get('offertype')
        price_min = request.POST.get('price_min')
        price_max = request.POST.get('price_max')
        unitprice_min = request.POST.get('unitprice_min')
        unitprice_max = request.POST.get('unitprice_max')
        area_min = request.POST.get('area_min')
        area_max = request.POST.get('area_max')
        if search_projectname is None or search_projectname == 'None':
            search_projectname = ""
        if search_country is None or search_country == 'None':
            search_country = ""
        request.session['search_projectname'] = search_projectname
        request.session['search_propertyno'] = search_propertyno
        request.session['search_have_value'] = search_have_value
        request.session['search_usage'] = search_usage
        request.session['search_country'] = search_country
        request.session['search_areacode'] = search_areacode
        request.session['search_offertype'] = search_offertype
        request.session['price_min'] = price_min
        request.session['price_max'] = price_max
        request.session['unitprice_min'] = unitprice_min
        request.session['unitprice_max'] = unitprice_max
        request.session['area_min'] = area_min
        request.session['area_max'] = area_max
        return HttpResponse("Success")
    return render(request, "web_template/main_response.html", context)


def common(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 45
    request.session['accessid'] = accessid
    # users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    # users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    # users.save(using='infinyrealty')
    # pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_team": team,
        "usagelist": UsageList,
    }
    return render(request, "web_template/common.html", context)


def about(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)
    memberid = request.session.get('memberid')

    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=1).order_by('sequence')

    request.session['currentpage'] = "about"

    context = {
        "user_memberid": memberid,
        "content_detail": content_detail,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/about.html", context)


def terms(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)
    memberid = request.session.get('memberid')

    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=2).order_by('sequence')

    accessid = 5159
    request.session['accessid'] = accessid
    # users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    # users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    # users.save(using='infinyrealty')
    # pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_memberid": memberid,
        "content_detail": content_detail,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/terms.html", context)


def news(request, date_id=None):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)
    memberid = request.session.get('memberid')
    select_date = date_id
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # if select_date is None:
    #    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=5).order_by('-create_date').order_by('sequence')
    # else:
    #    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=5, create_date__date=select_date).order_by('-create_date').order_by('sequence')
    # cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
    # cursor = cnxn.cursor()
    # cursor.execute("select * from V_Usage_count")
    # usage_view_list = cursor.fetchall()

    request.session['currentpage'] = "news"

    context = {
        "user_memberid": memberid,
        "favorites_cookies": favorites_cookies,
        "select_date": select_date,
    }
    return render(request, "web_template/news.html", context)


def news_detail(request, news_id):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)
    memberid = request.session.get('memberid')

    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=5).filter(
        content_detail_id=news_id).order_by('sequence')
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_Usage_count")
    usage_view_list = cursor.fetchall()

    request.session['currentpage'] = "news"
    context = {
        "user_memberid": memberid,
        "content_detail": content_detail,
        "usage_view_list": usage_view_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/news_detail.html", context)


@csrf_exempt
def news_response(request, date_id=None):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    select_date = date_id
    action = request.POST.get('action')
    news_content = request.POST.get('news_content')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    # start_date = "08/09/2024"
    # end_date = "12/09/2024"
    # date_object = datetime.strptime(start_date, "%d/%m/%Y")
    # formatted_start_date = date_object.strftime("%Y-%m-%d")
    # date_object = datetime.strptime(end_date, "%d/%m/%Y")
    # formatted_end_date = date_object.strftime("%Y-%m-%d")

    # if select_date is None:
    #    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=5).order_by('-create_date').order_by('sequence')
    # else:
    if action == "news_list":
        if news_content:
            content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=5,
                                                                                 create_date__date__range=[start_date,
                                                                                                           end_date]).order_by(
                '-create_date', 'sequence')
            filtered_content_detail = [u for u in content_detail if news_content in u.content_detail_title]
            content_detail = filtered_content_detail

        else:
            content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=5,
                                                                                 create_date__date__range=[start_date,
                                                                                                           end_date]).order_by(
                '-create_date', 'sequence')

        request.session['currentpage'] = "news"

        context = {
            "action": action,
            "content_detail": content_detail,
            "select_date": select_date,
            "start_date": start_date,
            "end_date": end_date,
        }
    if action == "news_content":
        # if not request.session.get('username'): return redirect('login')
        favorites_cookies = getcookielist(request)
        memberid = request.session.get('memberid')
        news_id = request.POST.get('news_id')

        content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=5).filter(
            content_detail_id=news_id).order_by('sequence')

        request.session['currentpage'] = "news"
        context = {
            "action": action,
            "user_memberid": memberid,
            "content_detail": content_detail,
            "favorites_cookies": favorites_cookies,
        }
    return render(request, "web_template/news_response.html", context)


def disclaimer(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)
    memberid = request.session.get('memberid')

    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=3).order_by('sequence')

    request.session['currentpage'] = "disclaimer"
    context = {
        "user_memberid": memberid,
        "content_detail": content_detail,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/disclaimer.html", context)


def privacy(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)
    memberid = request.session.get('memberid')

    content_detail = ContentDetails.objects.using('infinyrealty').filter(content_id=4).order_by('sequence')

    request.session['currentpage'] = "privacy"
    context = {
        "user_memberid": memberid,
        "content_detail": content_detail,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/privacy.html", context)


def account(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    request.session['currentpage'] = "account"
    context = {
        "user_loginid": loginid,
        "user_team": team,
        "usagelist": UsageList,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/account.html", context)


@csrf_exempt
def account_save(request):
    # if not request.session.get('loginid'): return redirect('login')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    username = request.POST.get('username')
    password = request.POST.get('password')

    action = str(request.POST.get('action'))
    if action == "register":
        member_name = request.POST.get('member_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        area_code = request.POST.get('area_code')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        try:
            member = Members.objects.using('infinyrealty').filter(username=username)
            if member:
                return HttpResponse("Username exist")
            else:
                member = Members.objects.using('infinyrealty').filter(phone_number=phone_number)
                if member:
                    return HttpResponse("Phone Number exist")
                else:
                    member = Members()
                    member.member_number = area_code.replace("+", "") + phone_number
                    member.member_name = member_name
                    member.username = username
                    hashed_password = hash_password(password)
                    member.password = hashed_password
                    member.phone_area_code = area_code
                    member.phone_number = phone_number
                    member.email = email
                    member.join_date = datetime_str
                    member.modify_date = datetime_str
                    member.lastlogin_date = datetime_str
                    member.status = 1
                    member.save(using='infinyrealty')
                    request.session['member_id'] = member.member_id
                    request.session['member_username'] = member_name

                    # smtp_email = "cs@infiny.group"
                    # smtp_password = "Infinywebsite2024"
                    # sender_email = "member@infiny.group"
                    # recipient_email = email
                    # subject = "InfinyRealty.com 會員"
                    # message = "This is an HTML email sent using smtplib and Outlook."

                    # send_email(smtp_email, smtp_password, sender_email, recipient_email, subject, message)

                    # return HttpResponse("Success")
                    subject = f'InfinyRealty 會員註冊 - {member_name}'
                    full_phone_number = area_code + phone_number
                    message_body = f'''
尊敬的團隊，

新用戶註冊通知：

姓名: {member_name}
電子郵件: {email}
註冊日期： {datetime_str}

請登入Infinyrealty管理平台查看和管理新用戶帳戶。

'''

                    to_email = 'cs@infiny.group'

                    try:
                        send_mail(
                            subject,
                            message_body,
                            settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                            [to_email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

                    message_body = f'''
尊敬的 {member_name}，

感謝您註冊 Infinyrealty.com！我們很高興地通知您，您的帳戶已成功建立。

您的註冊信息如下：

姓名： {member_name}
電子郵件： {email}
註冊日期： {datetime_str}
您現在可以登入我們的網站，享受各種服務和功能。請使用以下鏈接訪問您的帳戶：

https://infinyrealty.com/account/

如果您有任何問題或需要進一步的協助，請隨時聯絡我們的客服團隊。

再次感謝您的註冊，期待為您提供優質的服務！

Infinyrealty 團隊
'''
                    to_email = email

                    try:
                        send_mail(
                            subject,
                            message_body,
                            settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                            [to_email],
                            fail_silently=False,
                        )
                    except Exception as e:
                        return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

                    return HttpResponse('Success')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "login":
        try:
            member = Members.objects.using('infinyrealty').get(username=username)
            hashed_password = hash_password(password)
            if member:
                if member.password == hashed_password:
                    member.lastlogin_date = datetime_str
                    member.save(using='infinyrealty')
                    request.session['member_username'] = username
                    request.session['member_id'] = member.member_id
                    return HttpResponse("Success")
                else:
                    return HttpResponse("Wrong Password")
            else:
                return HttpResponse("Wrong Username")
        except Exception as e:
            return HttpResponse("Wrong Username")
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)


def send_email(smtp_email, smtp_password, sender_email, recipient_email, subject, message):
    # Create a multipart message object
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Create both plain text and HTML versions of the email
    text = 'This is a plain text email.'
    html = f'<html><body><>{message}</h1></body></html>'

    # Attach the plain text and HTML versions to the email
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # SMTP server settings for Outlook
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587

    try:
        # Create a secure SSL/TLS connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to your Outlook email account
        server.login(smtp_email, smtp_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Email sent successfully!")

    except smtplib.SMTPException as e:
        print("Error sending email:", str(e))

    finally:
        # Close the connection to the SMTP server
        server.quit()


def entrust(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    request.session['currentpage'] = "entrust"

    context = {
        "usagelist": UsageList,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/entrust.html", context)


@csrf_exempt
def entrust_save(request):
    # if not request.session.get('loginid'): return redirect('login')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

    action = str(request.POST.get('action'))
    if action == "entrust":
        contact_name = request.POST.get('contact_name')
        email = request.POST.get('email')
        phone_area_code = request.POST.get('phone_area_code')
        phone_number = request.POST.get('phone_number')
        contact_period = request.POST.get('contact_period')
        contact_period_other = request.POST.get('contact_period_other')
        property_address_1 = request.POST.get('property_address_1')
        offer_type_1 = request.POST.get('offer_type_1')
        usage_1 = request.POST.get('usage_1')
        netarea_1 = request.POST.get('netarea_1')
        rent_1 = request.POST.get('rent_1')
        selling_1 = request.POST.get('selling_1')
        property_address_2 = request.POST.get('property_address_2')
        offer_type_2 = request.POST.get('offer_type_2')
        usage_2 = request.POST.get('usage_2')
        netarea_2 = request.POST.get('netarea_2')
        rent_2 = request.POST.get('rent_2')
        selling_2 = request.POST.get('selling_2')
        remarks = request.POST.get('remarks')

        try:
            entrust = Entrusts()
            entrust.contact_name = contact_name
            entrust.email = email
            entrust.phone_area_code = phone_area_code
            entrust.phone_number = phone_number
            entrust.contact_period = contact_period
            entrust.contact_period_other = contact_period_other
            entrust.property_address_1 = property_address_1
            entrust.offer_type_1 = offer_type_1
            entrust.usage_1 = usage_1
            if netarea_1 is not None and netarea_1: entrust.netarea_1 = netarea_1
            if rent_1 is not None and rent_1: entrust.rent_1 = rent_1
            if selling_1 is not None and selling_1: entrust.selling_1 = selling_1
            entrust.offer_type_2 = offer_type_2
            entrust.usage_2 = usage_2
            if netarea_2 is not None and netarea_2: entrust.netarea_2 = netarea_2
            if rent_2 is not None and rent_2: entrust.rent_2 = rent_2
            if selling_2 is not None and selling_2: entrust.selling_2 = selling_2
            entrust.remarks = remarks
            entrust.create_date = datetime_str
            entrust.modify_date = datetime_str
            entrust.status = 0
            entrust.save(using='infinyrealty')

            subject = f'InfinyRealty 網上委託'
            full_phone_number = phone_area_code + phone_number
            message_body = f'''
有新的網上委託請求：

聯繫人姓名: {contact_name}
電子郵件: {email}
電話: {full_phone_number}
委託請求日期： {datetime_str}
聯繫時段: {contact_period}

物業信息 1:
地址: {property_address_1}
報價類型: {offer_type_1}
用途: {usage_1}

物業信息 2:
地址: {property_address_2}
報價類型: {offer_type_2}
用途: {usage_2}

備註: {remarks}

'''

            to_email = 'cs@infiny.group'

            try:
                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                    [to_email],
                    fail_silently=False,
                )
            except Exception as e:
                return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

            message_body = f'''
尊敬的客戶，

我們很高興通知您，您有一個新的網上委託請求。我們的團隊將會儘快處理您的請求。以下是相關的詳細信息：

聯繫人姓名: {contact_name}
電子郵件: {email}
電話: {full_phone_number}
委託請求日期： {datetime_str}
聯繫時段: {contact_period}
物業信息 1:
地址: {property_address_1}
報價類型: {offer_type_1}
用途: {usage_1}
物業信息 2:
地址: {property_address_2}
報價類型: {offer_type_2}
用途: {usage_2}
備註: {remarks}

感謝您選擇 Infinyrealty。我們期待著為您提供優質的服務。如有任何疑問或需要進一步的幫助，請隨時聯絡我們。

Infinyrealty 團隊
'''
            to_email = email

            try:
                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                    [to_email],
                    fail_silently=False,
                )
            except Exception as e:
                return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)


def newproperty(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    favorites_cookies = getcookielist(request)

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    cursor.execute("select * from V_District_Count")
    district_count_list = cursor.fetchall()

    request.session['currentpage'] = "newproperty"

    context = {
        "usagelist": UsageList,
        "district_count_list": district_count_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/newproperty.html", context)


def oversea(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    UsageForeignList = CodeDetails.objects.using('infinyrealty').filter(code_id=9, status=1).order_by('sequence')
    CountryList = CodeDetails.objects.using('infinyrealty').filter(code_id=8, status=1).order_by('sequence')

    request.session['currentpage'] = "oversea"

    context = {
        "usageforeignlist": UsageForeignList,
        "countrylist": CountryList,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/oversea.html", context)


def mortgage(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)

    request.session['currentpage'] = "mortgage"

    context = {
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/mortgage.html", context)


@csrf_exempt
def mortgage_response(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('member_username'): return redirect('login')
    action = request.POST.get('action')
    member_username = request.session.get('member_username')
    today = datetime.datetime.now()

    if action == "service":
        member = Members.objects.using('infinyrealty').filter(username=member_username)
        if member:
            member_id = member[0].member_id

        context = {
            "action": action,
            "member": member,
        }
    if action == "interest":
        member = Members.objects.using('infinyrealty').filter(username=member_username)
        interest_list = Interests.objects.using('infinyrealty').filter(status=1)

        url = "https://www.centamortgage.com/mortgage-plan/API-bank"
        response = requests.get(url)
        # 使用 BeautifulSoup 解析網頁內容
        soup = BeautifulSoup(response.content, "html.parser")
        div_elements = soup.find_all("div", class_="el-card box-card is-always-shadow")
        # 輸出每個 div 元素的內容
        webpage_content = ""
        for div in div_elements:
            for a_tag in div.find_all("a", class_="btn_togo_s"):
                a_tag.decompose()
        for div in div_elements:
            webpage_content = webpage_content + div.prettify()

        # 獲取整個網頁的HTML內容
        # webpage_content = soup.prettify()

        if member:
            member_id = member[0].member_id

        context = {
            "action": action,
            "member": member,
            "interest_list": interest_list,
            "webpage_content": webpage_content,
        }
    if action == "calculator":
        member = Members.objects.using('infinyrealty').filter(username=member_username)
        interest_list = Interests.objects.using('infinyrealty').filter(status=1)
        if member:
            member_id = member[0].member_id

        context = {
            "action": action,
            "member": member,
            "interest_list": interest_list,
        }
    if action == "transfer":
        member = Members.objects.using('infinyrealty').filter(username=member_username)
        if member:
            member_id = member[0].member_id

        context = {
            "action": action,
            "member": member,
        }
    return render(request, "web_template/mortgage_response.html", context)


@csrf_exempt
def mortgage_save(request):
    # if not request.session.get('loginid'): return redirect('login')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

    action = str(request.POST.get('action'))
    if action == "apply":
        english_name = request.POST.get('english_name')
        title = request.POST.get('title')
        email = request.POST.get('email')
        phone_area_code = request.POST.get('phone_area_code')
        phone_number = request.POST.get('phone_number')
        id_type = request.POST.get('id_type')
        id_number = request.POST.get('id_number')
        english_name_2 = request.POST.get('english_name_2')
        title_2 = request.POST.get('title_2')
        email_2 = request.POST.get('email_2')
        phone_area_code_2 = request.POST.get('phone_area_code_2')
        phone_number_2 = request.POST.get('phone_number_2')
        id_type_2 = request.POST.get('id_type_2')
        id_number_2 = request.POST.get('id_number_2')
        unit = request.POST.get('unit')
        floor = request.POST.get('floor')
        block = request.POST.get('block')
        building = request.POST.get('building')
        street = request.POST.get('street')
        area = request.POST.get('area')
        district = request.POST.get('district')
        loan_purpose = request.POST.get('loan_purpose')
        purchase_price = request.POST.get('purchase_price')
        drawdown_date = request.POST.get('drawdown_date')
        referral = request.POST.get('referral')
        referral_name = request.POST.get('referral_name')
        referral_phone_number = request.POST.get('referral_phone_number')

        try:
            mortgagerefer = MortgageRefers()
            mortgagerefer.english_name = english_name
            mortgagerefer.title = title
            mortgagerefer.email = email
            mortgagerefer.phone_area_code = phone_area_code
            mortgagerefer.phone_number = phone_number
            mortgagerefer.id_type = id_type
            mortgagerefer.id_number = id_number
            mortgagerefer.english_name_2 = english_name_2
            mortgagerefer.title_2 = title_2
            mortgagerefer.email_2 = email_2
            mortgagerefer.phone_area_code_2 = phone_area_code_2
            mortgagerefer.phone_number_2 = phone_number_2
            mortgagerefer.id_type_2 = id_type_2
            mortgagerefer.id_number_2 = id_number_2
            mortgagerefer.unit = unit
            mortgagerefer.floor = floor
            mortgagerefer.block = block
            mortgagerefer.building = building
            mortgagerefer.street = street
            mortgagerefer.area = area
            mortgagerefer.district = district
            mortgagerefer.loan_purpose = loan_purpose
            mortgagerefer.purchase_price = purchase_price
            mortgagerefer.drawdown_date = drawdown_date
            mortgagerefer.referral = referral
            mortgagerefer.referral_name = referral_name
            mortgagerefer.referral_phone_number = referral_phone_number
            mortgagerefer.create_date = datetime_str
            mortgagerefer.modify_date = datetime_str
            mortgagerefer.status = 0
            mortgagerefer.save(using='infinyrealty')

            subject = f'InfinyRealty 按揭查詢信息'
            full_phone_number = phone_area_code + phone_number
            message_body = f'''
有新的按揭查詢信息：

稱謂: {title}
姓名: {english_name}
電子郵件: {email}
電話: {full_phone_number}
物業地址: Unit {unit}, Floor {floor}, Block {block}, {building}, {street}, {area}, {district}
貸款目的: {loan_purpose}
購入價: {purchase_price}
完成提取貸款日期: {drawdown_date}

'''

            to_email = 'cs@infiny.group'

            try:
                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                    [to_email],
                    fail_silently=False,
                )
            except Exception as e:
                return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

            message_body = f'''
尊敬的客戶，

我們收到一則新的按揭查詢信息，詳細內容如下：

稱謂: {title}
姓名: {english_name}
電子郵件: {email}
電話: {full_phone_number}
物業地址: Unit {unit}, Floor {floor}, Block {block}, {building}, {street}, {area}, {district}
貸款目的: {loan_purpose}
購入價: {purchase_price}
完成提取貸款日期: {drawdown_date}

如需進一步了解或有任何問題，請隨時與我們聯絡。
謝謝您的支持！

Infinyrealty 團隊
'''

            to_email = email

            try:
                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                    [to_email],
                    fail_silently=False,
                )
            except Exception as e:
                return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)


@csrf_exempt
def property_add(request, property_id):
    if not request.session.get('member_username'): return redirect('account')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    username = request.session.get('member_username')
    member = Members.objects.using('infinyrealty').filter(username=username)
    if member:
        member_id = member[0].member_id
        memberproperty = MemberPropertys.objects.using('infinyrealty').filter(propertyid=property_id).filter(
            member_id=member_id)
        if memberproperty:
            return HttpResponse("Member Property exist")
        else:
            memberproperty = MemberPropertys()
            memberproperty.member_id = member_id
            memberproperty.propertyid = property_id
            memberproperty.createdate = datetime_str
            memberproperty.save(using='infinyrealty')
            return HttpResponse("Success")

    return render(request, "web_template/property_show.html", context)


def property_show(request, property_id):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    property_list = Propertys.objects.using('infinyrealty').filter(propertyid=property_id)
    property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=property_id, filetype="photo",
                                                                            isapprove=1).order_by('-ismain')
    property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=property_id,
                                                                                 filetype="floorplan",
                                                                                 isapprove=1).order_by('-ismain')

    property = Propertys.objects.using('infinyrealty').get(propertyid=property_id)
    property.viewcounter = property.viewcounter + 1
    property.save(using='infinyrealty')
    property = Propertys.objects.using('infinyrealty').filter(propertyid=property_id)
    if property:
        propertyname = property[0].propertyname
    else:
        propertyname = ""

    # Get the map image from Google Maps
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={propertyname.replace(' ', '+')}&zoom=18&markers=color:red|{propertyname.replace(' ', '+')}&size=800x600&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
    # map_url = "https://maps.googleapis.com/maps/api/staticmap?center=San+Francisco,CA&zoom=12&size=600x400&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
    response = requests.get(map_url)

    file_path = f"static/dist/img-web/property-cms/{property_id}/location_map.png"

    # Create the directory path if it doesn't exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Save the map image to a file
    with open("static/dist/img-web/property-cms/" + property_id + "/location_map.png", "wb") as f:
        f.write(response.content)

    request.session['currentpage'] = "property"
    context = {
        "property_list": property_list,
        "property_file_list": property_file_list,
        "property_floorplan_list": property_floorplan_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/property_show.html", context)


def property_preview(request, property_id):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    property_list = Propertys.objects.using('infinyrealty').filter(propertyid=property_id)
    property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=property_id, filetype="photo",
                                                                            isapprove=1).order_by('-ismain')
    property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=property_id,
                                                                                 filetype="floorplan",
                                                                                 isapprove=1).order_by('-ismain')

    property = Propertys.objects.using('infinyrealty').get(propertyid=property_id)
    property.viewcounter = property.viewcounter + 1
    property.save(using='infinyrealty')
    property = Propertys.objects.using('infinyrealty').filter(propertyid=property_id)
    if property:
        propertyname = property[0].propertyname
    else:
        propertyname = ""

    # Get the map image from Google Maps
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={propertyname.replace(' ', '+')}&zoom=18&markers=color:red|{propertyname.replace(' ', '+')}&size=800x600&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
    # map_url = "https://maps.googleapis.com/maps/api/staticmap?center=San+Francisco,CA&zoom=12&size=600x400&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
    response = requests.get(map_url)

    file_path = f"static/dist/img-web/property-cms/{property_id}/location_map.png"

    # Create the directory path if it doesn't exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Save the map image to a file
    with open("static/dist/img-web/property-cms/" + property_id + "/location_map.png", "wb") as f:
        f.write(response.content)

    request.session['currentpage'] = "property"
    context = {
        "property_list": property_list,
        "property_file_list": property_file_list,
        "property_floorplan_list": property_floorplan_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/property_preview.html", context)


def newproperty_show(request, listing_id):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    property_list = PropertyListings.objects.using('infinyrealty').filter(listing_id=listing_id)
    property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=listing_id, filetype="newphoto",
                                                                            isapprove=1).order_by('-ismain')
    property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=listing_id,
                                                                                 filetype="newfloorplan",
                                                                                 isapprove=1).order_by('-ismain')

    property = PropertyListings.objects.using('infinyrealty').get(listing_id=listing_id)
    property.viewcounter = property.viewcounter + 1
    property.save(using='infinyrealty')
    property = PropertyListings.objects.using('infinyrealty').filter(listing_id=listing_id)
    if property:
        address = property[0].address
    else:
        address = ""

    # Get the map image from Google Maps
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={address.replace(' ', '+')}&zoom=18&markers=color:red|{address.replace(' ', '+')}&size=800x600&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
    # map_url = "https://maps.googleapis.com/maps/api/staticmap?center=San+Francisco,CA&zoom=12&size=600x400&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
    response = requests.get(map_url)
    # Save the map image to a file

    file_path = f"static/dist/img-web/propertynew-cms/{listing_id}/location_map.png"

    # Create the directory path if it doesn't exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open("static/dist/img-web/propertynew-cms/" + listing_id + "/location_map.png", "wb") as f:
        f.write(response.content)

    request.session['currentpage'] = "newproperty"
    context = {
        "property_list": property_list,
        "property_file_list": property_file_list,
        "property_floorplan_list": property_floorplan_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/newproperty_show.html", context)


def property_foreign_show(request, property_foreign_id=None):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    property_list = PropertyForeigns.objects.using('infinyrealty').filter(propertyforeignid=property_foreign_id)
    property_file_list = PropertyForeignFiles.objects.using('infinyrealty').filter(
        propertyforeignid=property_foreign_id, filetype="photo", isapprove=1).order_by('-ismain')
    property_floorplan_list = PropertyForeignFiles.objects.using('infinyrealty').filter(
        propertyforeignid=property_foreign_id, filetype="floorplan", isapprove=1).order_by('-ismain')

    property = PropertyForeigns.objects.using('infinyrealty').get(propertyforeignid=property_foreign_id)
    property.viewcounter = property.viewcounter + 1
    property.save(using='infinyrealty')

    request.session['currentpage'] = "property"
    context = {
        "property_list": property_list,
        "property_file_list": property_file_list,
        "property_floorplan_list": property_floorplan_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/property_foreign_show.html", context)


def property_foreign_preview(request, property_foreign_id=None):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    property_list = PropertyForeigns.objects.using('infinyrealty').filter(propertyforeignid=property_foreign_id)
    property_file_list = PropertyForeignFiles.objects.using('infinyrealty').filter(
        propertyforeignid=property_foreign_id, filetype="photo", isapprove=1).order_by('-ismain')
    property_floorplan_list = PropertyForeignFiles.objects.using('infinyrealty').filter(
        propertyforeignid=property_foreign_id, filetype="floorplan", isapprove=1).order_by('-ismain')

    property = PropertyForeigns.objects.using('infinyrealty').get(propertyforeignid=property_foreign_id)
    property.viewcounter = property.viewcounter + 1
    property.save(using='infinyrealty')

    request.session['currentpage'] = "property"
    context = {
        "property_list": property_list,
        "property_file_list": property_file_list,
        "property_floorplan_list": property_floorplan_list,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/property_foreign_preview.html", context)


@csrf_exempt
def enquiry_save(request):
    if request.method == 'POST':
        # Get data from POST request
        action = request.POST.get('action')
        property_id = request.POST.get('property_id') or 0
        property_name = request.POST.get('property_name').strip() or ""
        contact_name = request.POST.get('contact_name')
        email = request.POST.get('email')
        phone_area_code = request.POST.get('phone_area_code')
        phone_number = request.POST.get('phone_number')
        message_content = request.POST.get('message')
        newsletter = request.POST.get('newsletter')
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

        enquiry = Enquirys()
        enquiry.property_id = property_id
        enquiry.property_name = property_name
        enquiry.contact_name = contact_name
        enquiry.email = email
        enquiry.phone_area_code = phone_area_code
        enquiry.phone_number = phone_number
        enquiry.message = message_content
        enquiry.newsletter = newsletter
        enquiry.create_date = datetime_str
        enquiry.modify_date = datetime_str
        enquiry.status = 0
        enquiry.save(using='infinyrealty')

        full_phone_number = phone_area_code + phone_number
        subject = f'InfinyRealty 物業查詢'
        message_body = f'''
有新的物業查詢信息：

物業名稱: {property_name}
聯絡姓名: {contact_name}
電子郵件: {email}
電話: {full_phone_number}
電子報訂閱: {'是' if newsletter == '1' else '否'}  

留言內容:
{message_content}


'''

        to_email = 'cs@infiny.group'

        try:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                [to_email],
                fail_silently=False,
            )
        except Exception as e:
            return HttpResponse(f'Error sending internal email: {str(e)}', status=500)
        message_body = f'''
尊敬的客戶，

我們收到一條新的物業查詢信息，以下是詳細內容：

物業名稱: {property_name}
聯絡姓名: {contact_name}
電子郵件: {email}
電話: {full_phone_number}
電子報訂閱: {'是' if newsletter == '1' else '否'}
留言內容:
{message_content}

感謝您對我們的支持！如有任何問題，請隨時與我們聯絡。

Infinyrealty 團隊
'''
        to_email = email

        try:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                [to_email],
                fail_silently=False,
            )
        except Exception as e:
            return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

        return HttpResponse('Success')
    else:
        return HttpResponse('Invalid request')

    # if not request.session.get('loginid'): return redirect('login')
    # datetime_dt = datetime.datetime.today()
    # datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
    #
    # action = str(request.POST.get('action'))
    # if action == "enquiry":
    #     property_id = request.POST.get('property_id')
    #     contact_name = request.POST.get('contact_name')
    #     email = request.POST.get('email')
    #     phone_area_code = request.POST.get('phone_area_code')
    #     phone_number = request.POST.get('phone_number')
    #     message = request.POST.get('message')
    #     newsletter = request.POST.get('newsletter')
    #
    #     try:
    #         enquiry = Enquirys()
    #         enquiry.property_id = property_id
    #         property_list = Propertys.objects.using('infinyrealty').filter(propertyid=property_id)
    #         if property_list:
    #             enquiry.property_name = property_list[0].propertyname
    #         else:
    #             enquiry.property_name = ""
    #         enquiry.contact_name = contact_name
    #         enquiry.email = email
    #         enquiry.phone_area_code = phone_area_code
    #         enquiry.phone_number = phone_number
    #         enquiry.message = message
    #         enquiry.newsletter = newsletter
    #         enquiry.create_date = datetime_str
    #         enquiry.modify_date = datetime_str
    #         enquiry.status = 0
    #         enquiry.save(using='infinyrealty')
    #
    #         smtp_email = "cs@infiny.group"
    #         smtp_password = "Infinywebsite2024"
    #         sender_email = "cs@infiny.group"
    #         recipient_email = email
    #         subject = "InfinyRealty.com 按揭查詢"
    #         message = message
    #
    #         send_email(smtp_email, smtp_password, sender_email, recipient_email, subject, message)
    #         return HttpResponse("Success")
    #     except Exception as e:
    #         exception_type, exception_object, exception_traceback = sys.exc_info()
    #         filename = exception_traceback.tb_frame.f_code.co_filename
    #         line_number = exception_traceback.tb_lineno
    #         return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    # if action == "mortgage":
    #     property_id = 0
    #     property_name = request.POST.get('property_name')
    #     contact_name = request.POST.get('contact_name')
    #     email = request.POST.get('email')
    #     phone_area_code = request.POST.get('phone_area_code')
    #     phone_number = request.POST.get('phone_number')
    #     message = request.POST.get('message')
    #     newsletter = request.POST.get('newsletter')
    #
    #     try:
    #         enquiry = Enquirys()
    #         enquiry.property_id = property_id
    #         enquiry.property_name = property_name
    #         enquiry.contact_name = contact_name
    #         enquiry.email = email
    #         enquiry.phone_area_code = phone_area_code
    #         enquiry.phone_number = phone_number
    #         enquiry.message = message
    #         enquiry.newsletter = newsletter
    #         enquiry.create_date = datetime_str
    #         enquiry.modify_date = datetime_str
    #         enquiry.status = 0
    #         enquiry.save(using='infinyrealty')
    #         return HttpResponse("Success")
    #     except Exception as e:
    #         exception_type, exception_object, exception_traceback = sys.exc_info()
    #         filename = exception_traceback.tb_frame.f_code.co_filename
    #         line_number = exception_traceback.tb_lineno
    #         return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)


def property_search(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    propertyname = request.session.get('search_propertyname')
    propertyno = request.session.get('search_propertyno')
    have_value = request.session.get('search_have_value')
    usage = request.session.get('search_usage')
    areacode = request.session.get('search_areacode')
    offertype = request.session.get('search_offertype')
    price_min = request.session.get('price_min')
    price_max = request.session.get('price_max')
    unitprice_min = request.session.get('unitprice_min')
    unitprice_max = request.session.get('unitprice_max')
    area_min = request.session.get('area_min')
    area_max = request.session.get('area_max')
    display_mode = request.session.get('display_mode')
    sorting_mode = request.session.get('sorting_mode')
    if propertyname is None or propertyname == "None": propertyname = ""
    if propertyno is None or propertyno == "None": propertyno = ""
    if have_value is None: have_value = 0
    if usage is None: usage = ""
    if areacode is None: areacode = ""
    if offertype is None: offertype = ""
    if price_min is None: price_min = ""
    if price_max is None: price_max = ""
    if unitprice_min is None: unitprice_min = ""
    if unitprice_max is None: unitprice_max = ""
    if area_min is None: area_min = ""
    if area_max is None: area_max = ""
    if sorting_mode is None: sorting_mode = ""
    currentpage = 1
    pagesize = 12
    # request.session.clear()

    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "exec spPropertyListPaging " + str(currentpage) + ", " + str(
        pagesize) + ", N'" + propertyname + "', N'" + propertyno + "'," + str(
        have_value) + ", N'" + usage + "', N'" + areacode + "', N'" + offertype + "', N'" + price_min + "', N'" + price_max + "', N'" + unitprice_min + "', N'" + unitprice_max + "', N'" + area_min + "', N'" + area_max + "', '" + sorting_mode + "'"
    cursor.execute(sql)
    property_search_list = cursor.fetchall()
    sql1 = "exec spPropertyLatestList N'" + usage + "', N'" + areacode + "'"
    cursor.execute(sql1)
    property_latest_list = cursor.fetchall()
    cursor.close()
    cnxn.close()
    if property_search_list:
        total_records = property_search_list[0].TotalRecords
    else:
        total_records = 0

    if display_mode == "" or display_mode is None:
        request.session['display_mode'] = "list"
        display_mode = "list"

    request.session['currentpage'] = "property"
    context = {
        "property_search_list": property_search_list,
        "property_latest_list": property_latest_list,
        "propertyname": propertyname,
        "propertyno": propertyno,
        "have_value": have_value,
        "usage": usage,
        "areacode": areacode,
        "offertype": offertype,
        "price_min": price_min,
        "price_max": price_max,
        "unitprice_min": unitprice_min,
        "unitprice_max": unitprice_max,
        "area_min": area_min,
        "area_max": area_max,
        "display_mode": display_mode,
        "sorting_mode": sorting_mode,
        "total_records": total_records,
        "currentpage": currentpage,
        "pagesize": pagesize,
        "favorites_cookies": favorites_cookies,
        "sql": sql,
    }
    return render(request, "web_template/property_search.html", context)


def property_foreign_search(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    projectname = request.session.get('search_projectname')
    propertyno = request.session.get('search_propertyno')
    have_value = request.session.get('search_have_value')
    usage = request.session.get('search_usage')
    country = request.session.get('search_country')
    areacode = request.session.get('search_areacode')
    offertype = request.session.get('search_offertype')
    price_min = request.session.get('price_min')
    price_max = request.session.get('price_max')
    unitprice_min = request.session.get('unitprice_min')
    unitprice_max = request.session.get('unitprice_max')
    area_min = request.session.get('area_min')
    area_max = request.session.get('area_max')
    display_mode = request.session.get('display_mode')
    sorting_mode = request.session.get('sorting_mode')
    if projectname is None: projectname = ""
    if propertyno is None: propertyno = ""
    if have_value is None: have_value = 0
    if usage is None: usage = ""
    if areacode is None: areacode = ""
    if offertype is None: offertype = ""
    if price_min is None: price_min = ""
    if price_max is None: price_max = ""
    if unitprice_min is None: unitprice_min = ""
    if unitprice_max is None: unitprice_max = ""
    if area_min is None: area_min = ""
    if area_max is None: area_max = ""
    if country is None: country = ""
    if sorting_mode is None: sorting_mode = ""
    currentpage = 1
    pagesize = 12
    # request.session.clear()

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=9, status=1).order_by('sequence')
    CountryList = CodeDetails.objects.using('infinyrealty').filter(code_id=8, status=1).order_by('sequence')
    try:
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "exec spPropertyForeignListPaging " + str(currentpage) + ", " + str(pagesize) + ", N'" + str(
            projectname) + "', N'" + str(propertyno) + "'," + str(have_value) + ", N'" + str(usage) + "', N'" + str(
            country) + "', N'" + str(areacode) + "', N'" + str(offertype) + "', N'" + str(price_min) + "', N'" + str(
            price_max) + "', N'" + str(unitprice_min) + "', N'" + str(unitprice_max) + "', N'" + str(
            area_min) + "', N'" + str(area_max) + "', '" + str(sorting_mode) + "'"
        cursor.execute(sql)
        property_search_list = cursor.fetchall()
        cursor.close()
        cnxn.close()
        if property_search_list:
            total_records = property_search_list[0].TotalRecords
        else:
            total_records = 0
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        property_search_list = []
        total_records = 0
        # return HttpResponse("Error line " + str(line_number) + ": " + str(e))

        if display_mode == "" or display_mode is None:
            request.session['display_mode'] = "list"
            display_mode = "list"

    request.session['currentpage'] = "oversea"
    context = {
        "property_search_list": property_search_list,
        "usagelist": UsageList,
        "countrylist": CountryList,
        "projectname": projectname,
        "propertyno": propertyno,
        "have_value": have_value,
        "usage": usage,
        "country": country,
        "areacode": areacode,
        "offertype": offertype,
        "price_min": price_min,
        "price_max": price_max,
        "unitprice_min": unitprice_min,
        "unitprice_max": unitprice_max,
        "area_min": area_min,
        "area_max": area_max,
        "display_mode": display_mode,
        "sorting_mode": sorting_mode,
        "total_records": total_records,
        "currentpage": currentpage,
        "pagesize": pagesize,
        "sql": sql,
    }
    return render(request, "web_template/property_foreign_search.html", context)


@csrf_exempt
def property_data(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    currentpage = request.POST.get('page')
    pagesize = request.POST.get('pageSize')
    propertyname = request.session.get('search_propertyname')
    propertyno = request.session.get('search_propertyno')
    have_value = request.session.get('search_have_value')
    usage = request.session.get('search_usage')
    areacode = request.session.get('search_areacode')
    offertype = request.session.get('search_offertype')
    price_min = request.session.get('price_min')
    price_max = request.session.get('price_max')
    unitprice_min = request.session.get('unitprice_min')
    unitprice_max = request.session.get('unitprice_max')
    area_min = request.session.get('area_min')
    area_max = request.session.get('area_max')
    display_mode = request.session.get('display_mode')
    sorting_mode = request.session.get('sorting_mode')
    if propertyname is None or propertyname == "None": propertyname = ""
    if propertyno is None or propertyno == "None": propertyno = ""
    if have_value is None: have_value = 0
    if usage is None: usage = ""
    if areacode is None: areacode = ""
    if offertype is None: offertype = ""
    if price_min is None: price_min = ""
    if price_max is None: price_max = ""
    if unitprice_min is None: unitprice_min = ""
    if unitprice_max is None: unitprice_max = ""
    if area_min is None: area_min = ""
    if area_max is None: area_max = ""
    if sorting_mode is None: sorting_mode = ""

    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "exec spPropertyListPaging " + str(currentpage) + ", " + str(
        pagesize) + ", N'" + propertyname + "', N'" + propertyno + "'," + str(
        have_value) + ", N'" + usage + "', N'" + areacode + "', N'" + offertype + "', N'" + price_min + "', N'" + price_max + "', N'" + unitprice_min + "', N'" + unitprice_max + "', N'" + area_min + "', N'" + area_max + "', '" + sorting_mode + "'"
    cursor.execute(sql)
    property_search_list = cursor.fetchall()
    cursor.close()
    cnxn.close()
    if property_search_list:
        total_records = property_search_list[0].TotalRecords
    else:
        total_records = 0

    if display_mode == "" or display_mode is None:
        request.session['display_mode'] = "list"
        display_mode = "list"

    context = {
        "property_search_list": property_search_list,
        "propertyname": propertyname,
        "propertyno": propertyno,
        "usage": usage,
        "areacode": areacode,
        "offertype": offertype,
        "price_min": price_min,
        "price_max": price_max,
        "unitprice_min": unitprice_min,
        "unitprice_max": unitprice_max,
        "area_min": area_min,
        "area_max": area_max,
        "display_mode": display_mode,
        "sorting_mode": sorting_mode,
        "total_records": total_records,
        "currentpage": currentpage,
        "pagesize": pagesize,
        "favorites_cookies": favorites_cookies,
        "sql": sql,
    }
    return render(request, "web_template/property_data.html", context)


@csrf_exempt
def property_foreign_data(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    currentpage = request.POST.get('page')
    pagesize = request.POST.get('pageSize')
    propertyname = request.session.get('search_propertyname')
    projectname = request.session.get('search_projectname')
    propertyno = request.session.get('search_propertyno')
    have_value = request.session.get('search_have_value')
    usage = request.session.get('search_usage')
    usage = ""
    country = request.session.get('search_country')
    areacode = request.session.get('search_areacode')
    offertype = request.session.get('search_offertype')
    price_min = request.session.get('price_min')
    price_max = request.session.get('price_max')
    unitprice_min = request.session.get('unitprice_min')
    unitprice_max = request.session.get('unitprice_max')
    area_min = request.session.get('area_min')
    area_max = request.session.get('area_max')
    display_mode = request.session.get('display_mode')
    sorting_mode = request.session.get('sorting_mode')
    if propertyname is None or propertyname == "None": propertyname = ""
    if propertyno is None: propertyno = ""
    if projectname is None: projectname = ""
    if have_value is None: have_value = 0
    if usage is None: usage = ""
    if country is None or country == "None": country = ""
    if areacode is None: areacode = ""
    if offertype is None: offertype = ""
    if price_min is None: price_min = ""
    if price_max is None: price_max = ""
    if unitprice_min is None: unitprice_min = ""
    if unitprice_max is None: unitprice_max = ""
    if area_min is None: area_min = ""
    if area_max is None: area_max = ""
    if display_mode is None: display_mode = ""
    if sorting_mode is None: sorting_mode = ""

    try:
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        # sql = "exec spPropertyListPaging "+str(currentpage)+", "+str(pagesize)+", N'" + propertyname + "', N'" + propertyno + "'," + str(have_value) + ", N'" + usage + "', N'" + areacode + "', N'" + offertype + "', N'" + price_min + "', N'" + price_max + "', N'" + unitprice_min + "', N'" + unitprice_max + "', N'" + area_min + "', N'" + area_max + "', '" + sorting_mode + "'"
        sql = "exec spPropertyForeignListPaging " + str(currentpage) + ", " + str(pagesize) + ", N'" + str(
            projectname) + "', N'" + str(propertyno) + "'," + str(have_value) + ", N'" + str(usage) + "', N'" + str(
            country) + "', N'" + str(areacode) + "', N'" + str(offertype) + "', N'" + str(price_min) + "', N'" + str(
            price_max) + "', N'" + str(unitprice_min) + "', N'" + str(unitprice_max) + "', N'" + str(
            area_min) + "', N'" + str(area_max) + "', '" + str(sorting_mode) + "'"
        cursor.execute(sql)
        property_foreign_search_list = cursor.fetchall()
        cursor.close()
        cnxn.close()
        if property_foreign_search_list:
            total_records = property_foreign_search_list[0].TotalRecords
        else:
            total_records = 0

        if display_mode == "" or display_mode is None:
            request.session['display_mode'] = "list"
            display_mode = "list"

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        return HttpResponse("Error line " + str(line_number) + ": " + str(e))

    context = {
        "property_foreign_search_list": property_foreign_search_list,
        "propertyname": propertyname,
        "propertyno": propertyno,
        "usage": usage,
        "areacode": areacode,
        "offertype": offertype,
        "price_min": price_min,
        "price_max": price_max,
        "unitprice_min": unitprice_min,
        "unitprice_max": unitprice_max,
        "area_min": area_min,
        "area_max": area_max,
        "display_mode": display_mode,
        "sorting_mode": sorting_mode,
        "total_records": total_records,
        "currentpage": currentpage,
        "pagesize": pagesize,
        "favorites_cookies": favorites_cookies,
        "sql": sql,
    }
    return render(request, "web_template/property_foreign_data.html", context)


def transaction(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    propertyname = request.session.get('search_propertyname')
    propertyno = request.session.get('search_propertyno')
    usage = request.session.get('search_usage')
    areacode = request.session.get('search_areacode')
    offertype = request.session.get('search_offertype')
    display_mode = request.session.get('display_mode')
    sorting_mode = request.session.get('sorting_mode')
    if propertyname is None: propertyname = ""
    if propertyno is None: propertyno = ""
    if usage is None: usage = ""
    if areacode is None: areacode = ""
    if offertype is None: offertype = ""
    if sorting_mode is None: sorting_mode = ""
    currentpage = 1
    pagesize = 12

    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    # sql = "exec spPropertyListPaging "+str(currentpage)+", "+str(pagesize)+", N'" + propertyname + "', N'" + propertyno + "', N'" + usage + "', N'" + areacode + "', N'" + offertype + "', '" + sorting_mode + "'"
    # cursor.execute(sql)
    # property_search_list = cursor.fetchall()
    sql1 = "exec spPropertyLatestList N'" + usage + "', N'" + areacode + "'"
    cursor.execute(sql1)
    property_latest_list = cursor.fetchall()
    cursor.close()
    cnxn.close()
    # if property_search_list:
    #    total_records = property_search_list[0].TotalRecords
    # else:
    #    total_records = 0

    if display_mode == "" or display_mode is None:
        request.session['display_mode'] = "list"
        display_mode = "list"

    request.session['currentpage'] = "property"
    context = {
        # "property_search_list": property_search_list,
        "property_latest_list": property_latest_list,
        "propertyname": propertyname,
        "propertyno": propertyno,
        "usage": usage,
        "areacode": areacode,
        "offertype": offertype,
        "display_mode": display_mode,
        "sorting_mode": sorting_mode,
        # "total_records": total_records,
        "currentpage": currentpage,
        "pagesize": pagesize,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/transaction.html", context)


def favourite(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookiestring(request)
    favorites_cookies_list = getcookielist(request)
    propertyname = ""
    propertyno = ""
    usage = ""
    areacode = ""
    offertype = ""
    display_mode = request.session.get('display_mode')
    sorting_mode = request.session.get('sorting_mode')
    if propertyname is None: propertyname = ""
    if propertyno is None: propertyno = ""
    if usage is None: usage = ""
    if areacode is None: areacode = ""
    if offertype is None: offertype = ""
    if sorting_mode is None: sorting_mode = ""
    currentpage = 1
    pagesize = 12

    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "exec spPropertyListPagingWithList " + str(currentpage) + ", " + str(
        pagesize) + ", N'" + propertyname + "', N'" + propertyno + "', N'" + usage + "', N'" + areacode + "', N'" + offertype + "', '" + sorting_mode + "', '" + favorites_cookies + "'"
    cursor.execute(sql)
    property_search_list = cursor.fetchall()
    cursor.close()
    cnxn.close()
    if property_search_list:
        total_records = property_search_list[0].TotalRecords
    else:
        total_records = 0

    if display_mode == "" or display_mode is None:
        request.session['display_mode'] = "list"
        display_mode = "list"

    context = {
        "property_search_list": property_search_list,
        "propertyname": propertyname,
        "propertyno": propertyno,
        "usage": usage,
        "areacode": areacode,
        "offertype": offertype,
        "display_mode": display_mode,
        "sorting_mode": sorting_mode,
        "total_records": total_records,
        "currentpage": currentpage,
        "pagesize": pagesize,
        "favorites_cookies": favorites_cookies_list,
        "sql": sql,
    }
    return render(request, "web_template/favourite.html", context)


@csrf_exempt
def favourite_data(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookiestring(request)
    propertyname = ""
    propertyno = ""
    usage = ""
    areacode = ""
    offertype = ""
    display_mode = request.session.get('display_mode')
    sorting_mode = request.session.get('sorting_mode')
    if propertyname is None: propertyname = ""
    if propertyno is None: propertyno = ""
    if usage is None: usage = ""
    if areacode is None: areacode = ""
    if offertype is None: offertype = ""
    if sorting_mode is None: sorting_mode = ""
    currentpage = 1
    pagesize = 12

    cnxn = pyodbc.connect(
        'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
            settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                             None) + ';Database=infinyrealty')
    cursor = cnxn.cursor()
    sql = "exec spPropertyListPagingWithList " + str(currentpage) + ", " + str(
        pagesize) + ", N'" + propertyname + "', N'" + propertyno + "', N'" + usage + "', N'" + areacode + "', N'" + offertype + "', '" + sorting_mode + "', '" + favorites_cookies + "'"
    cursor.execute(sql)
    property_search_list = cursor.fetchall()
    cursor.close()
    cnxn.close()
    if property_search_list:
        total_records = property_search_list[0].TotalRecords
    else:
        total_records = 0

    if display_mode == "" or display_mode is None:
        request.session['display_mode'] = "list"
        display_mode = "list"

    context = {
        "property_search_list": property_search_list,
        "propertyname": propertyname,
        "propertyno": propertyno,
        "usage": usage,
        "areacode": areacode,
        "offertype": offertype,
        "display_mode": display_mode,
        "sorting_mode": sorting_mode,
        "total_records": total_records,
        "currentpage": currentpage,
        "pagesize": pagesize,
        "favorites_cookies": favorites_cookies,
        "sql": sql,
    }
    return render(request, "web_template/favourite_data.html", context)


def search_result(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    # if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')
    team = request.session.get('team')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    accessid = 45
    request.session['accessid'] = accessid
    # users = Users.objects.using('infinyrealty').get(username=request.session.get('username'),isactive=1)
    # users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    # users.save(using='infinyrealty')
    # pageviewlog(accessid,request.session.get('loginid'),request.session.get('username'),request.session.get('username_org'))
    context = {
        "user_loginid": loginid,
        "user_team": team,

        "usagelist": UsageList,
    }
    return render(request, "web_template/search_result.html", context)


def contact(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    request.session['currentpage'] = "contact"

    context = {
        "usagelist": UsageList,
        "favorites_cookies": favorites_cookies,
    }
    return render(request, "web_template/contact.html", context)


def logoutw(request):
    request.session['member_username'] = ""
    return HttpResponseRedirect('/main')


def getcookielist(request):
    try:
        cookie_header = request.META.get('HTTP_COOKIE', '')
        favorite_cookies = {}
        for cookie in cookie_header.split(';'):
            key, value = cookie.strip().split('=')

            # Check if the cookie is a favorite
            if key.startswith('favorites'):
                my_list = value.split(',')
                cookie_list = my_list
        return cookie_list
    except:
        return ""


def getcookiestring(request):
    try:
        cookie_header = request.META.get('HTTP_COOKIE', '')
        favorite_cookies = {}
        for cookie in cookie_header.split(';'):
            key, value = cookie.strip().split('=')

            # Check if the cookie is a favorite
            if key.startswith('favorites'):
                cookie_list = value
        return cookie_list
    except:
        return ""


def capture(request):
    # request.session['capture_count'] = 0
    # num = int(request.session.get('capture_count')) + 20
    for type in ["商舗"]:
        # for type in ["商舗"]:
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
                            if not TransactionRecords.objects.using('infinyrealty').filter(
                                    transactiondate=transactionrecord.transactiondate,
                                    district=transactionrecord.district, propertyname=transactionrecord.propertyname,
                                    approximatearea=transactionrecord.approximatearea, floor=transactionrecord.floor,
                                    source=transactionrecord.source, usage=transactionrecord.usage).exists():
                                transactionrecord.save(using='infinyrealty')
                except TimeoutException:
                    continue
    # request.session['capture_count'] = num
    return redirect('capture')

    context = {
        "table_rows": table_container_elements,
        "capture": "1",
    }
    return render(request, "web_template/capture.html", context)


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
                        if not TransactionRecords.objects.using('infinyrealty').filter(
                                transactiondate=transactionrecord.transactiondate, district=transactionrecord.district,
                                propertyname=transactionrecord.propertyname, floor=transactionrecord.floor,
                                source=transactionrecord.source, usage=transactionrecord.usage).exists():
                            transactionrecord.save(using='infinyrealty')
    pass


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


def hash_password(password):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Convert the password to bytes and hash it
    sha256_hash.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = sha256_hash.hexdigest()

    return hashed_password


def form_visittour(request):
    if request.session.get('lang') is None or request.session.get('lang') == "":
        request.session['lang'] = "tc"
    favorites_cookies = getcookielist(request)
    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')

    request.session['currentpage'] = "form_visittour"

    visit_tour_form = VisitTourForm.objects.using('infinyrealty').get(id=1)
    match request.session.get('lang'):
        case "tc":
            form_title = visit_tour_form.title
            form_desc = visit_tour_form.desc
        case "sc":
            form_title = visit_tour_form.title_sc
            form_desc = visit_tour_form.desc_sc
        case "en":
            form_title = visit_tour_form.title_en
            form_desc = visit_tour_form.desc_en
        case _:
            form_title = visit_tour_form.title
            form_desc = visit_tour_form.desc

    form_time_list = visit_tour_form.time.split(";")

    context = {
        "usagelist": UsageList,
        "favorites_cookies": favorites_cookies,
        "visit_tour_form": visit_tour_form,
        "form_title": form_title,
        "form_desc": form_desc,
        "form_time_list": form_time_list,
    }
    return render(request, "web_template/form_visit_tour.html", context)


@csrf_exempt
def form_visittour_save(request):
    # if not request.session.get('loginid'): return redirect('login')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone_area_code = request.POST.get('phone_area_code') and request.POST.get('phone_area_code') or ""
    phone_number = request.POST.get('phone_number')
    total_guest = request.POST.get('total_guest')
    date_of_visit = request.POST.get('date_of_visit')
    time_of_visit = request.POST.get('time_of_visit')

    try:
        visit_tour = VisitTour()
        visit_tour.first_name = first_name
        visit_tour.last_name = last_name
        visit_tour.email = email
        visit_tour.phone_area_code = phone_area_code
        visit_tour.phone_number = phone_number
        visit_tour.date_of_visit = date_of_visit
        visit_tour.time_of_visit = time_of_visit
        visit_tour.total_guest = total_guest
        visit_tour.create_date = datetime_str
        visit_tour.modify_date = datetime_str
        visit_tour.save(using='infinyrealty')

        subject = f'InfinyRealty 導賞團'
        full_phone_number = phone_area_code + phone_number
        message_body = f'''
有新的導賞團請求：

聯繫人姓名: {first_name} {last_name}
電子郵件: {email}
電話: {full_phone_number}
參加導賞團日期： {date_of_visit}
參加導賞團時間: {time_of_visit}
同行總人數: {total_guest}

'''

        to_email = 'cs@infiny.group'

        try:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                [to_email],
                fail_silently=False,
            )
        except Exception as e:
            return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

        message_body = f'''
尊敬的客戶，

我們很高興通知您，您有一個新的導賞團請求。我們的團隊將會儘快處理您的請求。以下是相關的詳細信息：

聯繫人姓名: {first_name} {last_name}
電子郵件: {email}
電話: {full_phone_number}
參加導賞團日期： {date_of_visit}
參加導賞團時間: {time_of_visit}
同行總人數: {total_guest}

感謝您選擇 Infinyrealty。我們期待著為您提供優質的服務。如有任何疑問或需要進一步的幫助，請隨時聯絡我們。

Infinyrealty 團隊
'''
        to_email = email

        try:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,  # From email (make sure it's set in your settings.py)
                [to_email],
                fail_silently=False,
            )
        except Exception as e:
            return HttpResponse(f'Error sending internal email: {str(e)}', status=500)

        return HttpResponse("Success")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

