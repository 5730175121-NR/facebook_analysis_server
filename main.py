from flask import Flask
from flask import request
from flask_cors import CORS
from system_managment.dashboard import Dashboard
from system_managment.getFacebookData.getFacebookData import GetFacebookData
from flask import jsonify
# import json

app = Flask(__name__)
CORS(app)

db_host = 'localhost'
db_port = 4200

@app.route("/")
def hello():
	return ("use /data to get dashboard\n    since , until in params\n   and add access token in header %s" % nut)

@app.route("/dashboard")
def dashboards():
    access_token = request.headers['access_token']
    since= request.args.get('since')
    until= request.args.get('until')
    if until == None: until = '-0 year'
    return jsonify(Dashboard(db_host, db_port).getDashboard(access_token,since,until))

#don't use this.
@app.route("/dashboard/getalltops/<uid>")
def getAllTops(uid):
    return jsonify(Dashboard(db_host, db_port).getAllTopData(uid))

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
        configuration_file.write("host:localhost\nport:8080\ndb_host:192.168.1.64\ndb_port:4200")
        configuration_file.close()
        print('configuration file is not found : server use "localhost" and port : 8080 as default\n database use "localhost" and port : 4200 as default')
        pass
    app.run(host=host,port=port)