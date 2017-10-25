import requests
import os
import json

headers = {"Authorization": os.environ.get('jira_authorize')}
jira_api_path = 'https://opsway.atlassian.net/rest/api/2/'

def process(event, context):
    issues = []
    
    start_at = 0
    max_result = 100
    
    url = 'search?jql=created>startOfDay(-1d)'

    while True:
        r = requests.get(jira_api_path + url + '&startAt=' + str(start_at) +
                                '&maxResults=' + str(max_result), headers = headers)
        result = r.json();
        
        if (result['issues'] == []):
            break;
        
        issues.append(result['issues'])
        
        start_at = max_result
        max_result += 100
    response = {}
    response['isBase64Encoded'] = False
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'application/json'}
    response['body'] = json.dumps(issues)
    return response
