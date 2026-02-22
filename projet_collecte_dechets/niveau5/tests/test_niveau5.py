import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from niveau5.src.simulation import CapteurIoT, SimulateurTempsReel
from niveau5.src.optimiseur_mo import OptimiseurMultiObjectif
from niveau2.src.zone import Zone
from niveau2.src.camion import Camion
from niveau1.src.graphe_routier import GrapheRoutier
from niveau1.src.point_collecte import PointCollecte

class TestNiveau5(unittest.TestCase):
    def setUp(self):
        self.z1 = Zone(1, [], 80, 0, 0) # 80% rempli
        self.c1 = Camion(1, 100, 10 )
        self.sim = SimulateurTempsReel([self.z1], [self.c1])

    def test_5_1_capteur_iot(self):
        c = CapteurIoT(1, "niveau")
        val = c.mesurer()
        self.assertTrue(0 <= val <= 100)

    def test_5_2_simulation_alerte(self):
        # Force high fill rate to trigger alert
        self.sim.capteurs_zones[1].valeur = 95
        events = self.sim.executer_pas_de_temps(15)
        
        found_alert = False
        for e in events:
            if e["type"] == "ALERTE_REMPLISSAGE" and e["zone_id"] == 1:
                found_alert = True
                break
        self.assertTrue(found_alert)

    def test_5_3_optimiseur_mo(self):
        # Setup minimal VRP context
        g = GrapheRoutier()
        p0 = PointCollecte(0, 0, 0)
        p1 = PointCollecte(1, 10, 0)
        g.ajouter_sommet(p0)
        g.ajouter_sommet(p1)
        g.ajouter_arete(0, 1, 10)
        g.matrice_distances()
        
        opt = OptimiseurMultiObjectif(g, [self.c1], {1: p1})
        tournees = opt.optimisation_bi_critere()
        
        # Verify result structure
        self.assertTrue(len(tournees) > 0)
        eval_res = opt.evaluer_solution(tournees)
        self.assertIn("distance_totale", eval_res)
        self.assertIn("ecart_charge", eval_res)

if __name__ == '__main__':
    unittest.main()
