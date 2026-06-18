#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "goblin_config.json"
DEFAULT_HISTORY = ROOT / "rename_history.jsonl"
SPLIT_RE = re.compile(r"[\s_\-.]+")
BAD_RE = re.compile(r'[\\/:*?"<>|]')


def load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def norm(s: str) -> str:
    return str(s).strip().lower()


def clean(s: str) -> str:
    s = str(s).strip().strip("'\"`.,;:[]{}()")
    s = re.sub(r"\s+", " ", s)
    s = BAD_RE.sub("-", s).rstrip(". ")
    return s[:180]


def tokens(s: str) -> list[str]:
    return [x for x in SPLIT_RE.split(norm(s)) if x]


def initials(s: str) -> str:
    return "".join(x[0] for x in tokens(s) if x)


def subseq(a: str, b: str) -> int | None:
    a, b = norm(a), norm(b)
    pos = 0
    score = 0
    for ch in a:
        found = b.find(ch, pos)
        if found < 0:
            return None
        score += found - pos
        pos = found + 1
    return score


def read_history(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            name = json.loads(line).get("name", "")
        except Exception:
            name = line
        name = clean(name)
        if name:
            out.append((name, "history"))
    return out


def save_history(name: str, path: Path) -> None:
    name = clean(name)
    if not name:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {norm(x[0]) for x in read_history(path)}
    if norm(name) not in existing:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")


def sibling_candidates(folder: Path, is_folder: bool, ext: str, current: str) -> list[tuple[str, str]]:
    try:
        kids = list(folder.iterdir())
    except Exception:
        return []
    out = []
    cur = norm(Path(current).stem if current else current)
    ext = norm(ext).lstrip(".")
    if is_folder:
        for k in kids:
            if k.is_dir() and norm(k.name) != cur:
                out.append((k.name, "folder nearby"))
        return out
    for k in kids:
        if k.is_file() and norm(k.stem) != cur:
            src = "same extension" if norm(k.suffix).lstrip(".") == ext else "nearby file"
            out.append((k.stem, src))
    return out


def fallback_candidates(typed: str, folder: Path, is_folder: bool, cfg: dict) -> list[tuple[str, str]]:
    base = list(cfg.get("fallback_dictionary", []))
    if is_folder:
        base += ["examples", "experiments", "exports", "explorer-goblin-experiments", "explorer-overlay-tests", "extension-tests"]
    for part in folder.parts[-5:]:
        p = norm(part)
        if p and p not in {"users", "documents", "desktop", "downloads"}:
            base += [p, f"{p}-examples", f"{p}-experiments", f"{p}-exports"]
    expansions = {
        "ex": ["examples", "experiments", "exports", "explorer-goblin-experiments", "extension-tests"],
        "exp": ["experiments", "exports", "explorer-goblin-experiments"],
        "sam": ["samples", "sample-packs", "samplefocus-catalog"],
        "dat": ["dataset", "datasets", "training-data"],
        "tex": ["textures", "texture-maps", "texture-map-tests"],
        "aud": ["audio-samples", "audio-dataset", "audio-training-data"],
        "doc": ["docs", "documentation", "notes"],
        "src": ["src", "source", "source-experiments"],
    }
    base += expansions.get(norm(typed), [])
    out = []
    for x in base:
        x = clean(x)
        if x:
            out.append((x, "fallback brain"))
    return out


def template_candidates(typed: str) -> list[tuple[str, str]]:
    t = norm(typed)
    out = []
    if any(x in t for x in ["sam", "aud", "bpm", "loop", "bass", "glitch"]):
        out += [
            ("author__publisher__genre__instrument__bpm__key__meter__sampletype", "audio template"),
            ("samplefocus__glitch__lead-melody__145bpm__A-minor__4-4__loop", "audio template"),
        ]
    if any(x in t for x in ["tex", "map", "norm", "rough", "metal"]):
        out += [("material_albedo_1024_v01", "texture template"), ("material_normal_1024_v01", "texture template"), ("material_roughness_1024_v01", "texture template")]
    return out


def local_model_candidates(req: dict, cfg: dict, nearby: list[str]) -> list[tuple[str, str]]:
    slm = cfg.get("slm", {})
    if not slm.get("enabled", False) or shutil.which("ollama") is None:
        return []
    typed = str(req.get("typed", "")).strip()
    if len(typed) < int(slm.get("minimum_typed_length", 2)):
        return []
    model = str(slm.get("model", "qwen2.5:0.5b"))
    timeout = float(slm.get("timeout_seconds", 2.5))
    mode = "folder" if req.get("is_folder") else "file name"
    prompt = "Suggest 8 short Windows " + mode + " options. One name per line. Typed text: " + typed + ". Nearby names: " + ", ".join(nearby[:20])
    try:
        r = subprocess.run(["ollama", "run", model, prompt], text=True, capture_output=True, timeout=timeout, encoding="utf-8", errors="ignore")
    except Exception:
        return []
    if r.returncode != 0:
        return []
    out = []
    for line in r.stdout.splitlines():
        line = re.sub(r"^\s*[-*\d.)]+\s*", "", line)
        name = clean(line)
        if name:
            out.append((name, "local model"))
    return out[:8]


def unique(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen = set()
    out = []
    for name, src in items:
        name = clean(name)
        k = norm(name)
        if name and k not in seen:
            seen.add(k)
            out.append((name, src))
    return out


def score(typed: str, name: str, src: str) -> tuple[int, str] | None:
    t, n = norm(typed), norm(name)
    if not t or not n:
        return None
    bias = {"history": -10, "folder nearby": -8, "same extension": -8, "fallback brain": 4, "audio template": 12, "texture template": 12, "local model": 16}.get(src, 0)
    if n == t:
        return (0, "exact " + src)
    if n.startswith(t):
        return (max(1, 10 + len(n) - len(t) + bias), "prefix " + src)
    for i, part in enumerate(tokens(name)):
        if part.startswith(t):
            return (max(1, 40 + i * 7 + len(n) - len(t) + bias), "word-start " + src)
    pos = n.find(t)
    if pos >= 0:
        return (max(1, 100 + pos + len(n) - len(t) + bias), "contains " + src)
    if initials(name).startswith(t):
        return (max(1, 160 + len(n) - len(t) + bias), "initials " + src)
    sq = subseq(t, n)
    if sq is not None:
        return (max(1, 240 + sq + len(n) - len(t) + bias), "fuzzy " + src)
    return None


def rank(req: dict, cfg: dict) -> list[tuple[str, int, str]]:
    typed = str(req.get("typed", ""))
    folder = Path(str(req.get("folder", "")))
    hist = Path(str(req.get("history_file", DEFAULT_HISTORY)))
    if not hist.is_absolute():
        hist = ROOT / hist
    if req.get("learn"):
        save_history(str(req.get("learn", "")), hist)
        return []
    maxn = int(req.get("max_suggestions", cfg.get("max_suggestions", 8)))
    items = unique(sibling_candidates(folder, bool(req.get("is_folder")), str(req.get("extension", "")), str(req.get("current_name", ""))) + read_history(hist) + fallback_candidates(typed, folder, bool(req.get("is_folder")), cfg) + template_candidates(typed))
    scored = []
    for name, src in items:
        s = score(typed, name, src)
        if s:
            scored.append((name, s[0], s[1]))
    scored.sort(key=lambda x: (x[1], len(x[0]), x[0].lower()))
    call_under = int(cfg.get("slm", {}).get("call_when_under_suggestions", 5))
    if len(scored) < call_under:
        more = unique(items + local_model_candidates(req, cfg, [x[0] for x in items]))
        scored = []
        for name, src in more:
            s = score(typed, name, src)
            if s:
                scored.append((name, s[0], s[1]))
        scored.sort(key=lambda x: (x[1], len(x[0]), x[0].lower()))
    return scored[:maxn]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--request", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    req = json.loads(Path(a.request).read_text(encoding="utf-8"))
    rows = rank(req, load_config())
    text = "\n".join(f"{n}\t{s}\t{r}" for n, s, r in rows)
    Path(a.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
