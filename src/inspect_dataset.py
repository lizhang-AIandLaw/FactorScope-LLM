"""Audit the released corpus without loading model dependencies."""

import argparse
import hashlib
import json
from pathlib import Path

FIELDS = ["text", "factor", "label", "split", "industry", "secret_type", "style"]
SPLITS = ("train", "test")


def _factor_key(path: Path) -> int:
    return int(path.name.removeprefix("F"))


def _read_jsonl(path: Path, digest):
    with path.open("rb") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            digest.update(raw_line)
            try:
                yield json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_number}") from exc


def _check_record(row: dict, path: Path, texts: set) -> None:
    if sorted(row) != sorted(FIELDS):
        raise ValueError(f"unexpected fields in {path}: {sorted(row)}")
    if row["split"] not in SPLITS:
        raise ValueError(f"invalid split in {path}: {row['split']}")
    text = row["text"]
    if not text or text in texts:
        raise ValueError(f"empty or duplicate passage in {path}")
    texts.add(text)


def audit_dataset(data_root: Path) -> dict:
    classification_root = data_root / "classification"
    factor_dirs = sorted(
        (
            path
            for path in classification_root.iterdir()
            if path.is_dir() and (path / "pos.jsonl").exists()
        ),
        key=_factor_key,
    )
    factor_ids = [path.name for path in factor_dirs]

    digest = hashlib.sha256()
    texts = set()
    counts = {}
    split_counts = {split: {"positive": 0, "neutral": 0} for split in SPLITS}
    for factor_dir in factor_dirs:
        path = factor_dir / "pos.jsonl"
        count = 0
        for row in _read_jsonl(path, digest):
            _check_record(row, path, texts)
            if row["factor"] != factor_dir.name or row["label"] != 1:
                raise ValueError(f"invalid positive label in {path}")
            split_counts[row["split"]]["positive"] += 1
            count += 1
        counts[factor_dir.name] = count

    neutral_count = 0
    neutral_path = classification_root / "neutral.jsonl"
    for row in _read_jsonl(neutral_path, digest):
        _check_record(row, neutral_path, texts)
        if row["factor"] != "NONE" or row["label"] != 0:
            raise ValueError(f"invalid neutral label in {neutral_path}")
        split_counts[row["split"]]["neutral"] += 1
        neutral_count += 1

    return {
        "factor_ids": factor_ids,
        "classification": {
            "positive_passages": sum(counts.values()),
            "neutral_passages": neutral_count,
            "counts_by_factor": counts,
            "counts_by_split": split_counts,
            "passages_unique": True,
            "fields": FIELDS,
            "sha256": digest.hexdigest(),
        },
    }


def verify_manifest(report: dict, manifest: dict) -> None:
    if report["factor_ids"] != manifest["factor_ids"]:
        raise ValueError("factor list differs from data/manifest.json")
    for key in ("positive_passages", "neutral_passages", "counts_by_split", "sha256"):
        if report["classification"][key] != manifest["classification"][key]:
            raise ValueError(f"classification {key} differs from the manifest")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    parser.add_argument("--verify-manifest", action="store_true")
    parser.add_argument("--write-manifest", action="store_true",
                        help="rewrite data/manifest.json from the audited corpus")
    args = parser.parse_args()
    report = audit_dataset(args.data_root)
    manifest_path = args.data_root / "manifest.json"
    if args.write_manifest:
        manifest = {
            "version": "1.0",
            "factor_ids": report["factor_ids"],
            "classification": {
                key: report["classification"][key]
                for key in ("positive_passages", "neutral_passages",
                            "counts_by_split", "sha256")
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    if args.verify_manifest:
        manifest = json.loads(manifest_path.read_text())
        verify_manifest(report, manifest)
        report["manifest_verified"] = True
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
