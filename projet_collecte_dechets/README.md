# Projet d'Optimisation de Collecte de Déchets

Ce projet implémente un système modulaire et robuste d'optimisation de tournées de collecte de déchets. Il est structuré en 5 niveaux de complexité croissante, permettant d'aborder successivement les défis géographiques, logistiques, temporels et dynamiques de la gestion des déchets urbains.

## 🎯 Objectifs du Projet

- **Niveau 1 :** Poser les bases géographiques via un graphe routier et le calcul du plus court chemin (Dijkstra).
- **Niveau 2 :** Optimiser l'affectation spatiale des camions aux zones de collecte (Bin Packing / Heuristique Gloutonne).
- **Niveau 3 :** Intégrer les contraintes temporelles (Fenêtres horaires, congestion du trafic, pauses conducteurs).
- **Niveau 4 :** Résoudre le problème de tournées de véhicules (VRP) via des algorithmes d'amélioration locale comme le 2-opt.
- **Niveau 5 :** Simuler un système intelligent en temps réel capable de réagir aux données de capteurs IoT et aux imprévus.

## 📂 Structure du Projet

- `niveau1/`: Modélisation du réseau routier et algorithmique de base.
- `niveau2/`: Stratégies d'affectation et équilibrage de charge.
- `niveau3/`: Planification horaire et gestion de la congestion.
- `niveau4/`: Optimisation avancée des itinéraires (VRP).
- `niveau5/`: Simulation dynamique et dashboard de supervision.
- `commun/`: Utilitaires transverses pour les calculs mathématiques et la persistence JSON.

## ⚙️ Installation

1. **Prérequis :** Python 3.8 ou supérieur.
2. **Dépendances :** Le projet utilise principalement la bibliothèque standard. Pour les visualisations de Niveau 4, `matplotlib` est requis.
   ```bash
   pip install matplotlib
   ```

## 🚀 Guide d'Utilisation

Chaque niveau dispose de son propre point d'entrée dans le dossier `src/`.

| Niveau | Commande d'exécution | Description |
| :--- | :--- | :--- |
| **1** | `python niveau1/src/main_niveau1.py` | Calcule les distances entre les points. |
| **2** | `python niveau2/src/main_niveau2.py` | Assigne les camions aux zones. |
| **3** | `python niveau3/src/main_niveau3.py` | Génère le planning hebdomadaire. |
| **4** | `python niveau4/src/main_niveau4.py` | Optimise les tracés (Génère une carte). |
| **5** | `python niveau5/src/main_niveau5.py` | Lance la simulation temps réel. |

## 🧪 Tests et Qualité

Pour vérifier l'intégrité du système et valider les algorithmes après modification :
```bash
python -m unittest discover .
```

---
*Projet développé dans le cadre d'une optimisation de services urbains intelligents.*
