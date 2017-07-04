import requests
import os
import json
import boto3

headers = {"Authorization": os.environ.get('jira_authorize')}
jira_url = 'https://opsway.atlassian.net/rest/api/2/'
bucket_name = 'opsway-zohobooks-backup';

def get_jira_clients_with_pagination ():
    clients = []
    opsway_users = []
    jira_software_users = []
    jira_servicedesk_users = []

    start_at = 0
    max_result = 50
    j_start_at = 0
    j_max_result = 50
    s_start_at = 0
    s_max_result = 50


    while True:
        opsway_g = requests.get(jira_url + 'group/member?' + 'includeInactiveUsers=false' + '&startAt=' + str(start_at) + '&maxResults=' + str(max_result) + '&groupname=opsway', headers = headers)
        opsway = opsway_g.json();
        if (opsway['values'] == []):
            break;
        for user in opsway['values']:
            result_user = {}
            result_user['name'] = user['name']
            opsway_users.append(result_user)
        start_at = start_at + 50
        max_result = max_result + 50

    while True:
        jira_software_g = requests.get(jira_url  + 'group/member?' + 'includeInactiveUsers=false'  + '&startAt=' + str(j_start_at) + '&maxResults=' + str(j_max_result) + '&groupname=jira-software-users', headers = headers)
        jira_software = jira_software_g.json();
        if (jira_software['values'] == []):
            break;
        for user in jira_software['values']:
            result_user = {}
            result_user['name'] = user['name']
            jira_software_users.append(result_user)
        j_start_at = j_start_at + 50
        j_max_result = j_max_result + 50

    while True:
        jira_servicedesk_g = requests.get(jira_url  + 'group/member?' + 'includeInactiveUsers=false'  + '&startAt=' + str(s_start_at) + '&maxResults=' + str(s_max_result) + '&groupname=jira-servicedesk-users', headers = headers)
        jira_servicedesk = jira_servicedesk_g.json();
        if (jira_servicedesk['values'] == []):
            break;
        for user in jira_servicedesk['values']:
            result_user = {}
            result_user['name'] = user['name']
            jira_servicedesk_users.append(result_user)
        s_start_at = s_start_at + 50
        s_max_result = s_max_result + 50

    for j_user in jira_software_users:
        success = 1
        for o_user in opsway_users:
            if j_user['name'] == o_user['name']:
                success = 0
                break;
        if success == 1:
            users = {}
            users['name'] = j_user['name']
            clients.append(users)

    for s_user in jira_servicedesk_users:
        success = 1
        for o_user in opsway_users:
            if s_user['name'] == o_user['name']:
                success = 0
                break;
        if success == 1:
            users = {}
            users['name'] = s_user['name']
            clients.append(users)

    return clients

def get_clients_group_membership ():
    client_groups = []
    
    for client in get_jira_clients_with_pagination():
        r = requests.get(jira_url + 'user?username=' + client['name'] + '&expand=groups' , headers = headers)
        result = r.json();
        for group in result['groups']['items']:
            if (group['name'] != 'jira-software-users'):
                error = {}
                error['client_name'] = client['name']
                error['member_of'] = group['name']
                client_groups.append(error)
    
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
        r = requests.get(jira_url + 'filter/'+ str(item['filter_id']) + '/permission', headers = headers)
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
    
    return share_permissions

def get_project_permissions ():

    schemes_permissions = []
    projects_access = []

    r = requests.get(jira_url + 'permissionscheme/', headers = headers)
    result = r.json();

    for item in result['permissionSchemes']:
        r = requests.get(jira_url + 'permissionscheme/' + str(item['id']) + '/permission', headers = headers)
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
    return projects_access
    
def process(event, context):
    s3 = boto3.resource('s3')
    key = 'Jira_clients_access.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(get_clients_group_membership()));
    print 'Uploaded jira clients who have more groups than only Jira-software-users'

    key = 'Jira_shared_filters.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(get_shared_filters()));
    print 'Uploaded jira shared filters'

    key = 'Jira_project_permissions.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(get_project_permissions()));
    print 'Uploaded jira project permissions'

