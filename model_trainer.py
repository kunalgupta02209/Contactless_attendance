from keras.layers import Dense,Activation
from keras.layers import LeakyReLU
from keras.models import Sequential
import cv2
import numpy as np
import os
from keras.models import load_model
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from bson.codec_options import CodecOptions
import pytz
from db_util import database

class emb:
    def __init__(self):
        self.model=load_model('facenet_keras.h5')
    def calculate(self,img):
        return self.model.predict(img)[0]

class DenseArchs:
    def __init__(self,classes):
        print('training initiated')
        self.model=Sequential()
        self.classes=classes
    def arch(self):
        self.model.add(Dense(64,input_dim=128))
        self.model.add(LeakyReLU(alpha=0.1))
        self.model.add(Dense(32))
        self.model.add(LeakyReLU(alpha=0.1))
        self.model.add(Dense(16))
        self.model.add(LeakyReLU(alpha=0.1))
        self.model.add(Dense(self.classes))
        self.model.add(Activation('softmax'))

        return self.model
db = database()
data_training = db.read_images_for_training()

n_classes= len(data_training.keys())

e=emb()
arc=DenseArchs(n_classes)
face_model=arc.arch()

x_data=[]
y_data=[]

learning_rate=0.01
epochs=27
batch_size=32


for y, images in data_training.items():
    for image in images:
        img=cv2.resize(image,(160,160))
        img=img.astype('float')/255.0
        img=np.expand_dims(img,axis=0)
        embs=e.calculate(img)
        x_data.append(embs)
        y_data.append(y)


x_data=np.array(x_data,dtype='float')
y_data=np.array(y_data)
y_data=y_data.reshape(len(y_data),1)
x_train,x_test,y_train,y_test=train_test_split(x_data,y_data,test_size=0.1,random_state=77)
y_train=to_categorical(y_train,num_classes=n_classes)
y_test=to_categorical(y_test,num_classes=n_classes)

o=Adam(lr=learning_rate,decay=learning_rate/epochs)
face_model.compile(optimizer=o,loss='categorical_crossentropy')
face_model.fit(x_train,y_train,batch_size=batch_size,epochs=epochs,shuffle='true',validation_data=(x_test,y_test))
face_model.save('face_reco2.MODEL')
print(x_data.shape,y_data.shape)
