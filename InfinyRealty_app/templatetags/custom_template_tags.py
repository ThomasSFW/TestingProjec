from django import template
from django.template.defaultfilters import stringfilter
from django.http import QueryDict
from datetime import datetime, timedelta
from django.utils.timezone import get_current_timezone

from InfinyRealty_app.models import Tabs, Categories, SubCategories, Users, Teams, Ranks, Schools, Schooltypes, Sessions, Districts, Financetypes, Curriculumtypes, ESRschools, ESRschoolsER, SSBs, C12Level, C12Comments, LogTypes, LogEnquiryResponses, KLALevel, KLAComments, SchoolDevelopmentPlanLevel, AccessRights
from InfinyRealty_app.models import CodeDetails, Shops, Printer, Propertys
register = template.Library()
import urllib.parse as urlparse
import mimetypes
import pyodbc
import re
import json
from django.conf import settings

@register.simple_tag
def setvar(val=None):
  return val

@register.filter(name='split')
def split(value, key):
  return value.split(key)

@register.filter(name='rstripc')
def rstripc(value):
  return value.rstrip(',')

@register.filter(name='trim')
def trim(value):
  return value.strip()

@register.filter(name='mid')
def mid(s, offset, amount):
    return s[offset-1:offset+amount-1]

@register.filter(name='addtext')
def addtext(value, arg):
  return str(value) + str(arg)

@register.filter(name='showlang')
def showlang(value, lang):
    if lang == "": lang = "tc"
    WebText = CodeDetails.objects.using('infinyrealty').filter(code_id=13).filter(code_detail_name=value)

    if WebText:
        if lang == "" or lang == "tc":
            return WebText[0].code_detail_name
        elif lang == "sc":
            return WebText[0].code_detail_name_s
        elif lang == "en":
            return WebText[0].code_detail_name_e

@register.filter(name='in_content_detail')
def in_content_detail(value, text):
    value1 = value.filter(sequence=text)
    text1 = value1[0].content_detail_name
    return text1

@register.filter(name='in_property')
def in_property(value):
    property = Propertys.objects.using('infinyrealty').filter(propertyid=value)
    if property:
        value = property[0].propertyname
    else:
        value = ""
    return value

@register.filter(name='getPropertyNo')
def getPropertyNo(value):
    property = Propertys.objects.using('infinyrealty').filter(propertyid=value)
    if property:
        value = property[0].propertyno
    else:
        value = ""
    return value

@register.filter(name='addtext')
def addtext(value, arg):
  return str(value) + str(arg)

@register.filter(name='showwatermark')
def showwatermark(value):
    if value == "" or value is None:
        return ""
    result = value.replace(".jpg","-wm.jpg")
    result = result.replace(".jpeg","-wm.jpeg")
    result = result.replace(".png","-wm.png")
    return result

@register.filter(name='remove_p_tags')
def remove_p_tags(value):
    result = value.replace("<p>","")
    result = result.replace("</p>","")
    return result

@register.filter(name='format_numeric')
def format_numeric(value):
    try:
        if value is None:
            return ""
        if value >= 1000000000:
            return f"{value / 1000000000:.0f}B"
        elif value >= 1000000:
            return f"{value / 1000000:.0f}M"
        elif value >= 1000:
            return f"{value / 1000:.0f}K"
        else:
            return str(value)
    except (ValueError, TypeError):
        return value

@register.filter(name='format_number_with_commas')
def format_number_with_commas(value):
    try:
        value = int(value)
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value

@register.filter
def get_current_timezone(val=None):
    return get_current_timezone()

@register.filter(name='teamtosection')
def teamtosection(value):
    value = value.replace("Ind. Sect.","Indicators Section")
    value = value.replace("IND","Indicators Section")
    value = value.replace("Team","Section")
    return value

