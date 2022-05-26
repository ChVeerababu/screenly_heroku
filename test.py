
import pymysql as p
import os
import requests
from dotenv import load_dotenv
import time
import requests
load_dotenv()

host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')
key=os.environ.get('API_KEY')
lat=os.environ.get('LATITUDE')
lng=os.environ.get('LONGTITUDE')


con=p.connect(host=host,user=user,password=password,database=database)
cur=con.cursor()

def get_image(re):

    query1="select qr_ads_image_path from qr_ads_master where qr_ads_id = {}".format(re)

    cur.execute(query1)

    img = cur.fetchone()[0]

    return img

def get_id(ad,r,account,site):
    cur.execute("select id from qr_code_rule_engine where condition_id={} and rule_id={} and qr_code_id={} and site_id={}".format(ad,r,account,site))
    id_main=cur.fetchone()
    return id_main


def get_latlong(site):
    query="select latitude,longitude from account where accountId={}".format(site)
    cur.execute(query)
    latlng=cur.fetchone()
    return float(latlng[0]),float(latlng[1])

    

def current_weather(lat,lng):
    
    api="https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=hourly,daily&appid={}".format(lat,lng,key)

    r=requests.get(api)

    data=r.json()

    c=data['current']

    return c


def get_temp(site,account,r):

    geo=get_latlong(site)
    lat,lng=geo[0],geo[1]
    w=current_weather(lat,lng)
    F=float(w['temp'])

    c=int(F-273.15)

    if 1<=c<=14:
        ad=4
        re=get_id(ad,r,account,site)
 

    elif 15<=c<=35:
        ad=5
        re=get_id(ad,r,account,site)
  
        
    else:
        ad=6
        re=get_id(ad,r,account,site)
    return re

    
def get_timing(site,account,r):

    tm=time.strftime('%p')

    if tm=='AM':
        ad=2
        re=get_id(ad,r,account,site)


    else:
        ad=3
        re=get_id(ad,r,account,site)
    return re


def get_temp_time(site,account,r):
    tme=get_timing(site,2,2)[0]
    tmp=get_temp(site,3,3)[0]
    if tme==2 and tmp==4:
        ad=7
        re=get_id(ad,r,account,site)
    elif tme==2 and tmp==5:
        ad=8
        re=get_id(ad,r,account,site)
    elif tme==2 and tmp==6:
        ad=9
        re=get_id(ad,r,account,site)
    elif tme==3 and tmp==4:
        ad=10
        re=get_id(ad,r,account,site)
    elif tme==3 and tmp==5:
        ad=11
        re=get_id(ad,r,account,site)
    else :
        ad=12
        re=get_id(ad,r,account,site)

    return re



def get_humidity(site,account,r):
    geo=get_latlong(site)
    lat,lng=geo[0],geo[1]
    w=current_weather(lat,lng)
    c=w['humidity']

    if 1<=c<=30:
        ad=13
        re=get_id(ad,r,account,site)
 

    elif 31<=c<=60:
        ad=14
        re=get_id(ad,r,account,site)
  
        
    else:
        ad=15
        re=get_id(ad,r,account,site)
    return re


def get_weekdays(site,account,r):

    tm=time.strftime('%A')

    if tm=='Monday':
        ad=16
        re=get_id(ad,r,account,site)
    elif tm=='Tuesday':
        ad=17
        re=get_id(ad,r,account,site)
    elif tm=='Wednesday':
        ad=18
        re=get_id(ad,r,account,site)
    elif tm=='Thursday':
        ad=19
        re=get_id(ad,r,account,site)
    elif tm=='Friday':
        ad=20
        re=get_id(ad,r,account,site)
    elif tm=='Saturday':
        ad=21
        re=get_id(ad,r,account,site)
    else:
        ad=22
        re=get_id(ad,r,account,site)
    return re


