# Elasticsearch API sync

Syncing data between elasticsearch and the internal NewsAI context API.

### Problems & solution

1. Syncing data from API and Elasticsearch without downtime:
    - Have an alias pointing to index `entities_v1`
    - Create index `elastic_v2`, populate data, point alias to new index
    - Delete old index `entities_v1`

### Installing & Running

`pip install -r requirements.txt`, `python sync.py`

### Running in the background

This command makes it run every 6 hours

`nohup python scripts/reindex_elasticsearch.py &`
