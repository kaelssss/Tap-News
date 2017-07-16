import json

PIPELINE_CONFIG = {
    'news_monitor': {
        'news_sources': [
            'bbc-news',
            'bbc-sport',
            'bloomberg',
            'cnn',
            'entertainment-weekly',
            'espn',
            'ign',
            'techcrunch',
            'the-new-york-times',
            'the-wall-street-journal',
            'the-washington-post'
        ],
        'news_timeout_seconds': 3600 * 24 * 1,
        'scrape_queue_client_sleeptime_seconds': 10
    },
    'news_fetcher': {
        'scrape_queue_client_sleeptime_seconds': 5,
        'dedupe_queue_client_sleeptime_seconds': 5
    },
    'news_deduper': {
        'dedupe_queue_client_sleeptime_seconds': 1,
        'same_news_similarity_threshold': 0.9
    }
}

BACKEND_CONFIG = {
    'pagination': {
        'user_news_memory_limit': 100,
        'user_news_memory_timeout_seconds': 60,
        'news_page_size': 20
    }
}

RECOMMENDATION_CONFIG = {
    'click_log_processor': {
        'click_log_queue_client_sleeptime_seconds': 1
    },
    'user_preference_model': {
        'alpha_to_raise': 0.1,
        'beta_to_depress': -0.1,
        'min_preference': 0.01
    }
}

def getPipelineConfigForSection(section_name):
    return getParamForUsecase(section_name, PIPELINE_CONFIG)

def getBackendConfigForUsecase(usecase_name):
    return getParamForUsecase(usecase_name, BACKEND_CONFIG)

def getRecommendationConfigForUsecase(usecase_name):
    return getParamForUsecase(usecase_name, RECOMMENDATION_CONFIG)

def getParamForUsecase(usecase_name, params_name):
    param = {}
    if usecase_name in params_name:
        param = params_name[usecase_name]
    print param
    return json.dumps(param)