import pyjsonrpc
import operations
import os
import sys
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client
from cloudAMQP_client import CloudAMQPClient

# prepare logging
import logging
logging.basicConfig(filename='./logging/backend_server.log', level=logging.INFO)

# ask server configs
server_config = config_service_client.getServerConfigForServer('backend_server')
server_host = server_config['url']
server_port = int(server_config['port'])

# ask mq configs
mq_config = config_service_client.getMessagequeueConfigForUsecase('log_clicks_task')
cloudAMQP_client = CloudAMQPClient(mq_config['queue_url'], mq_config['queue_name'])

class RequestHandler(pyjsonrpc.HttpRequestHandler):
    @pyjsonrpc.rpcmethod
    def getNewsSummariesForUser(self, user_id, page_num):
        logging.info('backend_server: %s asks for page %s' % (user_id, page_num))
        return operations.getNewsSummariesForUser(user_id, page_num)

    @pyjsonrpc.rpcmethod
    def logNewsClickForUser(self, user_id, news_id, rate):
        logging.info('backend_server: %s rates %s for news: %s' % (user_id, rate, news_id))
        return operations.logNewsClickForUser(user_id, news_id, rate)

# Threading HTTP Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (server_host, server_port),
    RequestHandlerClass = RequestHandler
)

print "Starting HTTP server on %s:%d" % (server_host, server_port)
logging.info('starting backend server on %s:%d' % (server_host, server_port))

http_server.serve_forever()

# WARNING: ISSUE with cloudAMQP client timeout: have to keep this cloud client heartbeating somewhere
# or the task msg send stops working after some time