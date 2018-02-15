import requests
import os
import json
import boto3

headers = {"Authorization": os.environ.get('jira_authorize')}
project_category = os.environ.get('project_category')
bucket_name = 'opsway-zohobooks-backup';
jira_api_path = 'https://opsway.atlassian.net/rest/api/2/'


def get_issues_by_category():
    issues = []
    
    start_at = 0
    max_result = 100
    
    url = "search?jql=category = " + project_category + " AND updated > startOfMonth(-1)"
    # url = "search?jql=category = " + project_category + " AND created >= '2017-10-16'"
    
    while True:
        r = requests.get(jira_api_path + url + '&startAt=' + str(start_at) +
                        '&maxResults=' + str(max_result), headers = headers)
        result = r.json();
        
        for issue_block in result['issues']:
            issues.append(issue_block)

        if (result['issues'] == []):
            break;

        start_at = max_result
        max_result += 100
    return issues
    
def put_data_to_s3_bucket(payload,key,success_message):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload));
    print success_message

def process(event, context):
    support_issues = get_issues_by_category()
    put_data_to_s3_bucket(support_issues,'Jira_watchers_support_issues.json','Uploaded jira watchers support issues')