import json
from pathlib import Path

from evaluate import calculate_metrics, evaluate_slices


def write_jsonl(path: Path, rows: list[dict]) -> None:
    """Write test rows to a JSONL file."""

    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")


def test_identical_predictions_have_zero_wer(tmp_path):
    """Identical reference and prediction should have WER of zero."""

    rows = [
        (
            {"id": "clip001", "text": "nigo ngocha ase"},
            {"id": "clip001", "text": "nigo ngocha ase"},
        )
    ]

    metrics = calculate_metrics(rows)

    assert metrics["wer"] == 0.0

def test_empty_prediction_has_100_percent_wer():
    """An empty prediction should produce 100% WER."""

    rows = [
        (
            {"id": "clip002", "text": "nigo ngocha ase"},
            {"id": "clip002", "text": ""},
        )
    ]

    metrics = calculate_metrics(rows)

    assert metrics["wer"] == 1.0

def test_one_known_substitution_is_counted():
    """One incorrect word should produce exactly one substitution."""

    rows = [
        (
            {"id": "clip003", "text": "nigo ngocha ase"},
            {"id": "clip003", "text": "nigo ngocha ose"},
        )
    ]

    metrics = calculate_metrics(rows)

    assert metrics["substitutions"] == 1

from evaluate import evaluate_slices


def test_evaluation_can_slice_by_style():
    """Evaluation should produce separate metrics for each speech style."""

    rows = [
        (
            {
                "id": "clip004",
                "text": "nigo ngocha",
                "style": "read",
            },
            {
                "id": "clip004",
                "text": "nigo ngocha",
            },
        ),
        (
            {
                "id": "clip005",
                "text": "nigo ngocha",
                "style": "spontaneous",
            },
            {
                "id": "clip005",
                "text": "nigo ngacha",
            },
        ),
    ]

    results = evaluate_slices(rows, ["style"])

    assert "style" in results
    assert "read" in results["style"]
    assert "spontaneous" in results["style"]

    assert results["style"]["read"]["wer"] == 0.0
    assert results["style"]["spontaneous"]["substitutions"] == 1

def test_all_required_slice_fields_are_supported():
    """All required Issue #7 slice fields should produce results."""

    manifest_row = {
        "id": "clip006",
        "text": "nigo ngocha",
        "style": "broadcast",
        "gender": "f",
        "age_band": "25-40",
        "dialect": "rogoro",
        "source_id": "radio-egesa",
        "duration": 6.42,
        "label_origin": "corrected",
    }

    prediction_row = {
        "id": "clip006",
        "text": "nigo ngocha",
    }

    rows = [(manifest_row, prediction_row)]

    fields = [
        "style",
        "gender",
        "age_band",
        "dialect",
        "source_id",
        "duration_bucket",
        "label_origin",
    ]

    results = evaluate_slices(rows, fields)

    assert results["style"]["broadcast"]["wer"] == 0.0
    assert results["gender"]["f"]["wer"] == 0.0
    assert results["age_band"]["25-40"]["wer"] == 0.0
    assert results["dialect"]["rogoro"]["wer"] == 0.0
    assert results["source_id"]["radio-egesa"]["wer"] == 0.0
    assert results["duration_bucket"]["5-10s"]["wer"] == 0.0
    assert results["label_origin"]["corrected"]["wer"] == 0.0