from sklearn.svm import SVC, SVR
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import colors
import pandas as pd
import seaborn as sns
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn_rvm import EMRVR, EMRVC
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

n_samples = 300
X = np.random.uniform(0, 10 * np.pi, n_samples).reshape(-1, 1)
Y = np.sin(X.flatten()) + 4 * np.sin(2.5 * X.flatten()) + np.random.normal(0, 1, size=n_samples)

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3)

model_EMRVR = EMRVR(verbose=False, kernel="rbf")
model_EMRVR.fit(X_train, Y_train)
y_pred_rvm = model_EMRVR.predict(X_test)


model_SVR = SVR()
cv_SVR = GridSearchCV(model_SVR, param_grid={
    "kernel": ["rbf"],
    "C": [0.1, 1, 10, 50, 100, 1e3, 1e4],
    'gamma': [0.01, 0.1, 0.5, 1]
}, cv=5, scoring="neg_mean_squared_error")  

cv_SVR.fit(X_train, Y_train)
y_pred_svr = cv_SVR.predict(X_test)
print(cv_SVR.best_params_)

print(f"RVM: {len(model_EMRVR.relevance_):3d} | "
      f"MSE: {mean_squared_error(Y_test, y_pred_rvm):.4f} | "
      f"R^2: {r2_score(Y_test, y_pred_rvm):.4f}")
print(f"SVR:    {len(cv_SVR.best_estimator_.support_):3d} | "
      f"  Лучшие параметры: {cv_SVR.best_params_} | "
      f"MSE: {mean_squared_error(Y_test, y_pred_svr):.4f} | "
      f"R^2: {r2_score(Y_test, y_pred_svr):.4f}")

X_dense = np.linspace(X.min(), X.max(), 400).reshape(-1, 1)
y_pred_rvm_dense = model_EMRVR.predict(X_dense)
y_pred_svr_dense = cv_SVR.predict(X_dense)

plt.figure(figsize=(10, 6))
plt.scatter(X_train, Y_train, label='Train', color='gray', alpha=0.5, s=30)
plt.scatter(X_test, Y_test, label='Test', color='black', alpha=0.7, s=40)
plt.plot(X_dense, y_pred_rvm_dense, label='RVM', color='blue', linewidth=2.5)
plt.plot(X_dense, y_pred_svr_dense, label='SVR', color='red', linewidth=2.5, linestyle='--')
plt.xlabel('X')
plt.ylabel('y')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('homework_nine_2.png', dpi=300, bbox_inches='tight')
plt.close()