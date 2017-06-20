#!/usr/bin/env python
import os
import json
import sys
import boto3
import time
import uuid
import datetime
import os
from dateutil import parser
from trello import TrelloClient

client = TrelloClient(
    api_key= os.environ.get('trelloApiKey'),
    token= os.environ.get('trelloToken'),
)

cache = {}
cards = []
cache_in_file = False;
cache_local_path = '/Users/ansam/Downloads/'
cache_file_prefix = 'trello_cards_'
config_board_id = os.environ.get('boardId')

def load_cache():
	data = {};
	if cache_in_file:
		with open(cache_local_path + cache_file_prefix + config_board_id + '.json') as data_file:    
		    data = json.load(data_file);

	else:
		s3 = boto3.resource('s3');
		key = cache_file_prefix + config_board_id + '.json';
		download_path = '/tmp/{}{}'.format(uuid.uuid4(), key);
		s3.Bucket('opsway-zohobooks-backup').download_file(key, download_path);
		with open(download_path) as data_file:    
			data = json.load(data_file);
	
	for card in data:
		cache[card['id']] = card;

def save_cache(cards):
	if cache_in_file:
		with open(cache_local_path + cache_file_prefix + config_board_id + '.json', 'w') as outfile:
			json.dump(cards, outfile);
	else:
		s3 = boto3.resource('s3')
		key = 'trello_cards_' + config_board_id + '.json'
		s3.Bucket('opsway-zohobooks-backup').put_object(Key=key, Body=json.dumps(cards));	

def get_cache(card_id, last_updated_at_unix):
	if ((card_id in cache) and cache[card_id]['last_updated_at_unix'] == last_updated_at_unix):
		return cache[card_id];
	else: 
		return None;

def get_card_estimation(custom_fields):
	if (custom_fields):
		json_obj = json.loads(custom_fields);
		if ('Mumoqgty-2h3LmQ' in json_obj['fields'].keys()):
			return int(round(float(json_obj['fields']['Mumoqgty-2h3LmQ'])));		
	return ''

def get_card_type(custom_fields):
	if (custom_fields):
		json_obj = json.loads(custom_fields);
		if not ('Mumoqgty-9vgr6q' in json_obj['fields'].keys()):
			return 'request'
		card_encoded_type = json_obj['fields']['Mumoqgty-9vgr6q'];
		if card_encoded_type == '7YXU3m':
			return 'requirement'
		elif card_encoded_type == 'xyzpY0':
			return 'task'
	return 'unknown'

def get_card_labels(labels):
	label_str = ""
	for label in labels:
		if len(label_str) == 0:
			label_str = label_str + label.name 
		else:
			label_str = label_str + "," + label.name 
	return label_str


def main(event, context):
	load_cache();
	board = client.get_board(config_board_id);
	current_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S');
	card_ids = []; 
	for card in board.get_cards():
		last_updated_at_unix = time.mktime(card.dateLastActivity.timetuple());
		card_cache = get_cache(card.id, last_updated_at_unix);

		if card.closed == False and not (card.id in card_ids) and  not get_cache(card.id, last_updated_at_unix):			
			print "Updating card '" + card.name + "', id = " +  card.id;
			card_json = {}
			card_json['timestamp'] = current_time;
			card_json['name'] = card.name;
			card_json['id'] = card.id;
			card_json['idShort'] = card.idShort;
			card_json['last_updated_at'] = card.dateLastActivity.strftime("%Y-%m-%d %H:%M:%S");
			card_json['last_updated_at_unix'] = last_updated_at_unix;
			custom_fields = card.get_custom_fields();
			card_json['custom_fields'] = custom_fields;
			card_json['type'] = get_card_type(custom_fields);
			card_json['shortUrl'] = card.shortUrl;
			card_json['idList'] = card.idList;
			card_json['labels'] = get_card_labels(card.labels);	
			if (card.due):
				card_json['dueDate'] = parser.parse(card.due).strftime("%Y-%m-%d %H:%M:%S");
			else:
				card_json['dueDate'] = '' 
			card_json['estimation'] = get_card_estimation(custom_fields);			
			cards.append(card_json);

		else:
			card_cache['timestamp'] = current_time; 
			cards.append(card_cache);
		card_ids.append(card.id);
	save_cache(cards);
	return cards;

#cache_in_file = True;
#main(1, 2)

