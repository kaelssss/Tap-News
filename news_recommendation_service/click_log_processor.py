# -*- coding: utf-8 -*-

'''
Time decay model:
If selected:
p = (1-α)p + α
If not:
p = (1-α)p
Where p is the selection probability, and α is the degree of weight decrease.
The result of this is that the nth most recent selection will have a weight of
(1-α)^n. Using a coefficient value of 0.05 as an example, the 10th most recent
selection would only have half the weight of the most recent. Increasing epsilon
would bias towards more recent results more.
'''

import news_classes_v2
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client
import mongodb_client
from cloudAMQP_client import CloudAMQPClient

# prepare logging
import logging
logging.basicConfig(filename='./logging/news_recommendation_server.log', level=logging.INFO)

# ask for db, mq configs
news_db_config = config_service_client.getDatabaseConfigForUsecase('news')
news_table_name = news_db_config['database_name']

preference_model_db_config = config_service_client.getDatabaseConfigForUsecase('user_preference_model')
preference_model_table_name = preference_model_db_config['database_name']

mq_config = config_service_client.getMessagequeueConfigForUsecase('log_clicks_task')
cloudAMQP_client = CloudAMQPClient(mq_config['queue_url'], mq_config['queue_name'])

# ask for other configs
click_log_processor_config = config_service_client.getRecommendationConfigForUsecase('click_log_processor')
sleep_time_in_seconds = int(click_log_processor_config['click_log_queue_client_sleeptime_seconds'])

# ask for user prefrence and learning params
user_preference_model_config = config_service_client.getRecommendationConfigForUsecase('user_preference_model')
alpha = float(user_preference_model_config['alpha_to_raise'])
beta = float(user_preference_model_config['beta_to_depress'])
min_preference = float(user_preference_model_config['min_preference'])

learning_param = config_service_client.getMachineLearningParamForUsecase('topic_modeling')
num_classes = int(learning_param['number_classes'])
initial_p = 1.0 / num_classes

def handle_message(msg):
    if msg is None or not isinstance(msg, dict) :
        print 'broken msg'
        logging.error('news_recommendation_server: broken message in click log queue')
        return

    if ('userId' not in msg
        or 'newsId' not in msg
        or 'rate' not in msg
        or 'timestamp' not in msg):
        print 'wrong msg'
        logging.error('news_recommendation_server: wrong message in click log queue')
        return

    userId = msg['userId']
    newsId = msg['newsId']
    rate = msg['rate']

    db = mongodb_client.get_db()
    model = db[preference_model_table_name].find_one({'userId': userId})
    if (model is None):
        print 'user preference model not found'
        logging.error('news_recommendation_server: user preference model for %s not found' % userId)

    print 'Updating preference model for new user: %s' % userId
    logging.info('news_recommendation_server: Updating preference model for new user: %s' % userId)

    news = db[news_table_name].find_one({'digest': newsId})
    if (news is None
        or 'class' not in news
        or news['class'] not in news_classes_v2.classes):
        print news is None
        print 'class' not in news
        print news['class'] not in news_classes_v2.classes
        print 'Skipping processing...'
        logging.error('news_recommendation_server: class for news: %s in click_task not defined' % newsId)
        return

    click_class = news['class']
    print click_class
    print rate

    # do positive or negative time decay model according to user's rate:
    if(rate == '1'):
        print 'raising'
        logging.info('news_recommendation_server: raising %s news for %s' %(click_class, userId))
        raise_class(click_class, model)
    elif(rate == '-1'):
        print 'depressing'
        logging.info('news_recommendation_server: depressing %s news for %s' %(click_class, userId))
        depress_class(click_class, model)

    db[preference_model_table_name].replace_one({'userId': userId}, model, upsert=True)
    print 'processing finished'
    logging.info('news_recommendation_server: processing finished')
    print model['preference']

# raise class clicked while slightly weaken all other classes
def raise_class(click_class, model):
    old_p = model['preference'][click_class]
    model['preference'][click_class] = float((1 - alpha) * old_p + alpha)
    for i, _ in model['preference'].iteritems():
        if not i == click_class:
            model['preference'][i] = float((1 - alpha) * model['preference'][i])

# depress class clicked while slightly strengthen all other classes (beta is negative)
# any class cannot be weaker than min_preference
def depress_class(click_class, model):
    old_p = model['preference'][click_class]
    model['preference'][click_class] = max(float((1 - beta) * old_p + beta), min_preference)
    for i, _ in model['preference'].iteritems():
        if not i == click_class:
            model['preference'][i] = float((1 - beta) * model['preference'][i])

def run():
    while True:
        if cloudAMQP_client is not None:
            msg = cloudAMQP_client.getMessage()
            if msg is not None:
                try:
                    handle_message(msg)
                except Exception as e:
                    print e
                    pass
            cloudAMQP_client.sleep(sleep_time_in_seconds)

if __name__ ==  "__main__":
    run()