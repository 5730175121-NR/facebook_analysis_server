import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint

from .getFacebookData.getFacebookData import GetFacebookData

class Dashboard:

    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.isConnect = False
        
    def connect(self):
        self.isConnect = True
        self.client = MongoClient(self.host, self.port)
        print('connecting to : %s : %s' % (self.host, self.port))
        self.db = self.client['database']
        self.dashboards = self.db.dashboards

    def getDashboard(self,access_token,since,until):
        user_dashboard = GetFacebookData(self.host, self.port).fetchData(access_token, since, until)
        return user_dashboard

    def getAllTopData(self, uid):
        if(not self.isConnect) : self.connect()
        print('connecting')
        allTopData = self.dashboards.find_one({'_uid' : uid})
        returnAllTopData = {
            '_uid' : allTopData['_uid'],
            'name' : allTopData['name'],
            'comments' : allTopData['comments'],
            'reactions' : allTopData['reactions']
        }
        return returnAllTopData