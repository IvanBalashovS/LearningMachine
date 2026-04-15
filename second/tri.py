import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
from sklearn.exceptions import ConvergenceWarning
from sklearn.utils._testing import ignore_warnings
from sklearn.model_selection import train_test_split


if __name__ == '__main__':
    df = pd.read_csv("hw2_strange_data.csv", sep=",")
    X = np.array(df[["x"]])
    Y = np.array(df[["y"]])

    X_learn, X_testing, Y_learn, Y_testing = train_test_split(X, Y,
    train_size=30,
)

    with ignore_warnings(category=ConvergenceWarning):
        lin = LinearRegression(fit_intercept=True)
        pol = PolynomialFeatures(11)
        pipe = make_pipeline = make_pipeline(pol, lin)

        pipe.fit(X_learn, Y_learn)

        print(str(mean_squared_error(Y_testing, pipe.predict(X_testing))))