import requests
import os
import json
import boto3
import time

slack_auth = os.environ.get('slack_token')
slack_url = 'https://slack.com/api/'
bucket_name = 'opsway-zohobooks-backup'

def channel_id_presence():
    url = 'https://s3.amazonaws.com/opsway-zohobooks-backup/slack_users.json'
    
    r = requests.get(url)
    result = r.json()
    
    for item in result:
        if item['opswaybot_im_channel'] != '':
            return True
        else:
            return False

def im_open(user_id):
    url = 'im.open'
    r = requests.post(slack_url + url + '?token=' +
                      slack_auth, data={'user': user_id})
    result = r.json()
    if (r.status_code != 200):
        raise ValueError('Error retrieving data')

    return result['channel']['id']


def compiling_slack_users_list():
    r = requests.get(slack_url + 'users.list?token=' + slack_auth)
    result = r.json()

    if (r.status_code != 200):
        raise ValueError('Error retrieving data')

    slack_users = []

    for member in result['members']:
        if (('is_restricted' in member and member['is_restricted'] is False
             and 'is_ultra_restricted' in member and member['is_ultra_restricted'] is False)
            or ('is_restricted' in member and member['is_restricted'] is True
                and 'is_ultra_restricted' in member and member['is_ultra_restricted'] is False)):

            time.sleep(1)
            if channel_id_presence():
                direct_channel_id = im_open(member['id'])

            r = requests.get(slack_url + 'users.profile.get?token=' +
                             slack_auth + '&user=' + member['id'])
            result = r.json()

            user = {}
            user['id'] = member['id']
            user['team_id'] = member['team_id']
            user['name'] = member['name']
            user['deleted'] = member['deleted']
            user['is_admin'] = member['is_admin']
            user['is_owner'] = member['is_owner']
            user['is_primary_owner'] = member['is_primary_owner']
            user['is_restricted'] = member['is_restricted']
            user['is_ultra_restricted'] = member['is_ultra_restricted']
            user['is_bot'] = member['is_bot']
            user['updated'] = member['updated']
            user['first_name'] = result['profile']['first_name']
            user['opswaybot_im_channel'] = str(direct_channel_id)
            user['has_2fa'] = member['has_2fa'] if 'has_2fa' in member else ''
            user['last_name'] = result['profile']['last_name'] if ('last_name' in result['profile'] and result['profile']['last_name'] != '') else ''
            user['phone'] = result['profile']['phone'] if 'phone' in result['profile'] else ''
            user['skype'] = result['profile']['skype'] if 'skype' in result['profile'] else ''
            user['real_name'] = result['profile']['real_name'] if 'real_name' in result['profile'] else ''
            user['email'] = result['profile']['email'] if 'email' in result['profile'] else ''                
            user['github_login'] = result['profile']['fields']['Xf5916FA0L']['value'] if (result['profile']['fields'] is not None and 'Xf5916FA0L' in result['profile']['fields']) else ''
            
            slack_users.append(user)
    
    return slack_users


def process(event, context):
    s3 = boto3.resource('s3')
    key = 'slack_users.json'
    s3.Bucket(bucket_name).put_object(
        Key=key, Body=json.dumps(compiling_slack_users_list()))
    print 'Uploaded slack users list with github logins and opswaybot_im_channel ids'
