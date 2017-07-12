import requests
import os
import json

slack_auth = os.environ.get('slack_token')
headers = {"Content-Type":"application/x-www-form-urlencoded"}
slack_url = 'https://slack.com/api/'

def only_paid_accounts(member):
    if (('is_restricted' in member and member['is_restricted'] is False
         and 'is_ultra_restricted' in member and member['is_ultra_restricted'] is False)
        or ('is_restricted' in member and member['is_restricted'] is True
            and 'is_ultra_restricted' in member and member['is_ultra_restricted'] is False)):
            return True

def get_github_login_from_user_profile(user_id):
    r = requests.get(slack_url + 'users.profile.get?token=' + slack_auth + '&user=' + user_id)
    result = r.json()
    
    return result['profile']['fields']['Xf5916FA0L']['value']  

def fill_slack_user_github_login_field(tocat_login,github_login):
    r = requests.get(slack_url + 'users.list?token=' + slack_auth)
    result = r.json()
    
    for user in result['members']:
        if only_paid_accounts(user):
            if user['name'] == tocat_login:
                if get_github_login_from_user_profile(user['id']) == '' or get_github_login_from_user_profile(user['id']) != github_login:
                    request = requests.post(slack_url + 'users.profile.set?token=' + slack_auth + '&user=' + user['id'], data="name=Xf5916FA0L&value=" + github_login, headers=headers)
                    result = request.json()
                
                    return 'Successfuly update github login field for user: ' + user['name']
    
def process(event, context):
    
    items = []
    data = json.loads(event['body'])
    items.append(data)
    
    tocat_login = items[0]['tocat_login']
    github_login = items[0]['github_login']
    
    res = fill_slack_user_github_login_field(tocat_login,github_login)
    
    response = {}
    response['isBase64Encoded'] = False
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'application/json'}
    response['body'] = json.dumps(res) 
    return response;
