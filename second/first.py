import numpy as np
import pandas as pd

m = 0
sigma = 2
sigma2 = sigma**2
simulation = 10000
print(f"истинная дисперсия={sigma2}")
data = []
for n_test in [5, 10, 20, 50, 100]:
    
    sam_test = np.random.normal(m, sigma, (simulation, n_test))
    sam_means_test = np.mean(sam_test, axis=1, keepdims=True)
    
    var_n_test = np.sum((sam_test - sam_means_test)**2, axis=1) / n_test
    var_minus_1_test = np.sum((sam_test - sam_means_test)**2, axis=1) / (n_test - 1)
    
    mean_var_n_test = np.mean(var_n_test) 
    mean_minus_1_test = np.mean(var_minus_1_test)
    
    data.append({
        'n': n_test,
        'Сред. знач. оценок дисперсии (n)': np.mean(var_n_test),
        'Смещение (n)': mean_var_n_test - sigma2,
        'Сред. знач. оценок дисперсии (n - 1)': np.mean(var_minus_1_test),
        'Смещение (n-1)': mean_minus_1_test - sigma2,
        'Теор. смещение (n)': -sigma2/n_test
    })

df_dependency = pd.DataFrame(data)

pd.set_option('display.float_format', lambda x: f'{x:.4f}')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print(df_dependency.to_string(index=False))