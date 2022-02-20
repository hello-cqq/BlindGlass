# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from tensorflow.contrib.slim import nets

slim = tf.contrib.slim

# resnet_v1_50 model
class Model(object):
    def __init__(self, num_classes, image_size=640):
        self.num_classes = num_classes  # 5 classes
        self.image_size = image_size    # 224

    # set placeholders for input images and labels
    def build_inputs(self):
        self.is_training = tf.placeholder(shape=None, dtype=tf.bool, name='is_training')
        self.data_feed = tf.placeholder(shape=[None, self.image_size, self.image_size, 3],
                                        dtype=tf.int64, name='data_feed')
        self.label_feed = tf.placeholder(shape=[None, ],
                                         dtype=tf.int64, name='label_feed')
        self.data_feed = tf.to_float(self.data_feed)

    # build the resnet_v1_50 model
    def build_logits(self):
        # set a arg_scope for whether to train the layers
        with slim.arg_scope(
                [slim.conv2d, slim.batch_norm],
                trainable=False):
            with slim.arg_scope(nets.resnet_v1.resnet_arg_scope()):
                net, endpoints = nets.resnet_v1.resnet_v1_50(
                    self.data_feed, num_classes=None,
                    is_training=self.is_training)
        net = tf.squeeze(net, axis=[1, 2])
        logits = slim.fully_connected(net, num_outputs=self.num_classes,
                                      activation_fn=None, scope='fc')
        self.logits = logits
        predict = tf.nn.softmax(self.logits)
        self.predict = tf.argmax(predict, axis=1)

    def build_loss(self):
        self.loss = tf.losses.sparse_softmax_cross_entropy(
            logits=self.logits,
            labels=self.label_feed,
            scope='Loss')
        tf.losses.add_loss(self.loss)
        self.loss = tf.losses.get_total_loss()

    def build_accuracy(self):
        self.accuracy = tf.reduce_mean(tf.cast(tf.equal(self.predict, self.label_feed), dtype=tf.float32))



    def build(self):
        self.build_inputs()
        self.build_logits()
        self.build_loss()
        self.build_accuracy()




