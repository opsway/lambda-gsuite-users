import requests
import os
import json
import boto3

git_api_path = 'https://api.github.com/'
headers = {"Authorization": os.environ.get('Authorization')}
bucket_name = 'opsway-zohobooks-backup';

def get_members_list():
    url = 'orgs/opsway/members'
    
    raw_list = []
    page = 1
    while True:  
        r = requests.get(git_api_path + url + '?page=' + str(page), headers = headers)
        result = r.json();
        if (result == []):
            break;
        raw_list += result
        page = page + 1
    return raw_list

def get_teams_list():
    url = 'orgs/opsway/teams'
    
    teams = []
    r = requests.get(git_api_path + url, headers = headers)
    result = r.json();
    teams += result
    
    return teams

def get_teams_members():
    url = 'teams/'
    
    team_members = []
    for team in get_teams_list():
        r = requests.get(git_api_path + url + str(team['id']) + '/members', headers = headers)
        result = r.json();
        for user in result:
            member = {}
            member['team_name'] = team['name']
            member['username'] = user['login']
            team_members.append(member)
    return team_members
        
def get_members():
    members = []
    for member_raw in get_members_list():
        url =  git_api_path + 'users/' + member_raw['login']
        r = requests.get(url, headers = headers)
        result = r.json();
        members.append(result)
    return members;


def get_repos_acl():
    url = 'orgs/opsway/repos'

    raw_list = []
    page = 1
    while True:
        r = requests.get(git_api_path + url + '?page=' + str(page), headers = headers)
        result = r.json();
        if (result == []):
            break;
        raw_list = raw_list + result
        page = page + 1
    return raw_list


def get_collaborators():
    collaborators = []
    for repo_raw in get_repos_acl():
        url = git_api_path + "repos/opsway/" + repo_raw['name'] + "/collaborators"
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

def put_data_to_s3_bucket(payload,key,success_message):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload));
    print success_message

def process(event, context):
    github_members = get_members()
    github_project_acl = get_collaborators()
    github_teams_members = get_teams_members()
    
    put_data_to_s3_bucket(github_members,'github_members.json','Uploaded github members')
    put_data_to_s3_bucket(github_project_acl,'github_project_acl.json','Uploaded github collaborators')
    put_data_to_s3_bucket(github_teams_members,'github_teams_members.json','Uploaded github teams members')