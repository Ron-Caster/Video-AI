from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile
import os

from .srt_utils import merge_srts_for_videos, write_srt
from .stt_google import transcribe_to_srt
from .utils import find_files_sorted, ensure_dir, pick_bgm_file


FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


def run(cmd: List[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\nOutput:\n{proc.stdout}")


def probe_duration(path: Path) -> float:
    cmd = [
        FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {proc.stdout}")
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def build_concat_file(videos: List[Path], concat_list_path: Path) -> None:
    with concat_list_path.open("w", encoding="utf-8") as f:
        for v in videos:
            f.write(f"file '{v.as_posix()}'\n")


def normalize_video(input_path: Path, output_path: Path) -> None:
    # Re-encode to a common format (H.264/AAC), 1080p max, 30fps, 2ch
    cmd = [
        FFMPEG, "-y",
        "-i", str(input_path),
        "-vf", "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease,fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2",
        str(output_path),
    ]
    run(cmd)


def concat_videos(videos: List[Path], tmpdir: Path, output_path: Path) -> Path:
    # Normalize first to avoid concat issues
    norm_paths: List[Path] = []
    for i, v in enumerate(videos):
        norm = tmpdir / f"norm_{i:03d}.mp4"
        normalize_video(v, norm)
        norm_paths.append(norm)

    concat_list = tmpdir / "concat.txt"
    build_concat_file(norm_paths, concat_list)

    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(output_path)]
    # If copy fails due to slight mismatches, re-encode on concat
    try:
        run(cmd)
    except RuntimeError:
        cmd = [
            FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ac", "2",
            str(output_path),
        ]
        run(cmd)
    return output_path


def mix_bgm(video_path: Path, bgm_path: Path, out_path: Path, bgm_volume: float = 0.15) -> Path:
    # duck original audio if too loud? For now, just mix with set volume and trim bgm via adelay/atrim
    # Use shortest to cut bgm when video ends
    vol = max(0.0, min(2.0, bgm_volume))
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-i", str(bgm_path),
        "-filter_complex",
        f"[1:a]volume={vol}[bgm];[0:a][bgm]amix=inputs=2:duration=shortest:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ]
    run(cmd)
    return out_path


def add_subtitles_soft(input_video: Path, srt_file: Path, out_path: Path) -> Path:
    cmd = [
        FFMPEG, "-y",
        "-i", str(input_video),
        "-i", str(srt_file),
        "-c", "copy",
        "-c:s", "mov_text",
        "-map", "0:v",
        "-map", "0:a?",
        "-map", "1:s:0?",
        str(out_path),
    ]
    run(cmd)
    return out_path


def _escape_path_for_subtitles_filter(p: Path) -> str:
    # On Windows, use native backslash paths and escape backslashes for filter
    s = str(p.resolve())
    # Escape backslashes for filter syntax
    s = s.replace("\\", "\\\\")
    return s


def add_subtitles_burn(input_video: Path, srt_file: Path, out_path: Path) -> Path:
    # Use libass filter instead of subtitles for better Windows compatibility
    srt_path = str(srt_file.resolve()).replace("\\", "/")
    cmd = [
        FFMPEG, "-y",
        "-i", str(input_video),
        "-vf", f"ass='{srt_path}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "copy",
        str(out_path),
    ]
    # If ass filter fails, try subtitles with file input
    try:
        run(cmd)
    except RuntimeError:
        # Fallback: copy SRT to a simple filename and use that
        simple_srt = out_path.parent / "subs.srt"
        shutil.copy2(srt_file, simple_srt)
        cmd = [
            FFMPEG, "-y",
            "-i", str(input_video),
            "-vf", f"subtitles={simple_srt.name}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "copy",
            str(out_path),
        ]
        # Change working directory to temp dir for relative path
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(simple_srt.parent)
            run(cmd)
        finally:
            os.chdir(old_cwd)
    return out_path


def run_pipeline(
    video_dir: Path,
    caption_dir: Path,
    bgm_dir: Path,
    output_dir: Path,
    output_file: Optional[Path],
    exts: List[str],
    bgm_file: Optional[Path],
    bgm_volume: float,
    burn_in: bool,
    generate_captions: bool,
    language: str,
    sample_rate: int,
    keep_temp: bool,
) -> Path:
    ensure_dir(output_dir)

    videos = find_files_sorted(video_dir, exts)
    if not videos:
        raise FileNotFoundError(f"No input videos found in {video_dir}")

    out_video = output_file or (output_dir / "merged.mp4")

    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)
        merged = tmpdir / "merged.mp4"
        concat_videos(videos, tmpdir, merged)

        # Captions handling
        srt_path: Optional[Path] = None
        # Merge SRTs per video using cumulative durations for accurate offsets
        srt_merged = tmpdir / "merged.srt"
        durations = [probe_duration(v) for v in videos]
        all_srt = []
        any_srt = False
        cum = 0.0
        for v, d in zip(videos, durations):
            sp = caption_dir / f"{v.stem}.srt"
            if sp.exists():
                from .srt_utils import read_srt, shift_subtitles
                subs = read_srt(sp)
                shifted = shift_subtitles(subs, cum)
                all_srt.extend(shifted)
                any_srt = True
            cum += max(0.0, d)
        if any_srt:
            write_srt(all_srt, srt_merged)
            srt_path = srt_merged
        elif (caption_dir / "combined.srt").exists():
            shutil.copy2(caption_dir / "combined.srt", srt_merged)
            srt_path = srt_merged
        elif generate_captions:
            # Extract audio and call Google STT
            audio_wav = tmpdir / "audio.wav"
            cmd = [
                FFMPEG, "-y", "-i", str(merged),
                "-ac", "1", "-ar", str(sample_rate), "-vn",
                str(audio_wav),
            ]
            run(cmd)
            srt_text = transcribe_to_srt(audio_wav, language=language, sample_rate=sample_rate)
            write_srt(srt_text, srt_merged)
            srt_path = srt_merged

        # BGM selection
        if bgm_file and bgm_file.exists():
            bgm = bgm_file
        else:
            bgm = pick_bgm_file(bgm_dir)

        current_video = merged
        if srt_path:
            subbed = tmpdir / ("subbed.mp4" if not burn_in else "burned.mp4")
            if burn_in:
                add_subtitles_burn(current_video, srt_path, subbed)
            else:
                add_subtitles_soft(current_video, srt_path, subbed)
            current_video = subbed

        if bgm:
            mixed = tmpdir / "mixed.mp4"
            # Choose mix strategy based on whether original video has audio
            if _has_audio(current_video):
                mix_bgm(current_video, bgm, mixed, bgm_volume=bgm_volume)
            else:
                # No original audio: map BGM as the only audio, cut off to video length using -shortest
                cmd = [
                    FFMPEG, "-y",
                    "-i", str(current_video),
                    "-i", str(bgm),
                    "-filter:a:1", f"volume={max(0.0, min(2.0, bgm_volume))}",
                    "-shortest",
                    "-map", "0:v",
                    "-map", "1:a",
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k",
                    str(mixed),
                ]
                run(cmd)
            current_video = mixed

        # Move to final output
        ensure_dir(out_video.parent)
        shutil.copy2(current_video, out_video)

        if keep_temp:
            # copy artifacts for inspection
            shutil.copy2(merged, output_dir / merged.name)
            if srt_path:
                shutil.copy2(srt_path, output_dir / srt_path.name)

    return out_video


def _has_audio(path: Path) -> bool:
    cmd = [FFPROBE, "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        return False
    return proc.stdout.strip() != ""
