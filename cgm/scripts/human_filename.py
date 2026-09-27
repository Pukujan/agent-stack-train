#!/usr/bin/env python3
"""Speakable generated artifact / asset filenames (CGM 0.5.5+).

Adopters MUST call this before writing generated media. Default output is a
**speakable** basename (identity first; omit default pitch/speed). Optional
``style="safe_twin"`` yields a machine-safe twin. Never emit opaque ``p0`` /
short-hash stems, and never emit robot ``key-value`` stems such as
``pitch-plus-8st``.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal, Union

Style = Literal["speakable", "safe_twin"]

# En dash between identity and modifier phrases (speakable style).
_SPEAKABLE_SEP = "–"  # en dash
_SAFE_SEP = "--"

# Classic hashy junk: song_food-p0-00e86d.mp3 / song_food-p20-8eb807.wav
_HASHY_BASENAME = re.compile(
    r"(?i)^(?P<head>.+)-p(?P<tag>\d+)-(?P<hex>[0-9a-f]{6})\.(?P<ext>[a-z0-9]+)$"
)

# Rejected robot key=value stems from the first 0.5.5 draft UX.
_ROBOT_KV = re.compile(r"(?i)_(?:pitch|speed|rate)-[a-z0-9.+-]+")

_UNSAFE = re.compile(r"[^a-z0-9._+-]+")
_MULTI_DASH = re.compile(r"-{2,}")
_PITCH_TOKEN = re.compile(
    r"(?i)^\s*(?:pitch\s*[:=]?\s*)?(?P<sign>[+-])?(?P<num>\d+)\s*(?:st|semitones?)?\s*$"
)
_SPEED_TOKEN = re.compile(
    r"(?i)^\s*(?:speed\s*[:=]?\s*)?(?P<sign>[+-])?(?P<num>\d+(?:\.\d+)?)\s*%?\s*"
    r"(?P<word>faster|slower)?\s*$"
)


def sanitize_label(value: object) -> str:
    """Filesystem-safe token for safe-twin segments: lowercase, spaces to -."""
    text = str(value if value is not None else "").strip().lower()
    text = re.sub(r"\+(?=\d)", "plus-", text)
    text = text.replace("+", "plus")
    text = text.replace("%", "-pct")
    text = text.replace(" ", "-").replace("/", "-").replace("\\", "-")
    text = text.replace("–", "-").replace("—", "-")
    text = _UNSAFE.sub("-", text)
    text = _MULTI_DASH.sub("-", text).strip("-._")
    return text or "unnamed"


def _normalize_extension(extension: str) -> str:
    ext = str(extension or "").strip().lower().lstrip(".")
    if not ext or not re.fullmatch(r"[a-z0-9]+", ext):
        raise ValueError(f"extension must be alphanumeric, got {extension!r}")
    return ext


def _parse_pitch_semitones(pitch: object | None) -> int | None:
    """Return signed semitone delta, or None when default / omitted."""
    if pitch is None:
        return None
    if isinstance(pitch, bool):
        raise TypeError("pitch must be int/str/None, not bool")
    if isinstance(pitch, (int, float)):
        value = int(pitch)
        return None if value == 0 else value
    text = str(pitch).strip()
    if not text or text.lower() in {"default", "none", "0", "+0", "-0", "0st", "+0st"}:
        return None
    speakable = re.fullmatch(r"(?i)\s*(up|down)\s+(\d+)\s*", text)
    if speakable:
        magnitude = int(speakable.group(2))
        if magnitude == 0:
            return None
        return magnitude if speakable.group(1).lower() == "up" else -magnitude
    match = _PITCH_TOKEN.fullmatch(text)
    if not match:
        raise ValueError(f"unrecognized pitch value: {pitch!r}")
    magnitude = int(match.group("num"))
    if magnitude == 0:
        return None
    sign = match.group("sign") or "+"
    return magnitude if sign != "-" else -magnitude


def _parse_speed_pct(speed_pct: object | None) -> float | None:
    """Return signed percent speed delta, or None when default / omitted."""
    if speed_pct is None:
        return None
    if isinstance(speed_pct, bool):
        raise TypeError("speed_pct must be number/str/None, not bool")
    if isinstance(speed_pct, (int, float)):
        value = float(speed_pct)
        return None if value == 0 else value
    text = str(speed_pct).strip()
    if not text or text.lower() in {"default", "none", "0", "+0", "-0", "0%", "+0%", "0pct"}:
        return None
    match = _SPEED_TOKEN.fullmatch(text)
    if not match:
        raise ValueError(f"unrecognized speed_pct value: {speed_pct!r}")
    magnitude = float(match.group("num"))
    if magnitude == 0:
        return None
    word = (match.group("word") or "").lower()
    sign = match.group("sign") or "+"
    if word == "slower" or sign == "-":
        return -magnitude
    return magnitude


def pitch_phrase(pitch: object | None) -> str | None:
    """Human phrase for pitch, or None when at default (omit from basename)."""
    delta = _parse_pitch_semitones(pitch)
    if delta is None:
        return None
    if delta > 0:
        return f"up {delta}"
    return f"down {abs(delta)}"


def speed_phrase(speed_pct: object | None) -> str | None:
    """Human phrase for speed, or None when at default (omit from basename)."""
    delta = _parse_speed_pct(speed_pct)
    if delta is None:
        return None
    if float(delta).is_integer():
        magnitude: int | float = abs(int(delta))
    else:
        magnitude = abs(delta)
    if delta > 0:
        return f"{magnitude}% faster"
    return f"{magnitude}% slower"


def _modifier_phrases(
    *,
    pitch: object | None = None,
    speed_pct: object | None = None,
) -> list[str]:
    phrases: list[str] = []
    # Order is fixed: identity -> pitch -> speed.
    pitch_text = pitch_phrase(pitch)
    if pitch_text:
        phrases.append(pitch_text)
    speed_text = speed_phrase(speed_pct)
    if speed_text:
        phrases.append(speed_text)
    return phrases


def _identity_text(identity: object) -> str:
    text = str(identity if identity is not None else "").strip()
    if not text:
        raise ValueError("identity must be a non-empty string")
    return text


def _append_optional_suffixes(
    stem: str,
    *,
    style: Style,
    disambiguator: str | None,
    content_hash: str | None,
) -> str:
    parts = [stem]
    if disambiguator:
        token = str(disambiguator).strip()
        if token:
            if style == "safe_twin":
                parts.append(sanitize_label(token))
            else:
                parts.append(token)
    if content_hash:
        digest = sanitize_label(content_hash)
        if len(digest) > 12:
            digest = digest[:12]
        if digest:
            parts.append(digest)
    if style == "safe_twin":
        return _SAFE_SEP.join(p for p in parts if p)
    if len(parts) == 1:
        return parts[0]
    return " ".join(parts)


def build_basename(
    identity: str,
    extension: str,
    *,
    pitch: object | None = None,
    speed_pct: object | None = None,
    style: Style = "speakable",
    disambiguator: str | None = None,
    content_hash: str | None = None,
) -> str:
    """Build a speakable (default) or machine-safe-twin basename.

    Examples::

        build_basename("Song Food", "mp3")
        # -> "Song Food.mp3"

        build_basename("Song Food", "mp3", pitch=8)
        # -> "Song Food – up 8.mp3"

        build_basename("Song Food", "mp3", pitch=8, speed_pct=20)
        # -> "Song Food – up 8, 20% faster.mp3"

        build_basename(
            "Song Food", "mp3", pitch=8, speed_pct=20, style="safe_twin"
        )
        # -> "song-food--up-8--20-pct-faster.mp3"

    Default pitch/speed are **omitted**. ``content_hash`` appends only after
    human labels, never instead of them.
    """
    if style not in ("speakable", "safe_twin"):
        raise ValueError(f"style must be 'speakable' or 'safe_twin', got {style!r}")

    identity_text = _identity_text(identity)
    phrases = _modifier_phrases(pitch=pitch, speed_pct=speed_pct)
    ext = _normalize_extension(extension)

    if style == "speakable":
        if phrases:
            stem = f"{identity_text} {_SPEAKABLE_SEP} {', '.join(phrases)}"
        else:
            stem = identity_text
        stem = _append_optional_suffixes(
            stem, style=style, disambiguator=disambiguator, content_hash=content_hash
        )
        return f"{stem}.{ext}"

    segments = [sanitize_label(identity_text)]
    for phrase in phrases:
        segments.append(sanitize_label(phrase))
    stem = _SAFE_SEP.join(segments)
    stem = _append_optional_suffixes(
        stem, style=style, disambiguator=disambiguator, content_hash=content_hash
    )
    return f"{stem}.{ext}"


def build_relative_path(
    identity: str,
    extension: str,
    *,
    parent: str | None = None,
    pitch: object | None = None,
    speed_pct: object | None = None,
    style: Style = "speakable",
    disambiguator: str | None = None,
    content_hash: str | None = None,
) -> str:
    """Basename plus optional parent folder (forward-slash relative path).

    Folders by identity are optional; the basename still repeats the identity.
    """
    name = build_basename(
        identity,
        extension,
        pitch=pitch,
        speed_pct=speed_pct,
        style=style,
        disambiguator=disambiguator,
        content_hash=content_hash,
    )
    if not parent:
        return name
    raw = str(parent).replace("\\", "/").strip("/")
    if not raw:
        return name
    if style == "safe_twin":
        folder = "/".join(sanitize_label(part) for part in raw.split("/") if part)
    else:
        folder = "/".join(part.strip() for part in raw.split("/") if part.strip())
    return f"{folder}/{name}" if folder else name


def build_basename_from_dimensions(
    dimensions: Union[Mapping[str, object], Sequence[tuple[str, object]]],
    extension: str,
    *,
    style: Style = "speakable",
    disambiguator: str | None = None,
    content_hash: str | None = None,
) -> str:
    """Map line/pitch/speed keys onto :func:`build_basename`."""
    if isinstance(dimensions, Mapping):
        pairs = list(dimensions.items())
    else:
        pairs = [(str(k), v) for k, v in dimensions]

    identity: object | None = None
    pitch: object | None = None
    speed: object | None = None
    for key, value in pairs:
        key_l = str(key).strip().lower()
        if key_l in {"line", "stem", "name", "title", "base", "identity"} and identity is None:
            identity = value
        elif key_l == "pitch" and pitch is None:
            pitch = value
        elif key_l in {"speed", "speed_pct", "rate"} and speed is None:
            speed = value
    if identity is None:
        raise ValueError(
            "dimensions must include an identity key (line/stem/name/title/base/identity)"
        )
    return build_basename(
        str(identity),
        extension,
        pitch=pitch,
        speed_pct=speed,
        style=style,
        disambiguator=disambiguator,
        content_hash=content_hash,
    )


def is_hashy_junk_basename(name: str) -> bool:
    """True when the basename matches classic ``stem-pN-<6hex>.ext`` folklore."""
    base = str(name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    match = _HASHY_BASENAME.fullmatch(base)
    if not match:
        return False
    return len(match.group("hex")) == 6


def is_robot_key_value_basename(name: str) -> bool:
    """True for rejected robot stems like ``…_pitch-plus-8st_speed-0pct.mp3``."""
    base = str(name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not base or is_hashy_junk_basename(base):
        return False
    return bool(_ROBOT_KV.search(base))


def is_accepted_basename(name: str) -> bool:
    """True when basename is speakable or safe-twin shaped (not hashy / robot)."""
    base = str(name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not base or "." not in base:
        return False
    if is_hashy_junk_basename(base) or is_robot_key_value_basename(base):
        return False
    stem = base.rsplit(".", 1)[0]
    if not stem or re.search(r"[A-Za-z]", stem) is None:
        return False
    if re.fullmatch(r"[0-9a-f]{6,}", stem):
        return False
    if _SAFE_SEP in stem:
        return stem == stem.lower() and bool(
            re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*(?:--[a-z0-9]+(?:-[a-z0-9]+)*)+",
                stem,
            )
        )
    return True


def expected_basename(
    identity: str,
    extension: str,
    *,
    pitch: object | None = None,
    speed_pct: object | None = None,
    style: Style = "speakable",
    disambiguator: str | None = None,
    content_hash: str | None = None,
) -> str:
    """Alias used by legend validators — same as :func:`build_basename`."""
    return build_basename(
        identity,
        extension,
        pitch=pitch,
        speed_pct=speed_pct,
        style=style,
        disambiguator=disambiguator,
        content_hash=content_hash,
    )


def legend_paths(root: Path, *, adapter: bool = False) -> list[Path]:
    """Return filename-legend JSON paths under docs/ or .content-system/."""
    if adapter:
        base = root / ".content-system" / "filename-legends"
    else:
        base = root / "docs" / "filename-legends"
    if not base.is_dir():
        return []
    return sorted(base.glob("*.json"))


__all__ = [
    "build_basename",
    "build_basename_from_dimensions",
    "build_relative_path",
    "expected_basename",
    "is_accepted_basename",
    "is_hashy_junk_basename",
    "is_robot_key_value_basename",
    "legend_paths",
    "pitch_phrase",
    "sanitize_label",
    "speed_phrase",
]
