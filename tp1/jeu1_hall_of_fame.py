from __future__ import annotations

import math
from heapq import nlargest
from operator import itemgetter
from pathlib import Path

from partie_a_etudiants import Notes, charger, nettoyer_nom, sauvegarder
from partie_d_pendu import choisir_mot_partie, jouer
from saisie import Lecteur, demander_oui_non

FICHIER_SCORES = Path(__file__).with_name("scores.txt")
TAILLE_PODIUM = 5

# Même structure que les notes de la Partie A : nom -> nombre (float).
Scores = Notes


def convertir_victoires(valeur: str) -> float:
    #Valide un nombre de victoires lu dans le fichier (réel fini, >= 0).
    try:
        victoires = float(valeur.strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"Nombre de victoires invalide : {valeur!r}") from None
    if not math.isfinite(victoires) or victoires < 0:
        raise ValueError(f"Nombre de victoires invalide : {valeur!r}")
    return victoires


def charger_scores(chemin: str | Path = FICHIER_SCORES) -> Scores:
    #Relit les scores ; fichier absent -> dictionnaire vide (départ à zéro).
    return charger(chemin, convertir=convertir_victoires)


def enregistrer_victoire(scores: Scores, nom: str) -> None:
    #Ajoute une victoire au joueur (créé s'il n'existe pas).

    scores[nom] = scores.get(nom, 0.0) + 1.0


def podium(scores: Scores, taille: int = TAILLE_PODIUM) -> str:
    #Classement des meilleurs joueurs, prêt à afficher.

    if not scores:
        return "Aucune victoire enregistrée."
    meilleurs = nlargest(taille, scores.items(), key=itemgetter(1))
    return "\n".join(f"{rang}. {nom} : {victoires:g} victoire(s)"
                     for rang, (nom, victoires) in enumerate(meilleurs, start=1))


def demander_nom(lire: Lecteur = input) -> str:
    #Demande un pseudo valide (non vide, sans « : » qui casserait le fichier).
    while True:
        try:
            return nettoyer_nom(lire("Votre pseudo : "))
        except ValueError as err:
            print(err)


def main() -> None:
    print("=== Pendu - Hall of fame ===")
    scores = charger_scores()
    print(podium(scores))

    try:
        nom = demander_nom()
        while True:
            if jouer(choisir_mot_partie()):
                enregistrer_victoire(scores, nom)
                print(f"{nom} : {scores[nom]:g} victoire(s)")
            if not demander_oui_non("Rejouer ? (o/n) "):
                break
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        # Exécuté même après Ctrl+C : les victoires de la session ne sont pas perdues.
        if sauvegarder(scores, FICHIER_SCORES):
            print("Scores enregistrés.")

    print("\n--- Hall of fame ---")
    print(podium(scores))


if __name__ == "__main__":
    main()
