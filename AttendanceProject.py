import re
from tabnanny import check
import requests
import json
import cv2
import numpy as np
import face_recognition
import os
from genericpath import isfile
from datetime import date 

#FUNCTIONS
def createImageFile():
    images=[]
    uID = []
    myList=os.listdir(path)
    for cl in myList:
        curImg=cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        uID.append(int(os.path.splitext(cl)[0]))
    return images,uID

def findEncodings(images):
    encodeList=[]
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def ATTENDANCE_PROCESS(S,uID,EncodeListKnown):
    cap=cv2.VideoCapture(0)
    present_uID = []
    while True:
        success, img=cap.read()
        imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

        for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
            matches=face_recognition.compare_faces(EncodeListKnown,encodeFace)
            faceDis=face_recognition.face_distance(EncodeListKnown,encodeFace)
            #print(faceDis)
            matchIndex=np.argmin(faceDis)
            check_uID = uID[matchIndex]
        
            if check_uID in present_uID :
                y1,x2,y2,x1=faceLoc
                y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img,"ALREADY PRESENT",(x1+6,y2-6),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),2) 

            elif matches[matchIndex]:
                print("Match found!")
                payload = get_payload(check_uID)
                status = camera_give_attendance(S,payload)
                if status == 201 : 
                    present_uID.append(check_uID)
                    y1,x2,y2,x1=faceLoc
                    y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img,str(check_uID),(x1+6,y2-6),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2) 

            else:
                # print("Error Occured : STATUS CODE"+str(status))
                y1,x2,y2,x1=faceLoc
                y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4
                cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img,"NOT RECOGNIZED",(x1+6,y2-6),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2) 

        cv2.imshow('Webcam',img)
        key = cv2.waitKey(5)
        if key == ord('q'):
            camera_logout(S,userName)
            cv2.destroyAllWindows();
            break

def camera_login(S,userName,password):
    payload = {'userName': userName,'password': password}
    login = S.post(camera_login_url,data=payload)
    print(login.status_code)
    data = login.json()
    studentList = data['studentList']
    for student_data in studentList :
        image_link = student_data['image']
        uID = student_data['uID']
        with open(f"{os.getcwd()}\\{uID}.jpg",'wb') as f:
            image = requests.get(image_link)            
            f.write(image.content)
            print("imageAdded")
    return studentList

def camera_give_attendance(S,payload):
    headers = {
    'Content-Type': 'application/json'
    }
    r = S.post(camera_attendance_url,headers=headers,data=json.dumps(payload))
    print(r.content)
    print(r.status_code)
    return (r.status_code)

def camera_logout(S,userName):
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    logout = S.post(camera_logout_url,data={'userName':userName})
    print(f"Logged_out : {logout}" )

def get_payload(uID):
    payload = {}
    for i in studentList:
        if i['uID'] == str(uID):
            payload = { "date" : str(date.today()) ,
                        "schoolId" : i['schoolId'],
                        "studentData" : i}
    return payload


cwd = os.getcwd()
path = cwd + "\\images"
try:
    os.chdir(path)
except OSError as err:
    os.mkdir(path)
    os.chdir(path)

camera_login_url = "https://api-govschool.herokuapp.com/camera/login"
camera_attendance_url = "https://api-govschool.herokuapp.com/camera/attendance"
camera_logout_url ="https://api-govschool.herokuapp.com/logout" 

if __name__ == "__main__":
    with requests.Session() as S :
        # Giving auth to Camera login endpoint and receving info about the students
        userName =  'CAM70015601'# input("Enter camera UserName : ") 
        password =  'Nvxgb617121@'# input("Enter password : ") 

        # studentList = camera_login(S,userName,password) 

        images,uID = createImageFile() 
        EncodeListKnown=findEncodings(images)
        print('Encoding Complete!')

        ATTENDANCE_PROCESS(S,uID,EncodeListKnown)