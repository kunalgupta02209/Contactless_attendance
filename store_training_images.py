import cv2
import numpy as np
import os

from db_util import database
pic_no=0
print('Enter the name of the person for enrollment')
name=input()
print('Enter the Unique ID of the person for enrollment')
UID=input()
try:
    os.mkdir('people')
except:
    pass

db = database()

dir_list = os.listdir('people')
if len(dir_list) == 0:
    no = 0
else:
<<<<<<< HEAD
    no = int(dir_list[-1].split('_')[0])
=======
    no = int(dir_list[-1].split('_')[0])+1
>>>>>>> e1f7c598c6863fe2a55aa80995bc3b3b410b03b8
name = str(no)+'_'+name

db.write_employee_to_db(name,UID)
os.makedirs('people/'+name)
fa=cv2.CascadeClassifier('faces.xml')
cap=cv2.VideoCapture(0)
ret=True
while ret:
    ret,frame=cap.read()
    frame=cv2.flip(frame,1)
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces=fa.detectMultiScale(gray,1.3,5)
    for (x,y,w,h) in faces:
        cropped=frame[y:y+h,x:x+w]
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2,cv2.LINE_AA)
        pic_no=pic_no+1
        cv2.imwrite('people/'+name+'/'+str(pic_no)+'.jpg',cropped)
    cv2.imshow('frame',frame)
    cv2.waitKey(100)

    if(pic_no>50):
    	break


cap.release()
cv2.destroyAllWindows()
