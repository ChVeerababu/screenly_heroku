import pymysql as p
import os
import requests
from dotenv import load_dotenv
import time
#import query as q

load_dotenv()

host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')



con=p.connect(host=host,user=user,password=password,database=database)
cur=con.cursor()

def get_image(re):

    query1="select qr_ads_image_path from qr_ads_master where qr_ads_id = {}".format(re)

    cur.execute(query1)

    img = cur.fetchone()[0]


    return img

# def get_latlong(site):
    
#     query="select latitude,longitude from account where accountId={};".format(site)
#     cur.execute(query)
#     lat=eval(cur.fetchone()[0])
#     lng=eval(cur.fetchone()[1])
#     return lat,lng

    

# def current_temp(lat,lng):
    
#     api="https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=hourly,daily&appid={}".format(lat,lng,key)

#     r=requests.get(api)

#     data=r.json()

#     F=float(data['current']['temp'])

#     c=F-273.15

#     return c


# def get_temp(r):

#     geo=get_latlong(site)
#     lat,lng=geo[0],geo[1]
#     print(lat,lng)
#     print(type(lat))

#     c=current_temp(lat,lng)

#     if 20<c>28:
#         ad=4
#         return get_image(r)

#     elif 28<=c>=35:
#         ad=5
#         return get_image(r)
        
#     else:
#         ad=6
#         return get_image(site,account,ad,rule)

    
# def get_timing(site,account,ad,rule):

#     tm=time.strftime('%p')

#     if tm=='AM':
#         ad=2

#         return get_image(site,account,ad,rule)

#     else:
#         ad=3
#         return get_image(site,account,ad,rule)



