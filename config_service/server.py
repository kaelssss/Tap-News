import pyjsonrpc
import configs
import params
import learnings
import logging

logging.basicConfig(filename='./logging/config_server.log', level=logging.INFO)

SERVER_HOST = 'localhost'
SERVER_PORT = 9999

class RequestHandler(pyjsonrpc.HttpRequestHandler):
    @pyjsonrpc.rpcmethod
    def getServerConfigForServer(self, server_name):
        logging.info('config_server: getting server config for %s' % server_name)
        return configs.getServerConfigForServer(server_name)
    
    @pyjsonrpc.rpcmethod
    def getDatabaseConfigForUsecase(self, usecase_name):
        logging.info('config_server: getting database config for %s' % usecase_name)
        return configs.getDatabaseConfigForUsecase(usecase_name)

    @pyjsonrpc.rpcmethod
    def getMessagequeueConfigForUsecase(self, usecase_name):
        logging.info('config_server: getting messagequeue config for %s' % usecase_name)
        return configs.getMessagequeueConfigForUsecase(usecase_name)

    @pyjsonrpc.rpcmethod
    def getMemoryConfig(self, memory_name):
        logging.info('config_server: getting memory config for %s' % memory_name)
        return configs.getMemoryConfig(memory_name)
    
    @pyjsonrpc.rpcmethod
    def getPipelineConfigForSection(self, section_name):
        logging.info('config_server: getting news_pipeline config for %s' % section_name)
        return params.getPipelineConfigForSection(section_name)

    @pyjsonrpc.rpcmethod
    def getBackendConfigForUsecase(self, usecase_name):
        logging.info('config_server: getting backend_server config for %s' % usecase_name)
        return params.getBackendConfigForUsecase(usecase_name)
    
    @pyjsonrpc.rpcmethod
    def getRecommendationConfigForUsecase(self, usecase_name):
        logging.info('config_server: getting news_recommendation config for %s' % usecase_name)
        return params.getRecommendationConfigForUsecase(usecase_name)

    @pyjsonrpc.rpcmethod
    def getMachineLearningParamForUsecase(self, usecase_name):
        logging.info('config_server: getting machine learning param for %s' % usecase_name)
        return learnings.getMachineLearningParamForUsecase(usecase_name)

# Threading HTTP Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (SERVER_HOST, SERVER_PORT),
    RequestHandlerClass = RequestHandler
)

print 'Starting HTTP server on %s:%d' % (SERVER_HOST, SERVER_PORT)
logging.info('Starting HTTP server on %s:%d' % (SERVER_HOST, SERVER_PORT))

http_server.serve_forever()