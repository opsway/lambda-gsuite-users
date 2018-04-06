import requests, os, xmltodict, json, boto3, datetime, calendar
from datetime import timedelta

bucket_name = os.environ.get('BUCKET_NAME')
tempo_api_key = os.environ.get('TEMPO_API_KEY')
date_now = datetime.datetime.now()

def get_date(key):
    date_from = (date_now + timedelta(days=-30)).strftime("%Y-%m-%d")
    date_to = date_now.strftime("%Y-%m-%d")

    if key == 'date_from':
        return str(date_from)
    elif key == 'date_to':
        return str(date_to)
    else:
        print 'Please pass the argument!'

api_url = 'https://opsway.atlassian.net/plugins/servlet/tempo-getWorklog/?baseUrl=https://opsway.atlassian.net&dateFrom=' + get_date('date_from') + '&dateTo=' + get_date('date_to') + '&format=xml&diffOnly=false&addApprovalStatus=true&tempoApiToken=' + str(tempo_api_key)

def put_data_to_s3(data):
    s3 = boto3.resource('s3')
    key = 'tempo_data.json'
    s3.Bucket(bucket_name).put_object(Key=key, Body=json.dumps(data))
    print 'Jira Tempo data for current month downloaded to S3'

def process(event, context):
    r = requests.get(api_url)

    if r.status_code == 200:
        put_data_to_s3(xmltodict.parse(r.content))
    else:
        print 'Response code is ' + str(r.status_code)













