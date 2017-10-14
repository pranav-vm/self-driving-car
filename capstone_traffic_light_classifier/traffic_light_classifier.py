import numpy as np
import tensorflow as tf


EPS  = np.finfo('float32').eps


class TrafficLightClassifier:

    def __init__(self, x, targets, keep_prob, n_classes, learning_rate):

        self.x         = x
        self.targets   = targets
        self.keep_prob = keep_prob

        self.n_classes      = n_classes      # {void, red, yellow, green}
        self.learning_rate  = learning_rate  # learning rate used in train step

        self._inference     = None
        self._loss          = None
        self._train_step    = None
        self._summaries     = None

        self.inference
        self.loss
        self.train_step
        # self.summaries # todo add these

    @property
    def inference(self):
        if self._inference is None:
            with tf.variable_scope('inference'):

                conv1_filters = 32
                conv1 = tf.layers.conv2d(self.x, conv1_filters, kernel_size=(3, 3), padding='same', activation=tf.nn.relu)
                pool1 = tf.layers.max_pooling2d(conv1, pool_size=(2, 2), strides=(2, 2), padding='same')

                conv2_filters = 64
                conv2 = tf.layers.conv2d(pool1, conv2_filters, kernel_size=(3, 3), padding='same', activation=tf.nn.relu)
                pool2 = tf.layers.max_pooling2d(conv2, pool_size=(2, 2), strides=(2, 2), padding='same')

                _, h, w, c = pool2.get_shape().as_list()
                pool2_flat = tf.reshape(pool2, shape=[-1, h * w * c])

                pool2_drop = tf.nn.dropout(pool2_flat, keep_prob=self.keep_prob)

                hidden_units = self.n_classes
                hidden = tf.layers.dense(pool2_drop, units=hidden_units, activation=tf.nn.relu)

                logits = tf.layers.dense(hidden, units=self.n_classes, activation=None)

                self._inference = tf.nn.softmax(logits)

        return self._inference

    @property
    def loss(self):
        if self._loss is None:
            with tf.variable_scope('loss'):
                predictions = self.inference
                targets_onehot = tf.one_hot(self.targets, depth=self.n_classes)
                self._loss = tf.reduce_mean(-tf.reduce_sum(targets_onehot * tf.log(predictions + EPS), reduction_indices=1))
        return self._loss

    @property
    def train_step(self):
        if self._train_step is None:
            with tf.variable_scope('training'):
                self._train_step = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(self.loss)
        return self._train_step
