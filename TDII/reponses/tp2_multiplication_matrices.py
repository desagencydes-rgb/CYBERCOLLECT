import numpy as np
import time

def add_matrices(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def sub_matrices(A, B):
    return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def multiplication_naive(A, B):
    """Multiplication naïve O(n^3)."""
    n = len(A)
    C = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C

def multiplication_strassen(A, B):
    """Algorithme de Strassen O(n^log2(7))."""
    n = len(A)
    
    # Cas de base
    if n <= 2: # Seuil bas pour la récursion
        return multiplication_naive(A, B)
    
    # Découpage des matrices
    m = n // 2
    A11 = [row[:m] for row in A[:m]]
    A12 = [row[m:] for row in A[:m]]
    A21 = [row[:m] for row in A[m:]]
    A22 = [row[m:] for row in A[m:]]

    B11 = [row[:m] for row in B[:m]]
    B12 = [row[m:] for row in B[:m]]
    B21 = [row[:m] for row in B[m:]]
    B22 = [row[m:] for row in B[m:]]

    # Calcul des 7 produits de Strassen
    M1 = multiplication_strassen(add_matrices(A11, A22), add_matrices(B11, B22))
    M2 = multiplication_strassen(add_matrices(A21, A22), B11)
    M3 = multiplication_strassen(A11, sub_matrices(B12, B22))
    M4 = multiplication_strassen(A22, sub_matrices(B21, B11))
    M5 = multiplication_strassen(add_matrices(A11, A12), B22)
    M6 = multiplication_strassen(sub_matrices(A21, A11), add_matrices(B11, B12))
    M7 = multiplication_strassen(sub_matrices(A12, A22), add_matrices(B21, B22))

    # Reconstruction
    C11 = add_matrices(sub_matrices(add_matrices(M1, M4), M5), M7)
    C12 = add_matrices(M3, M5)
    C21 = add_matrices(M2, M4)
    C22 = add_matrices(add_matrices(sub_matrices(M1, M2), M3), M6)

    # Combinaison
    C = []
    for i in range(m):
        C.append(C11[i] + C12[i])
    for i in range(m):
        C.append(C21[i] + C22[i])
        
    return C

def comparer_performances():
    """Compare les performances des deux algorithmes."""
    tailles = [2, 4, 8, 16, 32, 64] # Strassen est visible sur de plus grandes tailles, mais limitons ici
    print(f"{'n':>5} | {'Naive (s)':>12} | {'Strassen (s)':>12} | {'Ratio':>8}")
    print("-" * 45)

    for n in tailles:
        A = np.random.randint(0, 10, (n, n)).tolist()
        B = np.random.randint(0, 10, (n, n)).tolist()

        # Naive
        start = time.time()
        multiplication_naive(A, B)
        t_naive = time.time() - start

        # Strassen
        start = time.time()
        multiplication_strassen(A, B)
        t_strassen = time.time() - start

        ratio = t_naive / t_strassen if t_strassen > 0 else 0
        print(f"{n:5} | {t_naive:12.6f} | {t_strassen:12.6f} | {ratio:8.2f}")

if __name__ == "__main__":
    comparer_performances()
