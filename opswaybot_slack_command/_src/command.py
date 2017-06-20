import json
import urlparse
import boto3
import os

def publish_message(data):
    client = boto3.client('sns')
    sns_topic = os.environ.get('SNS_TOPIC')

    sns_response = client.publish(
        TopicArn=sns_topic,
        Message=json.dumps(data),
        Subject='string'
    )

def get_response():
    response = {}
    body = {
        'text': 'Processing your command...'
    }

    response['isBase64Encoded'] = False
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'application/json'}
    response['body'] = json.dumps(body)
    return response


def verify_token(data):
    if os.environ.get('VERIFICATION_TOKEN') != data['data']['token'][0]:
        raise Exception('Incorrect token')

def main(event, context):
    data = {}
    data['type'] = 'command'
    data['data'] = urlparse.parse_qs(event['body'])
    verify_token(data)
    publish_message(data)
    return get_response()