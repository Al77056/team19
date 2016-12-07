from datetime import datetime
from google.cloud import datastore
import utility
import json

class Capital:

    def __init__(self):
        self.ds = datastore.Client(project=utility.project_id())
        self.kind = "capital"

    def store_capital(self, msg):
        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)

        item= msg
        if item.has_key('id'):
            entity['id'] = item['id']
        else:
            return None
        
        if item.has_key('country'):
            entity['country'] = item['country']
        
        if item.has_key('name'):
            entity['name'] = item['name']
            
        if item.has_key('location'):
            entity['location'] = item['location']
            
        if item.has_key('countryCode'):
            entity['countryCode'] = item['countryCode']
            
        if item.has_key('continent'):
            entity['continent'] = item['continent']
        
        utility.log_info(entity)       
        return self.ds.put(entity)

    def fetch_capital(self, id):
        query = self.ds.query(kind=self.kind)
        query.id = id;
        return self.get_query_results(query)

    def fetch_notes(self):
        query = self.ds.query(kind=self.kind)
        query.order = ['-timestamp']
        return self.get_query_results(query)

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results


def parse_note_time(note):
    """converts a greeting to an object"""
    return {
        'text': note['text'],
        'timestamp': note['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    }
