"""Per-directory session configuration loaded from ~/.ccgram/dir-configs.toml.

Config file format:

    [dirs."~/Development/myproject"]
    provider = "shell"
    auto = true
    init_command = "source ~/.zshrc"

``auto = true`` causes CCGram to skip the provider/mode picker and create the
window immediately when the directory is confirmed in the browser.
``init_command`` is sent to the pane after shell prompt setup (shell provider
only; ignored for other providers).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import structlog

logger = structlog.get_logger()

_CONFIG_FILE = Path("~/.ccgram/dir-configs.toml")


@dataclass(frozen=True)
class DirConfig:
    provider: str = "shell"
    auto: bool = False
    init_command: str = ""


def _load_raw() -> dict:
    path = _CONFIG_FILE.expanduser()
    if not path.exists():
        return {}
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        logger.exception("Failed to load dir-configs.toml at %s", path)
        return {}


def get_dir_config(directory: str) -> DirConfig | None:
    """Return the ``DirConfig`` for *directory*, or ``None`` if unconfigured.

    Matching is done after ``~`` expansion and ``Path.resolve()`` normalization.
    Exact match only — subdirectories do not inherit parent config.
    """
    raw = _load_raw()
    dirs: dict = raw.get("dirs", {})
    if not dirs:
        return None

    target = Path(directory).expanduser().resolve()
    for raw_path, settings in dirs.items():
        if not isinstance(settings, dict):
            continue
        candidate = Path(raw_path).expanduser().resolve()
        if candidate == target:
            return DirConfig(
                provider=str(settings.get("provider", "shell")),
                auto=bool(settings.get("auto", False)),
                init_command=str(settings.get("init_command", "")),
            )
    return None