@register.filter(name='schoolyear')
def schoolyear(value):
    value1 = int(value)+1      
    value1 = str(value1)
    value = value.replace(value,value[0:4]+"/"+value1[2:4])
    return value

@register.filter(name='currentschoolyear')
def currentschoolyear(value):
    years = Users.objects.using('sqp').order_by('-year').values('year').distinct()
    value = years[0]['year']
    return value

@register.filter(name='bookingslot')
def bookingslot(value):
    if value:
        if value[-1] == ',':
            value = value.replace(value,value[0:-1])
            value = value.replace("0830-0930,0930-1030,1030-1130,1130-1230,1400-1500,1500-1600,1600-1700,1700-1800", "WD (0830-1800)")
            value = value.replace("0830-0930,0930-1030,1030-1130,1130-1230","AM (0830-1230)")
            value = value.replace("1400-1500,1500-1600,1600-1700,1700-1800","PM (1400-1800)")
            value = value.replace("-0930,0930","")
            value = value.replace("-1030,1030","")
            value = value.replace("-1130,1130","")
            value = value.replace("-1500,1500","")
            value = value.replace("-1600,1600","")
            value = value.replace("-1700,1700","")
    return value

@register.filter(name='eventtype')
def eventtype(value):
    if value == 'Inspection':
        value = value.replace("Inspection", "I")        
    if value == 'Pre-ESR Introduction Session':
        value = value.replace("Pre-ESR Introduction Session", "P")           
    if value == 'Vetting':
        value = value.replace("Vetting", "V")              
    if value == 'Meeting':
        value = value.replace("Meeting", "M")        
    if value == 'Training':
        value = value.replace("Training", "T")        
    if value == 'Others':
        value = value.replace("Others", "O")        
    return value
  
@register.filter(name='schooltypeid')    
def schooltypeid(value):
    schooltypes = Schooltypes.objects.using('schoolmaster').filter(schooltypeid=value)
    value = schooltypes[0].schooltypedesc
    return value

@register.filter(name='schoollevel')
def schoollevel(value):
    if value == 'P':
        value = "Primary"
    if value == 'M':
        value = "Secondary"
    if value == 'SMP':
        value = "Special"
    if value == 'Special':
        value = "Special"
    return value

@register.filter(name='codeqa')
def codeqa(value):
    value = value.replace("EP0", "EP")
    value = value.replace("ES0", "ES")
    value = value.replace("EX0", "ESP")
    return value

@register.filter(name='codeparentid')
def codeparentid(value):
    codedetails = CodeDetails.objects.using('infinyrealty').filter(code_detail_id=value)
    try:
        value = codedetails[0].code_detail_name
    except:
        value = "不適用"
    return value

@register.filter(name='tasteid')
def tasteid(value):
    codedetails = CodeDetails.objects.using('zenpos').filter(shop="east", code_id=11, status=1, code_key=value)
    try:
        value = codedetails[0].code_detail_name
    except:
        value = ""
    return value

@register.filter(name='sessionid')    
def sessionid(value):
    sessions = Sessions.objects.using('schoolmaster').filter(sessionid=value)
    value = sessions[0].sessiondesc
    return value

@register.filter(name='sessiontype')
def sessiontype(value):
    if value == 'W':
        value = "WD"
    if value == 'A':
        value = "AM"
    if value == 'P':
        value = "PM"
    return value

@register.filter(name='districtid')    
def districtid(value):
    districts = Districts.objects.using('schoolmaster').filter(districtid=value)
    value = districts[0].districtname
    return value
    
@register.filter(name='districtid1')    
def districtid1(value):
    districts1 = Districts.objects.using('schoolmaster').filter(districtid1=value)
    value = districts1[0].districtnamec
    return value

@register.filter(name='financetypeid')    
def financetypeid(value):
    financetypes = Financetypes.objects.using('schoolmaster').filter(financetypeid=value)
    value = financetypes[0].financetypedesc
    return value

