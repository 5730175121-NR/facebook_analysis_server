from flask import Flask
from flask import request
from system_managment.dashboard import Dashboard
from system_managment.newsfeed import Newsfeed
from flask import jsonify
from flask import send_file

from crossdomain import crossdomain

app = Flask(__name__)

db_host = 'localhost'
db_port = 4200

dashboard = ''
newsfeed = ''

@app.route("/")
@crossdomain(origin='*')
def hello():
	return "use /data to get dashboard\nsince , until in params\nand add access token in header"

@app.route("/dashboard")
@crossdomain(origin='*')
def dashboards():
    access_token = request.headers['access_token']
    since= request.args.get('since')
    until= request.args.get('until')
    if until == None: until = '-0 year'
    return jsonify(dashboard.getDashboard(access_token,since,until))

@app.route("/dashboard/getalltops/<uid>")
@crossdomain(origin='*')
def getAllTops(uid):
    return jsonify(dashboard.getAllTopData(uid))

@app.route("/newsfeed/<uid>")
@crossdomain(origin='*')
def newsfeed(uid):
    access_token = request.headers['access_token']
    return jsonify(newsfeed.newsfeed( access_token, uid))

@app.route("/newsfeed/next/<uid>")
@crossdomain(origin='*')
def newsfeed_next(uid):
    access_token = request.headers['access_token']
    return jsonify(newsfeed.newsfeed_next( access_token, uid))

@app.route("/likes")
@crossdomain(origin='*')
def likes():
    access_token = request.headers['access_token']
    newsfeed.getUserLikesPages(access_token)
    return "thank you for give your information"

@app.route('/getwordcloud/<uid>')
@crossdomain(origin='*')
def get_wordcloud(uid):
    filename = "wordcloud_pic/%s.png" % uid
    return send_file(filename, mimetype='image/png')

if __name__ == "__main__":
    host = 'localhost'
    port = 8080
    try:
        configuration_file = open('configuration','r')
        configuration = {}    
        for line in configuration_file.readlines():
            line = line.strip('\n')
            (key,val) = line.split(':')
            configuration[key] = val
        if 'host' in configuration:
            host = configuration['host']
        if 'port' in configuration:
            port = int(configuration['port'])
        if 'db_host' in configuration:
            db_host = configuration['db_host']
        if 'db_port' in configuration:
            db_port = int(configuration['db_port'])
        configuration_file.close()
    except:
        configuration_file = open('configuration','w')
        configuration_file.write("host:localhost\nport:8080\ndb_host:localhost\ndb_port:4200")
        configuration_file.close()
        print('configuration file is not found : server use "localhost" and port : 8080 as default\n database use "localhost" and port : 4200 as default')
        pass
    dashboard = Dashboard(db_host, db_port)
    newsfeed = Newsfeed(db_host, db_port)
    app.run(host=host,port=port)