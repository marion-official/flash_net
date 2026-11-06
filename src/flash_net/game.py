"""Flashcard game: show a Network+ acronym, type what it stands for."""

import argparse
import random
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CARDS = Path(__file__).with_name("acronyms.yaml")


@dataclass(frozen=True)
class Card:
    name: str
    answers: list[str]  # the first one is shown when the player gets it wrong
    hint: str | None = None  # shown in the prompt to tell similar meanings apart

    @property
    def label(self):
        return f"{self.name} ({self.hint})" if self.hint else self.name


def _normalize(text):
    return "".join(char for char in text.casefold() if char.isalnum())


def is_correct(card, guess):
    """Compare ignoring case, spacing and punctuation ("Wi-Fi" == "wi fi")."""
    guess = _normalize(guess)
    return bool(guess) and guess in map(_normalize, card.answers)


def _parse_card(entry):
    if not isinstance(entry, dict):
        raise ValueError(f"expected a name and answers, got: {entry!r}")
    name, answers = entry.get("name"), entry.get("answers")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"'name' must be text (quote values like NO): {entry!r}")
    if (
        not isinstance(answers, list)
        or not answers
        or not all(isinstance(a, str) and _normalize(a) for a in answers)
    ):
        raise ValueError(f"'answers' must be a non-empty list of text: {entry!r}")
    hint = entry.get("hint")
    if hint is not None and (not isinstance(hint, str) or not hint.strip()):
        raise ValueError(f"'hint' must be text: {entry!r}")
    return Card(name, answers, hint)


def load_cards(path=DEFAULT_CARDS):
    """Read cards from a YAML file. Raises OSError or ValueError."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML: {error}") from error
    if not isinstance(data, list) or not data:
        raise ValueError("expected a non-empty list of cards")
    return [_parse_card(entry) for entry in data]


def play(cards, ask=input, show=print, rng=random, shuffle=True):
    """Ask each card once. Returns (correct, answered); Ctrl-C/Ctrl-D stops early."""
    order = rng.sample(cards, len(cards)) if shuffle else cards
    score = answered = 0
    for card in order:
        try:
            guess = ask(f"{card.label}: ")
        except (EOFError, KeyboardInterrupt):
            show("")
            break
        answered += 1
        if is_correct(card, guess):
            score += 1
            show("Correct!")
        else:
            show(f"Wrong: {card.answers[0]}")
    return score, answered


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file", type=Path, default=DEFAULT_CARDS, help="YAML file of acronyms"
    )
    args = parser.parse_args(argv)
    try:
        cards = load_cards(args.file)
    except (OSError, ValueError) as error:
        print(f"Could not load {args.file}: {error}", file=sys.stderr)
        return 1

    print(f"Cards: {len(cards)}. Type the long form, or press Ctrl-D to stop.\n")
    score, answered = play(cards)
    print(f"\nScore: {score}/{answered}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
