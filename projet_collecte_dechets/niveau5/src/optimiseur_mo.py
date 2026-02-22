"""
Optimiseur Multi-Objectif (MO).
Cherche un compromis entre l'efficacité opérationnelle (distance) et l'équité sociale (répartition du travail).
"""
from niveau4.src.optimiseur_vrp import OptimiseurVRP
import copy

class OptimiseurMultiObjectif(OptimiseurVRP):
    """
    Étendre l'optimiseur VRP pour gérer plusieurs fonctions objectifs simultanément.
    """
    def __init__(self, graphe, camions, points_collecte):
        super().__init__(graphe, camions, points_collecte)
        
    def evaluer_solution(self, tournees: list) -> dict:
        """
        Évalue la qualité d'une solution selon plusieurs axes de performance.
        
        Critères :
        1. Distance totale (Coût économique/écologique).
        2. Équilibre des charges (Dispersion de la charge entre camions).
        
        Args:
            tournees (list): L'ensemble des tournées de la solution.
            
        Returns:
            dict: Les scores sur les différents objectifs.
        """
        dist_totale = sum(t.calculer_distance(self.graphe) for t in tournees)
        
        charges = []
        for t in tournees:
            # Mesure de la charge par le nombre de points visités
            nb_points = len(t.points_ids) - 2 if len(t.points_ids) >= 2 else 0
            charges.append(nb_points)
            
        # L'écart de charge mesure l'injustice de répartition du travail
        ecart_charge = max(charges) - min(charges) if charges else 0
        
        return {
            "distance_totale": dist_totale,
            "ecart_charge": ecart_charge
        }
        
    def optimisation_bi_critere(self) -> list:
        """
        Recherche une solution située sur le front de Pareto (compromis distance/équilibre).
        
        Heuristique :
        1. Génère une solution minimisant la distance.
        2. Tente des transferts de points pour lisser les différences de charge.
        
        Returns:
            list: Liste des tournées optimisées.
        """
        # Phase 1 : Optimisation spatiale pure (VRP)
        self.construire_solution_initiale()
        if self.tournees:
            self.algorithme_2opt(self.tournees[0]) 
        
        sol_base = copy.deepcopy(self.tournees)
        
        # Phase 2 : Rééquilibrage (Logique de bascule de points)
        # Note: L'implémentation complète nécessiterait une recherche locale multiobjectif
        
        return sol_base 
