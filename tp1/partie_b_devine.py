from __future__ import annotations

import random
from enum import Enum

from saisie import Lecteur, demander_oui_non, lire_entier

BORNE_MIN = 1
BORNE_MAX = 100
ESSAIS_MAX = 10


class Resultat(Enum):
    """Réponse du jeu à une proposition (la valeur est le texte affiché)."""
    TROP_PETIT = "Trop petit"
    TROP_GRAND = "Trop grand"
    GAGNE = "Gagné"



# Logique pure                                                                
def comparer(proposition: int, secret: int) -> Resultat:
    if proposition < secret:
        return Resultat.TROP_PETIT
    if proposition > secret:
        return Resultat.TROP_GRAND
    return Resultat.GAGNE


def jouer_partie(secret: int,
                 borne_min: int = BORNE_MIN,
                 borne_max: int = BORNE_MAX,
                 essais_max: int = ESSAIS_MAX,
                 lire: Lecteur = input) -> int | None:
    for essai in range(1, essais_max + 1):
        message = f"Essai {essai}/{essais_max} - votre nombre ({borne_min}-{borne_max}) : "
        proposition = lire_entier(message, borne_min, borne_max, lire)

        resultat = comparer(proposition, secret)
        if resultat is Resultat.GAGNE:
            print(f"Gagné en {essai} essai(s) !")
            return essai
        print(resultat.value)

    print(f"Perdu ! Le nombre était {secret}.")
    return None



# Interface joueur                                                            
def choisir_bornes(lire: Lecteur = input) -> tuple[int, int]:
    """Bonus : propose des bornes personnalisées, sinon garde 1-100."""
    if not demander_oui_non(
            f"Garder l'intervalle par défaut {BORNE_MIN}-{BORNE_MAX} ? (o/n) ", lire):
        borne_min = lire_entier("Borne minimale : ", lire=lire)
        # La borne max doit être strictement supérieure : sinon rien à deviner.
        borne_max = lire_entier("Borne maximale : ", minimum=borne_min + 1, lire=lire)
        return borne_min, borne_max
    return BORNE_MIN, BORNE_MAX


def main() -> None:
    print("=== Devine le nombre ===")
    try:
        while True:
            borne_min, borne_max = choisir_bornes()
            # randint inclut les deux bornes.
            secret = random.randint(borne_min, borne_max)
            jouer_partie(secret, borne_min, borne_max)
            if not demander_oui_non("Rejouer ? (o/n) "):
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print("À bientôt !")


if __name__ == "__main__":
    main()
