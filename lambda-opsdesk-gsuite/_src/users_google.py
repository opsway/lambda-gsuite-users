
from __future__ import print_function
import httplib2
import os
import json
import tempfile
import base64

from apiclient import discovery
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
ADMIN_USER = os.environ.get('admin_user_email')
#Base65 encoded client_secret.json
CLIENT_SECRET = os.environ.get('client_secret')

## Service Account Configuration https://developers.google.com/admin-sdk/directory/v1/guides/delegation

def main(event, context):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(base64.b64decode(CLIENT_SECRET)), SCOPES)
    delegated_credentials = credentials.create_delegated(ADMIN_USER)

    http = delegated_credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http, cache_discovery=False)

    results = service.users().list(domain='opsway.com',
        orderBy='email').execute()
    users = results.get('users', [])

    result_users = []
    if not users:
        print ({});
    else:
        for user in users:
            result_user = {}
            result_user['fullName'] = user['name']['fullName']
            result_user['firstName'] = user['name']['givenName']
            result_user['lastName'] = user['name']['familyName']
            result_user['email'] = user['primaryEmail']
            result_user['isAdmin'] = user['isAdmin']
            result_user['isDelegatedAdmin'] = user['isDelegatedAdmin']
            result_users.append(result_user)

        response = {}
        response['isBase64Encoded'] = False
        response['statusCode'] = 200
        response['headers'] = {'Content-Type': 'application/json'}
        response['body'] = json.dumps(result_users) 
        return response;

# ADMIN_USER = 'ansam@opsway.com'
# with open('client_secret.json', 'r') as keyfile:
#     CLIENT_SECRET=base64.b64encode(keyfile.read())

# main(1,2);
