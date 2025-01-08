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
from django.template.defaulttags import register
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import RGBColor
from docxcompose.composer import Composer
from copy import deepcopy
import pdfkit
from bs4 import BeautifulSoup
from django.http import FileResponse
import json
import pyodbc
import requests
import datetime
import os
import sys
import shutil
import io
import pandas as pd
import numpy as np
from PIL import ImageDraw
from PIL import Image, ImageEnhance
from PIL import ImageFont
from PIL import JpegImagePlugin
from urllib.parse import quote
import openpyxl
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import groupdocs.merger as gv
import hashlib
import random
import string
from itertools import chain

from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks, Focusgroup, Focussubtypes
from InfinyRealty_app.models import PageView, CodeDetails, Propertys, PropertyArea, PropertyForeigns, PropertyFiles, PropertyForeignFiles, PropertyContacts, PropertyFollows, PropertyHighlights, PropertyUsages, PropertyListings, AccessLogs

from django.conf import settings

JpegImagePlugin._getmp = lambda: None

def property(request, propertyid=None):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    #propertyid = request.POST.get('propertyid')
    if propertyid is None:
        propertyid = ""

    usage_list = PropertyUsages.objects.using('infinyrealty').order_by('sequence')

    accessid = 5158
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
        "user_usage": 1,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usage_list": usage_list,
        "user_propertyid": propertyid,
    }
    return render(request, "property_template/property.html", context)

