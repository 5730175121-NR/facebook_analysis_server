import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint

from .getLikesPage.getLikesPage import GetLikesPage

class Newsfeed:
    def __init__(self, host='localhost', port=4200):
        self.host = host
        self.port = port
        self.client = MongoClient(self.host, self.port)
        print('connecting to : %s : %s' % (self.host, self.port))
        self.db = self.client['database']
        self.user_pages = self.db['user_pages']

    def newsfeed(self, uid):
        user_pages_data = self.user_pages.find_one({'_uid' : uid})
        pprint.pprint(user_pages_data)

    def test(self, access_token):
        GetLikesPage(self.host, self.port).fetchData(access_token=access_token)
