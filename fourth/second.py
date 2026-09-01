import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Lasso, Ridge, RANSACRegressor, TheilSenRegressor
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
import pandas as pd
from sklearn.metrics import mean_squared_error

b = 1.5
x_min, x_max = -5, 30
x = np.random.uniform(x_min, x_max, 30)
center = x * b + np.random.normal(0, 1, 30)
x = np.append(x, [-5, 0, 5, 10, 15, 20, 25, 30, 31])
center = np.append(center, [-12, -20, -30, -20, -30, -35, 20, -1, 30])
scaler = StandardScaler()



modelLinRegr = LinearRegression()
modelLinRegr.fit(x[:,None], center)

modelRANSAC = RANSACRegressor()
modelRANSAC.fit(x[:, None], center)

modelTheilSen = TheilSenRegressor()
modelTheilSen.fit(x[:, None], center)

t = np.linspace(x_min, x_max, 200)

predictLinRegr = modelLinRegr.predict(t[:,None])
predictRANSAC = modelRANSAC.predict(t[:,None])
predictTheilSen = modelTheilSen.predict(t[:,None])

plt.scatter(x, center)
plt.plot(t, t * b, label="Исходная функция")
plt.plot(t, predictLinRegr, label="Линейная регрессия")
plt.plot(t, predictRANSAC, label="RANSAC регрессия")
plt.plot(t, predictTheilSen, label="RANSAC регрессия")
plt.legend()
plt.savefig("number_2.png", dpi=300, bbox_inches='tight')

print("Ошибка линейной регрессии")
print(mean_squared_error(t * b, predictLinRegr))
print(modelLinRegr.score(t[:,None], t * b))

print("Ошибка RANSAC регрессии")
print(mean_squared_error(t * b, predictRANSAC))
print(modelRANSAC.score(t[:,None], t * b))

print("Ошибка TheilSen регрессии")
print(mean_squared_error(t * b, predictTheilSen))
print(modelTheilSen.score(t[:,None], t * b))
