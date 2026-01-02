import math
import numpy as np
import matplotlib.pyplot as plt

NOISE = -1
UNDEFINED = 0


def visualize_DBscan(x, labels):
    x_coords = [p[0] for p in x]
    y_coords = [p[1] for p in x]

    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    plt.figure(figsize=(8, 6))

    for k, col in zip(unique_labels, colors):
        if k == -1:
            col = [0, 0, 0, 1]

        class_member_mask = [label == k for label in labels]

        xy = [x[i] for i in range(len(x)) if class_member_mask[i]]
        xy_x = [p[0] for p in xy]
        xy_y = [p[1] for p in xy]

        plt.plot(xy_x, xy_y, 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=10 if k != -1 else 6,
                 label=f'Cluster {k}' if k != -1 else 'Noise')

    plt.title('Result of dbSCAN')
    plt.legend()
    plt.grid(True)
    plt.show()


def DBscan(db, dist_func, eps, min_pts):
    c = 0  # Cluster counter
    labels = [UNDEFINED] * len(db)  # Init labels for all points

    for p_idx in range(len(db)):

        if labels[p_idx] != UNDEFINED:
            continue

        neighbors = range_query(db, dist_func, p_idx, eps)

        if len(neighbors) < min_pts:
            labels[p_idx] = NOISE
            continue

        c += 1
        labels[p_idx] = c

        seeds = [n for n in neighbors if n != p_idx]

        i = 0
        while i < len(seeds):
            q_idx = seeds[i]
            i += 1

            if labels[q_idx] == NOISE:
                labels[q_idx] = c

            if labels[q_idx] != UNDEFINED:
                continue

            labels[q_idx] = c

            neighbors_q = range_query(db, dist_func, q_idx, eps)

            if len(neighbors_q) >= min_pts:
                for n_idx in neighbors_q:
                    if n_idx not in seeds:
                        seeds.append(n_idx)

    return labels


def range_query(db, dist_func, q_idx, eps):
    neighbors = []
    q_val = db[q_idx]

    for p_idx, p_val in enumerate(db):
        if dist_func(q_val, p_val) <= eps:
            neighbors.append(p_idx)

    return neighbors


def euclidean_dist(p1, p2):
    sum_sq = sum((a - b) ** 2 for a, b in zip(p1, p2))
    return math.sqrt(sum_sq)


if __name__ == "__main__":
    x = [[1, 2], [2, 2], [2, 3], [8, 7], [8, 8], [25, 80]]

    # eps=3, min_pts=2
    result_labels = DBscan(x, euclidean_dist, 3, 2)

    print("Data:", x)
    print("Labels:", result_labels)

    # Gọi hàm vẽ
    visualize_DBscan(x, result_labels)
