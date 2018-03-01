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
    
    def fetchData(self, access_token, page_id , limit=2):
        list_of_posts = []
        base_url = 'https://graph.facebook.com/v2.12/%s' % page_id
        fields = 'name,fan_count,photos.limit(1){images},posts.limit(%d){created_time,message,full_picture,reactions.summary(true),comments.summary(true),permalink_url,type}' % limit
        url = '%s?fields=%s&access_token=%s' % (base_url,fields,access_token)
        content = requests.get(url).json()
        if 'name' not in content: return (True, content)
        page_name = content['name']
        page_picture = ''
        fan_count = 0
        isActive = True
        priority = ''
        if 'photos' in content : page_picture = content['photos']['data'][0]['images'][0]['source']
        if 'fan_count' in content: fan_count = content['fan_count']
        if fan_count != 0: priority = self.cal_priority(fan_count)
        if 'posts' in content : 
            for post in content['posts']['data']:
                message = ''
                full_picture = ''
                if 'message' in post: message = post['message']
                if 'full_picture' in post: full_picture = post['full_picture']
                list_of_posts.append({
                    'id' : post['id'],
                    'type' : post['type'],
                    'created_time' : post['created_time'],
                    'message': message,
                    'full_picture' : full_picture,
                    'reactions_summary' : post['reactions']['summary']['total_count'],
                    'comments_summary' : post['comments']['summary']['total_count'],
                    'permalink_url' : post['permalink_url']
                })
        if len(list_of_posts) > 0: 
            last_updated_full = list_of_posts[0]['created_time']
            last_updated , offset = last_updated_full.split("+")
            last_updated = datetime.datetime.strptime(last_updated, "%Y-%m-%dT%X")
            detla_time = datetime.datetime.now() - last_updated
            isActive = detla_time.days < 180
        else :
            isActive = False
        self.updateDatabase(page_id, page_name, page_picture, fan_count, list_of_posts, isActive, priority)
        return (False, 'get data from page success')

    def updateDatabase(self, page_id, page_name, page_picture, fan_count, list_of_posts, isActive, priority):
        if self.cache_pages.find_one({'page_id' : page_id}) != None : 
            self.cache_pages.find_one_and_update(
                {'page_id' : page_id}, 
                { '$set': 
                    {
                        'page_name' : page_name,
                        'page_picture' : page_picture,
                        'time_stamp' : datetime.datetime.now(),
                        'fan_count' : fan_count,
                        'list_of_posts' : list_of_posts,
                        'isActive' : isActive,
                        'priority' : priority
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
                    'fan_count' : fan_count,
                    'list_of_posts' : list_of_posts,
                    'isActive' : isActive,
                    'priority' : priority
                }
            )

    def cal_priority(self, fan_count):
        if fan_count > 1000000:
            return 7200 # 2 hours
        elif fan_count > 750000:
            return 14400 # 4 hours
        elif fan_count > 500000:
            return 21600 # 6 hours
        elif fan_count > 100000:
            return 28800 # 8 hours
        else:
            return 36000 # 10 hours


