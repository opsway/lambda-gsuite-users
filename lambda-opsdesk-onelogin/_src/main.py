import requests
import os
import json
# import boto3

# bucket_name = 'opsway-zohobooks-backup'
onelogin_api_path = 'https://api.us.onelogin.com/api/1/'

def get_access_token():
    url = 'https://api.us.onelogin.com/auth/oauth2/token'
    params = {"grant_type":"client_credentials"}
    client_id = os.environ.get('client_id1')
    client_secret = os.environ.get('client_secret1')
    headers = {"Authorization": "client_id:"+client_id +", client_secret:" + client_secret,
                "Content-Type": "application/json"
            }
    r = requests.post(url, params = params, headers = headers)
    result = r.json()
    return result['data'][0]['access_token']

headers = {"Authorization": "bearer:" + get_access_token()}

def get_users():
    url = 'https://api.us.onelogin.com/api/1/users'
    
    users = []
    while True:
        r = requests.get(url, headers = headers)
        result = r.json();
        url = result['pagination']['next_link'];
        users = users + result['data']
        if (url == None):
            break;
    return users

def get_roles():
    r = requests.get(onelogin_api_path + 'roles', headers = headers)
    result = r.json();
    
    return result['data']

def get_user_roles_list():
    composite_list = []

    for user in get_users():
        r = requests.get(onelogin_api_path + 'users/' + str(user['id']) + '/roles', headers = headers)
        result = r.json();
        for role in result['data'][0]:
            raw_data = {}
            raw_data['login'] = user['username']
            raw_data['role_id'] = role
            composite_list.append(raw_data)
    return composite_list

def matching_user_with_role():
    user_roles = []
    
    for user_role in get_user_roles_list():
        for role in get_roles():
            raw_list = {}
            raw_list['login'] = user_role['login']
            if user_role['role_id'] == role['id']:
                raw_list['role_name'] = role['name']
                user_roles.append(raw_list)
    return user_roles

def put_data_to_s3_bucket(payload, key, success_message):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload))
    print success_message


def process(event, context):
    put_data_to_s3_bucket(get_users(), 'Onelogin_users.json', 'Uploaded onelogin users')
    put_data_to_s3_bucket(matching_user_with_role(), 'Onelogin_users_with_roles.json', 'Uploaded users with their roles')
