import requests
import json
from datetime import datetime
class RequestSender:

    def __init__(self):
        self.session=requests.Session()

    def Get(self,url,headers=None):
        if headers is not None:
            pass

        else:
            pass
    
    def post(self,url,data,headers=None):
        try:
            if headers is not None:
                req=self.session.post(url,data=json.dumps(data),json=json.dumps(data),headers=headers)

                if req.status_code==200:
                    return req.json()
                else:
                    return req.text
            else:
                pass
        except Exception as e:
            return e
        
date=datetime.now().date()

date1=datetime.strptime("2024-08-21","%Y-%m-%d")
print(date1.day)