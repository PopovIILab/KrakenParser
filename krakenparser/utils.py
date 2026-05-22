# krakenparser/utils.py
from pathlib import Path


def ensure_output_dir(path: str | Path, is_file: bool = True) -> Path:
    """Create parent directory for a file output, or the directory itself."""
    p = Path(path)
    target = p.parent if is_file else p
    target.mkdir(parents=True, exist_ok=True)
    return p