@register.filter(name='curriculumtypeid')    
def curriculumtypeid(value):
    curriculumtypes = Curriculumtypes.objects.using('schoolmaster').filter(curriculumtypeid=value)
    try:
        value = curriculumtypes[0].curriculumtypedesc
    except:
        value = ""
    return value
    
@register.filter(name='ssbid')
def ssbid(value):
    ssbs = SSBs.objects.using('schoolmaster').filter(ssbid=value)
    try:
        value = value + " - " + ssbs[0].ssbdesc
    except:
        value = ""
    return value

@register.filter(name='logtypeid')
def logtypeid(value):
    logtypes = LogTypes.objects.using('enquirylog').filter(logtypeid=value)
    try:
        value = logtypes[0].logtypedesc
    except:
        value = ""
    return value

@register.filter(name='isactive')
def isactive(value):
    if value == 1:
        value = "Active"
    if value == 0:
        value = "Inactive"
    return value  

@register.filter(name='get_list_item')
def get_list_item(list_obj, index):
    try:
        return list_obj[index]
    except IndexError:
        return None

@register.filter(name='get_file_icon')
def get_file_icon(filename):
    mimetype, _ = mimetypes.guess_type(filename)
    if mimetype is None:
        return None
    if mimetype.startswith('image/'):
        return 'file-icon/image.png'
    elif mimetype.startswith('audio/'):
        return 'file-icon/audio.png'
    elif mimetype.startswith('video/'):
        return 'file-icon/video.png'
    elif mimetype == 'application/pdf':
        return 'file-icon/pdf.png'
    elif mimetype == 'application/msword' or mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'file-icon/doc.png'
    elif mimetype == 'application/vnd.ms-excel' or mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimetype == 'application/vnd.ms-excel.sheet.macroEnabled.12':
        return 'file-icon/xls.png'
    elif mimetype == 'application/x-zip-compressed':
        return 'file-icon/zip-folder.png'
    # Add more MIME type to icon mappings as needed
    else:
        return 'file-icon/generic.png'+mimetype

@register.filter(name='in_schoolid')
def in_schoolid(value, schoolid):
    return value.filter(schoolid=schoolid)

@register.filter(name='in_SchoolID')
def in_SchoolID(value, schoolid):
    return value.filter(SchoolID=schoolid)

@register.filter(name='filter_by_school_id')
def filter_by_school_id(records, school_id):
    for record in records:
        if record['schoolid'] == school_id:
            return record
    return ""

@register.filter(name='filter_by_schoolid')
def filter_by_school_id(records, schoolid):
    for record in records:
        if record['schoolid'] == schoolid:
            return record
    return ""

@register.filter(name='filter_by_field')
def filter_by_field(record, field):
    try:
        value = record[field]
    except:
        value = ""
    return value

@register.filter(name='in_year')
def in_year(value, year):
    return value.filter(year=year)

@register.filter(name='in_loginid')
def in_loginid(value, loginid):
    return value.filter(loginid=loginid)

@register.filter(name='in_school_and_year')
def in_school_and_year(value, schoolid, year):
    return value.filter(schoolid=schoolid, year=year)

@register.filter(name='in_c12year')
def in_year(value, year):
    return value.filter(c12year=year)

@register.filter(name='in_sdptype')
def in_sdptype(value, sdptype):
    return value.filter(sdptype=sdptype)

@register.filter(name='in_functionid')
def in_functionid(value, functionid):
    if functionid in value:
        return 1
    else:
        return 0

@register.filter(name='make_list')
def make_list(value):
    return [None] * value

@register.filter(name='get_item')
def get_item(value, index):
    try:
        return value[index].answerTypeID
    except (IndexError, KeyError):
        return None

@register.filter(name='getESRRating', is_safe=True)
def getESRRating(value):
    if value == 1: value = "1"
    if value == 2: value = "1+"
    if value == 3: value = "2-"
    if value == 4: value = "2"
    if value == 5: value = "2+"
    if value == 6: value = "3-"
    if value == 7: value = "3"
    if value == 8: value = "3+"
    if value == 9: value = "4"
    return value

