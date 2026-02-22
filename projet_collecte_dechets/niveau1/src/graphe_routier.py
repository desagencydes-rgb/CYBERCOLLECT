"""
Implémentation d'un graphe routier pour le calcul des distances et des plus courts chemins.
Utilise l'algorithme de Dijkstra (avec heapq) pour l'optimisation des parcours.
"""
import heapq
from niveau1.src.point_collecte import PointCollecte

class GrapheRoutier:
    """
    Classe gérant un réseau de points (sommets) et de routes (arêtes).
    Le graphe est considéré comme non-orienté par défaut.
    """
    def __init__(self):
        self.sommets = {}  # Stockage des instances PointCollecte {id: instance}
        self.aretes = {}   # Stockage des poids des arêtes {(id1, id2): poids}

    def ajouter_sommet(self, point: PointCollecte) -> None:
        """Ajoute un sommet (point de collecte) au graphe."""
        self.sommets[point.id] = point

    def ajouter_arete(self, id1: int, id2: int, distance: float = None) -> None:
        """
        Ajoute une arête bidirectionnelle entre deux sommets.
        
        Args:
            id1 (int): ID du premier sommet.
            id2 (int): ID du second sommet.
            distance (float): Poids de l'arête. Si None, calculé via distance euclidienne.
        """
        if id1 not in self.sommets or id2 not in self.sommets:
            raise ValueError("Les sommets doivent exister avant d'ajouter une arête.")
        
        if distance is None:
            distance = self.sommets[id1].distance_vers(self.sommets[id2])
        
        # Enregistrement des connexions dans les deux sens (réseau routier symétrique)
        self.aretes[(id1, id2)] = distance
        self.aretes[(id2, id1)] = distance

    def plus_court_chemin(self, depart: int, arrivee: int) -> tuple:
        """
        Calcule le plus court chemin entre deux sommets via l'algorithme de Dijkstra.
        
        Args:
            depart (int): ID du sommet de départ.
            arrivee (int): ID du sommet d'arrivée.
            
        Returns:
            tuple: (distance_totale, liste_ids_chemin). 
                   Retourne (inf, []) si aucune connexion n'existe.
        """
        if depart not in self.sommets or arrivee not in self.sommets:
            return float('inf'), []

        # Initialisation Dijkstra
        distances = {sommet: float('inf') for sommet in self.sommets}
        distances[depart] = 0
        predecesseurs = {sommet: None for sommet in self.sommets}
        pq = [(0, depart)]

        while pq:
            d_actuelle, u = heapq.heappop(pq)

            if d_actuelle > distances[u]:
                continue
            
            if u == arrivee:
                break

            for (id1, id2), poids in self.aretes.items():
                if id1 == u:
                    v = id2
                    nouvelle_dist = d_actuelle + poids
                    if nouvelle_dist < distances[v]:
                        distances[v] = nouvelle_dist
                        predecesseurs[v] = u
                        heapq.heappush(pq, (nouvelle_dist, v))
        
        # Reconstruction chemin
        if distances[arrivee] == float('inf'):
            return float('inf'), []
        
        chemin = []
        curr = arrivee
        while curr is not None:
            chemin.append(curr)
            curr = predecesseurs[curr]
        chemin.reverse()
        
        return distances[arrivee], chemin

    def matrice_distances(self) -> list:
        """
        Génère une matrice complète des distances (n x n) entre tous les sommets.
        
        Returns:
            list: Liste de listes contenant les distances n x n.
        """
        ids_tries = sorted(self.sommets.keys())
        n = len(ids_tries)
        matrice = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    matrice[i][j] = 0.0
                else:
                    dist, _ = self.plus_court_chemin(ids_tries[i], ids_tries[j])
                    matrice[i][j] = dist if dist != float('inf') else float('inf')
        return matrice
