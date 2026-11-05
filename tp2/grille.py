# TP2 - Partie A : classe Grille du Morpion.
# x = numéro de ligne, y = numéro de colonne, de 0 à 2.

TAILLE = 3
VIDE = " "
SYMBOLES = ("X", "O")

class Grille:
    #Grille 3x3 stockée sous forme de liste de listes.

    def __init__(self):
        # Une nouvelle liste par ligne : [[VIDE] * 3] * 3 créerait 3 fois
        # la MÊME ligne, et jouer dans une case la remplirait sur toutes les lignes.
        self.cases = [[VIDE] * TAILLE for _ in range(TAILLE)]

    def afficher(self):
        #Affiche la grille, lignes séparées par des tirets.
        lignes = [" " + " | ".join(ligne) for ligne in self.cases]
        separateur = "\n" + "-" * 11 + "\n"
        print(separateur.join(lignes))

    def est_dans_grille(self, x, y):
        #Vrai si (x, y) désigne une case existante.
        # On vérifie aussi le type : jouer("a", 0) ne doit pas faire planter.
        # Et on refuse les négatifs : en Python, cases[-1] existe (dernière ligne) !
        return (isinstance(x, int) and isinstance(y, int)
                and 0 <= x < TAILLE and 0 <= y < TAILLE)

    def est_libre(self, x, y):
        #Vrai si la case existe et n'est pas encore occupée.
        return self.est_dans_grille(x, y) and self.cases[x][y] == VIDE

    def jouer(self, x, y, joueur):
        #Place le symbole du joueur en (x, y).

        if joueur not in SYMBOLES or not self.est_libre(x, y):
            return False
        self.cases[x][y] = joueur
        return True

    def est_gagnant(self, j):
        #Vrai si le joueur j a aligné 3 symboles (ligne, colonne ou diagonale).
        c = self.cases
        lignes = [ligne for ligne in c]
        colonnes = [[c[x][y] for x in range(TAILLE)] for y in range(TAILLE)]
        diagonales = [[c[i][i] for i in range(TAILLE)],
                      [c[i][TAILLE - 1 - i] for i in range(TAILLE)]]

        # any() s'arrête dès qu'un alignement gagnant est trouvé.
        return any(all(case == j for case in alignement)
                   for alignement in lignes + colonnes + diagonales)

    def est_plein(self):
        #Vrai s'il ne reste aucune case libre.
        return all(case != VIDE for ligne in self.cases for case in ligne)

    def cases_libres(self):
        #Liste des coordonnées (x, y) libres (servira aux joueurs IA).
        return [(x, y) for x in range(TAILLE) for y in range(TAILLE)
                if self.cases[x][y] == VIDE]


def tester():
    #Rejoue le jeu d'essai de l'énoncé ; s'arrête sur une erreur si un test échoue.
    g = Grille()
    assert g.jouer(0, 0, "X")
    assert g.jouer(0, 1, "O")
    assert g.jouer(1, 1, "X")
    g.afficher()

    assert not g.jouer(0, 0, "O"), "case occupée : doit être refusé"
    assert not g.jouer(3, 0, "O"), "hors grille : doit être refusé"
    assert not g.jouer(-1, 0, "O"), "x négatif : doit être refusé"
    assert not g.jouer("a", 0, "O"), "coordonnée non entière : doit être refusé"
    assert not g.jouer(2, 0, "Z"), "symbole inconnu : doit être refusé"

    assert not g.est_gagnant("X")
    assert g.jouer(2, 2, "X")
    assert g.est_gagnant("X")
    assert not g.est_gagnant("O")

    # Grille pleine sans gagnant (match nul)
    nul = Grille()
    for x, ligne in enumerate(["XOX", "XOO", "OXX"]):
        for y, symbole in enumerate(ligne):
            nul.jouer(x, y, symbole)
    assert nul.est_plein()
    assert not nul.est_gagnant("X") and not nul.est_gagnant("O")

    print("\nTous les tests de la Partie A passent.")


if __name__ == "__main__":
    tester()
