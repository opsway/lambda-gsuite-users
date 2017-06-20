import requests
import os
import json

slack_api_path = 'https://slack.com/api/' 
token = os.environ.get('SLACK_TOKEN') 

def users_list():
	url = 'users.list'
	r = requests.post(slack_api_path + url + '?token=' + token, data = {'presence' : 'false'})
	print "Respone from users.list"
	result = r.json();
	if (r.status_code != 200):
		raise ValueError('Error retrieving data')
	return result['members']

def im_open(user_id):
	url = 'im.open'
	r = requests.post(slack_api_path + url + '?token=' + token, data = {'user' : user_id})
	result = r.json();
	if (r.status_code != 200):
		raise ValueError('Error retrieving data')
	return result['channel']['id']

def chat_post_message(channel_id,text):
	url = 'chat.postMessage'
	r = requests.post(slack_api_path + url + '?token=' + token, 
		data = {'channel' : channel_id, 'text' : text})
	result = r.json();
	if (r.status_code != 200):
		raise ValueError('Error retrieving data')

def get_user_id_by_name(username):
	users = users_list()
	for user in users:
		if user['name'] == username:	 
			return user['id']
			break;
	raise Exception('Can not find user id for username: ' + username)	

def process(message):
	print 'Forwarding message to Slack'
	print message
	if 'sleep' in message:
		pause = random.randint(1, message['sleep'])
		print 'Sleeping for ' + pause + 's before sending a message'
	channel_id = ''
	if 'to' in message:
		channel_id = im_open(message['to'])
	else:
		user_id = get_user_id_by_name(message['to_name'])
		channel_id = im_open(user_id)
	chat_post_message(channel_id, message['text'])