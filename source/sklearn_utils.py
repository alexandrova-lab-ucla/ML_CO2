import time

import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import SGDRegressor, BayesianRidge
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


def grid(x, y, method="sgd"):
    if (method == "nn"):
        print(".........neural network grid optimization selected.........")
        params = {"alpha": [1e-10, 1e-7, 1e-4, 1e-1],
                  "activation": ["relu"],
                  "solver": ["adam"],
                  "learning_rate": ["adaptive"],
                  "max_iter": [100, 10000, 1000000],
                  "tol": [1e-11, 1e-7, 1e-5, 1e-3, 1e-1, 1],
                  "learning_rate_init": [0.00001, 0.0001, 0.001, 0.01],
                  "shuffle": [True]
                  }
        reg = MLPRegressor(hidden_layer_sizes=(100, 1000, 100,))
    elif (method == "rf"):
        print(".........random forest grid optimization selected.........")

        params = {"max_depth": [10, 20, 30, 40],
                  "min_samples_split": [2, 4, 6],
                  "n_jobs": [1],
                  "n_estimators": [500, 1000, 2000, 5000]
                  }
        reg = RandomForestRegressor()

    elif (method == "grad"):
        print(".........gradient boost grid optimization selected.........")

        params = {"loss": ["ls"],
                  "n_estimators": [500, 1000, 2000, 4000],
                  "learning_rate": [i * 0.03 for i in range(10)],
                  "subsample": [(i * 0.06) for i in range(1, 10)],
                  "criterion": ["mse"],
                  "max_depth": [i * 10 for i in range(1, 3)],
                  "tol": [0.0001, 0.000001]
                  }
        grad = GradientBoostingRegressor()

    elif (method == "svr_rbf"):
        print(".........svr grid optimization selected.........")

        params = {"kernel": ["rbf"],
                  "C": [10, 1, 0.1, 0.01, 0.001, 0.0001],
                  "gamma": [0.1, 0.0001, 0.00001],
                  "epsilon": [0.01, 0.1, 1, 5, 10, 20],
                  "cache_size": [500, 1000, 2000, 4000, 8000]
                  }

        reg = SVR()

    elif (method == "svr_poly"):
        print(".........svr grid optimization selected.........")

        params = {"kernel": ["poly"],
                  "C": [1, 0.1, 0.01, 0.001, 0.0001],
                  "gamma": [0.1, 0.0001, 0.00001],
                  "epsilon": [0.01, 0.1, 1, 5, 10, 20],
                  "degree": [5, 7, 9, 20],
                  "coef0": [0.2, 0.4, 0.5, 0.6, 0.8],
                  "cache_size": [500, 1000, 2000, 4000, 8000]
                  }

        reg = SVR()
    elif (method == "svr_lin"):
        print(".........svr grid optimization selected.........")

        params = {"kernel": ["linear"],
                  "C": [10, 1, 0.1, 0.01, 0.001, 0.0001],
                  "gamma": [0.1, 0.0001, 0.00001],
                  "cache_size": [500, 1000, 2000, 4000, 8000]
                  }

        reg = SVR()

    elif (method == "bayes"):
        print(".........bayes grid optimization selected.........")

        params = {
            "n_iter": [1000, 2000, 5000, 10000],
            "tol": [1e-3, 1e-5, 1e-7, 1e-9],
            "alpha_1": [1e-01, 1e-03, 1e-05, 1e-07],
            "alpha_2": [1e-01, 1e-03, 1e-05, 1e-07],
            "lambda_1": [1e-01, 1e-03, 1e-05, 1e-07],
            "lambda_2": [1e-01, 1e-03, 1e-05, 1e-07]
        }

        reg = BayesianRidge()


    elif (method == "kernel"):
        print(".........kernel grid optimization selected.........")

        params = {"kernel": ["rbf"],
                  "alpha": [1e-6, 1e-4, 1e-2, 1, 2],
                  "gamma": [1e-8, 1e-6, 1e-4, 1e-2, 1]
                  }

        reg = KernelRidge()

    elif (method == "gaussian"):
        print(".........gaussian grid optimization selected.........")

        params = {"alpha": [1e-10, 1e-7, 1e-4, 1e-1]
                  }

        kernel = DotProduct() + WhiteKernel()
        reg = GaussianProcessRegressor(kernel=kernel)


    else:

        params = {"loss": ['squared_loss', "huber"],
                  "tol": [0.01, 0.001, 0.0001s],
                  "shuffle": [True],
                  "penalty": ["l1"],
                  "l1_ratio": [0.15, 0.20, 0.25],
                  "epsilon": [0.01, 0.1, 1],
                  "eta0": [10 ** (-2 * i) for i in range(1, 5)],
                  }
        reg = SGDRegressor()

    if (method == "xgboost"):
        print(".........xgboost grid optimization selected.........")

        from xgboost_util import xgboost_grid

        xgboost_grid(x, y)

    else:
        print(".........sgd grid optimization selected.........")

        try:
            x = preprocessing.scale(np.array(x))
            scaler = preprocessing.StandardScaler().fit(x)
        except:
            x = list(x)
            x = preprocessing.scale(np.array(x))
            scaler = preprocessing.StandardScaler().fit(x)

        if (method == "xg"):
            xgboost_grid(x, y)

        reg = GridSearchCV(reg, params, verbose=3, cv=3)
        x = scaler.transform(x)
        reg.fit(list(x), y)
        print(reg.best_params_)
        print(reg.best_score_)
        return reg

