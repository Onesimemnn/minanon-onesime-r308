class Livre:
    # Un livre de la bibliothèque. Il retient aussi QUI l'a emprunté :
    # utile pour la sauvegarde CSV (Partie C) et pour refuser qu'un autre
    # que l'emprunteur le rende (défi de la soutenance).

    def __init__(self, titre, auteur, annee):
        self.titre = titre.strip()
        self.auteur = auteur.strip()
        # int() lève ValueError si l'année n'est pas un nombre :
        # le menu (Partie D) attrapera l'erreur et affichera un message.
        self.annee = int(annee)
        self.disponible = True
        self.emprunteur = None  # nom de l'emprunteur, None si disponible

    def __str__(self):
        etat = "disponible" if self.disponible else f"emprunté par {self.emprunteur}"
        return f"« {self.titre} », {self.auteur} ({self.annee}) - {etat}"

    def afficher(self):
        print(self)

    def emprunter(self, nom):
        # Renvoie True si l'emprunt réussit, False si le livre est déjà pris.
        if not self.disponible:
            return False
        self.disponible = False
        self.emprunteur = nom
        return True

    def rendre(self):
        # Renvoie True si le livre était bien emprunté, False sinon.
        if self.disponible:
            return False
        self.disponible = True
        self.emprunteur = None
        return True


class Utilisateur:
    # Un lecteur et la liste des livres qu'il a actuellement empruntés.

    def __init__(self, nom):
        self.nom = nom.strip()
        self.emprunts = []  # liste d'objets Livre

    def emprunter_livre(self, livre):
        # On passe par livre.emprunter() : c'est le Livre qui sait s'il est libre.
        # On n'ajoute à la liste QUE si l'emprunt a réussi.
        if livre.emprunter(self.nom):
            self.emprunts.append(livre)
            return True
        return False

    def rendre_livre(self, livre):
        # Refuse si ce n'est pas cet utilisateur qui a le livre
        # (livre rendu par un autre que l'emprunteur).
        if livre not in self.emprunts:
            return False
        livre.rendre()
        self.emprunts.remove(livre)
        return True

    def afficher_emprunts(self):
        if not self.emprunts:
            print(f"{self.nom} n'a aucun emprunt.")
            return
        print(f"Emprunts de {self.nom} :")
        for livre in self.emprunts:
            print(f"  - {livre.titre} ({livre.auteur})")


def tester():
    # Jeu d'essai de l'énoncé
    l = Livre("1984", "Orwell", 1949)
    assert l.emprunter("Ana") is True
    assert l.emprunter("Léo") is False   # déjà emprunté
    assert l.emprunteur == "Ana"
    assert l.rendre() is True
    assert l.rendre() is False           # rendre un livre déjà disponible
    l.afficher()

    # Année non numérique : ValueError, que le menu attrapera
    try:
        Livre("Titre", "Auteur", "mille neuf cent")
        assert False, "aurait dû lever ValueError"
    except ValueError:
        pass

    # Utilisateurs
    ana, leo = Utilisateur("Ana"), Utilisateur("Léo")
    livre = Livre("Dune", "Herbert", "1965")  # l'année en texte est convertie
    assert ana.emprunter_livre(livre)
    assert not leo.emprunter_livre(livre)     # déjà pris par Ana
    assert leo.emprunts == []                 # rien ajouté chez Léo
    assert not leo.rendre_livre(livre)        # Léo ne peut pas rendre le livre d'Ana
    assert not livre.disponible               # ... et le livre reste emprunté
    ana.afficher_emprunts()
    assert ana.rendre_livre(livre)
    assert livre.disponible and ana.emprunts == []
    ana.afficher_emprunts()

    print("\nTous les tests de la Partie A passent.")


if __name__ == "__main__":
    tester()
