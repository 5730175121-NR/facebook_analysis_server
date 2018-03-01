import requests
import json
import threading
import time

import pymongo
from pymongo import MongoClient

from .wordCloudGenerator import WordCloudGenerator

class GetPostsData:

    def __init__(self,host='localhost',port=8080):
        # Dict
        self.reactions_list = {}
        self.comments_list = {}
        # Sorted List
        self.reactions_sorted_list = []
        self.comments_sorted_list = []
        self.summary_sorted_list = []
        # Locker 
        self.reactions_list_locker = threading.Lock()
        self.comments_list_locker = threading.Lock()
        # host and port for database
        self.host = host
        self.port = port
        # Message
        self.message = []

    def fetchData(self,access_token='',since='',until=''):
        start = time.time()
        reactions_content = []
        comments_content = []
        base_url = 'https://graph.facebook.com/v2.12/me'
        fields = 'id,name,posts.until(%s).since(%s){reactions{id,name,type},comments{from,comments{from}},message}' % (until, since)
        url = '%s?fields=%s&access_token=%s' % (base_url,fields,access_token)
        content = requests.get(url).json()
        next_page = ''
        if 'posts' not in content: print('posts not found')
        try:
            if 'paging' in content['posts']: next_page = content['posts']['paging']['next']
        except :
            return content
        for post in content['posts']['data']:
            if 'message' in post: self.message.append(post['message'])
            if 'reactions' in post: reactions_content.append(post['reactions'])
            if 'comments' in post: comments_content.append(post['comments'])
        summary_thread = threading.Thread(target= self.getSummaryPost, args= (access_token,since,until), daemon=True)
        getReactions_thread = threading.Thread(target= self.getReactions, args= (reactions_content,), daemon= True)
        getComments_thread = threading.Thread(target= self.getComments, args= (comments_content,), daemon= True)
        summary_thread.start()
        getReactions_thread.start()
        getComments_thread.start()

        self.doData(next_page)

        getReactions_thread.join()
        getComments_thread.join()
        summary_thread.join()

        print('get data finnished in : ', str(time.time() - start))

        updateDatabase_threading = threading.Thread(target= self.updateDatabase, args=(content['id'], content['name'], self.reactions_sorted_list[:100], self.comments_sorted_list[:100]), daemon= True)
        updateDatabase_threading.start()

        reactions_next = len(self.reactions_sorted_list) > 10
        comments_next = len(self.comments_sorted_list) > 10

        self.generate_wordcloud(str(content['id']))
        
        return {
            '_uid' : str(content['id']),
            'name' : content['name'],
            'reactions' : {
                'data' : self.reactions_sorted_list[:10],
                'next' : reactions_next
            },
            'comments': {
                'data' : self.comments_sorted_list[:10],
                'next' : comments_next
            },
            'post_summary' : {
                'data' : self.summary_sorted_list,
            }
        }

    def doData(self,next_page):
        self.doNext(next_page)
        reactionsToJson_threading = threading.Thread(target=self.reactionsToJson, daemon= True)
        commentsToJson_threading  = threading.Thread(target=self.commentsToJson, daemon= True)
        reactionsToJson_threading.start()
        commentsToJson_threading.start()
        reactionsToJson_threading.join()
        commentsToJson_threading.join()

    def doNext(self,current_page):
        content = requests.get(current_page).json()
        reactions_content = []
        comments_content = []
        do_next = ''
        if 'paging' in content:
            next_page = content['paging']['next']
            do_next = threading.Thread(target= self.doNext, args=(next_page,), daemon= True)
            do_next.start()
            
        for post in content['data']:
            if 'message' in post: self.message.append(post['message'])
            if 'reactions' in post: reactions_content.append(post['reactions'])
            if 'comments' in post: comments_content.append(post['comments'])
        getReactions_thread = threading.Thread(target= self.getReactions, args= (reactions_content,), daemon= True)
        getComments_thread = threading.Thread(target= self.getComments, args= (comments_content,), daemon= True)
        getReactions_thread.start()
        getComments_thread.start()
        getReactions_thread.join()
        getComments_thread.join()
        if do_next != '' : do_next.join()

    def getReactions(self,content):
        for data in content:
            next_reactions = ''
            if 'next' in data['paging']:
                next_content = [requests.get(data['paging']['next']).json()]
                next_reactions = threading.Thread(target= self.getReactions, args=(next_content,), daemon= True)
                next_reactions.start()
            for friend in data['data']:
                with self.reactions_list_locker :
                    if friend['id'] not in self.reactions_list: 
                        self.reactions_list[friend['id']] = { 'user_id' : friend['id'], 'name': friend['name'],'LIKE' :  0,'LOVE' :  0,'WOW' :  0,'HAHA' :  0,'SAD' :  0,'ANGRY' :  0,'THANKFUL' :  0, 'total': 0}
                    self.reactions_list[friend['id']][friend['type']] += 1
                    self.reactions_list[friend['id']]['total'] += 1
            if next_reactions != '' : next_reactions.join()

    def getComments(self,content):
        for data in content:
            next_comments = ''
            if 'next' in data['paging']:
                next_content = [requests.get(data['paging']['next']).json()]
                next_comments = threading.Thread(target= self.getComments, args=(next_content,), daemon= True)
                next_comments.start()
            for comment in data['data']:
                with self.comments_list_locker:
                    if comment['from']['id'] not in self.comments_list:
                        self.comments_list[comment['from']['id']] = { 'user_id' : comment['from']['id'], 'name': comment['from']['name'], 'comments': 0}
                    self.comments_list[comment['from']['id']]['comments'] += 1
                if 'comments' in comment:
                    in_comments = threading.Thread(target= self.getComments, args=([comment['comments']],), daemon= True)
                    in_comments.start()
                    in_comments.join()
            if next_comments != '': next_comments.join()
    
    def reactionsToJson(self):
        for uid in self.reactions_list:
            friend = self.reactions_list[uid]
            json = {
                '_uid' : friend['user_id'],
                'name' : friend['name'],
                'like': friend['LIKE'],
                'love': friend['LOVE'],
                'wow': friend['WOW'],
                'haha': friend['HAHA'],
                'sad': friend['SAD'],
                'angry': friend['ANGRY'],
                'thankful': friend['THANKFUL'],
                'total': friend['total']
            }
            self.reactions_sorted_list.append(json)
        self.reactions_sorted_list = sorted(self.reactions_sorted_list, key= self.getReactionKey, reverse=True)

    def commentsToJson(self):
        for uid in self.comments_list:
            friend = self.comments_list[uid]
            json = {
                '_uid' : friend['user_id'],
                'name' : friend['name'],
                'comments': friend['comments']
            }
            self.comments_sorted_list.append(json)
        self.comments_sorted_list = sorted(self.comments_sorted_list, key=self.getCommentsKey, reverse=True)

    def getReactionKey(self, custom):
        return custom['total']

    def getCommentsKey(self, custom):
        return custom['comments']

    def updateDatabase(self, uid, name, reactions_sorted_list, comments_sorted_list):
        client = MongoClient(self.host, self.port)
        db = client['database']
        dashboards = db.dashboards
        if dashboards.find_one({'_uid' : uid}) != None : 
            dashboards.find_one_and_update(
                {'_uid' : uid}, 
                { '$set': 
                    {
                        'name' : name, 
                        'comments' : comments_sorted_list, 
                        'reactions' : reactions_sorted_list
                    }
                }
            )
        else : 
            dashboards.insert_one(
                {
                    '_uid' : uid,
                    'name' : name, 
                    'comments' : comments_sorted_list, 
                    'reactions' : reactions_sorted_list
                }
            )

    def getSummaryPost(self,access_token, since='',until=''):
        base_url = 'https://graph.facebook.com/v2.12/me'
        fields = 'id,name,posts.until(%s).since(%s){reactions.summary(true),comments.summary(true),permalink_url,created_time}' % (until, since)
        url = '%s?fields=%s&access_token=%s' % (base_url,fields,access_token)
        content = requests.get(url).json()
        next_page = ''
        try:
            if 'paging' in content['posts']: next_page = content['posts']['paging']['next']
        except :
            print(content)
            return content
        for post in content['posts']['data']:
            self.summary_sorted_list.append({
                'id': post['id'],
                'created_time': post['created_time'],
                'link_url': post['permalink_url'],
                'total_reactions': post['reactions']['summary']['total_count'],
                'total_comments': post['comments']['summary']['total_count'],
            })
        while next_page != '':
            next_content = requests.get(next_page).json()
            if 'paging' in next_content['data']: next_page = content['paging']['next']
            else : next_page = ''
            for post in next_content['data']:
                self.summary_sorted_list.append({
                'id': post['id'],
                'created_time': post['created_time'],
                'link_url': post['permalink_url'],
                'total_reactions': post['reactions']['summary']['total_count'],
                'total_comments': post['comments']['summary']['total_count'],
            })
    
    def generate_wordcloud(self, uid):
        text = (" ".join(self.message))
        self.whatisthis(text)
        wordcloud = WordCloudGenerator().generate(text, uid)
        if(wordcloud == 'error'): 
            print("uid : %s can't generate world clound" % uid)
            print(text)
            return {
                'error' : {
                    'message' : "can't generate world clound"
                }
            }

    def whatisthis(self,s):
        if isinstance(s, str):
            print ("ordinary string")
        elif isinstance(s, unicode):
            print ("unicode string")
        else:
            print ("not a string")


