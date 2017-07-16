import os
import sys
import redis
import hashlib
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import news_api_client
import config_service_client
from cloudAMQP_client import CloudAMQPClient

# prepare logging
import logging
logging.basicConfig(filename='./logging/news_pipeline.log', level=logging.INFO)

# ask for mq and memory configs
mq_config = config_service_client.getMessagequeueConfigForUsecase('scrape_news_task')
cloudAMQP_client = CloudAMQPClient(mq_config['queue_url'], mq_config['queue_name'])

mmr_config = config_service_client.getMemoryConfig('redis')
redis_client = redis.StrictRedis(mmr_config['host'], mmr_config['port'])

# ask for other params
news_monitor_config = config_service_client.getPipelineConfigForSection('news_monitor')
news_sources = news_monitor_config['news_sources']
news_timeout_seconds = int(news_monitor_config['news_timeout_seconds'])
sleeptime_seconds = int(news_monitor_config['scrape_queue_client_sleeptime_seconds'])

while True:
    # such a step takes a list of latest news task, but most of them could be old duplicates
    news_list = news_api_client.getNewsFromSource(news_sources)
    num_of_new_news = 0

    for news in news_list:
        news_digest = hashlib.md5(news['title'].encode('utf-8')).digest().encode('base64')

        if redis_client.get(news_digest) is None:
            num_of_new_news = num_of_new_news + 1
            news['digest'] = news_digest

            if news['publishedAt'] is None:
                news['publishedAt'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # first level anti-duplicate by redis: only report new news tasks
            redis_client.set(news_digest, news)
            redis_client.expire(news_digest, news_timeout_seconds)

            cloudAMQP_client.sendMessage(news)

    print 'Fetched %d news.' % num_of_new_news
    if num_of_new_news != 0:
        logging.info('news_monitor: Fetched %d news and sent to news_to_scrape queue.' % num_of_new_news)

    cloudAMQP_client.sleep(sleeptime_seconds)