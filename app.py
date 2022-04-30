import json
import pymysql as p
import time
import pandas as pd
import threading
import os
from flask import Flask, render_template, flash, request, redirect, url_for,send_file
from test import get_image
#,get_timing,get_temp
from dotenv import load_dotenv


# load data from .env file
load_dotenv()

host = os.environ.get('RDS_URL')
user = os.environ.get('RDS_USER')
password = os.environ.get('RDS_PASS')
database = os.environ.get('RDS_DB')


# take one record for each hour using list
rest=[]

app=Flask(__name__)


# getting data from .env file
account = os.environ.get('QRCODE_ACCOUNT')
site =os.environ.get('QRCODE_SITE')



# main api calling through

@app.route('/<int:site>/<int:account>', methods=['GET'])
def index(site,account):
    print("user_agent: ",request.user_agent)
    print("dir:",dir(request.user_agent))

    tm=time.strftime("%Y-%m-%d %H-%M-%S")
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        data={'ip': request.environ['REMOTE_ADDR'],'timestamp':tm,'browser':request.user_agent._browser, 'os':request.user_agent._platform }
        a = [tm[:10],tm[11:13],data['ip'],data['browser'],data['os']]
    else:
        data={'ip': request.environ['HTTP_X_FORWARDED_FOR'],'timestamp':tm,'browser':request.user_agent._browser, 'os':request.user_agent._platform }
        a = [tm[:10],tm[11:13],data['ip'],data['browser'],data['os']] 
    print(a)
    print(data)
    threading.Thread(target=dbstdata(a,data,site,account,tm)).start()
    
    r=rule(site,account)
    print("rule:",r)
    
    '''try:
        res = get_image(r)
            
    except:'''
        
    res = "https://wallpaperaccess.com/full/57166.jpg"


    return render_template('index.html',res = res,site_name="IVIS")



# store hourwise data using funcion
def dbstdata(a,data,site,account,tm):
    con=p.connect(host=host,user=user,password=password,database=database)
    cur=con.cursor()

    
    sql="insert into qr_user_data(site_id,qr_code_id,scanned_date,hour,ipaddress,user_browser,user_device_os)values(%s,%s,%s,%s,%s,%s,%s)"
    sqls="insert into qr_hourly_user_data(site_id,qr_code_id,scanned_date,hour,VISITS,UNIQUES,user_browser,user_device_os,ipaddress)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.executemany("select * from qr_hourly_user_data where scanned_date=%s and hour=%s and site_id=%s and qr_code_id=%s order by scanned_date and hour",[(tm[:10],tm[11:13],site,account)])
    check=cur.fetchall()

    cur.executemany(sql,[(site,account,a[0],a[1],a[2],a[-2],a[-1])])
    con.commit() 


    if len(check)==0:
        rest.clear()
    else:
        print(rest)
        mn=[tm[:10],tm[11:13],eval(check[-1][5]),eval(check[-1][6]),eval(check[-1][-3]),eval(check[-1][-2]),eval(check[-1][-1])]
        rest.append(mn)
        print(mn)
        


    if len(rest)==0:
        v,u=1,1
        mn=[tm[:10],tm[11:13],v,u,{data['browser']:1},{data['os']:1},[data['ip']]]
        rest.append(mn)
        if len(check)==0:
            cur.executemany(sqls,[(site,account,rest[-1][0],rest[-1][1],str(rest[-1][2]),str(rest[-1][3]),str(rest[-1][-3]),str(rest[-1][-2]),str(rest[-1][-1]))])
            con.commit()


    else:
        

        rest[-1][2]+=1
        
        if a[2] not in rest[-1][-1]:
            rest[-1][3]+=1
            rest[-1][-1].append(a[2])
        if a[3] in rest[-1][4]:
            rest[-1][4][a[3]] += 1
        else:
            rest[-1][4][a[3]] = 1
        if a[-1] in rest[-1][-2]:
            rest[-1][-2][a[-1]] += 1
        else:
            rest[-1][-2][a[-1]] = 1

        cur.executemany("update qr_hourly_user_data set site_id=%s,qr_code_id=%s,VISITS=%s,UNIQUES=%s,user_browser=%s,user_device_os=%s,ipaddress=%s where scanned_date=%s and hour=%s and site_id=%s and qr_code_id=%s order by scanned_date and hour desc limit 1",\
        [(site,account,str(rest[-1][2]),str(rest[-1][3]),str(rest[-1][-3]),str(rest[-1][-2]),str(rest[-1][-1]),tm[:10],tm[11:13],site,account)])
        con.commit()


# connect database here
def db():
    dbcon=p.connect(host=host,user=user,password=password,database=database)
    return dbcon.cursor()
# query execution block
def query_db(query, args=(), one=False):
    cur = db()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.connection.close()
    return (r[0] if r else None) if one else r

# rule for ads
def rule(site,account):
    cur=db()
    cur.execute("select id from qr_code_rule_engine where site_id={} and qr_code_id={}".format(site,account))
    rule=cur.fetchone()[0]
    return rule


# sub api calling thrigh endpoints like /hr/result
@app.route('/<int:site>/<int:account>/hr/result', methods=['GET'])
def res(site,account):
    
    my_query = query_db("select * from qr_hourly_user_data where site_id={} and qr_code_id={}".format(site,account))

    json_output = json.dumps(my_query)
    
    jsn=eval(json_output)

    d={}
    date=[]
    l=[]
    for i in jsn:
        if i['scanned_date'] in date:
            l.append(i)
            d[i['scanned_date']]=l
            del i['scanned_date']
            del i['ipaddress']
        else:
            date.append(i['scanned_date'])
            d[i['scanned_date']]=[i]
            del i['scanned_date']
            del i['ipaddress']
            l=[i]
    dfc=json.dumps(d,indent=4)
    return dfc

# calling api's
if __name__=="__main__":
    app.run()