import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Lasso, Ridge, RANSACRegressor, TheilSenRegressor
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
import pandas as pd
from sklearn.metrics import mean_squared_error

class GaussianFeatures(BaseEstimator, TransformerMixin):
    def __init__(self, N, width_factor=.5):
        self.N = N
        self.width_factor = width_factor
    
    @staticmethod
    def _gauss_basis(x, center, width, axis=None):
        arg = (x - center) / width
        return np.exp(-0.5 * np.sum(arg ** 2, axis))
        
    def fit(self, X, y=None):
        self.centers_ = np.linspace(X.min(), X.max(), self.N)
        self.width_ = self.width_factor * (self.centers_[1] - self.centers_[0])
        return self
        
    def transform(self, X):
        return self._gauss_basis(X[:, :, None], self.centers_, self.width_, axis=1)
    
def generate_samples(function, n_samples, x_min=0, x_max=10, sigma=1):
    x = np.random.uniform(x_min, x_max, n_samples)
    y = function(x) + np.random.normal(0, sigma, n_samples)
    return x, y

relation = lambda x: np.abs(2 + x + 2 * np.sin(x) - 30)
num_samples  = 220
sigma = 1
x_min, x_max = 0, 60
x, center = generate_samples(relation, num_samples, x_min, x_max, sigma)

gf = GaussianFeatures(30, 0.65)
lr = LinearRegression()
model = make_pipeline(gf, lr)

model.fit(x[:,None], center)

t = np.linspace(x_min, x_max, 101)
predict = model.predict(t[:,None])

plt.scatter(x, center)
plt.plot(t, relation(t))
plt.plot(t, predict)
print(mean_squared_error(relation(t), predict))
plt.plot(t, lr.intercept_ + gf.transform(t[:,None]) * lr.coef_, color="gray")
plt.axhline(lr.intercept_, color = "green", label="bias")
plt.savefig('number_1', dpi=300, bbox_inches='tight')
plt.show()