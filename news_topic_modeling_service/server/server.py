import news_classes_v2
import numpy as np
import os
import pandas as pd
import pickle
import pyjsonrpc
import sys
import tensorflow as tf
import time
from tensorflow.contrib.learn.python.learn.estimators import model_fn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# prepare logging
import logging
logging.basicConfig(filename='../logging/news_topic_modeling_server.log', level=logging.INFO)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'trainer'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client
import news_cnn_model

learn = tf.contrib.learn

# ask for server configs
server_config = config_service_client.getServerConfigForServer('news_topic_modeling_server')
server_host = server_config['url']
server_port = int(server_config['port'])

# Note: dir related params are still hard coded here
MODEL_DIR = '../model'
MODEL_UPDATE_LAG_IN_SECONDS = 60
VARS_FILE = '../model/vars'
VOCAB_PROCESSOR_SAVE_FILE = '../model/vocab_procesor_save_file'
DATA_FILE = '../training_data/labeled_news_v3.csv'

# ask for learning params
learning_param = config_service_client.getMachineLearningParamForUsecase('topic_modeling')
number_classes = int(learning_param['number_classes'])
testing_index_end = int(learning_param['testing_index_end'])
learning_rate = float(learning_param['learning_rate'])

n_words = 0
vocab_processor = None
classifier = None

def restoreVars():
    with open(VARS_FILE, 'r') as f:
        global n_words
        n_words = pickle.load(f)
    global vocab_processor
    vocab_processor = learn.preprocessing.VocabularyProcessor.restore(VOCAB_PROCESSOR_SAVE_FILE)
    print vocab_processor
    print 'Vars updated.'
    logging.info('news_topic_modeling: vars updated')

def loadModel():
    global classifier
    classifier = learn.Estimator(
        model_fn=news_cnn_model.generate_cnn_model(number_classes, n_words, learning_rate),
        model_dir=MODEL_DIR)
    # Prepare training and testing
    df = pd.read_csv(DATA_FILE, header=None)
    # TODO: fix this until https://github.com/tensorflow/tensorflow/issues/5548 is solved.
    # We have to call evaluate or predict at least once to make the restored Estimator work.
    test_df = df[0:testing_index_end]
    x_test = test_df[1]
    x_test = np.array(list(vocab_processor.transform(x_test)))
    y_test = test_df[0]
    classifier.evaluate(x_test, y_test)

    print "Model updated."
    logging.info('news_topic_modeling: model updated')

restoreVars()
loadModel()

print "Model loaded"

class ReloadModelHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Reload model
        print "Model update detected. Loading new model."
        logging.info('news_topic_modeling: updating new model')
        time.sleep(MODEL_UPDATE_LAG_IN_SECONDS)
        restoreVars()
        loadModel()

class RequestHandler(pyjsonrpc.HttpRequestHandler):
    @pyjsonrpc.rpcmethod
    def classify(self, text):
        text_series = pd.Series([text])
        predict_x = np.array(list(vocab_processor.transform(text_series)))
        print predict_x
        y_predicted = [
            p['class'] for p in classifier.predict(
                predict_x, as_iterable=True)
        ]
        # y_predicted is a list with only one class index in it
        print y_predicted
        topic = news_classes_v2.class_map[str(y_predicted[0])]
        return topic

# Setup watchdog
observer = Observer()
observer.schedule(ReloadModelHandler(), path=MODEL_DIR, recursive=False)
observer.start()

# Threading HTTP-Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (server_host, server_port),
    RequestHandlerClass = RequestHandler
)

print "Starting predicting server ..."
print "URL: http://" + str(server_host) + ":" + str(server_port)
logging.info('starting classifying server: %s:%s' %(server_host, server_port))

http_server.serve_forever()