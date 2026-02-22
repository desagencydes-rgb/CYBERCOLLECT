"""
Optimiseur VRP (Vehicle Routing Problem).
Utilise des méta-heuristiques pour minimiser la distance totale de collecte.
"""
from niveau4.src.tournee import Tournee
import random
import copy

class OptimiseurVRP:
    """
    Classe gérant l'optimisation des tournées de plusieurs véhicules.
    """
    def __init__(self, graphe, camions: list, points_collecte: dict):
        """
        Initialise l'optimiseur.
        
        Args:
            graphe (GrapheRoutier): Le réseau routier.
            camions (list): Liste des camions disponibles.
            points_collecte (dict): Dictionnaire des points à visiter.
        """
        self.graphe = graphe
        self.camions = camions
        self.points_collecte = points_collecte
        self.tournees = []
        
        # Pré-calculer la matrice des distances pour accélérer les itérations de l'optimiseur
        print("Précalcul de la matrice des distances pour VRP...")
        self.matrice_distances = self.graphe.matrice_distances()
        self.graphe.matrice = self.matrice_distances

    def construire_solution_initiale(self) -> list:
        """
        Génère une première solution valide via une heuristique gloutonne du "Plus Proche Voisin".
        Chaque camion dessert les points les plus proches jusqu'à ce qu'il n'y ait plus de points.
        
        Returns:
            list: Liste des objets Tournee créés.
        """
        points_a_visiter = set(self.points_collecte.keys())
        if 0 in points_a_visiter: points_a_visiter.remove(0) # Le dépôt (0) est géré à part
        
        tournees = []
        
        for camion in self.camions:
            if not points_a_visiter:
                break
                
            tournee = Tournee(camion.id)
            tournee.ajouter_point(0) # Départ du dépôt
            
            curr_point = 0
            
            while True:
                # Recherche du point le plus proche parmi les points restants
                meilleur_p = None
                meilleure_dist = float('inf')
                
                for p_id in points_a_visiter:
                    dist = self.matrice_distances[curr_point][p_id]
                    if dist < meilleure_dist:
                        meilleure_dist = dist
                        meilleur_p = p_id
                
                if meilleur_p is not None:
                    tournee.ajouter_point(meilleur_p)
                    points_a_visiter.remove(meilleur_p)
                    curr_point = meilleur_p
                else:
                    break
            
            tournee.ajouter_point(0) # Retour au dépôt
            tournees.append(tournee)
            
        self.tournees = tournees
        return tournees

    def algorithme_2opt(self, tournee: Tournee) -> Tournee:
        """
        Améliore une tournée en supprimant les croisements (heuristique 2-opt).
        Inverse itérativement des segments de la tournée si cela réduit la distance totale.
        
        Args:
            tournee (Tournee): La tournée à optimiser.
            
        Returns:
            Tournee: La tournée améliorée.
        """
        points = tournee.points_ids
        n = len(points)
        if n < 4: return tournee # Pas de permutation possible avec moins de 2 points intermédiaires
        
        best_points = points[:]
        best_dist = tournee.calculer_distance(self.graphe)
        
        improved = True
        while improved:
            improved = False
            # On parcourt toutes les paires possibles de segments à "décroiser"
            for i in range(1, n - 1):
                for j in range(i + 1, n - 1):
                    if j - i == 0: continue
                    
                    # Application du swap 2-opt : inversion de l'ordre des points entre i et j
                    new_points = best_points[:]
                    new_points[i:j+1] = best_points[i:j+1][::-1]
                    
                    t_temp = Tournee(tournee.camion_id, new_points)
                    d = t_temp.calculer_distance(self.graphe)
                    
                    # Si la nouvelle distance est meilleure, on valide le changement
                    if d < best_dist - 1e-9:
                        best_dist = d
                        best_points = new_points
                        improved = True
                        break 
                if improved: break
                        
        tournee.points_ids = best_points
        return tournee

    def recherche_tabou(self, iterations: int = 100) -> list:
        """
        Méthode de recherche de haut niveau (Recherche Tabou).
        Dans cette implémentation, s'appuie principalement sur l'optimisation locale 2-opt.
        
        Returns:
            list: Ensemble des tournées optimisées.
        """
        # Garantir qu'on a une solution de base
        if not self.tournees:
            self.construire_solution_initiale()
            
        # Optimisation locale sur chaque camion
        for t in self.tournees:
            self.algorithme_2opt(t)
            
        return self.tournees
