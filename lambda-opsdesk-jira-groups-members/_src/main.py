import requests
import os
import json
import boto3

bucket_name = 'opsway-zohobooks-backup'
jira_api_path = 'https://opsway.atlassian.net/rest/api/2/'
headers = {"Authorization": os.environ.get('jira_authorize')}


def get_jira_groups_members_with_pagination(group_name):
    users = []

    start_at = 0
    max_result = 50

    url = 'group/member?includeInactiveUsers=true'

    while True:
        r = requests.get(jira_api_path + url + '&startAt=' + str(start_at) +
                         '&maxResults=' + str(max_result) + '&groupname=' + group_name, headers=headers)
        result = r.json()

        if (result['values'] == []):
            break

        users += result['values']

        start_at = max_result
        max_result += 50

    return users


def put_data_to_s3_bucket(payload, key, success_message):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload))
    print success_message


def process(event, context):
    put_data_to_s3_bucket(get_jira_groups_members_with_pagination(
        'jira-software-users'), 'Jira_software_users.json', 'Uploaded jira-software-users group members')
    put_data_to_s3_bucket(get_jira_groups_members_with_pagination(
        'jira-servicedesk-users'), 'Jira_servicedesk_users.json', 'Uploaded jira-servicedesk-users group members')
    put_data_to_s3_bucket(get_jira_groups_members_with_pagination(
        'opsway'), 'Jira_opsway_users.json', 'Uploaded opsway group members')
