import requests
import time
import os
import sys
import tempfile
import base64
import csv
import datetime
import json


# If python gives error "Can not find module google", just add file __init__.py to google and google/cloud directory
from google.cloud import bigquery


def auth_google_cloud_sdk():
    # Copy file with google secret from Lambda environment settings
    google_secret_file = tempfile.mkdtemp() + '/client_secret.json'
    f = open(google_secret_file, 'w')
    f.write(base64.b64decode(os.environ.get('GOOGLE_CLIENT_SECRET_CONTENTS')))
    f.close()
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_secret_file



def export_slackaccesslog(event, context):
    auth_google_cloud_sdk()

    table = bigquery.Client().dataset('slack').table('logins_partitioned')
    table.reload()
    rows = []
    for login in get_logins_with_pagination('https://slack.com/api/team.accessLogs'):
        if (time.time() - float(login['date_first']) < 48 * 60):
        # We need 48 hours of recent history, as Slack does not allow sessions longer than 24 hours
            login['date_first'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(login['date_first']))
            login['date_last'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(login['date_last'])) 
            
            rows.append((login['username'],login['count'],login['user_id'],
                login['ip'],login['region'], login['isp'], login['user_agent'], login['country'], 
                login['date_first'], login['date_last']))

    print "Sending " + str(len(rows)) + " records to BigQuery ..."
    errors = table.insert_data(rows)
    if errors:
        print (errors)
        raise Exception(errors)