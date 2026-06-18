#!/usr/bin/env python3
"""Windows Explorer Goblin suggestion brain.

Reads a small request JSON file and writes ranked suggestions as TSV lines:

    suggestion<TAB>score<TAB>reason

The AutoHotkey frontend keeps UI control. This module stays fast,
dependency-free, and replaceable. Later we can bolt in Ollama or a
small local model behind the same request/response contract.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "goblin_config.json"
DEFAULT_HISTORY = ROOT / "rename_history.jsonl"

SEPARATORS_RE = re.compile(r"[\s_\-.]+")
BPM_RE = re.compile(r"(?P<bpm>\d{2,3})\s*bpm", re.IGNORECASE)
KEY_RE = re.compile(r"(?P<key>[A-G](?:#|b)?)[_\-\s]?(?P<mode>major|minor|maj|min)", re.IGNORECASE)


@dataclass(frozen=True)
class Candidate:
    text: str
    source: str


@dataclass(frozen=True)
class Scored:
    text: str
    score: int
    reason: str


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def read_request(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_response(path: Path, rows: Sequence[Scored]) -> None:
    lines: list[str] = []
    for row in rows:
        safe_text = row.text.replace("\t", " ").replace("\n", " ").strip()
        safe_reason = row.reason.replace("\t", " ").replace("\n", " ").strip()
        lines.append(f"{safe_text}\t{row.score}\t{safe_reason}")
    path.write_text("\n".join(lines), encoding="utf-8")


def normalize(text: str) -> str:
    return text.strip().lower()


def tokenize(text: str) -> list[str]:
    return [t for t in SEPARATORS_RE.split(normalize(text)) if t]


def initials(text: str) -> str:
    return "".join(t[:1] for t in tokenize(text))


def subsequence_score(needle: str, haystack: str) -> int | None:
    n = normalize(needle)
    h = normalize(haystack)
    pos = 0
    score = 0
    for ch in n:
        found = h.find(ch, pos)
        if found < 0:
            return None
        score += found - pos
        pos = found + 1
    return score


def word_start_score(typed: str, candidate: str) -> int | None:
    t = normalize(typed)
    parts = tokenize(candidate)
    for index, part in enumerate(parts):
        if part.startswith(t):
            return 40 + index * 7 + abs(len(candidate) - len(typed))
    return None


def contains_score(typed: str, candidate: str) -> int | None:
    t = normalize(typed)
    c = normalize(candidate)
    pos = c.find(t)
    if pos >= 0:
        return 100 + pos + abs(len(candidate) - len(typed))
    return None


def structural_bonus(typed: str, candidate: str) -> int:
    """Bonus for common dataset/audio naming signals."""
    t = normalize(typed)
    c = normalize(candidate)
    bonus = 0

    if BPM_RE.search(c) and any(ch.isdigit() for ch in t):
        bonus -= 12

    if KEY_RE.search(c):
        key = KEY_RE.search(c)
        if key and normalize(key.group("key")) in t:
            bonus -= 12

    audio_terms = [
        "bass",
        "bassline",
        "break",
        "drum",
        "glitch",
        "lead",
        "loop",
        "melody",
        "sfx",
        "vocal",
    ]
    if any(term in c for term in audio_terms) and any(term[:2] in t for term in audio_terms):
        bonus -= 8

    return bonus


def score_candidate(typed: str, candidate: Candidate) -> Scored | None:
    t = normalize(typed)
    c = normalize(candidate.text)

    if not t or not c:
        return None

    if c == t:
        return Scored(candidate.text, 0, f"exact match from {candidate.source}")

    if c.startswith(t):
        score = 10 + abs(len(candidate.text) - len(typed))
        if candidate.source == "history":
            score -= 4
        score += structural_bonus(typed, candidate.text)
        return Scored(candidate.text, max(score, 1), f"prefix match from {candidate.source}")

    ws = word_start_score(typed, candidate.text)
    if ws is not None:
        score = ws + structural_bonus(typed, candidate.text)
        return Scored(candidate.text, max(score, 1), f"word-start match from {candidate.source}")

    cs = contains_score(typed, candidate.text)
    if cs is not None:
        score = cs + structural_bonus(typed, candidate.text)
        return Scored(candidate.text, max(score, 1), f"contains match from {candidate.source}")

    init = initials(candidate.text)
    if init.startswith(t):
        score = 160 + abs(len(candidate.text) - len(typed)) + structural_bonus(typed, candidate.text)
        return Scored(candidate.text, max(score, 1), f"initials match from {candidate.source}")

    sub = subsequence_score(typed, candidate.text)
    if sub is not None:
        score = 240 + sub + abs(len(candidate.text) - len(typed)) + structural_bonus(typed, candidate.text)
        return Scored(candidate.text, max(score, 1), f"fuzzy sequence from {candidate.source}")

    return None


def unique_candidates(candidates: Iterable[Candidate]) -> list[Candidate]:
    seen: set[str] = set()
    out: list[Candidate] = []
    for cand in candidates:
        text = cand.text.strip()
        if not text:
            continue
        key = normalize(text)
        if key in seen:
            continue
        seen.add(key)
        out.append(Candidate(text=text, source=cand.source))
    return out


def local_candidates(folder: Path, is_folder: bool, extension: str, current_name: str) -> list[Candidate]:
    out: list[Candidate] = []
    if not folder.exists() or not folder.is_dir():
        return out

    current_base = normalize(Path(current_name).stem if current_name else current_name)
    ext = normalize(extension).lstrip(".")

    try:
        children = list(folder.iterdir())
    except OSError:
        return out

    if is_folder:
        for child in children:
            if child.is_dir() and normalize(child.name) != current_base:
                out.append(Candidate(child.name, "sibling-folder"))
        return out

    same_ext: list[Candidate] = []
    other_ext: list[Candidate] = []
    for child in children:
        if not child.is_file():
            continue
        if normalize(child.stem) == current_base:
            continue
        if normalize(child.suffix).lstrip(".") == ext:
            same_ext.append(Candidate(child.stem, "same-extension"))
        else:
            other_ext.append(Candidate(child.stem, "nearby-file"))

    out.extend(same_ext)
    out.extend(other_ext)
    return out


def load_history(history_path: Path) -> list[Candidate]:
    if not history_path.exists():
        return []

    out: list[Candidate] = []
    try:
        for line in history_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                name = str(item.get("name", "")).strip()
            except Exception:
                name = line
            if name:
                out.append(Candidate(name, "history"))
    except OSError:
        return []
    return out


def save_history(name: str, history_path: Path) -> None:
    name = name.strip()
    if not name:
        return
    history_path.parent.mkdir(parents=True, exist_ok=True)
    existing = {normalize(c.text) for c in load_history(history_path)}
    if normalize(name) in existing:
        return
    with history_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")


def template_candidates(typed: str, config: dict) -> list[Candidate]:
    """Lightweight project-aware hints. These are intentionally conservative."""
    t = normalize(typed)
    out: list[Candidate] = []

    if not t:
        return out

    audio_terms = set(config.get("audio_keywords", []))
    if any(term in t for term in audio_terms) or any(part in t for part in ["bpm", "minor", "major", "loop"]):
        out.extend(
            [
                Candidate("author__publisher__genre__instrument__bpm__key__meter__sampletype", "template"),
                Candidate("samplefocus__glitch__lead-melody__145bpm__A-minor__4-4__loop", "template"),
            ]
        )

    if any(part in t for part in ["alb", "norm", "rough", "metal", "texture", "map"]):
        out.extend(
            [
                Candidate("material_albedo_1024_v01", "template"),
                Candidate("material_normal_1024_v01", "template"),
                Candidate("material_roughness_1024_v01", "template"),
            ]
        )

    return out


def rank_suggestions(request: dict, config: dict) -> list[Scored]:
    typed = str(request.get("typed", ""))
    folder = Path(str(request.get("folder", "")))
    is_folder = bool(request.get("is_folder", False))
    extension = str(request.get("extension", ""))
    current_name = str(request.get("current_name", ""))
    max_suggestions = int(request.get("max_suggestions", config.get("max_suggestions", 8)))

    history_path = Path(str(request.get("history_file", DEFAULT_HISTORY)))
    if not history_path.is_absolute():
        history_path = ROOT / history_path

    if request.get("learn"):
        save_history(str(request.get("learn", "")), history_path)
        return []

    candidates = unique_candidates(
        [
            *local_candidates(folder, is_folder, extension, current_name),
            *load_history(history_path),
            *template_candidates(typed, config),
        ]
    )

    scored: list[Scored] = []
    for cand in candidates:
        row = score_candidate(typed, cand)
        if row is not None:
            scored.append(row)

    scored.sort(key=lambda r: (r.score, len(r.text), r.text.lower()))
    return scored[:max_suggestions]


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows Explorer Goblin suggestion brain")
    parser.add_argument("--request", required=True, help="Path to request JSON")
    parser.add_argument("--out", required=True, help="Path to output TSV")
    args = parser.parse_args()

    config = load_config()
    request = read_request(Path(args.request))
    rows = rank_suggestions(request, config)
    write_response(Path(args.out), rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
