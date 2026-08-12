"""Shared helpers for the standalone RealSense capture scripts."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import cv2


def prepare_directory(path: str | Path) -> Path:
    """Create and return an output directory."""
    directory = Path(path).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def prepare_class_directories(root: str | Path) -> tuple[Path, Path]:
    """Create the conventional ``real`` and ``fake`` class directories."""
    root_directory = prepare_directory(root)
    return (
        prepare_directory(root_directory / "real"),
        prepare_directory(root_directory / "fake"),
    )


def unique_image_path(directory: Path, prefix: str, extension: str) -> Path:
    """Return a collision-resistant image path without overwriting old data."""
    normalized_extension = extension.lower().lstrip(".")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    while True:
        candidate = directory / (
            f"{prefix}_{timestamp}_{uuid4().hex[:8]}.{normalized_extension}"
        )
        if not candidate.exists():
            return candidate


def save_image_checked(
    image,
    directory: Path,
    prefix: str,
    extension: str,
    params: Iterable[int] | None = None,
) -> Path:
    """Save an image and raise a clear error when OpenCV reports failure."""
    path = unique_image_path(directory, prefix, extension)
    options = list(params) if params is not None else []
    if not cv2.imwrite(str(path), image, options):
        raise OSError(f"OpenCV failed to write image: {path}")
    return path


def enable_selected_device(config, serial: str | None) -> None:
    """Select a RealSense by serial number when one was requested."""
    if serial:
        config.enable_device(serial)
