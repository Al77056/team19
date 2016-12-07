from datetime import datetime
from google.cloud import datastore
import utility
import json

class Capital:

    def __init__(self):
        self.ds = datastore.Client(project="hackathon-team-019")
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
            entity['location'] = datastore.Entity(key=self.ds.key('GeoPoint'))
            entity['location']['latitude'] = item['location']['latitude']
            entity['location']['longitude'] = item['location']['longitude']
            
        if item.has_key('countryCode'):
            entity['countryCode'] = item['countryCode']
            
        if item.has_key('continent'):
            entity['continent'] = item['continent']
        
        utility.log_info(entity)       
        return self.ds.put(entity)

    def fetch_capital(self, itemId):
        query = self.ds.query(kind=self.kind)
        query.add_filter('id', '=', long(itemId))
        return self.get_query_results(query)

    def fetch_allCapitals(self):
        query = self.ds.query(kind=self.kind)
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
        for entity in list(query.fetch()):
#             utility.log_info(entity)
            self.ds.delete(entity.key)
        return 'ok'
    
def parse_note_time(note):
    """converts a greeting to an object"""
    return {
        'text': note['text'],
        'timestamp': note['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    }
