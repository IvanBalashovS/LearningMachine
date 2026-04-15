import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
import os

# Разделим данные на обучающую и тестовую выборки
# Для временных рядов важно сохранить порядок
split_idx = int(len(x) * 0.8)
x_train, x_test = x[:split_idx], x[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

print(f"Обучающая выборка: {len(x_train)} точек")
print(f"Тестовая выборка: {len(x_test)} точек")
print(f"Диапазон предсказания: [{min(x_test):.2f}, {max(x_test):.2f}]")

# Функция для создания признаков на основе ряда Фурье
class FourierFeatures:
    def __init__(self, n_harmonics=3, include_poly=False, poly_degree=2):
        self.n_harmonics = n_harmonics
        self.include_poly = include_poly
        self.poly_degree = poly_degree
    
    def transform(self, x):
        x = np.array(x).reshape(-1, 1)
        features = []
        
        # Полиномиальные признаки (опционально)
        if self.include_poly:
            for d in range(1, self.poly_degree + 1):
                features.append(x ** d)
        
        # Масштабируем x для лучшей работы тригонометрических функций
        x_scaled = x / max(x) * 2 * np.pi
        
        # Признаки Фурье
        for k in range(1, self.n_harmonics + 1):
            features.append(np.sin(k * x_scaled))
            features.append(np.cos(k * x_scaled))
        
        return np.hstack(features) if features else x

# Создадим и обучим несколько моделей
degrees = [3, 5, 7, 9]
n_harmonics_list = [2, 3, 4, 5]

models = {}
results = {}

# 1. Полиномиальная регрессия
for degree in degrees:
    model = make_pipeline(
        PolynomialFeatures(degree, include_bias=False),
        LinearRegression()
    )
    model.fit(x_train.reshape(-1, 1), y_train)
    models[f'Poly_{degree}'] = model
    
    y_pred = model.predict(x_test.reshape(-1, 1))
    mse = mean_squared_error(y_test, y_pred)
    results[f'Poly_{degree}'] = {'model': model, 'mse': mse, 'y_pred': y_pred}

# 2. Регрессия на основе ряда Фурье
for n_harm in n_harmonics_list:
    # Чистый ряд Фурье
    fourier_model = LinearRegression()
    X_train_fourier = FourierFeatures(n_harmonics=n_harm, include_poly=False).transform(x_train)
    fourier_model.fit(X_train_fourier, y_train)
    models[f'Fourier_{n_harm}'] = fourier_model
    
    X_test_fourier = FourierFeatures(n_harmonics=n_harm, include_poly=False).transform(x_test)
    y_pred = fourier_model.predict(X_test_fourier)
    mse = mean_squared_error(y_test, y_pred)
    results[f'Fourier_{n_harm}'] = {'model': fourier_model, 'mse': mse, 'y_pred': y_pred}
    
    # Комбинация полиномов и Фурье
    fourier_poly_model = LinearRegression()
    X_train_fp = FourierFeatures(n_harmonics=n_harm, include_poly=True, poly_degree=2).transform(x_train)
    fourier_poly_model.fit(X_train_fp, y_train)
    models[f'FourierPoly_{n_harm}'] = fourier_poly_model
    
    X_test_fp = FourierFeatures(n_harmonics=n_harm, include_poly=True, poly_degree=2).transform(x_test)
    y_pred = fourier_poly_model.predict(X_test_fp)
    mse = mean_squared_error(y_test, y_pred)
    results[f'FourierPoly_{n_harm}'] = {'model': fourier_poly_model, 'mse': mse, 'y_pred': y_pred}

# 3. Регрессия с регуляризацией (Ridge) для полиномов
alphas = [0.001, 0.01, 0.1, 1, 10]
for degree in [7, 9]:
    for alpha in alphas:
        model = make_pipeline(
            PolynomialFeatures(degree, include_bias=False),
            Ridge(alpha=alpha)
        )
        model.fit(x_train.reshape(-1, 1), y_train)
        models[f'RidgePoly_{degree}_a{alpha}'] = model
        
        y_pred = model.predict(x_test.reshape(-1, 1))
        mse = mean_squared_error(y_test, y_pred)
        results[f'RidgePoly_{degree}_a{alpha}'] = {'model': model, 'mse': mse, 'y_pred': y_pred}

# Найдем лучшую модель по MSE
best_model_name = min(results, key=lambda name: results[name]['mse'])
best_model = results[best_model_name]['model']
best_mse = results[best_model_name]['mse']

print(f"\nЛучшая модель: {best_model_name}")
print(f"MSE на тесте: {best_mse:.4f}")

print("\nТоп-5 моделей по MSE:")
sorted_results = sorted(results.items(), key=lambda x: x[1]['mse'])
for name, res in sorted_results[:5]:
    print(f"{name}: MSE = {res['mse']:.4f}")

# Предсказание будущих значений
x_future = np.linspace(max(x) + 0.1, max(x) + 2, 50)

plt.figure(figsize=(15, 10))

# График 1: Сравнение моделей на тестовых данных
plt.subplot(2, 2, 1)
plt.scatter(x_train, y_train, alpha=0.6, label='Обучающие данные', c='blue', edgecolors='black')
plt.scatter(x_test, y_test, alpha=0.8, label='Тестовые данные', c='green', edgecolors='black', s=80)

# Покажем предсказания лучших моделей
colors = ['red', 'purple', 'orange', 'brown']
for i, (name, res) in enumerate(sorted_results[:4]):
    plt.plot(x_test, res['y_pred'], 'o-', label=f'{name} (MSE={res["mse"]:.3f})', 
             color=colors[i], alpha=0.7, markersize=6)

plt.xlabel('x')
plt.ylabel('y')
plt.title('Сравнение моделей на тестовых данных')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)

