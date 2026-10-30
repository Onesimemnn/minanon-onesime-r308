from __future__ import annotations

from enum import Enum, auto
from getpass import getpass

from partie_c_mots import (CACHE, charger_mots, choisir_mot, est_mot_valide,
                           masque, sans_accents)
from saisie import Lecteur, demander_oui_non, lire_lettre

ERREURS_MAX = 7

# Bonus ASCII art : une étape par erreur (index 0 = aucune erreur).
DESSINS = (
    "\n\n\n\n\n=========",
    "\n      |\n      |\n      |\n      |\n=========",
    "  +---+\n      |\n      |\n      |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n      |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n  |   |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n=========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n=========",
)
# Garantit à l'import qu'il y a bien un dessin par nombre d'erreurs possible.
assert len(DESSINS) == ERREURS_MAX + 1


class Coup(Enum):
    """Résultat d'une proposition de lettre."""
    PRESENTE = auto()
    ABSENTE = auto()
    DEJA_PROPOSEE = auto()


class PartiePendu:
    #État d'une partie de Pendu, indépendant de l'affichage et du clavier.

    def __init__(self, mot: str, erreurs_max: int = ERREURS_MAX) -> None:
        if not est_mot_valide(mot):
            raise ValueError(f"Mot non jouable : {mot!r}")
        self.mot = mot.upper()
        self.erreurs_max = erreurs_max
        self.erreurs = 0
        self.masque = masque(self.mot)
        self.lettres_proposees: set[str] = set()

        # Pré-calcul (une seule fois) : lettre sans accent -> positions dans le mot.
        # Chaque proposition est ensuite traitée sans reparcourir tout le mot.
        self._positions: dict[str, list[int]] = {}
        for i, lettre in enumerate(sans_accents(self.mot)):
            if lettre.isalpha():
                self._positions.setdefault(lettre, []).append(i)

        # Compteur de cases encore cachées : victoire testée en O(1).
        self._restantes = self.masque.count(CACHE)

    def proposer(self, lettre: str) -> Coup:
        #Joue une lettre (accents et minuscules acceptés).
        lettre = sans_accents(lettre.strip().upper())
        if len(lettre) != 1 or not lettre.isalpha():
            raise ValueError(f"Lettre invalide : {lettre!r}")

        if lettre in self.lettres_proposees:
            return Coup.DEJA_PROPOSEE
        self.lettres_proposees.add(lettre)

        positions = self._positions.get(lettre)
        if not positions:
            self.erreurs += 1
            return Coup.ABSENTE

        for i in positions:
            self.masque[i] = self.mot[i]  # révèle la vraie lettre (avec accent)
        self._restantes -= len(positions)
        return Coup.PRESENTE

    def est_gagnee(self) -> bool:
        return self._restantes == 0

    def est_perdue(self) -> bool:
        return self.erreurs >= self.erreurs_max

    def est_terminee(self) -> bool:
        return self.est_gagnee() or self.est_perdue()

    def mot_masque(self) -> str:
        return " ".join(self.masque)

    def dessin(self) -> str:
        return DESSINS[min(self.erreurs, len(DESSINS) - 1)]

    def etat(self) -> str:
        #Texte affiché à chaque tour : dessin, mot, erreurs, lettres jouées.
        lettres = " ".join(sorted(self.lettres_proposees)) or "-"
        return (f"{self.dessin()}\n\n"
                f"Mot      : {self.mot_masque()}\n"
                f"Erreurs  : {self.erreurs}/{self.erreurs_max}\n"
                f"Proposées: {lettres}")


# Déroulement d'une partie                                                    
MESSAGES = {
    Coup.PRESENTE: "Bien joué !",
    Coup.ABSENTE: "Raté...",
    Coup.DEJA_PROPOSEE: "Lettre déjà proposée (pas de pénalité).",
}


def jouer(mot: str, lire: Lecteur = input, afficher: bool = True) -> bool:
    #Joue une partie complète sur `mot` ; renvoie True en cas de victoire.

    partie = PartiePendu(mot)
    while not partie.est_terminee():
        if afficher:
            print("\n" + partie.etat())
        coup = partie.proposer(lire_lettre("Votre lettre : ", lire))
        if afficher:
            print(MESSAGES[coup])

    if afficher:
        print("\n" + partie.etat())
    if partie.est_gagnee():
        print(f"Gagné ! Le mot était {partie.mot}.")
        return True
    print(f"Perdu, le mot était {partie.mot}")
    return False


def saisir_mot_secret() -> str:
    #Bonus 2 joueurs : le joueur 1 tape un mot sans qu'il s'affiche.
    while True:
        # getpass masque la saisie ; certains IDE l'affichent quand même (avertissement).
        mot = getpass("Joueur 1, entrez le mot secret (invisible) : ").strip()
        if est_mot_valide(mot):
            return mot.upper()
        print("Mot invalide : lettres (accents acceptés) et tirets uniquement.")


def choisir_mot_partie() -> str:
    #Demande le mode de jeu et renvoie le mot à deviner.
    if demander_oui_non("Mode 2 joueurs ? (o/n) "):
        mot = saisir_mot_secret()
        print("\n" * 40)  # pousse l'écran pour que le joueur 2 ne voie rien
        return mot
    return choisir_mot(charger_mots())


def main() -> None:
    print("=== Jeu du Pendu ===")
    try:
        while True:
            jouer(choisir_mot_partie())
            if not demander_oui_non("Rejouer ? (o/n) "):
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print("À bientôt !")


if __name__ == "__main__":
    main()
