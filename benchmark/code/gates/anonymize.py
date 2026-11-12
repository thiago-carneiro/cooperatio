#!/usr/bin/env python3
"""Anonymize the three target programs: names in code, comments and paths, the
license headers of the files, the answer keys and the gates reports.

Line counts are preserved, so the line numbers of a key stay valid. The upstream
licenses and the mapping stay beside the benchmark and never reach a reviewer.
The analyzers run on the real tree; only their report is anonymized afterwards.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

RULES = {
    "asyncnet": [(r"friendfeed\.com", "example.com"), (r"tornadoweb", "netlibproject"), (r"tornado", "netlib"), (r"Tornado", "Netlib"), (r"TORNADO", "NETLIB")],
    "jsontool": [
        (r"\bjv\.([ch])\b", r"value.\1"), (r"\bjv_([a-z_0-9]+)\.([ch])\b", r"value_\1.\2"),
        (r"\bjq\.([ch])\b", r"engine.\1"), (r"\bjq_([a-z_0-9]+)\.([ch])\b", r"engine_\1.\2"),
        (r"\bjqlang\b", "qelang"), (r"\bstedolan\b", "qeauthor"),
        (r"\bjvp_", "valp_"), (r"\bJVP_", "VALP_"), (r"\bjv_", "val_"), (r"\bJV_", "VAL_"),
        (r"\bjv\b", "val_t"), (r"\bjq_", "qe_"), (r"\bJQ_", "QE_"), (r"\bjq\b", "qe"), (r"\bJQ\b", "QE"),
        (r"\bjq(\d)", r"qe\1"),
    ],
    "buildtool": [(r"ninja", "forge"), (r"Ninja", "Forge"), (r"NINJA", "FORGE")],
}
RESIDUE = {
    "asyncnet": r"tornado|facebook|friendfeed",
    "jsontool": r"\bjq\b|jqlang|\bjv\b|stedolan|Dolan",
    "buildtool": r"ninja|google|Evan Martin",
}
HEADER_MARK = re.compile(r"copyright|licensed under|permission is hereby|apache license|\bspdx\b", re.I)
HEADER_SPAN = 30


def anon_tokens(tool: str, text: str) -> str:
    for pattern, repl in RULES[tool]:
        text = re.sub(pattern, repl, text)
    return text


def strip_header(text: str, suffix: str) -> str:
    """Empty the license comment at the top of a file, keeping its line count."""
    lines = text.splitlines(keepends=True)
    if not any(HEADER_MARK.search(ln) for ln in lines[:HEADER_SPAN]):
        return text
    marker = "#" if suffix == ".py" else "//"
    for i, ln in enumerate(lines[:HEADER_SPAN]):
        stripped = ln.strip()
        if stripped.startswith(("#!", "#include", "import ", "from ")) or (suffix != ".py" and stripped.startswith("#")):
            break
        if stripped.startswith(("#", "//", "/*", "*", "*/")):
            lines[i] = marker + "\n"
        elif stripped and HEADER_MARK.search(ln):
            lines[i] = marker + "\n"
        elif stripped:
            break
    return "".join(lines)


def main() -> int:
    status = 0
    for tool in RULES:
        obj = HERE / "objects" / tool
        anon = obj / "anon"
        for variant in ("pristine", "seeded"):
            base = obj / variant
            for path in sorted(p for p in base.rglob("*") if p.is_file()):
                rel = path.relative_to(base)
                text = path.read_text(encoding="utf-8")
                out = anon_tokens(tool, strip_header(text, path.suffix))
                if len(out.splitlines()) != len(text.splitlines()):
                    print(f"{tool}: line count changed in {rel}")
                    status = 1
                target = anon / variant / anon_tokens(tool, str(rel))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(out, encoding="utf-8")
        key = json.loads((obj / "answer-key.json").read_text(encoding="utf-8"))
        out_key = [{k: anon_tokens(tool, v) if isinstance(v, str) else v for k, v in d.items()} for d in key]
        (anon / "answer-key.json").write_text(json.dumps(out_key, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        md = (obj / "answer-key.md").read_text(encoding="utf-8")
        (anon / "answer-key.md").write_text(anon_tokens(tool, md), encoding="utf-8")
        # replay the anonymized key on the anonymized pristine copy
        by_file: dict[str, str] = {}
        for d in out_key:
            text = by_file.get(d["file"]) or (anon / "pristine" / d["file"]).read_text(encoding="utf-8")
            if text.count(d["old"]) != 1:
                print(f"{d['id']}: anonymized old occurs {text.count(d['old'])} times")
                status = 1
            by_file[d["file"]] = text.replace(d["old"], d["new"], 1)
        for rel, text in by_file.items():
            if text != (anon / "seeded" / rel).read_text(encoding="utf-8"):
                print(f"{tool}: replay differs for {rel}")
                status = 1
        pat = re.compile(RESIDUE[tool], re.I)
        hits = []
        for path in sorted(p for p in (anon / "seeded").rglob("*") if p.is_file()):
            for n, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if pat.search(ln):
                    hits.append(f"{path.name}:{n}: {ln.strip()[:80]}")
        print(tool, "files", sum(1 for p in (anon / "seeded").rglob("*") if p.is_file()), "residue", len(hits), hits[:6])
        (obj / "anonymization.json").write_text(json.dumps({"rules": RULES[tool]}, indent=1) + "\n", encoding="utf-8")
    return status


if __name__ == "__main__":
    sys.exit(main())
