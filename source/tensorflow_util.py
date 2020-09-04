import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.layers import Dense, MaxPooling2D, Conv2D, Dropout, \
    Flatten, BatchNormalization, Activation, GlobalAvgPool2D
from tensorflow.keras.models import Sequential


class ResidualUnit(keras.layers.Layer):
    def __init__(self, filters, strides=1, activation="relu", **kwargs):
        super().__init__(**kwargs)
        self.activation = keras.activations.get(activation)
        self.main_layers = [
            Conv2D(filters, 3, strides=strides, padding="same",
                   use_bias=False),
            BatchNormalization(),
            self.activation,
            Conv2D(filters, 3, strides=1, padding="same",
                   use_bias=False),
            BatchNormalization()]

        self.skip_layers = []

        if strides > 1:
            self.skip_layers = [
                Conv2D(filters, 1, strides=strides, padding="same",
                       use_bias=False),
                BatchNormalization()
            ]

    def call(self, inputs):
        Z = inputs
        for layer in self.main_layers:
            Z = layer(Z)
        skip_Z = inputs
        for layer in self.skip_layers:
            skip_Z = layer(skip_Z)
        return self.activation(Z + skip_Z)


def resnet34(x, y, scale):
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)

    try:
        x.shape
        x = x.tolist()
    except:
        pass

    try:
        x = tf.convert_to_tensor(x.tolist())
        y = tf.convert_to_tensor(y.tolist())
        input_dim = np.shape(x[0])

    except:
        input_dim = len(x[0])

    x = np.array(x)
    y = np.array(y)

    dim_persist = int(np.shape(x)[1] ** 0.5)
    x = x.reshape((np.shape(x)[0], dim_persist, dim_persist))
    x = np.expand_dims(x, -1)
    print(np.shape(x))
    samples = int(np.shape(x)[0])

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)
    print("Input vector size: " + str(input_dim))
    model = Sequential()
    model.add(Conv2D(filters=64, kernel_size=7, activation='relu', input_shape=(dim_persist, dim_persist, 1),
                     strides=2, data_format="channels_last", use_bias=False))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=3, strides=2, padding="same"))
    prev_filters = 64
    for filters in [64] * 2 + [128] * 2 + [256] * 2 + [512] * 2:
        strides = 1 if filters == prev_filters else 2
        model.add(ResidualUnit(filters, strides=strides))
        prev_filters = filters
    model.add(GlobalAvgPool2D())
    model.add(Flatten())
    model.add(Dense(1000))
    model.add(Dropout(0.5))
    model.add(Dense(1))

    model.summary()
    model.compile(optimizer='adam', loss="MSE", metrics=["MeanSquaredError", "MAE"])

    history = model.fit(x_train, y_train, epochs=500)
    ret = model.evaluate(x_test, y_test, verbose=2)

    score = str(mean_squared_error(model.predict(x_test), y_test))
    print("MSE score:   " + str(score))

    score = str(mean_absolute_error(model.predict(x_test), y_test))
    print("MAE score:   " + str(score))

    score = str(r2_score(model.predict(x_test), y_test))
    print("r2 score:   " + str(score))

    score_mae = mean_absolute_error(model.predict(x_test), y_test)
    print("scaled MAE")
    print(scale * score_mae)

    return model


def nn_basic(x, y, scale):
    try:
        x.shape
        x = x.tolist()
    except:
        pass

    try:
        x = tf.convert_to_tensor(x.tolist())
        y = tf.convert_to_tensor(y.tolist())
        input_dim = np.shape(x[0])

    except:
        input_dim = len(x[0])

    x = np.array(x)
    y = np.array(y)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)
    print("Input vector size: " + str(input_dim))

    model = tf.keras.models.Sequential()
    model.add(tf.keras.Input(shape=(input_dim,)))
    model.add(tf.keras.layers.Dense(2048, activation="relu"))
    model.add(tf.keras.Input(tf.keras.layers.Dropout(0.2)))
    model.add(tf.keras.layers.Dense(1024, activation="relu"))
    model.add(tf.keras.Input(tf.keras.layers.Dropout(0.2)))
    model.add(tf.keras.layers.Dense(512, activation="relu"))
    model.add(tf.keras.layers.Dense(1))

    # tf.keras.layers.Dropout(0.2),
    # tf.keras.layers.Dense(256),
    # mse = tf.keras.losses.MeanSquaredError()
    # mae = tf.keras.losses.MeanAverageError()

    # mae = tf.keras.losses.MAE()
    # rmse = tf.keras.losses.RMSE()
    log_dir = "./logs/training/"
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
    # model.compile(optimizer='adam', loss=mse, metrics=[keras.metrics.mae])
    model.compile(optimizer='adam', loss="MSE", metrics=["MeanSquaredError", "MAE"])

    tensorboard_cbk = TensorBoard(log_dir=log_dir)
    history = model.fit(x_train, y_train, epochs=10, callbacks=[tensorboard_callback])
    ret = model.evaluate(x_test, y_test, verbose=2)

    score = str(mean_squared_error(model.predict(x_test), y_test))
    print("MSE score:   " + str(score))

    score = str(mean_absolute_error(model.predict(x_test), y_test))
    print("MAE score:   " + str(score))

    score = str(r2_score(model.predict(x_test), y_test))
    print("r2 score:   " + str(score))

    score_mae = mean_absolute_error(model.predict(x_test), y_test)
    print("scaled MAE")
    print(scale * score_mae)

    return model


