# from channels.auth import login, logout
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import datetime
import time
import base64
import hashlib
import socket
from django.utils.encoding import uri_to_iri
from django.core import serializers
from rest_framework import status
from rest_framework.response import Response

from InfinyRealty_app.EmailBackEnd import EmailBackEnd
from InfinyRealty_app.models import Users, UserInfo, Ranks, AccessRights, LoginHist

# import urllib library
from urllib.request import urlopen

# import json
import json

# import sll
import ssl
import certifi

from django.conf import settings

#def loginPage(request):
#    return render(request, 'login.html')1


def login(request):
    request.session['username'] = ""
    return render(request, 'login.html')

def logout(request):
    request.session['username'] = ""
    return render(request, 'login.html')

def checkLogin(request):
    username = request.GET.get('valUsername')
    password = request.GET.get('valPassword')
    #username = "admin"
    #password = "password"
    hashed_password = hash_password(password)

    try:
        users = Users.objects.using('infinyrealty').filter(username=username).filter(password=hashed_password).filter(isactive=1)
        if users:
            request.session['loginid'] = users[0].loginid
            request.session['username'] = users[0].username
            request.session['hashed_password'] = hashed_password
            request.session['loginnamedesc'] = users[0].loginnamedesc
            request.session['email'] = users[0].email
            request.session['team'] = users[0].team
            request.session['rank'] = users[0].rank
            request.session['lang'] = "tc"
            ranks = Ranks.objects.using('infinyrealty').filter(rank=users[0].rank)
            request.session['rankdesc'] = ranks[0].rankdesc
            recordid = users[0].id
            loginid = users[0].loginid
            user = Users.objects.using('infinyrealty').get(id=recordid)
            user.loginid = loginid
            user.logincount = users[0].logincount + 1
            user.lastlogindate = datetime.datetime.today()
            user.save(using='infinyrealty')

            accessrights = AccessRights.objects.using('infinyrealty').filter(username=username).filter(approved=1)
            accessrightslist = []
            for ar in accessrights:
                accessrightslist.append(ar.functionid)
            request.session['accessright'] = accessrightslist
            request.session['username_org'] = users[0].username

            request.session['httpreferer1'] = request.META.get('HTTP_ORIGIN')
            request.session['httpuseragent'] = request.META.get('HTTP_USER_AGENT')
            loginhist = LoginHist()
            loginhist.loginid = users[0].loginid
            loginhist.username = users[0].username
            loginhist.ip = request.META.get('REMOTE_ADDR')
            loginhist.clientip = get_client_ip_address()
            loginhist.clientinfo = request.META.get('HTTP_USER_AGENT')
            loginhist.servername = request.META.get('SERVER_NAME')
            loginhist.lastlogin = datetime.datetime.today()
            loginhist.logintype = 'Live'
            loginhist.save(using='infinyrealty')
            return JsonResponse({'message': 'Login Success'})
        else:
            return JsonResponse({'message': 'Login Fail'})
    except Exception as e:
        return JsonResponse({'message': 'Login Fail'})

def doLogin(request):
    request.session['httpreferer'] = request.META.get('HTTP_ORIGIN')
    username = request.GET.get('valUsername')
    password = request.GET.get('valPassword')
    hashed_password = hash_password(password)
    #print("Hashed Password: ", hashed_password)

    users = Users.objects.using('infinyrealty').filter(username=username).filter(password=hashed_password).filter(isactive=1)
    if users:
        request.session['loginid'] = users[0].loginid
        request.session['username'] = users[0].username
        request.session['loginnamedesc'] = users[0].loginnamedesc
        request.session['email'] = users[0].email
        request.session['team'] = users[0].team
        request.session['rank'] = users[0].rank
        request.session['lang'] = "tc"
        recordid = users[0].id
        loginid = users[0].loginid
        user = Users.objects.using('infinyrealty').get(id=recordid)
        user.loginid = loginid
        user.logincount = users[0].logincount + 1
        user.lastlogindate = datetime.datetime.today()
        user.save(using='infinyrealty')

        accessrights = AccessRights.objects.using('infinyrealty').filter(username=username).filter(approved=1)
        accessrightslist = []
        for ar in accessrights:
            accessrightslist.append(ar.functionid)
        request.session['accessright'] = accessrightslist
        request.session['username_org'] = users[0].username

        request.session['httpreferer1'] = request.META.get('HTTP_ORIGIN')
        request.session['httpuseragent'] = request.META.get('HTTP_USER_AGENT')
        loginhist = LoginHist()
        loginhist.loginid = users[0].loginid
        loginhist.username = users[0].username
        loginhist.ip = request.META.get('REMOTE_ADDR')
        loginhist.clientip = get_client_ip_address()
        loginhist.clientinfo = request.META.get('HTTP_USER_AGENT')
        loginhist.servername = request.META.get('SERVER_NAME')
        loginhist.lastlogin = datetime.datetime.today()
        loginhist.logintype = 'Live'
        loginhist.save(using='infinyrealty')
        return redirect('home')
    else:
        return JsonResponse({'message': 'Login Fail'})

def accessdenied(request):
    context = {
        "username": request.session.get('username'),
    }
    return render(request, 'common_template/access_denied.html')


def undercon(request):
    context = {
        "username": request.session.get('username'),
    }
    return render(request, 'common_template/under_construction.html')

def get_user_details(request):
    if request.user != None:
        return HttpResponse("User: " + request.user.email + " User Type: " + request.user.user_type)
    else:
        return HttpResponse("Please Login First")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

def GetUserInfo(uid):
    if uid == "admin":
        directoryItem = "xxxx"
    else:
        directoryItem = "X"
    return directoryItem

def get_client_ip_address():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to a remote server (doesn't matter which)
        sock.connect(("8.8.8.8", 80))

        # Get the local IP address of the socket
        ip_address = sock.getsockname()[0]
        return ip_address
    except Exception as e:
        print("Error retrieving IP address:", str(e))
    finally:
        # Close the socket
        sock.close()

def hash_password(password):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Convert the password to bytes and hash it
    sha256_hash.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = sha256_hash.hexdigest()

    return hashed_password