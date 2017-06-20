import requests
import json
import time
import os
import datetime
from google.cloud import bigquery

def get_logins_with_pagination(url):
    values = []
    page = 1

    while True:         
        r = requests.get(url + '?count=1000&token=' + os.environ['SLACK_TOKEN'] + '&page=' + str(page))
        result = r.json();

        if (r.status_code != 200):
            raise ValueError('Error retrieving date')    

        if ('logins' in result):
            values = values + result['logins']
        else:
            break;

        if (result['paging']['page'] < result['paging']['pages']):
            page = page + 1;
        else:
            break;
    return values;


def main(event, context):
    f = open('client_secret.json', 'w')
    f.write(base64.b64decode(os.environ.get('GOOGLE_CLIENT_SECRET_CONTENTS')))
    f.close()

    table = bigquery.Client().dataset('slack').table('presence_partitioned')
    table.reload()
    rows = []
    for login in get_logins_with_pagination('https://slack.com/api/team.accessLogs'):
        if (time.time() - float(login['date_first']) < 48 * 60 * 60):
        # We need 48 hours of recent history, as Slack does not allow sessions longer than 24 hours
            login['date_first'] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(login['date_first']))
            login['date_last'] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(login['date_last'])) 
            rows.append(login)

        errors = table.insert_data(rows)
        if errors:
            raise Exception(errors)
