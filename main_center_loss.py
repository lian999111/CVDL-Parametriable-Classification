# %%
# TODO: This makes sure the weights are initialized the same, but results after training still not reproducible
seed_value = 1
import os
os.environ['PYTHONHASHSEED']=str(seed_value)
os.environ['TF_CUDNN_DETERMINISTIC'] = '1'  # new flag present in tf 2.0+
import random
random.seed(seed_value)
import numpy as np 
np.random.seed(seed_value)
import tensorflow as tf 
tf.random.set_seed(seed_value)   

import DLCVDatasets
import lenet_model
import utils_center_loss

# %% Load and preprocess data
dataset_name = 'mnist'    # mnist or cifar10
train_size = 60000
test_size = 10000
used_labels = list(range(0, 9))    # the labels to be loaded
num_classes = len(used_labels)
x_train, y_train, x_test, y_test, class_names = DLCVDatasets.get_dataset(dataset_name,
                                                                         used_labels=used_labels,
                                                                         training_size=train_size,
                                                                         test_size=test_size)
# Normalization
mean = np.mean(x_train)
x_train -= mean
x_test -= mean
x_train, x_test = x_train / 255.0, x_test / 255.0

# Reshape to add the channel dimension
x_train = np.reshape(x_train, x_train.shape+(1,))
x_test = np.reshape(x_test, x_test.shape+(1,))
input_shape = x_train.shape[1:]

# %% Get the model
lenet = lenet_model.get_lenet_model(input_shape=input_shape)
lenet.summary()

# %% Train the model with center loss
utils_center_loss.train_model_with_centerloss(lenet, x_train, y_train,
                                              x_test, y_test, num_classes=10, len_encoding=64,
                                              num_epochs=5, batch_size=64,
                                              learning_rate=0.005, alpha=0.1, ratio=0.5)

# %% Evaluate the model
# Load the complete dataset, including 0 - 9
used_labels = list(range(0, 10))    # the labels to be loaded
x_train, y_train, x_test, y_test, class_names = DLCVDatasets.get_dataset(dataset_name,
                                                                         used_labels=used_labels,
                                                                         training_size=train_size,
                                                                         test_size=test_size)
# Reshape to add the channel dimension
x_train = np.reshape(x_train, x_train.shape+(1,))
x_test = np.reshape(x_test, x_test.shape+(1,))

x_2 = x_test[y_test == 2]
encoding_2_0 = tf.math.l2_normalize(lenet(x_2[[0],]))   # this strange [[0],] indexing is to keep dimensions after index slicing
encoding_2_1 = tf.math.l2_normalize(lenet(x_2[[20],]))

x_5 = x_test[y_test == 5]
encoding_5_0 = tf.math.l2_normalize(lenet(x_5[[0],]))
encoding_5_1 = tf.math.l2_normalize(lenet(x_5[[20],]))

x_6 = x_test[y_test == 6]
encoding_6_0 = tf.math.l2_normalize(lenet(x_6[[0],]))
encoding_6_1 = tf.math.l2_normalize(lenet(x_6[[20],]))

x_9 = x_test[y_test == 9]
encoding_9_0 = tf.math.l2_normalize(lenet(x_9[[0],]))
encoding_9_1 = tf.math.l2_normalize(lenet(x_9[[20],]))

print('2 & 2: {}'.format(tf.norm(encoding_2_0 - encoding_2_1).numpy()))
print('2 & 5: {}'.format(tf.norm(encoding_2_0 - encoding_5_0).numpy()))
print('2 & 6: {}'.format(tf.norm(encoding_2_0 - encoding_6_0).numpy()))

print('5 & 5: {}'.format(tf.norm(encoding_5_0 - encoding_5_1).numpy()))
print('6 & 6: {}'.format(tf.norm(encoding_6_0 - encoding_6_1).numpy()))
print('5 & 6: {}'.format(tf.norm(encoding_5_0 - encoding_6_0).numpy()))

print('9 & 9: {}'.format(tf.norm(encoding_9_0 - encoding_9_1).numpy()))
print('5 & 9: {}'.format(tf.norm(encoding_5_0 - encoding_9_0).numpy()))
print('6 & 9: {}'.format(tf.norm(encoding_6_0 - encoding_9_0).numpy()))

# %% Intraclass test
test_num = 0
anchor_idx = 0
x = x_test[y_test == test_num]
encoding_anchor = tf.math.l2_normalize(lenet(x[[anchor_idx],]))
for idx in range(0, 100):
    encoding = tf.math.l2_normalize(lenet(x[[idx],]))
    print('Intraclass: No.{}, id{} & id{}: {}'.format(test_num, anchor_idx, idx, tf.norm(encoding - encoding_anchor).numpy()))

# %%
