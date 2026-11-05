import random

from grille import TAILLE, VIDE, Grille


def cases_libres(tab):
    #Liste des coordonnées (x, y) des cases vides de tab.
    return [(x, y) for x in range(TAILLE) for y in range(TAILLE)
            if tab[x][y] == VIDE]


class Joueur:
    #Classe de base : définit ce que tout joueur doit savoir faire.

    def __init__(self, nom):
        self.nom = nom

    def prochain_coup(self, tab, symbole):
        # Chaque classe fille doit redéfinir cette méthode.
        raise NotImplementedError("prochain_coup() doit être redéfinie")

    def __str__(self):
        return self.nom


class JoueurHumain(Joueur):
    #Joueur qui saisit son coup au clavier.

    def __init__(self, nom, lire=input):
        super().__init__(nom)
        # lire = input par défaut ; les tests le remplacent par des réponses écrites.
        self.lire = lire

    def prochain_coup(self, tab, symbole):
        #Demande « ligne colonne » jusqu'à obtenir deux nombres entiers.
        while True:
            saisie = self.lire(f"{self.nom} ({symbole}), ligne et colonne (ex : 0 2) : ")
            # On accepte « 0 2 », « 0,2 » ou « 0;2 ».
            morceaux = saisie.replace(",", " ").replace(";", " ").split()
            if len(morceaux) == 2:
                try:
                    return int(morceaux[0]), int(morceaux[1])
                except ValueError:
                    pass
            print("Saisie invalide : tapez deux nombres, par exemple 1 2.")


class JoueurIA(Joueur):
    #Joueur qui choisit une case libre au hasard.

    def prochain_coup(self, tab, symbole):
        libres = cases_libres(tab)
        if not libres:
            raise ValueError("Aucune case libre : la partie aurait dû s'arrêter")
        return random.choice(libres)


class JoueurIAMalin(JoueurIA):
    #IA bonus : gagne si elle peut, sinon bloque l'adversaire, sinon hasard.

    def prochain_coup(self, tab, symbole):
        adversaire = "O" if symbole == "X" else "X"

        # 1. Coup gagnant pour moi ?  2. Sinon, coup gagnant à bloquer chez l'adversaire ?
        # L'ordre compte : gagner tout de suite vaut mieux que bloquer.
        for cible in (symbole, adversaire):
            coup = self.coup_gagnant(tab, cible)
            if coup is not None:
                return coup

        # 3. Sinon : coup au hasard, en réutilisant la méthode de la classe mère.
        return super().prochain_coup(tab, symbole)

    @staticmethod
    def coup_gagnant(tab, symbole):
        #Renvoie une case qui ferait gagner `symbole`, ou None s'il n'y en a pas.

        copie = Grille()
        copie.cases = [ligne[:] for ligne in tab]  # ligne[:] copie chaque ligne
        for x, y in cases_libres(tab):
            copie.cases[x][y] = symbole
            if copie.est_gagnant(symbole):
                return x, y
            copie.cases[x][y] = VIDE  # on annule le coup simulé
        return None


def tester():
    #Vérifie le comportement des deux types de joueurs.
    tab = [["X", "O", VIDE],
           [VIDE, "X", VIDE],
           [VIDE, VIDE, VIDE]]

    # L'IA ne choisit jamais une case occupée (testé 100 fois car c'est aléatoire).
    ia = JoueurIA("Ordi")
    for _ in range(100):
        x, y = ia.prochain_coup(tab, "O")
        assert tab[x][y] == VIDE

    # Grille pleine : l'IA signale le problème au lieu de boucler.
    pleine = [["X"] * 3 for _ in range(3)]
    try:
        ia.prochain_coup(pleine, "O")
        assert False, "aurait dû lever ValueError"
    except ValueError:
        pass

    # L'humain : les saisies mal formées sont redemandées.
    reponses = iter(["", "abc", "1", "1 2 3", "a b", "2,0"])
    humain = JoueurHumain("Ana", lire=lambda _: next(reponses))
    assert humain.prochain_coup(tab, "X") == (2, 0)

    # Le format est valide même hors grille : c'est Grille qui refusera.
    humain = JoueurHumain("Ana", lire=lambda _: "-1 3")
    assert humain.prochain_coup(tab, "X") == (-1, 3)

    # Polymorphisme : même appel pour les deux types.
    for joueur in (JoueurIA("IA"), JoueurHumain("Bob", lire=lambda _: "2 2")):
        assert isinstance(joueur, Joueur)
        assert joueur.prochain_coup(tab, "X") in cases_libres(tab)

    print("\nTous les tests de la Partie B passent.")

    # --- Bonus Jeu 1 : jeu d'essai de l'énoncé ---
    malin = JoueurIAMalin("Malin")
    bloque = [["X", "X", VIDE],
              [VIDE, "O", VIDE],
              [VIDE, VIDE, VIDE]]
    assert malin.prochain_coup(bloque, "O") == (0, 2), "doit bloquer"

    gagne = [["O", "O", VIDE],
             ["X", "X", VIDE],
             [VIDE, VIDE, VIDE]]
    # X menace aussi (1, 2), mais gagner passe avant bloquer.
    assert malin.prochain_coup(gagne, "O") == (0, 2), "doit gagner"

    # La simulation ne doit pas modifier la grille reçue.
    assert gagne == [["O", "O", VIDE], ["X", "X", VIDE], [VIDE, VIDE, VIDE]]

    # Aucune menace : coup au hasard, mais toujours sur une case libre.
    vide = [[VIDE] * 3 for _ in range(3)]
    assert malin.prochain_coup(vide, "O") in cases_libres(vide)

    print("Tous les tests du bonus IA malin passent.")


if __name__ == "__main__":
    tester()
