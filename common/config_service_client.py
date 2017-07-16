import pyjsonrpc
import json

URL = 'http://localhost:9999/'

client = pyjsonrpc.HttpClient(url=URL)

def getServerConfigForServer(server_name):
    server_config = json.loads(client.call('getServerConfigForServer', server_name))
    print 'Server config:'
    print server_config
    return server_config

def getDatabaseConfigForUsecase(usecase_name):
    database_config = json.loads(client.call('getDatabaseConfigForUsecase', usecase_name))
    print 'Database config:'
    print database_config
    return database_config

def getMessagequeueConfigForUsecase(usecase_name):
    messagequeue_config = json.loads(client.call('getMessagequeueConfigForUsecase', usecase_name))
    print 'Messagequeue config:'
    print messagequeue_config
    return messagequeue_config

def getMemoryConfig(memory_name):
    memory_config = json.loads(client.call('getMemoryConfig', memory_name))
    print 'Memory config:'
    print memory_config
    return memory_config

def getPipelineConfigForSection(section_name):
    section_config = json.loads(client.call('getPipelineConfigForSection', section_name))
    print 'Section config:'
    print section_config
    return section_config

def getBackendConfigForUsecase(usecase_name):
    backend_config = json.loads(client.call('getBackendConfigForUsecase', usecase_name))
    print 'Backend config:'
    print backend_config
    return backend_config

def getRecommendationConfigForUsecase(usecase_name):
    recommendation_config = json.loads(client.call('getRecommendationConfigForUsecase', usecase_name))
    print 'Recommendation config:'
    print recommendation_config
    return recommendation_config

def getMachineLearningParamForUsecase(usecase_name):
    learning_param = json.loads(client.call('getMachineLearningParamForUsecase', usecase_name))
    print 'Machine Learning param:'
    print learning_param
    return learning_param