# График 2: Предсказание будущих значений лучшей моделью
plt.subplot(2, 2, 2)
plt.scatter(x, y, alpha=0.7, label='Все исходные данные', c='blue', edgecolors='black')

# Для лучшей модели готовим признаки для будущих точек
if 'Fourier' in best_model_name:
    n_harm = int(best_model_name.split('_')[1].split('a')[0])
    include_poly = 'Poly' in best_model_name
    X_future = FourierFeatures(n_harmonics=n_harm, include_poly=include_poly, poly_degree=2).transform(x_future)
else:
    # Для полиномиальных моделей
    degree = int(best_model_name.split('_')[1].split('a')[0]) if 'Ridge' in best_model_name else int(best_model_name.split('_')[1])
    poly = PolynomialFeatures(degree, include_bias=False)
    X_future = poly.fit_transform(x_future.reshape(-1, 1))

y_future = best_model.predict(X_future)

plt.plot(x_future, y_future, 'r-', linewidth=2, label=f'Предсказание ({best_model_name})')
plt.axvline(x=max(x), color='gray', linestyle='--', alpha=0.7, label='Граница известных данных')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Предсказание будущих значений')
plt.legend()
plt.grid(True, alpha=0.3)

# График 3: Визуализация MSE для всех моделей
plt.subplot(2, 2, 3)
model_names = list(results.keys())
mse_values = [results[name]['mse'] for name in model_names]
bars = plt.bar(range(len(model_names)), mse_values)
plt.xticks(range(len(model_names)), model_names, rotation=90, fontsize=8)
plt.ylabel('MSE')
plt.title('Сравнение MSE моделей')
plt.yscale('log')
plt.grid(True, alpha=0.3, axis='y')

# График 4: Ансамблевое предсказание
plt.subplot(2, 2, 4)
plt.scatter(x, y, alpha=0.7, label='Исходные данные', c='blue', edgecolors='black')

# Усредненное предсказание нескольких лучших моделей
ensemble_predictions = []
for name, res in sorted_results[:3]:
    if 'Fourier' in name:
        n_harm = int(name.split('_')[1].split('a')[0]) if 'a' in name else int(name.split('_')[1])
        include_poly = 'Poly' in name
        X_future_ens = FourierFeatures(n_harmonics=n_harm, include_poly=include_poly, poly_degree=2).transform(x_future)
    else:
        degree = int(name.split('_')[1].split('a')[0]) if 'Ridge' in name else int(name.split('_')[1])
        poly = PolynomialFeatures(degree, include_bias=False)
        X_future_ens = poly.fit_transform(x_future.reshape(-1, 1))
    
    ensemble_predictions.append(res['model'].predict(X_future_ens))

y_ensemble = np.mean(ensemble_predictions, axis=0)
y_ensemble_std = np.std(ensemble_predictions, axis=0)

plt.plot(x_future, y_ensemble, 'r-', linewidth=2, label='Ансамбль (среднее)')
plt.fill_between(x_future, y_ensemble - y_ensemble_std, y_ensemble + y_ensemble_std, 
                 alpha=0.2, color='red', label='±1 стандартное отклонение')
plt.axvline(x=max(x), color='gray', linestyle='--', alpha=0.7)
plt.xlabel('x')
plt.ylabel('y')
plt.title('Ансамблевое предсказание (3 лучшие модели)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('future_predictions.png', dpi=150, bbox_inches='tight')
plt.show()

# Вывод коэффициентов лучшей модели
print(f"\nКоэффициенты лучшей модели ({best_model_name}):")
if hasattr(best_model, 'coef_'):
    print(f"Коэффициенты: {best_model.coef_}")
    if hasattr(best_model, 'intercept_'):
        print(f"Свободный член: {best_model.intercept_:.4f}")

# Финальное предсказание для будущего момента времени
future_point = max(x) + 1.5  # Пример будущего момента
print(f"\nПредсказание для x = {future_point:.2f}:")

if 'Fourier' in best_model_name:
    n_harm = int(best_model_name.split('_')[1].split('a')[0])
    include_poly = 'Poly' in best_model_name
    X_future_point = FourierFeatures(n_harmonics=n_harm, include_poly=include_poly, poly_degree=2).transform([future_point])
else:
    degree = int(best_model_name.split('_')[1].split('a')[0]) if 'Ridge' in best_model_name else int(best_model_name.split('_')[1])
    poly = PolynomialFeatures(degree, include_bias=False)
    X_future_point = poly.fit_transform(np.array([future_point]).reshape(-1, 1))

y_future_point = best_model.predict(X_future_point)[0]
print(f"y = {y_future_point:.4f}")



    