@register.filter(name='getConcern', is_safe=True)
def getConcern(value):
    if value == 1: value = "推介"
    if value == 2: value = "關注"
    return value

@register.filter(name='getYesNo', is_safe=True)
def getYesNo(value):
    if value == 1: value = "是"
    if value == 0: value = "否"
    if value == None: value = "不適用"
    return value

@register.filter(name='getPicID')
def getPicID(value):
    school = Schools.objects.using('schoolmaster').filter(schoolid=value)
    try:
        url = school[0].urlprofile
        parsed = urlparse.urlparse(url)
    except:
        pic_id = "1"
    try:
        pic_id = urlparse.parse_qs(parsed.query)['sch_id'][0]
    except:
        pic_id = "1"
    return pic_id

@register.filter(name='getSchoolName')
def getSchoolName(value):
    school = Schools.objects.using('schoolmaster').filter(schoolid=value)
    try:
        schoolname = school[0].schoolnamec
        return schoolname
    except:
        return ""

@register.filter(name='getSpecialType')
def getSpecialType(value):
    school = Schools.objects.using('schoolmaster').filter(schoolid=value)
    try:
        url = school[0].urlprofile
        if "spsp" in url:
            return "1"
        else:
            return "0"
    except:
        return "0"

@register.filter(name='getSchoolType')
def getSchoolType(value):
    try:
        if value[10] == "2":
            return "#PRI"
        if value[10] == "3":
            return "#SEC"
        if value[10] == "1":
            return "#SPEC"
    except:
        value = ""
    return value

@register.filter(name='getComment')
def getComment(value):
    c12comments = C12Comments.objects.using('esrform').filter(commentid=value)
    value = c12comments[0].commentdescc
    return value

@register.filter(name='getCaption', is_safe=True)
def getCaption(value, year):
    try:
        c12levels = C12Level.objects.using('esrform').filter(levelid=value)
        for c12level in c12levels:
            if c12level.c12year == year:
                value = c12level.leveldescc
        return value
    except ValueError:
        value = ""
        return value

@register.filter(name='getKLAComment')
def getKLAComment(value):
    klacomments = KLAComments.objects.using('klaform').filter(commentid=value)
    value = klacomments[0].commentdescc
    return value

@register.filter(name='getKLACaption')
def getKLACaption(value, args):
    try:
        qs = QueryDict(args)
        klalevels = KLALevel.objects.using('klaform').filter(levelid=value).filter(part=qs['kla'])
        for klalevel in klalevels:
            if str(klalevel.klayear) == str(qs['year']):
                value = klalevel.leveldescc
        return value
    except ValueError:
        value = ""
        return value

@register.filter(name='getSDPCaption')
def getSDPCaption(value, args):
    try:
        qs = QueryDict(args)
        schooldevelopmentplanlevels = SchoolDevelopmentPlanLevel.objects.using('schoolmaster').filter(levelid=value).filter(sdpyear=2014)
        for schooldevelopmentplanlevel in schooldevelopmentplanlevels:
            value = schooldevelopmentplanlevel.leveldescc
        return value
    except ValueError:
        value = ""
        return value

@register.filter(name='getAccessRight')
def getAccessRight(arg1, arg2):
    try:
        accessrights = AccessRights.objects.using('infinyrealty').filter(functionid=arg1).filter(username=arg2)
        approved = accessrights.first().approved if accessrights.exists() else None
        #approved = accessrights[0].approved
        return approved
    except AccessRights.DoesNotExist:
        return "-1"
    except ValueError:
        value = "0"
        return value

