# Stdlib imports
import urllib3
import json
from datetime import datetime

# Third-party app imports
import requests
import certifi
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from elasticsearch import Elasticsearch, helpers

# Imports from app
from middleware.config import (
    ELASTICSEARCH_USER,
    ELASTICSEARCH_PASSWORD,
    CONTEXT_API_USERNAME,
    CONTEXT_API_PASSWORD,
)

# Removing requests warning
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Context Setup
base_url = 'https://context.newsai.org/api'

# Elasticsearch setup
es = Elasticsearch(
    ['https://search.newsai.org'],
    http_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    port=443,
    use_ssl=True,
    verify_certs=True,
    ca_certs=certifi.where(),
)


def get_login_token():
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "username": CONTEXT_API_USERNAME,
        "password": CONTEXT_API_PASSWORD,
    }

    r = requests.post(base_url + "/jwt-token/",
                      headers=headers, data=json.dumps(payload), verify=False)
    data = json.loads(r.text)
    token = data.get('token')
    return token


def sync_entities_es(entities):
    if entities:
        to_append = []
        for entity in entities:
            doc = {
                '_type': 'entity',
                '_index': 'entities',
                'data': entity
            }
            to_append.append(doc)
        res = helpers.bulk(es, to_append)
        print res


def get_entities():
    token = get_login_token()
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    r = requests.get(base_url + '/entities/',
                     headers=headers, verify=False)
    entities = r.json()
    offset = 100
    for x in range(0, entities['count'], offset):
        print x
        r = requests.get(base_url + '/entities/?limit=' + str(offset) + '&offset=' + str(x),
                         headers=headers, verify=False)
        entity = r.json()
        sync_entities_es(entity['results'])


def reset_elastic():
    es.indices.delete(index='entities', ignore=[400, 404])
    es.indices.create(index='entities', ignore=[400, 404])
    get_entities()


reset_elastic()
