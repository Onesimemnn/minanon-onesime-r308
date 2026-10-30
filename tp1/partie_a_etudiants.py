from __future__ import annotations

import logging
import math
from operator import itemgetter
from pathlib import Path
from typing import Callable

# Type des données manipulées : nom de l'étudiant -> note.
Notes = dict[str, float]

# Fonction qui convertit et valide la valeur lue dans le fichier.
Convertisseur = Callable[[str], float]

# Bornes d'une note valide (système français sur 20).
NOTE_MIN = 0.0
NOTE_MAX = 20.0

# Séparateur utilisé dans le fichier de sauvegarde.
SEPARATEUR = ":"

logger = logging.getLogger(__name__)



# Validation des entrées                                                      

def convertir_note(valeur: str | int | float) -> float:
    
    #Convertit une valeur en note (float) en la validant.
    #Accepte la virgule française comme séparateur décimal et ignore
    #les espaces autour. Lève ValueError si la valeur n'est pas une note valide.
    
    try:
        # str() permet de traiter int, float et str de la même manière.
        note = float(str(valeur).strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"Note invalide : {valeur!r}") from None

    # float() accepte nan  et  inf : on les refuse explicitement.
    if not math.isfinite(note):
        raise ValueError(f"Note invalide : {valeur!r}")
    if not NOTE_MIN <= note <= NOTE_MAX:
        raise ValueError(f"Note hors bornes [{NOTE_MIN}, {NOTE_MAX}] : {note}")
    return note


def nettoyer_nom(nom: str) -> str:
    
    #Nettoie un nom et vérifie qu'il est utilisable comme clé.
    #Le nom ne doit pas être vide ni contenir le séparateur du fichier,
    #sinon la sauvegarde produirait une ligne impossible à relire.
    
    nom = nom.strip()
    if not nom:
        raise ValueError("Le nom ne peut pas être vide")
    if SEPARATEUR in nom:
        raise ValueError(f"Le nom ne doit pas contenir {SEPARATEUR!r}")
    return nom



# Opérations sur le dictionnaire                                              

def ajouter_etudiant(d: Notes, nom: str, note: str | int | float) -> None:
    #Ajoute un étudiant ou met à jour sa note (modifie d en place).
    
    d[nettoyer_nom(nom)] = convertir_note(note)


def moyenne_classe(d: Notes, decimales: int = 2) -> float | None:
    #Renvoie la moyenne arrondie des notes, ou None si d est vide.

    if not d:
        return None
    return round(sum(d.values()) / len(d), decimales)


def meilleur_etudiant(d: Notes) -> tuple[str, float] | None:
    #Renvoie (nom, note) du meilleur étudiant, ou None si d est vide.
    #En cas d'égalité, le premier inséré l'emporte.
    
    if not d:
        return None
    # max() en une seule passe, en comparant sur la note (élément d'indice 1).
    return max(d.items(), key=itemgetter(1))



# Persistance fichier                                                         

def sauvegarder(d: Notes, chemin: str | Path) -> bool:
    #Écrit d dans un fichier texte, une ligne  nom:note  par entrée.
    #Renvoie True si l'écriture a réussi, False sinon (l'erreur est journalisée,le programme ne plante pas).
    
    contenu = "".join(f"{nom}{SEPARATEUR}{note}\n" for nom, note in d.items())
    try:
        Path(chemin).write_text(contenu, encoding="utf-8")
    except OSError as err:  # disque plein, droits, dossier inexistant...
        logger.error("Sauvegarde impossible dans %s : %s", chemin, err)
        return False
    return True


def charger(chemin: str | Path,
            convertir: Convertisseur = convertir_note) -> Notes:
    #Recharge un dictionnaire depuis un fichier « nom:valeur ».

    #`convertir` valide chaque valeur : par défaut une note sur 20 ; le hall of

    #- fichier absent        -> dictionnaire vide ;
    #- fichier illisible     -> dictionnaire vide (erreur journalisée) ;
    #- ligne vide            -> ignorée ;
    #- ligne mal formée      -> ignorée avec un avertissement (numéro de ligne).
    
    d: Notes = {}
    try:
        # Lecture ligne par ligne : pas de chargement complet en mémoire.
        with open(chemin, encoding="utf-8") as fichier:
            for num, ligne in enumerate(fichier, start=1):
                ligne = ligne.strip()
                if not ligne:
                    continue
                # partition() ne lève jamais d'exception, contrairement à split+unpack.
                nom, sep, note = ligne.partition(SEPARATEUR)
                if not sep:
                    logger.warning("Ligne %d ignorée (pas de '%s') : %r",
                                   num, SEPARATEUR, ligne)
                    continue
                try:
                    d[nettoyer_nom(nom)] = convertir(note)
                except ValueError as err:
                    logger.warning("Ligne %d ignorée (%s) : %r", num, err, ligne)
    except FileNotFoundError:
        logger.info("Fichier %s absent : départ avec un dictionnaire vide", chemin)
    except (OSError, UnicodeDecodeError) as err:
        logger.error("Lecture impossible de %s : %s", chemin, err)
    return d



# Démonstration : rejoue le jeu d'essai de l'énoncé                           

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    fichier = Path(__file__).with_name("notes.txt")

    # 1. Création et remplissage
    notes: Notes = {}
    for nom, note in (("Alice", 12), ("Bob", 15), ("Claire", 9.5)):
        ajouter_etudiant(notes, nom, note)
    print("Dictionnaire      :", notes)
    print("Moyenne           :", moyenne_classe(notes))
    print("Meilleur étudiant :", meilleur_etudiant(notes))

    # 2. Sauvegarde puis rechargement
    sauvegarder(notes, fichier)
    print("Rechargé identique :", charger(fichier) == notes)

    # 3. Cas limites : aucun ne doit faire planter le programme
    print("\n--- Cas limites ---")
    print("Dico vide -> moyenne :", moyenne_classe({}),
          "| meilleur :", meilleur_etudiant({}))
    print("Fichier absent ->", charger(fichier.with_name("inexistant.txt")))

    fichier_test = fichier.with_name("notes_corrompues.txt")
    fichier_test.write_text("Alice:12\nligne sans separateur\nBob:abc\n"
                            "Zoe:25\n\nClaire:9,5\n", encoding="utf-8")
    print("Lignes mal formées ->", charger(fichier_test))
    fichier_test.unlink()


if __name__ == "__main__":
    main()
