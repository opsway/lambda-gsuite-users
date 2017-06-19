import requests
import os
import json
import urlparse

headers = {"Authorization": os.environ.get('Authorization'), "Content-Type": "application/json"}
api_path = "https://opsway.atlassian.net/rest/api/2/"
onduty_groupname = os.environ.get('onduty_groupname')

def set_onduty_user(username):
    url = api_path + 'group/member?includeInactiveUsers=false&groupname='+onduty_groupname    
    for user in get_results_with_pagination(url):
        remove_user_from_group(user)
    add_user_to_group(username)

def remove_user_from_group(user):
    url = 'group/user?groupname=' + onduty_groupname + '&username=' + user['name']
    r = requests.delete(api_path + url, headers = headers)
    if (r.status_code != 200):
        raise ValueError('Error deleting user from group')

def add_user_to_group(username):
    url = 'group/user?groupname=' + onduty_groupname

    payload = json.dumps({'name': username})
    r = requests.post(api_path + url, headers = headers, data=payload)
    if (r.status_code != 201):
        raise ValueError('Error adding user to group')


def get_results_with_pagination(url):
    values = []
    while True:  
        r = requests.get(url, headers = headers)
        result = r.json();
        if (r.status_code != 200):
            raise ValueError('Error retrieving date')    

        values = values + result['values']
        
        if ('nextPage' in result):
            url = result['nextPage'];
        else:
            break;
        
    return values;

def main(event, context):
    data = urlparse.parse_qs(event['body'])
    set_onduty_user(data['username'][0])

    response = {}
    response['isBase64Encoded'] = False
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'application/json'}
    response['body'] =  ''
    return response
