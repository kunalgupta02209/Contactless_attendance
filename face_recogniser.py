import cv2
import numpy as np
from keras.models import load_model
from db_util import database
import pymongo
from pymongo.errors import DuplicateKeyError

class face:
    def __init__(self):
        self.cascade=cv2.CascadeClassifier('faces.xml')
        self.x=None
        self.y=None
        self.w=None
        self.h=None

    def detectFace(self,img):
        cropped=None
        grey=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces=self.cascade.detectMultiScale(grey,1.3,5)
        cropped=[]
        coor=[]
        for (self.x,self.y,self.w,self.h) in faces:
            cropped.append(img[self.y:self.y+self.h,self.x:self.x+self.w])
            coor.append([self.x,self.y,self.w,self.h])
        return cropped,coor


class emb:
    def __init__(self):
        self.model=load_model('facenet_keras.h5')
    def calculate(self,img):
        return self.model.predict(img)[0]

data=database()

label=None
people=data.read_employee_dict()

e=emb()
fd=face()

print('attendance till now is ')
data.view()

model=load_model('face_reco2.MODEL')


cap=cv2.VideoCapture(0)
ret=True
# test()
while ret:
    ret,frame=cap.read()
    frame=cv2.flip(frame,1)
    det,coor=fd.detectFace(frame)

    if(det is not None):
        for i in range(len(det)):
            detected=det[i]
            k=coor[i]
            f=detected
            detected=cv2.resize(detected,(160,160))
            #detected=np.rollaxis(detected,2,0)
            detected=detected.astype('float')/255.0
            detected=np.expand_dims(detected,axis=0)
            feed=e.calculate(detected)
            feed=np.expand_dims(feed,axis=0)
            prediction=model.predict(feed)[0]

            result=int(np.argmax(prediction))
            if(np.max(prediction)>.70):
                for i in people.keys():
                    if(result==i):
                        label=people[i]['_id']
                        data.update(label)
                        label=people[i]['name']
            else:
                label='unknown'


            cv2.putText(frame,label,(k[0],k[1]),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
            cv2.rectangle(frame,(k[0],k[1]),(k[0]+k[2],k[1]+k[3]),(252,160,39),3)
            cv2.imshow('onlyFace',f)
    cv2.imshow('frame',frame)
    if(cv2.waitKey(1) & 0XFF==ord('q')):
        break
cap.release()
cv2.destroyAllWindows()
data.export_csv()
