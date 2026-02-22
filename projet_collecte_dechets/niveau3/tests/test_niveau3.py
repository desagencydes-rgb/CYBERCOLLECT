import unittest
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from niveau3.src.creneau_horaire import CreneauHoraire
from niveau3.src.contrainte_temporelle import ContrainteTemporelle
from niveau3.src.planificateur_triparti import PlanificateurTriparti
from niveau2.src.camion import Camion
from niveau2.src.zone import Zone
from niveau2.src.affectateur_biparti import AffectateurBiparti

class TestNiveau3(unittest.TestCase):
    def setUp(self):
        self.c1 = Camion(1, 100, 10, [1])
        self.z1 = Zone(1, [], 10, 0, 0)
        self.affectateur = AffectateurBiparti([self.c1], [self.z1])
        
        self.creneau1 = CreneauHoraire(1, "08:00", "10:00", "lundi") # 2h
        self.creneau2 = CreneauHoraire(2, "10:00", "12:00", "lundi")
        self.contraintes = ContrainteTemporelle()

    def test_3_1_planification_simple(self):
        # 1 camion, 1 zone, 2 slots.
        # Should assign to first available slot if feasible
        planif = PlanificateurTriparti(self.affectateur, self.contraintes, [self.creneau1, self.creneau2])
        plan = planif.generer_plan_optimal()
        
        self.assertEqual(len(plan["lundi"]), 1)
        # Should pick creneau1 (first)
        self.assertEqual(plan["lundi"][0]["creneau"]["id"], 1)

    def test_3_2_chevauchement(self):
        c_overlap = CreneauHoraire(3, "09:00", "11:00", "lundi")
        self.assertTrue(self.creneau1.chevauche(c_overlap))
        self.assertFalse(self.creneau1.chevauche(self.creneau2)) # 10:00 boundary usually false if strict < > logic

    def test_3_3_fenetre_interdite(self):
        # Zone 1 open 06-09. Creneau 2 (10-12) should fail.
        self.contraintes.ajouter_fenetre_zone(1, "06:00", "09:00")
        
        planif = PlanificateurTriparti(self.affectateur, self.contraintes, [self.creneau2]) 
        plan = planif.generer_plan_optimal()
        
        # Should be empty for lundi
        self.assertEqual(len(plan["lundi"]), 0)

if __name__ == '__main__':
    unittest.main()
