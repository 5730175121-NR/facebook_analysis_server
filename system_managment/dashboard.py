import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint

from .user_posts_manage.getPostsData import GetPostsData

class Dashboard:

    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.client = MongoClient(self.host, self.port)
        print('dashboard database connected to : %s : %s' % (self.host, self.port))
        self.db = self.client['database']
        self.dashboards = self.db.dashboards

    def getDashboard(self,access_token,since,until):
        user_dashboard = GetPostsData(self.host, self.port).fetchData(access_token, since, until)
        return user_dashboard

    def getAllTopData(self, uid):
        allTopData = self.dashboards.find_one({'_uid' : uid})
        returnAllTopData = {
            '_uid' : allTopData['_uid'],
            'name' : allTopData['name'],
            'comments' : {
                'data' : allTopData['comments']
            },
            'reactions' : {
                'data' : allTopData['reactions']
            }
        }
        return returnAllTopData