import requests
import os
import json
import boto3
import urllib2

slack_api_path = 'https://slack.com/api/'
token = os.environ.get('SLACK_BOT_TOKEN')
bucket_name = os.environ.get('BUCKET_NAME')
bucket_key = os.environ.get('BUCKET_KEY')
s3 = boto3.resource('s3')
object = s3.Object(bucket_name, bucket_key)

def users_list():
    response = object.get()
    users = json.loads(response["Body"].read())
    return users

def im_open(user_id):
    for user in users_list():
        if user_id == user['id']:
            return user['opswaybot_im_channel']

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
