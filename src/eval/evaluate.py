"""Evaluation harness for Ekegusii ASR predictions."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import jiwer

def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file and return its rows."""
    rows = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}"
                ) from exc

    return rows

def match_predictions(
    manifest: list[dict], predictions: list[dict]
) -> list[tuple[dict, dict]]:
    """Match prediction rows to manifest rows using the clip ID."""

    manifest_by_id = {}

    for row in manifest:
        clip_id = row.get("id")

        if not clip_id:
            raise ValueError("Manifest row is missing 'id'.")

        if clip_id in manifest_by_id:
            raise ValueError(f"Duplicate manifest id: {clip_id}")

        manifest_by_id[clip_id] = row

    predictions_by_id = {}

    for row in predictions:
        clip_id = row.get("id")

        if not clip_id:
            raise ValueError("Prediction row is missing 'id'.")

        if clip_id in predictions_by_id:
            raise ValueError(f"Duplicate prediction id: {clip_id}")

        predictions_by_id[clip_id] = row

    missing = set(manifest_by_id) - set(predictions_by_id)
    extra = set(predictions_by_id) - set(manifest_by_id)

    if missing:
        raise ValueError(f"Missing predictions for IDs: {sorted(missing)}")

    if extra:
        raise ValueError(f"Unknown prediction IDs: {sorted(extra)}")

    return [
        (manifest_by_id[clip_id], predictions_by_id[clip_id])
        for clip_id in manifest_by_id
    ]

def calculate_metrics(rows: list[tuple[dict, dict]]) -> dict:
    """Calculate ASR evaluation metrics for matched rows."""

    references = []
    hypotheses = []

    for manifest_row, prediction_row in rows:
        reference = manifest_row.get("text", "")
        hypothesis = prediction_row.get("text", "")

        references.append(reference)
        hypotheses.append(hypothesis)

    word_result = jiwer.process_words(references, hypotheses)
    char_result = jiwer.process_characters(references, hypotheses)

    return {
        "wer": word_result.wer,
        "cer": char_result.cer,
        "substitutions": word_result.substitutions,
        "deletions": word_result.deletions,
        "insertions": word_result.insertions,
    }

def get_slice_value(manifest_row: dict, field: str) -> str:
    """Return the value used to group a manifest row for evaluation."""

    if field == "duration_bucket":
        duration = float(manifest_row.get("duration", 0))

        if duration < 5:
            return "<5s"
        if duration < 10:
            return "5-10s"
        if duration < 15:
            return "10-15s"
        if duration < 20:
            return "15-20s"

        return "20s+"

    value = manifest_row.get(field)

    if value is None or value == "":
        return "unknown"

    return str(value)

def evaluate_slices(
    rows: list[tuple[dict, dict]],
    fields: list[str],
) -> dict[str, dict[str, dict]]:
    """Calculate metrics for each requested evaluation slice."""

    results = {}

    for field in fields:
        grouped_rows = defaultdict(list)

        for manifest_row, prediction_row in rows:
            slice_value = get_slice_value(manifest_row, field)
            grouped_rows[slice_value].append(
                (manifest_row, prediction_row)
            )

        results[field] = {}

        for slice_value, group in sorted(grouped_rows.items()):
            results[field][slice_value] = calculate_metrics(group)

    return results

def evaluate(
    manifest_path: Path,
    predictions_path: Path,
    slice_fields: list[str] | None = None,
) -> dict:
    """Run the complete evaluation."""

    manifest = load_jsonl(manifest_path)
    predictions = load_jsonl(predictions_path)

    rows = match_predictions(manifest, predictions)

    result = {
        "overall": calculate_metrics(rows),
        "slices": {},
    }

    if slice_fields:
        result["slices"] = evaluate_slices(rows, slice_fields)

    return result

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate ASR predictions against a manifest."
    )

    parser.add_argument(
        "manifest",
        type=Path,
        help="Path to the reference manifest JSONL file.",
    )

    parser.add_argument(
        "predictions",
        type=Path,
        help="Path to the predictions JSONL file.",
    )

    parser.add_argument(
        "--slice",
        dest="slice_fields",
        action="append",
        choices=[
            "style",
            "gender",
            "age_band",
            "dialect",
            "source_id",
            "duration_bucket",
            "label_origin",
        ],
        help="Evaluation field to slice by. Can be supplied multiple times.",
    )

    args = parser.parse_args()

    result = evaluate(
        args.manifest,
        args.predictions,
        args.slice_fields,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()