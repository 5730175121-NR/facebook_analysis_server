import requests
import json
import threading
import time

import pymongo
from pymongo import MongoClient

class GetLikesPage:

    def __init__(self, host='localhost', port=4200):
        self.host = host
        self.port = port

        self.list_of_page = {}
        self.list_of_page_locker = threading.Lock()

    def fetchData(self,access_token=''):
        base_url = 'https://graph.facebook.com/v2.12/me'
        fields = 'likes{name}'
        url = '%s?fields=%s&access_token=%s' % (base_url,fields,access_token)
        content = requests.get(url).json()
        next_page = ''
        try:
            if 'paging' in content['likes']: next_page = content['likes']['paging']['next']
        except :
            print(content)
            return content
        do_next = threading.Thread(target= self.doNext, args=(next_page,), daemon= True)
        do_next.start()
        for page in content['likes']['data']:
            with self.list_of_page_locker :
                self.list_of_page[page['id']] = { 'id' : page['id'], 'name' : page['name']}
        do_next.join()
        updateDatabase_threading = threading.Thread(target= self.updateDatabase, args=(content['id'], self.list_of_page), daemon= True)
        updateDatabase_threading.start()
        return self.list_of_page

    def doNext(self, current_page):
        content = requests.get(current_page).json()
        next_page = ''
        if 'paging' in content:
            if 'next' in content['paging']:
                next_page = content['paging']['next']
                do_next = threading.Thread(target= self.doNext, args=(next_page,), daemon= True)
                do_next.start()
        for page in content['data']:
            with self.list_of_page_locker :
                self.list_of_page[page['id']] = { 'id' : page['id'], 'name' : page['name']}
        if next_page != '' : do_next.join()

    def updateDatabase(self, uid, list_of_page):
        client = MongoClient(self.host, self.port)
        db = client['database']
        user_pages = db['user_pages']
        if user_pages.find_one({'_uid' : uid}) != None : 
            user_pages.find_one_and_update(
                {'_uid' : uid}, 
                { '$set': 
                    {
                        'pages' : list_of_page
                    }
                }
            )
        else : 
            user_pages.insert_one(
                {
                    '_uid' : uid,
                    'pages' : list_of_page,
                    'active_pages' : {},
                    'non_active_pages' : {}
                }
            )