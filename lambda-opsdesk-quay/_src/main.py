import requests
import os
import json
import boto3

bucket_name = 'opsway-zohobooks-backup'
headers = {"Authorization": os.environ.get('quay_auth')}
quay_api_url = 'https://quay.io/api/v1/'

def send_request(url):
	r = requests.get(quay_api_url + url, headers = headers)
	result = r.json()

	return result

def get_org_repos():
	org_repos = send_request('repository?namespace=opsway')
	repos_names = []

	for repo in org_repos['repositories']:
		repos_names.append(repo['name'])

	return repos_names

def get_org_members():
	data = send_request('organization/opsway/members')
	org_members = []

	for member in data['members']:
		for team in member['teams']:
			members = {}
			members['name'] = member['name']
			members['team'] = team['name']
			org_members.append(members)

	return org_members

def get_permissions_for_repos(data):
	repos = get_org_repos()

	permissions = []

	for repo in repos:
		repo_perms = {}
		url = 'repository/opsway/' + str(repo) + '/permissions/' + data
		raw_data = send_request(url)
		repo_perms['repo'] = repo
		if data == 'user':
			for user in raw_data['permissions'].keys():
				repo_perms['user'] = user
		else:
			for team in raw_data['permissions'].keys():
				repo_perms['team'] = team

		permissions.append(repo_perms)

	return permissions


def org_permissions():
	org_permissions = get_permissions_for_repos('user') + get_permissions_for_repos('team')
	return org_permissions



def put_data_to_s3_bucket(payload, key, success_message):
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(payload))
    print success_message


def process(event, context):
    put_data_to_s3_bucket(org_permissions(), 'Quay_org_permissions.json', 'Uploaded quay org permissions for users and teams')
    put_data_to_s3_bucket(get_org_members(), 'Quay_members.json', 'Uploaded quay org memebers')



