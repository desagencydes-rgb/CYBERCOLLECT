"""
Level 1 API – Road Graph & Dijkstra Shortest Paths
Returns node positions, edges, and calculated shortest paths for Three.js rendering.
"""
import sys
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from niveau1.src.graphe_routier import GrapheRoutier
from niveau1.src.point_collecte import PointCollecte

router = APIRouter()

DEFAULT_INPUT = {
    "depot": {"id": 0, "x": 0, "y": 0, "nom": "Dépôt Central"},
    "points_collecte": [
        {"id": 1, "x": 2, "y": 3, "nom": "Zone A"},
        {"id": 2, "x": 5, "y": 1, "nom": "Zone B"},
        {"id": 3, "x": 7, "y": 4, "nom": "Zone C"},
        {"id": 4, "x": 3, "y": 7, "nom": "Zone D"},
        {"id": 5, "x": 8, "y": 6, "nom": "Zone E"},
        {"id": 6, "x": 1, "y": 5, "nom": "Zone F"},
        {"id": 7, "x": 6, "y": 8, "nom": "Zone G"},
        {"id": 8, "x": 9, "y": 2, "nom": "Zone H"},
    ],
    "connexions": [
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
    ],
}


class Level1Input(BaseModel):
    depot: Optional[dict] = None
    points_collecte: Optional[List[dict]] = None
    connexions: Optional[List[dict]] = None


@router.post("/run")
def run_level1(body: Level1Input = None):
    data = DEFAULT_INPUT.copy()
    if body:
        if body.depot:
            data["depot"] = body.depot
        if body.points_collecte:
            data["points_collecte"] = body.points_collecte
        if body.connexions:
            data["connexions"] = body.connexions

    graphe = GrapheRoutier()
    depot_data = data["depot"]
    depot = PointCollecte(depot_data["id"], depot_data["x"], depot_data["y"], depot_data.get("nom", "Dépôt"))
    graphe.ajouter_sommet(depot)

    nodes = [{"id": depot.id, "x": depot.x, "y": depot.y, "nom": depot.nom, "type": "depot"}]

    for pt in data["points_collecte"]:
        p = PointCollecte(pt["id"], pt["x"], pt["y"], pt.get("nom", ""))
        graphe.ajouter_sommet(p)
        nodes.append({"id": p.id, "x": p.x, "y": p.y, "nom": p.nom, "type": "collection"})

    edges = []
    for conn in data.get("connexions", []):
        graphe.ajouter_arete(conn["depart"], conn["arrivee"], conn.get("distance"))
        edges.append({"from": conn["depart"], "to": conn["arrivee"], "distance": conn.get("distance", 0)})

    matrice = graphe.matrice_distances()

    shortest_paths = []
    depot_id = depot.id
    for node in nodes:
        if node["id"] == depot_id:
            continue
        dist, path = graphe.plus_court_chemin(depot_id, node["id"])
        if dist != float("inf"):
            shortest_paths.append({
                "from": depot_id,
                "to": node["id"],
                "distance": round(dist, 2),
                "path": path
            })

    return {
        "nodes": nodes,
        "edges": edges,
        "shortest_paths": shortest_paths,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "max_distance": round(max((sp["distance"] for sp in shortest_paths), default=0), 2),
            "algorithm": "Dijkstra"
        }
    }
