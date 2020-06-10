
import pymongo
import pandas as pd
from pymongo.errors import DuplicateKeyError
from bson.codec_options import CodecOptions
import pytz
from datetime import datetime as dt
from datetime import timedelta
timezone = 'Asia/Calcutta'
TIMEZONE = pytz.timezone(timezone)
mongodb_url = "mongodb+srv://muskanasmath:attendance123@attendance-db.4l4qt.gcp.mongodb.net/attendance-db?authSource=admin&replicaSet=atlas-qr4lca-shard-0&compressors=zlib&readPreference=primary&appname=MongoDB%20Compass&ssl=true"

class database:
    def __init__(self):
        self.client=pymongo.MongoClient(mongodb_url)
        self.db=self.client['ATTENDANCE_DB'].with_options(
            codec_options=CodecOptions(tz_aware=True, tzinfo=TIMEZONE))
        self.name=[]
        self.attendance=[]
        
    def write_employee_to_db(self, name, UID):
        attendance_db = self.client['ATTENDANCE_DB'].with_options(
            codec_options=CodecOptions(tz_aware=True, tzinfo=TIMEZONE))
        try:
            attendance_db['ATTENDANCE_COL'].insert_one({'_id':UID, 'name':name.split('_')[1], 'no': int(name.split('_')[0]),'attendance':0,'last_login':dt.now(TIMEZONE)-timedelta(days=2)})
        except:
            print("Name already exists")
        
    def update(self,UID):
        result = self.db.ATTENDANCE_COL.find_one({'_id':UID})
        last_login = result['last_login']
        if last_login.date() != dt.now(TIMEZONE).date():
            self.db.ATTENDANCE_COL.update_one({"_id":UID},{"$inc":{"attendance":1}
                                                ,"$set":{"last_login":dt.now(TIMEZONE)}})
            self.db.ATTENDANCE_RECORD_COL.insert_one({'uid':UID,'timestamp':dt.now(TIMEZONE)})
            res = self.db.ATTENDANCE_NET_TODAY.find_one({'_id':TIMEZONE.localize( dt.now().replace(hour=0,minute=0,second=0,microsecond=0))})
            if res is not None:
                self.db.ATTENDANCE_NET_TODAY.update_one({'_id':TIMEZONE.localize( dt.now().replace(hour=0,minute=0,second=0,microsecond=0))}, {"$inc":{"total":1}})
            else:
                self.db.ATTENDANCE_NET_TODAY.insert_one({'_id':TIMEZONE.localize( dt.now().replace(hour=0,minute=0,second=0,microsecond=0)), "total":1 })

    def read_employee_dict(self):
    
        attendance_db = self.client['ATTENDANCE_DB'].with_options(
            codec_options=CodecOptions(tz_aware=True, tzinfo=TIMEZONE))
        collection = attendance_db['ATTENDANCE_COL']
        result = collection.find()
        res_list = list(result)
        res_dict = {i['no']: i for i in res_list}
        return res_dict

    def view(self):
        self.name=[]
        self.attendance=[]
        records=self.db.ATTENDANCE_COL.find()
        j=0
        for i in records:
            j=j+1
            self.name.append(i["name"])
            self.attendance.append(i["attendance"])
        for i in range(j):
            print(self.name[i],self.attendance[i])
    
    def show_attendance(self):
        records_att=self.db.ATTENDANCE_COL.find()
        df = pd.DataFrame(data=list(records_att))
        df.rename({'_id':'UID'},axis=1,inplace=True)
        df.drop('no',axis=1,inplace=True)
        print(df)
        records_today=self.db.ATTENDANCE_NET_TODAY.find({'_id':TIMEZONE.localize( dt.now().replace(hour=0,minute=0,second=0,microsecond=0))})
        df = pd.DataFrame(data=list(records_today))
        df.rename({'_id':'Date','total':'Total Attendance'},axis=1,inplace=True)
        print(df)


    def export_csv(self):
        self.view()
        data={"name":self.name,"attendance":self.attendance}
        df=pd.DataFrame(data,columns=["name","attendance"])
        df.to_csv("attendance.csv",index=True)
