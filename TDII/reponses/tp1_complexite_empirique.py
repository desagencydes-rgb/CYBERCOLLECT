import time
import matplotlib.pyplot as plt
import numpy as np

def algorithme_quadratique(n):
    """Calcule une double somme pour simuler O(n^2)."""
    somme = 0
    for i in range(n):
        for j in range(n):
            somme += i * j
    return somme

def algorithme_lineaire(n):
    """Calcule une somme simple pour simuler O(n)."""
    somme = 0
    for i in range(n):
        somme += i
    return somme

def mesurer_temps():
    tailles = [10, 50, 100, 500, 1000, 2000]
    temps_quad = []
    temps_lin = []

    print(f"{'n':>10} | {'O(n) (s)':>15} | {'O(n^2) (s)':>15}")
    print("-" * 45)

    for n in tailles:
        # Mesure temps linéaire
        start = time.time()
        algorithme_lineaire(n)
        t_lin = time.time() - start
        temps_lin.append(t_lin)

        # Mesure temps quadratique
        start = time.time()
        algorithme_quadratique(n)
        t_quad = time.time() - start
        temps_quad.append(t_quad)
        
        print(f"{n:10} | {t_lin:15.6f} | {t_quad:15.6f}")

    # Affichage des résultats
    plt.figure(figsize=(10, 6))
    plt.plot(tailles, temps_quad, 'r-o', label='O(n^2) - Quadratique')
    plt.plot(tailles, temps_lin, 'b-o', label='O(n) - Linéaire')
    plt.xlabel('Taille de l\'entrée (n)')
    plt.ylabel('Temps d\'exécution (s)')
    plt.title('Croissance des temps d\'exécution : O(n) vs O(n^2)')
    plt.legend()
    plt.grid(True)
    
    # Analyse du rapport
    print("\nRapport des temps (quadratique / lineaire) :")
    for i in range(len(tailles)):
        rapport = temps_quad[i] / temps_lin[i] if temps_lin[i] > 0 else 0
        print(f"n={tailles[i]:4} : {rapport:.2f}")

    output_img = 'complexite_empirique.png'
    plt.savefig(output_img)
    print(f"\nGraphique sauvegardé sous : {output_img}")
    # plt.show() # Commenté pour éviter le blocage dans un environnement sans écran

if __name__ == "__main__":
    mesurer_temps()
