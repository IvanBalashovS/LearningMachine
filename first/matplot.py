import matplotlib.pyplot as plt
import numpy as np

def project_points(points, point_on_line, direction):
    """
    Проецирует точки на прямую, заданную точкой на прямой и направлением
    """
    vectors = points - point_on_line
    
    # Находим длину проекции
    projections_length = np.dot(vectors, direction)
    
    # Координаты проекций
    projections = point_on_line + np.outer(projections_length, direction)
    
    return projections

def calculate_perpendicular(v):
    """
    Вычисляет единичный вектор, перпендикулярный данному
    """
    v_normalized = v / np.linalg.norm(v)
    
    n = np.array([-v_normalized[1], v_normalized[0]])
    
    return n

def draw_picture():

    X1 = np.random.multivariate_normal([4,4], [[0.1,-0.4], [-0.4,3]], size=20)
    X2 = np.random.multivariate_normal([8,4], [[0.2,0.4], [0.4,1]], size=20)
    
    plt.figure(figsize=(12, 8))
    
    plt.scatter(X1[:,0], X1[:,1], c='blue', label='Набор 1', alpha=0.6, s=50)
    plt.scatter(X2[:,0], X2[:,1], c='red', label='Набор 2', alpha=0.6, s=50)
    
    center1 = np.mean(X1, axis=0)
    center2 = np.mean(X2, axis=0)
    
    plt.scatter(center1[0], center1[1], c='darkblue', s=200, marker='D', 
                label=f'Центр 1 ({center1[0]:.2f}, {center1[1]:.2f})')
    plt.scatter(center2[0], center2[1], c='darkred', s=200, marker='s', 
                label=f'Центр 2 ({center2[0]:.2f}, {center2[1]:.2f})')
    

    plt.plot([center1[0], center2[0]], [center1[1], center2[1]], 
             c='darkgreen', linewidth=2, linestyle='--', label='Линия центров')
    
    mid_point = (center1 + center2) / 2
    
    v = center2 - center1
    
    n = calculate_perpendicular(v)

    t = np.linspace(-8, 8, 100)
    perp_x = mid_point[0] + n[0] * t
    perp_y = mid_point[1] + n[1] * t
    plt.plot(perp_x, perp_y, 'purple', linewidth=2.5, label='Срединный перпендикуляр')
    
    plt.scatter(mid_point[0], mid_point[1], c='gold', s=150, marker='o', 
                label=f'Середина ({mid_point[0]:.2f}, {mid_point[1]:.2f})', 
                edgecolor='black', zorder=5)
    
    all_points = np.vstack([X1, X2])
    
    projections = project_points(all_points, mid_point, n)
    
    plt.scatter(projections[:,0], projections[:,1], c='orange', s=80, 
                marker='^', alpha=0.7, label='Проекции точек')
    

    for i in range(len(all_points)):
        if i < 20:
            plt.plot([all_points[i,0], projections[i,0]], 
                    [all_points[i,1], projections[i,1]], 
                    'blue', linewidth=0.8, alpha=0.3)
        else:
            plt.plot([all_points[i,0], projections[i,0]], 
                    [all_points[i,1], projections[i,1]], 
                    'red', linewidth=0.8, alpha=0.3)
    
    plt.annotate(f'({center1[0]:.2f}, {center1[1]:.2f})', 
                (center1[0], center1[1]), 
                xytext=(10, 10), textcoords='offset points', 
                fontsize=10, fontweight='bold', color='darkblue')
    plt.annotate(f'({center2[0]:.2f}, {center2[1]:.2f})', 
                (center2[0], center2[1]), 
                xytext=(-10, -15), textcoords='offset points', 
                fontsize=10, fontweight='bold', color='darkred')
    
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xlabel('X координата', fontsize=12)
    plt.ylabel('Y координата', fontsize=12)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    plt.axis('equal')
    
    x_min = min(np.min(X1[:,0]), np.min(X2[:,0]), np.min(projections[:,0])) - 2
    x_max = max(np.max(X1[:,0]), np.max(X2[:,0]), np.max(projections[:,0])) + 2
    y_min = min(np.min(X1[:,1]), np.min(X2[:,1]), np.min(projections[:,1])) - 2
    y_max = max(np.max(X1[:,1]), np.max(X2[:,1]), np.max(projections[:,1])) + 2
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    plt.tight_layout()
    plt.savefig('matplotlib_task_improved.png', dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    draw_picture()
    
    