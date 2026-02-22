"""
Level 2 API – Truck-Zone Greedy Assignment + Load Balancing
Returns assignment map with utilization percentages for radial bar charts.
"""
import sys
import statistics
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from niveau2.src.camion import Camion
from niveau2.src.zone import Zone
from niveau2.src.affectateur_biparti import AffectateurBiparti

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


class Level2Input(BaseModel):
    camions: Optional[List[dict]] = None
    zones: Optional[List[dict]] = None


@router.post("/run")
def run_level2(body: Level2Input = None):
    camions_data = (body.camions if body and body.camions else DEFAULT_CAMIONS)
    zones_data = (body.zones if body and body.zones else DEFAULT_ZONES)

    camions = [Camion.from_dict(c) for c in camions_data]
    zones = [Zone.from_dict(z) for z in zones_data]

    affectateur = AffectateurBiparti(camions, zones)
    resultats = affectateur.affectation_gloutonne()
    resultats_final = affectateur.equilibrage_charges(resultats)

    zone_lookup = {z.id: z for z in zones}
    assignments = []
    loads = []

    for c in camions:
        z_ids = resultats_final.get(c.id, [])
        charge = sum(zone_lookup[zid].volume_estime for zid in z_ids if zid in zone_lookup)
        pct = round((charge / c.capacite) * 100, 1) if c.capacite > 0 else 0
        loads.append(charge)
        assignments.append({
            "camion_id": c.id,
            "capacite": c.capacite,
            "cout_fixe": c.cout_fixe,
            "zones_affectees": z_ids,
            "charge_totale": charge,
            "pourcentage_utilisation": pct,
            "zones_detail": [
                {
                    "id": zid,
                    "volume": zone_lookup[zid].volume_estime,
                    "priorite": next((zd.get("priorite", 1) for zd in zones_data if zd["id"] == zid), 1),
                    "x": zone_lookup[zid].centre[0],
                    "y": zone_lookup[zid].centre[1],
                }
                for zid in z_ids
                if zid in zone_lookup
            ],
        })

    return {
        "assignments": assignments,
        "zones": [
            {
                "id": z.id,
                "volume_estime": z.volume_estime,
                "priorite": next((zd.get("priorite", 1) for zd in zones_data if zd["id"] == z.id), 1),
                "x": z.centre[0],
                "y": z.centre[1],
            }
            for z in zones
        ],
        "stats": {
            "nombre_camions": len(camions),
            "charge_moyenne": round(statistics.mean(loads), 1) if loads else 0,
            "ecart_type": round(statistics.stdev(loads), 1) if len(loads) > 1 else 0,
            "utilisation_moyenne_pct": round(
                sum(a["pourcentage_utilisation"] for a in assignments) / len(assignments), 1
            ) if assignments else 0,
            "algorithm": "Greedy + Load Balancing"
        }
    }
