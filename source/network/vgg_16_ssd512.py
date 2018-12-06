# Copyright 2018 Lambda Labs. All Rights Reserved.
# Licensed under
# ============================================================================

"""VGG 19 backbone for SSD based on Tensorflow slim
"""
from __future__ import print_function

import tensorflow as tf

from source.network.external.tf_slim import vgg

slim = tf.contrib.slim


def net(inputs, data_format, is_training, init_flag, ckpt_path):

  (net, end_points) = vgg.vgg_16_ssd512(inputs, is_training=is_training)

  if init_flag:
    tf.logging.set_verbosity(tf.logging.WARN)
    restore_var_list = ["vgg_16"]
    variables_to_restore = {v.name.split(':')[0]: v
                            for v in tf.get_collection(
                                tf.GraphKeys.TRAINABLE_VARIABLES)}
    if restore_var_list is not None:
      variables_to_restore = {v: v for v in variables_to_restore
                              if any(x in v for x in restore_var_list)}

    print("Restoring weights from " + ckpt_path)
    tf.train.init_from_checkpoint(ckpt_path,
                                  variables_to_restore)
    init_flag = False
    print("Weights restored.")
    tf.logging.set_verbosity(tf.logging.INFO)

  return net, end_points, init_flag
