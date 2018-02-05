import requests
import json
import threading
import time
import datetime

import pymongo
from pymongo import MongoClient
import pprint

class GetPostsPage:

    def __init__(self, host='localhost', port=4200):
        self.host = host
        self.port = port
        self.client = MongoClient(self.host, self.port)
        print('cache_pages database connected to : %s : %s' % (self.host, self.port))
        self.db = self.client['database']
        self.cache_pages = self.db['cache_pages']
    
    def fetchData(self, access_token, page_id , limit=3):
        list_of_posts = []
        base_url = 'https://graph.facebook.com/v2.12/%s' % page_id
        fields = 'name,photos.limit(1){images},posts.limit(%d){created_time,message,full_picture,reactions.summary(true),comments.summary(true),permalink_url}' % limit
        url = '%s?fields=%s&access_token=%s' % (base_url,fields,access_token)
        content = requests.get(url).json()
        if 'name' not in content: return (True, content)
        page_name = content['name']
        if 'photos' in content : page_picture = content['photos']['data'][0]['images'][0]['source']
        else : page_picture = ''
        if 'posts' in content : 
            for post in content['posts']['data']:
                message = ''
                full_picture = ''
                if 'message' in post: message = post['message']
                if 'full_picture' in post: full_picture = post['full_picture']
                list_of_posts.append({
                    'id' : post['id'],
                    'created_time' : post['created_time'],
                    'message': message,
                    'full_picture' : full_picture,
                    'reactions_summary' : post['reactions']['summary']['total_count'],
                    'comments_summary' : post['comments']['summary']['total_count'],
                    'permalink_url' : post['permalink_url']
                })
        self.updateDatabase(page_id, page_name, page_picture, list_of_posts)
        return (False, 'get data from page success')

    def updateDatabase(self, page_id, page_name, page_picture, list_of_posts):
        if self.cache_pages.find_one({'page_id' : page_id}) != None : 
            self.cache_pages.find_one_and_update(
                {'page_id' : page_id}, 
                { '$set': 
                    {
                        'page_name' : page_name,
                        'page_picture' : page_picture,
                        'time_stamp' : datetime.datetime.now(),
                        'list_of_posts' : list_of_posts
                    }
                }
            )
        else : 
            self.cache_pages.insert_one(
                {
                    'page_id' : page_id,
                    'page_name' : page_name,
                    'page_picture' : page_picture,
                    'time_stamp' : datetime.datetime.now(),
                    'list_of_posts' : list_of_posts
                }
            )

