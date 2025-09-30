"""SRT subtitle file processing and manipulation utilities."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import datetime as dt
import srt as srtlib


def read_srt(path: Path) -> List[srtlib.Subtitle]:
    """Read and parse SRT subtitle file."""
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        return list(srtlib.parse(f.read()))


def write_srt(text_or_subs, path: Path) -> None:
    """Write subtitle data to SRT file."""
    if isinstance(text_or_subs, str):
        text = text_or_subs
    else:
        text = srtlib.compose(text_or_subs)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def shift_subtitles(subs: List[srtlib.Subtitle], offset_seconds: float) -> List[srtlib.Subtitle]:
    """Shift subtitle timings by specified offset."""
    offset = dt.timedelta(seconds=offset_seconds)
    shifted: List[srtlib.Subtitle] = []
    for sub in subs:
        shifted.append(
            srtlib.Subtitle(
                index=sub.index,
                start=sub.start + offset,
                end=sub.end + offset,
                content=sub.content,
                proprietary=sub.proprietary,
            )
        )
    return shifted


def merge_srts_for_videos(videos: List[Path], caption_dir: Path) -> Optional[List[srtlib.Subtitle]]:
    # Deprecated basic version kept for compatibility; accurate merging should be done with known durations.
    any_srt = False
    all_subs: List[srtlib.Subtitle] = []
    current_start = 0.0

    for v in videos:
        srt_path = caption_dir / (v.stem + ".srt")
        if srt_path.exists():
            any_srt = True
            subs = read_srt(srt_path)
            shifted = shift_subtitles(subs, current_start)
            all_subs.extend(shifted)
            # Update current_start by last end of these subs
            if shifted:
                current_start = shifted[-1].end.total_seconds()

    if not any_srt:
        combined = caption_dir / "combined.srt"
        if combined.exists():
            return read_srt(combined)
        return None

    # Fix indices
    for i, sub in enumerate(all_subs, start=1):
        sub.index = i
    return all_subs
