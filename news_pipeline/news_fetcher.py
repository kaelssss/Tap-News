import os
import sys
from newspaper import Article
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client
from cloudAMQP_client import CloudAMQPClient

# prepare logging
import logging
logging.basicConfig(filename='./logging/news_pipeline.log', level=logging.INFO)

# ask for mq configs
scrape_mq_config = config_service_client.getMessagequeueConfigForUsecase('scrape_news_task')
dedupe_mq_config = config_service_client.getMessagequeueConfigForUsecase('dedupe_news_task')
scrape_news_queue_client = CloudAMQPClient(scrape_mq_config['queue_url'], scrape_mq_config['queue_name'])
dedupe_news_queue_client = CloudAMQPClient(dedupe_mq_config['queue_url'], dedupe_mq_config['queue_name'])

# ask for other configs
fetch_config = config_service_client.getPipelineConfigForSection('news_fetcher')
scrape_sleeptime_seconds = int(fetch_config['scrape_queue_client_sleeptime_seconds'])
dedupe_sleeptime_seconds = int(fetch_config['dedupe_queue_client_sleeptime_seconds'])

def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        print 'message from news_to_scrape is broken'
        logging.error('news_fetcher: message from news_to_scrape is broken')
        return
    
    # use Newspaper to scrape the text of news
    task = msg
    text = None
    article = Article(task['url'])
    article.download()
    article.parse()
    task['text'] = article.text
    
    # send this news to mq
    dedupe_news_queue_client.sendMessage(task)
    logging.info('news_fetcher: news text scraped, loaded and sent to news_to_dedupe queue')

while True:
    if scrape_news_queue_client is not None:
        msg = scrape_news_queue_client.getMessage()
        if msg is not None:
            logging.info('news_fetcher: news task aquired from news_to_scrape queue')
            try:
                handle_message(msg)
            except Exception as e:
                print 'news_fetcher exception: %s' % e
                logging.warning('news_fetcher: exception: %s' % e)
                pass
        scrape_news_queue_client.sleep(scrape_sleeptime_seconds)
    
    if dedupe_news_queue_client is not None:
        dedupe_news_queue_client.sleep(dedupe_sleeptime_seconds)