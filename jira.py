import requests
import os
import json

headers = {"Authorization": "Basic YW5zYW06d2lraVBhJCQyMDE3"}
url_base = "https://opsway.atlassian.net"

def get_group_users(groupname):
    url = url_base + '/rest/api/2/group/member?includeInactiveUsers=false&groupname='+groupname    
    
    users = []
    while True:  
        r = requests.get(url, headers = headers)
        result = r.json();
        url = result['nextPage'];
        users = users + result['values']
        if (url == None):
            break;
    return users;


all_jira_users = get_group_users('jira-software-users')
opsway_jira_users = get_group_users('opsway')

