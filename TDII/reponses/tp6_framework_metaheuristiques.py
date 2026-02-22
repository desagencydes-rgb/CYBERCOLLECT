import numpy as np
import random
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import List, Tuple, Any

class Problem(ABC):
    @abstractmethod
    def evaluate(self, solution: Any) -> float:
        pass
    @abstractmethod
    def generate_random_solution(self) -> Any:
        pass
    @abstractmethod
    def get_neighborhood(self, solution: Any) -> List[Any]:
        pass

class TSPProblem(Problem):
    def __init__(self, distances: np.ndarray):
        self.distances = distances
        self.n = len(distances)

    def evaluate(self, tour: List[int]) -> float:
        total = 0
        for i in range(self.n):
            total += self.distances[tour[i]][tour[(i + 1) % self.n]]
        return total

    def generate_random_solution(self) -> List[int]:
        tour = list(range(self.n))
        random.shuffle(tour)
        return tour

    def get_neighborhood(self, tour: List[int]) -> List[List[int]]:
        neighbors = []
        n = len(tour)
        # 2-opt swap
        for i in range(n):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1: continue
                new_tour = tour[:]
                new_tour[i+1:j+1] = reversed(new_tour[i+1:j+1])
                neighbors.append(new_tour)
        return neighbors

class Metaheuristic(ABC):
    def __init__(self, problem: Problem, max_iter: int = 1000):
        self.problem = problem
        self.max_iter = max_iter
        self.history = []

    @abstractmethod
    def solve(self) -> Tuple[Any, float]:
        pass

class SimulatedAnnealing(Metaheuristic):
    def __init__(self, problem, max_iter=1000, temp_init=1000, cooling_rate=0.99):
        super().__init__(problem, max_iter)
        self.temp_init = temp_init
        self.cooling_rate = cooling_rate

    def solve(self):
        current = self.problem.generate_random_solution()
        current_val = self.problem.evaluate(current)
        best, best_val = current[:], current_val
        temp = self.temp_init

        for _ in range(self.max_iter):
            neighbors = self.problem.get_neighborhood(current)
            if not neighbors: break
            
            neighbor = random.choice(neighbors)
            neighbor_val = self.problem.evaluate(neighbor)
            
            delta = neighbor_val - current_val
            if delta < 0 or random.random() < np.exp(-delta / temp):
                current, current_val = neighbor, neighbor_val
                if current_val < best_val:
                    best, best_val = current[:], current_val
            
            temp *= self.cooling_rate
            self.history.append(best_val)
            
        return best, best_val

def demo_tsp():
    # Générer 10 villes aléatoires
    n = 10
    coords = np.random.rand(n, 2) * 100
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i][j] = np.linalg.norm(coords[i] - coords[j])

    problem = TSPProblem(dist_matrix)
    
    print("--- Benchmark Méta-heuristiques (TSP) ---")
    
    # Recuit Simulé
    sa = SimulatedAnnealing(problem, max_iter=2000)
    best_tour, best_val = sa.solve()
    print(f"Recuit Simulé : Meilleure distance = {best_val:.2f}")

    plt.figure(figsize=(10, 5))
    plt.plot(sa.history)
    plt.title("Convergence du Recuit Simulé")
    plt.xlabel("Itérations")
    plt.ylabel("Distance")
    plt.grid(True)
    plt.savefig("convergence_tsp.png")
    print("Graphique de convergence sauvegardé sous : convergence_tsp.png")

if __name__ == "__main__":
    demo_tsp()
