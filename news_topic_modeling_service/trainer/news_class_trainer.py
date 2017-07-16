import news_cnn_model
import numpy as np
import os
import pandas as pd
import pickle
import shutil
import sys
import nltk
# uncomment the next 2 lines if anything in nltk-data not found
#nltk.download('punkt')
#nltk.download('all-corpora')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import string
import tensorflow as tf
from sklearn import metrics
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client

learn = tf.contrib.learn

# dir related params are still hard coded
MODEL_OUTPUT_DIR = '../model/'
DATA_SET_FILE = '../training_data/labeled_news_v3.csv'
VARS_FILE = '../model/vars'
VOCAB_PROCESSOR_SAVE_FILE = '../model/vocab_procesor_save_file'
REMOVE_PREVIOUS_MODEL = True

learning_param = config_service_client.getMachineLearningParamForUsecase('topic_modeling')
number_classes = int(learning_param['number_classes'])
training_index_end = int(learning_param['training_index_end'])
max_document_length = int(learning_param['max_document_length'])
min_frequency = float(learning_param['min_frequency'])
steps = int(learning_param['steps'])
learning_rate = float(learning_param['learning_rate'])

def main(unused_argv):
    if REMOVE_PREVIOUS_MODEL:
        # Remove old model
        shutil.rmtree(MODEL_OUTPUT_DIR)
        os.mkdir(MODEL_OUTPUT_DIR)

    # Prepare training and testing data
    df = pd.read_csv(DATA_SET_FILE, header=None)
    df.sample(frac=1)
    stemmer = SnowballStemmer('english')
    for i in range(0, len(df)):
        print i
        df_line = str(df.loc[i, 1]) + ' ' + str(df.loc[i, 2]) + ' ' + str(df.loc[i, 3])
        df_line = df_line.translate(None, string.punctuation)
        df_line = df_line.lower()
        df_tokens = word_tokenize(df_line)
        df_filtered_tokens = []
        for word in df_tokens:
            if word not in stopwords.words('english'):
                df_filtered_tokens.append(stemmer.stem(word.decode('utf-8')))
        df_filtered_line = ' '.join(df_filtered_tokens)
        #print df_filtered_line
        df.loc[i, 1] = df_filtered_line
        #df.loc[i, 2] = df.loc[i, 3]

    train_df = df[0:training_index_end]
    test_df = df.drop(train_df.index)

    # x - news title, y - class
    x_train = train_df[1]
    y_train = train_df[0]
    x_test = test_df[1]
    y_test = test_df[0]

    # Process vocabulary
    vocab_processor = learn.preprocessing.VocabularyProcessor(max_document_length, min_frequency, None, None)
    x_train = np.array(list(vocab_processor.fit_transform(x_train)))
    x_test = np.array(list(vocab_processor.transform(x_test)))

    n_words = len(vocab_processor.vocabulary_)
    print('Total words: %d' % n_words)

    # Saving n_words and vocab_processor:
    with open(VARS_FILE, 'w') as f:
        pickle.dump(n_words, f)

    vocab_processor.save(VOCAB_PROCESSOR_SAVE_FILE)

    # Build model
    classifier = learn.Estimator(
        model_fn=news_cnn_model.generate_cnn_model(number_classes, n_words, learning_rate),
        model_dir=MODEL_OUTPUT_DIR)

    # Train and predict
    classifier.fit(x_train, y_train, steps=steps)

    # Evaluate model
    y_predicted = [
        p['class'] for p in classifier.predict(x_test, as_iterable=True)
    ]

    score = metrics.accuracy_score(y_test, y_predicted)
    print('Accuracy: {0:f}'.format(score))

if __name__ == '__main__':
    tf.app.run(main=main)