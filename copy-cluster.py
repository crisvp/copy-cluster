#!/usr/bin/env python

import requests
import argparse
import json
from requests.compat import urljoin, quote_plus

FROM_URL = 'http://localhost:9200'
TO_URL = 'http://localhost:9201'

def get_indexes(host):
    result = []
    response = requests.get(urljoin(host, '_cat/indices'), params={ 'v': '' })

    if response.status_code != 200:
        raise Exception('Invalid response getting indexes: Status {0}, response: {1}'.
            format(response.status_code, response.text))

    lines = response.text.split('\n')

    if lines[0].split()[2] != 'index':
        raise Exception('Could not parse response getting indexes: Status {0}, response: {1}'.
            format(response.status_code, response.text))

    for line in lines[1:]:
        words = line.split()
        if len(words):
            result.append(words[2])

    return result

def get_aliases(host):
    result = []
    response = requests.get(urljoin(host, '_cat/aliases'), params={ 'v': '' })

    if response.status_code != 200:
        raise Exception('Invalid response getting indexes: Status {0}, response: {1}'.
            format(response.status_code, response.text))

    lines = response.text.split('\n')

    if lines[0].split()[0] != 'alias' or lines[0].split()[1] != 'index':
        raise Exception('Could not parse response getting aliases: Status {0}, response: {1}'.
            format(response.status_code, response.text))

    for line in lines[1:]:
        words = line.split()
        if len(words):
            result.append({ 'index': words[1], 'alias': words[0] })

    return result

def get_mappings(host, index):
    response = requests.get(urljoin(host, '{0}/_mapping'.format(quote_plus(index))))

    if response.status_code != 200:
        raise Exception('Invalid response getting indexes: Status {0}, response: {1}'.
            format(response.status_code, response.text))

    return response.json()[index]

def get_settings(host, index):
    response = requests.get(urljoin(host, '{0}/_settings'.format(quote_plus(index))))

    if response.status_code != 200:
        raise Exception('Invalid response getting settings: Status {0}, response: {1}'.
            format(response.status_code, response.text))

    response_json = response.json()[index]
    if not 'settings' in response_json or not 'index' in response_json['settings']:
        raise Exception('Invalid response getting settings: Status {0}, response: {1}'.
            format(response.status_code, response.text))

    response_json['settings']['index'].pop('uuid', None)
    response_json['settings']['index'].pop('version', None)

    return response_json

def create_index(host, index, settings, mappings):
    payload = {}
    payload.update(settings)
    payload.update(mappings)

    response = requests.put(urljoin(host, '{0}'.format(quote_plus(index))), data=json.dumps(payload),
        headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        raise Exception('Invalid response creating index {2}: Status {0}, response: {1}'.
            format(response.status_code, response.text, index))

def add_alias(host, alias, index):
    payload = { 'actions': [ { 'add': { 'index': index, 'alias': alias } } ] }

    response = requests.post(urljoin(host, '_aliases'), data=json.dumps(payload),
        headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        raise Exception('Invalid response adding alias {2}: Status {0}, response: {1}'.
            format(response.status_code, response.text, alias))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("from_url", help="The URL to the source cluster")
    parser.add_argument("to_url", help="The URL to destination cluster")
    args = parser.parse_args()

    if not args.from_url.startswith('http://') and not args.from_url.startswith('https://'):
        raise Exception('invalid url: {0}'.format(args.from_url))

    if not args.to_url.startswith('http://') and not args.to_url.startswith('https://'):
        raise Exception('invalid url: {0}'.format(args.to_url))

    print('Getting index information ...')
    indexes = get_indexes(FROM_URL)
    indexdata = {}

    print('{0} indexes found.'.format(len(indexes)))

    for index in indexes:
        indexdata[index] = {}
        print('Getting settings for index {0} ...'.format(index))
        indexdata[index]['settings'] = get_settings(FROM_URL, index)
        print('Getting mappings for index {0} ...'.format(index))
        indexdata[index]['mappings'] = get_mappings(FROM_URL, index)

    for index in indexes:
        print('Creating index {0} ...'.format(index))
        create_index(TO_URL, index, indexdata[index]['settings'], indexdata[index]['mappings'])

    print('Getting aliases ...')
    aliases = get_aliases(FROM_URL)
    for alias in aliases:
        print('Adding alias {0} -> {1}'.format(alias['alias'], alias['index']))
        add_alias(TO_URL, alias['alias'], alias['index'])
