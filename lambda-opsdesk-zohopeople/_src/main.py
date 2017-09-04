import requests
import os
import json
import boto3

bucket_name = 'opsway-zohobooks-backup'
zoho_people_auth = os.environ.get('zoho_people_auth')
zoho_people_api_url = 'https://people.zoho.com/people/api/'

def get_all_users():
    url = 'forms/P_EmployeeView/records'
    r = requests.get(zoho_people_api_url + url + '?authtoken=' + zoho_people_auth)
    result = r.json()
    
    zoho_people_users = []

    for user in result:
        raw_list = {}
        raw_list['employee_id'] = user['EmployeeID']
        raw_list['first_name'] = user['First Name']
        raw_list['last_name'] = user['Last Name']
        raw_list['email'] = user['Email ID']
        raw_list['reporting_to'] = user['Reporting To']
        raw_list['job_description'] = user['Job Description']
        raw_list['date_of_joining'] = user['Date of joining']
        raw_list['employee_status'] = user['Employee Status']
        raw_list['department'] = user['Department']
        raw_list['employee_role'] = user['Employee Role']
        raw_list['approval_status'] = user['ApprovalStatus']
        raw_list['birth_date'] = user['Birth Date']
        raw_list['owner_id'] = user['ownerID']
        zoho_people_users.append(raw_list)

    return zoho_people_users

def get_user_goals():
    url = 'forms/P_Goals/getRecords'
    r = requests.get(zoho_people_api_url + url + '?authtoken=' + zoho_people_auth)
    result = r.json()

    user_goals = []

    for goal in result['response']['result']:
        goals = {}
        goals['goal_name'] = goal.items()[0][1][0]['GoalName']
        goals['description'] = goal.items()[0][1][0]['Description']
        goals['assigned_to'] = goal.items()[0][1][0]['AssignedTo']
        goals['assigned_by'] = goal.items()[0][1][0]['AssignedBy']
        goals['due_date'] = goal.items()[0][1][0]['DueDate']
        goals['progress'] = goal.items()[0][1][0]['Progress']
        goals['modified_time'] = goal.items()[0][1][0]['ModifiedTime']
        goals['zoho_id'] = goal.items()[0][1][0]['Zoho_ID']
        goals['approval_status'] = goal.items()[0][1][0]['ApprovalStatus']
        goals['assigned_to_id'] = goal.items()[0][1][0]['AssignedTo.ID']
        goals['created_time'] = goal.items()[0][1][0]['CreatedTime']
        user_goals.append(goals)

    return user_goals

def put_data_to_s3_bucket(payload, key, success_message):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload))
    print success_message


def process(event, context):
    put_data_to_s3_bucket(get_all_users(), 'ZohoPeople_users.json', 'Uploaded ZohoPeople users list.')
    put_data_to_s3_bucket(get_user_goals(), 'ZohoPeople_users_goals.json', 'Uploaded ZohoPeople users goals.')

