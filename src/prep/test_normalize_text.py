"""Guard tests for Ekegusii text normalization.

test_apostrophe_survives is the single most important test in this repository.
If it ever fails, STOP -- every downstream transcript is silently corrupted.
"""

import pytest

from normalize_text import NormalizationError, normalize, normalize_and_validate, validate


# --- the critical one ---------------------------------------------------------

def test_apostrophe_survives():
    """ng' is one phoneme. The apostrophe must never be stripped."""
    assert normalize("Omong'ina.") == "omong'ina"
    assert "'" in normalize("ng'ombe")
    assert normalize("Ng'ana, ng'iti!") == "ng'ana ng'iti"


def test_curly_apostrophes_become_ascii_but_are_not_removed():
    for variant in ["omong’ina", "omongʼina", "omong´ina"]:
        assert normalize(variant) == "omong'ina"


def test_ng_and_ng_apostrophe_stay_distinct():
    assert normalize("omongina") != normalize("omong'ina")


# --- ordinary normalization ---------------------------------------------------

def test_lowercase_and_punctuation():
    assert normalize("Nigo Ngocha, ase omobere?") == "nigo ngocha ase omobere"


def test_whitespace_collapse():
    assert normalize("  nigo   ngocha \n") == "nigo ngocha"


def test_digraphs_preserved():
    assert normalize("Chinyomba ny'ase") == "chinyomba ny'ase"


# --- tags ---------------------------------------------------------------------

def test_tags_dropped_by_default():
    assert normalize("nigo [noise] ngocha") == "nigo ngocha"


def test_tags_kept_when_requested():
    assert normalize("nigo [laughter] ngocha", keep_tags=True) == "nigo [laughter] ngocha"


# --- validation ---------------------------------------------------------------

def test_validator_rejects_unknown_character():
    with pytest.raises(NormalizationError) as exc:
        validate("nigo ngócha", clip_id="spk001_00007")
    assert "spk001_00007" in str(exc.value)


def test_validator_never_silently_drops():
    """Bad input must raise, not return cleaned text."""
    with pytest.raises(NormalizationError):
        normalize_and_validate("nigo 中文 ngocha", clip_id="x")


def test_digits_are_rejected_so_they_get_written_as_words():
    with pytest.raises(NormalizationError):
        normalize_and_validate("mwaka 2019", clip_id="x")
