import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint

import random
import threading

from .pages_manage.getLikesPage import GetLikesPage
from .pages_manage.getPostsPage import GetPostsPage

class Newsfeed:
    def __init__(self, host='localhost', port=4200):
        self.host = host
        self.port = port
        self.client = MongoClient(self.host, self.port)
        print('newsfeed database connected to : %s : %s' % (self.host, self.port))
        self.db = self.client['database']
        self.user_pages = self.db['user_pages']
        self.cache_pages = self.db['cache_pages']
        self.getLikesPage = GetLikesPage(self.host, self.port)
        self.getPostsPage = GetPostsPage(self.host, self.port)

    def newsfeed(self, access_token, uid):
        user_pages_data = self.user_pages.find_one({'_uid' : uid})
        pages = user_pages_data['pages']
        return self.checkPagesCache(access_token, random.sample(list(pages.values()), 20))

    def checkPagesCache(self, access_token, list_of_user_pages):
        newsfeed = []
        for page in list_of_user_pages:
            page_data = self.cache_pages.find_one({ 'page_id' : page['id']})
            if page_data != None: 
                for post in page_data['list_of_posts']:
                    post['page_id'] = page_data['page_id']
                    post['page_name'] = page_data['page_name']
                    post['page_picture'] = page_data['page_picture']
                    newsfeed.append(post)
            else:
                get_pages_thread = threading.Thread(target= self.getPostsPage.fetchData, args= (access_token, page['id']), daemon= True)
                get_pages_thread.start()
        return newsfeed

    def getUserLikesPages(self, access_token):
        GetLikesPage(self.host, self.port).fetchData(access_token=access_token)
