import config_service_client as client

def test_server():
    client.getServerConfigForServer('backend_server')
    client.getServerConfigForServer('news_recommendation_server')
    client.getServerConfigForServer('news_topic_modeling_server')

def test_db():
    client.getDatabaseConfigForUsecase('news')
    client.getDatabaseConfigForUsecase('user_preference_model')

def test_mq():
    client.getMessagequeueConfigForUsecase('scrape_news_task')
    client.getMessagequeueConfigForUsecase('dedupe_news_task')
    client.getMessagequeueConfigForUsecase('log_clicks_task')

def test_mmr():
    client.getMemoryConfig('redis')

if __name__ == '__main__':
    test_server()
    test_db()
    test_mq()
    test_mmr()