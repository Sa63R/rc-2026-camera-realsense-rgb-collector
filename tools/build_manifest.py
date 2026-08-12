#!/usr/bin/env python3
"""Build a relative-path and SHA-256 manifest for a reviewed capture directory."""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

IMAGE_SUFFIXES = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff"}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def infer_class(relative_path: Path) -> str:
    lowered_parts = [part.lower() for part in relative_path.parts[:-1]]
    for candidate in ("real", "fake"):
        if candidate in lowered_parts:
            return candidate
    return ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Capture directory to inventory.")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination CSV; keep it outside the Git repo until reviewed.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"Capture directory does not exist: {root}")
    if output.suffix.lower() != ".csv":
        raise SystemExit("--output must use the .csv extension.")
    if output == root or root in output.parents:
        raise SystemExit(
            "--output must be outside the capture root so generated metadata "
            "cannot pollute the scanned dataset."
        )
    output.parent.mkdir(parents=True, exist_ok=True)

    images = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=(
                "relative_path",
                "class_hint",
                "size_bytes",
                "modified_utc",
                "sha256",
            ),
        )
        writer.writeheader()
        for path in images:
            stat = path.stat()
            relative_path = path.relative_to(root)
            writer.writerow(
                {
                    "relative_path": relative_path.as_posix(),
                    "class_hint": infer_class(relative_path),
                    "size_bytes": stat.st_size,
                    "modified_utc": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                    "sha256": sha256_file(path),
                }
            )

    print(f"Wrote {len(images)} image records to {output}")
    print("Class hints come from folder names and are not validated labels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
