# Code is based on convention that for each team there are two groups:
# onduty-teamname (active onduty engineer)
# onduty-list-teamname (all possible onduty engineers)
# This processor removes all users from target groups leaving only user who asked to be checked-in

import requests
import os
import json
import boto3

headers = {'Authorization': os.environ.get('JIRA_Authorization'), 'Content-Type': 'application/json'}
jira_api_path = 'https://opsway.atlassian.net/rest/api/2/'

def publish_message(data):
    client = boto3.client('sns')
    sns_topic = os.environ.get('SNS_TOPIC')
    sns_response = client.publish(
        TopicArn=sns_topic,
        Message=json.dumps(data),
        Subject='string'
    )

def process(message):
	username = message['user_name'][0]
	print 'Processing command onduty for ' + username
	groups_updated = []
	groups = get_available_onduty_groups(username)
	for group in groups:
		onduty_groupname = group.replace('-list','')
		remove_all_users_from_group(onduty_groupname)
		add_user_to_group(username, onduty_groupname)
		groups_updated.append(onduty_groupname.replace('onduty-',''))
	post_response(groups_updated, message['response_url'][0])
	broadcast(username, groups_updated)

def broadcast(onduty_username, groups):
	for group in groups:
		groupname = 'onduty-list-' + group
		print 'Broadcasting notification to ' +  groupname
		user_names = get_users_in_group(groupname)
		for user_name in user_names:
			message = {}
			message['type'] = 'im'
			# This is required as Slack impose rate limits
			# https://api.slack.com/docs/rate-limits
			# So we expect that on average every message will be sent once in 2 seconds
			message['sleep'] = 2 * len(groups)
			message['data'] = {'to_name' : user_name, 'text' : '@' + onduty_username + ' is on duty in JIRA/' + group}
			publish_message(message)

def post_response(groups, response_url):
	if len(groups) == 0:
		response = { 'text': 'Can not set you on duty - no groups available'}
		print 'Sending response to user: ' + response['text']
		headers = {'content-type': 'application/json'}
		r = requests.post(response_url, data = json.dumps(response), headers = headers)
		if (r.status_code != 200):
			raise ValueError('Error while sending data back')

def get_users_in_group(groupname):
	url = 'group/member?includeInactiveUsers=true&groupname=' + groupname
	r = requests.get(jira_api_path + url, headers = headers)
	result = r.json();
	if (r.status_code != 200):
		raise ValueError('Error retrieving data')
	users = result['values']
	users_in_group = []
	for user in users:
		users_in_group.append(user['name'])
	return users_in_group

def get_available_onduty_groups(username):
	url = 'user?username=' + username + '&expand=groups';
	r = requests.get(jira_api_path + url, headers = headers)
	result = r.json();
	if (r.status_code != 200):
		raise ValueError('Error retrieving data')
		
	usergroups = result['groups']['items']
	available_groups = []
	for usergroup in usergroups:
		if '-list-' in usergroup['name']:
			available_groups.append(usergroup['name'])
	return available_groups 

def remove_all_users_from_group(groupname):
	url = 'group/member?includeInactiveUsers=false&groupname='+groupname   
	for user in get_results_with_pagination(url):
		remove_user_from_group(user, groupname)

def remove_user_from_group(user, groupname):
	url = 'group/user?groupname=' + groupname + '&username=' + user['name']
	r = requests.delete(jira_api_path + url, headers = headers)
	if (r.status_code != 200):
		raise ValueError('Error deleting user from group')

def add_user_to_group(username, groupname):
	url = 'group/user?groupname=' + groupname

	payload = json.dumps({'name': username})
	r = requests.post(jira_api_path + url, headers = headers, data=payload)
	if (r.status_code != 201):
		raise ValueError('Error adding user to group')

def get_results_with_pagination(url):
	values = []
	while True:  
		r = requests.get(jira_api_path + url, headers = headers)
		result = r.json();
		if (r.status_code != 200):
			raise ValueError('Error retrieving data')	
		values = values + result['values']
		
		if ('nextPage' in result):
			url = result['nextPage'];
		else:
			break;
		
	return values;