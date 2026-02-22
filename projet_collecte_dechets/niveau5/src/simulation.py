"""
Composant de simulation temps réel pour le système de collecte de déchets.
Simule des capteurs IoT sur les bacs et des événements imprévus (pannes).
"""
import random
import time

class CapteurIoT:
    """
    Simule un capteur connecté récoltant des données environnementales ou opérationnelles.
    """
    def __init__(self, id_capteur: int, type_capteur: str = "niveau"):
        """
        Initialise un capteur.
        
        Args:
            id_capteur (int): Identifiant du capteur.
            type_capteur (str): "niveau" pour remplissage des bacs, "trafic" pour congestion.
        """
        self.id = id_capteur
        self.type = type_capteur
        self.valeur = 0.0

    def mesurer(self) -> float:
        """
        Simule l'acquisition d'une nouvelle donnée.
        
        Returns:
            float: La valeur mesurée (0-100% ou vitesse).
        """
        if self.type == "niveau":
            self.valeur = random.uniform(0, 100) # % de remplissage du bac
        elif self.type == "trafic":
            self.valeur = random.uniform(20, 120) # km/h (simulation trafic)
        return self.valeur

class SimulateurTempsReel:
    """
    Moteur de simulation gérant l'évolution de l'état du système au fil du temps.
    """
    def __init__(self, zones: list, camions: list):
        """
        Initialise le simulateur.
        
        Args:
            zones (list): Liste des zones de collecte.
            camions (list): Flotte de camions en service.
        """
        self.zones = zones
        self.camions = camions
        # Chaque zone est équipée d'un capteur de niveau
        self.capteurs_zones = {z.id: CapteurIoT(z.id, "niveau") for z in zones}
        self.evenements = []

    def executer_pas_de_temps(self, duree_minutes: int = 15):
        """
        Avance la simulation d'un certain nombre de minutes.
        Génère des événements aléatoires (alertes de remplissage, pannes).
        
        Args:
            duree_minutes (int): Le saut temporel à simuler.
            
        Returns:
            list: Liste des nouveaux événements survenus.
        """
        nouveaux_evenements = []
        
        # 1. Mise à jour de l'état des zones (remplissage progressif)
        for z in self.zones:
            taux = random.uniform(0, 5) # Augmentation de 0 à 5% par pas
            capteur = self.capteurs_zones[z.id]
            niveau_actuel = capteur.valeur
            nouveau_niveau = min(100, niveau_actuel + taux)
            capteur.valeur = nouveau_niveau
            
            # Alerte si le bac est presque plein
            if nouveau_niveau > 90:
                nouveaux_evenements.append({
                    "type": "ALERTE_REMPLISSAGE",
                    "zone_id": z.id,
                    "niveau": nouveau_niveau,
                    "message": f"Zone {z.id} remplie à {nouveau_niveau:.1f}%"
                })
        
        # 2. Simulation d'événements aléatoires (ex: Panne Camion)
        if random.random() < 0.01: # Probabilité de 1%
            camion_panne = random.choice(self.camions)
            nouveaux_evenements.append({
                "type": "PANNE_CAMION",
                "camion_id": camion_panne.id,
                "message": f"Camion {camion_panne.id} en panne!"
            })
            
        self.evenements.extend(nouveaux_evenements)
        return nouveaux_evenements
