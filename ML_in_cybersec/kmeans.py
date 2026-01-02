import numpy as np
import matplotlib.pyplot as plt


def euclidean_distance(point1, point2):
    return np.sqrt(np.sum((point1 - point2) ** 2))


def initialize_centroids(data, k):
    indices = np.random.choice(len(data), k, replace=False)
    return data[indices]


def assign_clusters(data, centroids):
    labels = []
    for point in data:
        distances = [euclidean_distance(point, c) for c in centroids]
        cluster_idx = np.argmin(distances)
        labels.append(cluster_idx)
    return np.array(labels)


def update_centroids(data, labels, k, old_centroids):
    new_centroids = []
    for i in range(k):
        points_in_cluster = data[labels == i]

        if len(points_in_cluster) > 0:
            new_centroids.append(np.mean(points_in_cluster, axis=0))
        else:
            new_centroids.append(old_centroids[i])

    return np.array(new_centroids)


def kmeans(data, k, max_iters=100, tol=0.001):
    centroids = initialize_centroids(data, k)

    for i in range(max_iters):
        labels = assign_clusters(data, centroids)

        prev_centroids = centroids.copy()

        centroids = update_centroids(data, labels, k, prev_centroids)

        shift = np.sum([euclidean_distance(p, c) for p, c in zip(prev_centroids, centroids)])

        if shift < tol:
            print(f"--> Convergence at loop {i + 1}")
            break

    return labels, centroids

def generate_data():
    np.random.seed(42)
    c1 = np.random.randn(50, 2) + [2, 2]
    c2 = np.random.randn(50, 2) + [8, 3]
    c3 = np.random.randn(50, 2) + [5, 8]
    return np.vstack((c1, c2, c3))


def visualize_kmeans(data, labels, centroids):
    plt.figure(figsize=(8, 6))

    # Draw data points
    plt.scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis', s=30, label='Points')

    # Draw centroids
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='x', s=200, linewidths=3, label='Centroids')

    plt.title("K-Means Clustering Result")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    X = generate_data()

    final_labels, final_centroids = kmeans(X, k=3)

    visualize_kmeans(X, final_labels, final_centroids)