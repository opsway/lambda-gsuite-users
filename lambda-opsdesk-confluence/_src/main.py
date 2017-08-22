import os
import json
import requests
import boto3

headers = {"Authorization": os.environ.get('confluence_auth'), "Content-Type":"application/json"}
confluence_url = 'https://opsway.atlassian.net/wiki/rest/api/'
bucket_name = 'opsway-zohobooks-backup';


# def get_space_permissions ():
#     r = requests.get(confluence_url + 'space?limit=1000&expand=permissions', headers = headers)
#     result = r.json();
#
#     permissions_arr = []
#
#     for res in result['results']:
#         for item in res['permissions']:
#             if 'user' in item['subjects']:
#                 for u in item['subjects']['user']['results']:
#                     user = {}
#                     user['space'] = res['name']
#                     user['username'] = u['username']
#                     user['type'] = 'user'
#                     permissions_arr.append(user)
#             elif 'group' in item['subjects']:
#                 for g in item['subjects']['group']['results']:
#                     group = {}
#                     group['space'] = res['name']
#                     group['name'] = g['name']
#                     group['type'] = 'group'
#                     permissions_arr.append(group)
#
#     result_permissions = [item for quantity, item in enumerate(permissions_arr) if item not in permissions_arr[:quantity]]
#
#     return result_permissions
#
#
# def get_groups_access():
#     r = requests.get(confluence_url + 'group?limit=1000', headers = headers)
#     result = r.json();
#
#     groups_access = []
#
#     for item in get_space_permissions():
#         for g_name in result['results']:
#             if item['type'] == 'group':
#                 if (item['name'] == g_name['name'] and g_name['name'] == 'jira-software-users'):
#                     group = {}
#                     group['name'] = g_name['name']
#                     group['space'] = item['space']
#                     groups_access.append(group)
#
#     default_data = {}
#     default_data['name'] = 'dummy'
#     default_data['space'] = 'dummy'
#     groups_access.append(default_data)
#
#     return groups_access
def get_users_with_their_teams():
    r = requests.get(confluence_url + 'group/confluence-users/member?&limit=1000', headers = headers)
    result = r.json()
    
    user_teams = []
    for user in result['results']:
        r = requests.get(confluence_url + 'user/memberof?username=' + str(user['username']) , headers = headers)
        result = r.json()
        for team in result['results']:
            user_team = {}
            user_team['login'] = user['username']
            user_team['team_name'] = team['name']
            user_teams.append(user_team)
    print user_teams

get_users_with_their_teams()
#
# def get_users_access():
#     r = requests.get(confluence_url + 'group/confluence-users/member?&limit=1000', headers = headers)
#     result = r.json();
#
#     confluence_users = []
#     users_from_permissions = []
#
#     for item in get_space_permissions():
#         if item['type'] == 'user':
#              users_from_permissions.append(item['username'])
#
#     for item in result['results']:
#         confluence_users.append(item['username'])
#
#     uniq = [val for val in users_from_permissions if not(val in confluence_users)]
#
#     user_access = []
#     for name in uniq:
#         for item in get_space_permissions():
#             if item['type'] == 'user':
#                 if name in item['username']:
#                     user = {}
#                     user['name'] = item['username']
#                     user['space'] = item['space']
#                     user_access.append(user)
#
#     default_data = {}
#     default_data['name'] = 'dummy'
#     default_data['space'] = 'dummy'
#     user_access.append(default_data)
#
#     return user_access

# def put_data_to_s3_bucket(payload,key,success_message):
#     s3 = boto3.resource('s3')
#     s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload));
#     print success_message
#
# def process(event, context):
#     groups_access = get_groups_access()
#     users_access = get_users_access()
#
#     put_data_to_s3_bucket(groups_access,'Confluence_groups_permissions_to_spaces.json','Uploaded spaces on wich jira-software-users group has access')
#     put_data_to_s3_bucket(users_access,'Confluence_users_permissions_to_spaces.json','Uploaded inactive users that have access to confluence spaces')
