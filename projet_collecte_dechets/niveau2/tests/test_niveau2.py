import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from niveau2.src.camion import Camion
from niveau2.src.zone import Zone
from niveau2.src.affectateur_biparti import AffectateurBiparti

class TestNiveau2(unittest.TestCase):
    def setUp(self):
        self.c1 = Camion(1, 100, 10, [1, 2])
        self.c2 = Camion(2, 100, 10, [2, 3])
        self.z1 = Zone(1, [], 40, 0, 0)
        self.z2 = Zone(2, [], 40, 0, 0)
        self.z3 = Zone(3, [], 40, 0, 0)
        
        self.camions = [self.c1, self.c2]
        self.zones = [self.z1, self.z2, self.z3]
        self.affectateur = AffectateurBiparti(self.camions, self.zones)

    def test_2_1_affectation_simple(self):
        # z1 -> c1 (only choice)
        # z3 -> c2 (only choice)
        # z2 -> c1 or c2
        resultats = self.affectateur.affectation_gloutonne()
        
        self.assertIn(1, resultats[1]) # c1 has z1
        self.assertIn(3, resultats[2]) # c2 has z3
        # z2 assigned to one of them
        assigned_z2 = (2 in resultats[1]) or (2 in resultats[2])
        self.assertTrue(assigned_z2)

    def test_2_2_capacite(self):
        # c1 cap 100. z1(40) + z2(40) = 80 <= 100. OK.
        # Reduce cap c1 to 50
        self.c1.capacite = 50
        resultats = self.affectateur.affectation_gloutonne()
        # c1 can take z1 (40) but not z2 (40 more -> 80 > 50)
        # c2 should take z2 if possible (cap 100, z3=40 + z2=40 = 80 <= 100) OK
        
        charge_c1 = sum(self.zones[z-1].volume_estime for z in resultats[1])
        self.assertTrue(charge_c1 <= 50)

    def test_2_3_inaccessible(self):
        # z4 inaccessible by any
        z4 = Zone(4, [], 10, 0, 0)
        self.zones.append(z4)
        self.affectateur = AffectateurBiparti(self.camions, self.zones)
        
        resultats = self.affectateur.affectation_gloutonne()
        # z4 not in any list
        found = False
        for z_ids in resultats.values():
            if 4 in z_ids: found = True
        self.assertFalse(found)

    def test_2_4_equilibrage(self):
        # c1 cap 200, c2 cap 200
        # z1=10, z2=10, z3=10, z4=10
        # Forcing a situation where greedy might fail to balance perfectly if order is unlucky
        # But here we just test that the method runs and preserves validity
        
        c3 = Camion(3, 100, 10, [1,2,3,4])
        c4 = Camion(4, 100, 10, [1,2,3,4])
        z_small = [Zone(i, [], 10, 0, 0) for i in range(1, 5)]
        
        aff = AffectateurBiparti([c3, c4], z_small)
        res = aff.affectation_gloutonne()
        
        # Manually unbalance
        res[3] = [1, 2, 3] # 30
        res[4] = [4]       # 10
        
        balanced = aff.equilibrage_charges(res)
        
        # Should have moved one from c3 to c4 -> 20 vs 20
        len_c3 = len(balanced[3])
        len_c4 = len(balanced[4])
        
        self.assertEqual(len_c3, 2)
        self.assertEqual(len_c4, 2)

if __name__ == '__main__':
    unittest.main()
