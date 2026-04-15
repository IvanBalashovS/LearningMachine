import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def firstTask(array):
    indexes = np.where(array == 0)
    if(array[np.size(array) - 1] == 0):
        indexes = np.delete(indexes, np.size(indexes) - 1)
    return np.max(array[indexes + 1])

def secondTask(matrix, value):
    index = np.argmin((np.abs(np.asarray(matrix).reshape(-1) - value)))
    return np.asarray(matrix).reshape(-1)[index]


#Третье задание

def fun(x):
    # код этой функции изменять нельзя
    return np.sum(x, axis=1) + np.trace(x @ x.T)

def threeTask(data):
    f = np.vectorize(fun, signature='(m,k)->(m)')
    return f(data)

data = np.random.normal(0, 5, size=(10,20,5))

# fun(data) не работает

#Четвертое задание

def four(matrix):
    g = np.sum(matrix**2, axis = 1)[:, np.newaxis] #gg - qq + 2 * dot
    dot = np.dot(matrix, matrix.T)
    dis2 = g + g.T - 2 * dot
    return np.sqrt(dis2)

if __name__ == '__main__':
    df = pd.read_csv("titanic.csv", sep="\t")
    print (np.sum(df["Survived"]))
    print (np.min(df["Age"]))
    print (np.max(df["Age"]))
    print (np.mean(df["Age"]))
    a = np.unique(df["Pclass"])
    for i in a:
        print(str(i) + ": " + str(np.size(np.where(df["Pclass"] == i))))
    print(np.size(np.where(df["Sex"] == "male")) / np.size(np.where(df["Sex"] == "female")))

    for i in a:
        mask = np.where(df["Pclass"] == i)[0]
        ages = df.iloc[mask]["Age"] 
        print(str(i) + ": " + str(np.mean(ages)))
    
    print(firstTask(np.array([0,1,0,2,0,3,0])))

    matrix = np.array([[1, 2, 3], [4, 5, 6]])
    print(secondTask(matrix, 3.5))

    print(print(threeTask(data)))

    X = np.array([
        [0,0,0],
        [1,0,0],
        [0,1,0],
        [0,0,1],
        [1,1,1]
    ])
    print(four(X))
