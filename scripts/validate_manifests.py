#!/usr/bin/env python3
"""Validate manifests before anything trains on them.

Wire into CI. A manifest that fails here must not be merged.

The speaker-leakage check is the one that protects our headline numbers: if the same voice
appears in train and test, the reported WER is meaningless and an examiner will spot it.

Usage:  python scripts/validate_manifests.py data/manifests/
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "prep"))
from normalize_text import NormalizationError, validate  # noqa: E402

REQUIRED = {
    "id", "audio_path", "duration", "text", "text_raw",
    "speaker_id", "source_id", "style", "label_origin",
}
VALID_STYLE = {"read", "spontaneous", "broadcast"}
VALID_ORIGIN = {"aligned", "human", "corrected"}
MIN_DUR, MAX_DUR = 1.0, 25.0


def load(path):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append((n, json.loads(line)))
        except json.JSONDecodeError as e:
            raise SystemExit(f"FAIL {path.name}:{n}: bad JSON: {e}")
    return rows


def main(manifest_dir):
    md = Path(manifest_dir)
    data_root = md.parent
    errors, warnings = [], []
    speakers_by_split = defaultdict(set)
    minutes_by_split = defaultdict(float)

    splits = [s for s in ("train", "dev", "test", "test-hard") if (md / f"{s}.jsonl").exists()]
    if not splits:
        raise SystemExit(f"FAIL: no manifests found in {md}")

    for split in splits:
        for n, r in load(md / f"{split}.jsonl"):
            where = f"{split}.jsonl:{n}"

            missing = REQUIRED - r.keys()
            if missing:
                errors.append(f"{where}: missing fields {sorted(missing)}")
                continue

            if not (MIN_DUR <= r["duration"] <= MAX_DUR):
                errors.append(f"{where}: duration {r['duration']}s outside [{MIN_DUR}, {MAX_DUR}]")
            if r["style"] not in VALID_STYLE:
                errors.append(f"{where}: bad style {r['style']!r}")
            if r["label_origin"] not in VALID_ORIGIN:
                errors.append(f"{where}: bad label_origin {r['label_origin']!r}")
            if not r["text"].strip():
                errors.append(f"{where}: empty text")

            try:
                validate(r["text"], clip_id=where)
            except NormalizationError as e:
                errors.append(str(e))

            if not (data_root / r["audio_path"]).exists():
                warnings.append(f"{where}: audio missing at {r['audio_path']}")

            # Aligned labels are machine-made and noisier -- they must not decide our score.
            if split in ("test", "test-hard") and r["label_origin"] == "aligned":
                errors.append(f"{where}: aligned label in {split}; test labels must be human-checked")

            speakers_by_split[split].add(r["speaker_id"])
            minutes_by_split[split] += r["duration"] / 60.0

    # --- speaker leakage: the check that protects the headline number ---
    for a in splits:
        for b in splits:
            if a < b:
                overlap = speakers_by_split[a] & speakers_by_split[b]
                if overlap:
                    errors.append(
                        f"SPEAKER LEAKAGE between {a} and {b}: {sorted(overlap)} "
                        f"-- splits must be speaker-disjoint (ARCHITECTURE 5.3)"
                    )

    print("split      speakers    minutes")
    total = 0.0
    for s in splits:
        print(f"{s:<10} {len(speakers_by_split[s]):>8} {minutes_by_split[s]:>10.1f}")
        total += minutes_by_split[s]
    print(f"{'TOTAL':<10} {'':>8} {total:>10.1f}  ({total/60:.2f} hours)")
    print()

    for w in warnings[:20]:
        print(f"WARN  {w}")
    if len(warnings) > 20:
        print(f"WARN  ... and {len(warnings) - 20} more")

    if errors:
        print()
        for e in errors[:40]:
            print(f"FAIL  {e}")
        if len(errors) > 40:
            print(f"FAIL  ... and {len(errors) - 40} more")
        print(f"\n{len(errors)} error(s). Manifests are NOT usable.")
        return 1

    print("OK: manifests valid, splits speaker-disjoint.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data/manifests/"))
