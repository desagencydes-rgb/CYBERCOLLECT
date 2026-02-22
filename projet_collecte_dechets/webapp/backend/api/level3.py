"""
Level 3 API – Weekly Schedule Planning with Time Windows
Returns a weekly Gantt-style schedule grid with KPIs.
"""
import sys
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from niveau2.src.camion import Camion
from niveau2.src.zone import Zone
from niveau2.src.affectateur_biparti import AffectateurBiparti
from niveau3.src.creneau_horaire import CreneauHoraire
from niveau3.src.contrainte_temporelle import ContrainteTemporelle
from niveau3.src.planificateur_triparti import PlanificateurTriparti

router = APIRouter()

DEFAULT_CAMIONS = [
    {"id": 1, "capacite": 500, "cout_fixe": 200, "zones_accessibles": [1, 2, 3, 4, 5]},
    {"id": 2, "capacite": 400, "cout_fixe": 180, "zones_accessibles": [1, 2, 3, 4, 5]},
    {"id": 3, "capacite": 600, "cout_fixe": 220, "zones_accessibles": [1, 2, 3, 4, 5]},
]

DEFAULT_ZONES = [
    {"id": 1, "points": [1, 2], "volume_moyen": 120, "centre": {"x": 2, "y": 3}, "priorite": 2},
    {"id": 2, "points": [3],    "volume_moyen": 95,  "centre": {"x": 5, "y": 1}, "priorite": 1},
    {"id": 3, "points": [4, 5], "volume_moyen": 180, "centre": {"x": 7, "y": 4}, "priorite": 3},
    {"id": 4, "points": [6],    "volume_moyen": 75,  "centre": {"x": 3, "y": 7}, "priorite": 1},
    {"id": 5, "points": [7, 8], "volume_moyen": 210, "centre": {"x": 8, "y": 5}, "priorite": 2},
]

DEFAULT_CRENEAUX = [
    {"id": 1, "debut": "06:00", "fin": "12:00", "jour": "Lundi"},
    {"id": 2, "debut": "06:00", "fin": "12:00", "jour": "Mardi"},
    {"id": 3, "debut": "06:00", "fin": "12:00", "jour": "Mercredi"},
    {"id": 4, "debut": "06:00", "fin": "12:00", "jour": "Jeudi"},
    {"id": 5, "debut": "06:00", "fin": "12:00", "jour": "Vendredi"},
    {"id": 6, "debut": "13:00", "fin": "19:00", "jour": "Lundi"},
    {"id": 7, "debut": "13:00", "fin": "19:00", "jour": "Mercredi"},
    {"id": 8, "debut": "13:00", "fin": "19:00", "jour": "Vendredi"},
]

DEFAULT_CONTRAINTES = {
    "fenetres_zone": [
        {"zone_id": 1, "debut": "07:00", "fin": "11:00"},
        {"zone_id": 3, "debut": "08:00", "fin": "16:00"},
    ],
    "pauses_obligatoires": [
        {"camion_id": 1, "debut": "12:00", "duree": 1.0},
    ],
    "zones_interdites_nuit": [2, 4],
}


class Level3Input(BaseModel):
    camions: Optional[List[dict]] = None
    zones: Optional[List[dict]] = None
    creneaux: Optional[List[dict]] = None
    contraintes_temporelles: Optional[dict] = None


@router.post("/run")
def run_level3(body: Level3Input = None):
    camions_data = body.camions if body and body.camions else DEFAULT_CAMIONS
    zones_data = body.zones if body and body.zones else DEFAULT_ZONES
    creneaux_data = body.creneaux if body and body.creneaux else DEFAULT_CRENEAUX
    contraintes_data = body.contraintes_temporelles if body and body.contraintes_temporelles else DEFAULT_CONTRAINTES

    camions = [Camion.from_dict(c) for c in camions_data]
    zones = [Zone.from_dict(z) for z in zones_data]

    creneaux = [CreneauHoraire.from_dict(c) for c in creneaux_data]

    contraintes = ContrainteTemporelle()
    for fz in contraintes_data.get("fenetres_zone", []):
        contraintes.ajouter_fenetre_zone(fz["zone_id"], fz["debut"], fz["fin"])
    for pc in contraintes_data.get("pauses_obligatoires", []):
        contraintes.ajouter_pause_camion(pc["camion_id"], pc["debut"], pc["duree"])
    for zi in contraintes_data.get("zones_interdites_nuit", []):
        contraintes.zones_interdites_nuit.add(zi)

    affectateur = AffectateurBiparti(camions, zones)
    planificateur = PlanificateurTriparti(affectateur, contraintes, creneaux)
    plan = planificateur.generer_plan_optimal()
    stats = planificateur.evaluer_plan(plan)

    return {
        "schedule": plan,
        "kpis": stats,
        "creneaux": creneaux_data,
        "camions": camions_data,
        "stats": {
            "algorithm": "Tri-partite Planning",
            "jours_planifies": len(plan),
        }
    }
