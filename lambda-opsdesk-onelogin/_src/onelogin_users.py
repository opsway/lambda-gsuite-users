import requests
import os
import json

def get_access_token():
    url = 'https://api.us.onelogin.com/auth/oauth2/token'
    params = {"grant_type":"client_credentials"}
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    headers = {"Authorization": "client_id:"+client_id +", client_secret:" + client_secret,
                "Content-Type": "application/json"
            }
    r = requests.post(url, params = params, headers = headers)
    result = r.json()
    return result['data'][0]['access_token']

def get_users(event, context):
    url = 'https://api.us.onelogin.com/api/1/users'
    headers = {"Authorization": "bearer:" + get_access_token()}
    
    users = []
    while True:  
        r = requests.get(url, headers = headers)
        result = r.json();
        url = result['pagination']['next_link'];
        users = users + result['data']
        if (url == None):
            break;

    print len(users)
    response = {}
    response['isBase64Encoded'] = False
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'application/json'}
    response['body'] = json.dumps(users) 
    return response;