@csrf_exempt
def property_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.session.get('loginid')
    username = request.session.get('username')
    propertyid = request.POST.get('propertyid')
    today = datetime.datetime.now()

    if action == "menutab":
        context = {
            "action": action,
            "user_loginid": loginid,
            "user_propertyid": propertyid,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "userlist": user_list,
        }
    if action == "usage_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_Usage_count")
        usage_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_view_list": usage_view_list,
            "today": today,
        }
    if action == "property_view":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage_list = PropertyUsages.objects.using('infinyrealty').order_by('sequence')
        area_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        cursor.execute("select * from V_AddressSubDistrict")
        subdistrict_list = cursor.fetchall()
        cursor.execute("select * from V_AddressStreet")
        street_list = cursor.fetchall()
        cursor.execute("select * from V_AddressBuilding")
        building_list = cursor.fetchall()
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')

        usage = request.POST.get('usage')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None or usage == "" :
            sql = "select * from V_PropertyFullList where propertyid <> 0"
        else:
            sql = "select * from V_PropertyFullList where usage = N'" + usage + "' and propertyid <> 0"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()
        today30 = today - timedelta(days=30)

        context = {
            "action": action,
            "user_loginid": loginid,
            "property_view_list": property_view_list,
            "usage_list": usage_list,
            "floorzone_list": floorzone_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "area_list": area_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "building_list": building_list,
            "today30": today30,
            "sql": sql,
        }
    if action == "property_edit":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        cursor.execute("select * from V_AddressBuilding")
        building_list = cursor.fetchall()
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_area_list = PropertyArea.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain','sequence')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain','sequence')
        property_document_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="document").order_by('-ismain')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact where propertyid = '" + str(propertyid) + "' order by createdate desc")
        property_contact_list = cursor.fetchall()
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyFollow where propertyid = '" + str(propertyid) + "' order by followdate desc")
        property_follow_list = cursor.fetchall()
        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "building_list": building_list,
            "floorzone_list": floorzone_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_area_list": property_area_list,
            "property_contact_list": property_contact_list,
            "property_follow_list": property_follow_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_document_list": property_document_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_info":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')
        decoration_list = CodeDetails.objects.using('infinyrealty').filter(code_id=15).order_by('sequence')
        view_list = CodeDetails.objects.using('infinyrealty').filter(code_id=16).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')
        property_document_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="document").order_by('-ismain')
        #property_photo_list = list(chain(property_file_list, property_floorplan_list))
        property_photo_list = ""

        for w in property_photo_list:
            filename = w.filename
            filename_extension = os.path.splitext(filename)[1][1:].lower()
            if "jpg" in filename_extension or "jpeg" in filename_extension or "png" in filename_extension:
                if w.filetype == "photo":
                    filename = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\"+w.filename
                    filename_wm = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\"+w.filename.replace("."+filename_extension, "-wm."+filename_extension)
                else:
                    filename = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename
                    filename_wm = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename.replace("."+filename_extension, "-wm."+filename_extension)
                filename_logo = getattr(settings, "PATH_MAIN", None) + "infinyrealty_logo_high.png"
                base_image = Image.open(filename)
                watermark_image = Image.open(filename_logo)
                if w.filetype == "photo":
                    watermark_ratio = 0.1  # 10% of the base image size
                else:
                    watermark_ratio = 0.03  # 3% of the base image size
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
                base_image.save(filename_wm)
                try:
                    PropertyFiles.objects.using('infinyrealty').filter(fileid=w.fileid).update(iswatermark=1)
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno
                    return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
                #draw = ImageDraw.Draw(image)
                #font = ImageFont.truetype("arial.ttf", size=150)
                #watermark_text = "infinyrealty.com2"
                #x = (image.width) / 2
                #y = (image.height) / 2
                #draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
                #image.save(filename_wm)

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "floorzone_list": floorzone_list,
            "decoration_list": decoration_list,
            "view_list": view_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_document_list": property_document_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_oddsheet":
        propertyid = request.POST.get('propertyid')
        lang = request.POST.get('lang')
        if propertyid is None or propertyid == "":
            propertyid = 0
        propertyid_list = request.POST.get('propertyid_list').split(",")
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").exclude(filename__endswith=".mp4").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')
        file_exist = []
        for w in propertyid_list:
            property_list1 = Propertys.objects.using('infinyrealty').filter(propertyid=w)
            propertyno = property_list1[0].propertyno
            path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None)
            file_path = f'{path}\\{w}\\InfinyRealty_{propertyno}.docx'
            if os.path.exists(file_path):
                file_exist.append(w)

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "propertyid_list": propertyid_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "file_exist": file_exist,
            "property_floorplan_list": property_floorplan_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "lang": lang,
            "today": today,
        }
    if action == "property_oddsheet_table":
        propertyid = request.POST.get('propertyid')
        lang = request.POST.get('lang')
        if propertyid is None or propertyid == "":
            propertyid = 0
        propertyid_list = request.POST.get('propertyid_list').split(",")
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        # property_list = Propertys.objects.using('infinyrealty').filter(propertyid__in=propertyid_list)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyFullList where propertyid IN (" + request.POST.get('propertyid_list') + ")")
        property_list = cursor.fetchall()
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").exclude(filename__endswith=".mp4").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')

        # Generate Oddsheet excel
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")
        propertyid_list = request.POST.get('propertyid_list')
        cnxn = pyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(
                settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD",
                                                                 None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if propertyid_list:
            # Convert the string into a list and format for SQL
            property_ids = propertyid_list.strip("[]").replace("'", "").split(',')
            formatted_ids = ','.join(f"'{id.strip()}'" for id in property_ids)  # Add quotes around each ID
            sql = f"SELECT * FROM tblProperty WHERE PropertyID IN ({formatted_ids}) order by SubDistrict"
        else:
            sql = "SELECT * FROM tblProperty"  # Fallback if property_list is empty
        df = pd.read_sql(sql, cnxn)

        # Path to the Excel template
        path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None)

        template_path = path + '\\InfinyRealty_OddSheet_Excel_template.xlsx'
        wb = load_workbook(template_path)
        sheet = wb.active  # or specify the sheet name with wb['SheetName']

        # Select a specific worksheet by name
        sheet_name = '繁'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            image_path = getattr(settings, "PATH_PROPERTY", None) + str(
                row.get('PropertyID', '')) + "\\" + "20240815_133107.jpg"
            # image_path = "D:\\Website\\InfinyRealty\\static\\dist\\img-web\\property-cms\\13\\20240815_133107.jpg"
            image_path = "//static//dist/img-web//property-cms//13//20240815_133107.jpg"

            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地區 (" + row.get('SubDistrict', '') + ")"
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter

            # Check if the image file exists
            if os.path.exists(image_path):
                try:
                    img = Image(image_path)  # Correct usage
                    img.anchor = 'A1'  # Adjust the cell reference as needed
                    sheet.add_image(img)
                except Exception as e:
                    print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")

            sheet[f'B{RowNo}'] = row.get('PropertyName', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'C{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'D{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'E{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'F{RowNo}'] = row.get('Tenant', '')
            sheet[f'G{RowNo}'] = row.get('Possession', '')

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'H{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'I{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'J{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'J{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'K{RowNo}'] = row.get('Rent', '')
            sheet[f'L{RowNo}'] = row.get('NetArea', '')
            sheet[f'M{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'N{RowNo}'] = row.get('Yield', '')
            sheet[f'O{RowNo}'] = row.get('FinalPrice', '')
            sheet[f'P{RowNo}'] = row.get('Decoration', '')
            sheet[f'Q{RowNo}'] = row.get('Views', '')
            sheet[f'R{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Select a specific worksheet by name
        sheet_name = '简'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地区 (" + row.get('SubDistrict_s', '') + ")"
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter
            sheet[f'B{RowNo}'] = row.get('PropertyName_s', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'C{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'D{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'E{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'F{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "商议"
            if row.get('Possession', '') == "現吉":
                Possession = "现吉"
            if row.get('Possession', '') == "連租約":
                Possession = "连租约"
            if row.get('Possession', '') == "已租":
                Possession = "已租"
            if row.get('Possession', '') == "已售":
                Possession = "已售"
            sheet[f'G{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'H{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'I{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'J{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'J{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'K{RowNo}'] = row.get('Rent', '')
            sheet[f'L{RowNo}'] = row.get('NetArea', '')
            sheet[f'M{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'N{RowNo}'] = row.get('Yield', '')
            sheet[f'O{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "基本裝修"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "精致装修"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "豪裝裝修"
            sheet[f'P{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "望山景"
            if row.get('Views', '') == "望園景":
                Views = "望园景"
            if row.get('Views', '') == "望開揚景":
                Views = "望开扬景"
            if row.get('Views', '') == "望樓景":
                Views = "望开扬景"
            if row.get('Views', '') == "望市景":
                Views = "望市景"
            if row.get('Views', '') == "望海景":
                Views = "望海景"
            if row.get('Views', '') == "望河景":
                Views = "望河景"
            if row.get('Views', '') == "望泳池景":
                Views = "望泳池景"
            sheet[f'Q{RowNo}'] = Views
            sheet[f'R{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Select a specific worksheet by name
        sheet_name = 'ENG'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "District (" + row.get('SubDistrict_e', '') + ")"
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter
            sheet[f'B{RowNo}'] = row.get('PropertyName_e', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'C{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'D{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'E{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'F{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "Discuss"
            if row.get('Possession', '') == "現吉":
                Possession = "Now auspicious"
            if row.get('Possession', '') == "連租約":
                Possession = "With lease"
            if row.get('Possession', '') == "已租":
                Possession = "Rented"
            if row.get('Possession', '') == "已售":
                Possession = "Sold"
            sheet[f'G{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'H{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'I{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'J{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'J{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'K{RowNo}'] = row.get('Rent', '')
            sheet[f'L{RowNo}'] = row.get('NetArea', '')
            sheet[f'M{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'N{RowNo}'] = row.get('Yield', '')
            sheet[f'O{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "Basic Decoration"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "Exquisite Decoration"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "Luxurious Decoration"
            sheet[f'P{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "Mountain view"
            if row.get('Views', '') == "望園景":
                Views = "Garden view"
            if row.get('Views', '') == "望開揚景":
                Views = "Open view"
            if row.get('Views', '') == "望樓景":
                Views = "Tower view"
            if row.get('Views', '') == "望市景":
                Views = "City view"
            if row.get('Views', '') == "望海景":
                Views = "Sea view"
            if row.get('Views', '') == "望河景":
                Views = "River view"
            if row.get('Views', '') == "望泳池景":
                Views = "Pool view"
            sheet[f'Q{RowNo}'] = Views
            sheet[f'R{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Save the workbook
        output_path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\物業盤紙(列表)_" + datetime_str + ".xlsx"
        wb.save(output_path)

        # Close the database connection
        cnxn.close()

        if os.path.exists(output_path):
            with open(output_path, 'rb') as fh:
                response = HttpResponse(
                    fh.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response['Content-Disposition'] = f'attachment; filename="物業盤紙(列表)_{datetime_str}.xlsx"'


        # Generate Oddsheet Image
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")
        propertyid_list = request.POST.get('propertyid_list')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if propertyid_list:
            # Convert the string into a list and format for SQL
            property_ids = propertyid_list.strip("[]").replace("'", "").split(',')
            formatted_ids = ','.join(f"'{id.strip()}'" for id in property_ids)  # Add quotes around each ID
            sql = f"SELECT * FROM tblProperty WHERE PropertyID IN ({formatted_ids}) order by SubDistrict"
        else:
            sql = "SELECT * FROM tblProperty"  # Fallback if property_list is empty
        df = pd.read_sql(sql, cnxn)

        # Path to the Excel template
        path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None)

        template_path = path + '\\InfinyRealty_OddSheet_Excel_Image_template.xlsx'
        wb = load_workbook(template_path)
        sheet = wb.active  # or specify the sheet name with wb['SheetName']

        # Select a specific worksheet by name
        sheet_name = '繁'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
            cursor = cnxn.cursor()
            sql = "select FileName from V_PropertyFullList where propertyid = "+str(row.get('PropertyID', ''))
            cursor.execute(sql)
            property_view_list = cursor.fetchall()
            cursor.close()
            if property_view_list:
                FileName = property_view_list[0].FileName
                if FileName:
                    image_path = getattr(settings, "PATH_PROPERTY", None) + str(row.get('PropertyID', '')) + "\\" + FileName
                else:
                    image_path = ""

            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地區 (" + row.get('SubDistrict', '') + ")"
                sheet.row_dimensions[RowNo].height = 20
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter

            # Check if the image file exists
            if os.path.exists(image_path):
                print("Image file exists.")
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
                if not any(image_path.endswith(ext) for ext in valid_extensions):
                    print("Invalid image file format.")
                else:
                    try:
                        img = Image(image_path)  # Correct usage
                        img.width = 140  # Set width in pixels
                        img.height = 90  # Set height in pixels
                        img.anchor = f'B{RowNo}'  # Adjust the cell reference as needed
                        sheet.add_image(img)
                    except Exception as e:
                        print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")

            sheet[f'C{RowNo}'] = row.get('PropertyName', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'D{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'E{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'F{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'G{RowNo}'] = row.get('Tenant', '')
            sheet[f'H{RowNo}'] = row.get('Possession', '')

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'I{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'J{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'K{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'K{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'L{RowNo}'] = row.get('Rent', '')
            sheet[f'M{RowNo}'] = row.get('NetArea', '')
            sheet[f'N{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'O{RowNo}'] = row.get('Yield', '')
            sheet[f'P{RowNo}'] = row.get('FinalPrice', '')
            sheet[f'Q{RowNo}'] = row.get('Decoration', '')
            sheet[f'R{RowNo}'] = row.get('Views', '')
            sheet[f'S{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')


        # Select a specific worksheet by name
        sheet_name = '简'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
            cursor = cnxn.cursor()
            sql = "select FileName from V_PropertyFullList where propertyid = "+str(row.get('PropertyID', ''))
            cursor.execute(sql)
            property_view_list = cursor.fetchall()
            cursor.close()
            if property_view_list:
                FileName = property_view_list[0].FileName
                if FileName:
                    image_path = getattr(settings, "PATH_PROPERTY", None) + str(row.get('PropertyID', '')) + "\\" + FileName
                else:
                    image_path = ""

            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地区 (" + row.get('SubDistrict_s', '') + ")"
                sheet.row_dimensions[RowNo].height = 20
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter

            # Check if the image file exists
            if os.path.exists(image_path):
                print("Image file exists.")
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
                if not any(image_path.endswith(ext) for ext in valid_extensions):
                    print("Invalid image file format.")
                else:
                    try:
                        img = Image(image_path)  # Correct usage
                        img.width = 140  # Set width in pixels
                        img.height = 90  # Set height in pixels
                        img.anchor = f'B{RowNo}'  # Adjust the cell reference as needed
                        sheet.add_image(img)
                    except Exception as e:
                        print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")

            sheet[f'C{RowNo}'] = row.get('PropertyName_s', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'D{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'E{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'F{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'G{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "商议"
            if row.get('Possession', '') == "現吉":
                Possession = "现吉"
            if row.get('Possession', '') == "連租約":
                Possession = "连租约"
            if row.get('Possession', '') == "已租":
                Possession = "已租"
            if row.get('Possession', '') == "已售":
                Possession = "已售"
            sheet[f'H{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'I{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'J{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'K{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'K{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'L{RowNo}'] = row.get('Rent', '')
            sheet[f'M{RowNo}'] = row.get('NetArea', '')
            sheet[f'N{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'O{RowNo}'] = row.get('Yield', '')
            sheet[f'P{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "基本裝修"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "精致装修"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "豪裝裝修"
            sheet[f'Q{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "望山景"
            if row.get('Views', '') == "望園景":
                Views = "望园景"
            if row.get('Views', '') == "望開揚景":
                Views = "望开扬景"
            if row.get('Views', '') == "望樓景":
                Views = "望开扬景"
            if row.get('Views', '') == "望市景":
                Views = "望市景"
            if row.get('Views', '') == "望海景":
                Views = "望海景"
            if row.get('Views', '') == "望河景":
                Views = "望河景"
            if row.get('Views', '') == "望泳池景":
                Views = "望泳池景"
            sheet[f'R{RowNo}'] = Views
            sheet[f'S{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Select a specific worksheet by name
        sheet_name = 'ENG'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
            cursor = cnxn.cursor()
            sql = "select FileName from V_PropertyFullList where propertyid = "+str(row.get('PropertyID', ''))
            cursor.execute(sql)
            property_view_list = cursor.fetchall()
            cursor.close()
            if property_view_list:
                FileName = property_view_list[0].FileName
                if FileName:
                    image_path = getattr(settings, "PATH_PROPERTY", None) + str(row.get('PropertyID', '')) + "\\" + FileName
                else:
                    image_path = ""

            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "District (" + row.get('SubDistrict_e', '') + ")"
                sheet.row_dimensions[RowNo].height = 20
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter
            # Check if the image file exists
            if os.path.exists(image_path):
                print("Image file exists.")
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
                if not any(image_path.endswith(ext) for ext in valid_extensions):
                    print("Invalid image file format.")
                else:
                    try:
                        img = Image(image_path)  # Correct usage
                        img.width = 140  # Set width in pixels
                        img.height = 90  # Set height in pixels
                        img.anchor = f'B{RowNo}'  # Adjust the cell reference as needed
                        sheet.add_image(img)
                    except Exception as e:
                        print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")

            sheet[f'C{RowNo}'] = row.get('PropertyName_e', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'D{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'E{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'F{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'G{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "Discuss"
            if row.get('Possession', '') == "現吉":
                Possession = "Now auspicious"
            if row.get('Possession', '') == "連租約":
                Possession = "With lease"
            if row.get('Possession', '') == "已租":
                Possession = "Rented"
            if row.get('Possession', '') == "已售":
                Possession = "Sold"
            sheet[f'H{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'I{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[f'J{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'K{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'K{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'L{RowNo}'] = row.get('Rent', '')
            sheet[f'M{RowNo}'] = row.get('NetArea', '')
            sheet[f'N{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'O{RowNo}'] = row.get('Yield', '')
            sheet[f'P{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "Basic Decoration"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "Exquisite Decoration"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "Luxurious Decoration"
            sheet[f'Q{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "Mountain view"
            if row.get('Views', '') == "望園景":
                Views = "Garden view"
            if row.get('Views', '') == "望開揚景":
                Views = "Open view"
            if row.get('Views', '') == "望樓景":
                Views = "Tower view"
            if row.get('Views', '') == "望市景":
                Views = "City view"
            if row.get('Views', '') == "望海景":
                Views = "Sea view"
            if row.get('Views', '') == "望河景":
                Views = "River view"
            if row.get('Views', '') == "望泳池景":
                Views = "Pool view"
            sheet[f'R{RowNo}'] = Views
            sheet[f'S{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Save the workbook
        output_path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\物業盤紙連圖(列表)_"+datetime_str+".xlsx"
        wb.save(output_path)

        # Close the database connection
        cnxn.close()

        if os.path.exists(output_path):
            with open(output_path, 'rb') as fh:
                response = HttpResponse(
                    fh.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response['Content-Disposition'] = f'attachment; filename="物業盤紙連圖(列表)_{datetime_str}.xlsx"'



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
            "property_floorplan_list": property_floorplan_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "propertyid_list": propertyid_list,
            "lang": lang,
            "today": today,
        }
    if action == "property_oddsheet_multi":
        propertyid = request.POST.get('propertyid')
        lang = request.POST.get('lang')
        if propertyid is None or propertyid == "":
            propertyid = 0
        propertyid_list = request.POST.get('propertyid_list').split(",")
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        # property_list = Propertys.objects.using('infinyrealty').filter(propertyid__in=propertyid_list)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyFullList where propertyid IN (" + request.POST.get('propertyid_list') + ")")
        property_list = cursor.fetchall()
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").exclude(filename__endswith=".mp4").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')

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
            "property_floorplan_list": property_floorplan_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "lang": lang,
            "today": today,
        }
    if action == "property_offer":
        propertyid = request.POST.get('propertyid')
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')
        datetime_dt = datetime.datetime.today()
        draftdate = datetime_dt
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact where propertyid = '" + str(propertyid) + "' order by createdate desc")
        property_contact_list = cursor.fetchall()

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
            "property_contact_list": property_contact_list,
            "draftdate": draftdate,
            "today": today,
        }
    if action == "property_contact":
        propertyid = request.POST.get('propertyid')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact where propertyid = '" + str(propertyid) + "' order by createdate desc")
        property_contact_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "propertyid": propertyid,
            "property_list": property_list,
            "property_contact_list": property_contact_list,
        }
    if action == "property_contact_property":
        contact_type = request.POST.get('contact_type')
        contact_data = request.POST.get('contact_data')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if contact_type == "company":
            cursor.execute("select * from V_PropertyContactCompanyFull where Company = N'" + str(contact_data) + "' order by modifydate desc")
        if contact_type == "person":
            cursor.execute("select * from V_PropertyContactPersonFull where Person = N'" + str(contact_data) + "' order by modifydate desc")
        if contact_type == "phone":
            cursor.execute("select * from V_PropertyContactPhoneFull where ContactInfo = N'" + str(contact_data) + "' order by modifydate desc")
        property_contact_property_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "contact_type": contact_type,
            "contact_data": contact_data,
            "property_contact_property_list": property_contact_property_list,
        }
    if action == "property_follow":
        propertyid = request.POST.get('propertyid')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyFollow where propertyid = '" + str(propertyid) + "' order by followdate desc")
        property_follow_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "propertyid": propertyid,
            "property_list": property_list,
            "property_follow_list": property_follow_list,
        }
    if action == "export_excel":
        usage = request.POST.get('usage')
        if usage == "None":
            usage = "全部本地物業"
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage == "全部本地物業":
            sql = "select * from tblProperty where propertyid <> 0"
        else:
            sql = "select * from tblProperty where propertyid <> 0 and usage = N'" + str(usage) + "'"

        df = pd.read_sql(sql, cnxn)

        # Close the connection
        cnxn.close()

        # Export the DataFrame to an Excel file
        output_file = getattr(settings, "PATH_PROPERTY", None) + "匯出_"+usage+".xlsx"
        df.to_excel(output_file, index=False, engine='openpyxl')
        if os.path.exists(output_file):
            with open(output_file, 'rb') as fh:
                response = HttpResponse(
                    fh.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response['Content-Disposition'] = f'attachment; filename="匯出_{usage}.xlsx"'
                return JsonResponse({
                    'message': 'File uploaded and processed successfully!',
                    'file_url': f'/static/dist/img-web/property-cms/匯出_{usage}.xlsx'  # Adjust the path based on your URL routing
                })
                #return response
        return HttpResponse('Export Success')
    if action == "import_excel":
        usage = request.POST.get('usage')
        return HttpResponse('Import Success')
    if action == "export_oddsheet_raw":
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")
        propertyid_list = request.POST.get('propertyid_list')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if propertyid_list:
            # Convert the string into a list and format for SQL
            property_ids = propertyid_list.strip("[]").replace("'", "").split(',')
            formatted_ids = ','.join(f"'{id.strip()}'" for id in property_ids)  # Add quotes around each ID
            sql = f"SELECT * FROM tblProperty WHERE PropertyID IN ({formatted_ids})"
        else:
            sql = "SELECT * FROM tblProperty"  # Fallback if property_list is empty
        df = pd.read_sql(sql, cnxn)

        # Close the connection
        cnxn.close()

        # Export the DataFrame to an Excel file
        output_file = getattr(settings, "PATH_PROPERTY", None) + "匯出已選物業資料_"+datetime_str+".xlsx"
        df.to_excel(output_file, index=False, engine='openpyxl')
        if os.path.exists(output_file):
            with open(output_file, 'rb') as fh:
                response = HttpResponse(
                    fh.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response['Content-Disposition'] = f'attachment; filename="匯出已選物業資料_{datetime_str}.xlsx"'
                return JsonResponse({
                    'message': 'File uploaded and processed successfully!',
                    'file_url': f'/static/dist/img-web/property-cms/匯出已選物業資料_{datetime_str}.xlsx'  # Adjust the path based on your URL routing
                })
                #return response
        return HttpResponse('Export Success')
    if action == "export_oddsheet_excel":
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")
        propertyid_list = request.POST.get('propertyid_list')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if propertyid_list:
            # Convert the string into a list and format for SQL
            property_ids = propertyid_list.strip("[]").replace("'", "").split(',')
            formatted_ids = ','.join(f"'{id.strip()}'" for id in property_ids)  # Add quotes around each ID
            sql = f"SELECT * FROM tblProperty WHERE PropertyID IN ({formatted_ids}) order by SubDistrict"
        else:
            sql = "SELECT * FROM tblProperty"  # Fallback if property_list is empty
        df = pd.read_sql(sql, cnxn)

        # Path to the Excel template
        path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None)

        template_path = path + '\\InfinyRealty_OddSheet_Excel_template.xlsx'
        wb = load_workbook(template_path)
        sheet = wb.active  # or specify the sheet name with wb['SheetName']

        # Select a specific worksheet by name
        sheet_name = '繁'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            image_path = getattr(settings, "PATH_PROPERTY", None) + str(row.get('PropertyID', '')) + "\\" + "20240815_133107.jpg"
            #image_path = "D:\\Website\\InfinyRealty\\static\\dist\\img-web\\property-cms\\13\\20240815_133107.jpg"
            image_path = "//static//dist/img-web//property-cms//13//20240815_133107.jpg"


            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地區 (" + row.get('SubDistrict', '') + ")"
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter

            # Check if the image file exists
            if os.path.exists(image_path):
                try:
                    img = Image(image_path)  # Correct usage
                    img.anchor = 'A1'  # Adjust the cell reference as needed
                    sheet.add_image(img)
                except Exception as e:
                    print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")


            sheet[f'B{RowNo}'] = row.get('PropertyName', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'C{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'D{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'E{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'F{RowNo}'] = row.get('Tenant', '')
            sheet[f'G{RowNo}'] = row.get('Possession', '')

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'H{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'I{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'J{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'J{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'K{RowNo}'] = row.get('Rent', '')
            sheet[f'L{RowNo}'] = row.get('NetArea', '')
            sheet[f'M{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'N{RowNo}'] = row.get('Yield', '')
            sheet[f'O{RowNo}'] = row.get('FinalPrice', '')
            sheet[f'P{RowNo}'] = row.get('Decoration', '')
            sheet[f'Q{RowNo}'] = row.get('Views', '')
            sheet[f'R{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')


        # Select a specific worksheet by name
        sheet_name = '简'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地区 (" + row.get('SubDistrict_s', '') + ")"
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter
            sheet[f'B{RowNo}'] = row.get('PropertyName_s', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'C{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'D{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'E{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'F{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "商议"
            if row.get('Possession', '') == "現吉":
                Possession = "现吉"
            if row.get('Possession', '') == "連租約":
                Possession = "连租约"
            if row.get('Possession', '') == "已租":
                Possession = "已租"
            if row.get('Possession', '') == "已售":
                Possession = "已售"
            sheet[f'G{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'H{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'I{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'J{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'J{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'K{RowNo}'] = row.get('Rent', '')
            sheet[f'L{RowNo}'] = row.get('NetArea', '')
            sheet[f'M{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'N{RowNo}'] = row.get('Yield', '')
            sheet[f'O{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "基本裝修"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "精致装修"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "豪裝裝修"
            sheet[f'P{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "望山景"
            if row.get('Views', '') == "望園景":
                Views = "望园景"
            if row.get('Views', '') == "望開揚景":
                Views = "望开扬景"
            if row.get('Views', '') == "望樓景":
                Views = "望开扬景"
            if row.get('Views', '') == "望市景":
                Views = "望市景"
            if row.get('Views', '') == "望海景":
                Views = "望海景"
            if row.get('Views', '') == "望河景":
                Views = "望河景"
            if row.get('Views', '') == "望泳池景":
                Views = "望泳池景"
            sheet[f'Q{RowNo}'] = Views
            sheet[f'R{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Select a specific worksheet by name
        sheet_name = 'ENG'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "District (" + row.get('SubDistrict_e', '') + ")"
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter
            sheet[f'B{RowNo}'] = row.get('PropertyName_e', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'C{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'D{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'E{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'F{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "Discuss"
            if row.get('Possession', '') == "現吉":
                Possession = "Now auspicious"
            if row.get('Possession', '') == "連租約":
                Possession = "With lease"
            if row.get('Possession', '') == "已租":
                Possession = "Rented"
            if row.get('Possession', '') == "已售":
                Possession = "Sold"
            sheet[f'G{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'H{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'I{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'J{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'J{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'K{RowNo}'] = row.get('Rent', '')
            sheet[f'L{RowNo}'] = row.get('NetArea', '')
            sheet[f'M{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'N{RowNo}'] = row.get('Yield', '')
            sheet[f'O{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "Basic Decoration"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "Exquisite Decoration"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "Luxurious Decoration"
            sheet[f'P{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "Mountain view"
            if row.get('Views', '') == "望園景":
                Views = "Garden view"
            if row.get('Views', '') == "望開揚景":
                Views = "Open view"
            if row.get('Views', '') == "望樓景":
                Views = "Tower view"
            if row.get('Views', '') == "望市景":
                Views = "City view"
            if row.get('Views', '') == "望海景":
                Views = "Sea view"
            if row.get('Views', '') == "望河景":
                Views = "River view"
            if row.get('Views', '') == "望泳池景":
                Views = "Pool view"
            sheet[f'Q{RowNo}'] = Views
            sheet[f'R{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Save the workbook
        output_path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\物業盤紙(列表)_"+datetime_str+".xlsx"
        wb.save(output_path)

        # Close the database connection
        cnxn.close()

        if os.path.exists(output_path):
            with open(output_path, 'rb') as fh:
                response = HttpResponse(
                    fh.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response['Content-Disposition'] = f'attachment; filename="物業盤紙(列表)_{datetime_str}.xlsx"'
                return JsonResponse({
                    'message': 'File uploaded and processed successfully!',
                    'file_url': f'/static/dist/img-web/oddsheet/物業盤紙(列表)_{datetime_str}.xlsx'  # Adjust the path based on your URL routing
                })
                #return response
        return HttpResponse('Export Success')

    if action == "export_oddsheet_image":
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y%m%d")
        propertyid_list = request.POST.get('propertyid_list')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if propertyid_list:
            # Convert the string into a list and format for SQL
            property_ids = propertyid_list.strip("[]").replace("'", "").split(',')
            formatted_ids = ','.join(f"'{id.strip()}'" for id in property_ids)  # Add quotes around each ID
            sql = f"SELECT * FROM tblProperty WHERE PropertyID IN ({formatted_ids}) order by SubDistrict"
        else:
            sql = "SELECT * FROM tblProperty"  # Fallback if property_list is empty
        df = pd.read_sql(sql, cnxn)

        # Path to the Excel template
        path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None)

        template_path = path + '\\InfinyRealty_OddSheet_Excel_Image_template.xlsx'
        wb = load_workbook(template_path)
        sheet = wb.active  # or specify the sheet name with wb['SheetName']

        # Select a specific worksheet by name
        sheet_name = '繁'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
            cursor = cnxn.cursor()
            sql = "select FileName from V_PropertyFullList where propertyid = "+str(row.get('PropertyID', ''))
            cursor.execute(sql)
            property_view_list = cursor.fetchall()
            cursor.close()
            if property_view_list:
                FileName = property_view_list[0].FileName
                if FileName:
                    image_path = getattr(settings, "PATH_PROPERTY", None) + str(row.get('PropertyID', '')) + "\\" + FileName
                else:
                    image_path = ""

            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地區 (" + row.get('SubDistrict', '') + ")"
                sheet.row_dimensions[RowNo].height = 20
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter

            # Check if the image file exists
            if os.path.exists(image_path):
                print("Image file exists.")
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
                if not any(image_path.endswith(ext) for ext in valid_extensions):
                    print("Invalid image file format.")
                else:
                    try:
                        img = Image(image_path)  # Correct usage
                        img.width = 140  # Set width in pixels
                        img.height = 90  # Set height in pixels
                        img.anchor = f'B{RowNo}'  # Adjust the cell reference as needed
                        sheet.add_image(img)
                    except Exception as e:
                        print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")

            sheet[f'C{RowNo}'] = row.get('PropertyName', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'D{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'E{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'F{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'G{RowNo}'] = row.get('Tenant', '')
            sheet[f'H{RowNo}'] = row.get('Possession', '')

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'I{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'J{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'K{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'K{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'L{RowNo}'] = row.get('Rent', '')
            sheet[f'M{RowNo}'] = row.get('NetArea', '')
            sheet[f'N{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'O{RowNo}'] = row.get('Yield', '')
            sheet[f'P{RowNo}'] = row.get('FinalPrice', '')
            sheet[f'Q{RowNo}'] = row.get('Decoration', '')
            sheet[f'R{RowNo}'] = row.get('Views', '')
            sheet[f'S{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')


        # Select a specific worksheet by name
        sheet_name = '简'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
            cursor = cnxn.cursor()
            sql = "select FileName from V_PropertyFullList where propertyid = "+str(row.get('PropertyID', ''))
            cursor.execute(sql)
            property_view_list = cursor.fetchall()
            cursor.close()
            if property_view_list:
                FileName = property_view_list[0].FileName
                if FileName:
                    image_path = getattr(settings, "PATH_PROPERTY", None) + str(row.get('PropertyID', '')) + "\\" + FileName
                else:
                    image_path = ""

            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "地区 (" + row.get('SubDistrict_s', '') + ")"
                sheet.row_dimensions[RowNo].height = 20
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter

            # Check if the image file exists
            if os.path.exists(image_path):
                print("Image file exists.")
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
                if not any(image_path.endswith(ext) for ext in valid_extensions):
                    print("Invalid image file format.")
                else:
                    try:
                        img = Image(image_path)  # Correct usage
                        img.width = 140  # Set width in pixels
                        img.height = 90  # Set height in pixels
                        img.anchor = f'B{RowNo}'  # Adjust the cell reference as needed
                        sheet.add_image(img)
                    except Exception as e:
                        print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")

            sheet[f'C{RowNo}'] = row.get('PropertyName_s', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'D{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'E{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'F{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'G{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "商议"
            if row.get('Possession', '') == "現吉":
                Possession = "现吉"
            if row.get('Possession', '') == "連租約":
                Possession = "连租约"
            if row.get('Possession', '') == "已租":
                Possession = "已租"
            if row.get('Possession', '') == "已售":
                Possession = "已售"
            sheet[f'H{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'I{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[
                f'J{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'K{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'K{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'L{RowNo}'] = row.get('Rent', '')
            sheet[f'M{RowNo}'] = row.get('NetArea', '')
            sheet[f'N{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'O{RowNo}'] = row.get('Yield', '')
            sheet[f'P{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "基本裝修"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "精致装修"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "豪裝裝修"
            sheet[f'Q{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "望山景"
            if row.get('Views', '') == "望園景":
                Views = "望园景"
            if row.get('Views', '') == "望開揚景":
                Views = "望开扬景"
            if row.get('Views', '') == "望樓景":
                Views = "望开扬景"
            if row.get('Views', '') == "望市景":
                Views = "望市景"
            if row.get('Views', '') == "望海景":
                Views = "望海景"
            if row.get('Views', '') == "望河景":
                Views = "望河景"
            if row.get('Views', '') == "望泳池景":
                Views = "望泳池景"
            sheet[f'R{RowNo}'] = Views
            sheet[f'S{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Select a specific worksheet by name
        sheet_name = 'ENG'  # Replace with the actual sheet name
        if sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
        else:
            raise ValueError(f"Sheet '{sheet_name}' does not exist in the workbook.")

        RowNo = 2
        TempSubDistrict = ""
        # Fill data into specific columns (example: A and B)
        for index, row in df.iterrows():
            cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
            cursor = cnxn.cursor()
            sql = "select FileName from V_PropertyFullList where propertyid = "+str(row.get('PropertyID', ''))
            cursor.execute(sql)
            property_view_list = cursor.fetchall()
            cursor.close()
            if property_view_list:
                FileName = property_view_list[0].FileName
                if FileName:
                    image_path = getattr(settings, "PATH_PROPERTY", None) + str(row.get('PropertyID', '')) + "\\" + FileName
                else:
                    image_path = ""

            SubDistrict = row.get('SubDistrict', '')
            if TempSubDistrict != SubDistrict:
                if RowNo != 2:
                    RowNo = RowNo + 1
                sheet[f'A{RowNo}'] = "District (" + row.get('SubDistrict_e', '') + ")"
                sheet.row_dimensions[RowNo].height = 20
                Counter = 0
            RowNo = RowNo + 1
            Counter = Counter + 1
            sheet[f'A{RowNo}'] = Counter
            # Check if the image file exists
            if os.path.exists(image_path):
                print("Image file exists.")
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
                if not any(image_path.endswith(ext) for ext in valid_extensions):
                    print("Invalid image file format.")
                else:
                    try:
                        img = Image(image_path)  # Correct usage
                        img.width = 140  # Set width in pixels
                        img.height = 90  # Set height in pixels
                        img.anchor = f'B{RowNo}'  # Adjust the cell reference as needed
                        sheet.add_image(img)
                    except Exception as e:
                        print(f"Failed to load image: {e}")
            else:
                print(f"Error: The image file at {image_path} does not exist.")

            sheet[f'C{RowNo}'] = row.get('PropertyName_e', '') + " (" + row.get('PropertyNo', '') + ")"
            sheet[f'D{RowNo}'] = row.get('GrossArea', '')

            # Handle potential None values for SellingPrice and UnitPrice
            selling_price = row.get('SellingPrice', '')
            unit_price = row.get('UnitPrice', '')
            sheet[f'E{RowNo}'] = f"{selling_price} (@{unit_price})" if selling_price or unit_price else ''

            sheet[f'F{RowNo}'] = row.get('RentalPeriod', '')
            sheet[f'G{RowNo}'] = row.get('Tenant', '')
            Possession = ""
            if row.get('Possession', '') == "商議":
                Possession = "Discuss"
            if row.get('Possession', '') == "現吉":
                Possession = "Now auspicious"
            if row.get('Possession', '') == "連租約":
                Possession = "With lease"
            if row.get('Possession', '') == "已租":
                Possession = "Rented"
            if row.get('Possession', '') == "已售":
                Possession = "Sold"
            sheet[f'H{RowNo}'] = Possession

            # Handle potential None values for Rent and UnitRent
            rent = row.get('Rent', '')
            unit_rent = row.get('UnitRent', '')
            sheet[f'I{RowNo}'] = f"{rent} (@{unit_rent})" if rent or unit_rent else ''

            # Handle potential None values for ManagementFee and UnitManagementFee
            management_fee = row.get('ManagementFee', '')
            unit_management_fee = row.get('UnitManagementFee', '')
            sheet[f'J{RowNo}'] = f"{management_fee} (@{unit_management_fee})" if management_fee or unit_management_fee else ''

            # Handle potential None values for Rates and UnitRates
            rates = row.get('Rates', '')
            unit_rates = row.get('UnitRates', '')
            # Use pd.isna() to check for NaN values
            if not pd.isna(rates) and rates != "nan":
                # Construct the output string only if both rates and unit_rates are not NaN
                sheet[f'K{RowNo}'] = f"{rates} (@{unit_rates})" if pd.notna(unit_rates) else str(rates)
            else:
                sheet[f'K{RowNo}'] = ''  # Set to empty if rates is NaN or "nan"

            sheet[f'L{RowNo}'] = row.get('Rent', '')
            sheet[f'M{RowNo}'] = row.get('NetArea', '')
            sheet[f'N{RowNo}'] = row.get('CurrentRent', '')
            sheet[f'O{RowNo}'] = row.get('Yield', '')
            sheet[f'P{RowNo}'] = row.get('FinalPrice', '')
            Decoration = ""
            if row.get('Decoration', '') == "基本裝修":
                Decoration = "Basic Decoration"
            if row.get('Decoration', '') == "精緻裝修":
                Decoration = "Exquisite Decoration"
            if row.get('Decoration', '') == "豪裝裝修":
                Decoration = "Luxurious Decoration"
            sheet[f'Q{RowNo}'] = Decoration
            Views = ""
            if row.get('Views', '') == "望山景":
                Views = "Mountain view"
            if row.get('Views', '') == "望園景":
                Views = "Garden view"
            if row.get('Views', '') == "望開揚景":
                Views = "Open view"
            if row.get('Views', '') == "望樓景":
                Views = "Tower view"
            if row.get('Views', '') == "望市景":
                Views = "City view"
            if row.get('Views', '') == "望海景":
                Views = "Sea view"
            if row.get('Views', '') == "望河景":
                Views = "River view"
            if row.get('Views', '') == "望泳池景":
                Views = "Pool view"
            sheet[f'R{RowNo}'] = Views
            sheet[f'S{RowNo}'] = row.get('Remarks', '')
            TempSubDistrict = row.get('SubDistrict', '')

        # Save the workbook
        output_path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\物業盤紙連圖(列表)_"+datetime_str+".xlsx"
        wb.save(output_path)

        # Close the database connection
        cnxn.close()

        if os.path.exists(output_path):
            with open(output_path, 'rb') as fh:
                response = HttpResponse(
                    fh.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response['Content-Disposition'] = f'attachment; filename="物業盤紙連圖(列表)_{datetime_str}.xlsx"'
                return JsonResponse({
                    'message': 'File uploaded and processed successfully!',
                    'file_url': f'/static/dist/img-web/oddsheet/物業盤紙連圖(列表)_{datetime_str}.xlsx'  # Adjust the path based on your URL routing
                })
                #return response

        return HttpResponse('Export Success')
    if action == "main_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')

        try:
            PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.ismain = 1
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "approve_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')
        approve = request.POST.get('approve')

        try:
            PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.isapprove = approve
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "delete_picture":
        fileid = request.POST.get('fileid')

        try:
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.delete()
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "save_file_order":
        fileid = request.POST.get('fileid')
        sequence = request.POST.get('order')

        try:
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.sequence = sequence
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "request_review":
        usage = request.POST.get('usage')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None or usage == "" :
            cursor.execute("select * from tblProperty where approved = 0")
        else:
            cursor.execute("select * from tblProperty where usage = N'" + usage + "' and approved = 0")
        usageapproveright_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "usageapproveright_list": usageapproveright_list,
        }
    if action == "request_review_update":
        propertyid = request.POST.get('propertyid')

        try:
            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
            #property.post = post
            #property.functionid = functionid
            property.approved = 1
            property.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "create_offer":
        propertyid = request.POST.get('propertyid')
        propertyno = request.POST.get('propertyno')
        propertyname = request.POST.get('propertyname')
        buyername = request.POST.get('buyername')
        draftdate = request.POST.get('draftdate')
        initialpaymentdate = request.POST.get('initialpaymentdate')
        snpdate = request.POST.get('snpdate')
        finalpaymentdate = request.POST.get('finalpaymentdate')
        #draftdate = "07/05/2024"
        #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        #date = datetime.datetime.strptime(draftdate, "%d/%m/%Y")
        date = datetime.datetime.strptime(draftdate, "%Y-%m-%d")
        formatted_draftdate = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(initialpaymentdate, "%Y-%m-%d")
        formatted_settledate1 = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(snpdate, "%Y-%m-%d")
        formatted_settledate2 = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(finalpaymentdate, "%Y-%m-%d")
        formatted_settledate3 = date.strftime("%dth %B %Y")
        purchasingprice = request.POST.get('purchasingprice')
        agencyfee = str(float(purchasingprice)/100)
        grossarea = request.POST.get('grossarea')
        netarea = request.POST.get('netarea')

        path = getattr(settings, "PATH_OFFER_TEMPLATE", None)
        doc = Document(path + '\\InfinyRealty_OfferLetter_template.docx')

        # Find and replace text in the template
        for paragraph in doc.paragraphs:
            if '@draft_date' in paragraph.text:
                paragraph.text = paragraph.text.replace('@draft_date', formatted_draftdate)
            if '@buyer_name' in paragraph.text:
                paragraph.text = paragraph.text.replace('@buyer_name', buyername)
            if '@property_name' in paragraph.text:
                paragraph.text = paragraph.text.replace('@property_name', propertyname)
            if '@purchasing_price' in paragraph.text:
                paragraph.text = paragraph.text.replace('@purchasing_price', purchasingprice)
            if '@agency_fee' in paragraph.text:
                paragraph.text = paragraph.text.replace('@agency_fee', agencyfee)
            if '@gross_area' in paragraph.text:
                paragraph.text = paragraph.text.replace('@gross_area', grossarea)
            if '@net_area' in paragraph.text:
                paragraph.text = paragraph.text.replace('@net_area', netarea)
            if '@settle_date1' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date1', formatted_settledate1)
            if '@settle_date2' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date2', formatted_settledate2)
            if '@settle_date3' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date3', formatted_settledate3)

        # Save the modified Docx as a new file
        folder_path = path + "\\" + str(propertyid) + "//"
        os.makedirs(folder_path, exist_ok=True)
        new_file_path = path + "\\" + propertyid + '\\InfinyRealty_OfferLetter_' + propertyno + '.docx'
        doc.save(new_file_path)

        # Open the file for reading
        with open(new_file_path, 'rb') as file:
            # Create a FileResponse and specify the content type as 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response = FileResponse(file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            # Set the content-disposition header to trigger the file download dialog with the specified filename
            response['Content-Disposition'] = 'attachment; filename="InfinyRealty_OfferLetter_' + propertyno + '.docx"'

            # Delete the generated file after sending the response
            #os.remove(new_file_path)

        return HttpResponse('Create Success')
    return render(request, "property_template/property_response.html", context)

def download_oddsheet_excel(request):
    if not request.session.get('loginid'): return redirect('login')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y%m%d")

    output_path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\物業盤紙(列表)_"+datetime_str+".xlsx"

    if os.path.exists(output_path):
        with open(output_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            # Encode the filename
            filename = f"物業盤紙(列表)_{datetime_str}.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
            return response

def download_oddsheet_image(request):
    if not request.session.get('loginid'): return redirect('login')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y%m%d")

    output_path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\物業盤紙連圖(列表)_" + datetime_str + ".xlsx"

    if os.path.exists(output_path):
        with open(output_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            # Encode the filename
            filename = f"物業盤紙連圖(列表)_{datetime_str}.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
            return response

@csrf_exempt
def property_save(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    username = request.session.get('username')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

    action = str(request.POST.get('action'))
    if action == "add" or action == "edit" or action == "delete" or action == "preview":
        propertyid = request.POST.get('propertyid')
        preview_propertyid = request.POST.get('preview_propertyid')
        usage = request.POST.get('usage')
        propertyno = request.POST.get('propertyno')
        propertyname = request.POST.get('propertyname')
        propertyname_s = request.POST.get('propertyname_s')
        propertyname_e = request.POST.get('propertyname_e')
        district = request.POST.get('district')
        subdistrict = request.POST.get('subdistrict')
        subdistrict_s = request.POST.get('subdistrict_s')
        subdistrict_e = request.POST.get('subdistrict_e')
        street = request.POST.get('street')
        street_s = request.POST.get('street_s')
        street_e = request.POST.get('street_e')
        streetno = request.POST.get('streetno')
        building = request.POST.get('building')
        building_s = request.POST.get('building_s')
        building_e = request.POST.get('building_e')
        floorzone = request.POST.get('floorzone')
        floor = request.POST.get('floor')
        unit = request.POST.get('unit')
        offertype = request.POST.get('offertype')
        possession = request.POST.get('possession')
        grossarea = request.POST.get('grossarea')
        netarea = request.POST.get('netarea')
        atticarea = request.POST.get('atticarea')
        platformarea = request.POST.get('platformarea')
        rooftoparea = request.POST.get('rooftoparea')
        gardenarea = request.POST.get('gardenarea')
        sellingprice = request.POST.get('sellingprice')
        unitprice = request.POST.get('unitprice')
        rent = request.POST.get('rent')
        unitrent = request.POST.get('unitrent')
        managementfee = request.POST.get('managementfee')
        unitmanagementfee = request.POST.get('unitmanagementfee')
        rates = request.POST.get('rates')
        unitrates = request.POST.get('unitrates')
        yield_field = request.POST.get('yield_field')
        description = request.POST.get('description')
        tenant = request.POST.get('tenant')
        currentrent = request.POST.get('currentrent')
        rentalperiod = request.POST.get('rentalperiod')
        rentalstartdate = request.POST.get('rentalstartdate')
        formerowner = request.POST.get('formerowner')
        finalprice = request.POST.get('finalprice')
        transactiondate = request.POST.get('transactiondate')

        property_area_id = json.loads(request.POST.get('property_area_id'))
        property_area_name = json.loads(request.POST.get('property_area_name'))
        property_area_grossarea = json.loads(request.POST.get('property_area_grossarea'))
        property_area_netarea = json.loads(request.POST.get('property_area_netarea'))
        
        try:
            if action == "add":
                property = Propertys()
                property.listingdate = datetime_str
                property.modifydate = datetime_str
                property.viewcounter = 0
                old_sellingprice = 0
                old_rent = 0
            else:
                property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
                property.modifydate = datetime_str
                old_sellingprice = property.sellingprice
                old_rent = property.rent
                old_offertype = property.offertype
                old_possession = property.possession
                if old_sellingprice is None:
                    old_sellingprice = ""
                if old_rent is None:
                    old_rent = ""
            old_possession = property.possession
            property.usage = usage
            property.propertyno = propertyno
            property.propertyname = propertyname
            property.propertyname_s = propertyname_s
            property.propertyname_e = propertyname_e
            property.district = district
            property.subdistrict = subdistrict
            property.subdistrict_s = subdistrict_s
            property.subdistrict_e = subdistrict_e
            property.street = street
            property.street_s = street_s
            property.street_e = street_e
            property.streetno = streetno
            property.building = building
            property.building_s = building_s
            property.building_e = building_e
            property.floorzone = floorzone
            property.floor = floor
            property.unit = unit
            property.offertype = offertype
            property.possession = possession
            property.grossarea = grossarea
            property.netarea = netarea
            property.atticarea = atticarea
            property.platformarea = platformarea
            property.rooftoparea = rooftoparea
            property.gardenarea = gardenarea
            if sellingprice == "" or sellingprice == "0":
                property.sellingprice = None
            else:
                property.sellingprice = sellingprice
            if unitprice == "" or unitprice == "0":
                property.unitprice = None
            else:
                property.unitprice = unitprice
            if rent == "" or rent == "0":
                property.rent = None
            else:
                property.rent = rent
            if unitrent == "" or unitrent == "0":
                property.unitrent = None
            else:
                property.unitrent = unitrent
            if managementfee == "" or managementfee == "0":
                property.managementfee = None
            else:
                property.managementfee = managementfee
            if unitmanagementfee == "" or unitmanagementfee == "0":
                property.unitmanagementfee = None
            else:
                property.unitmanagementfee = unitmanagementfee
            if rates == "" or rates == "0":
                property.rates = None
            else:
                property.rates = rates
            if unitrates == "" or unitrates == "0":
                property.unitrates = None
            else:
                property.unitrates = unitrates
            if yield_field is not None and yield_field:
                property.yield_field = yield_field
            elif yield_field == "":
                property.yield_field = None
            if tenant is not None: property.tenant = tenant
            if currentrent is not None and currentrent:
                property.currentrent = currentrent
            elif currentrent == "":
                property.currentrent = None
            if rentalperiod is not None: property.rentalperiod = rentalperiod
            if rentalstartdate is not None: property.rentalstartdate = rentalstartdate

            if str(old_possession) != possession and possession == "已售":
                propertycontact = PropertyContacts.objects.using('infinyrealty').filter(propertyid=propertyid)
                if propertycontact:
                    contact_list = ""
                    for contacts in propertycontact:
                        #if contacts.company == "業主":
                        contact_list = contact_list + str(contacts.company) + ","
                    property.formerowner = contact_list
            else:
                property.formerowner = formerowner
            if finalprice == "" or finalprice == "0":
                property.finalprice = None
            else:
                property.finalprice = finalprice
            if transactiondate is not None: property.transactiondate = transactiondate
            property.approved = 0
            property.agentid = 0
            property.loginid = request.session.get('loginid')

            if action == "add" or action == "edit": property.save(using='infinyrealty')
            if action == "delete": property.delete()
            if action == "preview":
                property.save(using='infinyrealty')
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
                cursor = cnxn.cursor()
                cursor.execute(f"exec spPropertyFileCopy {preview_propertyid}")
                cnxn.commit()

                source_directory = getattr(settings, "PATH_PROPERTY", None) + str(preview_propertyid) + "\\"
                destination_directory = getattr(settings, "PATH_PROPERTY", None) + "0" + "\\"
                if os.path.exists(destination_directory):
                    shutil.rmtree(destination_directory)
                shutil.copytree(source_directory, destination_directory)

                source_directory = getattr(settings, "PATH_FLOORPLAN", None) + str(preview_propertyid) + "\\"
                destination_directory = getattr(settings, "PATH_FLOORPLAN", None) + "0" + "\\"
                if os.path.exists(destination_directory):
                    shutil.rmtree(destination_directory)
                shutil.copytree(source_directory, destination_directory)

            messages.success(request, "New Poperty was created successfully.")
            
            if property.propertyid:
                for i, area_row in enumerate(property_area_name):
                    if property_area_name[i] != "": 
                        if property_area_id[i] == 0 or property_area_id[i] =="0" or property_area_id[i] =="":
                            propertyarea = PropertyArea()
                            propertyarea.listingdate = datetime_str
                        else:
                            propertyarea = PropertyArea.objects.using('infinyrealty').get(propertyareaid=property_area_id[i])
                        
                        propertyarea.propertyid = property.propertyid
                        propertyarea.name = property_area_name[i]
                        propertyarea.grossarea = property_area_grossarea[i]
                        propertyarea.netarea = property_area_netarea[i]
                        propertyarea.modifydate = datetime_str
                        propertyarea.save(using='infinyrealty')

            # Example: Save the file to a specific directory
            folder_path = getattr(settings, "PATH_PROPERTY", None) + str(propertyid) + "//"
            os.makedirs(folder_path, exist_ok=True)
            if action != "add":
                # Add follow log record
                propertyfollow = PropertyFollows()
                propertyfollow.followdate = datetime_str
                if str(old_sellingprice) != str(sellingprice) and str(old_sellingprice) is not None:
                    propertyfollow.propertyid = propertyid
                    propertyfollow.status = "跟進"
                    if sellingprice is not None and sellingprice: propertyfollow.sellingprice = sellingprice
                    if unitprice is not None and unitprice: propertyfollow.unitprice = unitprice
                    #if rent is not None and rent: propertyfollow.rent = rent
                    #if unitrent is not None and unitrent: propertyfollow.unitrent = unitrent
                    propertyfollow.description = "更改叫價"
                    propertyfollow.loginid = request.session.get('loginid')
                    propertyfollow.save(using='infinyrealty')
                propertyfollow = PropertyFollows()
                propertyfollow.followdate = datetime_str
                if str(old_rent) != str(rent) and str(old_rent) is not None:
                    propertyfollow.propertyid = propertyid
                    propertyfollow.status = "跟進"
                    #if sellingprice is not None and sellingprice: propertyfollow.sellingprice = sellingprice
                    #if unitprice is not None and unitprice: propertyfollow.unitprice = unitprice
                    if rent is not None and rent: propertyfollow.rent = rent
                    if unitrent is not None and unitrent: propertyfollow.unitrent = unitrent
                    propertyfollow.description = "更改租金"
                    propertyfollow.loginid = request.session.get('loginid')
                    propertyfollow.save(using='infinyrealty')
                if str(old_offertype) != offertype:
                    propertyfollow.propertyid = propertyid
                    propertyfollow.status = offertype
                    #if sellingprice is not None and sellingprice: propertyfollow.sellingprice = sellingprice
                    #if unitprice is not None and unitprice: propertyfollow.unitprice = unitprice
                    propertyfollow.description = "更改盤類"
                    propertyfollow.loginid = request.session.get('loginid')
                    propertyfollow.save(using='infinyrealty')
                if str(old_possession) != possession:
                    propertyfollow.propertyid = propertyid
                    propertyfollow.status = possession
                    #if sellingprice is not None and sellingprice: propertyfollow.sellingprice = sellingprice
                    #if unitprice is not None and unitprice: propertyfollow.unitprice = unitprice
                    propertyfollow.description = "更改狀況"
                    propertyfollow.loginid = request.session.get('loginid')
                    propertyfollow.save(using='infinyrealty')

                # Get the map image from Google Maps
                map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={propertyname.replace(' ', '+')}&zoom=18&markers=color:red|{propertyname.replace(' ', '+')}&size=800x600&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
                # map_url = "https://maps.googleapis.com/maps/api/staticmap?center=San+Francisco,CA&zoom=12&size=600x400&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
                response = requests.get(map_url)
                # Save the map image to a file
                with open("static/dist/img-web/property-cms/" + propertyid + "/location_map.png", "wb") as f:
                    f.write(response.content)

            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "edit_info":
        try:
            propertyid = request.POST.get('propertyid')
            availability = request.POST.get('availability')
            decoration = request.POST.get('decoration')
            views = request.POST.get('views')
            remarks = request.POST.get('remarks')
            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
            property.availability = availability
            property.decoration = decoration
            property.views = views
            property.remarks = remarks
            property.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "add_contact" or action == "edit_contact" or action == "delete_contact":
        try:
            contactid = request.POST.get('contactid')
            propertyid = request.POST.get('propertyid')
            contacttype = request.POST.get('contacttype')
            company = request.POST.get('company')
            title = request.POST.get('title')
            person = request.POST.get('person')
            address = request.POST.get('address')
            infotype = request.POST.get('infotype')
            contactinfo = request.POST.get('contactinfo')
            email = request.POST.get('email')
            ctcperson = request.POST.get('ctcperson')
            if action == "add_contact":
                propertycontact = PropertyContacts()
                propertycontact.createdate = datetime_str
            else:
                propertycontact = PropertyContacts.objects.using('infinyrealty').get(contactid=contactid)
                propertycontact.createdate = datetime_str
            propertycontact.propertyid = propertyid
            propertycontact.contacttype = contacttype
            propertycontact.company = company
            propertycontact.title = title
            propertycontact.person = person
            propertycontact.address = address
            propertycontact.infotype = infotype
            propertycontact.contactinfo = contactinfo
            propertycontact.email = email
            propertycontact.ctcperson = ctcperson
            propertycontact.status = 1
            propertycontact.loginid = request.session.get('loginid')
            if action == "delete_contact":
                propertycontact.delete()
            else:
                propertycontact.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "add_contact_log":
        try:
            accessid = request.POST.get('accessid')
            propertyid = request.POST.get('propertyid')
            property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
            accesslog(accessid, loginid, username, "display", property_list[0].propertyno, propertyid, "Show contact detail")
            propertyfollow = PropertyFollows()
            propertyfollow.followdate = datetime_str
            propertyfollow.propertyid = propertyid
            propertyfollow.status = "跟進"
            propertyfollow.description = "聯絡人查詢"
            propertyfollow.loginid = request.session.get('loginid')
            propertyfollow.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "add_follow" or action == "edit_follow" or action == "delete_follow":
        try:
            followid = request.POST.get('followid')
            propertyid = request.POST.get('propertyid')
            status = request.POST.get('status')
            sellingprice = request.POST.get('sellingprice')
            unitprice = request.POST.get('unitprice')
            rent = request.POST.get('rent')
            unitrent = request.POST.get('unitrent')
            description = request.POST.get('description')
            if action == "add_follow":
                propertyfollow = PropertyFollows()
                propertyfollow.followdate = datetime_str
            else:
                propertyfollow = PropertyFollows.objects.using('infinyrealty').get(followid=followid)
                propertyfollow.followdate = datetime_str
            if sellingprice == "": sellingprice = "0"
            if unitprice == "": unitprice = "0"
            if rent == "": rent = "0"
            if unitrent == "": unitrent = "0"
            propertyfollow.propertyid = propertyid
            propertyfollow.status = status
            propertyfollow.sellingprice = sellingprice
            propertyfollow.unitprice = unitprice
            propertyfollow.rent = rent
            propertyfollow.unitrent = unitrent
            propertyfollow.description = description
            propertyfollow.loginid = request.session.get('loginid')
            if action == "delete_follow":
                propertyfollow.delete()
            else:
                propertyfollow.save(using='infinyrealty')
            if status == "已租" or status == "已售":
                property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
                property.possession = status
                property.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

def newPropertyMain(request, propertyid=None):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    #propertyid = request.POST.get('propertyid')
    if propertyid is None:
        propertyid = ""

    accessid = 5170
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
        "user_area": 1,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "user_propertyid": propertyid,
    }
    return render(request, "property_template/newPropertyMain.html", context)

@csrf_exempt
def newPropertyMain_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.session.get('loginid')
    username = request.session.get('username')
    propertyid = request.POST.get('propertyid')
    today = datetime.datetime.now()

    if action == "menutab":
        context = {
            "action": action,
            "user_loginid": loginid,
            "user_propertyid": propertyid,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "userlist": user_list,
        }
    if action == "area_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_Area_count")
        area_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "area_view_list": area_view_list,
            "today": today,
        }
    if action == "property_view":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_Area_count")
        area_list = cursor.fetchall()
        cursor.execute("select * from V_District_NewProperty_Count")
        district_list = cursor.fetchall()

        area = request.POST.get('area')
        dname = request.POST.get('dname')
        pricemin = request.POST.get('pricemin')
        pricemax = request.POST.get('pricemax')
        if area == "" or area is None:
            area = ""
        if dname == "" or dname is None:
            dname = ""
        if pricemin == "" or pricemin is None:
            pricemin = 0
        if pricemax == "" or pricemax is None:
            pricemax = 0
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = "exec spNewProperty N'" + area + "',N'" + dname + "','" + str(pricemin) + "','" + str(pricemax) + "'"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_loginid": loginid,
            "property_view_list": property_view_list,
            "area_list": area_list,
            "district_list": district_list,
            "sql": sql,
        }
    if action == "property_edit":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        area_list = CodeDetails.objects.using('infinyrealty').filter(code_id=12).order_by('sequence')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_District_NewProperty_Count")
        district_list = cursor.fetchall()
        #district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        cursor.execute("select * from V_AddressBuilding")
        building_list = cursor.fetchall()
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        development_type_list = CodeDetails.objects.using('infinyrealty').filter(code_id=11).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')

        property_list = PropertyListings.objects.using('infinyrealty').filter(listing_id=propertyid)

        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="newphoto").order_by('-ismain','sequence')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="newfloorplan").order_by('-ismain','sequence')

        context = {
            "action": action,
            "user_loginid": loginid,
            "area_list": area_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "building_list": building_list,
            "floorzone_list": floorzone_list,
            "possession_list": possession_list,
            "development_type_list": development_type_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_info":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')
        property_document_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="document").order_by('-ismain')
        #property_photo_list = list(chain(property_file_list, property_floorplan_list))
        property_photo_list = ""

        for w in property_photo_list:
            filename = w.filename
            filename_extension = os.path.splitext(filename)[1][1:].lower()
            if "jpg" in filename_extension or "jpeg" in filename_extension or "png" in filename_extension:
                if w.filetype == "photo":
                    filename = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\"+w.filename
                    filename_wm = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\"+w.filename.replace("."+filename_extension, "-wm."+filename_extension)
                else:
                    filename = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename
                    filename_wm = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename.replace("."+filename_extension, "-wm."+filename_extension)
                filename_logo = getattr(settings, "PATH_MAIN", None) + "infinyrealty_logo_high.png"
                base_image = Image.open(filename)
                watermark_image = Image.open(filename_logo)
                if w.filetype == "photo":
                    watermark_ratio = 0.1  # 10% of the base image size
                else:
                    watermark_ratio = 0.03  # 3% of the base image size
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
                base_image.save(filename_wm)
                try:
                    PropertyFiles.objects.using('infinyrealty').filter(fileid=w.fileid).update(iswatermark=1)
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno
                    return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
                #draw = ImageDraw.Draw(image)
                #font = ImageFont.truetype("arial.ttf", size=150)
                #watermark_text = "infinyrealty.com2"
                #x = (image.width) / 2
                #y = (image.height) / 2
                #draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
                #image.save(filename_wm)

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "floorzone_list": floorzone_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_document_list": property_document_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "main_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')

        try:
            PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.ismain = 1
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "approve_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')
        approve = request.POST.get('approve')

        try:
            PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.isapprove = approve
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "save_file_order":
        fileid = request.POST.get('fileid')
        sequence = request.POST.get('order')

        try:
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.sequence = sequence
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "delete_picture":
        fileid = request.POST.get('fileid')

        try:
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.delete()
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "request_review":
        usage = request.POST.get('usage')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None or usage == "" :
            cursor.execute("select * from tblProperty where approved = 0")
        else:
            cursor.execute("select * from tblProperty where usage = N'" + usage + "' and approved = 0")
        usageapproveright_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "usageapproveright_list": usageapproveright_list,
        }
    if action == "request_review_update":
        propertyid = request.POST.get('propertyid')

        try:
            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
            #property.post = post
            #property.functionid = functionid
            property.approved = 1
            property.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "export_excel":
        area = request.POST.get('area')
        if area == "None":
            area = "全部一手新盤"
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if area == "全部一手新盤":
            sql = "select * from tblPropertyListing where listing_id <> 0 order by listing_id"
        else:
            sql = "select * from tblPropertyListing where listing_id <> 0 and area = N'" + str(area) + "' order by listing_id"
        df = pd.read_sql(sql, cnxn)

        # Close the connection
        cnxn.close()

        # Export the DataFrame to an Excel file
        output_file = getattr(settings, "PATH_PROPERTY_NEW", None) + "匯出_一手新盤_"+area+".xlsx"
        df.to_excel(output_file, index=False, engine='openpyxl')
        if os.path.exists(output_file):
            with open(output_file, 'rb') as fh:
                response = HttpResponse(
                    fh.read(),
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response['Content-Disposition'] = f'attachment; filename="匯出_一手新盤_{area}.xlsx"'
                return JsonResponse({
                    'message': 'File uploaded and processed successfully!',
                    'file_url': f'/static/dist/img-web/propertynew-cms/匯出_一手新盤_{area}.xlsx'  # Adjust the path based on your URL routing
                })
                #return response
        return HttpResponse('Export Success')
    if action == "create_offer":
        propertyid = request.POST.get('propertyid')
        propertyno = request.POST.get('propertyno')
        propertyname = request.POST.get('propertyname')
        buyername = request.POST.get('buyername')
        draftdate = request.POST.get('draftdate')
        initialpaymentdate = request.POST.get('initialpaymentdate')
        snpdate = request.POST.get('snpdate')
        finalpaymentdate = request.POST.get('finalpaymentdate')
        #draftdate = "07/05/2024"
        #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        #date = datetime.datetime.strptime(draftdate, "%d/%m/%Y")
        date = datetime.datetime.strptime(draftdate, "%Y-%m-%d")
        formatted_draftdate = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(initialpaymentdate, "%Y-%m-%d")
        formatted_settledate1 = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(snpdate, "%Y-%m-%d")
        formatted_settledate2 = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(finalpaymentdate, "%Y-%m-%d")
        formatted_settledate3 = date.strftime("%dth %B %Y")
        purchasingprice = request.POST.get('purchasingprice')
        agencyfee = str(float(purchasingprice)/100)
        grossarea = request.POST.get('grossarea')
        netarea = request.POST.get('netarea')

        path = getattr(settings, "PATH_OFFER_TEMPLATE", None)
        doc = Document(path + '\\InfinyRealty_OfferLetter_template.docx')

        # Find and replace text in the template
        for paragraph in doc.paragraphs:
            if '@draft_date' in paragraph.text:
                paragraph.text = paragraph.text.replace('@draft_date', formatted_draftdate)
            if '@buyer_name' in paragraph.text:
                paragraph.text = paragraph.text.replace('@buyer_name', buyername)
            if '@property_name' in paragraph.text:
                paragraph.text = paragraph.text.replace('@property_name', propertyname)
            if '@purchasing_price' in paragraph.text:
                paragraph.text = paragraph.text.replace('@purchasing_price', purchasingprice)
            if '@agency_fee' in paragraph.text:
                paragraph.text = paragraph.text.replace('@agency_fee', agencyfee)
            if '@gross_area' in paragraph.text:
                paragraph.text = paragraph.text.replace('@gross_area', grossarea)
            if '@net_area' in paragraph.text:
                paragraph.text = paragraph.text.replace('@net_area', netarea)
            if '@settle_date1' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date1', formatted_settledate1)
            if '@settle_date2' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date2', formatted_settledate2)
            if '@settle_date3' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date3', formatted_settledate3)

        # Save the modified Docx as a new file
        folder_path = path + "\\" + str(propertyid) + "//"
        os.makedirs(folder_path, exist_ok=True)
        new_file_path = path + "\\" + propertyid + '\\InfinyRealty_OfferLetter_' + propertyno + '.docx'
        doc.save(new_file_path)

        # Open the file for reading
        with open(new_file_path, 'rb') as file:
            # Create a FileResponse and specify the content type as 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response = FileResponse(file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            # Set the content-disposition header to trigger the file download dialog with the specified filename
            response['Content-Disposition'] = 'attachment; filename="InfinyRealty_OfferLetter_' + propertyno + '.docx"'

            # Delete the generated file after sending the response
            #os.remove(new_file_path)

        return HttpResponse('Create Success')
    return render(request, "property_template/newPropertyMain_response.html", context)

@csrf_exempt
def newPropertyMain_save(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    username = request.session.get('username')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

    action = str(request.POST.get('action'))
    if action in ["add", "edit", "delete"]:
        # Retrieve data from the request
        propertyid = request.POST.get('propertyid')
        listing_id = request.POST.get('listing_id')
        property_number = request.POST.get('property_number')
        developer = request.POST.get('developer')
        developer_s = request.POST.get('developer_s')
        developer_e = request.POST.get('developer_e')
        development_name = request.POST.get('development_name')
        development_name_s = request.POST.get('development_name_s')
        development_name_e = request.POST.get('development_name_e')
        phase = request.POST.get('phase')
        phase_s = request.POST.get('phase_s')
        phase_e = request.POST.get('phase_e')
        address = request.POST.get('address')
        address_s = request.POST.get('address_s')
        address_e = request.POST.get('address_e')
        area = request.POST.get('area')
        area_s = request.POST.get('area_s')
        area_e = request.POST.get('area_e')
        district = request.POST.get('district')
        district_s = request.POST.get('district_s')
        district_e = request.POST.get('district_e')
        development_type = request.POST.get('development_type')
        min_selling_price = request.POST.get('min_selling_price')
        num_units = request.POST.get('num_units')
        first_sale_date = request.POST.get('first_sale_date')
        estimated_completion_date = request.POST.get('estimated_completion_date')
        management_company = request.POST.get('management_company')
        management_company_s = request.POST.get('management_company_s')
        management_company_e = request.POST.get('management_company_e')
        vendor_holding_company = request.POST.get('vendor_holding_company')
        vendor_holding_company_s = request.POST.get('vendor_holding_company_s')
        vendor_holding_company_e = request.POST.get('vendor_holding_company_e')
        school_net = request.POST.get('school_net')
        school_net_s = request.POST.get('school_net_s')
        school_net_e = request.POST.get('school_net_e')
        project_details = request.POST.get('project_details')
        project_details_s = request.POST.get('project_details_s')
        project_details_e = request.POST.get('project_details_e')
        advertisement_date = request.POST.get('advertisement_date')

        try:
            if action == "add":
                property = PropertyListings()
                property.listingdate = datetime_str
                property.create_date = datetime_str
                property.viewcounter = 0
            else:
                property = PropertyListings.objects.using('infinyrealty').get(listing_id=listing_id)
                property.create_date = datetime_str
            property.property_number = property_number
            property.developer = developer
            property.developer_s = developer_s
            property.developer_e = developer_e
            property.development_name = development_name
            property.development_name_s = development_name_s
            property.development_name_e = development_name_e
            property.phase = phase
            property.phase_s = phase_s
            property.phase_e = phase_e
            property.address = address
            property.address_s = address_s
            property.address_e = address_e
            property.area = area
            property.area_s = area_s
            property.area_e = area_e
            property.district = district
            property.district_s = district_s
            property.district_e = district_e
            property.development_type = development_type
            property.min_selling_price = min_selling_price if min_selling_price not in ["", "0"] else None
            property.num_units = num_units if num_units not in ["", "0"] else None
            if first_sale_date:
                property.first_sale_date = first_sale_date
            else:
                property.first_sale_date = None
            if estimated_completion_date:
                property.estimated_completion_date = estimated_completion_date
            else:
                property.estimated_completion_date = None
            property.management_company = management_company
            property.management_company_s = management_company_s
            property.management_company_e = management_company_e
            property.vendor_holding_company = vendor_holding_company
            property.vendor_holding_company_s = vendor_holding_company_s
            property.vendor_holding_company_e = vendor_holding_company_e
            property.school_net = school_net
            property.school_net_s = school_net_s
            property.school_net_e = school_net_e
            property.project_details = project_details
            property.project_details_s = project_details_s
            property.project_details_e = project_details_e
            if advertisement_date:
                property.advertisement_date = advertisement_date
            else:
                property.advertisement_date = None
            #property.loginid = request.session.get('loginid')

            if action == "add" or action == "edit": property.save(using='infinyrealty')
            if action == "delete": property.delete()
            messages.success(request, "New Poperty was created successfully.")

            # Example: Save the file to a specific directory
            folder_path = getattr(settings, "PATH_PROPERTY_NEW", None) + str(listing_id) + "//"
            os.makedirs(folder_path, exist_ok=True)

            # Get the map image from Google Maps
            map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={address.replace(' ', '+')}&zoom=18&markers=color:red|{address.replace(' ', '+')}&size=800x600&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
            # map_url = "https://maps.googleapis.com/maps/api/staticmap?center=San+Francisco,CA&zoom=12&size=600x400&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
            response = requests.get(map_url)
            # Save the map image to a file
            with open("static/dist/img-web/propertynew-cms/" + listing_id + "/location_map.png", "wb") as f:
                f.write(response.content)

            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "edit_info":
        try:
            propertyid = request.POST.get('propertyid')
            availability = request.POST.get('availability')
            decoration = request.POST.get('decoration')
            views = request.POST.get('views')
            remarks = request.POST.get('remarks')
            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
            property.availability = availability
            property.decoration = decoration
            property.views = views
            property.remarks = remarks
            property.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "add_contact" or action == "edit_contact" or action == "delete_contact":
        try:
            contactid = request.POST.get('contactid')
            propertyid = request.POST.get('propertyid')
            contacttype = request.POST.get('contacttype')
            company = request.POST.get('company')
            title = request.POST.get('title')
            person = request.POST.get('person')
            address = request.POST.get('address')
            infotype = request.POST.get('infotype')
            contactinfo = request.POST.get('contactinfo')
            email = request.POST.get('email')
            ctcperson = request.POST.get('ctcperson')
            if action == "add_contact":
                propertycontact = PropertyContacts()
                propertycontact.createdate = datetime_str
            else:
                propertycontact = PropertyContacts.objects.using('infinyrealty').get(contactid=contactid)
                propertycontact.createdate = datetime_str
            propertycontact.propertyid = propertyid
            propertycontact.contacttype = contacttype
            propertycontact.company = company
            propertycontact.title = title
            propertycontact.person = person
            propertycontact.address = address
            propertycontact.infotype = infotype
            propertycontact.contactinfo = contactinfo
            propertycontact.email = email
            propertycontact.ctcperson = ctcperson
            propertycontact.status = 1
            propertycontact.loginid = request.session.get('loginid')
            if action == "delete_contact":
                propertycontact.delete()
            else:
                propertycontact.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "add_contact_log":
        try:
            accessid = request.POST.get('accessid')
            propertyid = request.POST.get('propertyid')
            property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
            accesslog(accessid, loginid, username, "display", property_list[0].propertyno, propertyid, "Show contact detail")
            propertyfollow = PropertyFollows()
            propertyfollow.followdate = datetime_str
            propertyfollow.propertyid = propertyid
            propertyfollow.status = "跟進"
            propertyfollow.description = "聯絡人查詢"
            propertyfollow.loginid = request.session.get('loginid')
            propertyfollow.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action == "add_follow" or action == "edit_follow" or action == "delete_follow":
        try:
            followid = request.POST.get('followid')
            propertyid = request.POST.get('propertyid')
            status = request.POST.get('status')
            sellingprice = request.POST.get('sellingprice')
            unitprice = request.POST.get('unitprice')
            rent = request.POST.get('rent')
            unitrent = request.POST.get('unitrent')
            description = request.POST.get('description')
            if action == "add_follow":
                propertyfollow = PropertyFollows()
                propertyfollow.followdate = datetime_str
            else:
                propertyfollow = PropertyFollows.objects.using('infinyrealty').get(followid=followid)
                propertyfollow.followdate = datetime_str
            if sellingprice == "": sellingprice = "0"
            if unitprice == "": unitprice = "0"
            if rent == "": rent = "0"
            if unitrent == "": unitrent = "0"
            propertyfollow.propertyid = propertyid
            propertyfollow.status = status
            propertyfollow.sellingprice = sellingprice
            propertyfollow.unitprice = unitprice
            propertyfollow.rent = rent
            propertyfollow.unitrent = unitrent
            propertyfollow.description = description
            propertyfollow.loginid = request.session.get('loginid')
            if action == "delete_follow":
                propertyfollow.delete()
            else:
                propertyfollow.save(using='infinyrealty')
            if status == "已租" or status == "已售":
                property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
                property.possession = status
                property.save(using='infinyrealty')
            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

def foreignPropertyMain(request, propertyid=None):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    #propertyid = request.POST.get('propertyid')
    if propertyid is None:
        propertyid = ""

    accessid = 5171
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
        "user_area": 1,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "user_propertyid": propertyid,
    }
    return render(request, "property_template/foreignPropertyMain.html", context)

@csrf_exempt
def foreignPropertyMain_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.session.get('loginid')
    username = request.session.get('username')
    propertyid = request.POST.get('propertyid')
    today = datetime.datetime.now()

    if action == "menutab":
        context = {
            "action": action,
            "user_loginid": loginid,
            "user_propertyid": propertyid,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "userlist": user_list,
        }
    if action == "country_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_Country_Count")
        country_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "country_view_list": country_view_list,
            "today": today,
        }
    if action == "property_view":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage = request.POST.get('usage')
        country = request.POST.get('country')
        district = request.POST.get('district')
        usage_list = CodeDetails.objects.using('infinyrealty').filter(code_id=9).filter(status=1).order_by('sequence')
        country_list = CodeDetails.objects.using('infinyrealty').filter(code_id=8).filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=14).filter(status=1).order_by('sequence')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if country is None or country == "":
            sql = "select * from V_PropertyForeignList where propertyforeignid <> 0"
        else:
            sql = "select * from V_PropertyForeignList where country = N'" + country + "' and propertyforeignid <> 0"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_loginid": loginid,
            "user_usage": usage,
            "user_country": country,
            "user_district": district,
            "property_view_list": property_view_list,
            "usage_list": usage_list,
            "country_list": country_list,
            "district_list": district_list,
            "sql": sql,
        }
    if action == "property_edit":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage_list = CodeDetails.objects.using('infinyrealty').filter(code_id=9).filter(status=1).order_by('sequence')
        country_list = CodeDetails.objects.using('infinyrealty').filter(code_id=8).filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=14).filter(status=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = PropertyForeigns.objects.using('infinyrealty').filter(propertyforeignid=propertyid)
        property_file_list = PropertyForeignFiles.objects.using('infinyrealty').filter(propertyforeignid=propertyid,filetype="photo").order_by('-ismain', 'sequence')
        property_floorplan_list = PropertyForeignFiles.objects.using('infinyrealty').filter(propertyforeignid=propertyid,filetype="floorplan").order_by('sequence')
        #property_document_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="document").order_by('-ismain')

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "country_list": country_list,
            "district_list": district_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_foreign_file_path": getattr(settings, "PATH_PROPERTY_FOREIGN", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_content":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage_list = CodeDetails.objects.using('infinyrealty').filter(code_id=9).filter(status=1).order_by('sequence')
        country_list = CodeDetails.objects.using('infinyrealty').filter(code_id=8).filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=14).filter(status=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = PropertyForeigns.objects.using('infinyrealty').filter(propertyforeignid=propertyid)
        property_file_list = PropertyForeignFiles.objects.using('infinyrealty').filter(propertyforeignid=propertyid,filetype="photo").order_by('-ismain')
        property_floorplan_list = PropertyForeignFiles.objects.using('infinyrealty').filter(propertyforeignid=propertyid,filetype="floorplan").order_by('-ismain')
        #property_document_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="document").order_by('-ismain')

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "country_list": country_list,
            "district_list": district_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_foreign_file_path": getattr(settings, "PATH_PROPERTY_FOREIGN", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "main_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')

        try:
            PropertyForeignFiles.objects.using('infinyrealty').filter(propertyforeignid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyForeignFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.ismain = 1
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "approve_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')
        approve = request.POST.get('approve')

        try:
            PropertyForeignFiles.objects.using('infinyrealty').filter(propertyforeignid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyForeignFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.isapprove = approve
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "edit_title_desc":
        fileid = request.POST.get("fileid")
        filetitle = request.POST.get("filetitle")
        filetitle_s = request.POST.get("filetitle_s")
        filetitle_e = request.POST.get("filetitle_e")
        filedescription = request.POST.get("filedescription")
        filedescription_s = request.POST.get("filedescription_s")
        filedescription_e = request.POST.get("filedescription_e")

        try:
            propertyfile = PropertyForeignFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.filetitle = filetitle
            propertyfile.filetitle_s = filetitle_s
            propertyfile.filetitle_e = filetitle_e
            propertyfile.filedescription = filedescription
            propertyfile.filedescription_s = filedescription_s
            propertyfile.filedescription_e = filedescription_e
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "edit_title":
        fileid = request.POST.get('fileid')
        filetitle = request.POST.get('filetitle')

        try:
            propertyfile = PropertyForeignFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.filetitle = filetitle
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "edit_description":
        fileid = request.POST.get('fileid')
        filedescription = request.POST.get('filedescription')

        try:
            propertyfile = PropertyForeignFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.filedescription = filedescription
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "save_file_order":
        fileid = request.POST.get('fileid')
        sequence = request.POST.get('order')

        try:
            propertyfile = PropertyForeignFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.sequence = sequence
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "delete_picture":
        fileid = request.POST.get('fileid')

        try:
            propertyfile = PropertyForeignFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.delete()
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "request_review":
        country = request.POST.get('country')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if country is None or country == "" :
            cursor.execute("select * from tblPropertyForeign where approved = 0 and propertyforeignid <> 0")
        else:
            cursor.execute("select * from tblPropertyForeign where country = N'" + country + "' and approved = 0 and propertyforeignid <> 0")
        usageapproveright_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "usageapproveright_list": usageapproveright_list,
        }
    if action == "request_review_update":
        propertyid = request.POST.get('propertyid')

        try:
            property = PropertyForeigns.objects.using('infinyrealty').get(propertyforeignid=propertyid)
            #property.post = post
            #property.functionid = functionid
            property.approved = 1
            property.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    return render(request, "property_template/foreignPropertyMain_response.html", context)

@csrf_exempt
def foreignPropertyMain_save(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    username = request.session.get('username')
    datetime_dt = datetime.datetime.today()
    datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

    action = str(request.POST.get('action'))
    if action in ["add", "edit", "delete", "preview"]:
        # Retrieve data from the request

        developer = request.POST.get('developer')
        developer_s = request.POST.get('developer_s')
        developer_e = request.POST.get('developer_e')

        propertyid = request.POST.get('propertyid')
        preview_propertyid = request.POST.get('preview_propertyid')
        propertyno = request.POST.get('propertyno')
        propertyname = request.POST.get('propertyname')
        propertyname_s = request.POST.get('propertyname_s')
        propertyname_e = request.POST.get('propertyname_e')

        projectname = request.POST.get('projectname')
        projectname_s = request.POST.get('projectname_s')
        projectname_e = request.POST.get('projectname_e')

        projectdescription = request.POST.get('projectdescription')
        projectdescription_s = request.POST.get('projectdescription_s')
        projectdescription_e = request.POST.get('projectdescription_e')

        completiondate = request.POST.get('completiondate')
        currency = request.POST.get('currency')

        usage = request.POST.get('usage')
        usage_s = request.POST.get('usage_s')
        usage_e = request.POST.get('usage_e')

        country = request.POST.get('country')
        country_s = request.POST.get('country_s')
        country_e = request.POST.get('country_e')

        unittypes = request.POST.get('unittypes')
        unittypes_s = request.POST.get('unittypes_s')
        unittypes_e = request.POST.get('unittypes_e')

        unitsizes = request.POST.get('unitsizes')
        unitsizes_s = request.POST.get('unitsizes_s')
        unitsizes_e = request.POST.get('unitsizes_e')

        offertype = request.POST.get('offertype')
        sellingprice = request.POST.get('sellingprice')

        residentialunits = request.POST.get('residentialunits')
        residentialunits_s = request.POST.get('residentialunits_s')
        residentialunits_e = request.POST.get('residentialunits_e')

        propertyfeatures = request.POST.get('propertyfeatures')
        propertyfeatures_s = request.POST.get('propertyfeatures_s')
        propertyfeatures_e = request.POST.get('propertyfeatures_e')

        district = request.POST.get('district')
        district_s = request.POST.get('district_s')
        district_e = request.POST.get('district_e')

        try:
            if action == "add":
                property = PropertyForeigns()
                property.listingdate = datetime_str
                property.modifydate = datetime_str
                property.viewcounter = 0
            else:
                property = PropertyForeigns.objects.using('infinyrealty').get(propertyforeignid=propertyid)
                property.modifydate = datetime_str

            property.developer = developer
            property.developer_s = developer_s
            property.developer_e = developer_e

            #property.propertyforeignid = propertyid
            property.propertyno = propertyno
            property.propertyname = propertyname
            property.propertyname_s = propertyname_s
            property.propertyname_e = propertyname_e

            property.projectname = projectname
            property.projectname_s = projectname_s
            property.projectname_e = projectname_e

            property.projectdescription = projectdescription
            property.projectdescription_s = projectdescription_s
            property.projectdescription_e = projectdescription_e
            property.completiondate = completiondate
            property.currency = currency

            property.usage = usage
            property.usage_s = usage_s
            property.usage_e = usage_e

            property.country = country
            property.country_s = country_s
            property.country_e = country_e

            property.unittypes = unittypes
            property.unittypes_s = unittypes_s
            property.unittypes_e = unittypes_e

            property.unitsizes = unitsizes
            property.unitsizes_s = unitsizes_s
            property.unitsizes_e = unitsizes_e

            property.offertype = offertype
            property.sellingprice = sellingprice

            property.residentialunits = residentialunits
            property.residentialunits_s = residentialunits_s
            property.residentialunits_e = residentialunits_e

            property.propertyfeatures = propertyfeatures
            property.propertyfeatures_s = propertyfeatures_s
            property.propertyfeatures_e = propertyfeatures_e

            property.district = district
            property.district_s = district_s
            property.district_e = district_e
            property.approved = 0
            property.agentid = 0
            property.loginid = request.session.get('loginid')

            #property.loginid = request.session.get('loginid')

            if action == "add" or action == "edit": property.save(using='infinyrealty')
            if action == "delete": property.delete()
            if action == "preview":
                property.save(using='infinyrealty')
                cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
                cursor = cnxn.cursor()
                cursor.execute(f"exec spPropertyForeignFileCopy {preview_propertyid}")
                cnxn.commit()

                source_directory = getattr(settings, "PATH_PROPERTY_FOREIGN", None) + str(preview_propertyid) + "\\"
                destination_directory = getattr(settings, "PATH_PROPERTY_FOREIGN", None) + "0" + "\\"
                if os.path.exists(destination_directory):
                    shutil.rmtree(destination_directory)
                shutil.copytree(source_directory, destination_directory)

                source_directory = getattr(settings, "PATH_FLOORPLAN_FOREIGN", None) + str(preview_propertyid) + "\\"
                destination_directory = getattr(settings, "PATH_FLOORPLAN_FOREIGN", None) + "0" + "\\"
                if os.path.exists(destination_directory):
                    shutil.rmtree(destination_directory)
                shutil.copytree(source_directory, destination_directory)

            messages.success(request, "New Poperty was created successfully.")
            propertyid = property.propertyforeignid

            # Example: Save the file to a specific directory
            folder_path = getattr(settings, "PATH_PROPERTY_FOREIGN", None) + str(propertyid) + "//"
            os.makedirs(folder_path, exist_ok=True)

            # Get the map image from Google Maps
            map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={propertyname.replace(' ', '+')}&zoom=18&markers=color:red|{propertyname.replace(' ', '+')}&size=800x600&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
            # map_url = "https://maps.googleapis.com/maps/api/staticmap?center=San+Francisco,CA&zoom=12&size=600x400&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
            response = requests.get(map_url)
            # Save the map image to a file
            with open("static/dist/img-web/propertyforeign-cms/" + str(propertyid) + "/location_map.png", "wb") as f:
                f.write(response.content)

            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
    if action in ["add2", "edit2", "delete2"]:
        # Retrieve data from the request

        propertyid = request.POST.get('propertyid')
        propertyno = request.POST.get('propertyno')
        propertycontents = request.POST.get('propertycontents')
        propertycontents_s = request.POST.get('propertycontents_s')
        propertycontents_e = request.POST.get('propertycontents_e')
        currency = request.POST.get('currency')
        if not currency:
            currency = ""

        try:
            if action == "add2":
                property = PropertyForeigns()
                property.listingdate = datetime_str
                property.modifydate = datetime_str
                property.viewcounter = 0
            else:
                property = PropertyForeigns.objects.using('infinyrealty').get(propertyforeignid=propertyid)
                property.modifydate = datetime_str

            property.currency = currency
            property.propertycontents = propertycontents
            property.propertycontents_s = propertycontents_s
            property.propertycontents_e = propertycontents_e

            property.approved = 0
            property.loginid = request.session.get('loginid')

            #property.loginid = request.session.get('loginid')

            if action == "add2" or action == "edit2": property.save(using='infinyrealty')
            if action == "delete2": property.delete()
            messages.success(request, "New Poperty was created successfully.")
            propertyid = property.propertyforeignid

            return HttpResponse("Success")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

def ownerMain(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')
    propertyid = request.POST.get('propertyid')
    if propertyid is None:
        propertyid = ""

    usage_list = PropertyUsages.objects.using('infinyrealty').order_by('sequence')

    accessid = 5169
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
        "user_usage": 1,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usage_list": usage_list,
        "user_propertyid": propertyid,
    }
    return render(request, "property_template/ownerMain.html", context)

@csrf_exempt
def ownerMain_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.session.get('loginid')
    username = request.session.get('username')
    propertyid = request.POST.get('propertyid')
    today = datetime.datetime.now()

    if action == "menutab":
        context = {
            "action": action,
            "user_loginid": loginid,
            "user_propertyid": propertyid,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "userlist": user_list,
        }
    if action == "company_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        sql = """
                SELECT
                    CAST(pc.Company AS NVARCHAR(MAX)) AS Company,
                    CAST(CTCPerson AS NVARCHAR(MAX)) AS CTCPerson,
                    CAST(ContactInfo AS NVARCHAR(MAX)) AS ContactInfo,
                    CAST(Email AS NVARCHAR(MAX)) AS Email,
                    pc.PropertyID,
                    p.PropertyName
                FROM
                    dbo.tblPropertyContact pc
                    LEFT JOIN dbo.tblProperty p ON p.PropertyID = pc.PropertyID
                WHERE
                    (CAST(Company AS NVARCHAR(MAX)) <> '')
        """
        cursor.execute(sql)
        property_list = cursor.fetchall()
        company_list = {}
        ctc_person_list = {}
        contact_info_list = {}
        email_list = {}
        
        for property_detail in property_list:
            if not property_detail.Company in company_list:
                company_list[property_detail.Company] = {}
                ctc_person_list[property_detail.Company] = set([])
                contact_info_list[property_detail.Company] = set([])
                email_list[property_detail.Company] = set([])
            company_list[property_detail.Company][property_detail.PropertyID] = property_detail.PropertyName
            if not property_detail.CTCPerson in (None, ""): 
                ctc_person_list[property_detail.Company].add(property_detail.CTCPerson)
            if not property_detail.ContactInfo in (None, ""): 
                contact_info_list[property_detail.Company].add(property_detail.ContactInfo)
            if not property_detail.Email in (None, ""):
                email_list[property_detail.Company].add(property_detail.Email)

        context = {
            "action": action,
            "user_loginid": loginid,
            "company_list": company_list,
            "ctc_person_list": ctc_person_list,
            "contact_info_list": contact_info_list,
            "email_list": email_list,
            "today": today,
        }
    if action == "ctc_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact_CTCPersonList")
        ctc_person_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "ctc_person_list": ctc_person_list,
            "today": today,
        }
    if action == "phone_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact_PhoneList")
        phone_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "phone_list": phone_list,
            "today": today,
        }
    if action == "email_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact_EmailList")
        email_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "email_list": email_list,
            "today": today,
        }
    if action == "property_view":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage_list = PropertyUsages.objects.using('infinyrealty').order_by('sequence')
        area_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        cursor.execute("select * from V_AddressSubDistrict")
        subdistrict_list = cursor.fetchall()
        cursor.execute("select * from V_AddressStreet")
        street_list = cursor.fetchall()
        cursor.execute("select * from V_AddressBuilding")
        building_list = cursor.fetchall()
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')

        usage = request.POST.get('usage')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None or usage == "" :
            sql = "select * from V_PropertyFullList"
        else:
            sql = "select * from V_PropertyFullList where usage = N'" + usage + "'"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_loginid": loginid,
            "property_view_list": property_view_list,
            "usage_list": usage_list,
            "floorzone_list": floorzone_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "area_list": area_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "building_list": building_list,
            "sql": sql,
        }
    if action == "property_edit":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        cursor.execute("select * from V_AddressBuilding")
        building_list = cursor.fetchall()
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain','sequence')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain','sequence')
        property_document_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="document").order_by('-ismain')

        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact where propertyid = '" + str(propertyid) + "' order by createdate desc")
        property_contact_list = cursor.fetchall()
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyFollow where propertyid = '" + str(propertyid) + "' order by followdate desc")
        property_follow_list = cursor.fetchall()
        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "building_list": building_list,
            "floorzone_list": floorzone_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_contact_list": property_contact_list,
            "property_follow_list": property_follow_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_document_list": property_document_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_info":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        floorzone_list = CodeDetails.objects.using('infinyrealty').filter(code_id=7).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')
        property_document_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="document").order_by('-ismain')
        #property_photo_list = list(chain(property_file_list, property_floorplan_list))
        property_photo_list = ""

        for w in property_photo_list:
            filename = w.filename
            filename_extension = os.path.splitext(filename)[1][1:].lower()
            if "jpg" in filename_extension or "jpeg" in filename_extension or "png" in filename_extension:
                if w.filetype == "photo":
                    filename = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\"+w.filename
                    filename_wm = getattr(settings, "PATH_PROPERTY", None) + str(w.propertyid) + "\\"+w.filename.replace("."+filename_extension, "-wm."+filename_extension)
                else:
                    filename = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename
                    filename_wm = getattr(settings, "PATH_FLOORPLAN", None) + str(w.propertyid) + "\\" + w.filename.replace("."+filename_extension, "-wm."+filename_extension)
                filename_logo = getattr(settings, "PATH_MAIN", None) + "infinyrealty_logo_high.png"
                base_image = Image.open(filename)
                watermark_image = Image.open(filename_logo)
                if w.filetype == "photo":
                    watermark_ratio = 0.1  # 10% of the base image size
                else:
                    watermark_ratio = 0.03  # 3% of the base image size
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
                base_image.save(filename_wm)
                try:
                    PropertyFiles.objects.using('infinyrealty').filter(fileid=w.fileid).update(iswatermark=1)
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno
                    return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
                #draw = ImageDraw.Draw(image)
                #font = ImageFont.truetype("arial.ttf", size=150)
                #watermark_text = "infinyrealty.com2"
                #x = (image.width) / 2
                #y = (image.height) / 2
                #draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
                #image.save(filename_wm)

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_list": usage_list,
            "district_list": district_list,
            "subdistrict_list": subdistrict_list,
            "street_list": street_list,
            "floorzone_list": floorzone_list,
            "possession_list": possession_list,
            "offertype_list": offertype_list,
            "property_list": property_list,
            "property_file_list": property_file_list,
            "property_floorplan_list": property_floorplan_list,
            "property_document_list": property_document_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_oddsheet":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").exclude(filename__endswith=".mp4").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')

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
            "property_floorplan_list": property_floorplan_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_oddsheet_multi":
        propertyid = request.POST.get('propertyid')
        if propertyid is None or propertyid == "":
            propertyid = 0
        propertyid_list = request.POST.get('propertyid_list').split(",")
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid__in=propertyid_list)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").exclude(filename__endswith=".mp4").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')

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
            "property_floorplan_list": property_floorplan_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_offer":
        propertyid = request.POST.get('propertyid')
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')
        datetime_dt = datetime.datetime.today()
        draftdate = datetime_dt
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact where propertyid = '" + str(propertyid) + "' order by createdate desc")
        property_contact_list = cursor.fetchall()

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
            "property_contact_list": property_contact_list,
            "draftdate": draftdate,
            "today": today,
        }
    if action == "property_contact":
        propertyid = request.POST.get('propertyid')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact where propertyid = '" + str(propertyid) + "' order by createdate desc")
        property_contact_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "propertyid": propertyid,
            "property_list": property_list,
            "property_contact_list": property_contact_list,
        }
    if action == "property_contact_property":
        contact_type = request.POST.get('contact_type')
        contact_data = request.POST.get('contact_data')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if contact_type == "company":
            cursor.execute("select * from V_PropertyContactCompanyFull where Company = N'" + str(contact_data) + "' order by modifydate desc")
        if contact_type == "person":
            cursor.execute("select * from V_PropertyContactPersonFull where Person = N'" + str(contact_data) + "' order by modifydate desc")
        if contact_type == "phone":
            cursor.execute("select * from V_PropertyContactPhoneFull where ContactInfo = N'" + str(contact_data) + "' order by modifydate desc")
        property_contact_property_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "contact_type": contact_type,
            "contact_data": contact_data,
            "property_contact_property_list": property_contact_property_list,
        }
    if action == "property_follow":
        propertyid = request.POST.get('propertyid')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyFollow where propertyid = '" + str(propertyid) + "' order by followdate desc")
        property_follow_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "propertyid": propertyid,
            "property_list": property_list,
            "property_follow_list": property_follow_list,
        }
    if action == "main_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')

        try:
            PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.ismain = 1
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "approve_picture":
        propertyid = request.POST.get('propertyid')
        fileid = request.POST.get('fileid')
        approve = request.POST.get('approve')

        try:
            PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid).update(ismain=0)
            #propertyfile.ismain = 3
            #propertyfile.save(using='infinyrealty')
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.isapprove = approve
            propertyfile.save(using='infinyrealty')
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Update Success')
    if action == "delete_picture":
        fileid = request.POST.get('fileid')

        try:
            propertyfile = PropertyFiles.objects.using('infinyrealty').get(fileid=fileid)
            propertyfile.delete()
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "request_review":
        usage = request.POST.get('usage')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None or usage == "" :
            cursor.execute("select * from tblProperty where approved = 0")
        else:
            cursor.execute("select * from tblProperty where usage = N'" + usage + "' and approved = 0")
        usageapproveright_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "usageapproveright_list": usageapproveright_list,
        }
    if action == "request_review_update":
        propertyid = request.POST.get('propertyid')

        try:
            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
            #property.post = post
            #property.functionid = functionid
            property.approved = 1
            property.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    if action == "create_offer":
        propertyid = request.POST.get('propertyid')
        propertyno = request.POST.get('propertyno')
        propertyname = request.POST.get('propertyname')
        buyername = request.POST.get('buyername')
        draftdate = request.POST.get('draftdate')
        initialpaymentdate = request.POST.get('initialpaymentdate')
        snpdate = request.POST.get('snpdate')
        finalpaymentdate = request.POST.get('finalpaymentdate')
        #draftdate = "07/05/2024"
        #users.activedate = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        #date = datetime.datetime.strptime(draftdate, "%d/%m/%Y")
        date = datetime.datetime.strptime(draftdate, "%Y-%m-%d")
        formatted_draftdate = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(initialpaymentdate, "%Y-%m-%d")
        formatted_settledate1 = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(snpdate, "%Y-%m-%d")
        formatted_settledate2 = date.strftime("%dth %B %Y")
        date = datetime.datetime.strptime(finalpaymentdate, "%Y-%m-%d")
        formatted_settledate3 = date.strftime("%dth %B %Y")
        purchasingprice = request.POST.get('purchasingprice')
        agencyfee = str(float(purchasingprice)/100)
        grossarea = request.POST.get('grossarea')
        netarea = request.POST.get('netarea')

        path = getattr(settings, "PATH_OFFER_TEMPLATE", None)
        doc = Document(path + '\\InfinyRealty_OfferLetter_template.docx')

        # Find and replace text in the template
        for paragraph in doc.paragraphs:
            if '@draft_date' in paragraph.text:
                paragraph.text = paragraph.text.replace('@draft_date', formatted_draftdate)
            if '@buyer_name' in paragraph.text:
                paragraph.text = paragraph.text.replace('@buyer_name', buyername)
            if '@property_name' in paragraph.text:
                paragraph.text = paragraph.text.replace('@property_name', propertyname)
            if '@purchasing_price' in paragraph.text:
                paragraph.text = paragraph.text.replace('@purchasing_price', purchasingprice)
            if '@agency_fee' in paragraph.text:
                paragraph.text = paragraph.text.replace('@agency_fee', agencyfee)
            if '@gross_area' in paragraph.text:
                paragraph.text = paragraph.text.replace('@gross_area', grossarea)
            if '@net_area' in paragraph.text:
                paragraph.text = paragraph.text.replace('@net_area', netarea)
            if '@settle_date1' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date1', formatted_settledate1)
            if '@settle_date2' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date2', formatted_settledate2)
            if '@settle_date3' in paragraph.text:
                paragraph.text = paragraph.text.replace('@settle_date3', formatted_settledate3)

        # Save the modified Docx as a new file
        folder_path = path + "\\" + str(propertyid) + "//"
        os.makedirs(folder_path, exist_ok=True)
        new_file_path = path + "\\" + propertyid + '\\InfinyRealty_OfferLetter_' + propertyno + '.docx'
        doc.save(new_file_path)

        # Open the file for reading
        with open(new_file_path, 'rb') as file:
            # Create a FileResponse and specify the content type as 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response = FileResponse(file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            # Set the content-disposition header to trigger the file download dialog with the specified filename
            response['Content-Disposition'] = 'attachment; filename="InfinyRealty_OfferLetter_' + propertyno + '.docx"'

            # Delete the generated file after sending the response
            #os.remove(new_file_path)

        return HttpResponse('Create Success')
    return render(request, "property_template/ownerMain_response.html", context)

def oddsheet(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    usage_list = PropertyUsages.objects.using('infinyrealty').order_by('sequence')

    accessid = 5158
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
        "user_usage": 1,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usage_list": usage_list,
    }
    return render(request, "property_template/oddsheet.html", context)

@csrf_exempt
def oddsheet_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.POST.get('loginid')
    today = datetime.datetime.now()

    if action == "menutab":
        context = {
            "action": action,
            "user_loginid": loginid,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "userlist": user_list,
        }
    if action == "usage_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_Usage_count")
        usage_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_view_list": usage_view_list,
            "today": today,
        }
    if action == "property_view":
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        usage_list = PropertyUsages.objects.using('infinyrealty').order_by('sequence')
        area_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        cursor.execute("select * from V_AddressStreet")
        street_list = cursor.fetchall()
        cursor.execute("select * from V_AddressBuilding")
        building_list = cursor.fetchall()
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')

        usage = request.POST.get('usage')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None or usage == "" :
            sql = "select * from tblProperty"
        else:
            sql = "select * from tblProperty where usage = N'" + usage + "'"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_loginid": loginid,
            "property_view_list": property_view_list,
            "area_list": area_list,
            "sql": sql,
        }
    if action == "property_oddsheet":
        propertyid = request.POST.get('propertyid')
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')
        property_floorplan_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="floorplan").order_by('-ismain')

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
            "property_floorplan_list": property_floorplan_list,
            "property_file_path": getattr(settings, "AUTH_HOST", None),
            "property_floorplan_path": getattr(settings, "AUTH_HOST", None),
            "propertyid": propertyid,
            "today": today,
        }
    if action == "property_oddsheet_multi":
        propertyid = request.POST.get('propertyid')
        propertyid_list = request.POST.get('propertyid_list').split(",")
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid__in=propertyid_list)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')

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
    if action == "create_oddsheet":
        propertyid = request.POST.get('propertyid')
        propertyno = request.POST.get('propertyno')
        propertyname = request.POST.get('propertyname')
        oddsheetdate = request.POST.get('oddsheetdate')
        usage = request.POST.get('usage')
        offertype = request.POST.get('offertype')
        sellingpoint = request.POST.get('sellingpoint')
        oddsheet_content = request.POST.get('oddsheet_content')
        floorplan_content = request.POST.get('floorplan_content')
        photo_content = request.POST.get('photo_content')
        soup = BeautifulSoup(oddsheet_content, 'html.parser')
        propertyidlist = request.POST.get('propertyidlist')

        path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None)
        doc = Document(path + '\\InfinyRealty_OddSheet_template.docx')

        # Get the map image from Google Maps
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={propertyname.replace(' ', '+')}&zoom=20&markers=color:red|{propertyname.replace(' ', '+')}&size=800x600&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
        #map_url = "https://maps.googleapis.com/maps/api/staticmap?center=San+Francisco,CA&zoom=12&size=600x400&maptype=roadmap&key=AIzaSyB-k1UGS0OD7HZxTLWIOOhyfrl8ryiHniY"
        response = requests.get(map_url)
        # Save the map image to a file
        with open("static/dist/img-web/property-cms/"+propertyid+"/location_map.png", "wb") as f:
            f.write(response.content)
        doc.add_page_break()
        doc.add_paragraph("位置圖")
        doc.add_picture("static/dist/img-web/property-cms/" + propertyid + "/location_map.png", width=Inches(7))

        if floorplan_content:
            floorplan_list = floorplan_content.split(',')
            for floorplan in floorplan_list:
                doc.add_page_break()
                doc.add_paragraph("平面圖")
                doc.add_picture("static/dist/img-web/floorplan-cms/"+propertyid+"/"+floorplan.strip(), width=Inches(7))
        if photo_content:
            photo_list = photo_content.split(",")
            for photo in photo_list:
                doc.add_page_break()
                doc.add_paragraph("物業相片")
                doc.add_picture("static/dist/img-web/property-cms/"+propertyid+"/"+photo.strip(), width=Inches(7))

        # doc.add_paragraph().add_run().add_picture(image_file, width=Inches(4))
        # doc.add_picture("static/dist/img-web/property-cms/38/20240408_110012.jpg", width=Inches(7))

        try:
            # Find and replace text in the template
            for paragraph in doc.paragraphs:
                if '@property_no' in paragraph.text:
                    paragraph.text = paragraph.text.replace('@property_no', propertyno)
                    paragraph.style = paragraph.style
                if '@oddsheet_date' in paragraph.text:
                    paragraph.text = paragraph.text.replace('@oddsheet_date', oddsheetdate)
                    paragraph.style = paragraph.style
                for paragraph in doc.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = '微軟正黑體'
                        run.font.bold = True
                #if '@content_00' in paragraph.text:
                #    paragraph.text = paragraph.text.replace('@content_00', oddsheet_content)
                #    paragraph.style = paragraph.style

                #paragraph.add_run().add_picture(image, width=Inches(6))
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if '@property_name' in cell.text:
                            cell.style = cell.text.style
                            cell.text = cell.text.replace('@property_name', propertyname)
                        if '@property_no' in cell.text:
                            cell.text = cell.text.replace('@property_no', propertyno)
                        if '@usage' in cell.text:
                            cell.text = cell.text.replace('@usage', usage)
                            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        if '@offertype' in cell.text:
                            cell.text = cell.text.replace('@offertype', offertype)
                            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        if '@selling_point' in cell.text:
                            cell.text = cell.text.replace('@selling_point', sellingpoint)
                            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                run.font.name = '微軟正黑體'
                                run.font.bold = True
            #labels = soup.find_all('h4', {'class': 'form-label'})
            #contents = soup.find_all('h4', style='font-weight:600')
            #for label, content in zip(labels, contents):
            #    title = label.text
            #    value = content.text.strip('：')
            w = 0
            table_rows = soup.find_all('div', class_='col-sm-3')
            num_rows = len(table_rows)
            for table_row in table_rows:
                label_text = table_row.find('label').get_text(strip=True)
                value_text = table_row.find_next_sibling('div', class_='col-sm-8').find('h4').get_text(strip=True)
                #value_text = value_text.replace('：', '')
                w = w + 1
                for table_index, table in enumerate(doc.tables):
                    if table_index == 2:
                        for row_index, row in enumerate(table.rows):
                            for cell in row.cells:
                                if '@title_'+str(w).zfill(2) in cell.text:
                                    cell.text = cell.text.replace('@title_'+str(w).zfill(2), label_text)
                                    cell.style = cell.paragraphs[0].style
                                    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
                                if '@content_'+str(w).zfill(2) in cell.text:
                                    cell.text = cell.text.replace('@content_'+str(w).zfill(2), value_text)
                                    cell.style = cell.paragraphs[0].style
                                    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
                                if row_index > num_rows - 1:
                                    for paragraph in cell.paragraphs:
                                        for run in paragraph.runs:
                                            run.font.color.rgb = RGBColor(255, 255, 255)
                                else:
                                    for paragraph in cell.paragraphs:
                                        for run in paragraph.runs:
                                            run.font.name = '微軟正黑體'
                                            run.font.bold = True

            # Save the modified Docx as a new file
            folder_path = path + "\\" + str(propertyid)
            os.makedirs(folder_path, exist_ok=True)
            #new_file_path = path + "\\" + propertyid + '\\InfinyRealty_OddSheet_' + propertyno + '.docx'
            #new_file_path = path + "\\" + propertyid + '\\InfinyRealty_' + propertyno + '_盤紙_' + propertyname + '.docx'
            new_file_path = path + "\\" + propertyid + '\\InfinyRealty_' + propertyno + '.docx'
            #new_pdf_path = path + "\\" + propertyid + '\\InfinyRealty_OddSheet_' + propertyno + '.pdf'
            doc.save(new_file_path)
            #pdfkit.from_file(new_file_path, new_pdf_path)

            # Open the file for reading
            with open(new_file_path, 'rb') as file:
                # Create a FileResponse and specify the content type as 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                response = FileResponse(file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

                # Set the content-disposition header to trigger the file download dialog with the specified filename
                response['Content-Disposition'] = 'attachment; filename="InfinyRealty_OddSheet_' + propertyno + '.docx"'

            # Combine word file
            #propertyid_list = []
            propertyid_list = propertyidlist[1:-1].replace("'", "")
            items = [int(x) for x in propertyid_list.split(", ")]
            #propertyid_list = [int(x) for x in propertyidlist]
            #files_to_combine = []
            i = 0
            for w in items:
                property_list = Propertys.objects.using('infinyrealty').filter(propertyid=w)
                propertyno = property_list[0].propertyno
                file_path = f'{path}\\{w}\\InfinyRealty_{propertyno}.docx'
                page_break_path = f'{path}\\page_break.docx'
                if os.path.exists(file_path):
                    if i == 0:
                        master = Document(file_path)
                        composer = Composer(master)
                    else:
                        doc0 = Document(page_break_path)
                        composer.append(doc0)
                        doc1 = Document(file_path)
                        composer.append(doc1)
                    i += 1
                #files_to_combine.append(file_path)

                #files_to_combine = [
                #    f'{path}\\353\\InfinyRealty_{propertyno}.docx',
                #    f'{path}\\44\\InfinyRealty_O-0043.docx',
                #]
            output_path = f'{path}\\all\\combined_document.docx'
            composer.save(output_path)

            #master = Document(f'{path}\\355\\InfinyRealty_R-0003.docx')
            #composer = Composer(master)
            #doc1 = Document(f'{path}\\353\\InfinyRealty_R-0001.docx')
            #composer.append(doc1)

            #combine_docx_files(files_to_combine, output_path)

            # Instantiate a Merger object and load a DOCX file
            #with gv.Merger(f'{path}\\355\\InfinyRealty_R-0003.docx') as merger:
                # Add another DOCX file to merge
                #merger.join(f'{path}\\353\\InfinyRealty_R-0001.docx')
                #merger.join(f'{path}\\44\\InfinyRealty_O-0043.docx')
                # Merge DOCX files and save result
                #merger.save(output_path)

            #with gv.Merger(files_to_combine[0]) as merger:
                # Add another DOCX file to merge
                #merger.join(files_to_combine[1])
                # Merge DOCX files and save result
                #merger.save(output_path)
            #merge_documents_with_headers_footers(files_to_combine, output_path)
            #combine_documents(files_to_combine, output_path)
            #merge_documents_with_headers(files_to_combine, output_path)

            #source_path = f'{path}\\353\\InfinyRealty_R-0001.docx'
            #target_path = f'{path}\\44\\InfinyRealty_O-0043.docx'
            #append_to_document(source_path, target_path)

            #merge_documents(files_to_combine, output_path)
            #combine_word_files(files_to_combine, output_path)

                # Delete the generated file after sending the response
                #os.remove(new_file_path)
            #pdfkit.from_file(new_file_path, "aa.pdf")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)
        return HttpResponse('Create Success')
    return render(request, "property_template/oddsheet_response.html", context)

def oddsheet_download(request, propertyid):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.POST.get('loginid')
    today = datetime.datetime.now()
    property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
    propertyno = property_list[0].propertyno

    path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\" + str(propertyid)
    os.makedirs(path, exist_ok=True)
    file_list = os.listdir(path)
    if file_list:
        file_single = []
        for filelist in file_list:
            file_single.append(filelist)
        file_path = os.path.join(path, str(filelist))

        if filelist != "":
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    #response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    response['Content-Disposition'] = 'attachment; filename="InfinyRealty_OddSheet_' + propertyno + '.docx"'
                    return response
    else:
        return "No file"

def oddsheet_download_all(request, propertyid):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.POST.get('loginid')
    today = datetime.datetime.now()
    property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
    propertyno = property_list[0].propertyno

    path = getattr(settings, "PATH_ODDSHEET_TEMPLATE", None) + "\\all"
    os.makedirs(path, exist_ok=True)
    file_list = os.listdir(path)
    if file_list:
        file_single = []
        for filelist in file_list:
            file_single.append(filelist)
        file_path = os.path.join(path, str(filelist))

        if filelist != "":
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    #response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    response['Content-Disposition'] = 'attachment; filename="InfinyRealty_OddSheet_All.docx"'
                    return response
    else:
        return "No file"

def residential(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    usage = "住宅"

    accessid = 45
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
        "user_usage": usage,
        "usage": usage,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usagelist": UsageList,
    }
    return render(request, "property_template/residential.html", context)

def office(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    usage = "住宅"

    accessid = 21
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
        "user_usage": usage,
        "usage": usage,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usagelist": UsageList,
    }
    return render(request, "property_template/office.html", context)

def shop(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    usage = "住宅"

    accessid = 21
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
        "user_usage": usage,
        "usage": usage,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usagelist": UsageList,
    }
    return render(request, "property_template/shop.html", context)

def industrial(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    usage = "住宅"

    accessid = 21
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
        "user_usage": usage,
        "usage": usage,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usagelist": UsageList,
    }
    return render(request, "property_template/industrial.html", context)

def carpark(request):
    if not request.session.get('username'): return redirect('login')
    loginid = request.session.get('loginid')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    usage = "住宅"

    accessid = 21
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
        "user_usage": usage,
        "usage": usage,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usagelist": UsageList,
    }
    return render(request, "property_template/carpark.html", context)

def offer(request):
    if not request.session.get('loginid'): return redirect('login')
    loginid = request.session.get('loginid')

    UsageList = CodeDetails.objects.using('infinyrealty').filter(code_id=5).order_by('sequence')
    district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
    subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
    street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
    possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
    offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')

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
        "user_usage": 1,
        "accessid": accessid,
        "menuitem": menuItem,
        "menulist": menuList,
        "usagelist": UsageList,
        "district_list": district_list,
        "subdistrict_list": subdistrict_list,
        "street_list": street_list,
        "offertype_list": offertype_list,
        "possession_list": possession_list,
    }
    return render(request, "property_template/offer.html", context)

@csrf_exempt
def offer_response(request):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.POST.get('loginid')
    today = datetime.datetime.now()

    if action == "menutab":
        context = {
            "action": action,
            "user_loginid": loginid,
        }
    if action == "team_list":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("exec spTeamList '', '1'")
        user_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "userlist": user_list,
        }
    if action == "usage_view":
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_Usage_count")
        usage_view_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "usage_view_list": usage_view_list,
            "today": today,
        }
    if action == "property_view":
        usage = request.POST.get('usage')
        offertype = request.POST.get('offertype')
        possession = request.POST.get('possession')
        cnxn=pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None: usage = ""
        if offertype is None: offertype = ""
        if possession is None: possession = ""
        sql = "select * from tblProperty " \
              "where (1 = case when N'" + str(usage) + "' = '' then 1 when usage = N'" + str(usage) + "' then 1 else 0 end) " \
              "and (1 = case when N'" + str(offertype) + "' = '' then 1 when offertype = N'" + str(offertype) + "' then 1 else 0 end)  " \
              "and (1 = case when N'" + str(possession) + "' = '' then 1 when possession = N'" + str(possession) + "' then 1 else 0 end)  " \
              "order by listingdate desc"
        cursor.execute(sql)
        property_view_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "user_loginid": loginid,
            "property_view_list": property_view_list,
            "sql": sql,
        }
    if action == "property_info":
        propertyid = request.POST.get('propertyid')
        usage_list = PropertyUsages.objects.using('infinyrealty').filter(status=1).order_by('sequence')
        district_list = CodeDetails.objects.using('infinyrealty').filter(code_id=2).order_by('sequence')
        subdistrict_list = CodeDetails.objects.using('infinyrealty').filter(code_id=3).order_by('sequence')
        street_list = CodeDetails.objects.using('infinyrealty').filter(code_id=4).order_by('sequence')
        possession_list = CodeDetails.objects.using('infinyrealty').filter(code_id=1).order_by('sequence')
        offertype_list = CodeDetails.objects.using('infinyrealty').filter(code_id=6).order_by('sequence')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        property_file_list = PropertyFiles.objects.using('infinyrealty').filter(propertyid=propertyid,filetype="photo").order_by('-ismain')
        datetime_dt = datetime.datetime.today()
        draftdate = datetime_dt.strftime("%Y-%m-%d")
        settledate = datetime_dt + datetime.timedelta(days=8)
        initialpaymentdate = settledate.strftime("%Y-%m-%d")
        settledate = datetime_dt + datetime.timedelta(days=22)
        snpdate = settledate.strftime("%Y-%m-%d")
        settledate = datetime_dt + datetime.timedelta(days=27)
        finalpaymentdate = settledate.strftime("%Y-%m-%d")

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
            "draftdate": draftdate,
            "initialpaymentdate": initialpaymentdate,
            "snpdate": snpdate,
            "finalpaymentdate": finalpaymentdate,
            "today": today,
        }
    if action == "create_offer":
        propertyid = request.POST.get('propertyid')
        propertyno = request.POST.get('propertyno')
        propertyname = request.POST.get('propertyname')
        recordno = request.POST.get('recordno')
        recorddate = request.POST.get('recorddate')
        companyname = request.POST.get('companyname')
        clientname = request.POST.get('clientname')

        tenanttype = request.POST.get('tenanttype')
        grossarea = request.POST.get('grossarea')
        rentperiod = request.POST.get('rentperiod')
        rent = request.POST.get('rent')
        liveyear = request.POST.get('liveyear')
        increaserent = request.POST.get('increaserent')
        startrent = request.POST.get('startrent')
        freemonth = request.POST.get('freemonth')
        monthlyrent = request.POST.get('monthlyrent')
        firstrent = request.POST.get('firstrent')
        ratemanagement = request.POST.get('ratemanagement')
        depositmonth = request.POST.get('depositmonth')
        loyerdate = request.POST.get('loyerdate')
        monthrent = request.POST.get('monthrent')
        previousmonth = request.POST.get('previousmonth')
        naturebusiness = request.POST.get('naturebusiness')
        situation = request.POST.get('situation')
        remarks = request.POST.get('remarks')
        ownermonth = request.POST.get('ownermonth')
        contactstaff = request.POST.get('contactstaff')

        path = getattr(settings, "PATH_OFFER_TEMPLATE", None)
        doc = Document(path + '\\InfinyRealty_OfferLetter_template.docx')

        # Find and replace text in the template
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if '@recordno' in cell.text:
                        cell.text = cell.text.replace('@recordno', recordno)
                    if '@recorddate' in cell.text:
                        cell.text = cell.text.replace('@recorddate', recorddate)
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.name = '微軟正黑體'
                            run.font.bold = True

        for paragraph in doc.paragraphs:
            if '@companyname' in paragraph.text:
                paragraph.text = paragraph.text.replace('@companyname', companyname)
            if '@clientname' in paragraph.text:
                paragraph.text = paragraph.text.replace('@clientname', clientname)
            if '@propertyname' in paragraph.text:
                paragraph.text = paragraph.text.replace('@propertyname', propertyname)
            if '@tenanttype' in paragraph.text:
                paragraph.text = paragraph.text.replace('@tenanttype', tenanttype)
            if '@grossarea' in paragraph.text:
                paragraph.text = paragraph.text.replace('@grossarea', grossarea)
            if '@rentperiod' in paragraph.text:
                paragraph.text = paragraph.text.replace('@rentperiod', rentperiod)
            if '@rent' in paragraph.text:
                paragraph.text = paragraph.text.replace('@rent', rent)
            if '@liveyear' in paragraph.text:
                paragraph.text = paragraph.text.replace('@liveyear', liveyear)
            if '@increaserent' in paragraph.text:
                paragraph.text = paragraph.text.replace('@increaserent', increaserent)
            if '@startrent' in paragraph.text:
                paragraph.text = paragraph.text.replace('@startrent', startrent)
            if '@freemonth' in paragraph.text:
                paragraph.text = paragraph.text.replace('@freemonth', freemonth)
            if '@monthlyrent' in paragraph.text:
                paragraph.text = paragraph.text.replace('@monthlyrent', monthlyrent)
            if '@firstrent' in paragraph.text:
                paragraph.text = paragraph.text.replace('@firstrent', firstrent)
            if '@ratemanagement' in paragraph.text:
                paragraph.text = paragraph.text.replace('@ratemanagement', ratemanagement)
            if '@depositmonth' in paragraph.text:
                paragraph.text = paragraph.text.replace('@depositmonth', depositmonth)
            if '@loyerdate' in paragraph.text:
                paragraph.text = paragraph.text.replace('@loyerdate', loyerdate)
            if '@monthrent' in paragraph.text:
                paragraph.text = paragraph.text.replace('@monthrent', monthrent)
            if '@previousmonth' in paragraph.text:
                paragraph.text = paragraph.text.replace('@previousmonth', previousmonth)
            if '@naturebusiness' in paragraph.text:
                paragraph.text = paragraph.text.replace('@naturebusiness', naturebusiness)
            if '@situation' in paragraph.text:
                paragraph.text = paragraph.text.replace('@situation', situation)
            if '@remarks' in paragraph.text:
                paragraph.text = paragraph.text.replace('@remarks', remarks)
            if '@ownermonth' in paragraph.text:
                paragraph.text = paragraph.text.replace('@ownermonth', ownermonth)
            if '@contactstaff' in paragraph.text:
                paragraph.text = paragraph.text.replace('@contactstaff', contactstaff)
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    run.font.name = '微軟正黑體'
                    run.font.bold = True
        # Save the modified Docx as a new file
        folder_path = path + "\\" + str(propertyid) + "//"
        os.makedirs(folder_path, exist_ok=True)
        new_file_path = path + "\\" + propertyid + '\\InfinyRealty_OfferLetter_' + propertyno + '.docx'
        doc.save(new_file_path)

        # Open the file for reading
        with open(new_file_path, 'rb') as file:
            # Create a FileResponse and specify the content type as 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response = FileResponse(file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            # Set the content-disposition header to trigger the file download dialog with the specified filename
            response['Content-Disposition'] = 'attachment; filename="InfinyRealty_OfferLetter_' + propertyno + '.docx"'

            # Delete the generated file after sending the response
            #os.remove(new_file_path)

        return HttpResponse('Create Success')

    if action == "property_contact":
        propertyid = request.POST.get('propertyid')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyContact where propertyid = '" + str(propertyid) + "' order by createdate desc")
        property_contact_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "propertyid": propertyid,
            "property_list": property_list,
            "property_contact_list": property_contact_list,
        }
    if action == "property_follow":
        propertyid = request.POST.get('propertyid')
        property_list = Propertys.objects.using('infinyrealty').filter(propertyid=propertyid)
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server='+getattr(settings, "AUTH_HOST", None)+';UID='+getattr(settings, "AUTH_USER", None)+';PWD='+getattr(settings, "AUTH_PASSWORD", None)+';Database=infinyrealty')
        cursor = cnxn.cursor()
        cursor.execute("select * from V_PropertyFollow where propertyid = '" + str(propertyid) + "' order by followdate desc")
        property_follow_list = cursor.fetchall()

        context = {
            "action": action,
            "user_loginid": loginid,
            "propertyid": propertyid,
            "property_list": property_list,
            "property_follow_list": property_follow_list,
        }
    if action == "request_review":
        usage = request.POST.get('usage')
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_HOST", None) + ';UID=' + getattr(settings, "AUTH_USER", None) + ';PWD=' + getattr(settings, "AUTH_PASSWORD", None) + ';Database=infinyrealty')
        cursor = cnxn.cursor()
        if usage is None or usage == "" :
            cursor.execute("select * from tblProperty where approved = 0")
        else:
            cursor.execute("select * from tblProperty where usage = N'" + usage + "' and approved = 0")
        usageapproveright_list = cursor.fetchall()
        cursor.close()
        cnxn.close()

        context = {
            "action": action,
            "usageapproveright_list": usageapproveright_list,
        }
    if action == "request_review_update":
        propertyid = request.POST.get('propertyid')

        try:
            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
            #property.post = post
            #property.functionid = functionid
            property.approved = 1
            property.save(using='infinyrealty')
        except Exception as e:
            return HttpResponse({'message': 'The record was updated fail.'+format(str(e))}, status=500)
        return HttpResponse('Update Success')
    return render(request, "property_template/offer_response.html", context)

def offer_download(request, propertyid):
    if not request.session.get('loginid'): return redirect('login')
    action = request.POST.get('action')
    loginid = request.POST.get('loginid')
    today = datetime.datetime.now()

    path = getattr(settings, "PATH_OFFER_TEMPLATE", None) + "\\" + str(propertyid)
    file_list = os.listdir(path)
    file_single = []
    for filelist in file_list:
        file_single.append(filelist)
    file_path = os.path.join(path, str(filelist))

    if filelist != "":
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response

@csrf_exempt  # Only use this for testing; handle CSRF properly in production
def upload_property(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        folder_path = getattr(settings, "PATH_PROPERTY", None) + "\\" + "upload" + "\\"
        new_filename = "import_property.xlsx"

        os.makedirs(folder_path, exist_ok=True)
        #with open(folder_path + uploaded_file.name, 'wb') as file:
        with open(folder_path + new_filename, 'wb') as file:
            for chunk in uploaded_file.chunks():
                file.write(chunk)

            file_path = os.path.join(folder_path, new_filename)

            # Read the Excel file
            try:
                df = pd.read_excel(file_path)  # Read the Excel file into a DataFrame

                # Iterate over the DataFrame and save to the database
                for index, row in df.iterrows():
                    propertyid = row['PropertyID']
                    if (propertyid in ["", "0", "nan", "NULL"] or
                            (isinstance(propertyid, float) and np.isnan(propertyid)) or
                            len(str(propertyid)) == 0):
                        property = Propertys()
                    else:
                        if Propertys.objects.using('infinyrealty').filter(propertyid=propertyid).exists():
                            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
                        else:
                            property = Propertys()


                    for col_name in df.columns:
                        #print(f"{col_name}: {row[col_name]}")  # or use logging

                        # Convert column name to lowercase
                        lower_col_name = col_name.lower()

                        # Create the corresponding property name
                        #property_name = lower_col_name.replace(' ', '')  # Remove spaces if necessary

                        # Use setattr to dynamically set the property value
                        if lower_col_name != "propertyid":
                            if hasattr(property, lower_col_name):
                                if lower_col_name != "listingdate" and lower_col_name != "modifydate":
                                    value = row[col_name]
                                    # Check for empty strings, zeros, NaN, and NULL
                                    if (value in ["", "0", "nan", "NULL"] or
                                            (isinstance(value, float) and np.isnan(value)) or
                                            len(str(value)) == 0):
                                        setattr(property, lower_col_name, None)
                                    else:
                                        try:
                                            if not isinstance(value, (float, int)):  # Check if value is not float or int
                                                print(f"Invalid type for {lower_col_name}: {value} (type: {type(value)})")
                                                setattr(property, lower_col_name, value)
                                            else:
                                                # Value is valid, so assign it
                                                setattr(property, lower_col_name, float(value))
                                        except ValueError:
                                            # Handle the case where conversion fails
                                            print(f"Invalid value for {lower_col_name}: {value}")
                                            setattr(property, lower_col_name, value)
                                else:
                                    try:
                                        # Handle Timestamp separately
                                        if isinstance(value, pd.Timestamp):
                                            # Handle the case where conversion fails
                                            print(f"Invalid value for {lower_col_name}: {value}")
                                            setattr(property, lower_col_name, value)
                                        else:
                                            datetime_dt = datetime.datetime.today()
                                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                                            setattr(property, lower_col_name,
                                                    datetime_str)  # or value.strftime('%Y-%m-%d %H:%M:%S')
                                    except ValueError:
                                        datetime_dt = datetime.datetime.today()
                                        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                                        setattr(property, lower_col_name,
                                                datetime_str)  # or value.strftime('%Y-%m-%d %H:%M:%S')
                    property.save(using='infinyrealty')
                return JsonResponse({'message': 'File uploaded and data imported successfully!'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
            return JsonResponse({'message': 'File uploaded successfully!'})
        return JsonResponse({'error': 'Failed to upload file.'}, status=400)

@csrf_exempt  # Only use this for testing; handle CSRF properly in production
def upload_newproperty(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        folder_path = getattr(settings, "PATH_PROPERTY", None) + "\\" + "upload" + "\\"
        new_filename = "import_newproperty.xlsx"

        os.makedirs(folder_path, exist_ok=True)
        #with open(folder_path + uploaded_file.name, 'wb') as file:
        with open(folder_path + new_filename, 'wb') as file:
            for chunk in uploaded_file.chunks():
                file.write(chunk)

            file_path = os.path.join(folder_path, new_filename)

            # Read the Excel file
            try:
                df = pd.read_excel(file_path)  # Read the Excel file into a DataFrame

                # Iterate over the DataFrame and save to the database
                for index, row in df.iterrows():
                    propertyid = row['PropertyID']
                    if (propertyid in ["", "0", "nan", "NULL"] or
                            (isinstance(propertyid, float) and np.isnan(propertyid)) or
                            len(str(propertyid)) == 0):
                        property = Propertys()
                    else:
                        if Propertys.objects.using('infinyrealty').filter(propertyid=propertyid).exists():
                            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
                        else:
                            property = Propertys()


                    for col_name in df.columns:
                        #print(f"{col_name}: {row[col_name]}")  # or use logging

                        # Convert column name to lowercase
                        lower_col_name = col_name.lower()

                        # Create the corresponding property name
                        #property_name = lower_col_name.replace(' ', '')  # Remove spaces if necessary

                        # Use setattr to dynamically set the property value
                        if lower_col_name != "propertyid":
                            if hasattr(property, lower_col_name):
                                if lower_col_name != "listingdate" and lower_col_name != "modifydate":
                                    value = row[col_name]
                                    # Check for empty strings, zeros, NaN, and NULL
                                    if (value in ["", "0", "nan", "NULL"] or
                                            (isinstance(value, float) and np.isnan(value)) or
                                            len(str(value)) == 0):
                                        setattr(property, lower_col_name, None)
                                    else:
                                        try:
                                            if not isinstance(value, (float, int)):  # Check if value is not float or int
                                                print(f"Invalid type for {lower_col_name}: {value} (type: {type(value)})")
                                                setattr(property, lower_col_name, value)
                                            else:
                                                # Value is valid, so assign it
                                                setattr(property, lower_col_name, float(value))
                                        except ValueError:
                                            # Handle the case where conversion fails
                                            print(f"Invalid value for {lower_col_name}: {value}")
                                            setattr(property, lower_col_name, value)
                                else:
                                    try:
                                        # Handle Timestamp separately
                                        if isinstance(value, pd.Timestamp):
                                            # Handle the case where conversion fails
                                            print(f"Invalid value for {lower_col_name}: {value}")
                                            setattr(property, lower_col_name, value)
                                        else:
                                            datetime_dt = datetime.datetime.today()
                                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                                            setattr(property, lower_col_name,
                                                    datetime_str)  # or value.strftime('%Y-%m-%d %H:%M:%S')
                                    except ValueError:
                                        datetime_dt = datetime.datetime.today()
                                        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                                        setattr(property, lower_col_name,
                                                datetime_str)  # or value.strftime('%Y-%m-%d %H:%M:%S')
                    property.save(using='infinyrealty')
                return JsonResponse({'message': 'File uploaded and data imported successfully!'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
            return JsonResponse({'message': 'File uploaded successfully!'})
        return JsonResponse({'error': 'Failed to upload file.'}, status=400)

@csrf_exempt  # Only use this for testing; handle CSRF properly in production
def upload_foreignproperty(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        folder_path = getattr(settings, "PATH_PROPERTY", None) + "\\" + "upload" + "\\"
        new_filename = "import_foreignproperty.xlsx"

        os.makedirs(folder_path, exist_ok=True)
        #with open(folder_path + uploaded_file.name, 'wb') as file:
        with open(folder_path + new_filename, 'wb') as file:
            for chunk in uploaded_file.chunks():
                file.write(chunk)

            file_path = os.path.join(folder_path, new_filename)

            # Read the Excel file
            try:
                df = pd.read_excel(file_path)  # Read the Excel file into a DataFrame

                # Iterate over the DataFrame and save to the database
                for index, row in df.iterrows():
                    propertyid = row['PropertyID']
                    if (propertyid in ["", "0", "nan", "NULL"] or
                            (isinstance(propertyid, float) and np.isnan(propertyid)) or
                            len(str(propertyid)) == 0):
                        property = Propertys()
                    else:
                        if Propertys.objects.using('infinyrealty').filter(propertyid=propertyid).exists():
                            property = Propertys.objects.using('infinyrealty').get(propertyid=propertyid)
                        else:
                            property = Propertys()


                    for col_name in df.columns:
                        #print(f"{col_name}: {row[col_name]}")  # or use logging

                        # Convert column name to lowercase
                        lower_col_name = col_name.lower()

                        # Create the corresponding property name
                        #property_name = lower_col_name.replace(' ', '')  # Remove spaces if necessary

                        # Use setattr to dynamically set the property value
                        if lower_col_name != "propertyid":
                            if hasattr(property, lower_col_name):
                                if lower_col_name != "listingdate" and lower_col_name != "modifydate":
                                    value = row[col_name]
                                    # Check for empty strings, zeros, NaN, and NULL
                                    if (value in ["", "0", "nan", "NULL"] or
                                            (isinstance(value, float) and np.isnan(value)) or
                                            len(str(value)) == 0):
                                        setattr(property, lower_col_name, None)
                                    else:
                                        try:
                                            if not isinstance(value, (float, int)):  # Check if value is not float or int
                                                print(f"Invalid type for {lower_col_name}: {value} (type: {type(value)})")
                                                setattr(property, lower_col_name, value)
                                            else:
                                                # Value is valid, so assign it
                                                setattr(property, lower_col_name, float(value))
                                        except ValueError:
                                            # Handle the case where conversion fails
                                            print(f"Invalid value for {lower_col_name}: {value}")
                                            setattr(property, lower_col_name, value)
                                else:
                                    try:
                                        # Handle Timestamp separately
                                        if isinstance(value, pd.Timestamp):
                                            # Handle the case where conversion fails
                                            print(f"Invalid value for {lower_col_name}: {value}")
                                            setattr(property, lower_col_name, value)
                                        else:
                                            datetime_dt = datetime.datetime.today()
                                            datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                                            setattr(property, lower_col_name,
                                                    datetime_str)  # or value.strftime('%Y-%m-%d %H:%M:%S')
                                    except ValueError:
                                        datetime_dt = datetime.datetime.today()
                                        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                                        setattr(property, lower_col_name,
                                                datetime_str)  # or value.strftime('%Y-%m-%d %H:%M:%S')
                    property.save(using='infinyrealty')
                return JsonResponse({'message': 'File uploaded and data imported successfully!'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
            return JsonResponse({'message': 'File uploaded successfully!'})
        return JsonResponse({'error': 'Failed to upload file.'}, status=400)
@csrf_exempt
def upload(request):
    if not request.session.get('username'): return redirect('login')

    if request.method == 'POST':
        propertyid = request.POST.get('property_id')
        filetype = request.POST.get('filetype')
        uploaded_files = request.FILES.getlist('file')
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

        for uploaded_file in uploaded_files:
            # Process each uploaded file
            # You can access the file content using uploaded_file.read()

            # Example: Save the file to a specific directory
            if filetype == "photo":
                folder_path = getattr(settings, "PATH_PROPERTY", None) + str(propertyid) + "//"
            if filetype == "floorplan":
                folder_path = getattr(settings, "PATH_FLOORPLAN", None) + str(propertyid) + "//"
            if filetype == "document":
                folder_path = getattr(settings, "PATH_DOCUMENT", None) + str(propertyid) + "//"

            os.makedirs(folder_path, exist_ok=True)
            with open(folder_path + uploaded_file.name, 'wb') as file:
                for chunk in uploaded_file.chunks():
                    file.write(chunk)
            propertyfile = PropertyFiles()
            propertyfile.propertyid = propertyid
            propertyfile.filetype = filetype
            propertyfile.filename = uploaded_file.name
            propertyfile.filetitle = ""
            propertyfile.filedescription = ""
            propertyfile.filetitle_s = ""
            propertyfile.filedescription_s = ""
            propertyfile.filetitle_e = ""
            propertyfile.filedescription_e = ""
            propertyfile.sequence = 0
            propertyfile.loginid = request.session.get('loginid')
            propertyfile.createdate = datetime_str
            propertyfile.modifydate = datetime_str
            propertyfile.iswatermark = 0
            propertyfile.isapprove = 1
            propertyfile.ismain = 0
            propertyfile.save(using='infinyrealty')

            if propertyfile.filetype == "photo" or propertyfile.filetype == "floorplan":
                filename = propertyfile.filename
                filename_extension = os.path.splitext(filename)[1][1:].lower()
                if "jpg" in filename_extension or "jpeg" in filename_extension or "png" in filename_extension:
                    if propertyfile.filetype == "photo":
                        filename = getattr(settings, "PATH_PROPERTY", None) + str(propertyfile.propertyid) + "\\"+propertyfile.filename
                        filename_wm = getattr(settings, "PATH_PROPERTY", None) + str(propertyfile.propertyid) + "\\"+propertyfile.filename.replace("."+filename_extension, "-wm."+filename_extension)
                    if propertyfile.filetype == "floorplan":
                        filename = getattr(settings, "PATH_FLOORPLAN", None) + str(propertyfile.propertyid) + "\\" + propertyfile.filename
                        filename_wm = getattr(settings, "PATH_FLOORPLAN", None) + str(propertyfile.propertyid) + "\\" + propertyfile.filename.replace("."+filename_extension, "-wm."+filename_extension)
                    filename_logo = getattr(settings, "PATH_MAIN", None) + "infinyrealty_logo_high.png"
                    watermark_method = 2

                    if watermark_method == 1:
                        base_image = Image.open(filename)
                        watermark_image = Image.open(filename_logo)
                        if propertyfile.filetype == "photo":
                            watermark_ratio = 0.1  # 10% of the base image size
                        else:
                            watermark_ratio = 0.03  # 3% of the base image size
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
                        if propertyfile.filetype == "photo" or propertyfile.filetype == "floorplan":
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
                                PropertyFiles.objects.using('infinyrealty').filter(fileid=propertyfile.fileid).update(iswatermark=1)
                            except Exception as e:
                                exception_type, exception_object, exception_traceback = sys.exc_info()
                                filename = exception_traceback.tb_frame.f_code.co_filename
                                line_number = exception_traceback.tb_lineno
                                return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

        return HttpResponse('Files uploaded successfully')
    return HttpResponse('File upload failed')

@csrf_exempt
def upload_foreign(request):
    if not request.session.get('username'): return redirect('login')

    if request.method == 'POST':
        propertyid = request.POST.get('property_id')
        filetype = request.POST.get('filetype')
        uploaded_files = request.FILES.getlist('file')
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

        for uploaded_file in uploaded_files:
            # Process each uploaded file
            # You can access the file content using uploaded_file.read()

            # Example: Save the file to a specific directory
            if filetype == "photo":
                folder_path = getattr(settings, "PATH_PROPERTY_FOREIGN", None) + str(propertyid) + "//"
            if filetype == "floorplan":
                folder_path = getattr(settings, "PATH_FLOORPLAN_FOREIGN", None) + str(propertyid) + "//"
            if filetype == "document":
                folder_path = getattr(settings, "PATH_DOCUMENT", None) + str(propertyid) + "//"

            os.makedirs(folder_path, exist_ok=True)
            with open(folder_path + uploaded_file.name, 'wb') as file:
                for chunk in uploaded_file.chunks():
                    file.write(chunk)
            propertyfile = PropertyForeignFiles()
            propertyfile.propertyforeignid = propertyid
            propertyfile.filetype = filetype
            propertyfile.filename = uploaded_file.name
            propertyfile.filetitle = ""
            propertyfile.filedescription = ""
            propertyfile.filetitle_s = ""
            propertyfile.filedescription_s = ""
            propertyfile.filetitle_e = ""
            propertyfile.filedescription_e = ""
            propertyfile.sequence = 0
            propertyfile.loginid = request.session.get('loginid')
            propertyfile.createdate = datetime_str
            propertyfile.modifydate = datetime_str
            propertyfile.iswatermark = 0
            propertyfile.isapprove = 1
            propertyfile.ismain = 0
            propertyfile.save(using='infinyrealty')

            if propertyfile.filetype == "photo" or propertyfile.filetype == "floorplan":
                filename = propertyfile.filename
                filename_extension = os.path.splitext(filename)[1][1:].lower()
                if "jpg" in filename_extension or "jpeg" in filename_extension or "png" in filename_extension:
                    if propertyfile.filetype == "photo":
                        filename = getattr(settings, "PATH_PROPERTY_FOREIGN", None) + str(propertyfile.propertyforeignid) + "\\"+propertyfile.filename
                        filename_wm = getattr(settings, "PATH_PROPERTY_FOREIGN", None) + str(propertyfile.propertyforeignid) + "\\"+propertyfile.filename.replace("."+filename_extension, "-wm."+filename_extension)
                    if propertyfile.filetype == "floorplan":
                        filename = getattr(settings, "PATH_FLOORPLAN_FOREIGN", None) + str(propertyfile.propertyforeignid) + "\\" + propertyfile.filename
                        filename_wm = getattr(settings, "PATH_FLOORPLAN_FOREIGN", None) + str(propertyfile.propertyforeignid) + "\\" + propertyfile.filename.replace("."+filename_extension, "-wm."+filename_extension)
                    filename_logo = getattr(settings, "PATH_MAIN", None) + "infinyrealty_logo_high.png"
                    watermark_method = 2

                    if watermark_method == 1:
                        base_image = Image.open(filename)
                        watermark_image = Image.open(filename_logo)
                        if propertyfile.filetype == "photo":
                            watermark_ratio = 0.1  # 10% of the base image size
                        else:
                            watermark_ratio = 0.03  # 3% of the base image size
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
                        if propertyfile.filetype == "photo" or propertyfile.filetype == "floorplan":
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
                                PropertyForeignFiles.objects.using('infinyrealty').filter(fileid=propertyfile.fileid).update(iswatermark=1)
                            except Exception as e:
                                exception_type, exception_object, exception_traceback = sys.exc_info()
                                filename = exception_traceback.tb_frame.f_code.co_filename
                                line_number = exception_traceback.tb_lineno
                                return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

        return HttpResponse('Files uploaded successfully')
    return HttpResponse('File upload failed')

@csrf_exempt
def upload_newproperty(request):
    if not request.session.get('username'): return redirect('login')

    if request.method == 'POST':
        propertyid = request.POST.get('property_id')
        filetype = request.POST.get('filetype')
        uploaded_files = request.FILES.getlist('file')
        datetime_dt = datetime.datetime.today()
        datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")

        for uploaded_file in uploaded_files:
            # Process each uploaded file
            # You can access the file content using uploaded_file.read()

            # Example: Save the file to a specific directory
            if filetype == "newphoto":
                folder_path = getattr(settings, "PATH_PROPERTY_NEW", None) + str(propertyid) + "//"
            if filetype == "newfloorplan":
                folder_path = getattr(settings, "PATH_FLOORPLAN_NEW", None) + str(propertyid) + "//"

            os.makedirs(folder_path, exist_ok=True)
            with open(folder_path + uploaded_file.name, 'wb') as file:
                for chunk in uploaded_file.chunks():
                    file.write(chunk)
            propertyfile = PropertyFiles()
            propertyfile.propertyid = propertyid
            propertyfile.filetype = filetype
            propertyfile.filename = uploaded_file.name
            propertyfile.filetitle = ""
            propertyfile.filedescription = ""
            propertyfile.filetitle_s = ""
            propertyfile.filedescription_s = ""
            propertyfile.filetitle_e = ""
            propertyfile.filedescription_e = ""
            propertyfile.sequence = 0
            propertyfile.loginid = request.session.get('loginid')
            propertyfile.createdate = datetime_str
            propertyfile.modifydate = datetime_str
            propertyfile.iswatermark = 0
            propertyfile.isapprove = 1
            propertyfile.ismain = 0
            propertyfile.save(using='infinyrealty')

            if propertyfile.filetype == "newphoto" or propertyfile.filetype == "newfloorplan":
                filename = propertyfile.filename
                filename_extension = os.path.splitext(filename)[1][1:].lower()
                if "jpg" in filename_extension or "jpeg" in filename_extension or "png" in filename_extension:
                    if propertyfile.filetype == "newphoto":
                        filename = getattr(settings, "PATH_PROPERTY_NEW", None) + str(propertyfile.propertyid) + "\\"+propertyfile.filename
                        filename_wm = getattr(settings, "PATH_PROPERTY_NEW", None) + str(propertyfile.propertyid) + "\\"+propertyfile.filename.replace("."+filename_extension, "-wm."+filename_extension)
                    if propertyfile.filetype == "newfloorplan":
                        filename = getattr(settings, "PATH_FLOORPLAN_NEW", None) + str(propertyfile.propertyid) + "\\" + propertyfile.filename
                        filename_wm = getattr(settings, "PATH_FLOORPLAN_NEW", None) + str(propertyfile.propertyid) + "\\" + propertyfile.filename.replace("."+filename_extension, "-wm."+filename_extension)
                    filename_logo = getattr(settings, "PATH_MAIN", None) + "infinyrealty_logo_high.png"
                    watermark_method = 2

                    if watermark_method == 1:
                        base_image = Image.open(filename)
                        watermark_image = Image.open(filename_logo)
                        if propertyfile.filetype == "newphoto":
                            watermark_ratio = 0.1  # 10% of the base image size
                        else:
                            watermark_ratio = 0.03  # 3% of the base image size
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
                        if propertyfile.filetype == "newphoto" or propertyfile.filetype == "newfloorplan":
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
                                PropertyFiles.objects.using('infinyrealty').filter(fileid=propertyfile.fileid).update(iswatermark=1)
                            except Exception as e:
                                exception_type, exception_object, exception_traceback = sys.exc_info()
                                filename = exception_traceback.tb_frame.f_code.co_filename
                                line_number = exception_traceback.tb_lineno
                                return HttpResponse("Error line " + str(line_number) + ": " + str(e) + action)

        return HttpResponse('Files uploaded successfully')

    return HttpResponse('File upload failed')

def combine_docx_files(input_files, output_file):
    """Combines multiple DOCX files, attempting to preserve more content."""

    combined_doc = Document()

    for input_file in input_files:
        try:
            doc = Document(input_file)
            for paragraph in doc.paragraphs:
                combined_doc.add_paragraph(paragraph.text) #Add paragraphs to maintain basic structure

            for table in doc.tables:
                num_rows = len(table.rows)
                num_cols = len(table.rows[0].cells)

                # Create table in the output doc
                new_table = combined_doc.add_table(rows=num_rows, cols=num_cols)

                # Copy table data
                for row_index, row in enumerate(table.rows):
                    for cell_index, cell in enumerate(row.cells):
                        new_table.cell(row_index, cell_index).text = cell.text

            #Handle images (simplified to avoid earlier issues)
            for i in range(len(doc.inline_shapes)):
              combined_doc.add_paragraph().add_run().add_picture(doc.inline_shapes[i]._inline.blob)

        except Exception as e:
            print(f"Error processing {input_file}: {e}")

    combined_doc.save(output_file)

def merge_documents_with_headers_footers(doc_files, output_file):
    # Create a new Document to hold the merged content
    merged_document = Document()

    for file in doc_files:
        # Load each document
        doc = Document(file)

        # If the document has sections, copy headers and footers
        for section in doc.sections:
            # Copy headers
            for header in section.headers.values():
                merged_document.sections[0].headers[header._type].text = header.text

            # Copy footers
            for footer in section.footers.values():
                merged_document.sections[0].footers[footer._type].text = footer.text

        # Append content from the current document to the merged document
        for element in doc.element.body:
            merged_document.element.body.append(element)

        # Optionally add a page break after each document
        merged_document.add_page_break()

    # Save the merged document
    merged_document.save(output_file)


def combine_documents(doc_files, output_file):
    # Create a new Document to hold the merged content
    merged_document = Document()

    for file in doc_files:
        # Load each document
        doc = Document(file)

        # Copy the entire body content while preserving formatting
        for element in doc.element.body:
            merged_document.element.body.append(element)

        # Optionally add a page break after each document
        merged_document.add_page_break()

    # Save the merged document
    merged_document.save(output_file)

def merge_documents_with_headers(doc_files, output_file):
    # Create a new Document to hold the merged content
    merged_document = Document()

    for file in doc_files:
        # Load each document
        doc = Document(file)

        # Copy headers and footers
        if doc.sections:
            for section in doc.sections:
                # Copy headers
                for header in section.headers:
                    merged_document.sections[0].headers[header.type].text = section.headers[header.type].text

                # Copy footers
                for footer in section.footers:
                    merged_document.sections[0].footers[footer.type].text = section.footers[footer.type].text

        # Append content from the current document to the merged document
        for element in doc.element.body:
            merged_document.element.body.append(element)

        # Optionally add a page break after each document
        merged_document.add_page_break()

    # Save the merged document
    merged_document.save(output_file)

def append_to_document(source_file, target_file):
    # Load the source and target documents
    source_doc = Document(source_file)
    target_doc = Document(target_file)

    # Iterate through each paragraph in the source document
    for paragraph in source_doc.paragraphs:
        # Append the paragraph to the target document
        target_doc.add_paragraph(paragraph.text)

    # Save the modified target document
    target_doc.save(target_file)
def merge_documents(doc_files, output_file):
    # Create a new Document
    master_doc = Document()
    composer = Composer(master_doc)

    for file in doc_files:
        doc = Document(file)
        composer.append(doc)

    composer.save(output_file)

def combine_word_files(file_list, output_file):
    # Create a new Document
    combined_doc = Document()

    for file in file_list:
        # Open each Word file
        doc = Document(file)

        # Add a page break before adding the next document (optional)
        #if combined_doc.paragraphs:
        #    combined_doc.add_page_break()

        # Add the content of the current document to the combined document
        for element in doc.element.body:
            combined_doc.element.body.append(element)

    # Save the combined document
    combined_doc.save(output_file)

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


def accesslog(accessid, loginid, username, logtype, propertyno, propertyid, logdesc):
    accesslog = AccessLogs()
    accesslog.loginid = loginid
    accesslog.username = username
    accesslog.logdatetime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    accesslog.logtype = logtype
    accesslog.subcatid = accessid
    subcategory = SubCategories.objects.using('infinyrealty').get(subcatid=accessid)
    accesslog.pagename = subcategory.subcatname
    accesslog.propertyno = propertyno
    accesslog.propertyid = propertyid
    accesslog.logdesc = logdesc
    accesslog.save(using='infinyrealty')

@register.filter
def getDictItem(dict, key):
    return dict.get(key)

