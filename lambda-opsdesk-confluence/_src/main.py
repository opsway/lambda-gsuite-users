import os
import json
import requests
import boto3

headers = {"Authorization": os.environ.get('confluence_auth'), "Content-Type":"application/json"}
confluence_url = 'https://opsway.atlassian.net/wiki/rest/api/'
bucket_name = 'opsway-zohobooks-backup';


def get_space_permissions ():
    r = requests.get(confluence_url + 'space?limit=1000&expand=permissions', headers = headers)
    result = r.json();
    
    permissions_arr = []
    
    for res in result['results']:
        for item in res['permissions']:
            if 'user' in item['subjects']:
                for u in item['subjects']['user']['results']:
                    user = {}
                    user['space'] = res['name']
                    user['username'] = u['username']
                    user['type'] = 'user'
                    permissions_arr.append(user)
            elif 'group' in item['subjects']:
                for g in item['subjects']['group']['results']:
                    group = {}
                    group['space'] = res['name']
                    group['name'] = g['name']
                    group['type'] = 'group'
                    permissions_arr.append(group)
    
    result_permissions = [item for quantity, item in enumerate(permissions_arr) if item not in permissions_arr[:quantity]]  
    
    return result_permissions

    
def get_groups_access ():
    r = requests.get(confluence_url + 'group?limit=1000', headers = headers)
    result = r.json();

    groups_access = []

    for item in get_space_permissions():
        for g_name in result['results']:
            if item['type'] == 'group':
                if (item['name'] == g_name['name'] and g_name['name'] == 'jira-software-users'):
                    group = {}
                    group['name'] = g_name['name']
                    group['space'] = item['space']
                    groups_access.append(group)
    
    return groups_access


def get_users_access ():
    r = requests.get(confluence_url + 'group/confluence-users/member?&limit=1000', headers = headers)
    result = r.json();
    
    confluence_users = []
    users_from_permissions = []
    
    for item in get_space_permissions():
        if item['type'] == 'user':
             users_from_permissions.append(item['username'])
    
    for item in result['results']:
        confluence_users.append(item['username'])

    uniq = [val for val in users_from_permissions if not(val in confluence_users)]
    
    user_access = []
    for name in uniq:
        for item in get_space_permissions():
            if item['type'] == 'user':
                if name in item['username']:
                    user = {}
                    user['name'] = item['username']
                    user['space'] = item['space']
                    user_access.append(user) 
    
    return user_access


def process(event, context):
    s3 = boto3.resource('s3')
    key = 'Confluence_groups_permissions_to_spaces.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(get_groups_access()));
    print 'Uploaded jira clients who have more groups than only Jira-software-users'

    key = 'Confluence_users_permissions_to_spaces.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(get_users_access()));
    print 'Uploaded jira shared filters'
