import math
import numpy as np
import matplotlib.pyplot as plt

NOISE = -1
UNDEFINED = 0


def visualize_dbscan(x, labels):
    # Chuyển đổi x thành list các tọa độ x và y để vẽ
    x_coords = [p[0] for p in x]
    y_coords = [p[1] for p in x]

    # Tạo danh sách màu sắc: Noise màu đen, các cụm màu khác
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

    plt.figure(figsize=(8, 6))

    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Màu đen cho Noise (dùng mã màu hex hoặc tên)
            col = [0, 0, 0, 1]

            # Lọc ra các điểm thuộc nhãn k
        class_member_mask = [label == k for label in labels]

        # Vẽ các điểm này
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


def dbscan(db, dist_func, eps, min_pts):
    c = 0  # Cluster counter
    labels = [UNDEFINED] * len(db)  # Khởi tạo nhãn cho tất cả các điểm

    # for each point P in database db
    # Dùng index (p_idx) để truy cập label dễ dàng hơn
    for p_idx in range(len(db)):

        # if label(P) ≠ undefined then continue
        if labels[p_idx] != UNDEFINED:
            continue

        # Neighbors N := RangeQuery(db, distFunc, P, eps)
        neighbors = range_query(db, dist_func, p_idx, eps)

        # if |N| < minPts then (Density check)
        if len(neighbors) < min_pts:
            labels[p_idx] = NOISE  # label(P) := Noise
            continue

        # C := C + 1
        c += 1
        # label(P) := C
        labels[p_idx] = c

        # SeedSet S := N \ {P}
        # Tạo danh sách hạt giống từ hàng xóm, loại bỏ chính điểm P
        seeds = [n for n in neighbors if n != p_idx]

        # for each point Q in S
        # Trong Python, không thể vừa lặp vừa thêm phần tử vào list bằng 'for'
        # Nên ta dùng 'while' để mô phỏng việc S mở rộng (S := S U N)
        i = 0
        while i < len(seeds):
            q_idx = seeds[i]
            i += 1

            # if label(Q) = Noise then label(Q) := C
            if labels[q_idx] == NOISE:
                labels[q_idx] = C

            # if label(Q) ≠ undefined then continue
            if labels[q_idx] != UNDEFINED:
                continue

            # label(Q) := C
            labels[q_idx] = c

            # Neighbors N := RangeQuery(db, distFunc, Q, eps)
            neighbors_q = range_query(db, dist_func, q_idx, eps)

            # if |N| ≥ minPts then (Density check)
            if len(neighbors_q) >= min_pts:
                # S := S U N (Add new neighbors to seed set)
                for n_idx in neighbors_q:
                    if n_idx not in seeds:  # Tránh thêm trùng lặp (Optimization)
                        seeds.append(n_idx)

    return labels


# RangeQuery(db, distFunc, Q, eps)
def range_query(db, dist_func, q_idx, eps):
    neighbors = []
    q_val = db[q_idx]

    # for each point P in database db
    for p_idx, p_val in enumerate(db):
        # if distFunc(Q, P) ≤ eps
        if dist_func(q_val, p_val) <= eps:
            neighbors.append(p_idx)

    return neighbors


# Hàm tính khoảng cách Euclid đơn giản
def euclidean_dist(p1, p2):
    sum_sq = sum((a - b) ** 2 for a, b in zip(p1, p2))
    return math.sqrt(sum_sq)


if __name__ == "__main__":
    x = [[1, 2], [2, 2], [2, 3], [8, 7], [8, 8], [25, 80]]

    # eps=3, min_pts=2
    result_labels = dbscan(x, euclidean_dist, 3, 2)

    print("Data:", x)
    print("Labels:", result_labels)

    # Gọi hàm vẽ
    visualize_dbscan(x, result_labels)