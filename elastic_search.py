from elasticsearch import Elasticsearch
from datetime import datetime

from flask import jsonify

es = Elasticsearch([{'scheme':'http','host': 'localhost', 'port': 9200}])

index_name1 = '123'
document_id = '123'
# 

# Create an index (you may need to define mappings here)
es.indices.create(index=index_name1, ignore=400)


# Bulk insert JSON documents
data = [
    { "id":10 ,"name": "Vivke", "content": "red car", "total" : 1200, "date":"12/06/2002"},
    { "id":22 ,"name": "Soni", "content": "blue car", "total" : 1200, "date":"11/05/2022"},
    { "id":31 ,"name": "XYZ", "content": "black car", "total" : 2400, "date":"01/02/2023"},
    { "id":32 ,"name": "qwerty", "content": "orange car", "total" : 2400, "date":"01/02/2023"}
    # ... (more documents)
]

# actions = [
#     {"_index": index_name, "_id": doc["id"], "_source": doc} for doc in data
# ]

# Index the sample data
for document in data:
    es.index(index=index_name1, document=document, id=document['name'])
    
es.indices.refresh(index=index_name1)
    
# Perform a search
# results = es.search(index=index_name, q="name:Document 2")

# # Print the search results
# for hit in results['hits']['hits']:
#     print(f"Document ID: {hit['_id']}, Document Name: {hit['_source']['name']}")

# search_query = {
#     "query": {
#         "match": {
#             "name": "Document 1"
#         }
#     }
# }

# results = es.search(index=index_name, body=search_query)

# for hit in results['hits']['hits']:
#     print(hit['_source'])

search_query = {
    "query": {
        "range": {
            "total": {
                "gt": 2000
            }
        }
    }
}

# Define the search query using a "range" query
search_query_date = {
    "query": {
        "range": {
            "date": {
                "lt": "12/09/2020"
            }
        }
    }
}

# Perform the search
# results = es.search(index=index_name, body=search_query_date)
date = "13.05.2024"
if "." in date:
    date = date.replace(".","/")
elif "-" in date:
    date = date.replace("-","/")

# Convert the date to Elasticsearch-friendly format
date_to_compare = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")

query = {
        "query": {
            "match": {
            "_all": "give me data which has red car"
                }
            }
        }

queries = {
        "query": {
            "simple_query_string": {
            "query": "give me data which has total value of 2400 and belongs to qwerty"
            }
        },
        "request_cache": False
        }
result = es.search(index=index_name1, body=queries)
results = es.search(index=index_name1, body=queries)

res = []
# Print the search results
for hit in results['hits']['hits']:
    invoice = hit['_source']
    # print(f"Invoice ID: {hit['_id']}, Total Amount: {invoice['total']}, content: {invoice}")
    res.append(invoice)
print(res)
    
