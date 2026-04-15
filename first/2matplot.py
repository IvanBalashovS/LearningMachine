import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Данные
x = np.array([1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.03, 2.13, 2.25, 2.3, 2.4, 2.55, 2.6, 2.75, 2.8, 2.95, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4])
y = np.array([0, 0.25, 0.75, 1.25, 1.8, 2.05, 2.2, 2, 2.7, 2.5, 1.1, 1.05, 1.4, 2.7, 2.5, 1.1, 1.05, 1.4, 1.7, 2.5, 3.2, 3.85, 4.4, 4.6, 4.5, 4.1, 3.6, 3.2, 2.8, 2.6])

print(f"Размер данных: {len(x)} точек")
print("-" * 50)

# Создаём признаки для модели
x_flat = x.flatten()
X_features = np.column_stack([
    np.ones_like(x_flat),           # φ0 = 1
    x_flat,                          # φ1 = x
    x_flat**2,                       # φ2 = x²
    x_flat**3,                       # φ3 = x³
    np.sin(x_flat),                   # φ4 = sin(x)
    np.cos(x_flat),                   # φ5 = cos(x)
    np.sin(2*x_flat),                 # φ6 = sin(2x)
    np.cos(2*x_flat)                  # φ7 = cos(2x)
])

# Названия признаков для красивого вывода
feature_names = [
    "1 (константа)",
    "x",
    "x²",
    "x³",
    "sin(x)",
    "cos(x)",
    "sin(2x)",
    "cos(2x)"
]

# Обучение модели
model = LinearRegression(fit_intercept=False)
model.fit(X_features, y)

# Получение коэффициентов
coefficients = model.coef_

# Вывод коэффициентов
print("\n📈 КОЭФФИЦИЕНТЫ МОДЕЛИ:")
print("-" * 50)
for name, coef in zip(feature_names, coefficients):
    print(f"{name:15s}: {coef:10.4f}")

# Формула модели
print("\n📝 ФОРМУЛА МОДЕЛИ:")
print("y = ", end="")
for i, (name, coef) in enumerate(zip(feature_names, coefficients)):
    if i == 0:
        print(f"{coef:.4f}", end="")
    else:
        if coef >= 0:
            print(f" + {coef:.4f}·{name}", end="")
        else:
            print(f" - {abs(coef):.4f}·{name}", end="")
print()

# Предсказания для исходных данных
y_pred = model.predict(X_features)

# Метрики качества
r2 = r2_score(y, y_pred)
print(f"\n📊 КАЧЕСТВО МОДЕЛИ:")
print(f"R² score: {r2:.4f}")

# Предсказание на будущее
x_future = np.array([4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0])
x_future_flat = x_future.flatten()
X_future_features = np.column_stack([
    np.ones_like(x_future_flat),
    x_future_flat,
    x_future_flat**2,
    x_future_flat**3,
    np.sin(x_future_flat),
    np.cos(x_future_flat),
    np.sin(2*x_future_flat),
    np.cos(2*x_future_flat)
])
y_future = model.predict(X_future_features)

print("\n🔮 ПРЕДСКАЗАНИЯ НА БУДУЩЕЕ:")
for xi, yi in zip(x_future, y_future):
    print(f"x = {xi:.1f} -> y = {yi:.4f}")

# =========== ПОСТРОЕНИЕ ГРАФИКОВ ===========
plt.figure(figsize=(12, 8))

# Для гладкой кривой создаём много точек
x_smooth = np.linspace(min(x), max(x_future), 500)
x_smooth_flat = x_smooth.flatten()
X_smooth_features = np.column_stack([
    np.ones_like(x_smooth_flat),
    x_smooth_flat,
    x_smooth_flat**2,
    x_smooth_flat**3,
    np.sin(x_smooth_flat),
    np.cos(x_smooth_flat),
    np.sin(2*x_smooth_flat),
    np.cos(2*x_smooth_flat)
])
y_smooth = model.predict(X_smooth_features)

# График 1: Исходные данные и модель
plt.subplot(2, 1, 1)
plt.scatter(x, y, color='red', s=50, label='Исходные данные', zorder=5)
plt.plot(x_smooth, y_smooth, 'b-', linewidth=2, label='Модель', zorder=3)
plt.scatter(x_future, y_future, color='green', s=100, marker='*', 
           label='Предсказания', zorder=6, edgecolors='darkgreen', linewidth=2)

plt.xlabel('x', fontsize=12)
plt.ylabel('y', fontsize=12)
plt.title('Аппроксимация данных и предсказание', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)

# Добавим вертикальную линию, разделяющую прошлое и будущее
plt.axvline(x=max(x), color='gray', linestyle='--', alpha=0.7, label='Текущий момент')
plt.legend()

# График 2: Остатки (ошибки модели)
plt.subplot(2, 1, 2)
residuals = y - y_pred
plt.stem(x, residuals, linefmt='r-', markerfmt='ro', basefmt='k-', use_line_collection=True)
plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
plt.xlabel('x', fontsize=12)
plt.ylabel('Остатки (y - y_pred)', fontsize=12)
plt.title('Остатки модели', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('gg.png', dpi=300, bbox_inches='tight', facecolor='white')

# =========== ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ ===========
print("\n📈 СТАТИСТИКА ОСТАТКОВ:")
print(f"Среднее остатков: {np.mean(residuals):.6f}")
print(f"Стд остатков: {np.std(residuals):.4f}")
print(f"Мин остаток: {np.min(residuals):.4f}")
print(f"Макс остаток: {np.max(residuals):.4f}")