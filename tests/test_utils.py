"""Unit tests for utility functions."""
from pathlib import Path
from src.video_cli.utils import find_files_sorted


def test_find_files_sorted(tmp_path: Path):
    """Test file discovery and sorting functionality."""
    (tmp_path / 'a.mp4').write_text('')
    (tmp_path / 'C.MP4').write_text('')
    (tmp_path / 'b.mov').write_text('')
    files = find_files_sorted(tmp_path, ['.mp4', '.mov'])
    assert [f.name for f in files] == ['a.mp4', 'b.mov', 'C.MP4']
