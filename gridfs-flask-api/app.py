import gridfs
import json
import os
import urllib.parse
from flask import Flask, request
from pymongo import MongoClient



mongo_user = urllib.parse.quote_plus(os.environ['MONGO_USER'])
mongo_pass = urllib.parse.quote_plus(os.environ['MONGO_PASS'])
mongo_host = os.environ['MONGO_HOST']
mongo_port = os.environ['MONGO_PORT']
mongo_auth = os.environ['MONGO_AUTH']

mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (mongo_user, mongo_pass, mongo_host, mongo_port, mongo_auth)

app = Flask(__name__)

'''
	Provides a `/insert` access point.
	The request data should be a JSON object of everything to push 
	(data + metadata)
'''
@app.route('/gridfs-insert')
def insert():
	data = json.loads(request.data.decode('utf-8'))
	try:
		data['data'] = bytes(data['data']['data'])
	except:
		data['data'] = bytes(data['data'])
	wf_db = MongoClient(mongo_uri).waterFilter
	fs = gridfs.GridFS(wf_db, 'Scanners')

	bson_id = fs.put(**data)

	return bson_id.binary, 200


