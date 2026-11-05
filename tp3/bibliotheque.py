

from modeles import Livre, Utilisateur
class Bibliotheque:

    def __init__(self):
        self.livres = {}        # titre -> Livre
        self.utilisateurs = {}  # nom -> Utilisateur

    # ------------------------------------------------------------------ ajouts
    def ajouter_livre(self, livre):
        # Le titre sert de clé : deux livres ne peuvent pas avoir le même titre.
        if livre.titre in self.livres:
            return False, f"Le livre « {livre.titre} » existe déjà."
        self.livres[livre.titre] = livre
        return True, f"Livre « {livre.titre} » ajouté."

    def ajouter_utilisateur(self, utilisateur):
        if utilisateur.nom in self.utilisateurs:
            return False, f"L'utilisateur {utilisateur.nom} existe déjà."
        self.utilisateurs[utilisateur.nom] = utilisateur
        return True, f"Utilisateur {utilisateur.nom} ajouté."

    # --------------------------------------------------------- emprunt / retour
    def _trouver(self, nom, titre):
        # Cherche l'utilisateur et le livre ; renvoie (utilisateur, livre, erreur).
        # dict.get() renvoie None au lieu de lever KeyError si la clé n'existe pas.
        utilisateur = self.utilisateurs.get(nom)
        livre = self.livres.get(titre)
        if utilisateur is None:
            return None, None, f"Utilisateur inconnu : {nom}"
        if livre is None:
            return None, None, f"Livre inconnu : {titre}"
        return utilisateur, livre, None

    def emprunter(self, nom, titre):
        utilisateur, livre, erreur = self._trouver(nom, titre)
        if erreur:
            return False, erreur
        if not utilisateur.emprunter_livre(livre):
            return False, f"« {titre} » est déjà emprunté par {livre.emprunteur}."
        return True, f"{nom} emprunte « {titre} »."

    def rendre(self, nom, titre):
        utilisateur, livre, erreur = self._trouver(nom, titre)
        if erreur:
            return False, erreur
        if not utilisateur.rendre_livre(livre):
            if livre.disponible:
                return False, f"« {titre} » n'est pas emprunté."
            return False, f"« {titre} » a été emprunté par {livre.emprunteur}, pas par {nom}."
        return True, f"{nom} rend « {titre} »."

    # ---------------------------------------------------------------- affichage
    def afficher_livres(self):
        if not self.livres:
            print("La bibliothèque est vide.")
            return
        disponibles = [l for l in self.livres.values() if l.disponible]
        empruntes = [l for l in self.livres.values() if not l.disponible]

        print(f"Disponibles ({len(disponibles)}) :")
        for livre in disponibles:
            print(f"  - {livre.titre}, {livre.auteur} ({livre.annee})")
        print(f"Empruntés ({len(empruntes)}) :")
        for livre in empruntes:
            print(f"  - {livre.titre}, {livre.auteur} ({livre.annee}) -> {livre.emprunteur}")

    # ------------------------------------------------------- Défi 1 : stats
    def stats(self):
        # Nombre de livres, nombre d'emprunts en cours, emprunts par utilisateur.
        # On ne garde que les utilisateurs qui ont au moins un emprunt.
        par_utilisateur = {nom: len(u.emprunts)
                           for nom, u in self.utilisateurs.items() if u.emprunts}
        return {
            "total": len(self.livres),
            "empruntes": sum(par_utilisateur.values()),
            "par_utilisateur": par_utilisateur,
        }


def tester():
    b = Bibliotheque()
    assert b.ajouter_livre(Livre("1984", "Orwell", 1949))[0]
    assert b.ajouter_livre(Livre("Dune", "Herbert", 1965))[0]
    assert not b.ajouter_livre(Livre("1984", "Orwell", 1949))[0]   # doublon
    assert b.ajouter_utilisateur(Utilisateur("Ana"))[0]
    assert b.ajouter_utilisateur(Utilisateur("Léo"))[0]
    assert not b.ajouter_utilisateur(Utilisateur("Ana"))[0]        # doublon

    # Jeu d'essai : nom inconnu, titre inconnu, livre déjà emprunté -> échec sans plantage
    cas_en_echec = [
        b.emprunter("Inconnu", "1984"),
        b.emprunter("Ana", "Titre inconnu"),
    ]
    assert b.emprunter("Ana", "1984")[0]
    cas_en_echec.append(b.emprunter("Léo", "1984"))              # déjà emprunté
    cas_en_echec.append(b.rendre("Léo", "1984"))                 # rendu par un autre
    cas_en_echec.append(b.rendre("Ana", "Dune"))                 # pas emprunté
    for succes, message in cas_en_echec:
        assert not succes
        print("Refusé :", message)

    print()
    b.afficher_livres()

    assert b.rendre("Ana", "1984")[0]
    assert b.livres["1984"].disponible
    assert b.utilisateurs["Ana"].emprunts == []

    print("\nTous les tests de la Partie B passent.")

    # Défi 1 : 3 livres, Ana en emprunte 2
    b.ajouter_livre(Livre("Fondation", "Asimov", 1951))
    b.emprunter("Ana", "1984")
    b.emprunter("Ana", "Dune")
    assert b.stats() == {"total": 3, "empruntes": 2, "par_utilisateur": {"Ana": 2}}
    print("Stats :", b.stats())
    print("Tous les tests du Défi 1 passent.")


if __name__ == "__main__":
    tester()
