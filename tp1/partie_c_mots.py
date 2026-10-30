from __future__ import annotations

import logging
import random
import re
import unicodedata
from pathlib import Path

# Liste de secours si le fichier de mots est absent ou vide.
MOTS_PAR_DEFAUT = ("PYTHON", "DICTIONNAIRE", "FONCTION", "VARIABLE",
                   "BOUCLE", "ÉLÉPHANT", "CLAVIER", "RÉSEAU")

FICHIER_MOTS = Path(__file__).with_name("mots.txt")

# Caractère qui cache une lettre non découverte.
CACHE = "_"

# Un mot valide, une fois les accents retirés : des lettres A-Z,
# éventuellement reliées par des tirets (ex. PORTE-MONNAIE).
_MOT_VALIDE = re.compile(r"[A-Z]+(-[A-Z]+)*")

logger = logging.getLogger(__name__)



# Normalisation                                                               
def sans_accents(texte: str) -> str:
    #Retire les accents en conservant la longueur du texte.
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def est_mot_valide(mot: str) -> bool:
    #Vrai si le mot est jouable au Pendu (lettres, accents, tirets).
    return _MOT_VALIDE.fullmatch(sans_accents(mot.upper())) is not None



# Chargement et choix                                                         
def charger_mots(chemin: str | Path = FICHIER_MOTS) -> list[str]:
    #Charge les mots d'un fichier texte (un mot par ligne).
    
    try:
        with open(chemin, encoding="utf-8") as fichier:
            lignes = [ligne.strip() for ligne in fichier]
    except FileNotFoundError:
        logger.info("Fichier %s absent : liste de mots par défaut", chemin)
        return list(MOTS_PAR_DEFAUT)
    except (OSError, UnicodeDecodeError) as err:
        logger.error("Lecture impossible de %s : %s", chemin, err)
        return list(MOTS_PAR_DEFAUT)

    mots = []
    for ligne in lignes:
        if not ligne or ligne.startswith("#"):
            continue
        if est_mot_valide(ligne):
            mots.append(ligne.upper())
        else:
            logger.warning("Mot ignoré (caractères non jouables) : %r", ligne)

    # dict.fromkeys supprime les doublons en O(n) tout en gardant l'ordre.
    mots = list(dict.fromkeys(mots))
    if not mots:
        logger.warning("Aucun mot valide dans %s : liste par défaut", chemin)
        return list(MOTS_PAR_DEFAUT)
    return mots


def choisir_mot(liste: list[str] | tuple[str, ...]) -> str:
    #Renvoie un mot de la liste au hasard, en MAJUSCULES.
    if not liste:
        raise ValueError("La liste de mots est vide")
    return random.choice(liste).strip().upper()


def masque(mot: str) -> list[str]:
    #Construit le masque du mot : « _ » pour chaque lettre.
    return [CACHE if c.isalpha() else c for c in mot]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    mots = charger_mots()
    print(f"{len(mots)} mots chargés :", mots)
    mot = choisir_mot(mots)
    print("Mot choisi :", mot)
    print("Masque     :", " ".join(masque(mot)))


if __name__ == "__main__":
    main()
