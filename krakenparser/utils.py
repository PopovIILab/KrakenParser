#!/usr/bin/env python3
"""Shared utility wrappers and filesystem helpers for the KrakenParser suite.

This module provides low-level infrastructure operations, such as safe path
resolution and idempotent directory creation, ensuring robust filesystem execution
across diverse operating systems.
"""

from pathlib import Path


def ensure_output_dir(path: str | Path, is_file: bool = True) -> Path:
    """Ensure the target directory or parent directory tree exists layout-ready.

    If the output target is designated as a file, this utility creates its
    containing parent directory. If designated as a directory, it constructs
    the target directory itself. Operations are idempotent (`exist_ok=True`).

    Args:
        path: A string path or Path object representing the targeted filesystem entry.
        is_file: If True, treats the path as a file and ensures its parent directory
            exists. If False, treats the entire path as a directory to create.

    Returns:
        Path: A fully instantiated Path object pointing to the original target destination.
    """
    path_obj: Path = Path(path)

    # Resolve whether to isolate the parent directory or target the path directly
    target_dir: Path = path_obj.parent if is_file else path_obj
    target_dir.mkdir(parents=True, exist_ok=True)

    return path_obj
