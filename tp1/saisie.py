from __future__ import annotations

from typing import Callable

# Signature d'une fonction de lecture : prend un message, renvoie une chaîne.
Lecteur = Callable[[str], str]

REPONSES_OUI = frozenset({"o", "oui", "y", "yes"})
REPONSES_NON = frozenset({"n", "non", "no"})


def lire_entier(message: str,
                minimum: int | None = None,
                maximum: int | None = None,
                lire: Lecteur = input) -> int:
    #Demande un entier, éventuellement borné, jusqu'à obtenir une saisie valide.
    while True:
        try:
            valeur = int(lire(message).strip())
        except ValueError:
            print("Saisie invalide : entrez un nombre entier.")
            continue
        if minimum is not None and valeur < minimum:
            print(_message_bornes(minimum, maximum))
        elif maximum is not None and valeur > maximum:
            print(_message_bornes(minimum, maximum))
        else:
            return valeur


def _message_bornes(minimum: int | None, maximum: int | None) -> str:
    #Construit le message d'erreur adapté aux bornes réellement fixées.

    if minimum is not None and maximum is not None:
        return f"Le nombre doit être compris entre {minimum} et {maximum}."
    if minimum is not None:
        return f"Le nombre doit être supérieur ou égal à {minimum}."
    return f"Le nombre doit être inférieur ou égal à {maximum}."


def lire_lettre(message: str, lire: Lecteur = input) -> str:
    #Demande une seule lettre (accents acceptés), renvoyée en majuscule.

    while True:
        saisie = lire(message).strip()
        if len(saisie) == 1 and saisie.isalpha():
            return saisie.upper()
        print("Entrez une seule lettre.")


def demander_oui_non(message: str, lire: Lecteur = input) -> bool:
    #Pose une question fermée ; renvoie True pour oui, False pour non.

    while True:
        reponse = lire(message).strip().lower()
        if reponse in REPONSES_OUI:
            return True
        if reponse in REPONSES_NON:
            return False
        print("Répondez par o (oui) ou n (non).")
