import os
import sys
import tensorflow as tf
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import config_service_client

learning_param = config_service_client.getMachineLearningParamForUsecase('topic_modeling')
number_filters = int(learning_param['number_filters'])
embedding_size = int(learning_param['embedding_size'])
window_size = int(learning_param['window_size'])
filter_shape1 = [window_size, embedding_size]
filter_shape2 = [window_size, number_filters]
pooling_window = int(learning_param['pooling_window'])
pooling_stride = int(learning_param['pooling_window'])

def generate_cnn_model(n_classes, n_words, learning_rate):
    """2 layer ConvNet to predict from sequence of words to a class."""
    def cnn_model(features, target):
        # Convert indexes of words into embeddings.
        # This creates embeddings matrix of [n_words, embedding_size] and then
        # maps word indexes of the sequence into [batch_size, sequence_length,
        # embedding_size].

        target = tf.one_hot(target, n_classes, 1, 0)
        word_vectors = tf.contrib.layers.embed_sequence(
            features, vocab_size=n_words, embed_dim=embedding_size, scope='words')
        word_vectors = tf.expand_dims(word_vectors, 3)
        with tf.variable_scope('CNN_layer1'):
            # Apply Convolution filtering on input sequence.
            conv1 = tf.contrib.layers.convolution2d(
                word_vectors, number_filters, filter_shape1, padding='VALID')
            # Add a RELU for non linearity.
            conv1 = tf.nn.relu(conv1)
            # Max pooling across output of Convolution+Relu.
            pool1 = tf.nn.max_pool(
                conv1,
                ksize=[1, pooling_window, 1, 1],
                strides=[1, pooling_stride, 1, 1],
                padding='SAME')
            # Transpose matrix so that number_filters from convolution becomes width.
            pool1 = tf.transpose(pool1, [0, 1, 3, 2])
        with tf.variable_scope('CNN_layer2'):
            # Second level of convolution filtering.
            conv2 = tf.contrib.layers.convolution2d(
                pool1, number_filters, filter_shape2, padding='VALID')
            # Max across each filter to get useful features for classification.
            pool2 = tf.squeeze(tf.reduce_max(conv2, 1), squeeze_dims=[1])

        # Apply regular WX + B and classification.
        logits = tf.contrib.layers.fully_connected(pool2, n_classes, activation_fn=None)
        loss = tf.contrib.losses.softmax_cross_entropy(logits, target)

        train_op = tf.contrib.layers.optimize_loss(
            loss,
            tf.contrib.framework.get_global_step(),
            optimizer='Adam',
            learning_rate=learning_rate)

        return ({
            'class': tf.argmax(logits, 1),
            'prob': tf.nn.softmax(logits)
        }, loss, train_op)

    return cnn_model