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

iris_df = pd.read_csv("/home/ivanbalashov/LearningMachine/eight/Iris.csv", index_col="Id") 
X = iris_df[["SepalLengthCm", "SepalWidthCm"]].to_numpy()
encoder = LabelEncoder()
Y = encoder.fit_transform(iris_df["Species"])
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=5, test_size=0.3,
                                                    stratify=Y)

model = SVC()
cv = GridSearchCV(model, param_grid={
    "kernel": ["linear", "poly", "rbf"],
    "C": [0.1, 1,10, 100, 1e3, 1e4]
}, cv=5, scoring="accuracy")  

cv.fit(X_train, Y_train)

best_model = cv.best_estimator_
print(f"{cv.best_params_}")

xmin, xmax = X[:, 0].min() - 1, X[:, 0].max() + 1
ymin, ymax = X[:, 1].min() - 1, X[:, 1].max() + 1

x_ = np.linspace(xmin, xmax, 100)
y_ = np.linspace(ymin, ymax, 100)

xx , yy = np.meshgrid(x_, y_)

xx_ = xx.reshape(-1, 1)
yy_ = yy.reshape(-1, 1)

points = np.hstack([xx_,yy_])

rez = cv.predict(points)

print(f"Лучшие параметры: {cv.best_params_}")
print(f"Лучшая точность (CV): {cv.best_score_:.4f}")
print(f"Точность на тестовой выборке: {accuracy_score(Y_test, best_model.predict(X_test)):.4f}")

plt.figure(figsize=(10, 8))
plt.contourf(xx, yy, rez.reshape(100,100), alpha=0.3)
plt.scatter(X[:, 0], X[:, 1], c=Y, edgecolor='black')
plt.savefig('homework_eight.png', dpi=300, bbox_inches='tight')
plt.close()