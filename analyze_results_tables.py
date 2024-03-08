from typing_extensions import Self
from pypika import MySQLQuery, Table, Field, Schema
import psycopg2
from multidomain import search_multi_domain
import pymongo
from pymongo.cursor import Cursor
from psycopg2.errors import UndefinedTable
from typing import Union

class MySQLDatabase():

    _database = None
    _cursor = None
    _state = None
    _mongo = None

    def __init__(self) -> None:
        #  Initialize Mongo
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")

        self._mongo = myclient["thesis_experiment"]
        pass

    def connect_to_db(self) -> Self | None:
        # Connect to the database
        try:
            self._database = psycopg2.connect(
                user='panos',
                password='password',
                host='127.0.0.1',
                port='5432',
                sslmode='disable',
                database='mfeatures')
            
            self._cursor = self._database.cursor()
            return self
        except Exception as e:
            print('error: ', e)
            return None


    def close(self):
        self._cursor.close()
        self._database.close()


    def list_set_get_for(self, website)-> Self:

        query = f'''
                    select *
                    from
                    (select  distinct a.feature_id, feature_name, a.setter, setter_tld, a.getter, getter_tld, b.pairs,
                    CAST(
                        case
                            when setter_tld = getter_tld
                                then 0
                            else 1
                        end as bit
                    ) as different_origin 
                    from
                    (select feature_id, feature_name, setter, regexp_substr(setter_url,'^[^:]*\:\/\/(?:[^ :.\/]*\.)+([^ \n\/]*)') as setter_tld, getter, regexp_substr(getter_url,'^[^:]*\:\/\/(?:[^ :.\/]*\.)+([^ \n\/]*)') as getter_tld
                    from mfeatures_results.{website.replace('.','_')}_s_g) as a
                    inner join
                    (SELECT feature_id, setter, getter, COUNT(*) as pairs FROM mfeatures_results.{website.replace('.','_')}_s_g
                    group by feature_id, setter, getter
                    order by pairs desc, setter desc, getter desc) as b
                    on(a.feature_id = b.feature_id)
                    where a.setter = b.setter and a.getter = b.getter
                    order by b.pairs desc) as generic
                    where different_origin = '1'
                    '''
        self._state = {
            'query_results': self.execute_query(query),
            'website': website
        }
        return self
    

    def execute_query(self, query)-> list[tuple[any,...]] | None:
        
        try:
            self._cursor.execute(query)
            return self._cursor.fetchall()
        except UndefinedTable as e:
            print('Table not Found')
            return None
        except Exception as e:
            raise e
    

    def parse_to_mongo(self, results=None, website=None, force_write=False):
        if results is None and 'query_results' not in self._state.keys():
            raise Exception('Query results do not exist. Run \'list_set_get_for\' method first or pass the results as parameter')
        
        if website is None and 'website' not in self._state.keys():
            raise Exception('Website value do not exist. Run \'list_set_get_for\' method first or pass the website as parameter')
        
        if 'website' in self._state.keys():
            website = self._state['website']

        if 'query_results' in self._state.keys():
            results = self._state['query_results']

        data = {'raw': [{
                    'feature_id': row[0],
                    'feature_name': row[1],
                    'setter_script_id': row[2],
                    'setter_top_level_domain': row[3],
                    'getter_script_id': row[4],
                    'getter_top_level_domain': row[5],
                    'number_of_pairs': row[6],
                                'setter_of_diff_origin_from_getter': row[7]
                            } for row in results]
        }
        # print(self._mongo['website_aggregator'][f'{website}'].count_documents({}))
        if force_write or self._mongo['website_aggregator'][f'{website}'].count_documents({}) == 0:
            res = self._mongo['website_aggregator'][f'{website}'].insert_one(data)
            print(res)

        return self
    

    def fetch_website_features_from_mongo(self, *args)->Union[Self, list, str]:
        if args:
            website = args[0]
        elif self._state['website']:
            website = self._state['website']
        else:
            print('Website wasn\'t found')
            raise TypeError

        try:
            data = self._mongo['website_aggregator'][f'{website}'].find_one()['raw']

            
            self._state = {
                'data': data,
                'website': website
            }

            return self
        except TypeError as e:
            print('Error, website does not exist in mongo database')
            return e

        


    def find_cooperating_urls(self, *args) -> Self | None:

        data = self._state['data']
        website = self._state['website']

        cooperating_urls = {}

        for row in data:
            setter_url = row['setter_top_level_domain']
            getter_url = row['getter_top_level_domain']
            pairs = row['number_of_pairs']

            saved_flag = False
            for key in cooperating_urls.keys():
                if setter_url in key and getter_url in key:
                    cooperating_urls[f'{key}']['pairs'] += pairs
                    saved_flag = True
                    break
            
            if saved_flag:
                continue

            key_value = f'{setter_url}_{getter_url}'
            cooperating_urls[f'{key_value}'] = {}
            cooperating_urls[f'{key_value}']['urls'] = [setter_url, getter_url]
            cooperating_urls[f'{key_value}']['pairs'] = pairs

        mongo_obj = self._mongo['website_aggregator'][f'{website}'].find_one_and_update({}, { '$set': {'Meta.url_combo': cooperating_urls}})

        return self


    def find_cooperating_scripts(self, *args) -> Self | None:

        data = self._state['data']
        website = self._state['website']

        cooperating_urls = {}

        for row in data:
            setter_url = row['setter_top_level_domain']
            getter_url = row['getter_top_level_domain']
            pairs = row['number_of_pairs']

            saved_flag = False
            for key in cooperating_urls.keys():
                if setter_url in key and getter_url in key:
                    cooperating_urls[f'{key}']['pairs'] += pairs
                    saved_flag = True
                    break
            
            if saved_flag:
                continue

            key_value = f'{setter_url}_{getter_url}'
            cooperating_urls[f'{key_value}'] = {}
            cooperating_urls[f'{key_value}']['urls'] = [setter_url, getter_url]
            cooperating_urls[f'{key_value}']['pairs'] = pairs

        mongo_obj = self._mongo['website_aggregator'][f'{website}'].find_one_and_update({}, { '$set': {'Meta.url_combo': cooperating_urls}})

        return self
    
    def aggregate_features_per_website(self, *args):

        data = self._state['data']
        website = self._state['website']

        features = {}

        for row in data:

            if row['feature_name'] not in features:
                features[row['feature_name']] = {
                    'name': row['feature_name'],
                    'pairs': 0,
                    'urls': set()
                }

            setter_url = row['setter_top_level_domain']
            getter_url = row['getter_top_level_domain']
            pairs = row['number_of_pairs']

            features[row['feature_name']]['pairs'] += pairs

            features[row['feature_name']]['urls'].add([setter_url,search_multi_domain(setter_url)])
            features[row['feature_name']]['urls'].add([getter_url,search_multi_domain(getter_url)])

        for feature in features:
            features[feature]['urls'] = list(features[feature]['urls'])

        mongo_obj = self._mongo['website_aggregator'][f'{website}'].find_one()

        results = self._mongo['website_aggregator'][f'{website}'].update_one({}, {'$set':{'Meta.features' : features}})
        
        return self

    def cluster_websites(website):

        group_index = search_multi_domain(website)
        


    

if __name__=="__main__":
    website = 'velvet.com'
    # db = MySQLDatabase()


    # db.connect_to_db()\
    #     .list_set_get_for(website)\
    #     .parse_to_mongo()\
    #     .fetch_website_features_from_mongo()\
    #     .aggregate_features_per_website()\
    #     .find_cooperating_urls()

    # db.close()