@register.filter(name='getFunctionCount')
def getFunctionCount(arg1):
    try:
        accessrights_count = AccessRights.objects.using('infinyrealty').filter(functionid=arg1).count()
        return accessrights_count
    except AccessRights.DoesNotExist:
        return "-1"
    except ValueError:
        value = "0"
        return value

@register.filter(name='getKPMExistList', is_safe=True)
def getKPMExistList(value, id):
    try:
        cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=' + getattr(settings, "AUTH_ESDA_QA_HOST", None) + ';UID=' + getattr( settings, "AUTH_ESDA_QA_USER", None) + ';PWD=' + getattr(settings, "AUTH_ESDA_QA_PASSWORD", None) + ';Database=ESDA_QA')
        cursor = cnxn.cursor()
        cursor.execute("SELECT KPM_CODE from VIEW_KPM_SCHOOL_RESULT_GROUP1 WHERE SUBMIT_ID = '"+str(id)+"' AND VERSION = '"+value+"'")
        KPMSchoolResultGroup = cursor.fetchall()

        value = KPMSchoolResultGroup
        return value
    except ValueError:
        value = ""
        return value

@register.filter(name='getShopName')
def getShopName(value):
    arr = value.split(',')
    keys = []  # Initialize an empty list to store the keys
    for item in arr:
        key = item.split()[0]  # Extract the key from each item
        shop = Shops.objects.using('zenpos').filter(shop_code=key)
        keys.append(shop[0].shop_name)  # Add the key to the list
    result = "<br>".join(keys)  # Join the keys using commas
    return result

@register.filter(name='getLoginName')
def getLoginName(value):
    try:
        value = str(value)
        if value is None or value == "":
            return ""
        else:
            arr = value.split(',')
            keys = []  # Initialize an empty list to store the keys
            if arr:
                for item in arr:
                    key = item.split()[0]  # Extract the key from each item
                    user = Users.objects.using('infinyrealty').filter(loginid=key)
                    keys.append(user[0].loginnamedesc)  # Add the key to the list
                result = "<br>".join(keys)  # Join the keys using commas
        return result
    except (ValueError, TypeError):
        return value

@register.filter(name='getFoodCategory')
def getFoodCategory(value):
    codedetail = CodeDetails.objects.using('zenpos').filter(code_key=value,code_id=2)
    try:
        FoodCategory = codedetail[0].code_detail_name
        return FoodCategory
    except:
        return value

@register.filter(name='getPeriodArray')
def getPeriodArray(value):
    arr = value.split(',')
    keys = []  # Initialize an empty list to store the keys
    for item in arr:
        key = item.split()[0]  # Extract the key from each item
        codedetail = CodeDetails.objects.using('zenpos').filter(code_key=key, code_id=1)
        keys.append(codedetail[0].code_detail_name)  # Add the key to the list
    result = "<br>".join(keys)  # Join the keys using commas
    return result

@register.filter(name='getDimSumCategoryName')
def getDimSumCategoryName(value):
    codedetail = CodeDetails.objects.using('zenpos').filter(code_key=value,code_id=7)
    try:
        DimSumCategoryName = codedetail[0].code_detail_name
        return DimSumCategoryName
    except:
        return value

@register.filter(name='getFoodStatus')
def getFoodStatus(value):
    codedetail = CodeDetails.objects.using('zenpos').filter(code_key=value,code_id=4)
    try:
        FoodStatus = codedetail[0].code_detail_name
        return FoodStatus
    except:
        return value

@register.filter(name='getPrintLocation')
def getPrintLocation(value):
    printer = Printer.objects.using('infinyrealty').filter(location_code=value)
    try:
        PrintLocation = printer[0].location
        return PrintLocation
    except:
        return value

@register.filter(name='add_commas')
def add_commas(value):
    value = str(value)
    parts = []
    while len(value) > 3:
        parts.insert(0, value[-3:])
        value = value[:-3]
    parts.insert(0, value)
    return ','.join(parts)

@register.filter(name='addstr')
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)

@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg

