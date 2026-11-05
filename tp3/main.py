from modeles import Livre, Utilisateur
from persistance import charger, sauvegarder

MENU = """
===== Bibliothèque =====
1. Ajouter un livre
2. Ajouter un utilisateur
3. Emprunter un livre
4. Rendre un livre
5. Afficher les livres
6. Quitter et sauvegarder
7. Statistiques"""


def demander(message):
    # input() + suppression des espaces autour de la saisie.
    return input(message).strip()


def ajouter_livre(biblio):
    titre = demander("Titre : ")
    auteur = demander("Auteur : ")
    annee = demander("Année : ")
    if not titre or not auteur:
        print("Le titre et l'auteur sont obligatoires.")
        return
    try:
        livre = Livre(titre, auteur, annee)
    except ValueError:
        # Jeu d'essai : année non numérique -> message, pas de plantage.
        print(f"Année invalide : « {annee} » n'est pas un nombre.")
        return
    print(biblio.ajouter_livre(livre)[1])


def ajouter_utilisateur(biblio):
    nom = demander("Nom : ")
    if not nom:
        print("Le nom est obligatoire.")
        return
    print(biblio.ajouter_utilisateur(Utilisateur(nom))[1])


def emprunter(biblio):
    nom = demander("Nom de l'utilisateur : ")
    titre = demander("Titre du livre : ")
    # La Bibliotheque renvoie (succes, message) : on affiche simplement le message.
    print(biblio.emprunter(nom, titre)[1])


def rendre(biblio):
    nom = demander("Nom de l'utilisateur : ")
    titre = demander("Titre du livre : ")
    print(biblio.rendre(nom, titre)[1])


def afficher_stats(biblio):
    # Défi 1 : option 7 du menu.
    s = biblio.stats()
    print(f"Livres : {s['total']} | Empruntés : {s['empruntes']}")
    for nom, nombre in s["par_utilisateur"].items():
        print(f"  - {nom} : {nombre} emprunt(s)")


# Associe chaque choix du menu à sa fonction : évite une longue suite de if/elif.
ACTIONS = {
    "1": ajouter_livre,
    "2": ajouter_utilisateur,
    "3": emprunter,
    "4": rendre,
    "5": lambda biblio: biblio.afficher_livres(),
    "7": afficher_stats,
}


def main():
    biblio = charger()
    try:
        while True:
            print(MENU)
            choix = demander("Votre choix : ")
            if choix == "6":
                break
            action = ACTIONS.get(choix)
            if action is None:
                print("Choix invalide.")  # jeu d'essai : choix « 9 »
            else:
                action(biblio)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C : on quitte proprement, et on sauvegarde quand même
        # pour ne pas perdre le travail de la session.
        print()

    if sauvegarder(biblio):
        print("Bibliothèque sauvegardée. À bientôt !")


if __name__ == "__main__":
    main()
