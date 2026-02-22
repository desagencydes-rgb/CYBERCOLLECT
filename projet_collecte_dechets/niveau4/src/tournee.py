"""
Définit la classe Tournee, représentant la séquence de points visités par un camion.
"""
from commun.outils_math import distance_euclidienne

class Tournee:
    """
    Objet représentant un itinéraire de collecte ordonné.
    Une tournée commence et se termine généralement au dépôt.
    """
    def __init__(self, camion_id: int, points: list = None):
        """
        Initialise une nouvelle tournée.
        
        Args:
            camion_id (int): L'ID du camion effectuant la tournée.
            points (list): Liste optionnelle d'IDs de points de collecte pour initialiser l'ordre.
        """
        self.camion_id = camion_id
        # Stockage des IDs des points pour faciliter la manipulation et l'export JSON
        self.points_ids = points or [] 
        self.heure_depart = None
        self.heure_retour = None

    def ajouter_point(self, point_id: int, position: int = -1) -> bool:
        """
        Insère un point dans l'itinéraire à la position spécifiée.
        
        Args:
            point_id (int): L'ID du point à ajouter.
            position (int): L'index d'insertion. Par défaut (-1), ajoute à la fin.
            
        Returns:
            bool: True si l'ajout a été possible.
        """
        if position == -1:
            self.points_ids.append(point_id)
        else:
            self.points_ids.insert(position, point_id)
        return True

    def calculer_distance(self, graphe) -> float:
        """
        Calcule la longueur totale du trajet en parcourant les points dans l'ordre du graphe.
        Utilise soit une matrice de distances pré-calculée, soit Dijkstra en direct.
        
        Args:
            graphe: Une instance de GrapheRoutier (Niveau 1).
            
        Returns:
            float: La distance totale cumulée.
        """
        if not self.points_ids:
            return 0.0
        
        distance = 0.0
        # Parcours de la séquence de points : [P0, P1, ..., Pn]
        for i in range(len(self.points_ids) - 1):
            id_a = self.points_ids[i]
            id_b = self.points_ids[i+1]
            
            # Utilisation de la matrice des distances pré-calculée si disponible (plus performant)
            if hasattr(graphe, 'matrice'):
                d = graphe.matrice[id_a][id_b]
            else:
                # Calcul à la volée via l'algorithme de Niveau 1
                d, _ = graphe.plus_court_chemin(id_a, id_b)
            
            distance += d
        return distance

    def to_dict(self):
        """Convertit l'objet Tournee en dictionnaire pour l'export JSON."""
        return {
            "camion_id": self.camion_id,
            "points_ordre": self.points_ids,
            "heure_depart": str(self.heure_depart) if self.heure_depart else None,
            "heure_retour": str(self.heure_retour) if self.heure_retour else None
        }
