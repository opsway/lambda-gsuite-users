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


class InMemoryCSVWriter():
    def __init__(self):
        self.contents = ''
    
    def write(self,str):
        self.contents += str

    def render(self):
        return self.contents


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


def auth_google_cloud_sdk():
    # Copy file with google secret from Lambda environment settings
    google_secret_file = tempfile.mkdtemp() + '/client_secret.json'
    f = open(google_secret_file, 'w')
    f.write(base64.b64decode(os.environ.get('GOOGLE_CLIENT_SECRET_CONTENTS')))
    f.close()
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_secret_file

def get_sql(event):
    return "SELECT * FROM " + get_dataset(event) + "." + get_table(event)


def get_table(event):
    if (not 'queryStringParameters' in event or not 'table' in event['queryStringParameters']):
            raise Exception("Expecting table parameter")
    table = event['queryStringParameters']['table']
    if ' ' in table.lower():
        raise Exception("Table parameter should be one word without spaces") 
    return table


def get_dataset(event):
    if (not 'queryStringParameters' in event or not 'dataset' in event['queryStringParameters']):
            raise Exception("Expecting dataset parameter")
    dataset = event['queryStringParameters']['dataset']
    if ' ' in dataset.lower():
        raise Exception("Dataset parameter should be one word without spaces") 
    return dataset


def get_column_names(dataset, table):
    dataset = bigquery.Client().dataset(dataset)
    table = dataset.table(table)
    table.reload()
    column_names = []
    for field in table.schema:
        column_names.append(field.name)
    return column_names

def run_sql(event, context):
    auth_google_cloud_sdk()

    dataset = get_dataset(event)
    table = get_table(event)

    sql = "SELECT * FROM " + dataset + "." + table 

    print "Running SQL: " + sql

    values = []
    values.append(get_column_names(dataset,table));

    client = bigquery.Client()
    query_results = client.run_sync_query(sql)

    query_results.use_legacy_sql = False
    query_results.run()

    rows, total_rows, page_token = query_results.fetch_data()

    for row in rows:
        values.append(row)
              
    return render_response(values)


def render_response(rows):
    out = InMemoryCSVWriter()
    csv_writer = csv.writer(out, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
    csv_writer.writerows(rows)

    response = {}
    response['isBase64Encoded'] = False
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'text/csv'}
    response['body'] = out.render()

    return response