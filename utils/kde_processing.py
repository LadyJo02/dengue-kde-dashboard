import numpy as np
from scipy.stats import gaussian_kde


def generate_kde(points, bandwidth='silverman', grid_size=300):
    x = points[:, 0]
    y = points[:, 1]

    kde = gaussian_kde([x, y], bw_method=bandwidth)
    xi, yi = np.mgrid[x.min():x.max():grid_size*1j, y.min():y.max():grid_size*1j]
    zi = kde(np.vstack([xi.flatten(), yi.flatten()]))

    return xi, yi, zi.reshape(xi.shape)