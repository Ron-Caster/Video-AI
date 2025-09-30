"""Unit tests for SRT subtitle utilities."""
from pathlib import Path
from src.video_cli.srt_utils import write_srt, read_srt


def test_write_and_read_srt(tmp_path: Path):
    """Test SRT file read/write functionality."""
    srt_text = "1\n00:00:00,000 --> 00:00:02,000\nHello world\n\n"
    p = tmp_path / 'a.srt'
    write_srt(srt_text, p)
    subs = read_srt(p)
    assert len(subs) == 1
    assert subs[0].content.strip() == 'Hello world'
