from topReactions import TopReactions

import datetime

class User:

    def __init__(self,uid,username):
        self.uid = uid
        self.username = username
        self.timestamp = datetime.datetime.utcnow()
        self.topReactions = TopReactions()

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp