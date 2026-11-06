import io
import random

import pytest

from flash_net.game import Card, is_correct, load_cards, main, play


def scripted(*answers):
    """Stand-in for input(): returns each answer, then behaves like Ctrl-D."""
    remaining = iter(answers)

    def ask(prompt):
        try:
            return next(remaining)
        except StopIteration:
            raise EOFError

    return ask


WIFI = Card("Wi-Fi", ["Wireless Fidelity"])
DNS = Card("DNS", ["Domain Name System", "Domain Name Service"])


@pytest.mark.parametrize(
    "guess",
    ["Wireless Fidelity", "wireless fidelity", "  WIRELESS   fidelity "],
)
def test_answer_ignores_case_and_whitespace(guess):
    assert is_correct(WIFI, guess)


def test_answer_ignores_punctuation():
    card = Card("SDN", ["Software-Defined Networking"])
    assert is_correct(card, "software defined networking")


def test_any_listed_answer_is_accepted():
    assert is_correct(DNS, "domain name service")


@pytest.mark.parametrize("guess", ["", "   ", "---", "Wireless", "Wireless Fidelity Plus"])
def test_wrong_answers_are_rejected(guess):
    assert not is_correct(WIFI, guess)


def test_load_cards_reads_yaml(tmp_path):
    path = tmp_path / "cards.yaml"
    path.write_text("- name: DNS\n  answers:\n    - Domain Name System\n")
    assert load_cards(path) == [Card("DNS", ["Domain Name System"])]


@pytest.mark.parametrize(
    "content",
    [
        "name: DNS",
        "[]",
        "- name: DNS",
        "- answers: [Domain Name System]",
        "- name: DNS\n  answers: []",
        "- name: DNS\n  answers: Domain Name System",
        "- name: NO\n  answers: [Nope]\n- 5",
    ],
)
def test_load_cards_rejects_malformed_files(tmp_path, content):
    path = tmp_path / "cards.yaml"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_cards(path)


def test_bundled_list_is_valid_and_has_no_duplicates():
    names = [card.name for card in load_cards()]
    assert names
    assert len(names) == len(set(names))


def test_bundled_list_includes_wifi():
    cards = {card.name: card for card in load_cards()}
    assert is_correct(cards["Wi-Fi"], "wireless fidelity")


def test_play_scores_right_and_wrong_answers():
    output = []
    score, asked = play(
        [WIFI, DNS],
        ask=scripted("wireless fidelity", "nope"),
        show=output.append,
        rng=random.Random(0),
        shuffle=False,
    )
    assert (score, asked) == (1, 2)
    assert any("Domain Name System" in line for line in output)


def test_play_asks_every_card_once_in_random_order():
    cards = [Card(str(n), [str(n)]) for n in range(50)]
    prompts = []

    def ask(prompt):
        prompts.append(prompt)
        return ""

    play(cards, ask=ask, show=lambda _: None, rng=random.Random(1))
    expected = [f"{card.name}: " for card in cards]
    assert sorted(prompts) == sorted(expected)
    assert prompts != expected


def test_play_does_not_reorder_the_callers_list():
    cards = [Card(str(n), [str(n)]) for n in range(50)]
    original = list(cards)
    play(cards, ask=scripted(), show=lambda _: None, rng=random.Random(1))
    assert cards == original


@pytest.mark.parametrize("interrupt", [EOFError, KeyboardInterrupt])
def test_quitting_counts_only_answered_cards(interrupt):
    answers = iter(["wireless fidelity"])

    def ask(prompt):
        try:
            return next(answers)
        except StopIteration:
            raise interrupt

    score, asked = play(
        [WIFI, DNS], ask=ask, show=lambda _: None, rng=random.Random(0), shuffle=False
    )
    assert (score, asked) == (1, 1)


def test_main_reports_a_missing_file(tmp_path, capsys):
    assert main(["--file", str(tmp_path / "missing.yaml")]) == 1
    assert "missing.yaml" in capsys.readouterr().err


def test_main_reports_a_malformed_file(tmp_path, capsys):
    path = tmp_path / "bad.yaml"
    path.write_text("a: [")
    assert main(["--file", str(path)]) == 1
    assert "bad.yaml" in capsys.readouterr().err


def test_main_plays_a_custom_file(tmp_path, monkeypatch, capsys):
    path = tmp_path / "cards.yaml"
    path.write_text("- name: DNS\n  answers: [Domain Name System]\n")
    monkeypatch.setattr("sys.stdin", io.StringIO("domain name system\n"))
    assert main(["--file", str(path)]) == 0
    assert "1/1" in capsys.readouterr().out