def cnn_basic(x, y, scale):
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)

    try:
        x.shape
        x = x.tolist()
    except:
        pass

    try:
        x = tf.convert_to_tensor(x.tolist())
        y = tf.convert_to_tensor(y.tolist())
        input_dim = np.shape(x[0])

    except:
        input_dim = len(x[0])

    x = np.array(x)
    y = np.array(y)

    dim_persist = int(np.shape(x)[1] ** 0.5)
    x = x.reshape((np.shape(x)[0], dim_persist, dim_persist))
    x = np.expand_dims(x, -1)
    print(np.shape(x))

    samples = int(np.shape(x)[0])

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)
    print("Input vector size: " + str(input_dim))
    model = Sequential()

    model.add(Conv2D(filters=64, kernel_size=3, activation='relu', input_shape=(dim_persist, dim_persist, 1),
                     strides=1, data_format="channels_last"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Conv2D(filters=128, kernel_size=3, activation='relu',
                     strides=1, data_format="channels_last"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Conv2D(filters=256, kernel_size=3, activation='relu',
                     strides=1, data_format="channels_last"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Conv2D(filters=512, kernel_size=3, activation='relu',
                     strides=1, data_format="channels_last"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(4096, activation="relu"))
    model.add(Dropout(0.5))

    model.add(Dense(1))

    model.summary()
    # mae = tf.keras.losses.MAE()
    # rmse = tf.keras.losses.RMSE()
    log_dir = "./logs/training/"
    # tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
    # model.compile(optimizer='adam', loss=mse, metrics=[keras.metrics.mae])
    model.compile(optimizer='adam', loss="MSE", metrics=["MeanSquaredError", "MAE"])

    # tensorboard_cbk = TensorBoard(log_dir=log_dir)
    history = model.fit(x_train, y_train, epochs=10)
    ret = model.evaluate(x_test, y_test, verbose=2)

    score = str(mean_squared_error(model.predict(x_test), y_test))
    print("MSE score:   " + str(score))

    score = str(mean_absolute_error(model.predict(x_test), y_test))
    print("MAE score:   " + str(score))

    score = str(r2_score(model.predict(x_test), y_test))
    print("r2 score:   " + str(score))

    score_mae = mean_absolute_error(model.predict(x_test), y_test)
    print("scaled MAE")
    print(scale * score_mae)

    return model


def cnn_norm_basic(x, y, scale):
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)

    try:
        x.shape
        x = x.tolist()
    except:
        pass

    try:
        x = tf.convert_to_tensor(x.tolist())
        y = tf.convert_to_tensor(y.tolist())
        input_dim = np.shape(x[0])

    except:
        input_dim = len(x[0])

    x = np.array(x)
    y = np.array(y)

    dim_persist = int(np.shape(x)[1] ** 0.5)
    x = x.reshape((np.shape(x)[0], dim_persist, dim_persist))
    x = np.expand_dims(x, -1)
    print(np.shape(x))

    samples = int(np.shape(x)[0])

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)
    print("Input vector size: " + str(input_dim))
    model = Sequential()

    model.add(Conv2D(filters=64, kernel_size=3, input_shape=(dim_persist, dim_persist, 1),
                     strides=1, data_format="channels_last"))
    # model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Conv2D(filters=128, kernel_size=3,
                     strides=1, data_format="channels_last"))
    # model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Conv2D(filters=256, kernel_size=3,
                     strides=1, data_format="channels_last"))
    # model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Conv2D(filters=512, kernel_size=3,
                     strides=1, data_format="channels_last"))
    # model.add(BatchNormalization())
    model.add(local)
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size=2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(4096, activation="relu"))
    model.add(Dropout(0.5))

    model.add(Dense(1))

    model.summary()
    # mae = tf.keras.losses.MAE()
    # rmse = tf.keras.losses.RMSE()
    log_dir = "./logs/training/"
    model.compile(optimizer='adam', loss="MSE", metrics=["MeanSquaredError", "MAE"])

    history = model.fit(x_train, y_train, epochs=100)
    ret = model.evaluate(x_test, y_test, verbose=2)

    score = str(mean_squared_error(model.predict(x_test), y_test))
    print("MSE score:   " + str(score))

    score = str(mean_absolute_error(model.predict(x_test), y_test))
    print("MAE score:   " + str(score))

    score = str(r2_score(model.predict(x_test), y_test))
    print("r2 score:   " + str(score))

    score_mae = mean_absolute_error(model.predict(x_test), y_test)
    print("scaled MAE")
    print(scale * score_mae)

    return model