import os, base64, re, logging
from elasticsearch import Elasticsearch

# Log transport details (optional):
logging.basicConfig(level=logging.INFO)


import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_all_items(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM core_item")

    rows = cur.fetchall()

    return rows

bonsai = os.environ['BONSAI_URL']
auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')

# optional port
match = re.search('(:\d+)', host)
if match:
    p = match.group(0)
    host = host.replace(p, '')
    port = int(p.split(':')[1])
else:
    port=443

# Connect to cluster over SSL using auth for best security:
es_header = [{
'host': host,
'port': port,
'use_ssl': True,
'http_auth': (auth[0],auth[1])
}]

# Instantiate the new Elasticsearch connection:
es = Elasticsearch(es_header)
es.ping()


def search(title):

    if title:
        query_body = {
            "sort" : [
    { "timesAddedToCart" : "desc" }
  ],
  "query": {
      "wildcard": {
          "title":{"value":"*"+title+"*"}
      }
  }
}
    else:
        query_body=None
    list_result=[]
    for each in (es.search(index="item",body=query_body)['hits'])['hits']:
        list_result.append(each['_source'])
    return list_result

def index():
    database = "db.sqlite3"
    conn = create_connection(database)
    mappings = {
        "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "text"},
            "price": {"type": "float"},
            "discount_price": {"type": "float"},
            "category": {"type": "text"},
            "label": {"type": "text"},
            "slug": {"type": "text"},
            "description": {"type": "text"},
            "image": {"type": "text"},
            "total": {"type": "integer"},
            "timesAddedToCart":{"type":"integer"}
    }
}
    }

    if es.indices.exists(index="item"):
        es.indices.delete(index="item")
    es.indices.create(index="item", body=mappings)
    with conn:
        rows = select_all_items(conn)
        for i, row in enumerate(rows):
            doc = {
            "id": row[0],
            "title": row[1],
            "price": row[2],
            "discount_price": row[3],
            "category": row[4],
            "label": row[5],
            "slug": row[6],
            "description": row[7],
            "image": row[8],
            "total": row[9],
            "timesAddedToCart":row[10]
            }
            
            es.index(index="item", id=i, body=doc)
