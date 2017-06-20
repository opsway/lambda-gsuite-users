import requests
import os
import json
import boto3

headers = {"Authorization": os.environ.get('jira_authorize')}
bucket_name = 'opsway-zohobooks-backup';

def jira_clients_access ():
    opsway_url = 'https://opsway.atlassian.net/rest/api/2/group/member?includeInactiveUsers=true&groupname=opsway'
    jira_software_url = 'https://opsway.atlassian.net/rest/api/2/group/member?includeInactiveUsers=true&groupname=jira-software-users'
    jira_servicedesk_url = 'https://opsway.atlassian.net/rest/api/2/group/member?includeInactiveUsers=true&groupname=jira-servicedesk-users'
    projects_url = 'https://opsway.atlassian.net/rest/api/2/project/'

    jira_users = []
    servicedesk_users = []
    opsway_users = []
    clients = []
    projects_keys = []
    client_permissions = []

    opsway_start_at = 0
    opsway_max_result = 50

    jira_start_at = 0
    jira_max_result = 50

    servicedesk_start_at = 0
    servicedesk_max_result = 50

    while True:
        r = requests.get(opsway_url + '&startAt=' + str(opsway_start_at) + '&maxResults=' + str(opsway_max_result), headers = headers)
        result = r.json();
        if (result['values'] == []):
            break;
        for user in result['values']:
            result_user = {}
            result_user['name'] = user['name']
            opsway_users.append(result_user)
        opsway_start_at = opsway_start_at + 50
        opsway_max_result = opsway_max_result + 50

    while True:
        r = requests.get(jira_servicedesk_url + '&startAt=' + str(servicedesk_start_at) + '&maxResults=' + str(servicedesk_max_result), headers = headers)
        result = r.json();
        if (result['values'] == []):
            break;
        for user in result['values']:
            result_user = {}
            result_user['name'] = user['name']
            servicedesk_users.append(result_user)
        servicedesk_start_at = servicedesk_start_at + 50
        servicedesk_max_result = servicedesk_max_result + 50

    while True:
        r = requests.get(jira_software_url + '&startAt=' + str(jira_start_at) + '&maxResults=' + str(jira_max_result), headers = headers)
        result = r.json();
        if (result['values'] == []):
            break;
        for user in result['values']:
            result_user = {}
            result_user['name'] = user['name']
            jira_users.append(result_user)
        jira_start_at = jira_start_at + 50
        jira_max_result = jira_max_result + 50

    for j_user in jira_users:
        success = 1
        for o_user in opsway_users:
            if j_user['name'] == o_user['name']:
                success = 0
                break;
        if success == 1:
            users = {}
            users['name'] = j_user['name']
            clients.append(users)

    for s_user in servicedesk_users:
        success = 1
        for o_user in opsway_users:
            if s_user['name'] == o_user['name']:
                success = 0
                break;
        if success == 1:
            s_users = {}
            users['name'] = j_user['name']
            clients.append(users)

    r = requests.get(projects_url, headers = headers)
    result = r.json();

    for key in result:
        keys = {}
        keys['project_key'] = key['key']
        keys['project_name'] = key['name']
        projects_keys.append(keys)

    for key in projects_keys:
        for client in clients:

            access_url = "https://opsway.atlassian.net/rest/api/2/user/viewissue/search?username=" + client['name'] + "&issueKey=" + key['project_key'] + '-1'
            check_access = requests.get(access_url, headers = headers)
            access_result = check_access.json();

            access = {}

            if (access_result == []):
                access['user_name'] = client['name']
                access['project_name'] = key['project_name']
                access['access'] = ''
            elif ('errorMessages' in access_result):
                access['access'] = "The project has no issues or issue no longer exist"
            else:
                access['user_name'] = client['name']
                access['project_name'] = key['project_name']
                access['project_key'] = key['project_key'] + '-1'
            client_permissions.append(access)

    return client_permissions

def shared_filters ():
    boards_url = 'https://opsway.atlassian.net/rest/agile/1.0/board/'
    filter_url = 'https://opsway.atlassian.net/rest/api/2/filter/'

    filter_ids = []

    r = requests.get(boards_url, headers = headers)
    result = r.json();

    for item in result['values']:
        r = requests.get(boards_url + str(item['id']) + '/configuration', headers = headers)
        result = r.json();
        filter_id = {}
        filter_id['board_name'] = result['name']
        filter_id['filter_id'] = result['filter']['id']
        filter_ids.append(filter_id)

    share_permissions = []
    for item in filter_ids:
        r = requests.get(filter_url + str(item['filter_id']) + '/permission', headers = headers)
        result = r.json();
        for item in result:
            share_permissions.append(item)

    result_permissions = []

    for item in share_permissions:
        filter_permission = {}
        if 'project' in item:
            filter_permission['shared'] = item['project']['name'] + ' project'
            filter_permission['project_link'] = item['project']['self']
        elif 'group' in item:
            filter_permission['shared'] = item['group']['name'] + ' group'
            filter_permission['group_link'] = item['group']['self']
        else:
            filter_permission['shared'] = 'Filter not shared'
        result_permissions.append(filter_permission)

    return result_permissions

def project_permissions ():
    #Find only groups permission, project roles permissions ignored
    permission_schemes_url = 'https://opsway.atlassian.net/rest/api/2/permissionscheme/'
    
    schemes_permissions = []
    projects_access = []
    
    r = requests.get(permission_schemes_url, headers = headers)
    result = r.json();
    
    for item in result['permissionSchemes']:
        r = requests.get(permission_schemes_url + str(item['id']) + '/permission', headers = headers)
        result = r.json();
        for item in result['permissions']:
            schemes_permissions.append(item)
    
    for item in schemes_permissions:
        access = {}
        if item['holder']['type'] == 'group':
            access['holder'] = item['holder']['parameter']
            access['permission_link'] = item['self']
            access['permission_id'] = item['id']
            access['permission_name'] = item['permission']
            projects_access.append(access)
    return projects_access


def main(event, context):
    s3 = boto3.resource('s3')
    key = 'Jira_clients_access.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(jira_clients_access()));
    print 'Uploaded user access list to Jira issues'
    
    key = 'Jira_shared_filters.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(shared_filters()));
    print 'Uploaded jira shared filters'
    
    key = 'Jira_project_permissions.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(project_permissions()));
    print 'Uploaded jira project permissions'

