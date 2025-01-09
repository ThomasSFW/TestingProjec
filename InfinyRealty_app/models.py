from django.contrib.auth.models import AbstractUser
from django.db import models, connections, router

from django.db.models.signals import post_save
from django.dispatch import receiver

import random
import string


class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    objects = models.Manager()


# Overriding the Default Django Auth User and adding One More Field (user_type)
class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class MenuTabs(models.Model):
    tabid = models.AutoField(db_column='tabID', primary_key=True)  # Field name made lowercase.
    tabname = models.CharField(db_column='tabName', max_length=100)  # Field name made lowercase.
    url = models.CharField(max_length=200)
    sequence = models.SmallIntegerField()
    isenabled = models.SmallIntegerField(db_column='isEnabled')  # Field name made lowercase.
    iconclass = models.CharField(max_length=50)
    objects = models.Manager()

    class Meta:
        managed = True
        db_table = 'tblTab'


class MenuCategories(models.Model):
    catid = models.AutoField(db_column='catID', primary_key=True)  # Field name made lowercase.
    # tabid = models.IntegerField(db_column='tabID')  # Field name made lowercase.
    # tabname = models.ForeignKey(Tabs, db_column='tabID', on_delete=models.DO_NOTHING, default=1)
    tabid = models.ForeignKey(MenuTabs, db_column='tabID', on_delete=models.DO_NOTHING)
    catname = models.CharField(db_column='catName', max_length=100)  # Field name made lowercase.
    url = models.CharField(max_length=100)
    urltype = models.SmallIntegerField(db_column='urlType')  # Field name made lowercase.
    sequence = models.SmallIntegerField()
    isenabled = models.SmallIntegerField(db_column='isEnabled')  # Field name made lowercase.
    iconclass = models.CharField(max_length=50)
    objects = models.Manager()

    def __init__(self, name):
        self.name = name

    class Meta:
        managed = True
        db_table = 'tblCat'


class MenuSubCategories(models.Model):
    subcatid = models.AutoField(db_column='subCatID', primary_key=True)  # Field name made lowercase.
    catid = models.ForeignKey(MenuCategories, db_column='catID', on_delete=models.DO_NOTHING, default=1)
    subcatname = models.CharField(db_column='subCatName', max_length=100)  # Field name made lowercase.
    url = models.CharField(max_length=200)
    urltype = models.SmallIntegerField(db_column='urlType')  # Field name made lowercase.
    accesspost = models.CharField(db_column='accessPost', max_length=800)  # Field name made lowercase.
    sequence = models.SmallIntegerField()
    iscore = models.SmallIntegerField(db_column='isCore')  # Field name made lowercase.
    isready = models.SmallIntegerField(db_column='isReady')  # Field name made lowercase.
    isenabled = models.SmallIntegerField(db_column='isEnabled')  # Field name made lowercase.
    objects = models.Manager()

    class Meta:
        managed = True
        db_table = 'tblSubCat'


class Tabs(models.Model):
    IsEnableds = (
        {'正常': 1},
        {'無效': 0}
    )
    tabid = models.AutoField(db_column='tabID', primary_key=True)  # Field name made lowercase.
    tabname = models.CharField(db_column='tabName', max_length=100)  # Field name made lowercase.
    url = models.CharField(max_length=200)
    sequence = models.SmallIntegerField()
    isenabled = models.SmallIntegerField(db_column='isEnabled', default=1,
                                         choices=IsEnableds)  # Field name made lowercase.
    iconclass = models.CharField(max_length=50)
    objects = models.Manager()

    class Meta:
        managed = True
        db_table = 'tblTab'


class Categories(models.Model):
    IsEnableds = (
        {'正常': 1},
        {'無效': 0}
    )
    URLTypes = (
        {'新視窗': 2},
        {'外部': 1},
        {'內部': 0}
    )
    catid = models.AutoField(db_column='catID', primary_key=True)  # Field name made lowercase.
    # tabid = models.IntegerField(db_column='tabID')  # Field name made lowercase.
    tabid = models.ForeignKey(Tabs, db_column='tabID', on_delete=models.DO_NOTHING, default=1)
    catname = models.CharField(db_column='catName', max_length=100)  # Field name made lowercase.
    url = models.CharField(max_length=100)
    urltype = models.SmallIntegerField(db_column='urlType', default=1, choices=URLTypes)  # Field name made lowercase.
    sequence = models.SmallIntegerField()
    isenabled = models.SmallIntegerField(db_column='isEnabled', default=1,
                                         choices=IsEnableds)  # Field name made lowercase.
    iconclass = models.CharField(max_length=50)
    objects = models.Manager()

    class Meta:
        managed = True
        db_table = 'tblCat'


class SubCategories(models.Model):
    IsCores = (
        {'是': 1},
        {'否': 0}
    )
    IsReady = (
        {'是': 1},
        {'否': 0}
    )
    IsEnableds = (
        {'正常': 1},
        {'無效': 0}
    )
    URLTypes = (
        {'新視窗': 2},
        {'外部': 1},
        {'內部': 0}
    )
    subcatid = models.AutoField(db_column='subCatID', primary_key=True)  # Field name made lowercase.
    catid = models.ForeignKey(Categories, db_column='catID', on_delete=models.DO_NOTHING, default=1)
    subcatname = models.CharField(db_column='subCatName', max_length=100)  # Field name made lowercase.
    url = models.CharField(max_length=200)
    urlnew = models.CharField(max_length=200)
    urltype = models.SmallIntegerField(db_column='urlType', default=1, choices=URLTypes)  # Field name made lowercase.
    accesspost = models.CharField(db_column='accessPost', max_length=800)  # Field name made lowercase.
    sequence = models.SmallIntegerField()
    iscore = models.SmallIntegerField(db_column='isCore', default=1, choices=IsCores)  # Field name made lowercase.
    isready = models.SmallIntegerField(db_column='isReady', default=1, choices=IsReady)  # Field name made lowercase.
    isenabled = models.SmallIntegerField(db_column='isEnabled', default=1,
                                         choices=IsEnableds)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblSubCat'


class Printer(models.Model):
    statuss = (
        {'正常': 1},
        {'無效': 0}
    )
    printer_id = models.AutoField(primary_key=True)
    printer_name = models.CharField(max_length=255, blank=True, null=True)
    printer_description = models.CharField(max_length=255, blank=True, null=True)
    printer_model = models.CharField(max_length=255, blank=True, null=True)
    printer_client_id = models.CharField(max_length=255, blank=True, null=True)
    printer_serial_number = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    location_code = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    location_level = models.CharField(max_length=255, blank=True, null=True)
    location_remark = models.CharField(max_length=255, blank=True, null=True)
    status = models.SmallIntegerField(db_column='status', default=1, choices=statuss)

    class Meta:
        managed = False
        db_table = 'tblPrinter'