def sgd (x,y):

    params = {"loss": 'squared_loss',
              "max_iter": 10 ** 7,
              "tol": 0.0000001,
              "penalty": "l2", "l1_ratio": 0.15,
              "epsilon": 0.01,
              "learning_rate": 'invscaling'
              }

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    reg = SGDRegressor(**params)

    est = make_pipeline(StandardScaler(), reg)
    t1 = time.time()
    est.fit(list(x_train), y_train)
    t2 = time.time()
    time_el = t2 - t1

    score = str(est.score(list(x_test), y_test))
    print("stochastic gradient descent score:   " + str(score) + " time: " + str(time_el))

def gradient_boost_reg(x, y):

    params = {"loss":"ls",
                "n_estimators": 2000,
              "learning_rate": 0.1,
              "subsample":0.8,
              "criterion":"mse",
              "max_depth": 10,
              "tol":0.0001
              }

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    reg = GradientBoostingRegressor(**params)

    est = make_pipeline(StandardScaler(), reg)
    t1 = time.time()
    est.fit(list(x_train), y_train)
    t2 = time.time()
    time_el = t2 - t1
    score = est.score(list(x_test), y_test)
    print("gradient boost score:                " + str(score) + " time: " + str(time_el))


def random_forest(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    params = {"max_depth": 30,
              "min_samples_split": 3,
              "n_estimators": 5000,
              "n_jobs": 16, "verbose": False
              }

    reg = RandomForestRegressor(**params)

    est = make_pipeline(StandardScaler(), reg)
    t1 = time.time()
    est.fit(list(x_train), y_train)
    t2 = time.time()
    time_el = t2 - t1
    score = est.score(list(x_test), y_test)
    print("random forest score:                 " + str(score) + " time: " + str(time_el))

def gaussian(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    kernel = DotProduct() + WhiteKernel()
    reg = GaussianProcessRegressor(kernel=kernel, alpha=1e-10, random_state=0)
    est = make_pipeline(StandardScaler(), reg)
    t1 = time.time()
    est.fit(list(x_train), y_train)
    t2 = time.time()
    time_el = t2 - t1
    score = est.score(list(x_test), y_test)
    print("gaussian process score:              " + str(score) + " time: " + str(time_el))

def kernel(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    # reg = KernelRidge(alpha=0.0001, degree = 10,kernel = "polynomial")
    reg = KernelRidge(kernel='rbf', alpha=0.00005, gamma=0.0001)

    est = make_pipeline(StandardScaler(), reg)
    t1 = time.time()
    est.fit(list(x_train), y_train)
    t2 = time.time()
    time_el = t2 - t1
    score = est.score(list(x_test), y_test)
    print("kernel regression score:             " + str(score) + " time: " + str(time_el))

def bayesian(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    reg = BayesianRidge(n_iter=10000, tol=1e-7, copy_X=True, alpha_1=1e-03, alpha_2=1e-03,
                        lambda_1=1e-03, lambda_2=1e-03)
    est = make_pipeline(StandardScaler(), reg)
    t1 = time.time()
    est.fit(list(x_train), y_train)
    t2 = time.time()
    time_el = t2 - t1
    score = est.score(list(x_test), y_test)
    print("bayesian score:                      " + str(score) + " time: " + str(time_el))

def svr(x, y):
    # change C
    # scale data
    # L1/L2 normalization

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    svr_rbf = SVR(kernel='rbf', C=0.001, gamma=0.1, epsilon=.1, cache_size=4000)
    est_rbf = make_pipeline(StandardScaler(), svr_rbf)
    svr_lin = SVR(kernel='linear', C=0.1, gamma='auto', cache_size=4000)
    est_lin = make_pipeline(StandardScaler(), svr_lin)
    svr_poly = SVR(kernel='poly', C=100, gamma='auto', degree=6, epsilon=.1, coef0=0.5, cache_size=4000)
    est_poly = make_pipeline(StandardScaler(), svr_poly)

    t1 = time.time()
    est_rbf.fit(list(x_train), y_train)
    t2 = time.time()
    time_rbf = t2 - t1
    s1 = svr_rbf.score(list(x_test), y_test)

    t1 = time.time()
    est_lin.fit(list(x_train), y_train)
    t2 = time.time()
    time_svr= t2 - t1
    s2 = svr_lin.score(list(x_test), y_test)

    t1 = time.time()
    est_poly.fit(list(x_train), y_train)
    t2 = time.time()
    time_poly = t2 - t1
    score = svr_poly.score(list(x_test), y_test)

    print("linear svr score:                    " + str(s2) + " time: " + str(time_rbf))
    print("radial basis svr score:              " + str(s1) + " time: " + str(time_svr))
    print("polynomial svr score:                " + str(score) + " time: " + str(time_poly))

def sk_nn(x, y):

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    reg = MLPRegressor(random_state=1, max_iter=100000, learning_rate_init=0.00001, learning_rate="adaptive",
                       early_stopping=True, tol=1e-7, shuffle=True, solver="adam", activation="relu",
                       hidden_layer_sizes=(1000,), verbose=False, alpha=0.00001)

    est = make_pipeline(StandardScaler(), reg, verbose=True)
    t1 = time.time()
    est.fit(list(x_train), y_train)
    t2 = time.time()
    time_el = t2 - t1
    score = est.score(list(x_test), y_test)
    print("Neural Network score:                " + str(score) + " time: " + str(time_el))
