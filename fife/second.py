from sklearn.linear_model import LinearRegression
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


iris_df = pd.read_csv("/home/ivanbalashov/LearningMachine/fife/Iris.csv", index_col="Id") 

X = iris_df[["SepalLengthCm", "SepalWidthCm"]].to_numpy()
encoder = LabelEncoder()
Y = encoder.fit_transform(iris_df["Species"])


model = KNeighborsClassifier(6)
model.fit(X, Y)


xmin, xmax = X[:, 0].min() - 1, X[:, 0].max() + 1
ymin, ymax = X[:, 1].min() - 1, X[:, 1].max() + 1

x_ = np.linspace(xmin, xmax, 1000)
y_ = np.linspace(ymin, ymax, 1000)

xx , yy = np.meshgrid(x_, y_)

xx_ = xx.reshape(-1, 1)
yy_ = yy.reshape(-1, 1)

points = np.hstack([xx_,yy_])

rez = model.predict(points)

plt.figure(figsize=(10, 8))
plt.contourf(xx, yy, rez.reshape(1000,1000), alpha=0.3)
plt.scatter(X[:, 0], X[:, 1], c=Y, edgecolor='black')
plt.savefig('KNN.png', dpi=300, bbox_inches='tight')
plt.close()
