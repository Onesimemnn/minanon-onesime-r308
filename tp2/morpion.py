"""
TP2 - Partie C : jeu de Morpion complet.

Boucle de jeu : les joueurs jouent chacun leur tour, chaque coup est validé
par la Grille, et la partie s'arrête sur une victoire ou un match nul.

Bonus réalisés : score sur plusieurs parties, mode 2 humains (et IA contre IA).
"""

from grille import Grille
from joueurs import JoueurHumain, JoueurIA


def jouer_partie(joueur_x, joueur_o, afficher=True):
    """Joue une partie complète.

    Renvoie le joueur gagnant, ou None en cas de match nul.
    `afficher=False` permet d'enchaîner des parties IA sans rien imprimer.
    """
    grille = Grille()
    # Chaque entrée associe un joueur à son symbole ; X commence.
    tours = [(joueur_x, "X"), (joueur_o, "O")]
    tour = 0

    while True:
        joueur, symbole = tours[tour % 2]
        if afficher:
            print()
            grille.afficher()

        x, y = joueur.prochain_coup(grille.cases, symbole)

        if not grille.jouer(x, y, symbole):
            # Coup refusé : message, puis le MÊME joueur rejoue (tour inchangé).
            if not grille.est_dans_grille(x, y):
                print(f"Coup ({x}, {y}) hors grille : lignes et colonnes de 0 à 2.")
            else:
                print(f"La case ({x}, {y}) est déjà occupée.")
            continue

        if afficher:
            print(f"{joueur} ({symbole}) joue en ({x}, {y}).")

        # On teste la victoire avant le nul : un dernier coup peut remplir
        # la grille ET faire gagner.
        if grille.est_gagnant(symbole):
            if afficher:
                print()
                grille.afficher()
                print(f"\n{joueur} ({symbole}) a gagné !")
            return joueur
        if grille.est_plein():
            if afficher:
                print()
                grille.afficher()
                print("\nMatch nul !")
            return None

        tour += 1


def choisir_joueurs():
    """Menu de départ : renvoie (joueur_x, joueur_o) selon le mode choisi."""
    print("1. Humain contre IA")
    print("2. Humain contre humain")
    print("3. IA contre IA")
    while True:
        choix = input("Votre choix (1-3) : ").strip()
        if choix == "1":
            return JoueurHumain(input("Votre nom : ").strip() or "Joueur"), JoueurIA("IA")
        if choix == "2":
            nom_x = input("Nom du joueur X : ").strip() or "Joueur X"
            nom_o = input("Nom du joueur O : ").strip() or "Joueur O"
            return JoueurHumain(nom_x), JoueurHumain(nom_o)
        if choix == "3":
            return JoueurIA("IA 1"), JoueurIA("IA 2")
        print("Choix invalide.")


def afficher_score(score):
    print("\n--- Score ---")
    for nom, points in score.items():
        print(f"{nom} : {points}")


def main():
    print("=== Morpion ===")
    try:
        joueur_x, joueur_o = choisir_joueurs()
        # Bonus : score sur plusieurs parties (ordre d'affichage fixe).
        score = {joueur_x.nom: 0, joueur_o.nom: 0, "Nuls": 0}

        while True:
            gagnant = jouer_partie(joueur_x, joueur_o)
            if gagnant is None:
                score["Nuls"] += 1
            else:
                score[gagnant.nom] += 1
            afficher_score(score)

            if input("\nRejouer ? (o/n) ").strip().lower() not in ("o", "oui"):
                break
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C / Ctrl+D : on quitte sans trace d'erreur.
        print()
    print("À bientôt !")


def tester():
    """Jeu d'essai de l'énoncé."""
    # IA contre IA, 20 parties : victoire ou nul à chaque fois, jamais de blocage.
    ia1, ia2 = JoueurIA("IA 1"), JoueurIA("IA 2")
    resultats = {"IA 1": 0, "IA 2": 0, "Nuls": 0}
    for _ in range(20):
        gagnant = jouer_partie(ia1, ia2, afficher=False)
        assert gagnant in (ia1, ia2, None)
        resultats["Nuls" if gagnant is None else gagnant.nom] += 1
    assert sum(resultats.values()) == 20
    print("20 parties IA contre IA :", resultats)

    # Coups invalides (occupé, x = 3, x = -1) : message, puis le même joueur rejoue.
    # X joue la colonne 0, O joue ailleurs : X gagne au 3e coup valide.
    coups_x = iter(["0 0", "1 0", "2 0"])
    coups_o = iter(["0 0", "3 0", "-1 0", "1 1", "2 2"])
    gagnant = jouer_partie(JoueurHumain("Ana", lire=lambda _: next(coups_x)),
                           JoueurHumain("Bob", lire=lambda _: next(coups_o)),
                           afficher=False)
    assert gagnant.nom == "Ana"
    print("Coups invalides : le même joueur rejoue, pas de plantage.")

    print("\nTous les tests de la Partie C passent.")


if __name__ == "__main__":
    import sys
    # « python morpion.py test » lance les tests, sinon on joue.
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        tester()
    else:
        main()
