import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from niveau4.src.tournee import Tournee
from niveau4.src.optimiseur_vrp import OptimiseurVRP
from niveau1.src.point_collecte import PointCollecte
from niveau1.src.graphe_routier import GrapheRoutier
from niveau2.src.camion import Camion

class TestNiveau4(unittest.TestCase):
    def setUp(self):
        self.graphe = GrapheRoutier()
        # Square: 0(0,0), 1(0,1), 2(1,1), 3(1,0)
        p0 = PointCollecte(0, 0, 0)
        p1 = PointCollecte(1, 0, 1)
        p2 = PointCollecte(2, 1, 1)
        p3 = PointCollecte(3, 1, 0)
        
        self.points = {0:p0, 1:p1, 2:p2, 3:p3}
        for p in self.points.values():
            self.graphe.ajouter_sommet(p)
            
        # Add edges (complete graph usually expected for VRP dist matrix)
        # 0-1, 0-2, 0-3, 1-2, 1-3, 2-3
        # Euclidean calc automatic if we don't specify distance
        ids = list(self.points.keys())
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                self.graphe.ajouter_arete(ids[i], ids[j])
        
        self.graphe.matrice_distances()
        
        self.c1 = Camion(1, 100, 10)
        self.camions = [self.c1]

    def test_4_1_construction_heuristique(self):
        opt = OptimiseurVRP(self.graphe, self.camions, self.points)
        tournees = opt.construire_solution_initiale()
        
        self.assertTrue(len(tournees) > 0)
        t = tournees[0]
        # Should visit all 3 points + start/end 0
        self.assertIn(1, t.points_ids)
        self.assertIn(2, t.points_ids)
        self.assertIn(3, t.points_ids)
        self.assertEqual(t.points_ids[0], 0)
        self.assertEqual(t.points_ids[-1], 0)

    def test_4_2_2opt_amelioration(self):
        # Create a suboptimal tour: 0 -> 1 -> 3 -> 2 -> 0
        # Perimeter 1+1+1+1 = 4?
        # 0(0,0)->1(0,1) = 1
        # 1(0,1)->3(1,0) = sqrt(2) ~1.41
        # 3(1,0)->2(1,1) = 1
        # 2(1,1)->0(0,0) = sqrt(2) ~1.41
        # Total ~ 4.82
        
        # Optimal: 0->1->2->3->0 (Square perimeter = 4)
        
        t = Tournee(1, [0, 1, 3, 2, 0])
        opt = OptimiseurVRP(self.graphe, self.camions, self.points)
        
        dist_before = t.calculer_distance(self.graphe)
        print(f"Dist before: {dist_before}")
        opt.algorithme_2opt(t)
        dist_after = t.calculer_distance(self.graphe)
        print(f"Dist after: {dist_after}")
        print(f"Points: {t.points_ids}")
        
        self.assertTrue(dist_after < dist_before)
        self.assertAlmostEqual(dist_after, 4.0)

if __name__ == '__main__':
    unittest.main()
