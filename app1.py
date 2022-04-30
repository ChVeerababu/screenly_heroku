import json
import pymysql as p
import time
import pandas as pd
import threading
import os
from flask import Flask, render_template, flash, request, redirect, url_for,send_file
from test import get_image


rest=[]

app=Flask(__name__)

host="database-1.czejdnwyu0eq.ap-south-1.rds.amazonaws.com"
user="root"
password="Ivisivis5"
database="ivigil_crm_us"



# main api calling through

@app.route('/<int:site>/<int:account>', methods=['GET'])
def index(site,account):
    print("user_agent_s: ",request.user_agent.string)
    print("user_agent_b: ",request.user_agent.browser)
    print("user_agent_l: ",request.user_agent.language)
    print("user_agent_p: ",request.user_agent.platform)
    print("directives:",dir(request.user_agent))

    tm=time.strftime("%Y-%m-%d %H-%M-%S")
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        data={'ip': request.environ['REMOTE_ADDR'],'timestamp':tm,'browser':request.user_agent.browser, 'os':request.user_agent.platform }
        a = [tm[:10],tm[11:13],data['ip'],data['browser'],data['os']]
    else:
        data={'ip': request.environ['HTTP_X_FORWARDED_FOR'],'timestamp':tm,'browser':request.user_agent.browser, 'os':request.user_agent.platform }
        a = [tm[:10],tm[11:13],data['ip'],data['browser'],data['os']] 

    #threading.Thread(target=dbstdata(a,data,site,account)).start()
    
    #r=rule(site,account)
    
    
    '''try:
        res = get_image(r)
            
    except:'''
        
    res = "https://wallpaperaccess.com/full/57166.jpg"


    return render_template('index.html',res = res,site_name="IVIS")



'''# store hourwise data using funcion
def dbstdata(a,data,site,account):
    tm=time.strftime("%Y-%m-%d %H-%M-%S")
    con=p.connect(host=host,user=user,password=password,database=database)
    cur=con.cursor()

    
    sql="insert into qr_user_data(site_id,qr_code_id,scanned_date,hour,ipaddress,user_browser,user_device_os)values(%s,%s,%s,%s,%s,%s,%s)"
    sqls="insert into qr_hourly_user_data(site_id,qr_code_id,scanned_date,hour,VISITS,UNIQUES,user_browser,user_device_os,ipaddress)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.executemany("select * from qr_hourly_user_data where scanned_date=%s and hour=%s and site_id=%s and qr_code_id=%s order by Date and Hour",[(tm[:10],tm[11:13],site,account)])
    check=cur.fetchall()

    cur.executemany(sql,[(site,account,a[0],a[1],a[2],a[-2],a[-1])])
    con.commit() 


    if len(check)==0:
        rest.clear()
    else:
        mn=[tm[:10],tm[11:13],eval(check[-1][5]),eval(check[-1][6]),eval(check[-1][3]),eval(check[-1][-2]),eval(check[-1][-1])]
        rest.append(mn)
        


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

        cur.executemany("update qr_hourly_user_data set site_id=%s,qr_code_id=%s,VISITS=%s,UNIQUES=%s,user_browser=%s,user_device_os=%s,ipaddress=%s where scanned_date=%s and hour=%s and site_id=%s and qr_code_id=%s order by DATE and HOUR desc limit 1",\
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
        if i['DATE'] in date:
            l.append(i)
            d[i['DATE']]=l
            del i['DATE']
            del i['IP']
        else:
            date.append(i['DATE'])
            d[i['DATE']]=[i]
            del i['DATE']
            del i['IP']
            l=[i]
    dfc=json.dumps(d,indent=4)
    return dfc'''

# calling api's
if __name__=="__main__":
    app.run()
