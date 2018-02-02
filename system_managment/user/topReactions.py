import datetime

class TopReaction:

    def __init__(self):
        self.timestamp = datetime.datetime.utcnow()
        self.topReactionList = []

    def setTopReactionList(self, topReactionList):
        self.topReactionList = topReactionList

