import csv
from pathlib import Path

from bibliotheque import Bibliotheque
from modeles import Livre, Utilisateur

DOSSIER = Path(__file__).parent
FICHIER_LIVRES = DOSSIER / "livres.csv"
FICHIER_UTILISATEURS = DOSSIER / "utilisateurs.csv"

COLONNES_LIVRES = ["titre", "auteur", "annee", "disponible", "emprunteur"]


def sauvegarder(biblio, fichier_livres=FICHIER_LIVRES,
                fichier_utilisateurs=FICHIER_UTILISATEURS):
    # Renvoie True si tout est écrit, False en cas d'erreur (sans planter).
    try:
        # newline="" est obligatoire avec csv : sinon, sous Windows,
        # une ligne vide apparaît entre chaque ligne du fichier.
        with open(fichier_livres, "w", newline="", encoding="utf-8") as f:
            ecrivain = csv.DictWriter(f, fieldnames=COLONNES_LIVRES)
            ecrivain.writeheader()
            for livre in biblio.livres.values():
                ecrivain.writerow({
                    "titre": livre.titre,
                    "auteur": livre.auteur,
                    "annee": livre.annee,
                    "disponible": "oui" if livre.disponible else "non",
                    "emprunteur": livre.emprunteur or "",
                })

        with open(fichier_utilisateurs, "w", newline="", encoding="utf-8") as f:
            ecrivain = csv.writer(f)
            ecrivain.writerow(["nom"])
            for nom in biblio.utilisateurs:
                ecrivain.writerow([nom])
    except OSError as erreur:  # droits, disque plein, fichier ouvert dans Excel...
        print(f"Erreur de sauvegarde : {erreur}")
        return False
    return True


def charger(fichier_livres=FICHIER_LIVRES,
            fichier_utilisateurs=FICHIER_UTILISATEURS):
    # Renvoie une nouvelle Bibliotheque. Fichier absent -> bibliothèque vide,
    # ligne abîmée -> ignorée avec un message. Jamais de plantage.
    biblio = Bibliotheque()
    _charger_utilisateurs(biblio, fichier_utilisateurs)
    _charger_livres(biblio, fichier_livres)
    return biblio


def _charger_utilisateurs(biblio, chemin):
    try:
        # utf-8-sig lit aussi un fichier réenregistré par Excel (qui ajoute un BOM).
        with open(chemin, newline="", encoding="utf-8-sig") as f:
            for ligne in csv.DictReader(f):
                nom = (ligne.get("nom") or "").strip()
                if nom:
                    biblio.ajouter_utilisateur(Utilisateur(nom))
    except FileNotFoundError:
        pass  # premier lancement : aucun utilisateur
    except (OSError, UnicodeDecodeError, csv.Error) as erreur:
        print(f"Lecture impossible de {chemin} : {erreur}")


def _charger_livres(biblio, chemin):
    try:
        with open(chemin, newline="", encoding="utf-8-sig") as f:
            # start=2 : la ligne 1 du fichier est l'en-tête.
            for num, ligne in enumerate(csv.DictReader(f), start=2):
                _charger_une_ligne(biblio, ligne, num)
    except FileNotFoundError:
        print("Aucune sauvegarde trouvée : bibliothèque vide.")
    except (OSError, UnicodeDecodeError, csv.Error) as erreur:
        print(f"Lecture impossible de {chemin} : {erreur}")


def _charger_une_ligne(biblio, ligne, num):
    # Une valeur manquante vaut None dans DictReader : « or "" » la remplace.
    titre = (ligne.get("titre") or "").strip()
    auteur = (ligne.get("auteur") or "").strip()
    emprunteur = (ligne.get("emprunteur") or "").strip()

    if not titre:
        print(f"Ligne {num} ignorée : titre manquant.")
        return
    if ligne.get("annee") is None:  # ligne trop courte
        print(f"Ligne {num} ignorée : colonnes manquantes.")
        return
    try:
        livre = Livre(titre, auteur, ligne.get("annee") or "")
    except ValueError:
        print(f"Ligne {num} ignorée : année invalide ({ligne.get('annee')!r}).")
        return

    ok, message = biblio.ajouter_livre(livre)
    if not ok:
        print(f"Ligne {num} ignorée : {message}")
        return

    # Le livre est emprunté si la colonne emprunteur est remplie.
    if emprunteur:
        # L'emprunteur doit exister pour pouvoir rendre le livre ensuite :
        # s'il manque (fichier utilisateurs perdu), on le recrée.
        if emprunteur not in biblio.utilisateurs:
            biblio.ajouter_utilisateur(Utilisateur(emprunteur))
        # On repasse par emprunter() : le livre ET la liste d'emprunts de
        # l'utilisateur sont mis à jour ensemble, comme pendant le jeu.
        biblio.emprunter(emprunteur, titre)


def tester():
    import tempfile

    with tempfile.TemporaryDirectory() as dossier:
        livres = Path(dossier) / "livres.csv"
        users = Path(dossier) / "utilisateurs.csv"

        # Jeu d'essai : Ana emprunte « 1984 », sauvegarde, rechargement
        b = Bibliotheque()
        b.ajouter_livre(Livre("1984", "Orwell", 1949))
        b.ajouter_livre(Livre("Guerre, et paix", "Tolstoï", 1869))  # virgule dans le titre
        b.ajouter_utilisateur(Utilisateur("Ana"))
        b.ajouter_utilisateur(Utilisateur("Léo"))                   # sans emprunt
        b.emprunter("Ana", "1984")
        assert sauvegarder(b, livres, users)
        print(livres.read_text(encoding="utf-8"))

        b2 = charger(livres, users)
        assert b2 is not b
        assert b2.livres["1984"].emprunteur == "Ana"
        assert "Léo" in b2.utilisateurs                 # utilisateur sans emprunt retrouvé
        assert "Guerre, et paix" in b2.livres           # la virgule n'a rien cassé
        assert b2.rendre("Ana", "1984")[0]              # Ana peut le rendre
        assert b2.livres["1984"].disponible

        # Fichier absent au lancement (défi de la soutenance)
        vide = charger(Path(dossier) / "absent.csv", Path(dossier) / "absent2.csv")
        assert vide.livres == {} and vide.utilisateurs == {}

        # Lignes abîmées : ignorées, le reste est chargé
        livres.write_text(
            "titre,auteur,annee,disponible,emprunteur\n"
            "Dune,Herbert,1965,oui,\n"
            "Fondation,Asimov,mille,oui,\n"   # année invalide
            ",SansTitre,2000,oui,\n"         # titre manquant
            "Dune,Herbert,1965,oui,\n"       # doublon
            "Ubik,Dick\n"                    # colonnes manquantes
            "Solaris,Lem,1961,non,Zoé\n",    # emprunteur absent de utilisateurs.csv
            encoding="utf-8")
        b3 = charger(livres, Path(dossier) / "absent.csv")
        assert set(b3.livres) == {"Dune", "Solaris"}
        assert b3.rendre("Zoé", "Solaris")[0]          # Zoé a été recréée

    print("\nTous les tests de la Partie C passent.")


if __name__ == "__main__":
    tester()
