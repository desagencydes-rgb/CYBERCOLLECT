"""
Level 4 API – VRP Optimization (Nearest Neighbor + 2-opt/Tabu Search)
Returns optimized truck routes with convergence data for animated path drawing.
"""
import sys
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from niveau1.src.graphe_routier import GrapheRoutier
from niveau1.src.point_collecte import PointCollecte
from niveau2.src.camion import Camion
from niveau4.src.optimiseur_vrp import OptimiseurVRP

router = APIRouter()

# Default network (same as Level 1 for consistency)
DEFAULT_POINTS = [
    {"id": 0, "x": 0, "y": 0, "nom": "Dépôt Central", "type": "depot"},
    {"id": 1, "x": 2, "y": 3, "nom": "Zone A"},
    {"id": 2, "x": 5, "y": 1, "nom": "Zone B"},
    {"id": 3, "x": 7, "y": 4, "nom": "Zone C"},
    {"id": 4, "x": 3, "y": 7, "nom": "Zone D"},
    {"id": 5, "x": 8, "y": 6, "nom": "Zone E"},
    {"id": 6, "x": 1, "y": 5, "nom": "Zone F"},
    {"id": 7, "x": 6, "y": 8, "nom": "Zone G"},
    {"id": 8, "x": 9, "y": 2, "nom": "Zone H"},
]

DEFAULT_CAMIONS = [
    {"id": 1, "capacite": 500, "cout_fixe": 200, "zones_accessibles": [1, 2, 3, 4, 5]},
    {"id": 2, "capacite": 400, "cout_fixe": 180, "zones_accessibles": [1, 2, 3, 4, 5]},
    {"id": 3, "capacite": 600, "cout_fixe": 220, "zones_accessibles": [1, 2, 3, 4, 5]},
]
DEFAULT_CONNEXIONS = [
    {"depart": 0, "arrivee": 1, "distance": 3.6},
    {"depart": 0, "arrivee": 6, "distance": 5.1},
    {"depart": 1, "arrivee": 2, "distance": 3.2},
    {"depart": 1, "arrivee": 4, "distance": 4.1},
    {"depart": 2, "arrivee": 3, "distance": 3.6},
    {"depart": 2, "arrivee": 8, "distance": 4.1},
    {"depart": 3, "arrivee": 5, "distance": 2.8},
    {"depart": 3, "arrivee": 7, "distance": 4.1},
    {"depart": 4, "arrivee": 6, "distance": 2.2},
    {"depart": 4, "arrivee": 7, "distance": 3.6},
    {"depart": 5, "arrivee": 7, "distance": 2.8},
    {"depart": 5, "arrivee": 8, "distance": 4.1},
    {"depart": 6, "arrivee": 0, "distance": 5.1},
]


class Level4Input(BaseModel):
    nombre_camions: Optional[int] = 3


@router.post("/run")
def run_level4(body: Level4Input = None):
    nb_camions = body.nombre_camions if body and body.nombre_camions else 3

    graphe = GrapheRoutier()
    points_dict = {}

    for p in DEFAULT_POINTS:
        pt = PointCollecte(p["id"], p["x"], p["y"], p.get("nom", ""))
        graphe.ajouter_sommet(pt)
        points_dict[p["id"]] = pt

    for c in DEFAULT_CONNEXIONS:
        graphe.ajouter_arete(c["depart"], c["arrivee"], c["distance"])

    graphe.matrice_distances()
    camions = [Camion(i + 1, 1000, 100) for i in range(nb_camions)]

    optimiseur = OptimiseurVRP(graphe, camions, points_dict)

    # Phase 1: nearest-neighbor construction
    tournees_init = optimiseur.construire_solution_initiale()
    dist_init = sum(t.calculer_distance(graphe) for t in tournees_init)

    # Phase 2: Tabu / 2-opt improvement
    tournees_opt = optimiseur.recherche_tabou()
    dist_opt = sum(t.calculer_distance(graphe) for t in tournees_opt)

    routes_output = []
    for t in tournees_opt:
        route_nodes = []
        for pid in t.points_ids:
            if pid in points_dict:
                pt = points_dict[pid]
                route_nodes.append({"id": pid, "x": pt.x, "y": pt.y, "nom": pt.nom})
        routes_output.append({
            "camion_id": t.camion_id,
            "sequence": t.points_ids,
            "nodes": route_nodes,
            "distance": round(t.calculer_distance(graphe), 2),
        })

    return {
        "routes": routes_output,
        "nodes": DEFAULT_POINTS,
        "edges": DEFAULT_CONNEXIONS,
        "performance": {
            "distance_initiale": round(dist_init, 2),
            "distance_optimisee": round(dist_opt, 2),
            "amelioration": round(dist_init - dist_opt, 2),
            "amelioration_pct": round((dist_init - dist_opt) / dist_init * 100, 1) if dist_init > 0 else 0,
            "nb_camions": nb_camions,
            "algorithm": "Nearest Neighbor + Tabu Search (2-opt)"
        }
    }
