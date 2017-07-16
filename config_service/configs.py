import json
import logging

SERVER_CONFIG = {
    'backend_server': {
        'url': 'localhost',
        'port': '4040'
    },
    'news_recommendation_server': {
        'url': 'localhost',
        'port': '5050'
    },
    'news_topic_modeling_server': {
        'url': 'localhost',
        'port': '6060'
    }
}

DATABASE_CONFIG = {
    'news': {
        'database_name': 'news/v2'
    },
    'user_preference_model': {
        'database_name': 'user_preference_model'
    }
}

MESSAGEQUEUE_CONFIG = {
    'scrape_news_task': {
        'queue_url': 'amqp://xufuhmdi:q4lMfFlrWzuDY7ScBMAH884d2Qgd1jt1@fish.rmq.cloudamqp.com/xufuhmdi',
        'queue_name': 'news_to_scrape'
    },
    'dedupe_news_task': {
        'queue_url': 'amqp://ypsqvrsl:_ppuUauPGXo5j1Ib3WFgiDENDW_zKGi-@fish.rmq.cloudamqp.com/ypsqvrsl',
        'queue_name': 'news_to_dedupe'
    },
    'log_clicks_task': {
        'queue_url': 'amqp://ywcwadko:SiLh9Yh3FeqbtuHq9h5MM70a6cpwUanW@wasp.rmq.cloudamqp.com/ywcwadko',
        'queue_name': 'click_logs'
    }
}

MEMORY_CONFIG = {
    'redis': {
        'host': 'localhost',
        'port': 6379
    }
}

def getServerConfigForServer(server_name):
    return getConfigForUsecase(server_name, SERVER_CONFIG)

def getDatabaseConfigForUsecase(usecase_name):
    return getConfigForUsecase(usecase_name, DATABASE_CONFIG)

def getMessagequeueConfigForUsecase(usecase_name):
    return getConfigForUsecase(usecase_name, MESSAGEQUEUE_CONFIG)

def getMemoryConfig(memory_name):
    return getConfigForUsecase(memory_name, MEMORY_CONFIG)

# common config-getting method
def getConfigForUsecase(usecase_name, configs_name):
    config = {}
    if usecase_name in configs_name:
        config = configs_name[usecase_name]
    print config
    return json.dumps(config)