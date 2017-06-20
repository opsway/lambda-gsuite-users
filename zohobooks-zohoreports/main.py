#!/usr/bin/env python
import json
import config
import requests
import time
from datetime import date


def getZohoBooksUrl(apiMethod) :
    return "https://books.zoho.com/api/v3/"  + apiMethod + '/?organization_id=' + config.getZohoBooksOrg()  + '&authtoken=' + config.getZohoBooksToken()  + '&accept=json'

def getZohoReportsURL(tableName, importType):
    return  "https://reportsapi.zoho.com/api/" + config.getZohoReportsLogin() + "/OpsWay Group Finance/" + tableName + "?ZOHO_ACTION=IMPORT&authtoken=" + config.getZohoReportsToken() + "&ZOHO_IMPORT_FILETYPE=JSON&ZOHO_IMPORT_TYPE=" + importType + "&ZOHO_AUTO_IDENTIFY=true&ZOHO_ON_IMPORT_ERROR=ABORT&ZOHO_OUTPUT_FORMAT=JSON&ZOHO_API_VERSION=1.0&ZOHO_CREATE_TABLE=false"

def uploadZohoReports(tableName, payload, importType):
    
    files = {'ZOHO_FILE': (tableName + '.csv', payload)}
    r = requests.post(getZohoReportsURL(tableName, importType), files=files)
    result = r.json()

    if ('error' in result['response']):
        print result['response']['error']
        raise Exception('Error encountered')

def getZohoBooks_BankAccounts():
    r = requests.get(getZohoBooksUrl('bankaccounts'))
    accounts = r.json()
    payload = []

    for account in accounts['bankaccounts']:
        if account['is_active']:
            account_info = {}
            account_info['Currency'] = account['currency_code']
            account_info['Account Name'] = account['account_name']
            account_info['Total'] = account['balance']
            payload.append(account_info)
    return payload

def getZohoBooks_CurrencyListJSON():
    r = requests.get(getZohoBooksUrl('settings/currencies'))
    return r.json()

def getZohoBooks_ExchangeRates():
    currencyListJson = getZohoBooks_CurrencyListJSON()
    currencies = []
    for currency in currencyListJson['currencies']:

        r = requests.get(getZohoBooksUrl('settings/currencies/' + currency['currency_id'] + '/exchangerates'))
        result = r.json()

        # code 1002 - is just when no exchange rate for given currency exists
        if (int(result['code']) > 0 and result['code'] != 1002):
            print result['message']
            raise Exception('Error encountered')

        if ('exchange_rates' in result):    
            currency_info = {}
            currency_info['BaseCurrency'] = currency['currency_code']
            currency_info['USD'] = result['exchange_rates'][0]['rate']
            currencies.append(currency_info)
    return currencies


def saveAccountDynamics(event, context):
    accounts = getZohoBooks_BankAccounts();
    currencies = getZohoBooks_ExchangeRates();
    dynamics = []
    for account in accounts:
        if (int(account['Total']) != 0): 
            accountInfo = {}
            accountInfo['Account Name'] = account['Account Name']
            accountInfo['Date'] = time.strftime("%Y-%m-%d")
            for currency in currencies:
                if (currency['BaseCurrency'] == account['Currency']):
                    accountInfo['Total (BCY)'] =  round(currency['USD'] * account['Total'])
            dynamics.append(accountInfo);
    uploadZohoReports('ZohoBooks_BankingDynamics',json.dumps(dynamics), 'APPEND');