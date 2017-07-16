import datetime
import os
import sys
from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client
import mongodb_client
import news_topic_modeling_service_client
import logging

# uncomment the next 2 lines if anything in nltk-data not found
#nltk.download('punkt')
#nltk.download('all-corpora')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

from cloudAMQP_client import CloudAMQPClient

mq_config = config_service_client.getMessagequeueConfigForUsecase('dedupe_news_task')
cloudAMQP_client = CloudAMQPClient(mq_config['queue_url'], mq_config['queue_name'])

db_config = config_service_client.getDatabaseConfigForUsecase('news')
news_table_name = db_config['database_name']

dedupe_config = config_service_client.getPipelineConfigForSection('news_deduper')
sleeptime_seconds = int(dedupe_config['dedupe_queue_client_sleeptime_seconds'])
similarity_threshold = float(dedupe_config['same_news_similarity_threshold'])

logging.basicConfig(filename='./logging/news_pipeline.log', level=logging.INFO)

def handle_message(msg):
    if msg is None or not isinstance(msg, dict) :
        logging.error('news_monitor: message from news_to_dedupe is broken')
        return
    task = msg
    #text = str(task['text'])
    text = task['text'].encode('utf-8')
    if text is None:
        return

    published_at = parser.parse(task['publishedAt'])
    published_at_day_begin = datetime.datetime(published_at.year,
                                               published_at.month,
                                               published_at.day,
                                               0, 0, 0, 0)
    published_at_day_end = published_at_day_begin + datetime.timedelta(days=1)

    db = mongodb_client.get_db()
    same_day_news_list = list(db[news_table_name].find(
        {'publishedAt': {'$gte': published_at_day_begin,
                         '$lt': published_at_day_end}}))

    if same_day_news_list is not None and len(same_day_news_list) > 0:
        #documents = [str(news['text']) for news in same_day_news_list]
        documents = [news['text'].encode('utf-8') for news in same_day_news_list]
        documents.insert(0, text)

        # Calculate similarity matrix
        tfidf = TfidfVectorizer().fit_transform(documents)
        pairwise_sim = tfidf * tfidf.T

        #print pairwise_sim
        print 'pairwise_sim calculated'

        rows, _ = pairwise_sim.shape

        for row in range(1, rows):
            if pairwise_sim[row, 0] > similarity_threshold:
                print 'Duplicated news. Ignore'
                logging.info('news_deduper: news ignored as duplicated')
                return
    
    task['publishedAt'] = parser.parse(task['publishedAt'])
    #print task
    print 'task inserted'
    db[news_table_name].replace_one({'digest': task['digest']}, task, upsert=True)
    # Classify news
    title = task['title']
    desc = task['description']
    src = task['source']
    info = title + ' ' + desc + ' ' + src
    #info = info.translate(None, string.punctuation)
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    info = info.translate(remove_punctuation_map)
    info = info.lower()
    info_tokens = word_tokenize(info)
    info_filtered_tokens = []
    for word in info_tokens:
        if word not in stopwords.words('english'):
            info_filtered_tokens.append(word)
    info_filtered_line = ' '.join(info_filtered_tokens)
    if info_filtered_line is not None:
        topic = news_topic_modeling_service_client.classify(info_filtered_line)
        task['class'] = topic

    db[news_table_name].replace_one({'digest': task['digest']}, task, upsert=True)
    logging.info('news_deduper: news classified and obtained')

while True:
    if cloudAMQP_client is not None:
        msg = cloudAMQP_client.getMessage()
        if msg is not None:
            logging.info('news_deduper: news task aquired from news_to_dedupe queue')
            try:
                handle_message(msg)
            except Exception as e:
                print 'news_deduper exception: %s' % e
                logging.warning('news_deduper: exception: %s' % e)
                pass
        cloudAMQP_client.sleep(sleeptime_seconds)