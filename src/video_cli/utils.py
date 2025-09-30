"""Utility functions for file system operations and directory management."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional


def ensure_dir(p: Path) -> None:
    """Create directory and all parent directories if they don't exist."""
    p.mkdir(parents=True, exist_ok=True)


def find_files_sorted(folder: Path, exts: List[str]) -> List[Path]:
    """Find files with specified extensions and return sorted by name."""
    exts_norm = {e.lower() for e in exts}
    files = [p for p in folder.glob("**/*") if p.is_file() and p.suffix.lower() in exts_norm]
    return sorted(files, key=lambda x: x.name.lower())


def pick_bgm_file(bgm_dir: Path) -> Optional[Path]:
    """Select the first audio file from BGM directory alphabetically."""
    if not bgm_dir.exists():
        return None
    candidates = find_files_sorted(bgm_dir, [".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"])
    return candidates[0] if candidates else None
