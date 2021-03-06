import cv2
import numpy as np
import os

from db_util import database
pic_no=0
print('Enter the name of the person for enrollment')
name=input()

db = database()

fa=cv2.CascadeClassifier('faces.xml')
cap=cv2.VideoCapture(0)
ret=True
img_arr = []
while ret:
    ret,frame=cap.read()
    frame=cv2.flip(frame,1)
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces=fa.detectMultiScale(gray,1.3,5)
    for (x,y,w,h) in faces:
        cropped=frame[y:y+h,x:x+w]
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2,cv2.LINE_AA)
        pic_no=pic_no+1
        img_arr.append(cropped)
    cv2.imshow('frame',frame)
    cv2.waitKey(100)

    if(pic_no>50):
    	break
db.write_employee_to_db(name,img_arr)

cap.release()
cv2.destroyAllWindows()
