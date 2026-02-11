# sutom.py
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Dict, Set, Tuple


def _clean_word(w: str) -> str:
    # Normalisation simple : minuscule, retrait espaces
    # Si tu veux gérer les accents, ajoute une translittération (ex: unidecode)
    return w.strip().lower()


@dataclass
class Constraints:
    """
    Contraintes cumulées au fil des tentatives.
    - greens : positions figées -> lettre (verts)
    - required_min : min d'occurrences pour chaque lettre vue (verts + jaunes)
    - forbidden_positions : lettres qui ne peuvent PAS être à certaines positions (jaunes)
    - absent : lettres exclues (gris ET jamais vues comme vert/jaune)
    """

    greens: Dict[int, str] = field(default_factory=dict)
    required_min: Counter = field(default_factory=Counter)
    forbidden_positions: Dict[str, Set[int]] = field(default_factory=lambda: defaultdict(set))
    absent: Set[str] = field(default_factory=set)

    def update_from_feedback(self, row: List[Tuple[str, str, int]]):
        """
        row = [(letter, status('green'|'yellow'|'gray'|'unknown'), pos), ...]
        Met à jour les contraintes en intégrant le feedback de la ligne.
        """
        local_required = Counter()
        local_greens = {}

        # 1) Comptage verts+jaunes pour minima
        for letter, status, pos in row:
            if not letter:
                continue
            if status == "green":
                local_required[letter] += 1
                local_greens[pos] = letter
            elif status == "yellow":
                local_required[letter] += 1
                self.forbidden_positions[letter].add(pos)

        # 2) Fixer les verts
        for pos, letter in local_greens.items():
            self.greens[pos] = letter

        # 3) Minima requis cumulés
        for letter, cnt in local_required.items():
            if cnt > self.required_min[letter]:
                self.required_min[letter] = cnt

        # 4) Lettres grises absentes (si non requises)
        for letter, status, _ in row:
            if not letter:
                continue
            if status == "gray":
                if letter not in self.required_min and letter not in self.greens.values():
                    self.absent.add(letter)

    def __repr__(self) -> str:
        return (
            f"Constraints(greens={self.greens}, required_min={dict(self.required_min)}, "
            f"forbidden_positions={{k:sorted(v) for k,v in self.forbidden_positions.items()}}, "
            f"absent={sorted(self.absent)})"
        )


class SutomSolver:
    def __init__(self, dict_path: Path):
        self.dict_path = Path(dict_path)
        self.words_by_len: Dict[int, List[str]] = defaultdict(list)
        self._load_dictionary()

    def _load_dictionary(self):
        with self.dict_path.open("r", encoding="utf-8") as f:
            for line in f:
                w = _clean_word(line)
                if not w:
                    continue
                # Filtrer caractères non alpha simples si besoin
                if not w.isalpha():
                    continue
                self.words_by_len[len(w)].append(w)

        # Déduplique et trie
        for L in list(self.words_by_len):
            self.words_by_len[L] = sorted(set(self.words_by_len[L]))

    def candidates_for(self, length: int, startswith: str | None = None) -> List[str]:
        base = self.words_by_len.get(length, [])
        if startswith:
            s = startswith.lower()
            return [w for w in base if w.startswith(s)]
        return list(base)

    @staticmethod
    def _respect_greens(word: str, greens: Dict[int, str]) -> bool:
        return all(0 <= pos < len(word) and word[pos] == letter for pos, letter in greens.items())

    @staticmethod
    def _respect_forbidden_positions(word: str, forbidden: Dict[str, Set[int]]) -> bool:
        for letter, positions in forbidden.items():
            for pos in positions:
                if 0 <= pos < len(word) and word[pos] == letter:
                    return False
        return True

    @staticmethod
    def _respect_required_min(word: str, required_min: Counter) -> bool:
        c = Counter(word)
        for letter, mn in required_min.items():
            if c[letter] < mn:
                return False
        return True

    @staticmethod
    def _respect_absent(word: str, absent: Set[str], required_min: Counter, greens: Dict[int, str]) -> bool:
        # Une lettre "absente" ne doit pas apparaître, sauf si elle est aussi requise
        req_letters = set(required_min.keys()) | set(greens.values())
        for ch in word:
            if ch in absent and ch not in req_letters:
                return False
        return True

    def filter_candidates(self, candidates: List[str], constraints: Constraints) -> List[str]:
        out = []
        for w in candidates:
            if not self._respect_greens(w, constraints.greens):
                continue
            if not self._respect_forbidden_positions(w, constraints.forbidden_positions):
                continue
            if not self._respect_required_min(w, constraints.required_min):
                continue
            if not self._respect_absent(w, constraints.absent, constraints.required_min, constraints.greens):
                continue
            out.append(w)
        return out

    @staticmethod
    def _letter_frequencies(words: List[str]) -> Counter:
        # Fréquence globale (on compte une fois par mot pour favoriser la diversité)
        freq = Counter()
        for w in words:
            for ch in set(w):
                freq[ch] += 1
        return freq

    def best_guess(self, candidates: List[str], constraints: Constraints) -> str:
        """
        Heuristique : score = somme des fréquences des lettres distinctes du mot,
        avec bonus léger quand la lettre est à une position encore inconnue (non verte).
        """
        if not candidates:
            raise ValueError("No candidates to choose from")

        freq = self._letter_frequencies(candidates)
        green_positions = set(constraints.greens.keys())

        def score(word: str) -> float:
            seen = set()
            s = 0.0
            for i, ch in enumerate(word):
                if ch in seen:
                    continue
                base = freq[ch]
                bonus = 0.15 if i not in green_positions else 0.0
                s += base * (1.0 + bonus)
                seen.add(ch)
            return s

        return max(candidates, key=score)