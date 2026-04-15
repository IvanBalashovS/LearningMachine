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
    df = pd.read_csv("./second/hw2_polynomial_data.csv", sep=",")
    print(df.columns.tolist())
    X = np.array(df[["x0", "x1", "x2"]])
    Y = np.array(df[["y"]])

 #   X_learn = X[0:100]
  #  X_testing = X[100:500]

   # Y_learn = Y[0:100]
   # Y_testing = Y[100:500]

    X_learn, X_testing, Y_learn, Y_testing = train_test_split(X, Y,
    train_size=400,)

    with ignore_warnings(category=ConvergenceWarning):
        for i in range(4, 7):
            print(f"Степень {i}")
            alphas = np.linspace(0.001, 5, 10)
            for alpha in alphas: 
                print(f"alpha :{alpha}")
                pol = PolynomialFeatures(i)
                lasso_regr = Lasso(fit_intercept=True, alpha=alpha)
                pipelineLas = make_pipeline(pol, lasso_regr)
                pipelineLas.fit(X_learn, Y_learn)
                las_model = pipelineLas.named_steps['lasso']
                coefficients = las_model .coef_.flatten()
                poly_features = pipelineLas.named_steps['polynomialfeatures']
                feature_names = poly_features.get_feature_names_out(['x0', 'x1', 'x2'])
                best_coef = 1e-10
                print("коэфициенты:")
                for name, coef in zip(feature_names, coefficients):
                    if(coef > best_coef):
                        print(f"{name:20s}: {coef:10.4f}")

                best_coef = 1e-10
                important_indices = []
                for j in range(len(coefficients)):
                    if np.abs(coefficients[j]) > best_coef:
                        important_indices.append(j)

                if len(important_indices) > 0:

                    lin_reg = LinearRegression(fit_intercept=True)
                    x_learn = pol.fit_transform(X_learn)
                    x_test = pol.transform(X_testing)

                    x_learn_imp = x_learn[:, important_indices]
                    x_test_imp = x_test[:, important_indices]

                    lin_reg.fit(x_learn_imp, Y_learn)

                    y_pred_final = lin_reg.predict(x_test_imp)
                    mse_final = mean_squared_error(Y_testing, y_pred_final)
                    
                    print(f"  Важных признаков: {len(important_indices)}")
                    print(f"  Среднеквадротичная ошибка после обучения на Линейной регрессии: {mse_final}")
                    