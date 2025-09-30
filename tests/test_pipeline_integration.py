"""Integration tests for the video processing pipeline."""
import shutil
from pathlib import Path
import subprocess
import pytest

from src.video_cli.pipeline import run_pipeline, probe_duration

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None, 
    reason="ffmpeg/ffprobe not installed"
)


def ff(cmd):
    """Run ffmpeg command and assert success."""
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    assert proc.returncode == 0, proc.stdout


def make_sample_inputs(base: Path):
    vdir = base / "Video"; vdir.mkdir(parents=True, exist_ok=True)
    cdir = base / "Caption"; cdir.mkdir(parents=True, exist_ok=True)
    adir = base / "BGM"; adir.mkdir(parents=True, exist_ok=True)
    outdir = base / "Output"; outdir.mkdir(parents=True, exist_ok=True)

    v1 = vdir / "A.mp4"
    v2 = vdir / "B.mp4"

    # 2s color videos with sine audio
    ff([FFMPEG, "-y", "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=30", "-f", "lavfi", "-i", "sine=f=440:duration=2", "-shortest", "-c:v", "libx264", "-t", "2", str(v1)])
    ff([FFMPEG, "-y", "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=30", "-f", "lavfi", "-i", "sine=f=660:duration=2", "-shortest", "-c:v", "libx264", "-t", "2", str(v2)])

    # SRTs matching
    (cdir / "A.srt").write_text("1\n00:00:00,000 --> 00:00:01,500\nHello A\n\n")
    (cdir / "B.srt").write_text("1\n00:00:00,000 --> 00:00:01,500\nHello B\n\n")

    # BGM 10s sine
    bgm = adir / "bgm.wav"
    ff([FFMPEG, "-y", "-f", "lavfi", "-i", "sine=f=220:duration=10", str(bgm)])

    return vdir, cdir, adir, outdir


def test_pipeline_end_to_end(tmp_path: Path):
    vdir, cdir, adir, outdir = make_sample_inputs(tmp_path)
    out = outdir / "merged.mp4"
    result = run_pipeline(
        video_dir=vdir,
        caption_dir=cdir,
        bgm_dir=adir,
        output_dir=outdir,
        output_file=out,
        exts=[".mp4"],
        bgm_file=None,
        bgm_volume=0.2,
        burn_in=False,
        generate_captions=False,
        language="en-US",
        sample_rate=16000,
        keep_temp=False,
    )

    assert result.exists()
    dur = probe_duration(result)
    assert 3.5 <= dur <= 5.0  # two 2s videos -> ~4s
