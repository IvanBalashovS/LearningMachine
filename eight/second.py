import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.multiclass import unique_labels
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
import numpy as np
from sklearn.datasets import make_classification
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.model_selection import GridSearchCV

class SVC_OVR(ClassifierMixin, BaseEstimator):
    def __init__(self, **svc_params):
        self.svc_params = svc_params
        self.classifiers = {}
        self.classes = None
    
    
    def fit(self, X, Y):
        self.classes = unique_labels(Y)
        self.classifiers = {}
        for model in self.classes:
            y = np.where(Y == model, 1, -1)
            svc = SVC(**self.svc_params)
            svc.fit(X, y)
            self.classifiers[model] = svc
        return self
    
    def predict(self, X):
        pred = np.array([model.decision_function(X) for model in self.classifiers.values()])
        return self.classes[np.argmax(pred, axis=0)]
    
iris_df = pd.read_csv("/home/ivanbalashov/LearningMachine/eight/Iris.csv", index_col="Id") 
X = iris_df[["SepalLengthCm", "SepalWidthCm"]].to_numpy()
encoder = LabelEncoder()
Y = encoder.fit_transform(iris_df["Species"])
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=5, test_size=0.3,
                                                    stratify=Y)
model = SVC_OVR(kernel='poly', degree=2, C=1.0, coef0=1.0)
model.fit(X_train, Y_train)


xmin, xmax = X[:, 0].min() - 1, X[:, 0].max() + 1
ymin, ymax = X[:, 1].min() - 1, X[:, 1].max() + 1

x_ = np.linspace(xmin, xmax, 100)
y_ = np.linspace(ymin, ymax, 100)

xx , yy = np.meshgrid(x_, y_)

xx_ = xx.reshape(-1, 1)
yy_ = yy.reshape(-1, 1)

points = np.hstack([xx_,yy_])

rez = model.predict(points)

print(f"Точность на тестовой выборке: {accuracy_score(Y_test, model.predict(X_test)):.4f}")

plt.figure(figsize=(10, 8))
plt.contourf(xx, yy, rez.reshape(100,100), alpha=0.3)
plt.scatter(X[:, 0], X[:, 1], c=Y, edgecolor='black')
plt.savefig('123.png', dpi=300, bbox_inches='tight')
plt.close()