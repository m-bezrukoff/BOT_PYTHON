# Q1: у меня есть следующий код, который принимает первые 2000 записей в качестве обучения и от 2001 до 20000
# записей в качестве теста, но я не знаю, как изменить код, чтобы сделать прогноз цены закрытия сегодня
# и через 1 день??? Пожалуйста, посоветуйте!


import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

def feature_scaling(input_pd, scaling_meathod):
    if scaling_meathod == 'z-score':
       scaled_pd = (input_pd - input_pd.mean()) / input_pd.std()
    elif scaling_meathod == 'min-max':
       scaled_pd = (input_pd - input_pd.min()) / (input_pd.max() -
    input_pd.min())
    return scaled_pd

def input_reshape(input_pd, start, end, batch_size, batch_shift, n_features):
    temp_pd = input_pd[start-1: end+batch_size-1]
    output_pd = map(lambda y : temp_pd[y:y+batch_size], xrange(0, end-start+1, batch_shift))
    output_temp = map(lambda x : np.array(output_pd[x]).reshape([-1]), xrange(len(output_pd)))
    output = np.reshape(output_temp, [-1, batch_size, n_features])
    return output

def target_reshape(input_pd, start, end, batch_size, batch_shift, n_step_ahead, m_steps_pred):
    temp_pd = input_pd[start+batch_size+n_step_ahead-2: end+batch_size+n_step_ahead+m_steps_pred-2]
    print temp_pd
    output_pd = map(lambda y : temp_pd[y:y+m_steps_pred], xrange(0, end-start+1, batch_shift))
    output_temp = map(lambda x : np.array(output_pd[x]).reshape([-1]), xrange(len(output_pd)))
    output = np.reshape(output_temp, [-1,1])
    return output

def lstm(input, n_inputs, n_steps, n_of_layers, scope_name):
    num_layers = n_of_layers
    input = tf.transpose(input,[1, 0, 2])
    input = tf.reshape(input,[-1, n_inputs])
    input = tf.split(0, n_steps, input)
    with tf.variable_scope(scope_name):
    cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=n_inputs)
    cell = tf.nn.rnn_cell.MultiRNNCell([cell]*num_layers)
    output, state = tf.nn.rnn(cell, input, dtype=tf.float32)    yi1
    output = output[-1]
    return output

    feature_to_input = ['open price', 'highest price', 'lowest price', 'close price','turnover', 'volume','mean price']
    feature_to_predict = ['close price']
    feature_to_scale = ['volume']
    sacling_meathod = 'min-max'

    train_start = 1
    train_end = 1000
    test_start = 1001
    test_end = 20000

    batch_size = 100
    batch_shift = 1
    n_step_ahead = 1
    m_steps_pred = 1
    n_features = len(feature_to_input)

    lstm_scope_name = 'lstm_prediction'
    n_lstm_layers = 1
    n_pred_class = 1
    learning_rate = 0.1
    EPOCHS = 1000
    PRINT_STEP = 100

    read_data_pd = pd.read_csv('./stock_price.csv')
    temp_pd = feature_scaling(input_pd[feature_to_scale],sacling_meathod)
    input_pd[feature_to_scale] = temp_pd
    train_input_temp_pd = input_pd[feature_to_input]
    train_input_nparr = input_reshape(train_input_temp_pd,
    train_start, train_end, batch_size, batch_shift, n_features)

    train_target_temp_pd = input_pd[feature_to_predict]
    train_target_nparr = target_reshape(train_target_temp_pd, train_start, train_end, batch_size, batch_shift, n_step_ahead, m_steps_pred)

    test_input_temp_pd = input_pd[feature_to_input]
    test_input_nparr = input_reshape(test_input_temp_pd, test_start, test_end, batch_size, batch_shift, n_features)

    test_target_temp_pd = input_pd[feature_to_predict]
    test_target_nparr = target_reshape(test_target_temp_pd, test_start, test_end, batch_size, batch_shift, n_step_ahead, m_steps_pred)

    tf.reset_default_graph()

    x_ = tf.placeholder(tf.float32, [None, batch_size, n_features])
    y_ = tf.placeholder(tf.float32, [None, 1])
    lstm_output = lstm(x_, n_features, batch_size, n_lstm_layers, lstm_scope_name)

    W = tf.Variable(tf.random_normal([n_features, n_pred_class]))
    b = tf.Variable(tf.random_normal([n_pred_class]))
    y = tf.matmul(lstm_output, W) + b
    cost_func = tf.reduce_mean(tf.square(y - y_))
    train_op = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost_func)

    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)
    init = tf.initialize_all_variables()
    with tf.Session() as sess:
        sess.run(init)
        for ii in range(EPOCHS):
            sess.run(train_op, feed_dict={x_:train_input_nparr, y_:train_target_nparr})
            if ii % PRINT_STEP == 0:
               cost = sess.run(cost_func, feed_dict={x_:train_input_nparr, y_:train_target_nparr})
               print 'iteration =', ii, 'training cost:', cost