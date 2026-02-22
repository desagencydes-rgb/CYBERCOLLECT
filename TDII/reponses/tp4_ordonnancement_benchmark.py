import random
import heapq
from dataclasses import dataclass
from typing import List
import matplotlib.pyplot as plt
import numpy as np

@dataclass
class Job:
    id: int
    processing_time: int
    due_date: int
    weight: float = 1.0

def earliest_due_date(jobs: List[Job]) -> List[Job]:
    """Règle EDD : Tri par date d'échéance croissante."""
    return sorted(jobs, key=lambda j: j.due_date)

def weighted_shortest_processing_time(jobs: List[Job]) -> List[Job]:
    """Règle WSPT : Tri par ratio p_i / w_i croissant."""
    return sorted(jobs, key=lambda j: j.processing_time / j.weight)

def moore_hodgson(jobs: List[Job]) -> List[Job]:
    """Minimise le nombre de tâches en retard."""
    sorted_jobs = sorted(jobs, key=lambda j: j.due_date)
    schedule = []
    current_time = 0
    
    # Utilisation d'un tas pour identifier la tâche la plus longue
    for job in sorted_jobs:
        schedule.append(job)
        current_time += job.processing_time
        
        if current_time > job.due_date:
            # Retrait de la tâche la plus longue parmi celles déjà prévues
            longest_job = max(schedule, key=lambda j: j.processing_time)
            schedule.remove(longest_job)
            current_time -= longest_job.processing_time
            
    return schedule

def evaluate_schedule(schedule: List[Job], metric: str = "tardiness") -> float:
    current_time = 0
    total = 0
    for job in schedule:
        current_time += job.processing_time
        if metric == "tardiness":
            total += max(0, current_time - job.due_date) * job.weight
        elif metric == "lateness":
            total += (current_time - job.due_date) * job.weight
    return total

def benchmark():
    n_counts = [10, 20, 50, 100, 200]
    results = {"EDD": [], "WSPT": [], "Moore": []}

    for n in n_counts:
        # Génération de jobs aléatoires
        jobs = []
        for i in range(n):
            p = random.randint(1, 20)
            d = random.randint(p, 5 * p)
            w = random.uniform(0.5, 2.0)
            jobs.append(Job(i, p, d, w))

        # Test des algos
        edd_res = evaluate_schedule(earliest_due_date(jobs))
        wspt_res = evaluate_schedule(weighted_shortest_processing_time(jobs))
        moore_res = len(jobs) - len(moore_hodgson(jobs)) # Nb tâches en retard
        
        results["EDD"].append(edd_res)
        results["WSPT"].append(wspt_res)
        results["Moore"].append(moore_res)

    print("--- Benchmark Ordonnancement ---")
    print(f"{'n':>5} | {'EDD (Tardiness)':>15} | {'WSPT (Tardiness)':>15} | {'Moore (Nb late)':>15}")
    print("-" * 60)
    for i in range(len(n_counts)):
        print(f"{n_counts[i]:5} | {results['EDD'][i]:15.2f} | {results['WSPT'][i]:15.2f} | {results['Moore'][i]:15d}")

if __name__ == "__main__":
    benchmark()