class AccessRights(models.Model):
    username = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    functionid = models.IntegerField(db_column='FunctionID')  # Field name made lowercase.
    team = models.CharField(db_column='Team', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    lastupdated = models.DateTimeField(db_column='LastUpdated')  # Field name made lowercase.
    expireddate = models.DateTimeField(db_column='ExpiredDate')  # Field name made lowercase.
    approved = models.IntegerField(db_column='Approved')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAccessRight'


class AccessLogs(models.Model):
    logid = models.AutoField(db_column='logID', primary_key=True)  # Field name made lowercase.
    logdatetime = models.DateTimeField(db_column='logDatetime')  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    username = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    pagename = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    logtype = models.CharField(db_column='logType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    propertyid = models.IntegerField(db_column='PropertyID', blank=True, null=True)  # Field name made lowercase.
    propertyno = models.CharField(db_column='PropertyNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    logdesc = models.CharField(db_column='logDesc', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblAccesslog'


class QAIPFunction(models.Model):
    functionid = models.AutoField(db_column='functionID', primary_key=True)  # Field name made lowercase.
    subcatid = models.IntegerField(db_column='subCatID', blank=True, null=True)  # Field name made lowercase.
    functionname = models.CharField(db_column='functionName', max_length=100, blank=True,
                                    null=True)  # Field name made lowercase.
    sequence = models.SmallIntegerField()
    isenabled = models.SmallIntegerField(db_column='isEnabled')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFunction'


class Users(models.Model):
    isactives = (
        {'Yes': 1},
        {'No': 0}
    )
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    username = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    password = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS')
    loginnamedesc = models.CharField(db_column='LoginNameDesc', max_length=50,
                                     db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                     null=True)  # Field name made lowercase.
    groupid = models.IntegerField(db_column='GroupID', blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='isActive', default=1, choices=isactives)  # Field name made lowercase.
    logincount = models.IntegerField(db_column='loginCount')  # Field name made lowercase.
    email = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    team = models.CharField(db_column='Team', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    rank = models.CharField(db_column='Rank', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='createDate', blank=True, null=True)  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='modifyDate', blank=True, null=True)  # Field name made lowercase.
    lastlogindate = models.DateTimeField(db_column='lastLoginDate', blank=True, null=True)  # Field name made lowercase.
    activedate = models.DateTimeField(db_column='activeDate', blank=True, null=True)  # Field name made lowercase.
    id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'tblLogin'


class Shops(models.Model):
    statuss = (
        {'Yes': 1},
        {'No': 0}
    )
    shop_id = models.AutoField(primary_key=True)
    shop_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    shop_name = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    shop_address = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    fax_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    fax_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    opening_hours = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    shop_photo = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    createdate = models.DateTimeField(db_column='createDate')  # Field name made lowercase.
    status = models.SmallIntegerField(db_column='status', default=1, choices=statuss)

    class Meta:
        managed = False
        db_table = 'tblShop'


class UserShops(models.Model):
    user_shop_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    shop = models.ForeignKey('Shops', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblUserShop'


class UserInfo(models.Model):
    postdesc = models.CharField(db_column='PostDesc', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUserInfo'


class Bookings(models.Model):
    booking_id = models.AutoField(primary_key=True)
    shop_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    username = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    booking_time = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    number_guests = models.SmallIntegerField()
    member_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    customer_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    gender = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    type = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    remarks = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    table_key = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    time = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS')
    booking_status = models.SmallIntegerField()
    deposit_status = models.SmallIntegerField()
    confirm_status = models.SmallIntegerField()
    show_status = models.SmallIntegerField()
    createdate = models.DateTimeField(db_column='createDate')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='modifyDate')  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblBooking'


class Foods(models.Model):
    food_id = models.AutoField(primary_key=True)
    food_name = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    food_name_e = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    food_description = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    food_photo = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    shop_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    food_group_id = models.IntegerField()
    food_category = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    food_sub_category = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)
    taste = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    print_location = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    period = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    show_menu = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    food_status = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    value_type = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    display_on_receipt = models.SmallIntegerField()
    internal = models.SmallIntegerField()
    east_b5_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    east_a5_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    coffee_b5_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    coffee_a5_charge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.SmallIntegerField()
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFood'


class DineIns(models.Model):
    dinein_id = models.AutoField(primary_key=True)
    table_id = models.IntegerField(blank=True, null=True)
    booking_id = models.IntegerField(blank=True, null=True)
    member_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    number_guests = models.SmallIntegerField()
    in_date = models.DateTimeField()
    out_date = models.DateTimeField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    shop_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    table_key = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    member_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    order_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDinein'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    member_id = models.IntegerField(blank=True, null=True)
    order_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    order_type = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    order_date = models.DateTimeField(blank=True, null=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2)
    tea_charge = models.DecimalField(max_digits=10, decimal_places=2)
    other_charge = models.DecimalField(max_digits=10, decimal_places=2)
    special_discount = models.DecimalField(max_digits=10, decimal_places=2)
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblOrder'


class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING, blank=True, null=True)
    food = models.ForeignKey('Foods', models.DO_NOTHING, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    order_item_date = models.DateTimeField(blank=True, null=True)
    order_item_type = models.SmallIntegerField()
    order_sequence = models.SmallIntegerField()
    status = models.SmallIntegerField(blank=True, null=True)
    order_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    food_name = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    food_name_e = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    food_description = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblOrderItem'


class OrderItemDetails(models.Model):
    order_item_detail_id = models.AutoField(primary_key=True)
    order_item_id = models.IntegerField(blank=True, null=True)
    item_id = models.IntegerField()
    code_key = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    code_detail_name = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)
    status = models.SmallIntegerField()
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblOrderItemDetail'


class OrderLogs(models.Model):
    order_log_id = models.AutoField(primary_key=True)
    order_item_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    food_id = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    order_item_date = models.DateTimeField(blank=True, null=True)
    order_item_type = models.SmallIntegerField()
    order_sequence = models.SmallIntegerField()
    status = models.SmallIntegerField(blank=True, null=True)
    order_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    food_name = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    food_name_e = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    food_description = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    order_log_date = models.DateTimeField(blank=True, null=True)
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblOrderLog'


class OrderNumbers(models.Model):
    order_number_id = models.AutoField(primary_key=True)
    order_number_date = models.DateField(blank=True, null=True)
    order_counter = models.IntegerField()
    order_number = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblOrderNumber'


class Invoices(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    shop_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    member_id = models.IntegerField()
    booking_id = models.IntegerField()
    order_id = models.IntegerField()
    invoice_number = models.CharField(max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    invoice_type = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tips_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    receivable_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transaction_reference = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    payment_method_2 = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)
    receivable_amount_2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transaction_reference_2 = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    invoice_date = models.DateTimeField()
    remarks = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    status = models.SmallIntegerField()
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblInvoice'


class InvoiceSnapshots(models.Model):
    snapshot_id = models.AutoField(primary_key=True)
    invoice_date = models.DateField(blank=True, null=True)
    daily_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_tips = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_receivable = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    visa_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    master_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cash_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    alipay_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wechatpay_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unionpay_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    banktransfer_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wallet_count = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shop_code = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    loginid = models.IntegerField(blank=True, null=True)
    snapshot_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblInvoiceSnapshot'


class Officers(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    post = models.CharField(max_length=10, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    event = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    venue = models.CharField(db_column='Venue', max_length=200, blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(max_length=200, blank=True, null=True)
    time = models.CharField(db_column='Time', max_length=20)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'officer'


class Times(models.Model):
    timeid = models.AutoField(primary_key=True)
    timedesc = models.CharField(db_column='timeDesc', max_length=100, blank=True,
                                null=True)  # Field name made lowercase.
    timelongdesc = models.CharField(db_column='timeLongDesc', max_length=100, blank=True,
                                    null=True)  # Field name made lowercase.
    timevar = models.CharField(db_column='timeVar', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.SmallIntegerField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tbltime'


class Teams(models.Model):
    teamdesc = models.CharField(db_column='TeamDesc', max_length=100, primary_key=True)  # Field name made lowercase.
    teamfulldesc = models.CharField(db_column='TeamFullDesc', max_length=100)  # Field name made lowercase.
    sequence = models.SmallIntegerField(db_column='Sequence')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblTeam'


class Ranks(models.Model):
    rank = models.CharField(primary_key=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    rankdesc = models.CharField(db_column='rankDesc', max_length=200,
                                db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    sequence = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblRank'


class Holiday(models.Model):
    holidaydate = models.DateTimeField(db_column='holidayDate', primary_key=True)  # Field name made lowercase.
    description = models.CharField(max_length=100)
    holidaytype = models.SmallIntegerField(db_column='holidayType')  # Field name made lowercase.
    period = models.CharField(max_length=2)

    class Meta:
        managed = True
        db_table = 'tblholiday'


class ESRschools(models.Model):
    schoolid = models.CharField(db_column='SchoolID', max_length=20)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=4)  # Field name made lowercase.
    previsitdate = models.DateTimeField(db_column='preVisitDate', blank=True, null=True)  # Field name made lowercase.
    esrstartdate = models.DateTimeField(db_column='esrStartDate', blank=True, null=True)  # Field name made lowercase.
    esrenddate = models.DateTimeField(db_column='esrEndDate', blank=True, null=True)  # Field name made lowercase.
    insptype = models.CharField(db_column='InspType', max_length=10)  # Field name made lowercase.
    isupdated = models.SmallIntegerField(db_column='IsUpdated')  # Field name made lowercase.
    totalinspday = models.DecimalField(db_column='totalInspDay', max_digits=18, decimal_places=1, blank=True,
                                       null=True)  # Field name made lowercase.
    lastupdate = models.DateTimeField(db_column='LastUpdate')  # Field name made lowercase.
    day1 = models.DateTimeField(blank=True, null=True)
    day2 = models.DateTimeField(blank=True, null=True)
    day3 = models.DateTimeField(blank=True, null=True)
    day4 = models.DateTimeField(blank=True, null=True)
    day5 = models.DateTimeField(blank=True, null=True)
    day6 = models.DateTimeField(blank=True, null=True)
    day7 = models.DateTimeField(blank=True, null=True)
    day8 = models.DateTimeField(blank=True, null=True)
    day9 = models.DateTimeField(blank=True, null=True)
    schoolid2 = models.CharField(db_column='schoolID2', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    schoolid3 = models.CharField(db_column='schoolID3', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    isdayconfirmed = models.SmallIntegerField(db_column='IsDayConfirmed')  # Field name made lowercase.
    dateattend = models.CharField(db_column='DateAttend', max_length=18)  # Field name made lowercase.
    preesrdate = models.DateTimeField(db_column='PreESRDate', blank=True, null=True)  # Field name made lowercase.
    preesrattend = models.CharField(db_column='PreESRAttend', max_length=2)  # Field name made lowercase.
    classstructure = models.CharField(db_column='ClassStructure', max_length=100)  # Field name made lowercase.
    preesrvisit = models.DateTimeField(db_column='PreESRVisit', blank=True, null=True)  # Field name made lowercase.
    preesrvisitattend = models.CharField(db_column='PreESRVisitAttend', max_length=2)  # Field name made lowercase.
    isvettingconfirmed = models.SmallIntegerField(db_column='IsVettingConfirmed')  # Field name made lowercase.
    iseformconfirmed = models.SmallIntegerField(db_column='IsEFormConfirmed')  # Field name made lowercase.
    isdraftconfirmed = models.SmallIntegerField(db_column='IsDraftConfirmed')  # Field name made lowercase.
    isfinalconfirmed = models.SmallIntegerField(db_column='IsFinalConfirmed')  # Field name made lowercase.
    ispostconfirmed = models.SmallIntegerField(db_column='IsPostConfirmed')  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblESRschools'


class InspectorAllocation(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=20)  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=4)  # Field name made lowercase.
    insptype = models.CharField(db_column='InspType', max_length=10)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    sheetno = models.SmallIntegerField(db_column='SheetNo')  # Field name made lowercase.
    namemember = models.CharField(db_column='NameMember', max_length=300)  # Field name made lowercase.
    post = models.CharField(db_column='Post', max_length=20)  # Field name made lowercase.
    memberid = models.IntegerField(db_column='MemberID')  # Field name made lowercase.
    esrschool = models.CharField(db_column='ESRSchool', max_length=500)  # Field name made lowercase.
    esrcode = models.CharField(db_column='ESRCode', max_length=20)  # Field name made lowercase.
    esrperiod = models.CharField(db_column='ESRPeriod', max_length=100)  # Field name made lowercase.
    d11 = models.SmallIntegerField(db_column='D11')  # Field name made lowercase.
    d12 = models.SmallIntegerField(db_column='D12')  # Field name made lowercase.
    d21 = models.SmallIntegerField(db_column='D21')  # Field name made lowercase.
    d22 = models.SmallIntegerField(db_column='D22')  # Field name made lowercase.
    d23 = models.SmallIntegerField(db_column='D23')  # Field name made lowercase.
    d31 = models.SmallIntegerField(db_column='D31')  # Field name made lowercase.
    d32 = models.SmallIntegerField(db_column='D32')  # Field name made lowercase.
    d41 = models.SmallIntegerField(db_column='D41')  # Field name made lowercase.
    d42 = models.SmallIntegerField(db_column='D42')  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created')  # Field name made lowercase.
    status = models.SmallIntegerField(db_column='Status')  # Field name made lowercase.
    id = models.IntegerField(db_column='ID', primary_key=True)

    class Meta:
        managed = False
        db_table = 'tblInspectorAllocation'
        unique_together = (('schoolid', 'esryear', 'insptype', 'loginid', 'memberid'),)


class Focus(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=12)  # Field name made lowercase.
    focusyear = models.CharField(db_column='focusYear', max_length=4)  # Field name made lowercase.
    focustypeid = models.ForeignKey('Focustype', models.DO_NOTHING,
                                    db_column='focusTypeID')  # Field name made lowercase.
    focuscode = models.CharField(db_column='focusCode', max_length=10)  # Field name made lowercase.
    focussubcode = models.CharField(db_column='focusSubCode', max_length=20, blank=True,
                                    null=True)  # Field name made lowercase.
    status = models.SmallIntegerField(blank=True, null=True)
    lastupdatedate = models.DateTimeField(db_column='lastUpdateDate', blank=True,
                                          null=True)  # Field name made lowercase.
    lastusedpost = models.CharField(db_column='lastUsedPost', max_length=1, blank=True,
                                    null=True)  # Field name made lowercase.
    schoolid2 = models.CharField(db_column='schoolID2', max_length=16, blank=True,
                                 null=True)  # Field name made lowercase.
    schoolid3 = models.CharField(db_column='schoolID3', max_length=16, blank=True,
                                 null=True)  # Field name made lowercase.
    developcyclebegin = models.CharField(db_column='developCycleBegin', max_length=9, blank=True,
                                         null=True)  # Field name made lowercase.
    developcycleend = models.CharField(db_column='developCycleEnd', max_length=9, blank=True,
                                       null=True)  # Field name made lowercase.
    teacherpercent = models.IntegerField(db_column='teacherPercent')  # Field name made lowercase.
    modify = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblFocus'
        unique_together = (('schoolid', 'focusyear', 'focustypeid', 'focuscode'),)


class Focusgroup(models.Model):
    subfocustypeid = models.CharField(db_column='subFocusTypeID', max_length=5)  # Field name made lowercase.
    tmpost = models.CharField(max_length=6)
    post = models.CharField(max_length=10)
    year = models.IntegerField()
    descriptor = models.SmallIntegerField(blank=True, null=True)
    schoollevel = models.CharField(db_column='schoolLevel', max_length=100, blank=True,
                                   null=True)  # Field name made lowercase.
    focusgroupid = models.AutoField(db_column='focusGroupID', primary_key=True)

    class Meta:
        managed = False
        db_table = 'tblfocusgroup'
        unique_together = (('subfocustypeid', 'tmpost', 'post', 'year'),)


class Focustype(models.Model):
    focustypeid = models.CharField(db_column='focusTypeID', primary_key=True,
                                   max_length=2)  # Field name made lowercase.
    focustypedesc = models.CharField(db_column='focusTypeDesc', max_length=50)  # Field name made lowercase.
    focustypefulldesc = models.CharField(db_column='focusTypeFullDesc', max_length=100, blank=True,
                                         null=True)  # Field name made lowercase.
    preinspsingle = models.CharField(db_column='preInspSingle', max_length=10)  # Field name made lowercase.
    actualinspsingle = models.CharField(db_column='actualInspSingle', max_length=10)  # Field name made lowercase.
    postinspsingle = models.CharField(db_column='postInspSingle', max_length=10)  # Field name made lowercase.
    totalinspsingle = models.CharField(db_column='totalInspSingle', max_length=10)  # Field name made lowercase.
    preinsppairc = models.CharField(db_column='preInspPairC', max_length=10)  # Field name made lowercase.
    actualinsppairc = models.CharField(db_column='actualInspPairC', max_length=10)  # Field name made lowercase.
    postinsppairc = models.CharField(db_column='postInspPairC', max_length=10)  # Field name made lowercase.
    totalinsppairc = models.CharField(db_column='totalInspPairC', max_length=10)  # Field name made lowercase.
    preinsppairm = models.CharField(db_column='preInspPairM', max_length=10)  # Field name made lowercase.
    actualinsppairm = models.CharField(db_column='actualInspPairM', max_length=10)  # Field name made lowercase.
    postinsppairm = models.CharField(db_column='postInspPairM', max_length=10)  # Field name made lowercase.
    totalinsppairm = models.CharField(db_column='totalInspPairM', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblFocusType'


class Focussubtypes(models.Model):
    subfocustypeid = models.CharField(db_column='subFocusTypeID', primary_key=True,
                                      max_length=5)  # Field name made lowercase.
    # focustypeid = models.ForeignKey(Focustype, models.DO_NOTHING, db_column='focusTypeID', default=1)  # Field name made lowercase.
    focustypeid = models.CharField(db_column='focusTypeID', default=1)  # Field name made lowercase.
    subtypedesc = models.CharField(db_column='subTypeDesc', max_length=100, blank=True,
                                   null=True)  # Field name made lowercase.
    newmappingcode = models.CharField(db_column='newMappingCode', max_length=20, blank=True,
                                      null=True)  # Field name made lowercase.
    newklacode = models.CharField(db_column='newKLACode', max_length=20, blank=True,
                                  null=True)  # Field name made lowercase.
    preinspsingle = models.CharField(db_column='preInspSingle', max_length=10)  # Field name made lowercase.
    actualinspsingle = models.CharField(db_column='actualInspSingle', max_length=10)  # Field name made lowercase.
    postinspsingle = models.CharField(db_column='postInspSingle', max_length=10)  # Field name made lowercase.
    totalinspsingle = models.CharField(db_column='totalInspSingle', max_length=10)  # Field name made lowercase.
    preinsppairc = models.CharField(db_column='preInspPairC', max_length=10)  # Field name made lowercase.
    actualinsppairc = models.CharField(db_column='actualInspPairC', max_length=10)  # Field name made lowercase.
    postinsppairc = models.CharField(db_column='postInspPairC', max_length=10)  # Field name made lowercase.
    totalinsppairc = models.CharField(db_column='totalInspPairC', max_length=10)  # Field name made lowercase.
    preinsppairm = models.CharField(db_column='preInspPairM', max_length=10)  # Field name made lowercase.
    actualinsppairm = models.CharField(db_column='actualInspPairM', max_length=10)  # Field name made lowercase.
    postinsppairm = models.CharField(db_column='postInspPairM', max_length=10)  # Field name made lowercase.
    totalinsppairm = models.CharField(db_column='totalInspPairM', max_length=10)  # Field name made lowercase.
    iscore = models.SmallIntegerField(db_column='isCore')  # Field name made lowercase.
    isdisplay = models.SmallIntegerField(db_column='isDisplay')  # Field name made lowercase.
    sequence = models.SmallIntegerField()

    class Meta:
        managed = True
        db_table = 'tblFocusSubType'
        unique_together = (('subfocustypeid', 'focustypeid'),)


class Schools(models.Model):
    IsActives = (
        {'True': 1},
        {'False': 0}
    )

    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=16)  # Field name made lowercase.
    schoolnamee = models.CharField(db_column='schoolNameE', max_length=255, blank=True,
                                   null=True)  # Field name made lowercase.
    schoolnamec = models.CharField(db_column='schoolNameC', max_length=255, blank=True,
                                   null=True)  # Field name made lowercase.
    dossiercode = models.CharField(db_column='dossierCode', max_length=16, blank=True,
                                   null=True)  # Field name made lowercase.
    ssbid = models.CharField(db_column='ssbID', max_length=3, blank=True, null=True)  # Field name made lowercase.
    schooltypeid = models.CharField(db_column='schoolTypeID', max_length=2, blank=True,
                                    null=True)  # Field name made lowercase.
    financetypeid = models.SmallIntegerField(db_column='financeTypeID', blank=True,
                                             null=True)  # Field name made lowercase.
    sessionid = models.CharField(db_column='sessionID', max_length=1, blank=True,
                                 null=True)  # Field name made lowercase.
    districtid = models.CharField(db_column='districtID', max_length=2, blank=True,
                                  null=True)  # Field name made lowercase.
    curriculumtypeid = models.SmallIntegerField(db_column='curriculumTypeID', blank=True,
                                                null=True)  # Field name made lowercase.
    phonenum = models.CharField(db_column='phoneNum', max_length=50, blank=True,
                                null=True)  # Field name made lowercase.
    faxnum = models.CharField(db_column='faxNum', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gendertypeid = models.CharField(db_column='genderTypeID', max_length=2, blank=True,
                                    null=True)  # Field name made lowercase.
    addresseng = models.TextField(db_column='addressEng', blank=True, null=True)  # Field name made lowercase.
    addresschi = models.TextField(db_column='addressChi', blank=True, null=True)  # Field name made lowercase.
    dateofoperation = models.DateTimeField(db_column='dateOfOperation', blank=True,
                                           null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True, default=1,
                                   choices=IsActives)  # Field name made lowercase.
    urlprofile = models.TextField(db_column='urlProfile', blank=True, null=True)  # Field name made lowercase.
    urlwebsite = models.TextField(db_column='urlWebsite', blank=True, null=True)  # Field name made lowercase.
    urlemail = models.TextField(db_column='urlEmail', blank=True, null=True)  # Field name made lowercase.
    languagetypeid = models.CharField(db_column='languageTypeID', max_length=2, blank=True,
                                      null=True)  # Field name made lowercase.
    principalnamee = models.CharField(db_column='principalNameE', max_length=255, blank=True,
                                      null=True)  # Field name made lowercase.
    principalnamec = models.CharField(db_column='principalNameC', max_length=255, blank=True,
                                      null=True)  # Field name made lowercase.
    supervisornamee = models.CharField(db_column='supervisorNameE', max_length=255, blank=True,
                                       null=True)  # Field name made lowercase.
    supervisornamec = models.CharField(db_column='supervisorNameC', max_length=255, blank=True,
                                       null=True)  # Field name made lowercase.
    religiontypeid = models.SmallIntegerField(db_column='religionTypeID', blank=True,
                                              null=True)  # Field name made lowercase.
    destinationid = models.CharField(db_column='destinationID', max_length=13, blank=True,
                                     null=True)  # Field name made lowercase.
    hasalumni = models.BooleanField(db_column='hasAlumni', blank=True, null=True)  # Field name made lowercase.
    haspta = models.BooleanField(db_column='hasPTA', blank=True, null=True)  # Field name made lowercase.
    hasprincipalappraisal = models.BooleanField(db_column='hasPrincipalAppraisal', blank=True,
                                                null=True)  # Field name made lowercase.
    hasstaffappraisal = models.BooleanField(db_column='hasStaffAppraisal', blank=True,
                                            null=True)  # Field name made lowercase.
    isinternational = models.BooleanField(db_column='isInternational', blank=True,
                                          null=True)  # Field name made lowercase.
    yearschmgminit = models.SmallIntegerField(db_column='yearSchMgmInit', blank=True,
                                              null=True)  # Field name made lowercase.
    yearincorpmgmcomm = models.SmallIntegerField(db_column='yearIncorpMgmComm', blank=True,
                                                 null=True)  # Field name made lowercase.
    nonprofittypeid = models.CharField(db_column='nonProfitTypeID', max_length=1, blank=True,
                                       null=True)  # Field name made lowercase.
    schoolyear = models.IntegerField(db_column='schoolYear', blank=True, null=True)  # Field name made lowercase.
    hkedcity_schoolid = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblSchool'


class Propertys(models.Model):
    propertyid = models.AutoField(db_column='PropertyID', primary_key=True)  # Field name made lowercase.
    propertyno = models.CharField(db_column='PropertyNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    propertyname = models.CharField(db_column='PropertyName', max_length=500,
                                    db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    propertyname_s = models.CharField(db_column='PropertyName_s', max_length=500,
                                      db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)  # Field name made lowercase.
    propertyname_e = models.CharField(db_column='PropertyName_e', max_length=500,
                                      db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)  # Field name made lowercase.
    usage = models.CharField(db_column='Usage', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    area = models.CharField(db_column='Area', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    district = models.CharField(db_column='District', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    subdistrict = models.CharField(db_column='SubDistrict', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    subdistrict_s = models.CharField(db_column='SubDistrict_s', max_length=100,
                                     db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                     null=True)  # Field name made lowercase.
    subdistrict_e = models.CharField(db_column='SubDistrict_e', max_length=100,
                                     db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                     null=True)  # Field name made lowercase.
    street = models.CharField(db_column='Street', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                              blank=True, null=True)  # Field name made lowercase.
    street_s = models.CharField(db_column='Street_s', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    street_e = models.CharField(db_column='Street_e', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    streetno = models.CharField(db_column='StreetNo', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    building = models.CharField(db_column='Building', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    building_s = models.CharField(db_column='Building_s', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    building_e = models.CharField(db_column='Building_e', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    floorzone = models.CharField(db_column='FloorZone', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    block = models.CharField(db_column='Block', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    floor = models.CharField(db_column='Floor', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='Unit', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    grossarea = models.CharField(db_column='GrossArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    netarea = models.CharField(db_column='NetArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    meterarea = models.CharField(db_column='MeterArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    atticarea = models.CharField(db_column='AtticArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    platformarea = models.CharField(db_column='PlatformArea', max_length=50,
                                    db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    rooftoparea = models.CharField(db_column='RooftopArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    gardenarea = models.CharField(db_column='GardenArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    offertype = models.CharField(db_column='OfferType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    sellingprice = models.DecimalField(db_column='SellingPrice', max_digits=13, decimal_places=2, blank=True,
                                       null=True)  # Field name made lowercase.
    unitprice = models.DecimalField(db_column='UnitPrice', max_digits=10, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    rent = models.DecimalField(db_column='Rent', max_digits=10, decimal_places=2, blank=True,
                               null=True)  # Field name made lowercase.
    unitrent = models.DecimalField(db_column='UnitRent', max_digits=10, decimal_places=2, blank=True,
                                   null=True)  # Field name made lowercase.
    managementfee = models.DecimalField(db_column='ManagementFee', max_digits=10, decimal_places=2, blank=True,
                                        null=True)  # Field name made lowercase.
    unitmanagementfee = models.DecimalField(db_column='UnitManagementFee', max_digits=10, decimal_places=2, blank=True,
                                            null=True)  # Field name made lowercase.
    rates = models.DecimalField(db_column='Rates', max_digits=10, decimal_places=2, blank=True,
                                null=True)  # Field name made lowercase.
    unitrates = models.DecimalField(db_column='UnitRates', max_digits=10, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    possession = models.CharField(db_column='Possession', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    yield_field = models.DecimalField(db_column='Yield', max_digits=10, decimal_places=2, blank=True,
                                      null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    tenant = models.CharField(db_column='Tenant', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                              blank=True, null=True)  # Field name made lowercase.
    currentrent = models.DecimalField(db_column='CurrentRent', max_digits=10, decimal_places=2, blank=True,
                                      null=True)  # Field name made lowercase.
    rentalperiod = models.CharField(db_column='RentalPeriod', max_length=100,
                                    db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    rentalstartdate = models.CharField(db_column='RentalStartDate', max_length=100,
                                       db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)  # Field name made lowercase.
    formerowner = models.CharField(db_column='FormerOwner', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    finalprice = models.DecimalField(db_column='FinalPrice', max_digits=10, decimal_places=2, blank=True,
                                     null=True)  # Field name made lowercase.
    transactiondate = models.CharField(db_column='TransactionDate', max_length=100,
                                       db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)  # Field name made lowercase.
    availability = models.TextField(db_column='Availability', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    decoration = models.TextField(db_column='Decoration', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    views = models.TextField(db_column='Views', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                               null=True)  # Field name made lowercase.
    listingdate = models.DateTimeField(db_column='ListingDate')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='ModifyDate')  # Field name made lowercase.
    approved = models.SmallIntegerField()
    followup_user = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    agentid = models.IntegerField(db_column='AgentID')  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    viewcounter = models.IntegerField(db_column='ViewCounter')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblProperty'


class PropertyArea(models.Model):
    propertyareaid = models.AutoField(db_column='PropertyAreaID', primary_key=True)  # Field name made lowercase.
    propertyid = models.IntegerField(db_column='PropertyID')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    grossarea = models.CharField(db_column='GrossArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    netarea = models.CharField(db_column='NetArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    listingdate = models.DateTimeField(db_column='ListingDate')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='ModifyDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropertyArea'


class PropertyFiles(models.Model):
    fileid = models.AutoField(db_column='FileID', primary_key=True)  # Field name made lowercase.
    propertyid = models.IntegerField(db_column='PropertyID', blank=True, null=True)  # Field name made lowercase.
    filetype = models.CharField(db_column='FileType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    filename = models.CharField(db_column='FileName', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    filetitle = models.CharField(db_column='FileTitle', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    filedescription = models.CharField(db_column='FileDescription', max_length=500,
                                       db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)  # Field name made lowercase.
    filetitle_s = models.CharField(db_column='FileTitle_s', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    filedescription_s = models.CharField(db_column='FileDescription_s', max_length=500,
                                         db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)  # Field name made lowercase.
    filetitle_e = models.CharField(db_column='FileTitle_e', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    filedescription_e = models.CharField(db_column='FileDescription_e', max_length=500,
                                         db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)  # Field name made lowercase.
    sequence = models.IntegerField(db_column='Sequence')  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='ModifyDate')  # Field name made lowercase.
    iswatermark = models.SmallIntegerField(db_column='IsWatermark')  # Field name made lowercase.
    isapprove = models.SmallIntegerField(db_column='IsApprove')  # Field name made lowercase.
    ismain = models.SmallIntegerField(db_column='IsMain')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropertyFile'


class PropertyContacts(models.Model):
    contactid = models.AutoField(db_column='ContactID', primary_key=True)  # Field name made lowercase.
    propertyid = models.IntegerField(db_column='PropertyID', blank=True, null=True)  # Field name made lowercase.
    contacttype = models.CharField(db_column='ContactType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    company = models.TextField(db_column='Company', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                               null=True)  # Field name made lowercase.
    title = models.TextField(db_column='Title', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    person = models.TextField(db_column='Person', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                              null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                               null=True)  # Field name made lowercase.
    ctcperson = models.TextField(db_column='CTCPerson', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                 null=True)  # Field name made lowercase.
    infotype = models.CharField(db_column='InfoType', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    contactinfo = models.TextField(db_column='ContactInfo', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                   null=True)  # Field name made lowercase.
    email = models.TextField(db_column='Email', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                               null=True)  # Field name made lowercase.
    status = models.SmallIntegerField()
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropertyContact'


class PropertyFollows(models.Model):
    followid = models.AutoField(db_column='FollowID', primary_key=True)  # Field name made lowercase.
    propertyid = models.IntegerField(db_column='PropertyID', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                              blank=True, null=True)  # Field name made lowercase.
    sellingprice = models.DecimalField(db_column='SellingPrice', max_digits=13, decimal_places=2, blank=True,
                                       null=True)  # Field name made lowercase.
    unitprice = models.DecimalField(db_column='UnitPrice', max_digits=13, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    rent = models.DecimalField(db_column='Rent', max_digits=13, decimal_places=2, blank=True,
                               null=True)  # Field name made lowercase.
    unitrent = models.DecimalField(db_column='UnitRent', max_digits=13, decimal_places=2, blank=True,
                                   null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                   null=True)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    followdate = models.DateTimeField(db_column='FollowDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropertyFollow'


class PropertyHighlights(models.Model):
    highlightid = models.AutoField(db_column='HighlightID', primary_key=True)  # Field name made lowercase.
    highlighttype = models.CharField(db_column='HighlightType', max_length=50,
                                     db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                     null=True)  # Field name made lowercase.
    propertyid = models.IntegerField(db_column='PropertyID', blank=True, null=True)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.
    isapprove = models.SmallIntegerField(db_column='IsApprove')  # Field name made lowercase.
    ismain = models.SmallIntegerField(db_column='IsMain')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropertyHighlight'


class PropertyUsages(models.Model):
    usage_id = models.AutoField(primary_key=True)
    usage_code = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')
    usage_name = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage_name_e = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage_counter = models.IntegerField(blank=True, null=True)
    usage_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage_photo = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage_icon = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    sequence = models.SmallIntegerField()
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblPropertyUsage'


class PropertyListings(models.Model):
    listing_id = models.AutoField(primary_key=True)
    development_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)
    development_name_s = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    development_name_e = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    address = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    address_s = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    address_e = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    developer = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    developer_s = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    developer_e = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    development_type = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)
    development_type_s = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    development_type_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    min_selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    first_sale_date = models.DateField(blank=True, null=True)
    estimated_completion_date = models.DateField(blank=True, null=True)
    phase = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phase_s = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phase_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    area = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    area_s = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    area_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    district = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    district_s = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    district_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    num_units = models.IntegerField(blank=True, null=True)
    management_company = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    management_company_s = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                            null=True)
    management_company_e = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                            null=True)
    vendor_holding_company = models.CharField(max_length=800, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                              null=True)
    vendor_holding_company_s = models.CharField(max_length=800, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                                null=True)
    vendor_holding_company_e = models.CharField(max_length=800, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                                null=True)
    school_net = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    school_net_s = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    school_net_e = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    project_details = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    project_details_s = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    project_details_e = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    property_number = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)
    advertisement_date = models.DateField(blank=True, null=True)
    viewcounter = models.IntegerField()
    create_date = models.DateTimeField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPropertyListing'


class PropertyForeigns(models.Model):
    propertyforeignid = models.AutoField(db_column='PropertyForeignID', primary_key=True)  # Field name made lowercase.
    propertyno = models.CharField(db_column='PropertyNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    propertyname = models.CharField(db_column='PropertyName', max_length=500,
                                    db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    propertyname_s = models.CharField(db_column='PropertyName_s', max_length=500,
                                      db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)  # Field name made lowercase.
    propertyname_e = models.CharField(db_column='PropertyName_e', max_length=500,
                                      db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)  # Field name made lowercase.
    usage = models.CharField(db_column='Usage', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    usage_s = models.CharField(db_column='Usage_s', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    usage_e = models.CharField(db_column='Usage_e', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    projectname = models.CharField(db_column='ProjectName', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    projectname_s = models.CharField(db_column='ProjectName_s', max_length=500,
                                     db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                     null=True)  # Field name made lowercase.
    projectname_e = models.CharField(db_column='ProjectName_e', max_length=500,
                                     db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                     null=True)  # Field name made lowercase.
    projectdescription = models.TextField(db_column='ProjectDescription', db_collation='SQL_Latin1_General_CP1_CI_AS',
                                          blank=True, null=True)  # Field name made lowercase.
    projectdescription_s = models.TextField(db_column='ProjectDescription_s',
                                            db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                            null=True)  # Field name made lowercase.
    projectdescription_e = models.TextField(db_column='ProjectDescription_e',
                                            db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                            null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    country_s = models.CharField(db_column='Country_s', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    country_e = models.CharField(db_column='Country_e', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    developer = models.CharField(db_column='Developer', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    developer_s = models.CharField(db_column='Developer_s', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    developer_e = models.CharField(db_column='Developer_e', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    completiondate = models.CharField(db_column='CompletionDate', max_length=100,
                                      db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)  # Field name made lowercase.
    unittypes = models.CharField(db_column='UnitTypes', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    unittypes_s = models.CharField(db_column='UnitTypes_s', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    unittypes_e = models.CharField(db_column='UnitTypes_e', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    unitsizes = models.CharField(db_column='UnitSize', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    unitsizes_s = models.CharField(db_column='UnitSize_s', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    unitsizes_e = models.CharField(db_column='UnitSize_e', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    residentialunits = models.CharField(db_column='ResidentialUnits', max_length=100,
                                        db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)  # Field name made lowercase.
    residentialunits_s = models.CharField(db_column='ResidentialUnits_s', max_length=100,
                                          db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)  # Field name made lowercase.
    residentialunits_e = models.CharField(db_column='ResidentialUnits_e', max_length=100,
                                          db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)  # Field name made lowercase.
    propertyfeatures = models.TextField(db_column='PropertyFeatures', db_collation='SQL_Latin1_General_CP1_CI_AS',
                                        blank=True, null=True)  # Field name made lowercase.
    propertyfeatures_s = models.TextField(db_column='PropertyFeatures_s', db_collation='SQL_Latin1_General_CP1_CI_AS',
                                          blank=True, null=True)  # Field name made lowercase.
    propertyfeatures_e = models.TextField(db_column='PropertyFeatures_e', db_collation='SQL_Latin1_General_CP1_CI_AS',
                                          blank=True, null=True)  # Field name made lowercase.
    propertycontents = models.TextField(db_column='PropertyContents', db_collation='SQL_Latin1_General_CP1_CI_AS',
                                        blank=True, null=True)  # Field name made lowercase.
    propertycontents_s = models.TextField(db_column='PropertyContents_s', db_collation='SQL_Latin1_General_CP1_CI_AS',
                                          blank=True, null=True)  # Field name made lowercase.
    propertycontents_e = models.TextField(db_column='PropertyContents_e', db_collation='SQL_Latin1_General_CP1_CI_AS',
                                          blank=True, null=True)  # Field name made lowercase.
    district = models.CharField(db_column='District', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    district_s = models.CharField(db_column='District_s', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    district_e = models.CharField(db_column='District_e', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    subdistrict = models.CharField(db_column='SubDistrict', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    street = models.CharField(db_column='Street', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                              blank=True, null=True)  # Field name made lowercase.
    streetno = models.CharField(db_column='StreetNo', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    building = models.CharField(db_column='Building', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    floorzone = models.CharField(db_column='FloorZone', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    block = models.CharField(db_column='Block', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    floor = models.CharField(db_column='Floor', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='Unit', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    grossarea = models.CharField(db_column='GrossArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    netarea = models.CharField(db_column='NetArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                               blank=True, null=True)  # Field name made lowercase.
    meterarea = models.CharField(db_column='MeterArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    atticarea = models.CharField(db_column='AtticArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    platformarea = models.CharField(db_column='PlatformArea', max_length=50,
                                    db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    rooftoparea = models.CharField(db_column='RooftopArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    gardenarea = models.CharField(db_column='GardenArea', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    offertype = models.CharField(db_column='OfferType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    sellingprice = models.DecimalField(db_column='SellingPrice', max_digits=13, decimal_places=2, blank=True,
                                       null=True)  # Field name made lowercase.
    unitprice = models.DecimalField(db_column='UnitPrice', max_digits=10, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    rent = models.DecimalField(db_column='Rent', max_digits=10, decimal_places=2, blank=True,
                               null=True)  # Field name made lowercase.
    unitrent = models.DecimalField(db_column='UnitRent', max_digits=10, decimal_places=2, blank=True,
                                   null=True)  # Field name made lowercase.
    managementfee = models.DecimalField(db_column='ManagementFee', max_digits=10, decimal_places=2, blank=True,
                                        null=True)  # Field name made lowercase.
    unitmanagementfee = models.DecimalField(db_column='UnitManagementFee', max_digits=10, decimal_places=2, blank=True,
                                            null=True)  # Field name made lowercase.
    rates = models.DecimalField(db_column='Rates', max_digits=10, decimal_places=2, blank=True,
                                null=True)  # Field name made lowercase.
    unitrates = models.DecimalField(db_column='UnitRates', max_digits=10, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    possession = models.CharField(db_column='Possession', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                  blank=True, null=True)  # Field name made lowercase.
    yield_field = models.DecimalField(db_column='Yield', max_digits=10, decimal_places=2, blank=True,
                                      null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    tenant = models.CharField(db_column='Tenant', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                              blank=True, null=True)  # Field name made lowercase.
    currentrent = models.DecimalField(db_column='CurrentRent', max_digits=10, decimal_places=2, blank=True,
                                      null=True)  # Field name made lowercase.
    rentalperiod = models.CharField(db_column='RentalPeriod', max_length=100,
                                    db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    rentalstartdate = models.CharField(db_column='RentalStartDate', max_length=100,
                                       db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)  # Field name made lowercase.
    formerowner = models.CharField(db_column='FormerOwner', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    finalprice = models.DecimalField(db_column='FinalPrice', max_digits=10, decimal_places=2, blank=True,
                                     null=True)  # Field name made lowercase.
    transactiondate = models.CharField(db_column='TransactionDate', max_length=100,
                                       db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)  # Field name made lowercase.
    availability = models.TextField(db_column='Availability', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    views = models.TextField(db_column='Views', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                               null=True)  # Field name made lowercase.
    listingdate = models.DateTimeField(db_column='ListingDate')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='ModifyDate')  # Field name made lowercase.
    approved = models.SmallIntegerField()
    agentid = models.IntegerField(db_column='AgentID')  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    viewcounter = models.IntegerField(db_column='ViewCounter')  # Field name made lowercase.
    currency = models.CharField(db_column='Currency', max_length=10,
                                db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropertyForeign'


class PropertyForeignFiles(models.Model):
    fileid = models.AutoField(db_column='FileID', primary_key=True)  # Field name made lowercase.
    propertyforeignid = models.IntegerField(db_column='PropertyForeignID', blank=True,
                                            null=True)  # Field name made lowercase.
    filetype = models.CharField(db_column='FileType', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    filename = models.CharField(db_column='FileName', max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    filetitle = models.CharField(db_column='FileTitle', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    filedescription = models.CharField(db_column='FileDescription', max_length=500,
                                       db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)  # Field name made lowercase.
    filetitle_s = models.CharField(db_column='FileTitle_s', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    filedescription_s = models.CharField(db_column='FileDescription_s', max_length=500,
                                         db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)  # Field name made lowercase.
    filetitle_e = models.CharField(db_column='FileTitle_e', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                   blank=True, null=True)  # Field name made lowercase.
    filedescription_e = models.CharField(db_column='FileDescription_e', max_length=500,
                                         db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)  # Field name made lowercase.
    sequence = models.IntegerField(db_column='Sequence')  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='ModifyDate')  # Field name made lowercase.
    iswatermark = models.SmallIntegerField(db_column='IsWatermark')  # Field name made lowercase.
    isapprove = models.SmallIntegerField(db_column='IsApprove')  # Field name made lowercase.
    ismain = models.SmallIntegerField(db_column='IsMain')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropertyForeignFile'


class Contents(models.Model):
    content_id = models.AutoField(primary_key=True)
    content_type = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    content_name = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    content_name_s = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)
    content_name_e = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)
    sequence = models.SmallIntegerField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblContent'


class ContentDetails(models.Model):
    content_detail_id = models.AutoField(primary_key=True)
    content_id = models.IntegerField(blank=True, null=True)
    content_detail_title = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    content_detail_title_s = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    content_detail_title_e = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    content_detail_name = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    content_detail_name_s = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    content_detail_name_e = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)
    sequence = models.SmallIntegerField()
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblContentDetail'


class Members(models.Model):
    member_id = models.AutoField(primary_key=True)
    member_number = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    member_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    username = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    password = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    gender = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    join_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    lastlogin_date = models.DateTimeField()
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblMember'


class MemberPropertys(models.Model):
    memberpropertyid = models.AutoField(db_column='MemberPropertyID', primary_key=True)  # Field name made lowercase.
    member_id = models.IntegerField(blank=True, null=True)
    propertyid = models.IntegerField(db_column='PropertyID')  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='createDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMemberProperty'


class Customers(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    industry = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    area_from = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    area_to = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    offer_type = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    sellingprice_from = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    sellingprice_to = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    rent_from = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    rent_to = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    login_id = models.IntegerField()
    followup_user = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblCustomer'


class Entrusts(models.Model):
    entrust_id = models.AutoField(primary_key=True)
    contact_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    contact_period = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)
    contact_period_other = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                            null=True)
    property_address_1 = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    offer_type_1 = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage_1 = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    netarea_1 = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    rent_1 = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    selling_1 = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    property_address_2 = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    offer_type_2 = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage_2 = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    netarea_2 = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    rent_2 = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    selling_2 = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    property_address_3 = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    offer_type_3 = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    usage_3 = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    netarea_3 = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    rent_3 = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    selling_3 = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    followup_user = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    followup_info = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    followup_user = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblEntrust'


class Enquirys(models.Model):
    contact_id = models.AutoField(primary_key=True)
    property_id = models.IntegerField(blank=True, null=True)
    property_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    contact_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    message = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    newsletter = models.SmallIntegerField(blank=True, null=True)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    followup_user = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblenquiry'


class VisitTour(models.Model):
    visit_tour_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    last_name = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    date_of_visit = models.DateField()
    time_of_visit = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    total_guest = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblVisitTour'


class VisitTourForm(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    title_en = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    title_sc = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    desc = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    desc_en = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    desc_sc = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    date_min = models.DateField()
    date_max = models.DateField()
    time = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tblVisitTourForm'


class Interests(models.Model):
    interest_id = models.AutoField(primary_key=True)
    bank_name = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    bank_name_s = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    bank_name_e = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    p_rate = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    p_score = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblInterest'


class TransactionRecords(models.Model):
    transactionid = models.AutoField(db_column='TransactionID', primary_key=True)  # Field name made lowercase.
    lang = models.CharField(db_column='Lang', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    transactiondate = models.DateTimeField(db_column='TransactionDate', blank=True,
                                           null=True)  # Field name made lowercase.
    district = models.CharField(db_column='District', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                blank=True, null=True)  # Field name made lowercase.
    propertyname = models.CharField(db_column='PropertyName', max_length=150,
                                    db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                    null=True)  # Field name made lowercase.
    floor = models.CharField(db_column='Floor', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='Unit', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                            null=True)  # Field name made lowercase.
    approximatearea = models.CharField(db_column='ApproximateArea', max_length=50,
                                       db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                       null=True)  # Field name made lowercase.
    transactionstatus = models.CharField(db_column='TransactionStatus', max_length=50,
                                         db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)  # Field name made lowercase.
    transactionprice = models.CharField(db_column='TransactionPrice', max_length=50,
                                        db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)  # Field name made lowercase.
    unitprice = models.CharField(db_column='UnitPrice', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                                 blank=True, null=True)  # Field name made lowercase.
    source = models.CharField(db_column='Source', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS',
                              blank=True, null=True)  # Field name made lowercase.
    usage = models.CharField(db_column='Usage', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblTransactionRecord'


class MortgageRefers(models.Model):
    mortgage_refer_id = models.AutoField(primary_key=True)
    english_name = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    title = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    id_type = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    id_number = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    english_name_2 = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                      null=True)
    title_2 = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email_2 = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone_area_code_2 = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)
    phone_number_2 = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    id_type_2 = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    id_number_2 = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    unit = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    floor = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    block = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    building = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    street = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    area = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    district = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    loan_purpose = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    purchase_price = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    drawdown_date = models.DateTimeField()
    referral = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    referral_name = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    referral_phone_number = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                             null=True)
    signature_pad = models.TextField(db_column='signature-pad', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                     null=True)  # Field renamed to remove unsuitable characters.
    remarks = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField()
    followup_user = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblMortgageRefer'


class ESRschoolsER(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=16)  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=4)  # Field name made lowercase.
    erid = models.CharField(db_column='ERId', max_length=10)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=10, blank=True, null=True)  # Field name made lowercase.
    ernamee = models.TextField(db_column='ERNameE', blank=True, null=True)  # Field name made lowercase.
    ernamec = models.TextField(db_column='ERNameC', blank=True, null=True)  # Field name made lowercase.
    postofer = models.TextField(db_column='PostofER', blank=True, null=True)  # Field name made lowercase.
    financedesc = models.TextField(db_column='FinanceDesc', blank=True, null=True)  # Field name made lowercase.
    erschoolc = models.TextField(db_column='ERSchoolC', blank=True, null=True)  # Field name made lowercase.
    erschoole = models.TextField(db_column='ERSchoolE', blank=True, null=True)  # Field name made lowercase.
    schooladdressc = models.TextField(db_column='SchoolAddressC', blank=True, null=True)  # Field name made lowercase.
    schooladdresse = models.TextField(db_column='SchoolAddressE', blank=True, null=True)  # Field name made lowercase.
    schooltel = models.CharField(db_column='SchoolTel', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    experience = models.CharField(db_column='Experience', max_length=1, blank=True,
                                  null=True)  # Field name made lowercase.
    erremark = models.TextField(db_column='ERRemark', blank=True, null=True)  # Field name made lowercase.
    periodofesrtext = models.TextField(db_column='PeriodOfEsrTEXT', blank=True, null=True)  # Field name made lowercase.
    erschoolcode = models.CharField(db_column='ERSchoolCode', max_length=6, blank=True,
                                    null=True)  # Field name made lowercase.
    proposedtl = models.TextField(db_column='ProposedTL', blank=True, null=True)  # Field name made lowercase.
    tlpost = models.CharField(db_column='TLPost', max_length=10, blank=True, null=True)  # Field name made lowercase.
    schoolidref = models.TextField(db_column='SchoolIDRef', blank=True, null=True)  # Field name made lowercase.
    dist = models.TextField(db_column='Dist', blank=True, null=True)  # Field name made lowercase.
    schlv = models.CharField(db_column='SchLv', max_length=5, blank=True, null=True)  # Field name made lowercase.
    schoolnameeng = models.TextField(db_column='SchoolNameEng', blank=True, null=True)  # Field name made lowercase.
    sess = models.CharField(db_column='Sess', max_length=5, blank=True, null=True)  # Field name made lowercase.
    schoolnamechi = models.TextField(db_column='SchoolNameChi', blank=True, null=True)  # Field name made lowercase.
    moi = models.CharField(db_column='MOI', max_length=5, blank=True, null=True)  # Field name made lowercase.
    batch = models.CharField(db_column='Batch', max_length=5, blank=True, null=True)  # Field name made lowercase.
    tlfinancedesc = models.TextField(db_column='TLFinanceDesc', blank=True, null=True)  # Field name made lowercase.
    schsex = models.CharField(db_column='SchSex', max_length=10, blank=True, null=True)  # Field name made lowercase.
    schheadnameeng = models.TextField(db_column='SchHeadNameEng', blank=True, null=True)  # Field name made lowercase.
    schheadnamechi = models.TextField(db_column='SchHeadNameChi', blank=True, null=True)  # Field name made lowercase.
    tel = models.CharField(db_column='Tel', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(db_column='Fax', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tlschooladdresseng = models.TextField(db_column='TLSchoolAddressEng', blank=True,
                                          null=True)  # Field name made lowercase.
    tlschooladdresschi = models.TextField(db_column='TLSchoolAddressChi', blank=True,
                                          null=True)  # Field name made lowercase.
    week = models.CharField(db_column='Week', max_length=5, blank=True, null=True)  # Field name made lowercase.
    nameengfull = models.TextField(db_column='NameEngFull', blank=True, null=True)  # Field name made lowercase.
    treasuryschcode = models.CharField(db_column='TreasurySchCode', max_length=10, blank=True,
                                       null=True)  # Field name made lowercase.
    regname = models.TextField(db_column='RegName', blank=True, null=True)  # Field name made lowercase.
    ssdochi = models.TextField(db_column='SSDOChi', blank=True, null=True)  # Field name made lowercase.
    ssdoeng = models.TextField(db_column='SSDOEng', blank=True, null=True)  # Field name made lowercase.
    post = models.CharField(db_column='Post', max_length=20, blank=True, null=True)  # Field name made lowercase.
    contactno = models.CharField(db_column='ContactNo', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    approvedclassstructure = models.TextField(db_column='ApprovedClassStructure', blank=True,
                                              null=True)  # Field name made lowercase.
    totalapprovedclass = models.CharField(db_column='TotalApprovedClass', max_length=10, blank=True,
                                          null=True)  # Field name made lowercase.
    schoolsponsornameeng = models.TextField(db_column='SchoolSponsorNameEng', blank=True,
                                            null=True)  # Field name made lowercase.
    schoolsponsornamechi = models.TextField(db_column='SchoolSponsorNameChi', blank=True,
                                            null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblESRSchoolsER'
        unique_together = (('schoolid', 'esryear', 'erid'),)


class Schooltypes(models.Model):
    schooltypeid = models.CharField(db_column='schoolTypeID', primary_key=True,
                                    max_length=2)  # Field name made lowercase.
    schooltypedesc = models.CharField(db_column='schoolTypeDesc', max_length=50, blank=True,
                                      null=True)  # Field name made lowercase.
    schooltypemainflag = models.BooleanField(db_column='schoolTypeMainFlag', blank=True,
                                             null=True)  # Field name made lowercase.
    sequence = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblSchoolType'


class Sessions(models.Model):
    sessionid = models.CharField(db_column='sessionID', primary_key=True, max_length=1)  # Field name made lowercase.
    sessiondesc = models.CharField(db_column='sessionDesc', max_length=50, blank=True,
                                   null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSession'


class Districts(models.Model):
    districtid = models.CharField(db_column='districtID', primary_key=True, max_length=2)  # Field name made lowercase.
    districtname = models.CharField(db_column='districtName', max_length=55, blank=True,
                                    null=True)  # Field name made lowercase.
    districtnamec = models.CharField(db_column='districtNameC', max_length=55, blank=True,
                                     null=True)  # Field name made lowercase.
    districtcode = models.CharField(db_column='districtCode', max_length=2, blank=True,
                                    null=True)  # Field name made lowercase.
    ordering = models.IntegerField(blank=True, null=True)
    districtnamerpt = models.CharField(db_column='districtNameRpt', max_length=55, blank=True,
                                       null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDistrict'


class Financetypes(models.Model):
    financetypeid = models.SmallIntegerField(db_column='financeTypeID', primary_key=True)  # Field name made lowercase.
    financetypedesc = models.CharField(db_column='financeTypeDesc', max_length=32, blank=True,
                                       null=True)  # Field name made lowercase.
    financetypemainflag = models.BooleanField(db_column='financeTypeMainFlag', blank=True,
                                              null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFinanceType'


class SSBs(models.Model):
    ssbid = models.CharField(db_column='ssbID', primary_key=True, max_length=3)  # Field name made lowercase.
    ssbdesc = models.CharField(db_column='ssbDesc', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ssbdesc_chi = models.CharField(db_column='ssbDesc_chi', max_length=255, blank=True,
                                   null=True)  # Field name made lowercase.
    ssbfax = models.CharField(db_column='ssbFax', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ssbphone = models.CharField(db_column='ssbPhone', max_length=50, blank=True,
                                null=True)  # Field name made lowercase.
    ssbcontacte = models.CharField(db_column='ssbContactE', max_length=100, blank=True,
                                   null=True)  # Field name made lowercase.
    ssbcontactc = models.CharField(db_column='ssbContactC', max_length=50, blank=True,
                                   null=True)  # Field name made lowercase.
    religiontypeid = models.SmallIntegerField(db_column='religionTypeID', blank=True,
                                              null=True)  # Field name made lowercase.
    ssbaddresse = models.CharField(db_column='ssbAddressE', max_length=255, blank=True,
                                   null=True)  # Field name made lowercase.
    ssbaddressc = models.CharField(db_column='ssbAddressC', max_length=100, blank=True,
                                   null=True)  # Field name made lowercase.
    nonprofittypeid = models.ForeignKey('NonProfitType', models.DO_NOTHING,
                                        db_column='nonProfitTypeID')  # Field name made lowercase.
    ssbdesc_abbr = models.CharField(db_column='ssbDesc_abbr', max_length=255, blank=True,
                                    null=True)  # Field name made lowercase.
    ssbmain_flag = models.CharField(db_column='ssbMain_flag', max_length=1, blank=True,
                                    null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSSB'


class NonProfitType(models.Model):
    nonprofittypeid = models.CharField(db_column='nonProfitTypeID', primary_key=True,
                                       max_length=3)  # Field name made lowercase.
    nonprofittypedesc = models.CharField(db_column='nonProfitTypeDesc', max_length=50, blank=True,
                                         null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblNonProfitType'


class Curriculumtypes(models.Model):
    curriculumtypeid = models.SmallIntegerField(db_column='curriculumTypeID',
                                                primary_key=True)  # Field name made lowercase.
    curriculumtypedesc = models.CharField(db_column='curriculumTypeDesc', max_length=50, blank=True,
                                          null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCurriculumType'


class SchoolRelatedInfo(models.Model):
    schoolid = models.CharField(primary_key=True, max_length=12)
    infotype = models.CharField(db_column='InfoType', max_length=10)  # Field name made lowercase.
    isvalid = models.SmallIntegerField(db_column='IsValid')  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=500)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolRelatedInfo'
        unique_together = (('schoolid', 'infotype'),)


class Schoolrelatedprogramme(models.Model):
    schoolid = models.CharField(primary_key=True, max_length=12)
    year = models.IntegerField(db_column='Year')  # Field name made lowercase.
    progno = models.SmallIntegerField(db_column='ProgNo')  # Field name made lowercase.
    fullname = models.TextField(db_column='FullName')  # Field name made lowercase.
    provider = models.TextField(db_column='Provider')  # Field name made lowercase.
    isvalid = models.SmallIntegerField(db_column='IsValid')  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=500)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolRelatedProgramme'
        unique_together = (('schoolid', 'year', 'progno'),)


class Schoolrelatedncs(models.Model):
    schoolid = models.CharField(primary_key=True, max_length=12)
    year = models.IntegerField(db_column='Year')  # Field name made lowercase.
    p1 = models.SmallIntegerField(db_column='P1')  # Field name made lowercase.
    p2 = models.SmallIntegerField(db_column='P2')  # Field name made lowercase.
    p3 = models.SmallIntegerField(db_column='P3')  # Field name made lowercase.
    p4 = models.SmallIntegerField(db_column='P4')  # Field name made lowercase.
    p5 = models.SmallIntegerField(db_column='P5')  # Field name made lowercase.
    p6 = models.SmallIntegerField(db_column='P6')  # Field name made lowercase.
    s1 = models.SmallIntegerField(db_column='S1')  # Field name made lowercase.
    s2 = models.SmallIntegerField(db_column='S2')  # Field name made lowercase.
    s3 = models.SmallIntegerField(db_column='S3')  # Field name made lowercase.
    s4 = models.SmallIntegerField(db_column='S4')  # Field name made lowercase.
    s5 = models.SmallIntegerField(db_column='S5')  # Field name made lowercase.
    s6 = models.SmallIntegerField(db_column='S6')  # Field name made lowercase.
    subtotal = models.IntegerField(db_column='Subtotal')  # Field name made lowercase.
    total = models.IntegerField(db_column='Total')  # Field name made lowercase.
    percentage = models.CharField(db_column='Percentage', max_length=50)  # Field name made lowercase.
    infonotavailable = models.IntegerField(db_column='InfoNotAvailable')  # Field name made lowercase.
    percentagenot = models.CharField(db_column='PercentageNot', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolRelatedNCS'
        unique_together = (('schoolid', 'year'),)


class Schoolfinancereport(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=16)  # Field name made lowercase.
    yearreceived = models.CharField(db_column='yearReceived', max_length=4)  # Field name made lowercase.
    datareceived = models.DateTimeField(db_column='dataReceived', blank=True, null=True)  # Field name made lowercase.
    auditinspperiod = models.CharField(db_column='auditInspPeriod', max_length=100, blank=True,
                                       null=True)  # Field name made lowercase.
    reportfilename = models.CharField(db_column='reportFileName', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolFinanceReport'
        unique_together = (('schoolid', 'yearreceived', 'reportfilename'),)


class Schoolsct(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=16)  # Field name made lowercase.
    yearsct = models.CharField(db_column='yearSCT', max_length=4)  # Field name made lowercase.
    p1 = models.CharField(db_column='P1', max_length=6, blank=True, null=True)  # Field name made lowercase.
    p2 = models.CharField(db_column='P2', max_length=6, blank=True, null=True)  # Field name made lowercase.
    p3 = models.CharField(db_column='P3', max_length=6, blank=True, null=True)  # Field name made lowercase.
    p4 = models.CharField(db_column='P4', max_length=6, blank=True, null=True)  # Field name made lowercase.
    p5 = models.CharField(db_column='P5', max_length=6, blank=True, null=True)  # Field name made lowercase.
    p6 = models.CharField(db_column='P6', max_length=6, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolSCT'


class Schoolmoireport(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=16)  # Field name made lowercase.
    yearreceived = models.CharField(db_column='YearReceived', max_length=4)  # Field name made lowercase.
    reportfilename = models.CharField(db_column='reportFileName', max_length=100)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolMOIReport'
        unique_together = (('schoolid', 'yearreceived', 'reportfilename'),)


class Areascore2008(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=12)  # Field name made lowercase.
    ssayear = models.IntegerField(db_column='ssaYear')  # Field name made lowercase.
    area01 = models.IntegerField(blank=True, null=True)
    area02 = models.IntegerField(blank=True, null=True)
    area03 = models.IntegerField(blank=True, null=True)
    area04 = models.IntegerField(blank=True, null=True)
    area05 = models.IntegerField(blank=True, null=True)
    area06 = models.IntegerField(blank=True, null=True)
    area07 = models.IntegerField(blank=True, null=True)
    area08 = models.IntegerField(blank=True, null=True)
    scoretypeid = models.IntegerField(db_column='scoreTypeID')  # Field name made lowercase.
    ssastatus = models.IntegerField(db_column='ssaStatus', blank=True, null=True)  # Field name made lowercase.
    lastmodify = models.DateTimeField(blank=True, null=True)
    loginid = models.IntegerField(db_column='LoginID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAreaScore_2008'
        unique_together = (('schoolid', 'ssayear', 'scoretypeid'),)


class SSPA(models.Model):
    schoolid = models.CharField(db_column='schoolID', max_length=12)  # Field name made lowercase.
    years = models.CharField(max_length=10)
    queue = models.SmallIntegerField()
    band1 = models.IntegerField(blank=True, null=True)
    band2 = models.IntegerField(blank=True, null=True)
    band3 = models.IntegerField(blank=True, null=True)
    bandtotal = models.IntegerField(db_column='bandTotal', blank=True, null=True)  # Field name made lowercase.
    band1pct = models.FloatField(blank=True, null=True)
    band2pct = models.FloatField(blank=True, null=True)
    band3pct = models.FloatField(blank=True, null=True)
    bandtotalpct = models.FloatField(db_column='bandTotalpct', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSSPA'


class SchoolInspReport(models.Model):
    schoolid = models.CharField(db_column='SchoolID', max_length=16)  # Field name made lowercase.
    inspyear = models.CharField(db_column='InspYear', max_length=4)  # Field name made lowercase.
    insptype = models.CharField(db_column='InspType', max_length=10)  # Field name made lowercase.
    reportfilename = models.CharField(db_column='reportFileName', max_length=100, blank=True,
                                      null=True)  # Field name made lowercase.
    reportfolder = models.CharField(max_length=100, blank=True, null=True)
    loginid = models.IntegerField(db_column='LoginID', blank=True, null=True)  # Field name made lowercase.
    lastuploaddate = models.DateTimeField(blank=True, null=True)
    indexstring = models.TextField(db_column='IndexString', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolInspReport'


class SchoolDevelopmentPlan(models.Model):
    sdpid = models.IntegerField(db_column='SDPid', primary_key=True)  # Field name made lowercase.
    district = models.CharField(max_length=100)
    schooltype = models.CharField(db_column='schoolType', max_length=2)  # Field name made lowercase.
    schoolnamee = models.CharField(db_column='schoolNameE', max_length=255)  # Field name made lowercase.
    session = models.CharField(max_length=10)
    schoolnamec = models.CharField(db_column='schoolNameC', max_length=255)  # Field name made lowercase.
    financetype = models.CharField(db_column='financeType', max_length=255)  # Field name made lowercase.
    schoolsex = models.CharField(db_column='schoolSex', max_length=100)  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=100)  # Field name made lowercase.
    cryear = models.CharField(db_column='crYear', max_length=100)  # Field name made lowercase.
    schoolid = models.CharField(max_length=16)
    sdoofficer = models.CharField(db_column='SDOOfficer', max_length=200)  # Field name made lowercase.
    ssdoofficer = models.CharField(db_column='SSDOOfficer', max_length=200)  # Field name made lowercase.
    email = models.CharField(max_length=200)
    website = models.CharField(max_length=200)
    code = models.CharField(max_length=16)
    sdpscrn_a = models.CharField(db_column='sdpScrn_A', max_length=50)  # Field name made lowercase.
    sdpscrn_b = models.CharField(db_column='sdpScrn_B', max_length=50)  # Field name made lowercase.
    sdpscrn_c = models.CharField(db_column='sdpScrn_C', max_length=50)  # Field name made lowercase.
    sdpscrn_d = models.CharField(db_column='sdpScrn_D', max_length=50)  # Field name made lowercase.
    sdpscrn_e = models.CharField(db_column='sdpScrn_E', max_length=50)  # Field name made lowercase.
    sdpscrn_f = models.CharField(db_column='sdpScrn_F', max_length=50)  # Field name made lowercase.
    endofsdp = models.CharField(db_column='endOfSdp', max_length=50)  # Field name made lowercase.
    kpmreportyearreceive = models.CharField(db_column='kpmReportYearReceive',
                                            max_length=50)  # Field name made lowercase.
    shsreportyearreceive = models.CharField(db_column='shsReportYearReceive',
                                            max_length=50)  # Field name made lowercase.
    remarks = models.CharField(max_length=1000)
    status_a = models.SmallIntegerField(db_column='status_A')  # Field name made lowercase.
    status_b = models.SmallIntegerField(db_column='status_B')  # Field name made lowercase.
    status_c = models.SmallIntegerField(db_column='status_C')  # Field name made lowercase.
    status_d = models.SmallIntegerField(db_column='status_D')  # Field name made lowercase.
    status_e = models.SmallIntegerField(db_column='status_E')  # Field name made lowercase.
    status_f = models.SmallIntegerField(db_column='status_F')  # Field name made lowercase.
    loginid = models.IntegerField(db_column='loginID')  # Field name made lowercase.
    nummajorconcern_a = models.SmallIntegerField(db_column='numMajorConcern_A')  # Field name made lowercase.
    nummajorconcern_b = models.SmallIntegerField(db_column='numMajorConcern_B')  # Field name made lowercase.
    nummajorconcern_c = models.SmallIntegerField(db_column='numMajorConcern_C')  # Field name made lowercase.
    nummajorconcern_d = models.SmallIntegerField(db_column='numMajorConcern_D')  # Field name made lowercase.
    nummajorconcern_e = models.SmallIntegerField(db_column='numMajorConcern_E')  # Field name made lowercase.
    nummajorconcern_f = models.SmallIntegerField(db_column='numMajorConcern_F')  # Field name made lowercase.
    numrecommendconclusion = models.SmallIntegerField(db_column='numRecommendConclusion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolDevelopmentPlan'


class SchoolDevelopmentPlanData(models.Model):
    sdpformid = models.CharField(db_column='sdpFormID', primary_key=True, max_length=16)  # Field name made lowercase.
    sdptype = models.CharField(db_column='sdpType', primary_key=True, max_length=10)  # Field name made lowercase.
    sheetno = models.SmallIntegerField(db_column='sheetNo', primary_key=True)  # Field name made lowercase.
    SDP0101 = models.BooleanField(db_column='SDP0101', blank=True, null=True)  # Field name made lowercase.
    SDP0102 = models.BooleanField(db_column='SDP0102', blank=True, null=True)  # Field name made lowercase.
    SDP0103 = models.BooleanField(db_column='SDP0103', blank=True, null=True)  # Field name made lowercase.
    SDP0104 = models.BooleanField(db_column='SDP0104', blank=True, null=True)  # Field name made lowercase.
    SDP0105 = models.BooleanField(db_column='SDP0105', blank=True, null=True)  # Field name made lowercase.
    SDP0201 = models.BooleanField(db_column='SDP0201', blank=True, null=True)  # Field name made lowercase.
    SDP0202 = models.BooleanField(db_column='SDP0202', blank=True, null=True)  # Field name made lowercase.
    SDP0203 = models.BooleanField(db_column='SDP0203', blank=True, null=True)  # Field name made lowercase.
    SDP0204 = models.BooleanField(db_column='SDP0204', blank=True, null=True)  # Field name made lowercase.
    SDP0205 = models.BooleanField(db_column='SDP0205', blank=True, null=True)  # Field name made lowercase.
    SDP0206 = models.BooleanField(db_column='SDP0206', blank=True, null=True)  # Field name made lowercase.
    SDP0207 = models.BooleanField(db_column='SDP0207', blank=True, null=True)  # Field name made lowercase.
    SDP0208 = models.BooleanField(db_column='SDP0208', blank=True, null=True)  # Field name made lowercase.
    SDP0209 = models.BooleanField(db_column='SDP0209', blank=True, null=True)  # Field name made lowercase.
    SDP0210 = models.BooleanField(db_column='SDP0210', blank=True, null=True)  # Field name made lowercase.
    SDP0211 = models.BooleanField(db_column='SDP0211', blank=True, null=True)  # Field name made lowercase.
    SDP0212 = models.BooleanField(db_column='SDP0212', blank=True, null=True)  # Field name made lowercase.
    SDP0213 = models.BooleanField(db_column='SDP0213', blank=True, null=True)  # Field name made lowercase.
    SDP0214 = models.BooleanField(db_column='SDP0214', blank=True, null=True)  # Field name made lowercase.
    SDP0215 = models.BooleanField(db_column='SDP0215', blank=True, null=True)  # Field name made lowercase.
    SDP0216 = models.BooleanField(db_column='SDP0216', blank=True, null=True)  # Field name made lowercase.
    SDP0217 = models.BooleanField(db_column='SDP0217', blank=True, null=True)  # Field name made lowercase.
    SDP0218 = models.BooleanField(db_column='SDP0218', blank=True, null=True)  # Field name made lowercase.
    SDP0219 = models.BooleanField(db_column='SDP0219', blank=True, null=True)  # Field name made lowercase.
    SDP0220 = models.BooleanField(db_column='SDP0220', blank=True, null=True)  # Field name made lowercase.
    SDP0221 = models.BooleanField(db_column='SDP0221', blank=True, null=True)  # Field name made lowercase.
    SDP0222 = models.BooleanField(db_column='SDP0222', blank=True, null=True)  # Field name made lowercase.
    SDP0223 = models.BooleanField(db_column='SDP0223', blank=True, null=True)  # Field name made lowercase.
    SDP0224 = models.BooleanField(db_column='SDP0224', blank=True, null=True)  # Field name made lowercase.
    SDP0301 = models.BooleanField(db_column='SDP0301', blank=True, null=True)  # Field name made lowercase.
    SDP0302 = models.BooleanField(db_column='SDP0302', blank=True, null=True)  # Field name made lowercase.
    SDP0303 = models.BooleanField(db_column='SDP0303', blank=True, null=True)  # Field name made lowercase.
    SDP0304 = models.BooleanField(db_column='SDP0304', blank=True, null=True)  # Field name made lowercase.
    SDP0305 = models.BooleanField(db_column='SDP0305', blank=True, null=True)  # Field name made lowercase.
    SDP0306 = models.BooleanField(db_column='SDP0306', blank=True, null=True)  # Field name made lowercase.
    SDP0307 = models.BooleanField(db_column='SDP0307', blank=True, null=True)  # Field name made lowercase.
    SDP0308 = models.BooleanField(db_column='SDP0308', blank=True, null=True)  # Field name made lowercase.
    SDP0309 = models.BooleanField(db_column='SDP0309', blank=True, null=True)  # Field name made lowercase.
    SDP0310 = models.BooleanField(db_column='SDP0310', blank=True, null=True)  # Field name made lowercase.
    SDP0311 = models.BooleanField(db_column='SDP0311', blank=True, null=True)  # Field name made lowercase.
    SDP0312 = models.BooleanField(db_column='SDP0312', blank=True, null=True)  # Field name made lowercase.
    SDP0313 = models.BooleanField(db_column='SDP0313', blank=True, null=True)  # Field name made lowercase.
    SDP0314 = models.BooleanField(db_column='SDP0314', blank=True, null=True)  # Field name made lowercase.
    SDP0315 = models.BooleanField(db_column='SDP0315', blank=True, null=True)  # Field name made lowercase.
    SDP0316 = models.BooleanField(db_column='SDP0316', blank=True, null=True)  # Field name made lowercase.
    SDP0317 = models.BooleanField(db_column='SDP0317', blank=True, null=True)  # Field name made lowercase.
    SDP0401 = models.TextField(db_column='SDP0401', blank=True, null=True)  # Field name made lowercase.
    SDP0402 = models.TextField(db_column='SDP0402', blank=True, null=True)  # Field name made lowercase.
    SDP0403 = models.TextField(db_column='SDP0403', blank=True, null=True)  # Field name made lowercase.
    SDP0404 = models.TextField(db_column='SDP0404', blank=True, null=True)  # Field name made lowercase.
    SDP0405 = models.TextField(db_column='SDP0405', blank=True, null=True)  # Field name made lowercase.
    SDP0406 = models.TextField(db_column='SDP0406', blank=True, null=True)  # Field name made lowercase.
    SDP0601 = models.BooleanField(db_column='SDP0601', blank=True, null=True)  # Field name made lowercase.
    SDP0602 = models.BooleanField(db_column='SDP0602', blank=True, null=True)  # Field name made lowercase.
    SDP060201 = models.BooleanField(db_column='SDP060201', blank=True, null=True)  # Field name made lowercase.
    SDP060202 = models.BooleanField(db_column='SDP060202', blank=True, null=True)  # Field name made lowercase.
    SDP060301 = models.BooleanField(db_column='SDP060301', blank=True, null=True)  # Field name made lowercase.
    SDP060302 = models.BooleanField(db_column='SDP060302', blank=True, null=True)  # Field name made lowercase.
    SDP060501 = models.BooleanField(db_column='SDP060501', blank=True, null=True)  # Field name made lowercase.
    SDP060502 = models.BooleanField(db_column='SDP060502', blank=True, null=True)  # Field name made lowercase.
    SDP060503 = models.BooleanField(db_column='SDP060503', blank=True, null=True)  # Field name made lowercase.
    SDP0603 = models.BooleanField(db_column='SDP0603', blank=True, null=True)  # Field name made lowercase.
    SDP0604 = models.BooleanField(db_column='SDP0604', blank=True, null=True)  # Field name made lowercase.
    SDP0605 = models.BooleanField(db_column='SDP0605', blank=True, null=True)  # Field name made lowercase.
    SDP0701 = models.BooleanField(db_column='SDP0701', blank=True, null=True)  # Field name made lowercase.
    SDP070101 = models.BooleanField(db_column='SDP070101', blank=True, null=True)  # Field name made lowercase.
    SDP070102 = models.BooleanField(db_column='SDP070102', blank=True, null=True)  # Field name made lowercase.
    SDP0702 = models.BooleanField(db_column='SDP0702', blank=True, null=True)  # Field name made lowercase.
    SDP070201 = models.BooleanField(db_column='SDP070201', blank=True, null=True)  # Field name made lowercase.
    SDP070202 = models.BooleanField(db_column='SDP070202', blank=True, null=True)  # Field name made lowercase.
    SDP0703 = models.BooleanField(db_column='SDP0703', blank=True, null=True)  # Field name made lowercase.
    SDP070301 = models.BooleanField(db_column='SDP070301', blank=True, null=True)  # Field name made lowercase.
    SDP070302 = models.BooleanField(db_column='SDP070302', blank=True, null=True)  # Field name made lowercase.
    SDP070303 = models.BooleanField(db_column='SDP070303', blank=True, null=True)  # Field name made lowercase.
    SDP070304 = models.BooleanField(db_column='SDP070304', blank=True, null=True)  # Field name made lowercase.
    SDP070305 = models.BooleanField(db_column='SDP070305', blank=True, null=True)  # Field name made lowercase.
    SDP070306 = models.BooleanField(db_column='SDP070306', blank=True, null=True)  # Field name made lowercase.
    SDP0704 = models.BooleanField(db_column='SDP0704', blank=True, null=True)  # Field name made lowercase.
    SDP070401 = models.BooleanField(db_column='SDP070401', blank=True, null=True)  # Field name made lowercase.
    SDP070402 = models.BooleanField(db_column='SDP070402', blank=True, null=True)  # Field name made lowercase.
    SDP070403 = models.BooleanField(db_column='SDP070403', blank=True, null=True)  # Field name made lowercase.
    SDP070404 = models.BooleanField(db_column='SDP070404', blank=True, null=True)  # Field name made lowercase.
    SDP0705 = models.BooleanField(db_column='SDP0705', blank=True, null=True)  # Field name made lowercase.
    SDP070501 = models.BooleanField(db_column='SDP070501', blank=True, null=True)  # Field name made lowercase.
    SDP070502 = models.BooleanField(db_column='SDP070502', blank=True, null=True)  # Field name made lowercase.
    SDP070503 = models.BooleanField(db_column='SDP070503', blank=True, null=True)  # Field name made lowercase.
    SDP070504 = models.BooleanField(db_column='SDP070504', blank=True, null=True)  # Field name made lowercase.
    SDP070505 = models.BooleanField(db_column='SDP070505', blank=True, null=True)  # Field name made lowercase.
    SDP070506 = models.BooleanField(db_column='SDP070506', blank=True, null=True)  # Field name made lowercase.
    SDP0706 = models.BooleanField(db_column='SDP0706', blank=True, null=True)  # Field name made lowercase.
    SDP070601 = models.BooleanField(db_column='SDP070601', blank=True, null=True)  # Field name made lowercase.
    SDP070602 = models.BooleanField(db_column='SDP070602', blank=True, null=True)  # Field name made lowercase.
    SDP070603 = models.BooleanField(db_column='SDP070603', blank=True, null=True)  # Field name made lowercase.
    SDP070604 = models.BooleanField(db_column='SDP070604', blank=True, null=True)  # Field name made lowercase.
    SDP070605 = models.BooleanField(db_column='SDP070605', blank=True, null=True)  # Field name made lowercase.
    SDP070606 = models.BooleanField(db_column='SDP070606', blank=True, null=True)  # Field name made lowercase.
    SDP070607 = models.BooleanField(db_column='SDP070607', blank=True, null=True)  # Field name made lowercase.
    SDP0707 = models.BooleanField(db_column='SDP0707', blank=True, null=True)  # Field name made lowercase.
    SDP070701 = models.BooleanField(db_column='SDP070701', blank=True, null=True)  # Field name made lowercase.
    SDP070702 = models.BooleanField(db_column='SDP070702', blank=True, null=True)  # Field name made lowercase.
    SDP070703 = models.BooleanField(db_column='SDP070703', blank=True, null=True)  # Field name made lowercase.
    SDP0708 = models.BooleanField(db_column='SDP0708', blank=True, null=True)  # Field name made lowercase.
    SDP070801 = models.BooleanField(db_column='SDP070801', blank=True, null=True)  # Field name made lowercase.
    SDP070802 = models.BooleanField(db_column='SDP070802', blank=True, null=True)  # Field name made lowercase.
    SDP070803 = models.BooleanField(db_column='SDP070803', blank=True, null=True)  # Field name made lowercase.
    SDP0709 = models.BooleanField(db_column='SDP0709', blank=True, null=True)  # Field name made lowercase.
    SDP070901 = models.BooleanField(db_column='SDP070901', blank=True, null=True)  # Field name made lowercase.
    SDP070902 = models.BooleanField(db_column='SDP070902', blank=True, null=True)  # Field name made lowercase.
    SDP0710 = models.BooleanField(db_column='SDP0710', blank=True, null=True)  # Field name made lowercase.
    SDP071001 = models.BooleanField(db_column='SDP071001', blank=True, null=True)  # Field name made lowercase.
    SDP071002 = models.BooleanField(db_column='SDP071002', blank=True, null=True)  # Field name made lowercase.
    SDP071003 = models.BooleanField(db_column='SDP071003', blank=True, null=True)  # Field name made lowercase.
    SDP071004 = models.BooleanField(db_column='SDP071004', blank=True, null=True)  # Field name made lowercase.
    SDP071005 = models.BooleanField(db_column='SDP071005', blank=True, null=True)  # Field name made lowercase.
    SDP0711 = models.BooleanField(db_column='SDP0711', blank=True, null=True)  # Field name made lowercase.
    SDP071101 = models.BooleanField(db_column='SDP071101', blank=True, null=True)  # Field name made lowercase.
    SDP0712 = models.BooleanField(db_column='SDP0712', blank=True, null=True)  # Field name made lowercase.
    SDP071201 = models.BooleanField(db_column='SDP071201', blank=True, null=True)  # Field name made lowercase.
    SDP071202 = models.BooleanField(db_column='SDP071202', blank=True, null=True)  # Field name made lowercase.
    SDP071203 = models.BooleanField(db_column='SDP071203', blank=True, null=True)  # Field name made lowercase.
    SDP071204 = models.BooleanField(db_column='SDP071204', blank=True, null=True)  # Field name made lowercase.
    SDP071205 = models.BooleanField(db_column='SDP071205', blank=True, null=True)  # Field name made lowercase.
    SDP071206 = models.BooleanField(db_column='SDP071206', blank=True, null=True)  # Field name made lowercase.
    SDP071207 = models.BooleanField(db_column='SDP071207', blank=True, null=True)  # Field name made lowercase.
    SDP071208 = models.BooleanField(db_column='SDP071208', blank=True, null=True)  # Field name made lowercase.
    SDP071209 = models.BooleanField(db_column='SDP071209', blank=True, null=True)  # Field name made lowercase.
    SDP071210 = models.BooleanField(db_column='SDP071210', blank=True, null=True)  # Field name made lowercase.
    SDP071211 = models.BooleanField(db_column='SDP071211', blank=True, null=True)  # Field name made lowercase.
    SDP071212 = models.BooleanField(db_column='SDP071212', blank=True, null=True)  # Field name made lowercase.
    SDP0713 = models.BooleanField(db_column='SDP0713', blank=True, null=True)  # Field name made lowercase.
    SDP071301 = models.BooleanField(db_column='SDP071301', blank=True, null=True)  # Field name made lowercase.
    SDP071302 = models.BooleanField(db_column='SDP071302', blank=True, null=True)  # Field name made lowercase.
    SDP071303 = models.BooleanField(db_column='SDP071303', blank=True, null=True)  # Field name made lowercase.
    SDP071304 = models.BooleanField(db_column='SDP071304', blank=True, null=True)  # Field name made lowercase.
    SDP0714 = models.BooleanField(db_column='SDP0714', blank=True, null=True)  # Field name made lowercase.
    SDP071401 = models.BooleanField(db_column='SDP071401', blank=True, null=True)  # Field name made lowercase.
    SDP071402 = models.BooleanField(db_column='SDP071402', blank=True, null=True)  # Field name made lowercase.
    SDP071403 = models.BooleanField(db_column='SDP071403', blank=True, null=True)  # Field name made lowercase.
    SDP071404 = models.BooleanField(db_column='SDP071404', blank=True, null=True)  # Field name made lowercase.
    SDP071405 = models.BooleanField(db_column='SDP071405', blank=True, null=True)  # Field name made lowercase.
    SDP071406 = models.BooleanField(db_column='SDP071406', blank=True, null=True)  # Field name made lowercase.
    SDP071407 = models.BooleanField(db_column='SDP071407', blank=True, null=True)  # Field name made lowercase.
    SDP071408 = models.BooleanField(db_column='SDP071408', blank=True, null=True)  # Field name made lowercase.
    SDP0715 = models.BooleanField(db_column='SDP0715', blank=True, null=True)  # Field name made lowercase.
    SDP071501 = models.BooleanField(db_column='SDP071501', blank=True, null=True)  # Field name made lowercase.
    SDP0716 = models.BooleanField(db_column='SDP0716', blank=True, null=True)  # Field name made lowercase.
    SDP071601 = models.BooleanField(db_column='SDP071601', blank=True, null=True)  # Field name made lowercase.
    SDP071602 = models.BooleanField(db_column='SDP071602', blank=True, null=True)  # Field name made lowercase.
    SDP0717 = models.BooleanField(db_column='SDP0717', blank=True, null=True)  # Field name made lowercase.
    SDP071701 = models.BooleanField(db_column='SDP071701', blank=True, null=True)  # Field name made lowercase.
    SDP0718 = models.BooleanField(db_column='SDP0718', blank=True, null=True)  # Field name made lowercase.
    SDP0719 = models.BooleanField(db_column='SDP0719', blank=True, null=True)  # Field name made lowercase.
    SDP071901 = models.BooleanField(db_column='SDP071901', blank=True, null=True)  # Field name made lowercase.
    SDP071902 = models.BooleanField(db_column='SDP071902', blank=True, null=True)  # Field name made lowercase.
    SDP071903 = models.BooleanField(db_column='SDP071903', blank=True, null=True)  # Field name made lowercase.
    SDP071904 = models.BooleanField(db_column='SDP071904', blank=True, null=True)  # Field name made lowercase.
    SDP0720 = models.BooleanField(db_column='SDP0720', blank=True, null=True)  # Field name made lowercase.
    SDP072001 = models.BooleanField(db_column='SDP072001', blank=True, null=True)  # Field name made lowercase.
    SDP072002 = models.BooleanField(db_column='SDP072002', blank=True, null=True)  # Field name made lowercase.
    SDP072003 = models.BooleanField(db_column='SDP072003', blank=True, null=True)  # Field name made lowercase.
    SDP0721 = models.BooleanField(db_column='SDP0721', blank=True, null=True)  # Field name made lowercase.
    SDP072101 = models.BooleanField(db_column='SDP072101', blank=True, null=True)  # Field name made lowercase.
    SDP072102 = models.BooleanField(db_column='SDP072102', blank=True, null=True)  # Field name made lowercase.
    SDP0722 = models.BooleanField(db_column='SDP0722', blank=True, null=True)  # Field name made lowercase.
    SDP072201 = models.BooleanField(db_column='SDP072201', blank=True, null=True)  # Field name made lowercase.
    SDP072202 = models.BooleanField(db_column='SDP072202', blank=True, null=True)  # Field name made lowercase.
    SDP072203 = models.BooleanField(db_column='SDP072203', blank=True, null=True)  # Field name made lowercase.
    SDP072204 = models.BooleanField(db_column='SDP072204', blank=True, null=True)  # Field name made lowercase.
    SDP0723 = models.BooleanField(db_column='SDP0723', blank=True, null=True)  # Field name made lowercase.
    SDP072301 = models.BooleanField(db_column='SDP072301', blank=True, null=True)  # Field name made lowercase.
    SDP072302 = models.BooleanField(db_column='SDP072302', blank=True, null=True)  # Field name made lowercase.
    SDP072303 = models.BooleanField(db_column='SDP072303', blank=True, null=True)  # Field name made lowercase.
    SDP072304 = models.BooleanField(db_column='SDP072304', blank=True, null=True)  # Field name made lowercase.
    SDP0724 = models.BooleanField(db_column='SDP0724', blank=True, null=True)  # Field name made lowercase.
    SDP0801 = models.BooleanField(db_column='SDP0801', blank=True, null=True)  # Field name made lowercase.
    SDP080101 = models.BooleanField(db_column='SDP080101', blank=True, null=True)  # Field name made lowercase.
    SDP080102 = models.BooleanField(db_column='SDP080102', blank=True, null=True)  # Field name made lowercase.
    SDP080103 = models.BooleanField(db_column='SDP080103', blank=True, null=True)  # Field name made lowercase.
    SDP080104 = models.BooleanField(db_column='SDP080104', blank=True, null=True)  # Field name made lowercase.
    SDP080105 = models.BooleanField(db_column='SDP080105', blank=True, null=True)  # Field name made lowercase.
    SDP080106 = models.BooleanField(db_column='SDP080106', blank=True, null=True)  # Field name made lowercase.
    SDP080107 = models.BooleanField(db_column='SDP080107', blank=True, null=True)  # Field name made lowercase.
    SDP0802 = models.BooleanField(db_column='SDP0802', blank=True, null=True)  # Field name made lowercase.
    SDP080201 = models.BooleanField(db_column='SDP080201', blank=True, null=True)  # Field name made lowercase.
    SDP080202 = models.BooleanField(db_column='SDP080202', blank=True, null=True)  # Field name made lowercase.
    SDP080203 = models.BooleanField(db_column='SDP080203', blank=True, null=True)  # Field name made lowercase.
    SDP0803 = models.BooleanField(db_column='SDP0803', blank=True, null=True)  # Field name made lowercase.
    SDP080301 = models.BooleanField(db_column='SDP080301', blank=True, null=True)  # Field name made lowercase.
    SDP0804 = models.BooleanField(db_column='SDP0804', blank=True, null=True)  # Field name made lowercase.
    SDP080401 = models.BooleanField(db_column='SDP080401', blank=True, null=True)  # Field name made lowercase.
    SDP080402 = models.BooleanField(db_column='SDP080402', blank=True, null=True)  # Field name made lowercase.
    SDP080403 = models.BooleanField(db_column='SDP080403', blank=True, null=True)  # Field name made lowercase.
    SDP0805 = models.BooleanField(db_column='SDP0805', blank=True, null=True)  # Field name made lowercase.
    SDP080501 = models.BooleanField(db_column='SDP080501', blank=True, null=True)  # Field name made lowercase.
    SDP0806 = models.BooleanField(db_column='SDP0806', blank=True, null=True)  # Field name made lowercase.
    SDP0807 = models.BooleanField(db_column='SDP0807', blank=True, null=True)  # Field name made lowercase.
    SDP080701 = models.BooleanField(db_column='SDP080701', blank=True, null=True)  # Field name made lowercase.
    SDP080702 = models.BooleanField(db_column='SDP080702', blank=True, null=True)  # Field name made lowercase.
    SDP080703 = models.BooleanField(db_column='SDP080703', blank=True, null=True)  # Field name made lowercase.
    SDP0808 = models.BooleanField(db_column='SDP0808', blank=True, null=True)  # Field name made lowercase.
    SDP080801 = models.BooleanField(db_column='SDP080801', blank=True, null=True)  # Field name made lowercase.
    SDP080802 = models.BooleanField(db_column='SDP080802', blank=True, null=True)  # Field name made lowercase.
    SDP080803 = models.BooleanField(db_column='SDP080803', blank=True, null=True)  # Field name made lowercase.
    SDP0809 = models.BooleanField(db_column='SDP0809', blank=True, null=True)  # Field name made lowercase.
    SDP080901 = models.BooleanField(db_column='SDP080901', blank=True, null=True)  # Field name made lowercase.
    SDP080902 = models.BooleanField(db_column='SDP080902', blank=True, null=True)  # Field name made lowercase.
    SDP0810 = models.BooleanField(db_column='SDP0810', blank=True, null=True)  # Field name made lowercase.
    SDP081001 = models.BooleanField(db_column='SDP081001', blank=True, null=True)  # Field name made lowercase.
    SDP081002 = models.BooleanField(db_column='SDP081002', blank=True, null=True)  # Field name made lowercase.
    SDP0811 = models.BooleanField(db_column='SDP0811', blank=True, null=True)  # Field name made lowercase.
    SDP081101 = models.BooleanField(db_column='SDP081101', blank=True, null=True)  # Field name made lowercase.
    SDP081102 = models.BooleanField(db_column='SDP081102', blank=True, null=True)  # Field name made lowercase.
    SDP0812 = models.BooleanField(db_column='SDP0812', blank=True, null=True)  # Field name made lowercase.
    SDP081201 = models.BooleanField(db_column='SDP081201', blank=True, null=True)  # Field name made lowercase.
    SDP081202 = models.BooleanField(db_column='SDP081202', blank=True, null=True)  # Field name made lowercase.
    SDP081203 = models.BooleanField(db_column='SDP081203', blank=True, null=True)  # Field name made lowercase.
    SDP0813 = models.BooleanField(db_column='SDP0813', blank=True, null=True)  # Field name made lowercase.
    SDP081301 = models.BooleanField(db_column='SDP081301', blank=True, null=True)  # Field name made lowercase.
    SDP081302 = models.BooleanField(db_column='SDP081302', blank=True, null=True)  # Field name made lowercase.
    SDP0814 = models.BooleanField(db_column='SDP0814', blank=True, null=True)  # Field name made lowercase.
    SDP081401 = models.BooleanField(db_column='SDP081401', blank=True, null=True)  # Field name made lowercase.
    SDP0815 = models.BooleanField(db_column='SDP0815', blank=True, null=True)  # Field name made lowercase.
    SDP081501 = models.BooleanField(db_column='SDP081501', blank=True, null=True)  # Field name made lowercase.
    SDP081502 = models.BooleanField(db_column='SDP081502', blank=True, null=True)  # Field name made lowercase.
    SDP081503 = models.BooleanField(db_column='SDP081503', blank=True, null=True)  # Field name made lowercase.
    SDP0816 = models.BooleanField(db_column='SDP0816', blank=True, null=True)  # Field name made lowercase.
    SDP081601 = models.BooleanField(db_column='SDP081601', blank=True, null=True)  # Field name made lowercase.
    SDP0817 = models.BooleanField(db_column='SDP0817', blank=True, null=True)  # Field name made lowercase.
    SDP081701 = models.BooleanField(db_column='SDP081701', blank=True, null=True)  # Field name made lowercase.
    SDP081702 = models.BooleanField(db_column='SDP081702', blank=True, null=True)  # Field name made lowercase.
    SDP0901 = models.TextField(db_column='SDP0901', blank=True, null=True)  # Field name made lowercase.
    SDP0902 = models.TextField(db_column='SDP0902', blank=True, null=True)  # Field name made lowercase.
    SDP0903 = models.TextField(db_column='SDP0903', blank=True, null=True)  # Field name made lowercase.
    SDP0904 = models.TextField(db_column='SDP0904', blank=True, null=True)  # Field name made lowercase.
    SDP0905 = models.TextField(db_column='SDP0905', blank=True, null=True)  # Field name made lowercase.
    SDP0906 = models.TextField(db_column='SDP0906', blank=True, null=True)  # Field name made lowercase.
    status = models.SmallIntegerField(blank=True, null=True)
    createdate = models.DateTimeField(db_column='createDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSchoolDevelopmentPlan_Data'
        unique_together = (('sdpformid', 'sdptype', 'sheetno'),)


class SchoolDevelopmentPlanLevel(models.Model):
    levelid = models.CharField(db_column='levelID', max_length=50)  # Field name made lowercase.
    levelbase = models.SmallIntegerField(db_column='levelBase')  # Field name made lowercase.
    leveldescc = models.CharField(db_column='levelDescC', max_length=1000, blank=True,
                                  null=True)  # Field name made lowercase.
    leveldesce = models.CharField(db_column='levelDescE', max_length=1000)  # Field name made lowercase.
    perviouslevelid = models.CharField(db_column='perviousLevelID', max_length=50)  # Field name made lowercase.
    answertypeid = models.SmallIntegerField(db_column='answerTypeID')  # Field name made lowercase.
    schooltypeid = models.CharField(db_column='schoolTypeID', max_length=1)  # Field name made lowercase.
    sdpyear = models.IntegerField(primary_key=True)
    part = models.CharField(max_length=10, blank=True, null=True)
    sequence = models.SmallIntegerField(blank=True, null=True)
    subsequence = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblSchoolDevelopmentPlan_Level'
        unique_together = (('sdpyear', 'schooltypeid', 'levelid'),)


class UserWatchlist(models.Model):
    loginid = models.IntegerField(db_column='loginID', primary_key=True)  # Field name made lowercase.
    schoolidlist = models.TextField(db_column='schoolIDList')  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'tblLogin_watchlist'


class LogItems(models.Model):
    logitemid = models.AutoField(db_column='logItemID', primary_key=True)  # Field name made lowercase.
    logtypeid = models.ForeignKey('LogTypes', models.DO_NOTHING, db_column='logTypeID', blank=True,
                                  null=True)  # Field name made lowercase.
    logitemsubject = models.TextField(db_column='logItemSubject', blank=True, null=True)  # Field name made lowercase.
    logitemdesc = models.TextField(db_column='logItemDesc', blank=True, null=True)  # Field name made lowercase.
    logitemdate = models.DateTimeField(db_column='logItemDate')  # Field name made lowercase.
    contactname = models.CharField(db_column='contactName', max_length=255, blank=True,
                                   null=True)  # Field name made lowercase.
    contactemail = models.CharField(db_column='contactEmail', max_length=255, blank=True,
                                    null=True)  # Field name made lowercase.
    contactschool = models.CharField(db_column='contactSchool', max_length=255, blank=True,
                                     null=True)  # Field name made lowercase.
    contactphone = models.CharField(db_column='contactPhone', max_length=50, blank=True,
                                    null=True)  # Field name made lowercase.
    logitmd = models.IntegerField(db_column='logITMD')  # Field name made lowercase.
    statusid = models.ForeignKey('LogStatus', models.DO_NOTHING, db_column='statusID', blank=True,
                                 null=True)  # Field name made lowercase.
    logcommtypeid = models.ForeignKey('LogCommTypes', models.DO_NOTHING,
                                      db_column='logCommTypeID')  # Field name made lowercase.
    logstaffid = models.SmallIntegerField(db_column='logStaffID', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='createDate')  # Field name made lowercase.
    logcategoryid = models.IntegerField(db_column='logCategoryID')  # Field name made lowercase.
    logsubcategoryid = models.IntegerField(db_column='logSubCategoryID')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='modifyDate')  # Field name made lowercase.
    schoolid = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblLogItem'


class LogCategories(models.Model):
    logcategoryid = models.AutoField(db_column='logCategoryID', primary_key=True)  # Field name made lowercase.
    logcategoryname = models.CharField(db_column='logCategoryName', max_length=100, blank=True,
                                       null=True)  # Field name made lowercase.
    logtypeid = models.ForeignKey('LogTypes', models.DO_NOTHING, db_column='logTypeID', blank=True,
                                  null=True)  # Field name made lowercase.
    ordering = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblLogCategory'


class LogCommTypes(models.Model):
    logcommtypeid = models.AutoField(db_column='logCommTypeID', primary_key=True)  # Field name made lowercase.
    logcommtypedesc = models.CharField(db_column='logCommTypeDesc', max_length=50, blank=True,
                                       null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLogCommType'


class LogPriority(models.Model):
    logpriorityid = models.AutoField(db_column='LogPriorityID', primary_key=True)  # Field name made lowercase.
    logpriorityname = models.CharField(db_column='LogPriorityName', max_length=100, blank=True,
                                       null=True)  # Field name made lowercase.
    ordering = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblLogPriority'


class LogProblemTypes(models.Model):
    logproblemtypeid = models.AutoField(db_column='LogProblemTypeID', primary_key=True)  # Field name made lowercase.
    logproblemtypename = models.CharField(db_column='LogProblemTypeName', max_length=100, blank=True,
                                          null=True)  # Field name made lowercase.
    ordering = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblLogProblemType'


class LogEnquiryResponses(models.Model):
    logresponseid = models.AutoField(db_column='logResponseID', primary_key=True)  # Field name made lowercase.
    logitemid = models.ForeignKey('LogItems', models.DO_NOTHING, db_column='logItemID', blank=True,
                                  null=True)  # Field name made lowercase.
    logresponsedesc = models.TextField(db_column='logResponseDesc', blank=True, null=True)  # Field name made lowercase.
    logstaffid = models.SmallIntegerField(db_column='logStaffID', blank=True, null=True)  # Field name made lowercase.
    logresponsedate = models.DateTimeField(db_column='logResponseDate')  # Field name made lowercase.
    logcommtypeid = models.ForeignKey('LogCommTypes', models.DO_NOTHING, db_column='logCommTypeID', blank=True,
                                      null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLogResponse'


class LogStatus(models.Model):
    statusid = models.AutoField(db_column='statusID', primary_key=True)  # Field name made lowercase.
    statusdesc = models.CharField(db_column='statusDesc', max_length=50, blank=True,
                                  null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLogStatus'


class LogSubCategories(models.Model):
    logsubcategoryid = models.AutoField(db_column='logSubCategoryID', primary_key=True)  # Field name made lowercase.
    logcategoryid = models.IntegerField(db_column='logCategoryID')  # Field name made lowercase.
    logsubcategoryname = models.CharField(db_column='logSubCategoryName', max_length=100, blank=True,
                                          null=True)  # Field name made lowercase.
    ordering = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblLogSubCategory'
        unique_together = (('logsubcategoryid', 'logcategoryid'),)


class LogTypes(models.Model):
    logtypeid = models.AutoField(db_column='logTypeID', primary_key=True)  # Field name made lowercase.
    logtypedesc = models.CharField(db_column='logTypeDesc', max_length=50, blank=True,
                                   null=True)  # Field name made lowercase.
    sequence = models.SmallIntegerField(db_column='sequence')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLogType'


class LogReport(models.Model):
    reportid = models.AutoField(db_column='ReportID', primary_key=True)  # Field name made lowercase.
    reportname = models.CharField(db_column='ReportName', max_length=500, blank=True,
                                  null=True)  # Field name made lowercase.
    sequence = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblReport'


class LoginHist(models.Model):
    logid = models.AutoField(db_column='LogID', primary_key=True)  # Field name made lowercase.
    loginid = models.IntegerField()
    username = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    lastlogin = models.DateTimeField(db_column='LastLogin')  # Field name made lowercase.
    ip = models.CharField(max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    clientip = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    clientinfo = models.CharField(db_column='clientInfo', max_length=300,
                                  db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    servername = models.CharField(db_column='serverName', max_length=300,
                                  db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    logintype = models.CharField(db_column='LoginType', max_length=20,
                                 db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLoginHist'


class PageView(models.Model):
    logid = models.AutoField(db_column='LogID', primary_key=True)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    username = models.CharField(db_column='username', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    logdatetime = models.DateTimeField(db_column='LogDatetime')  # Field name made lowercase.
    subcatid = models.IntegerField(db_column='subcatid')  # Field name made lowercase.
    pagename = models.CharField(db_column='PageName', max_length=500)  # Field name made lowercase.
    logintype = models.CharField(db_column='LoginType', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLoginPageView'


class Roster(models.Model):
    id = models.IntegerField(primary_key=True)
    postid = models.IntegerField()
    post = models.CharField(db_column='post', max_length=10, blank=True, null=True)  # Field name made lowercase.
    groupid = models.IntegerField(blank=True, null=True)
    weekid = models.IntegerField(blank=True, null=True)
    dayid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblRoster'


class DutyPattern(models.Model):
    id = models.IntegerField(primary_key=True)
    post = models.CharField(db_column='post', max_length=10, blank=True, null=True)  # Field name made lowercase.
    pattern = models.CharField(db_column='post', max_length=2, blank=True, null=True)  # Field name made lowercase.
    monthid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblDutyPattern'


class Venues(models.Model):
    id = models.IntegerField(primary_key=True)
    venue = models.CharField(db_column='Venue', max_length=500)  # Field name made lowercase.
    ismost = models.IntegerField(db_column='IsMost', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblVenue'


class Rooms(models.Model):
    roomid = models.IntegerField(primary_key=True)
    roomdesc = models.CharField(db_column='roomDesc', max_length=100, blank=True,
                                null=True)  # Field name made lowercase.
    location = models.CharField(max_length=100, blank=True, null=True)
    roomvar = models.CharField(db_column='roomVar', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.SmallIntegerField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblroom'


class QAI(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=16)  # Field name made lowercase.
    qaiyear = models.CharField(db_column='qaiYear', max_length=4)  # Field name made lowercase.
    qaitypeid = models.ForeignKey('Tblqaitype', models.DO_NOTHING, db_column='qaiTypeID')  # Field name made lowercase.
    schcode = models.CharField(db_column='schCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    inspreport = models.CharField(db_column='InspReport', max_length=100, blank=True,
                                  null=True)  # Field name made lowercase.
    inspsum = models.CharField(db_column='InspSum', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblqai'
        unique_together = (('schoolid', 'qaiyear', 'qaitypeid'),)


class Account(models.Model):
    postid = models.IntegerField(blank=True, null=True)
    posttitle = models.CharField(db_column='postTitle', max_length=50, blank=True,
                                 null=True)  # Field name made lowercase.
    name_en = models.CharField(max_length=50, blank=True, null=True)
    tel = models.IntegerField(blank=True, null=True)
    ordering = models.IntegerField(blank=True, null=True)
    isactive = models.SmallIntegerField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblaccount'
        unique_together = (('posttitle', 'ordering'),)


class UsersProfile(models.Model):
    def last_seen(self):
        return cache.get('seen_%s' % self.users.loginnamedesc)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                    seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False


class ESRForms(models.Model):
    esrformid = models.CharField(db_column='esrFormID', primary_key=True, max_length=16)  # Field name made lowercase.
    schoolid = models.CharField(db_column='schoolID', max_length=16)  # Field name made lowercase.
    esrcode = models.CharField(db_column='esrCode', max_length=10)  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=4)  # Field name made lowercase.
    sserecommenddesc = models.TextField(db_column='sseRecommendDesc', blank=True,
                                        null=True)  # Field name made lowercase.
    swdesc = models.TextField(db_column='swDesc', blank=True, null=True)  # Field name made lowercase.
    schoolid2 = models.CharField(db_column='schoolID2', max_length=16, blank=True,
                                 null=True)  # Field name made lowercase.
    schoolid3 = models.CharField(db_column='schoolID3', max_length=16, blank=True,
                                 null=True)  # Field name made lowercase.
    developcyclebegin = models.CharField(db_column='developCycleBegin', max_length=9, blank=True,
                                         null=True)  # Field name made lowercase.
    developcycleend = models.CharField(db_column='developCycleEnd', max_length=9, blank=True,
                                       null=True)  # Field name made lowercase.
    status = models.SmallIntegerField()
    lastupdatedate = models.DateTimeField(db_column='lastUpdateDate')  # Field name made lowercase.
    lastusedpost = models.CharField(db_column='lastUsedPost', max_length=20)  # Field name made lowercase.
    teacherpercent = models.IntegerField(db_column='teacherPercent')  # Field name made lowercase.
    modify = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblESRForm'


class EformPage(models.Model):
    year = models.CharField(primary_key=True, max_length=4)
    insptype = models.CharField(db_column='inspType', max_length=10)  # Field name made lowercase.
    formpage = models.CharField(db_column='formPage', max_length=50)  # Field name made lowercase.
    pageid = models.CharField(db_column='pageID', max_length=50)  # Field name made lowercase.
    pagebase = models.SmallIntegerField(db_column='pageBase')  # Field name made lowercase.
    pagedescc = models.CharField(db_column='pageDescC', max_length=500, blank=True,
                                 null=True)  # Field name made lowercase.
    pagedesce = models.CharField(db_column='pageDescE', max_length=500)  # Field name made lowercase.
    subfocustypeid = models.CharField(db_column='subFocusTypeID', max_length=5)  # Field name made lowercase.
    part = models.CharField(max_length=50)
    schooltypeid = models.CharField(db_column='schoolTypeID', max_length=1)  # Field name made lowercase.
    focustypeid = models.CharField(db_column='focusTypeID', max_length=2)  # Field name made lowercase.
    sequence = models.IntegerField()
    readdb = models.CharField(db_column='readDb', max_length=100)  # Field name made lowercase.
    readtable = models.CharField(db_column='readTable', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblEformPage'
        unique_together = (('year', 'insptype', 'formpage', 'pageid', 'subfocustypeid'),)


class EformLog(models.Model):
    logid = models.AutoField(db_column='logID', primary_key=True)  # Field name made lowercase.
    logdatetime = models.DateTimeField(db_column='logDatetime')  # Field name made lowercase.
    loginid = models.CharField(db_column='loginID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    year = models.CharField(max_length=10, blank=True, null=True)
    formid = models.CharField(db_column='formID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    schoolid = models.CharField(db_column='schoolID', max_length=16, blank=True,
                                null=True)  # Field name made lowercase.
    esrcode = models.CharField(db_column='esrCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    databasename = models.CharField(db_column='databaseName', max_length=100, blank=True,
                                    null=True)  # Field name made lowercase.
    tablename = models.CharField(db_column='tableName', max_length=100, blank=True,
                                 null=True)  # Field name made lowercase.
    fieldname = models.CharField(db_column='fieldName', max_length=500, blank=True,
                                 null=True)  # Field name made lowercase.
    fieldvalue = models.TextField(db_column='fieldValue', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbleformlog'


class C12Level(models.Model):
    levelid = models.CharField(db_column='levelID', primary_key=True, max_length=50)  # Field name made lowercase.
    levelbase = models.SmallIntegerField(db_column='levelBase')  # Field name made lowercase.
    leveldescc = models.CharField(db_column='levelDescC', max_length=500, blank=True,
                                  null=True)  # Field name made lowercase.
    leveldesce = models.CharField(db_column='levelDescE', max_length=500)  # Field name made lowercase.
    perviouslevelid = models.CharField(db_column='perviousLevelID', max_length=50)  # Field name made lowercase.
    answertypeid = models.SmallIntegerField(db_column='answerTypeID')  # Field name made lowercase.
    schooltypeid = models.CharField(db_column='schoolTypeID', max_length=1)  # Field name made lowercase.
    c12year = models.CharField(db_column='c12year', max_length=4)

    class Meta:
        managed = False
        db_table = 'tblC12_level'
        unique_together = (('levelid', 'answertypeid', 'schooltypeid', 'c12year'),)


class C12Comments(models.Model):
    commentid = models.CharField(db_column='CommentID', primary_key=True, max_length=50)  # Field name made lowercase.
    commentdescc = models.TextField(db_column='CommentDescC', blank=True, null=True)  # Field name made lowercase.
    commentdesce = models.TextField(db_column='CommentDescE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblC12_Comments'


class KLAForms(models.Model):
    klaformid = models.CharField(db_column='klaFormID', primary_key=True, max_length=20)  # Field name made lowercase.
    schoolid = models.CharField(db_column='schoolID', max_length=12, blank=True,
                                null=True)  # Field name made lowercase.
    schoolyear = models.CharField(db_column='schoolYear', max_length=4, blank=True,
                                  null=True)  # Field name made lowercase.
    ref = models.CharField(max_length=10, blank=True, null=True)
    klaid = models.ForeignKey('KLAGroups', models.DO_NOTHING, db_column='klaID', blank=True,
                              null=True)  # Field name made lowercase.
    inspectiontypeid = models.ForeignKey('InspectionTypes', models.DO_NOTHING, db_column='inspectionTypeID', blank=True,
                                         null=True)  # Field name made lowercase.
    incharge = models.CharField(db_column='inCharge', max_length=225, blank=True,
                                null=True)  # Field name made lowercase.
    inputdate = models.TextField(db_column='inputDate', blank=True,
                                 null=True)  # Field name made lowercase. This field type is a guess.
    subjectinspected = models.CharField(db_column='subjectInspected', max_length=50, blank=True,
                                        null=True)  # Field name made lowercase.
    status = models.SmallIntegerField(blank=True, null=True)
    lastupdatedate = models.DateTimeField(db_column='lastUpdateDate')  # Field name made lowercase.
    lastusedpost = models.CharField(db_column='lastUsedPost', max_length=20)  # Field name made lowercase.
    modify = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblKLAForm'


class KLAGroups(models.Model):
    klaid = models.SmallIntegerField(db_column='klaID', primary_key=True)  # Field name made lowercase.
    kladesce = models.CharField(db_column='klaDescE', max_length=60, blank=True,
                                null=True)  # Field name made lowercase.
    kladescc = models.CharField(db_column='klaDescC', max_length=60, blank=True,
                                null=True)  # Field name made lowercase.
    subfocustypeid = models.CharField(db_column='subFocusTypeID', max_length=2, blank=True,
                                      null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblKLAGroup'


class KLALevel(models.Model):
    levelid = models.CharField(db_column='levelID', primary_key=True, max_length=50)  # Field name made lowercase.
    levelbase = models.SmallIntegerField(db_column='levelBase')  # Field name made lowercase.
    leveldescc = models.CharField(db_column='levelDescC', max_length=1000, blank=True,
                                  null=True)  # Field name made lowercase.
    leveldesce = models.CharField(db_column='levelDescE', max_length=1000)  # Field name made lowercase.
    perviouslevelid = models.CharField(db_column='perviousLevelID', max_length=50)  # Field name made lowercase.
    answertypeid = models.SmallIntegerField(db_column='answerTypeID')  # Field name made lowercase.
    schooltypeid = models.CharField(db_column='schoolTypeID', max_length=1)  # Field name made lowercase.
    klayear = models.IntegerField()
    part = models.CharField(db_column='part', max_length=10)

    class Meta:
        managed = False
        db_table = 'tblKLA_LEVEL'
        unique_together = (('levelid', 'schooltypeid', 'klayear', 'part'),)


class KLAComments(models.Model):
    commentid = models.CharField(db_column='CommentID', primary_key=True, max_length=50)  # Field name made lowercase.
    commentdescc = models.TextField(db_column='CommentDescC', blank=True, null=True)  # Field name made lowercase.
    commentdesce = models.TextField(db_column='CommentDescE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblKLAForm_Comments'


class InspectionTypes(models.Model):
    inspectiontypeid = models.SmallIntegerField(db_column='inspectionTypeID',
                                                primary_key=True)  # Field name made lowercase.
    inspectiontypedesc = models.CharField(db_column='inspectionTypeDesc', max_length=50, blank=True,
                                          null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tblinspectiontype'


class ESRE09C2015(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=20)  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=4)  # Field name made lowercase.
    insptype = models.CharField(db_column='InspType', max_length=10)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    nameexternalreviewer = models.CharField(db_column='NameExternalReviewer',
                                            max_length=500)  # Field name made lowercase.
    erno = models.CharField(db_column='ERNo', max_length=20)  # Field name made lowercase.
    hkidno = models.CharField(db_column='HKIDNo', max_length=20)  # Field name made lowercase.
    postschool = models.CharField(db_column='PostSchool', max_length=500)  # Field name made lowercase.
    rank = models.CharField(db_column='Rank', max_length=20)  # Field name made lowercase.
    parentschool = models.CharField(db_column='ParentSchool', max_length=500)  # Field name made lowercase.
    esrschool = models.CharField(db_column='ESRSchool', max_length=500)  # Field name made lowercase.
    schoolcode = models.CharField(db_column='SchoolCode', max_length=20)  # Field name made lowercase.
    dateattend = models.CharField(db_column='DateAttend', max_length=100)  # Field name made lowercase.
    exactdayattend = models.CharField(db_column='ExactDayAttend', max_length=20)  # Field name made lowercase.
    esrduties = models.CharField(db_column='ESRDuties', max_length=500)  # Field name made lowercase.
    esrrecommend = models.CharField(db_column='ESRRecommend', max_length=500)  # Field name made lowercase.
    subjectexpertise = models.CharField(db_column='SubjectExpertise', max_length=500)  # Field name made lowercase.
    esrdutiesothers = models.CharField(db_column='ESRDutiesOthers', max_length=500)  # Field name made lowercase.
    esrrecommendothers = models.CharField(db_column='ESRRecommendOthers', max_length=500)  # Field name made lowercase.
    subjectexpertiseothers = models.CharField(db_column='SubjectExpertiseOthers',
                                              max_length=500)  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created')  # Field name made lowercase.
    status = models.SmallIntegerField(db_column='Status')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblESRE09c_2015'
        unique_together = (('schoolid', 'esryear', 'insptype', 'loginid', 'erno'),)


class ESRE112017(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=20)  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=4)  # Field name made lowercase.
    insptype = models.CharField(db_column='InspType', max_length=10)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    erno = models.CharField(db_column='ERNo', max_length=20)  # Field name made lowercase.
    esrcode = models.CharField(db_column='ESRCode', max_length=10)  # Field name made lowercase.
    chk01 = models.SmallIntegerField()
    chk02 = models.SmallIntegerField()
    chk03 = models.SmallIntegerField()
    chk04 = models.SmallIntegerField()
    chk05 = models.SmallIntegerField()
    chk06 = models.SmallIntegerField()
    chk07i = models.SmallIntegerField()
    chk07ii = models.SmallIntegerField()
    chk07iii = models.SmallIntegerField()
    chk08i = models.SmallIntegerField()
    chk08ii = models.SmallIntegerField()
    chk08iii = models.SmallIntegerField()
    chk09 = models.SmallIntegerField()
    chk10 = models.SmallIntegerField()
    chk11 = models.SmallIntegerField()
    difficulties = models.TextField(db_column='Difficulties')  # Field name made lowercase.
    suggestions = models.TextField(db_column='Suggestions')  # Field name made lowercase.
    experience = models.TextField(db_column='Experience')  # Field name made lowercase.
    comments = models.TextField(db_column='Comments')  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created')  # Field name made lowercase.
    status = models.SmallIntegerField(db_column='Status')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblESRE11_2017'
        unique_together = (('schoolid', 'esryear', 'insptype', 'loginid', 'erno'),)


class FIE05(models.Model):
    schoolid = models.CharField(db_column='schoolID', primary_key=True, max_length=20)  # Field name made lowercase.
    esryear = models.CharField(db_column='esrYear', max_length=4)  # Field name made lowercase.
    insptype = models.CharField(db_column='InspType', max_length=10)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginID')  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=10)  # Field name made lowercase.
    preinsp = models.DecimalField(db_column='PreInsp', max_digits=18, decimal_places=2, blank=True,
                                  null=True)  # Field name made lowercase.
    actualinsp = models.DecimalField(db_column='ActualInsp', max_digits=18, decimal_places=2, blank=True,
                                     null=True)  # Field name made lowercase.
    postinsp = models.DecimalField(db_column='PostInsp', max_digits=18, decimal_places=2, blank=True,
                                   null=True)  # Field name made lowercase.
    totalinsp = models.DecimalField(db_column='TotalInsp', max_digits=18, decimal_places=2, blank=True,
                                    null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks')  # Field name made lowercase.
    status = models.SmallIntegerField(db_column='Status')  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFIE05'
        unique_together = (('schoolid', 'esryear', 'insptype', 'loginid'),)


class c12A1022015(models.Model):
    esrformid = models.CharField(db_column='esrFormID', primary_key=True, max_length=20)  # Field name made lowercase.
    esr01020101 = models.CharField(db_column='ESR01020101', max_length=50, blank=True,
                                   null=True)  # Field name made lowercase.
    esr01020102 = models.TextField(db_column='ESR01020102', blank=True, null=True)  # Field name made lowercase.
    esr01020103 = models.TextField(db_column='ESR01020103', blank=True, null=True)  # Field name made lowercase.
    esr01020104 = models.IntegerField(db_column='ESR01020104', blank=True, null=True)  # Field name made lowercase.
    esr01020201 = models.TextField(db_column='ESR01020201', blank=True, null=True)  # Field name made lowercase.
    esr01020202 = models.TextField(db_column='ESR01020202', blank=True, null=True)  # Field name made lowercase.
    esr01020203 = models.TextField(db_column='ESR01020203', blank=True, null=True)  # Field name made lowercase.
    esr01020204 = models.IntegerField(db_column='ESR01020204', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblC12_A102_2015'


class c12A1032015(models.Model):
    esrformid = models.CharField(db_column='esrFormID', primary_key=True, max_length=20)  # Field name made lowercase.
    esr0103 = models.IntegerField(db_column='ESR0103', blank=True, null=True)  # Field name made lowercase.
    esr010301 = models.TextField(db_column='ESR010301', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblC12_A103_2015'


class LofForms(models.Model):
    lofformid = models.CharField(db_column='lofFormID', primary_key=True, max_length=25)  # Field name made lowercase.
    schoolid = models.CharField(db_column='schoolID', max_length=12)  # Field name made lowercase.
    lofformyear = models.CharField(db_column='lofFormYear', max_length=4)  # Field name made lowercase.
    teachingmode = models.SmallIntegerField(db_column='TeachingMode', blank=True,
                                            null=True)  # Field name made lowercase.
    classlevelid = models.ForeignKey('LofClassLevel', models.DO_NOTHING,
                                     db_column='classLevelID')  # Field name made lowercase.
    inputdate = models.DateTimeField(db_column='inputDate', blank=True, null=True)  # Field name made lowercase.
    languageid = models.ForeignKey('LofLanguage', models.DO_NOTHING,
                                   db_column='languageID')  # Field name made lowercase.
    moispecify = models.CharField(db_column='MOISpecify', max_length=255, blank=True,
                                  null=True)  # Field name made lowercase.
    issubjectid = models.ForeignKey('LofisSubject', models.DO_NOTHING,
                                    db_column='isSubjectID')  # Field name made lowercase.
    subject = models.CharField(max_length=255, blank=True, null=True)
    subjectdimension = models.CharField(db_column='subjectDimension', max_length=100, blank=True,
                                        null=True)  # Field name made lowercase.
    klaid = models.ForeignKey('LofKLA', models.DO_NOTHING, db_column='klaid')  # Field name made lowercase.
    lessontopic = models.TextField(db_column='lessonTopic', blank=True, null=True)  # Field name made lowercase.
    ismatchmoiid = models.ForeignKey('LofIsMatchMOI', models.DO_NOTHING,
                                     db_column='ismatchMOIID')  # Field name made lowercase.
    observedtime = models.SmallIntegerField(db_column='observedTime', blank=True,
                                            null=True)  # Field name made lowercase.
    observedslotid = models.ForeignKey('LofObservedSlot', models.DO_NOTHING,
                                       db_column='observedSlotID')  # Field name made lowercase.
    staffname = models.CharField(db_column='staffName', max_length=50, blank=True,
                                 null=True)  # Field name made lowercase.
    inspectiontype_id = models.ForeignKey('LofInspectionType', models.DO_NOTHING, db_column='inspectionTypeID',
                                          blank=True, null=True)  # Field name made lovercase.
    uptime = models.TextField(db_column='upTime', blank=True,
                              null=True)  # Field name made lowercase. This field type is a guess.
    inspectorid = models.ForeignKey('LofInspectorList', models.DO_NOTHING, db_column='inspectorID', blank=True,
                                    null=True)  # Field nane made lowercase.
    wholeclass = models.SmallIntegerField(db_column='wholeClass', blank=True, null=True)  # Field name made lowercase.
    splitclass = models.SmallIntegerField(db_column='splitClass', blank=True, null=True)  # Field name made lowercase.
    collaborativeclass = models.SmallIntegerField(db_column='collaborativeClass', blank=True,
                                                  null=True)  # Field name made lovercase.
    lessthan25students = models.SmallIntegerField(db_column='lessThan25Students', blank=True,
                                                  null=True)  # Field name made lovercase.

    class Meta:
        managed = True
        db_table = 'tblLOFForm'


class LofClassLevel(models.Model):
    classlevelid = models.IntegerField(db_column='classLevelID', primary_key=True)  # Field name made lowercase.
    classleveldesce = models.CharField(db_column='classLevelDescE', max_length=10, blank=True,
                                       null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tblclasslevel'


class LofLanguage(models.Model):
    languageid = models.CharField(db_column='languageID', primary_key=True, max_length=2)  # Field name made lowercase.
    languagedesce = models.CharField(db_column='languageDescE', max_length=10, blank=True,
                                     null=True)  # Field name made lowercase.
    languagedescc = models.CharField(db_column='languageDescc', max_length=10, blank=True,
                                     null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbllanguage'


class LofisSubject(models.Model):
    issubjectid = models.CharField(db_column='isSubjectID', primary_key=True,
                                   max_length=2)  # Field name made lowercase.
    issubiectdesce = models.CharField(db_column='isSubjectDesce', max_length=10, blank=True,
                                      null=True)  # Field name made lowercase.
    issubjectdescc = models.CharField(db_column='isSubjectDescc', max_length=10, blank=True,
                                      null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tbllsSubject'


class LofKLA(models.Model):
    klaid = models.SmallIntegerField(db_column='klaID', primary_key=True)  # Field name made lowercase.
    kladesce = models.CharField(db_column='klaDescE', max_length=60, blank=True,
                                null=True)  # Field name made lowercase.
    kladescc = models.CharField(db_column='klaDescc', max_length=60, blank=True,
                                null=True)  # Field name made lowercase.
    ordering = models.IntegerField(db_column='Ordering', blank=True, null=True)  # Field name made lowercase.
    kladisplaye = models.CharField(db_column='klaDisplayE', max_length=100, blank=True,
                                   null=True)  # Field name made lowercase.
    klashortcut = models.CharField(db_column='klaShortCut', max_length=50, blank=True,
                                   null=True)  # Field name made lowercase.
    subfocustypeid = models.CharField(db_column='subFocusTypeID', max_length=5, blank=True,
                                      null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblkla'


class LofIsMatchMOI(models.Model):
    ismatchmoiid = models.CharField(db_column='isMatchMOIID', primary_key=True,
                                    max_length=2)  # Field name made lowercase.
    ismatchmoidesce = models.CharField(db_column='isMatchMOIDescE', max_length=10, blank=True,
                                       null=True)  # Field name made lowercase.
    ismatchmoidescc = models.CharField(db_column='isMatchMOIDescC', max_length=10, blank=True,
                                       null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblismatchmoi'


class LofObservedSlot(models.Model):
    observedslotid = models.CharField(db_column='observedSlotID', primary_key=True,
                                      max_length=2)  # Field name made lowercase.
    observedslotdesce = models.CharField(db_column='observedSlotDescE', max_length=10, blank=True,
                                         null=True)  # Field name made lowercase.
    observedslotdescc = models.CharField(db_column='observedSlotDescC', max_length=10, blank=True,
                                         null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tblobservedslot'


class LofInspectionType(models.Model):
    inspectiontypeid = models.CharField(db_column='inspectionTypeID', primary_key=True,
                                        max_length=2)  # Field name made lowercase.
    inspectiontypedesce = models.CharField(db_column='inspectionTypeDescE', max_length=50, blank=True,
                                           null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tblinspectiontype'


class LofInspectorList(models.Model):
    inspectorid = models.SmallIntegerField(db_column='inspectorID', primary_key=True)  # Field name made lowercase.
    inspectornamee = models.CharField(db_column='inspectorNameE', max_length=255, blank=True,
                                      null=True)  # Field name made lowercase.
    inspectornamec = models.CharField(db_column='inspectorNameC', max_length=255, blank=True,
                                      null=True)  # Field name made lowercase.
    inspectoremail = models.CharField(db_column='inspectorEmail', max_length=255, blank=True,
                                      null=True)  # Field name made lowercase.
    updated = models.DateTimeField(db_column='Updated', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tblinspectorlist'


class LofKLASubjects(models.Model):
    subjectid = models.AutoField(db_column='subjectID', primary_key=True)  # Field name made lowercase.
    klaid = models.ForeignKey('LofKLA', models.DO_NOTHING, db_column='klaID')  # Field name made lowercase.
    subject = models.CharField(max_length=255, blank=True, null=True)
    sequence = models.SmallIntegerField()

    # subjectid = models.SmallIntegerField(db_column='subjectID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TblKLASubject'


class LofFormOverall(models.Model):
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    lofid = models.CharField(db_column='LOFID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    descc = models.CharField(db_column='descC', max_length=255, blank=True, null=True)  # Field name made lowercase.
    desce = models.CharField(db_column='descE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    displaytypeid = models.SmallIntegerField(db_column='displayTypeID', blank=True,
                                             null=True)  # Field name made lowercase.
    year_2005 = models.SmallIntegerField(db_column='2005', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2006 = models.SmallIntegerField(db_column='2006', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2007 = models.SmallIntegerField(db_column='2007', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2008 = models.SmallIntegerField(db_column='2008', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2009 = models.SmallIntegerField(db_column='2009', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2010 = models.SmallIntegerField(db_column='2010', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2011 = models.SmallIntegerField(db_column='2011', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2012 = models.SmallIntegerField(db_column='2012', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2013 = models.SmallIntegerField(db_column='2013', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2014 = models.SmallIntegerField(db_column='2014', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2015 = models.SmallIntegerField(db_column='2015', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2016 = models.SmallIntegerField(db_column='2016', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2017 = models.SmallIntegerField(db_column='2017', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2018 = models.SmallIntegerField(db_column='2018', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2019 = models.SmallIntegerField(db_column='2019', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2020 = models.SmallIntegerField(db_column='2020', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2021 = models.SmallIntegerField(db_column='2021', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2022 = models.SmallIntegerField(db_column='2022', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2023 = models.SmallIntegerField(db_column='2023', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.

    class Meta:
        managed = False
        db_table = 'TblLOFFormOverall'
        # unique_together = (('id', 'lofid', 'displaytypeid'),)


class LofFormOverall_2019_SPC(models.Model):
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    lofid = models.CharField(db_column='LOFID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    descc = models.CharField(db_column='descC', max_length=255, blank=True, null=True)  # Field name made lowercase.
    desce = models.CharField(db_column='descE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    displaytypeid = models.SmallIntegerField(db_column='displayTypeID', blank=True,
                                             null=True)  # Field name made lowercase.
    year_2019 = models.SmallIntegerField(db_column='2019', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2020 = models.SmallIntegerField(db_column='2020', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2021 = models.SmallIntegerField(db_column='2021', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2022 = models.SmallIntegerField(db_column='2022', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.
    year_2023 = models.SmallIntegerField(db_column='2023', blank=True,
                                         null=True)  # Field renamed because it wasn't a valid Python identifier.

    class Meta:
        managed = False
        db_table = 'tblLOFFormOverall_2019_SPC'
        # unique_together = (('id', 'lofid', 'displaytypeid'),)


class SvaisUsers(models.Model):
    schooluser = models.CharField(max_length=200)
    schoolid = models.SmallIntegerField(primary_key=True)
    namee = models.CharField(max_length=200)
    namec = models.CharField(max_length=200)
    password = models.CharField(max_length=50)
    hashpasswo = models.CharField(max_length=50)
    districtid = models.SmallIntegerField()
    eacode = models.SmallIntegerField()
    district = models.CharField(max_length=50)
    remarks = models.CharField(max_length=50)
    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'school_user'


class Shops(models.Model):
    shop_id = models.AutoField(primary_key=True)
    shop_code = models.CharField(max_length=50, blank=True, null=True)
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    shop_name_e = models.CharField(max_length=255, blank=True, null=True)
    shop_address = models.CharField(max_length=255, blank=True, null=True)
    phone_area_code = models.CharField(max_length=3, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    fax_area_code = models.CharField(max_length=3, blank=True, null=True)
    fax_number = models.CharField(max_length=20, blank=True, null=True)
    opening_hours = models.CharField(max_length=100, blank=True, null=True)
    shop_photo = models.CharField(max_length=255, blank=True, null=True)
    shop_logo = models.CharField(max_length=255, blank=True, null=True)
    createdate = models.DateTimeField(db_column='createDate')  # Field name made lowercase.
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblShop'


class Codes(models.Model):
    code_id = models.AutoField(primary_key=True)
    code_type = models.CharField(max_length=10, blank=True, null=True)
    code_name = models.CharField(max_length=255, blank=True, null=True)
    code_name_s = models.CharField(max_length=255, blank=True, null=True)
    code_name_e = models.CharField(max_length=255, blank=True, null=True)
    sequence = models.SmallIntegerField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblCode'


class CodeDetails(models.Model):
    code_detail_id = models.AutoField(primary_key=True)
    code_id = models.IntegerField(blank=True, null=True)
    code_parent_id = models.IntegerField(blank=True, null=True)
    code_key = models.CharField(max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')
    code_detail_name = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)
    code_detail_name_s = models.CharField(max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    code_detail_name_e = models.CharField(max_length=1000, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                          null=True)
    code_detail_photo = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                         null=True)
    code_detail_icon = models.CharField(max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True,
                                        null=True)
    sequence = models.SmallIntegerField()
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblCodeDetail'


class Tables(models.Model):
    table_id = models.AutoField(primary_key=True)
    table_key = models.CharField(max_length=10)
    table_name = models.CharField(max_length=255, blank=True, null=True)
    table_name_e = models.CharField(max_length=255, blank=True, null=True)
    table_seat = models.SmallIntegerField()
    table_shape = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    time_period = models.CharField(max_length=20, blank=True, null=True)
    charge = models.IntegerField(blank=True, null=True)
    shop = models.CharField(max_length=50, blank=True, null=True)
    table_photo = models.CharField(max_length=255, blank=True, null=True)
    table_icon = models.CharField(max_length=255, blank=True, null=True)
    sequence = models.SmallIntegerField()
    status = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'tblTable'


class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Subjects(models.Model):
    id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE, default=1)  # need to give defauult course
    staff_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50)
    profile_pic = models.FileField()
    address = models.TextField()
    course_id = models.ForeignKey(Courses, on_delete=models.DO_NOTHING, default=1)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Attendance(models.Model):
    # Subject Attendance
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class AttendanceReport(models.Model):
    # Individual Student Attendance
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    stafff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class ESCPOSManager:
    def __init__(self):
        self.command_buffer = b""  # Create an instruction buffer.

    def add_command(self, command):
        self.command_buffer += command

    def send_command(self):
        esc_data = self.command_buffer
        return esc_data

    def Prefix_command(self):
        random_id = ''.join(random.choices(string.digits, k=6))
        prefix_command = bytes([0x03, 0x00]) + random_id.encode('utf-8') + b"\x00"
        # Construct print instructions for a specific format
        self.add_command(prefix_command)

    def print_text(self, text):
        text_command = text.encode('utf-8')  # 将文本编码为字节串
        self.add_command(text_command)

    def print_barcode(self, barcode_data, barcode_type):
        barcode_types = {
            'CODE39': b"\x1Dk\x04",
            'CODE128': b"\x1Dk\x49",
            # 添加其他条码类型和相应的 ESC/POS 指令
        }
        if barcode_type in barcode_types:
            barcode_command = barcode_types[barcode_type] + barcode_data.encode('utf-8')
            self.add_command(barcode_command)
        else:
            print("Invalid barcode type")

    def set_font_size(self, size):
        """
        设置字体大小
        :param size: 字体大小，可选值为 1 到 8
        :return: 对应的 ESC/POS 指令
        """
        if size < 1 or size > 128:
            raise ValueError("Font size should be between 1 and 8")
        font_size = bytes([0x1B, 0x21, size - 1])
        # 计算对应的字体放大倍数指令
        # ESC ! n 设置字体大小，n的值为字体高度和宽度放大的倍数，取值范围是 0-7
        # 具体倍数需要根据打印机规格和支持的倍数来调整
        self.add_command(font_size)

    def set_font_big_size(self, big_size):
        """
        设置字体大小
        :param big_size:
        :param size: 字体大小，可选值为 1 到 8
        :return: 对应的 ESC/POS 指令
        """
        if big_size < 1 or big_size > 113:
            raise ValueError("Font size should be between 1 and 8")
        font_big_size = bytes([0x1D, 0x21, big_size - 1])
        self.add_command(font_big_size)

    def print_qr_code(self, data, size=8, error_correction='M'):
        """
        打印 QR Code
        :param data: 要编码的数据
        :param size: QR Code 尺寸，默认为8
        :param error_correction: 纠错级别，可选值为 L（7%），M（15%），Q（25%），H（30%），默认为 M
        :param printer: ESC/POS 打印机对象
        """
        # 纠错级别对应的 ESC/POS 指令
        error_correction_levels = {'L': 48, 'M': 49, 'Q': 50, 'H': 51}
        if error_correction not in error_correction_levels:
            raise ValueError("Error correction should be 'L', 'M', 'Q', or 'H'")

        # 设置 QR Code 的尺寸和纠错级别
        qr_code_size = bytes([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, size])
        qr_code_error_Levels = bytes(
            [0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x45, error_correction_levels[error_correction]])
        qr_code_data_seting = bytes([0x1D, 0x28, 0x6B, len(data) + 3, 0x00, 0x31, 0x50, 0x30])
        real_data = data.encode('utf-8')
        get_qrcode_data = bytes([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x51, 0x30])
        print_qrcode_seting = bytes([0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x52, 0x30])
        qrcode_data = qr_code_size + qr_code_error_Levels + qr_code_data_seting + real_data + print_qrcode_seting + get_qrcode_data
        self.add_command(qrcode_data)
        # 传输数据到打印机
        # qr_code_data = bytes([0x1D, 0x28, 0x6B, len(data) + 3, 0x00, 0x31, 0x50, error_correction_levels[error_correction]])
        # qr_code_data += data.encode('utf-8')

    def cut_paper(self):
        self.add_command(b"\x1D\x41\x00")  # 切纸指令

    def feed_lines(self, num_lines):
        self.add_command(b"\x1Bd" + bytes([num_lines]))  # 进纸指令

    def Print_barcode(self, barcode_data, set_hri_position=2, Set_Barcode_height=64, set_barcode_width=2,
                      set_barcode_type="CODE128"):
        Set_barcode_types = {
            'CODE39': b"\x1Dk\x04",
            'CODE128': b"\x1Dk\x49",
            # 添加其他条码类型和相应的 ESC/POS 指令
        }
        Barcode_hri = bytes([0x1d, 0x48, set_hri_position])
        Barcode_height = bytes([0x1d, 0x68, Set_Barcode_height])
        Barcode_width = bytes([0x1d, 0x77, set_barcode_width])
        pass

    def set_line_space(self, line_space_dots):
        """
        设置行间距为  [ Line_space_dots × 纵向或横向移动单位] 点
        :param line_space_dots: 00 ≤ n ≤ 255
        :return:
        """
        self.add_command(b"\x1b\x33" + bytes([line_space_dots]))  # 设置行间距

    def set_default_line_space(self):
        self.add_command(b"\x1b\x32")

    def set_print_position(self, nl, nH):
        self.add_command(b"\x1b\x24" + bytes([nl, nH]))

    def set_print_bold(self, bold="bold"):
        """
        bold = normal, it is not bold,
        bold = bold ,it is bold the font
        :param bold:
        :return:
        """
        if bold == "bold":
            bold_number = 1
        elif bold == "normal":
            bold_number = 0
        else:
            print("you type wrong values,pls choose bold or normal")
        self.add_command(b"\x1b\x45" + bytes([bold_number]))

    def set_alignment(self, align="left"):
        if align == "left":
            self.add_command(b"\x1b\x61\x00")
        elif align == "center":
            self.add_command(b"\x1b\x61\x01")
        elif align == "right":
            self.add_command(b"\x1b\x61\x02")


@receiver(post_save, sender=CustomUser)
# Now Creating a Function which will automatically insert data in HOD, Staff or Student
def create_user_profile(sender, instance, created, **kwargs):
    # if Created is true (Means Data Inserted)
    if created:
        # Check the user_type and insert the data in respective tables
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        if instance.user_type == 3:
            Students.objects.create(admin=instance, course_id=Courses.objects.get(id=1),
                                    session_year_id=SessionYearModel.objects.get(id=1), address="", profile_pic="",
                                    gender="")


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    if instance.user_type == 2:
        instance.staffs.save()
    if instance.user_type == 3:
        instance.students.save()
