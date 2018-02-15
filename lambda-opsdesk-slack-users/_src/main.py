import requests
import os
import json
import boto3
import time

slack_auth = os.environ.get('SLACK_TOKEN')
slack_bot_auth_token = os.environ.get('SLACK_BOT_TOKEN')
slack_url = 'https://slack.com/api/'
bucket_name = 'opsway-zohobooks-backup'

def channel_id_presence():
    url = 'https://s3.amazonaws.com/opsway-zohobooks-backup/slack_users.json'
    
    r = requests.get(url)
    result = r.json()
    
    for item in result:
        if item['opswaybot_im_channel'] != '':
            return True

def only_paid_accounts(member):
    if (('is_restricted' in member and member['is_restricted'] is False
         and 'is_ultra_restricted' in member and member['is_ultra_restricted'] is False)
        or ('is_restricted' in member and member['is_restricted'] is True
            and 'is_ultra_restricted' in member and member['is_ultra_restricted'] is False)):
            return True

def im_open(user_id,is_bot=False):
    url = 'im.open'
    if is_bot is not True:
        r = requests.post(slack_url + url + '?token=' + slack_bot_auth_token, data={'user': user_id})
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
        if only_paid_accounts(member):
            time.sleep(1)
            # if channel_id_presence():
            direct_channel_id = im_open(member['id'],member['is_bot'])

            r = requests.get(slack_url + 'users.profile.get?token=' +
                             slack_auth + '&user=' + member['id'])
            result = r.json()

            user = {}
            user['id'] = member['id']
            user['name'] = member['name']
            user['is_bot'] = member['is_bot']
            user['team_id'] = member['team_id']
            user['deleted'] = member['deleted']
            user['updated'] = member['updated']
            user['is_admin'] = member['is_admin']
            user['is_owner'] = member['is_owner']
            user['is_restricted'] = member['is_restricted']
            user['first_name'] = result['profile']['first_name'] if ('first_name' in result['profile'] and result['profile']['first_name'] != '') else ''
            user['is_primary_owner'] = member['is_primary_owner']
            user['is_ultra_restricted'] = member['is_ultra_restricted']
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
