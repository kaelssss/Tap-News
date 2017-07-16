import json
import os
import pickle
import random
import redis
import sys
import numpy
from bson.json_util import dumps
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client
import mongodb_client
import news_recommendation_service_client

import news_classes_v2

from cloudAMQP_client import CloudAMQPClient

redis_config = config_service_client.getMemoryConfig('redis')
redis_client = redis.StrictRedis(redis_config['host'], redis_config['port'], db=0)

db_config = config_service_client.getDatabaseConfigForUsecase('news')
news_table_name = db_config['database_name']

mq_config = config_service_client.getMessagequeueConfigForUsecase('log_clicks_task')
cloudAMQP_client = CloudAMQPClient(mq_config['queue_url'], mq_config['queue_name'])

backend_config = config_service_client.getBackendConfigForUsecase('pagination')
news_limit = int(backend_config['user_news_memory_limit'])
news_list_batch_size = int(backend_config['news_page_size'])
user_news_time_out_in_seconds = int(backend_config['user_news_memory_timeout_seconds'])

def getNewsSummariesForUser(user_id, page_num):
    page_num = int(page_num)
    begin_index = (page_num - 1) * news_list_batch_size
    end_index = page_num * news_list_batch_size

    # The final list of news to be returned.
    sliced_news = []

    # personalizing
    preferences = news_recommendation_service_client.getPreferenceForUser(user_id)
    news_numbers = []
    if preferences is not None and len(preferences) > 0:
        news_numbers = [int(round(preference * news_limit)) for preference in preferences]
    print news_numbers

    if redis_client.get(user_id) is not None:
        news_digests = pickle.loads(redis_client.get(user_id))
        # If begin_index is out of range, this will return empty list;
        # If end_index is out of range (begin_index is within the range), this
        # will return all remaining news ids.
        sliced_news_digests = news_digests[begin_index:end_index]
        db = mongodb_client.get_db()
        sliced_news = list(db[news_table_name].find({
            'digest': {
                '$in': sliced_news_digests
            }
        }))
    else:
        db = mongodb_client.get_db()
        print 'taking from db'
        #total_news = list(db[news_table_name].find().sort([('publishedAt', -1)]).limit(news_limit))
        selected_news = []
        for i in range(0, len(news_numbers)):
            selected_news.extend(list(db[news_table_name].find({
                'class': news_classes_v2.class_map[str(i+1)]
            }).limit(news_numbers[i])))
        selected_news = sorted(selected_news, key=lambda k: k['publishedAt'], reverse=True)[:]
        
        selected_news_digests = map(lambda x:x['digest'], selected_news)
        redis_client.set(user_id, pickle.dumps(selected_news_digests))
        redis_client.expire(user_id, user_news_time_out_in_seconds)
        sliced_news = selected_news[begin_index:end_index]

    # tagging
    for news in sliced_news:
        del news['text']
        #if news['class'] == topPreference:
            #news['reason'] = 'Recommend'
        if news['publishedAt'].date() == datetime.today().date():
            news['time'] = 'today'
    return json.loads(dumps(sliced_news))

def logNewsClickForUser(user_id, news_id, rate):
    message = {
        'userId': user_id,
        'newsId': news_id,
        'rate': rate,
        'timestamp': str(datetime.utcnow())
    }
    cloudAMQP_client.sendMessage(message)