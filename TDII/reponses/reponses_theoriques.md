---

## Activité 6 : Recherche Locale et Méta-heuristiques

### Travail Dirigé 6.1 : Analyse de Convergence

#### Exercice 6.1.1 : Recuit simulé (Simulated Annealing)

1.  **Fonction de voisinage (2-opt swap) :** Consiste à inverser l'ordre d'un segment du tour. C'est le voisinage standard pour le TSP car il décroise les arêtes sans briser la structure du cycle hamiltonien.
2.  **Fonction de décroissance de température :** Généralement géométrique : $T_{k+1} = \alpha T_k$ avec $0.8 \le \alpha \le 0.99$. Permet de passer d'une exploration large (température haute) à une exploitation intense (température basse).
3.  **Impact des paramètres :**
    *   $\alpha$ trop petit -> convergence prématurée vers un minimum local.
    *   $\alpha$ trop grand -> temps de calcul excessif.
    *   Température initiale trop basse -> se comporte comme une simple descente de gradient.
4.  **Comparaison avec descente de gradient :** La descente de gradient s'arrête dès qu'elle rencontre un minimum local (elle n'accepte que les améliorations). Le recuit simulé peut "remonter" une pente avec une probabilité $P = e^{-\Delta E / T}$ pour s'échapper des minima locaux.

#### Exercice 6.1.2 : Algorithmes génétiques

1.  **Représentation des chromosomes :** Pour le sac à dos, un vecteur binaire de taille $n$ (1 si l'objet est pris, 0 sinon).
2.  **Opérateurs :**
    *   **Croisement (Crossover) :** Mélange les gènes de deux parents (ex: point de coupure unique).
    *   **Mutation :** Inverse un bit aléatoirement pour maintenir la diversité génétique.
3.  **Taille de population :** Trop petite -> perte de diversité et convergence prématurée (dérive génétique). Trop grande -> trop lente.
4.  **Diversité génétique :** Cruciale pour explorer différentes zones de l'espace de recherche. Sans elle, la population devient uniforme et l'évolution s'arrête.

---

### Travail Pratique 6.2 : Framework de Méta-heuristiques

#### Réponses aux tâches :

1.  **Implémentation :** (Voir `tp6_framework_metaheuristiques.py`).
2.  **Analyse de la robustesse :** La robustesse est mesurée par l'écart-type sur plusieurs runs. Les méta-heuristiques étant stochastiques, elles nécessitent souvent plusieurs exécutions pour garantir une solution de qualité.
3.  **Compromis Temps/Qualité :** Le recuit simulé est souvent plus rapide à converger vers une bonne solution, tandis que les algorithmes génétiques peuvent explorer plus largement mais nécessitent plus de réglages de paramètres.
