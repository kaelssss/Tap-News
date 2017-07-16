import operator
import os
import pyjsonrpc
import sys
import news_classes_v2
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client
import mongodb_client
import logging

logging.basicConfig(filename='./logging/news_recommendation_server.log', level=logging.INFO)

server_config = config_service_client.getServerConfigForServer('news_recommendation_server')
server_host = server_config['url']
server_port = int(server_config['port'])

preference_model_db_config = config_service_client.getDatabaseConfigForUsecase('user_preference_model')
preference_model_table_name = preference_model_db_config['database_name']

learning_param = config_service_client.getMachineLearningParamForUsecase('topic_modeling')
num_classes = int(learning_param['number_classes'])
initial_p = 1.0 / num_classes

class RequestHandler(pyjsonrpc.HttpRequestHandler):

    @pyjsonrpc.rpcmethod
    def getPreferenceForUser(self, user_id):
        logging.info('news_recommendation_server: getting preference model for %s' % user_id)
        db = mongodb_client.get_db()
        model = db[preference_model_table_name].find_one({'userId':user_id})
        if model is None:
            print 'Creating preference model for new user: %s' % user_id
            logging.info('news_recommendation_server: creating preference model for %s' % user_id)
            new_model = {'userId' : user_id}
            preference = {}
            for i in news_classes_v2.classes:
                preference[i] = float(initial_p)
            new_model['preference'] = preference
            model = new_model
            db[preference_model_table_name].replace_one({'userId': user_id}, model, upsert=True)
        
        preference_tuples = model['preference'].items()
        preference_list = [x[0] for x in preference_tuples]
        preference_value_list = [x[1] for x in preference_tuples]

        print preference_list
        print preference_value_list
        return preference_value_list


# Threading HTTP Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (server_host, server_port),
    RequestHandlerClass = RequestHandler
)

print "Starting HTTP server on %s:%d" % (server_host, server_port)
logging.info("Starting HTTP server on %s:%d" % (server_host, server_port))

http_server.serve_forever()