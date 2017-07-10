import requests
import os
import json
import boto3

headers = {"Authorization": os.environ.get('jira_authorize')}
jira_api_path = 'https://opsway.atlassian.net/rest/api/2/'
bucket_name = 'opsway-zohobooks-backup';

def get_jira_users_from_group_with_pagination(group_name):
    users = []
    
    start_at = 0
    max_result = 50
    
    url = 'group/member?includeInactiveUsers=false'
    
    while True:
        r = requests.get(jira_api_path + url + '&startAt=' + str(start_at) +
                                '&maxResults=' + str(max_result) + '&groupname=' + group_name, headers = headers)
        result = r.json();
        if (result['values'] == []):
            break;
        for item in result['values']:
            user = {}
            user['name'] = item['name']
            users.append(user)
        start_at = max_result
        max_result += 50
    
    return users
    
def get_only_clients(group_users):
    opsway_users = []
    opsway_users += get_jira_users_from_group_with_pagination('opsway')
    
    clients = []
    for user in group_users:
        success = 1
        for o_user in opsway_users:
            if user['name'] == o_user['name']:
                success = 0
                break;
        if success == 1:
            users = {}
            users['name'] = user['name']
            clients.append(users)
    
    return clients


def get_clients_group_membership():
    clients = []
    
    jira_software_users = []
    jira_software_users += get_jira_users_from_group_with_pagination('jira-software-users')
    clients += get_only_clients(jira_software_users)
    
    jira_servicedesk_users = []
    jira_servicedesk_users += get_jira_users_from_group_with_pagination('jira-servicedesk-users')
    clients += get_only_clients(jira_servicedesk_users)
    
    client_groups = []

    for client in clients:
        r = requests.get(jira_api_path + 'user?username=' + client['name'] + '&expand=groups' , headers = headers)
        result = r.json();
        for group in result['groups']['items']:
            if (group['name'] != 'jira-software-users'):
                error = {}
                error['client_name'] = client['name']
                error['member_of'] = group['name']
                client_groups.append(error)
    
    default_data = {}
    default_data['client_name'] = 'dummy'
    default_data['member_of'] = 'dummy'
    client_groups.append(default_data)

    return client_groups

def get_shared_filters ():

    boards_url = 'https://opsway.atlassian.net/rest/agile/1.0/board/'

    filter_ids = []

    r = requests.get(boards_url, headers = headers)
    result = r.json();

    for item in result['values']:
        r = requests.get(boards_url + str(item['id']) + '/configuration', headers = headers)
        result = r.json();
        filter_id = {}
        filter_id['board_name'] = result['name']
        filter_id['board_link'] = result['self']
        filter_id['board_type'] = result['type']
        filter_id['filter_id'] = result['filter']['id']
        filter_id['filter_link'] = result['filter']['self']
        filter_ids.append(filter_id)

    share_permissions = []

    for item in filter_ids:
        r = requests.get(jira_api_path + 'filter/'+ str(item['filter_id']) + '/permission', headers = headers)
        result = r.json();
        for s_filter in result:
            if ('group' in s_filter and s_filter['group']['name'] == 'jira-software-users'):
                filter_permission = {}
                filter_permission['board_name'] = item['board_name']
                filter_permission['board_link'] = item['board_link']
                filter_permission['board_type'] = item['board_type']
                filter_permission['filter_link'] = item['filter_link']
                filter_permission['filter_id'] = item['filter_id']
                filter_permission['group'] = s_filter['group']['name']
                share_permissions.append(filter_permission)
                
    default_data = {}
    default_data['board_name'] = 'dummy'
    default_data['board_link'] = 'dummy'
    default_data['board_type'] = 'dummy'
    default_data['filter_link'] = 'dummy'
    default_data['filter_id'] = 'dummy'
    default_data['group'] = 'dummy'
    share_permissions.append(default_data)

    return share_permissions

def get_project_permissions ():

    schemes_permissions = []
    projects_access = []

    r = requests.get(jira_api_path + 'permissionscheme/', headers = headers)
    result = r.json();

    for item in result['permissionSchemes']:
        r = requests.get(jira_api_path + 'permissionscheme/' + str(item['id']) + '/permission', headers = headers)
        result = r.json();
        for item in result['permissions']:
            schemes_permissions.append(item)

    for item in schemes_permissions:
        access = {}
        if item['holder']['type'] == 'group':
            if item['holder']['parameter'] == 'jira-software-users':
                access['holder'] = item['holder']['parameter']
                access['permission_link'] = item['self']
                access['permission_id'] = item['id']
                access['permission_name'] = item['permission']
                projects_access.append(access)
    
    default_data = {}
    default_data['holder'] = 'dummy'
    default_data['permission_link'] = 'dummy'
    default_data['permission_id'] = 'dummy'
    default_data['permission_name'] = 'dummy'
    projects_access.append(default_data)
    
    return projects_access

def put_data_to_s3_bucket(payload,key,success_message):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload));
    print success_message

def process(event, context):
    clients_group_membership = get_clients_group_membership()
    shared_filters = get_shared_filters()
    project_permissions = get_project_permissions()
    
    put_data_to_s3_bucket(clients_group_membership,'Jira_clients_access.json','Uploaded jira clients who have more groups than only Jira-software-users')
    put_data_to_s3_bucket(shared_filters,'Jira_shared_filters.json','Uploaded jira shared filters')
    put_data_to_s3_bucket(project_permissions,'Jira_project_permissions.json','Uploaded jira project permissions')

