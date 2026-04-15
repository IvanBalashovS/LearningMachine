
import matplotlib.pyplot as plt
import numpy as np
from typing import Literal

class Regressor:
    
    def __init__(self, lr=0.001, lr_decay=False, epochs=100, use_newton = False, regularization:Literal["None","L1","L2"]="None", alpha=0.1):
        self.lr = lr
        self.lr_decay = lr_decay
        self.epochs = epochs
        self.use_newton = use_newton
        self.regularization = regularization
        self.alpha = alpha
        self.w_list = []
        self.w = None
        if self.regularization == "L1" and self.use_newton:
            raise Exception("Метод ньютона не применим к L1 регуляризации.")
    
    def loss(self, x:np.ndarray, y:np.ndarray, w:np.ndarray):
        n = len(x)
        mse = x @ w - y
        ans = 1 / n  * np.sum(np.square(mse), axis=0)
        if self.regularization == "None":# отдельно компонента функции ошибки и регуляризации для удобной отрисовки
            return [ans, 0]
        elif self.regularization == "L2":
            print(len(ans), len(self.alpha * np.sum(w**2, axis=0)))
            return [ans + self.alpha * np.sum(w**2, axis=0),  self.alpha * np.sum(w**2, axis=0)]
        elif self.regularization == "L1":
            print(len(ans), len(self.alpha * np.sum(w**2, axis=0)))
            return [ans + self.alpha * np.sum(np.abs(w), axis=0), self.alpha * np.sum(np.abs(w), axis=0)]
            
    def grad(self, x:np.ndarray, y:np.ndarray, w:np.ndarray):
        if self.regularization == "None":
            return 2 / len(x) * x.T @ (x @ w - y)
        elif self.regularization == "L2":
            return 2 / len(x) * x.T @ (x @ w - y) + 2 * self.alpha * w
        elif self.regularization == "L1":
            return 2 / len(x) * x.T @ (x @ w - y) + self.alpha * np.sign(w)
        
    def hessian(self, x:np.ndarray, y:np.ndarray, w:np.ndarray):
        if self.regularization == "None":
            return 2 / len(x) * x.T @ x 
        elif self.regularization == "L2":
            return 2 / len(x) * x.T @ x + 2 * self.alpha * np.identity(x.shape[1])
    
    def init_w(self, n_dim):
        """ Функция начальной инициализации весов."""
        return np.random.normal(0, 1, (n_dim, 1))
    
    def fit(self, x, y):
        # инициализация весов
        w = self.init_w(x.shape[1])
        w_list = [w]
        # Цикл обучения
        for i in range(0, self.epochs):
            # Вычисление градиента
            grad = self.grad(x, y, w)
            # Измените параметры модели
            if self.use_newton:
                # Вычисление Гессиана
                H = self.hessian(x, y, w)
                w = w - np.linalg.inv(H) @ grad
            else:
                w = w - self.lr * grad
            # Сохраняем веса в список
            w_list.append(w.copy())
            if self.lr_decay:
                self.lr *=0.95
        self.w_list = np.array(w_list)
        self.w = w
            
    def predict(self, x):
        return x @ self.w
    
    def show_training(self, w_true, x, y):
        if self.w.shape[0] !=2:
            raise Exception("Веса должны быть размерности 2.")
        radius = 2
    
        A, B = np.meshgrid(np.linspace(w_true[0] - radius, w_true[0] + radius, 200),
                        np.linspace(w_true[1] - radius, w_true[1] + radius, 200))

        W = np.vstack([A.ravel(), B.ravel()])
        
        loss, reg = self.loss(x, y, W)
        levels_loss = loss.reshape(A.shape)
        levels_reg = reg.reshape(A.shape)
        
        plt.figure(figsize=(13, 9))
        plt.title('GD trajectory')
        plt.xlabel('$w_1$')
        plt.ylabel('$w_2$')
        wmin, wmax = self.w_list[:, 0].min(),self.w_list[:, 0].max()
        centr_x = (wmin + wmax) / 2
        width_x = np.abs(wmin - wmax)
        wmin, wmax = self.w_list[:, 1].min(),self.w_list[:, 1].max()
        centr_y = (wmin + wmax) / 2
        width_y = np.abs(wmin - wmax)
        width = np.max([width_x, width_y]) / 2 * 1.1
        plt.xlim(centr_x - width, centr_x + width)
        plt.ylim(centr_y - width, centr_y + width)
        # plt.gca().set_aspect('equal')

        # visualize the level set
        CS = plt.contour(A, B, levels_loss, levels=np.logspace(0, 2, num=50), cmap=plt.cm.rainbow_r)
        CB = plt.colorbar(CS, shrink=0.8, extend='both')
        CS = plt.contour(A, B, levels_reg, levels=np.linspace(0, 5*self.alpha, num=50), cmap=plt.cm.brg)

        # visualize trajectory
        plt.scatter(self.w_list[:, 0], self.w_list[:, 1], color="black")
        plt.plot(self.w_list[:, 0], self.w_list[:, 1], color="black")

        plt.show()