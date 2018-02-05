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
        return self.checkPagesCache(access_token, random.sample(list(pages.values()), 7))

    def checkPagesCache(self, access_token, list_of_user_pages):
        newsfeed = []
        isError = False
        msg = ''
        for page in list_of_user_pages:
            page_data = self.cache_pages.find_one({ 'page_id' : page['id']})
            if page_data != None:
                delta_time = datetime.datetime.now() - page_data['time_stamp']
                if(delta_time.days > 0 or delta_time.seconds > 4200):
                    (isError, msg) = self.getPostsPage.fetchData(access_token, page['id'])
                    page_data = self.cache_pages.find_one({ 'page_id' : page['id']})
            else:
                (isError, msg) = self.getPostsPage.fetchData(access_token, page['id'])
                page_data = self.cache_pages.find_one({ 'page_id' : page['id']})
            if isError : return msg
            for post in page_data['list_of_posts']:
                post['page_id'] = page_data['page_id']
                post['page_name'] = page_data['page_name']
                post['page_picture'] = page_data['page_picture']
                newsfeed.append(post)
        random.shuffle(newsfeed)
        print( 'total post count : %d' % len(newsfeed))
        return newsfeed

    def getUserLikesPages(self, access_token):
        GetLikesPage(self.host, self.port).fetchData(access_token=access_token)
