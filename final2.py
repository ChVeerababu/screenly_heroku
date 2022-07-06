import numpy as np
import cv2
import time
from switch import TestThreading
import os
from PIL import Image
from watch import Watcher,TimeLimit
import requests,json
from requests.structures import CaseInsensitiveDict
import requests
from asset import get_dict
import pymysql
from datetime import datetime
from aws_rds import get_device,get_latlng,get_rule_id,get_asset_id,get_asset,get_cam,insert_details
from facelib import FaceDetector, AgeGenderEstimator
face_detector = FaceDetector()
age_gender_detector = AgeGenderEstimator()
from flask import Flask,request

app = Flask(__name__)



w = Watcher(0)
t = TimeLimit()
key=os.getenv('KEY')


def pin(status,no,ip):
    #url = os.getenv("RPI_PINS_API")+ status
    url = 'http://'+ip+':8083/api/pins/'+status
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data = json.dumps({"pin":no})
    resp = requests.post(url, headers=headers, data=data)
    return resp.status_code





def temp(lat,lng,rng):
    day=time.strftime("%p")
    url = os.getenv('URL').format(lat,lng,key)
    c =int(float(requests.get(url).json()['current']['temp'])-273.15)


    if 1 <= c <= rng:
        a = 'R1'
        
    elif 1+rng <= c <= 2 * rng:
        a = 'R2'
        
    else:
        a = 'R3'
    
    return day+a

@app.route('/')
def sample():
    return "This application running"



@app.route('/ads', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        data = request.form.get('metadata', '')
        od = eval(data)
        print(od,type(od))
        od_list = od['objDetectionList']
        print(od_list)
        camera_id = od['cameraId']
        print(camera_id)
        cams = get_cam(camera_id)
        device_id = cams[1]
        device_data = get_device(device_id)
        latlng = get_latlng(device_data[2])
        print(od_list)
        npimg = np.fromfile(request.files['imagedata'], np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        print(type(img))

        count = len(od_list)


        watch = w.variable < count
        print(watch,w.variable,count)
        
                
        if count >= 1 and watch:
            try:
                if eval(device_data[-2]):
                    try:
                        faces, boxes, scores, landmarks = face_detector.detect_align(img)
                        genders, ages = age_gender_detector.detect(faces)
                        #pin('on',[21,26],device_data[-1])
                        z = tuple(zip(genders,ages))
                        print("this is z",z)
                        g = genders.count('Male') > genders.count('Female')
                        print(g)
                        ages_males = [ y for x, y in z if x  == 'Male' ]
                        print(ages_males)
                        m_classifications = [(i//device_data[-3] + 1) for i in ages_males]
                        ages_females = [ y for x, y in z if x  == 'Female' ]
                        print(ages_females)
                        f_classifications = [(i//device_data[-3] + 1) for i in ages_females]

                                
                        if g:
                            print('its true')
                            m = max(m_classifications,key=m_classifications.count)
                            print(m)
                            r1=temp(latlng[0],latlng[1],device_data[3])+'MC'+str(m)
                                    
                        else:
                            print('its false')
                            f = max(f_classifications,key=f_classifications.count)
                            r1=temp(latlng[0],latlng[1],device_data[3])+'FC'+str(f)
                    except Exception as e:
                        return "no faces detected"

                else:
                    z=None
                    r1 = temp(latlng[0],latlng[1],device_data[3])

                print(r1)
                r_id = get_rule_id(r1)
                print(r_id)
                a_id = get_asset_id(device_data[2],r_id,device_data[1],device_id)
                asset = get_asset(a_id)
                print(asset)
                print(device_data[0])
                data_dict = get_dict(device_data[0],asset)
                print(data_dict)

                mimetype = str(data_dict['mimetype'])
                name = str(data_dict['name'])
                duration = int(data_dict['duration'])
                print(name,mimetype)
                TestThreading(asset,device_data[0])
                insert_details(device_data[2],device_data[0],name,mimetype,count,z,r1)
                time.sleep(duration+1)
                return "its done"
            except Exception as e:
                return str(e)
    return "no detection occured"




