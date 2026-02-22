import time

def knapsack_2D(W, wt, val, n):
    """Version classique O(nW) en espace."""
    K = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, W + 1):
            if wt[i - 1] <= w:
                K[i][w] = max(val[i - 1] + K[i - 1][w - wt[i - 1]], K[i - 1][w])
            else:
                K[i][w] = K[i - 1][w]
    return K[n][W]

def knapsack_1D(W, wt, val, n):
    """Version optimisée en mémoire O(W)."""
    dp = [0 for _ in range(W + 1)]
    for i in range(n):
        # Parcours inverse pour ne pas réutiliser le même objet
        for w in range(W, wt[i] - 1, -1):
            dp[w] = max(dp[w], val[i] + dp[w - wt[i]])
    return dp[W]

def knapsack_approximation(W, wt, val, n, epsilon=0.1):
    """Version d'approximation FPTAS."""
    max_val = max(val)
    # Facteur de mise à l'échelle
    K = (epsilon * max_val) / n
    if K == 0: K = 1 # Sécurité
    
    scaled_val = [int(v / K) for v in val]
    total_val = sum(scaled_val)
    
    # DP sur les valeurs (recherche du poids min pour une valeur donnée)
    dp = [float('inf')] * (total_val + 1)
    dp[0] = 0
    
    for i in range(n):
        for v in range(total_val, scaled_val[i] - 1, -1):
            dp[v] = min(dp[v], dp[v - scaled_val[i]] + wt[i])
            
    # Trouver la meilleure valeur réalisable sous le poids W
    best_val = 0
    for v in range(total_val + 1):
        if dp[v] <= W:
            best_val = v
            
    return best_val * K

def experimenter():
    W = 50
    wt = [10, 20, 30]
    val = [60, 100, 120]
    n = len(val)

    print("--- Benchmark Sac à Dos ---")
    
    # 2D
    start = time.time()
    res_2d = knapsack_2D(W, wt, val, n)
    t_2d = time.time() - start
    print(f"2D (Classique) : Valeur = {res_2d}, Temps = {t_2d:.6f}s")

    # 1D
    start = time.time()
    res_1d = knapsack_1D(W, wt, val, n)
    t_1d = time.time() - start
    print(f"1D (Optimisé)  : Valeur = {res_1d}, Temps = {t_1d:.6f}s")

    # FPTAS (Approximation)
    epsilons = [0.5, 0.1, 0.05]
    for eps in epsilons:
        start = time.time()
        res_approx = knapsack_approximation(W, wt, val, n, eps)
        t_approx = time.time() - start
        print(f"FPTAS (eps={eps:0.2f}): Valeur ~ {res_approx:.2f}, Temps = {t_approx:.6f}s")

if __name__ == "__main__":
    experimenter()
