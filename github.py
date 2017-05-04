import requests
import os
import json
import boto3

headers = {"Authorization": os.environ.get('Authorization')}
bucket_name = 'opsway-zohobooks-backup';

def get_members_list():
    url = 'https://api.github.com/orgs/opsway/members'
    
    raw_list = []
    page = 1
    while True:  
        r = requests.get(url + '?page=' + str(page), headers = headers)
        result = r.json();
        if (result == []):
            break;
        raw_list = raw_list + result
        page = page + 1
    return raw_list

def get_members():
    members = []
    for member_raw in get_members_list():
        url =  'https://api.github.com/users/' + member_raw['login']
        r = requests.get(url, headers = headers)
        result = r.json();
        members.append(result)
    return members;


def get_repos_acl():
    url = 'https://api.github.com/orgs/opsway/repos'
    
    raw_list = []
    page = 1
    while True:  
        r = requests.get(url + '?page=' + str(page), headers = headers)
        result = r.json();
        if (result == []):
            break;
        raw_list = raw_list + result
        page = page + 1
    return raw_list


def get_collaborators():
    collaborators = []
    for repo_raw in get_repos_acl():
        url = "https://api.github.com/repos/opsway/" + repo_raw['name'] + "/collaborators"
        r = requests.get(url, headers = headers)
        result = r.json();
        for item in result:
            repo = {}
            repo['project_name'] = repo_raw['name']
            repo['collaborator'] = item['login']
            repo['private'] = repo_raw['private']
            repo['fork'] = repo_raw['fork']
            repo['site_admin'] = item['site_admin']
            repo['permissions'] = item['permissions']
            collaborators.append(repo)
    return collaborators;

def get_presigned_url(key):
    s3 = boto3.client('s3')
    url = s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': bucket_name,
        'Key': key
    }
    )
    print url

def main(event, context):
    s3 = boto3.resource('s3')
    key = 'github_members.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(get_members()));
    print 'Uploaded github members'

    key = 'github_project_acl.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(get_collaborators()));
    print 'Uploaded github collaborators'   