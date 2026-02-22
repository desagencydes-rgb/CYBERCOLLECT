"""
Définit la classe PointCollecte, représentant un sommet dans le réseau de collecte.
"""
from commun.outils_math import distance_euclidienne

class PointCollecte:
    """
    Représente un point géographique sur le réseau (dépôt ou point de collecte).
    """
    def __init__(self, id_point: int, x: float, y: float, nom: str = ""):
        """
        Initialise un nouveau point de collecte.
        
        Args:
            id_point (int): Identifiant unique du point.
            x (float): Coordonnée X.
            y (float): Coordonnée Y.
            nom (str): Nom facultatif pour le point.
        """
        self.id = id_point
        self.x = x
        self.y = y
        self.nom = nom

    def distance_vers(self, autre_point) -> float:
        """
        Calcule la distance euclidienne directe vers un autre point.
        
        Args:
            autre_point (PointCollecte): Le point de destination.
            
        Returns:
            float: La distance à vol d'oiseau.
        """
        return distance_euclidienne(self, autre_point)

    def to_dict(self):
        """Convertit l'objet en dictionnaire pour la sérialisation JSON."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "nom": self.nom
        }
    
    @staticmethod
    def from_dict(data):
        """Crée une instance de PointCollecte à partir d'un dictionnaire."""
        return PointCollecte(data["id"], data["x"], data["y"], data.get("nom", ""))

    def __repr__(self):
        return f"PointCollecte(id={self.id}, x={self.x}, y={self.y}, nom='{self.nom}')"
