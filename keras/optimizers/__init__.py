# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# pylint: disable=invalid-name
"""Built-in optimizer classes.

For more examples see the base class `tf.keras.optimizers.Optimizer`.
"""

import tensorflow.compat.v2 as tf

from keras import backend
from keras.optimizers.optimizer_experimental import optimizer as optimizer_experimental
from keras.optimizers.optimizer_experimental import adadelta as adadelta_experimental
from keras.optimizers.optimizer_experimental import adagrad as adagrad_experimental
from keras.optimizers.optimizer_experimental import adam as adam_experimental
from keras.optimizers.optimizer_experimental import adamax as adamax_experimental
from keras.optimizers.optimizer_experimental import adamw as adamw_experimental
from keras.optimizers.optimizer_experimental import ftrl as ftrl_experimental
from keras.optimizers.optimizer_experimental import rmsprop as rmsprop_experimental
from keras.optimizers.optimizer_experimental import sgd as sgd_experimental
from keras.optimizers.optimizer_v1 import Optimizer
from keras.optimizers.optimizer_v1 import TFOptimizer
from keras.optimizers.optimizer_v2 import adadelta as adadelta_v2
from keras.optimizers.optimizer_v2 import adagrad as adagrad_v2
from keras.optimizers.optimizer_v2 import adam as adam_v2
from keras.optimizers.optimizer_v2 import adamax as adamax_v2
from keras.optimizers.optimizer_v2 import ftrl
from keras.optimizers.optimizer_v2 import gradient_descent as gradient_descent_v2
from keras.optimizers.optimizer_v2 import nadam as nadam_v2
from keras.optimizers.optimizer_v2 import optimizer_v2 as base_optimizer_v2
from keras.optimizers.optimizer_v2 import rmsprop as rmsprop_v2
from keras.utils.generic_utils import deserialize_keras_object
from keras.utils.generic_utils import serialize_keras_object
from tensorflow.python.util.tf_export import keras_export


@keras_export('keras.optimizers.serialize')
def serialize(optimizer):
  """Serialize the optimizer configuration to JSON compatible python dict.

  The configuration can be used for persistence and reconstruct the `Optimizer`
  instance again.

  >>> tf.keras.optimizers.serialize(tf.keras.optimizers.SGD())
  {'class_name': 'SGD', 'config': {'name': 'SGD', 'learning_rate': 0.01,
                                   'decay': 0.0, 'momentum': 0.0,
                                   'nesterov': False}}

  Args:
    optimizer: An `Optimizer` instance to serialize.

  Returns:
    Python dict which contains the configuration of the input optimizer.
  """
  return serialize_keras_object(optimizer)


@keras_export('keras.optimizers.deserialize')
def deserialize(config, custom_objects=None):
  """Inverse of the `serialize` function.

  Args:
      config: Optimizer configuration dictionary.
      custom_objects: Optional dictionary mapping names (strings) to custom
        objects (classes and functions) to be considered during deserialization.

  Returns:
      A Keras Optimizer instance.
  """
  # loss_scale_optimizer has a direct dependency of optimizer, import here
  # rather than top to avoid the cyclic dependency.
  from keras.mixed_precision import loss_scale_optimizer  # pylint: disable=g-import-not-at-top
  all_classes = {
      'adadelta': adadelta_v2.Adadelta,
      'adagrad': adagrad_v2.Adagrad,
      'adam': adam_v2.Adam,
      'adamax': adamax_v2.Adamax,
      'experimentaladadelta': adadelta_experimental.Adadelta,
      'experimentaladagrad': adagrad_experimental.Adagrad,
      'experimentaladam': adam_experimental.Adam,
      'experimentalsgd': sgd_experimental.SGD,
      'nadam': nadam_v2.Nadam,
      'rmsprop': rmsprop_v2.RMSprop,
      'sgd': gradient_descent_v2.SGD,
      'ftrl': ftrl.Ftrl,
      'lossscaleoptimizer': loss_scale_optimizer.LossScaleOptimizer,
      'lossscaleoptimizerv3': loss_scale_optimizer.LossScaleOptimizerV3,
      # LossScaleOptimizerV1 was an old version of LSO that was removed.
      # Deserializing it turns it into a LossScaleOptimizer
      'lossscaleoptimizerv1': loss_scale_optimizer.LossScaleOptimizer,
  }

  # Make deserialization case-insensitive for built-in optimizers.
  if config['class_name'].lower() in all_classes:
    config['class_name'] = config['class_name'].lower()
  return deserialize_keras_object(
      config,
      module_objects=all_classes,
      custom_objects=custom_objects,
      printable_module_name='optimizer')


@keras_export('keras.optimizers.get')
def get(identifier):
  """Retrieves a Keras Optimizer instance.

  Args:
      identifier: Optimizer identifier, one of
          - String: name of an optimizer
          - Dictionary: configuration dictionary. - Keras Optimizer instance (it
            will be returned unchanged). - TensorFlow Optimizer instance (it
            will be wrapped as a Keras Optimizer).

  Returns:
      A Keras Optimizer instance.

  Raises:
      ValueError: If `identifier` cannot be interpreted.
  """
  if isinstance(
      identifier,
      (Optimizer, base_optimizer_v2.OptimizerV2,
       optimizer_experimental.Optimizer)):
    return identifier
  # Wrap legacy TF optimizer instances
  elif isinstance(identifier, tf.compat.v1.train.Optimizer):
    opt = TFOptimizer(identifier)
    backend.track_tf_optimizer(opt)
    return opt
  elif isinstance(identifier, dict):
    return deserialize(identifier)
  elif isinstance(identifier, str):
    config = {'class_name': str(identifier), 'config': {}}
    return deserialize(config)
  else:
    raise ValueError(
        'Could not interpret optimizer identifier: {}'.format(identifier))
