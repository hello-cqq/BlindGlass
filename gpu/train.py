# -*- coding: UTF-8 -*-
import tensorflow as tf
import numpy as np
import os.path as osp
import os
import model
import logging
import time
from datetime import datetime
from dataloader import load_data

slim = tf.contrib.slim

# 定义超参及路径
flags = tf.app.flags

flags.DEFINE_string('data_dir',
                    './data',
                    'Path to training tfrecord file.')
flags.DEFINE_string('checkpoint_path',
                    './ckpt/' +
                    'resnet_v1_50.ckpt',
                    'Path to pretrained ResNet-50 model.')
flags.DEFINE_string('logdir', './logs', 'Path to log directory.')
flags.DEFINE_float('learning_rate', 0.01, 'Initial learning rate.')
flags.DEFINE_float(
    'learning_rate_decay_factor', 0.1, 'Learning rate decay factor.')
flags.DEFINE_float(
    'num_epochs_per_decay', 100.0,
    'Number of epochs after which learning rate decays. Note: this flag counts '
    'epochs per clone but aggregates per sync replicas. So 1.0 means that '
    'each clone will go over full epoch individually, but replicas will go '
    'once across all replicas.')
flags.DEFINE_integer('num_samples', 80, 'Number of samples.')
flags.DEFINE_integer('num_steps', 1000, 'Number of steps.')
flags.DEFINE_integer('batch_size', 32, 'Batch size')

FLAGS = flags.FLAGS
'''
模型预训练脚本
'''
# 设置学习率
def configure_learning_rate(num_samples_per_epoch, global_step):
    '''
    设置学习率
    '''
    decay_steps = int(num_samples_per_epoch * FLAGS.num_epochs_per_decay /
                      FLAGS.batch_size)
    return tf.train.exponential_decay(FLAGS.learning_rate,
                                      global_step,
                                      decay_steps,
                                      FLAGS.learning_rate_decay_factor,
                                      staircase=True,
                                      name='exponential_decay_learning_rate')

# 设置训练batch坐标
def batch_indices(num_batches, data, batch_size):
    '''
    设置训练batch坐标
    '''
    batch_indices = []
    index_in_epoch = 0
    dataset_size = len(data)
    dataset_indices = np.arange(dataset_size)
    np.random.shuffle(dataset_indices)

    for _ in range(num_batches):
      start = index_in_epoch
      index_in_epoch += batch_size
      if index_in_epoch > dataset_size:

        # 随机打乱
        np.random.shuffle(dataset_indices)

        # 开始下一个循环
        start = 0
        index_in_epoch = batch_size

      end = index_in_epoch
      # 得到每个循环的batch坐标
      batch_indices.append(dataset_indices[start:end].tolist())

    return batch_indices

def main(_):
    '''
    模型训练主函数，设置GPU，样本参数等等
    '''
    # 设置GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = '1'
    # 训练样本的数量
    num_samples = FLAGS.num_samples
    # 读取训练和验证的图片和标签
    image, label = load_data(FLAGS.data_dir, 'gt.txt')
    image_val, label_val = load_data('data_val', 'gt_val.txt')

    # 调用model类创建模型
    cls_model = model.Model(is_training=True, num_classes=5)
    cls_model.build()

    # 记录图
    tf.summary.scalar('loss', cls_model.loss)
    tf.summary.scalar('accuracy', cls_model.accuracy)

    # 设置全局步数、学习率和优化器
    global_step = slim.create_global_step()
    learning_rate = configure_learning_rate(num_samples, global_step)
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
    train_op = slim.learning.create_train_op(cls_model.loss, optimizer,
                                             summarize_gradients=True)
    tf.summary.scalar('learning_rate', learning_rate)

    # 读取预训练模型resnet_v1_50中的参数
    tf.contrib.framework.init_from_checkpoint(FLAGS.checkpoint_path, {
        'resnet_v1_50/': 'resnet_v1_50/'
    })
    # 创建模型保存的保存器
    saver = tf.train.Saver(tf.global_variables(),
                           max_to_keep=None)
    global_variables_init_op = tf.global_variables_initializer()
    local_variables_init_op = tf.local_variables_initializer()
    gpu_options = tf.GPUOptions(allow_growth=True)
    sess_config = tf.ConfigProto(gpu_options=gpu_options)
    # 创建会话
    sess = tf.Session(config=sess_config)
    model_path = tf.train.latest_checkpoint(FLAGS.logdir)
    logging.info('Restore from last checkpoint: {}'.format(model_path))

    # 从头训练
    if not model_path:
        sess.run(global_variables_init_op)
        sess.run(local_variables_init_op)
        start_step = 0
    # 断点续接，继续训练
    else:
        logging.info('Restore from last checkpoint: {}'.format(model_path))
        sess.run(local_variables_init_op)
        saver.restore(sess, model_path)
        start_step = tf.train.global_step(sess, global_step.name) + 1
    total_steps = FLAGS.num_steps
    batch_inds = batch_indices(total_steps - start_step + 1, image, FLAGS.batch_size)
    print('training!')
    # 训练的主循环
    for step, batch in enumerate(batch_inds):
      # 得到loss
      _, loss, acc = sess.run([train_op, cls_model.loss, cls_model.accuracy], feed_dict={"data_feed:0": image[batch],
                                                                "label_feed:0": label[batch]})
      # 每10步打印一次loss
      if step % 10 == 0:
        print('step: %d, loss: %.2f' % (step, loss))
      # 每100步打印一次验证集的准确率
      if step % 100 == 0:
        accuracy = sess.run([cls_model.accuracy], feed_dict={"data_feed:0": image_val,
                                                             "label_feed:0": label_val})
        print(accuracy)
      # 每100步存一次模型
      if step % 100 == 0 or (step + 1) == total_steps:
        checkpoint_path = osp.join(FLAGS.logdir, 'model.ckpt')
        saver.save(sess, checkpoint_path, global_step=step)

if __name__ == '__main__':
    tf.app.run()