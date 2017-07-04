import os
import json
import urlparse
import requests

headers = {"autopilotapikey": os.environ.get('autopilot_key'), "Content-Type":"application/json"}
autopilot_url = 'https://api2.autopilothq.com/v1/contact'

def process(event, context):
    items = []
    result = urlparse.parse_qs(event['body'])
    items.append(result)
    
    formid = str(items[0]['formid'][0])
    email = str(items[0]['email'][0])
    
    if 'name' in items[0]:
        lead_name = items[0]['name'][0]
        send_data_to_autopilot(formid,email,lead_name)
    else:
        send_data_to_autopilot(formid,email)

    response = {}
    response['isBase64Encoded'] = False
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'application/json'}
    response['body'] = json.dumps('Success') 
    return response;
    
    
def send_data_to_autopilot (formid,email,name=''):    
    
    #academy.opsway.com/test-your-idea
    if (formid == 'form20008826'):
        data = {"contact":{"Email":email, "_autopilot_list":"contactlist_4726CCE6-3BA7-4E7F-8F53-68D8BFA0D5AC"}}
        r = requests.post(autopilot_url, json=data, headers = headers)
        response = r.json();

    #academy.opsway.com/optimize-magento-store
    if (formid == 'form22575448'):
        data = {"contact":{"Email":email, "_autopilot_list":"contactlist_4940B828-3271-4911-8C12-2D2C04AEF932"}}
        r = requests.post(autopilot_url, json=data, headers = headers)
        response = r.json();

    #services.opsway.com/magento-support
    if (formid == 'form21394082'):
        data = {"contact":{"FirstName": name, "Email":email, "_autopilot_list":"contactlist_428AB5B8-84AF-4950-B49A-F266674008B7"}}
        r = requests.post(autopilot_url, json=data, headers = headers)
        response = r.json();
    
    #services.opsway.com/prototyping
    if (formid == 'form22126700' or formid =='form22126710'):
        data = {"contact":{"Email":email, "_autopilot_list":"contactlist_674A3167-5161-4FA4-A8E9-015B78EF2DDC"}}
        r = requests.post(autopilot_url, json=data, headers = headers)
        response = r.json();
    

    print response
    return response