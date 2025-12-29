import math

# Định nghĩa các hằng số trạng thái để code dễ đọc (giống pseudocode)
NOISE = -1
UNDEFINED = 0


def dbscan(DB, dist_func, eps, min_pts):
    """
    DB: List các điểm dữ liệu (ví dụ: [[1,2], [2,2], ...])
    dist_func: Hàm tính khoảng cách
    eps: Bán kính epsilon
    min_pts: Số điểm tối thiểu
    """
    C = 0  # Cluster counter
    labels = [UNDEFINED] * len(DB)  # Khởi tạo nhãn cho tất cả các điểm

    # for each point P in database DB
    # Dùng index (P_idx) để truy cập label dễ dàng hơn
    for P_idx in range(len(DB)):

        # if label(P) ≠ undefined then continue
        if labels[P_idx] != UNDEFINED:
            continue

        # Neighbors N := RangeQuery(DB, distFunc, P, eps)
        neighbors = range_query(DB, dist_func, P_idx, eps)

        # if |N| < minPts then (Density check)
        if len(neighbors) < min_pts:
            labels[P_idx] = NOISE  # label(P) := Noise
            continue

        # C := C + 1
        C += 1
        # label(P) := C
        labels[P_idx] = C

        # SeedSet S := N \ {P}
        # Tạo danh sách hạt giống từ hàng xóm, loại bỏ chính điểm P
        seeds = [n for n in neighbors if n != P_idx]

        # for each point Q in S
        # Trong Python, không thể vừa lặp vừa thêm phần tử vào list bằng 'for'
        # Nên ta dùng 'while' để mô phỏng việc S mở rộng (S := S U N)
        i = 0
        while i < len(seeds):
            Q_idx = seeds[i]
            i += 1

            # if label(Q) = Noise then label(Q) := C
            if labels[Q_idx] == NOISE:
                labels[Q_idx] = C

            # if label(Q) ≠ undefined then continue
            if labels[Q_idx] != UNDEFINED:
                continue

            # label(Q) := C
            labels[Q_idx] = C

            # Neighbors N := RangeQuery(DB, distFunc, Q, eps)
            neighbors_Q = range_query(DB, dist_func, Q_idx, eps)

            # if |N| ≥ minPts then (Density check)
            if len(neighbors_Q) >= min_pts:
                # S := S U N (Add new neighbors to seed set)
                for n_idx in neighbors_Q:
                    if n_idx not in seeds:  # Tránh thêm trùng lặp (Optimization)
                        seeds.append(n_idx)

    return labels


# RangeQuery(DB, distFunc, Q, eps)
def range_query(DB, dist_func, Q_idx, eps):
    neighbors = []
    Q_val = DB[Q_idx]

    # for each point P in database DB
    for P_idx, P_val in enumerate(DB):
        # if distFunc(Q, P) ≤ eps
        if dist_func(Q_val, P_val) <= eps:
            neighbors.append(P_idx)

    return neighbors


# --- Hàm phụ trợ để chạy thử (Helper) ---

# Hàm tính khoảng cách Euclid đơn giản
def euclidean_dist(p1, p2):
    sum_sq = sum((a - b) ** 2 for a, b in zip(p1, p2))
    return math.sqrt(sum_sq)


# --- Chạy thử (Example Usage) ---
if __name__ == "__main__":
    # Dữ liệu mẫu
    X = [[1, 2], [2, 2], [2, 3], [8, 7], [8, 8], [25, 80]]

    # Chạy thuật toán
    # eps=3, min_pts=2
    result_labels = dbscan(X, euclidean_dist, 3, 2)

    print("Dữ liệu:", X)
    print("Nhãn (0=Unused, -1=Noise, >0=Cluster):", result_labels)





























