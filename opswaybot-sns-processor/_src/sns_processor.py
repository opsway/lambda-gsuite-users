import json

def main(event, context):
    if len(event['Records']) > 1:
        raise Exception('Expecting only 1 record from SNS, got ' + len(event['Records']))

    payload = json.loads(event['Records'][0]['Sns']['Message'])

    if payload['type'] == 'command':
    	command = payload['data']['command'][0]
    	module_name = 'command_' + command[1:]
    	module = __import__(module_name)
    	func = getattr(module, 'process')
    	func(payload['data'])
    elif payload['type'] == 'im':
    	module = __import__('im')
    	func = getattr(module, 'process')
    	func(payload['data'])
    else:
    	raise Exception('Unexpected message type: ' + payload['type'])
    	print event