@register.filter(name='multiple', is_safe=True)
def multiple(value, arg):
    return value * arg

@register.filter(name='divide')
def divide(value, arg):
    try:
        if int(arg) != 0:
            result = int(value) / int(arg)
        else:
            result = 0
        return result
    except (ValueError, ZeroDivisionError):
        return 0.0

@register.filter(name='divide_round')
def divide_round(value, arg):
    try:
        if int(arg) != 0:
            result = int(value) / int(arg)
        else:
            result = 0
        return round(result, 1)
    except (ValueError, ZeroDivisionError):
        return 0.0


@register.filter(name='divide_round2')
def divide_round2(value, arg):
    try:
        if int(arg) != 0:
            result = int(value) / int(arg)
        else:
            result = 0.00
        return round(result, 2)
    except (ValueError, ZeroDivisionError):
        return 0.00

@register.filter(name='currency')
def currency(dollars):
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

@register.filter(name='cint')
def cint(value):
    try:
        if value is None or value == "":
            return ""
        return int(value)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter(name='index')
def index(indexable, i):
    return indexable[(int(i)-1)]

@register.filter(name='getFormValue')
def getFormValue(value, list):
    return str(value) + str(list)

@register.filter(name='mult', is_safe=True)
def mult(value, arg):
    return int(value) * int(arg)

@register.filter(name='multdec', is_safe=True)
def multdec(value, arg):
    try:
        arg = int(arg)
        if value is None:
            return value  # Invalid arg.
        else:
            return (value) * (arg)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter(name='setzero', is_safe=True)
def setzero(value):
    if value == 0:
        value = ""
    return value

@register.filter(name='plus_days', is_safe=True)
def plus_days(value, days):
    try:
        if value is None:
            return value  # Invalid arg.
        else:
            return value + timedelta(days=days)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter(name='plus_hours', is_safe=True)
def plus_hours(value, hours):
    try:
        if value is None:
            return value  # Invalid arg.
        else:
            return value + timedelta(hours=hours)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter(name='add_dash', is_safe=True)
def add_dash(value):
    data = value[0:8] + "-" + value[8:16] + "-" + value[16:24] + "-" + value[24:32] + "-" + value[32:40]
    return data

@register.filter(name='add_dash5', is_safe=True)
def add_dash5(value):
    data = value[0:5] + "-" + value[5:10] + "-" + value[10:15] + "-" + value[15:20] + "-" + value[20:25]
    return data

@register.filter(name='update_variable', is_safe=True)
def update_variable(value):
    data = value
    return data

@register.filter(name='last_day_of_month', is_safe=True)
def last_day_of_month(date_value):
    return date_value.replace(day=monthrange(date_value.year, date_value.month)[1])

@register.filter(name='percentage', is_safe=True)
def percentage(value):
    return float(value) * 100

@register.filter(name='subr', is_safe=True)
def subr(value, arg):
    return int(arg) - int(value)

@register.filter(name='replace_str_linebreak', is_safe=True)
def replace_str_linebreak(value, arg):
    try:
        value = value.replace(arg, "\n")
        if value is None:
            return value  # Invalid arg.
        else:
            return (value)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter(name='replace_str_br', is_safe=True)
def replace_str_br(value, arg):
    try:
        value = value.replace(arg, "<br>")
        if value is None:
            return value  # Invalid arg.
        else:
            return (value)
    except ValueError:
        return value  # Fail silently for an invalid argument


@register.filter(name='replace_str', is_safe=True)
def replace_str(value, arg):
    try:
        value = value.replace(arg, "")
        if value is None:
            return value  # Invalid arg.
        else:
            return (value)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter(name='replace_workarea', is_safe=True)
def replace_workarea(value, arg):
    try:
        value = value.replace("Indicators Section", arg)
        value = value.replace("Indicator%20Section", arg)
        if value is None:
            return value  # Invalid arg.
        else:
            return (value)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter(name='replace_to', is_safe=True)
