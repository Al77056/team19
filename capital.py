from datetime import datetime
from google.cloud import datastore
from google.cloud import storage
import utility
import json

from flask import jsonify
from google.cloud import pubsub

import argparse

class Capital:

    def __init__(self):
        self.ds = datastore.Client(project="hackathon-team-019")
        self.kind = "capital"


    def _update_capital_entity(self, entity, item):
        if item.has_key('country'):
            entity['country'] = item['country']
        if item.has_key('name'):
            entity['name'] = item['name']
        if item.has_key('location'):
            entity['location'] = datastore.Entity(key=self.ds.key('GeoPoint'))
            entity['location']['latitude'] = item['location']['latitude']
            entity['location']['longitude'] = item['location']['longitude']
        if item.has_key('countryCode'):
            entity['countryCode'] = item['countryCode']
        if item.has_key('continent'):
            entity['continent'] = item['continent']
        return self.ds.put(entity)

    def store_capital(self, msg, itemId):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', long(itemId))
        for entity in list(query.fetch()):
            # update the first instance
            return self._update_capital_entity(entity, msg)
        
        # create a new one
        key = self.ds.key(self.kind, long(itemId))
        entity = datastore.Entity(key)
        item= msg
        if item.has_key('id'):
            entity['id'] = item['id']
        else:
            return None
            
        return self._update_capital_entity(entity, item)       

    def fetch_capital(self, itemId):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', long(itemId))
        return self.get_query_results(query)

    def fetch_allCapitals(self):
        query = self.ds.query(kind=self.kind)
        return self.get_query_results(query)

    def publish_toPubSub(self, topic_name, itemId):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', long(itemId))
        cap = self.get_query_results(query)

        pubsub_client = pubsub.Client(project="hackathon-team-019")
        topic = pubsub_client.topic(topic_name)

        # Data must be a bytestring
        data = json.dumps(cap)
        

        data = data.encode('utf-8')

        message_id = topic.publish(data)

        print('Message {} published.'.format(message_id))

        return message_id

    def fetch_notes(self):
        query = self.ds.query(kind=self.kind)
        query.order = ['-timestamp']
        return self.get_query_results(query)

    def fetch_capitals(self, query_string, search_string):
        query = self.ds.query(kind=self.kind)
        queryString = str(query_string)
        if(len(queryString) > 0):
            lists = queryString.split(':', 1)
            if(len(lists) > 1 and len(lists[0]) > 0 and len(lists[1]) > 0):
                query.add_filter(lists[0], '=', lists[1])

        return self.get_query_results(query)

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results

    def filter_query_results(self, query, itemId):
        results = list()
        for entity in list(query.fetch()):
            de = dict(entity)
#             utility.log_info(de)
            if int(de['id']) == int(itemId):
                results.append(de)
        return results

    def delete_capital(self, itemId):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', long(itemId))
        success = False
        for entity in list(query.fetch()):
#             utility.log_info(entity)
            self.ds.delete(entity.key)
            success = True
        return success
    
    def save_capital_to_bucket(self, itemId, bucket_name):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', long(itemId))
        for entity in list(query.fetch()):
            content = json.dumps(dict(entity))
            object_name = str(itemId)
            self._store_in_bucket(bucket_name, object_name, content)
            return True
        return False
    
    def _store_in_bucket(self, bucket_name, object_name, content):
        storage_client = storage.client.Client(project="hackathon-team-019")
        bucket = storage.bucket.Bucket(storage_client, bucket_name)
        if not bucket.exists():
            bucket.create()
        
        blob = storage.blob.Blob(object_name, bucket)
        blob.upload_from_string(content)

def parse_note_time(note):
    """converts a greeting to an object"""
    return {
        'text': note['text'],
        'timestamp': note['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    }
