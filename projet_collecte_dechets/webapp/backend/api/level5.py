"""
Level 5 API – Real-Time IoT Simulation
Returns simulation events, KPIs, and zone fill levels for the live dashboard.
"""
import sys
import random
from pathlib import Path
from fastapi import APIRouter
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from niveau2.src.camion import Camion
from niveau2.src.zone import Zone
from niveau5.src.simulation import SimulateurTempsReel
from niveau5.src.dashboard import DashboardTempsReel

router = APIRouter()

# Single shared simulation instance (reset-able)
_sim_state = {"simulator": None, "zones": None, "camions": None, "tick": 0}

DEFAULT_ZONES_DATA = [
    {"id": 1, "points": [1, 2], "volume_moyen": 120, "centre": {"x": 2, "y": 3}, "priorite": 2},
    {"id": 2, "points": [3],    "volume_moyen": 95,  "centre": {"x": 5, "y": 1}, "priorite": 1},
    {"id": 3, "points": [4, 5], "volume_moyen": 180, "centre": {"x": 7, "y": 4}, "priorite": 3},
    {"id": 4, "points": [6],    "volume_moyen": 75,  "centre": {"x": 3, "y": 7}, "priorite": 1},
    {"id": 5, "points": [7, 8], "volume_moyen": 210, "centre": {"x": 8, "y": 5}, "priorite": 2},
]

DEFAULT_CAMIONS_DATA = [
    {"id": 1, "capacite": 500, "cout_fixe": 200, "zones_accessibles": [1, 2, 3, 4, 5]},
    {"id": 2, "capacite": 400, "cout_fixe": 180, "zones_accessibles": [1, 2, 3, 4, 5]},
    {"id": 3, "capacite": 600, "cout_fixe": 220, "zones_accessibles": [1, 2, 3, 4, 5]},
]

ZONE_POSITIONS = {1: (2, 3), 2: (5, 1), 3: (7, 4), 4: (3, 7), 5: (8, 5)}


def _get_or_create_simulator():
    if _sim_state["simulator"] is None:
        zones = [Zone.from_dict(z) for z in DEFAULT_ZONES_DATA]
        camions = [Camion.from_dict(c) for c in DEFAULT_CAMIONS_DATA]
        _sim_state["simulator"] = SimulateurTempsReel(zones, camions)
        _sim_state["zones"] = zones
        _sim_state["camions"] = camions
        _sim_state["tick"] = 0
    return _sim_state["simulator"], _sim_state["zones"], _sim_state["camions"]


@router.post("/tick")
def tick_simulation():
    sim, zones, camions = _get_or_create_simulator()
    events = sim.executer_pas_de_temps(15)  # 15-minute step
    _sim_state["tick"] += 1

    # Build zone fill levels (simulated from events + random variation)
    zone_levels = []
    priorites = {1: 1, 2: 2, 3: 3, 4: 1, 5: 2}  # static zone priority lookup
    for z in zones:
        base_fill = min(95, 30 + _sim_state["tick"] * random.uniform(3, 8))
        is_critical = any(
            e.get("zone_id") == z.id and e.get("type") == "ALERTE_REMPLISSAGE"
            for e in events
        )
        zone_levels.append({
            "zone_id": z.id,
            "fill_percent": round(base_fill + (20 if is_critical else 0), 1),
            "alerte": is_critical,
            "x": z.centre[0] if hasattr(z, 'centre') else ZONE_POSITIONS.get(z.id, (0, 0))[0],
            "y": z.centre[1] if hasattr(z, 'centre') else ZONE_POSITIONS.get(z.id, (0, 0))[1],
            "priorite": priorites.get(z.id, 1),
        })

    nb_alerts = len([e for e in events if e.get("type") == "ALERTE_REMPLISSAGE"])
    efficacite = max(0, 100 - _sim_state["tick"] * 2 - nb_alerts * 5)

    return {
        "tick": _sim_state["tick"],
        "events": events,
        "zone_levels": zone_levels,
        "kpis": {
            "nb_alertes": nb_alerts,
            "zones_critiques": [z["zone_id"] for z in zone_levels if z["alerte"]],
            "efficacite_collecte": round(efficacite, 1),
            "temps_ecoule_min": _sim_state["tick"] * 15,
            "camions_actifs": len(camions),
        },
    }


@router.post("/reset")
def reset_simulation():
    _sim_state["simulator"] = None
    _sim_state["tick"] = 0
    return {"status": "reset", "message": "Simulation réinitialisée"}