def replace_to(value, arg):
    try:
        value = value.replace(arg, " <i class='fa fa-arrow-right' aria-hidden='true'></i> ")
        if value is None:
            return value  # Invalid arg.
        else:
            return (value)
    except ValueError:
        return value  # Fail silently for an invalid argument

@register.filter('url_target_blank', is_safe = True)
def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')

@register.filter(name='comm_type', is_safe=True)
def comm_type(value):
    if value == 'Phone':
        value = value.replace("Phone", "fa fa-phone")        
    if value == 'Email':
        value = value.replace("Email", "fa fa-envelope")           
    if value == 'Fax':
        value = value.replace("Fax", "fa fa-fax")              
    if value == 'Seminar':
        value = value.replace("Seminar", "fa fa-users")       
    return value

@register.filter(name='url_target_blank', is_safe=True)
def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')

@register.filter(name='translate_days', is_safe=True)
def translate_days(value):
    if value == "Mon":
        value = '一'
    if value == "Tue":
        value = '二'
    if value == "Wed":
        value = '三'
    if value == "Thu":
        value = '四'
    if value == "Fri":
        value = '五'
    if value == "Sat":
        value = '六'
    if value == "Sun":
        value = '日'

    return value

@register.filter(name='translate_month_year', is_safe=True)
def translate_month_year(value):
    chinese_months = {
        'Jan': '一月',
        'Feb': '二月',
        'Mar': '三月',
        'Apr': '四月',
        'May': '五月',
        'Jun': '六月',
        'Jul': '七月',
        'Aug': '八月',
        'Sep': '九月',
        'Oct': '十月',
        'Nov': '十一月',
        'Dec': '十二月',
    }
    month, year = value.split(' ')
    translated_month = chinese_months.get(month, '')
    return f'{translated_month} {year}'

@register.filter(name='jsonify')
def jsonify(data):
    if isinstance(data, dict):
        return data
    else:
        return json.loads(data)

url_target_blank = register.filter(url_target_blank, is_safe = True)

class GlobalVariable(object):
    def __init__(self, varname, varval):
        self.varname = varname
        self.varval = varval

    def name(self):
        return self.varname

    def value(self):
        return self.varval

    def set(self, newval):
        self.varval = newval

class GlobalVariableSetNode(template.Node):
    def __init__(self, varname, varval):
        self.varname = varname
        self.varval = varval

    def render(self, context):
        gv = context.get(self.varname, None)
        if gv:
            gv.set(self.varval)
        else:
            gv = context[self.varname] = GlobalVariable(
                self.varname, self.varval)
        return ''

def setglobal(parser, token):
    try:
        tag_name, varname, varval = token.contents.split(None, 2)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires 2 arguments" % token.contents.split()[0])
    return GlobalVariableSetNode(varname, varval)

register.tag('setglobal', setglobal)

class GlobalVariableGetNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        try:
            return context[self.varname].value()
        except AttributeError:
            return ''

def getglobal(parser, token):
    try:
        tag_name, varname = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments" % token.contents.split()[0])
    return GlobalVariableGetNode(varname)

register.tag('getglobal', getglobal)

class GlobalVariableIncrementNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        gv = context.get(self.varname, None)
        if gv is None:
            return ''
        gv.set(int(gv.value()) + 1)
        return ''

def incrementglobal(parser, token):
    try:
        tag_name, varname = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires arguments" % token.contents.split()[0])
    return GlobalVariableIncrementNode(varname)
register.tag('incrementglobal', incrementglobal)


@register.filter(name='splitstroke')
def splitstroke(key):
    arr = counter.split('|')
    return arr[key]
register.tag('splitstroke', incrementglobal)

@register.filter(name='klasubcount')
def klasubcount(post,year):
    return ''

register.tag('klasubcount', klasubcount)
