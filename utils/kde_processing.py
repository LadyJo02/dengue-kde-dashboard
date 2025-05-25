import numpy as np
from scipy.stats import gaussian_kde

def generate_kde(points, bandwidth):
    if points is None or points.shape[1] < 2:
        return np.array([]), np.array([]), np.array([])

    try:
        kde = gaussian_kde(points, bw_method=bandwidth)
        x_min, x_max = points[0].min(), points[0].max()
        y_min, y_max = points[1].min(), points[1].max()

        xi, yi = np.mgrid[x_min:x_max:300j, y_min:y_max:300j]
        zi = kde(np.vstack([xi.flatten(), yi.flatten()])).reshape(xi.shape)
        return xi, yi, zi
    except Exception as e:
        print(f"[KDE ERROR] {e}")
        return np.array([]), np.array([]), np.array([])
