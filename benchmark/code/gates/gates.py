#!/usr/bin/env python3
"""Domain gates of the code part of E4, for Python, C and C++.

Overlays an excerpt (pristine or seeded) on a complete copy of its tool, builds
it when the language needs it, runs static analyzers (never the program's own tests),
writes one domain-result file per gate and a capped text report for the
reviewer. Written before any seeded copy exists and not tuned on them. Upstream
findings are kept, not subtracted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Benchmark copy: the two absolute paths of the run are read from the environment
# (the folder of ruff, bandit and clang-tidy; the folder of gcc and g++).
VENV = Path(os.environ.get("BENCHMARK_TOOLS_BIN", ""))
GCC_BIN = os.environ.get("BENCHMARK_GCC_BIN", "/usr/bin")
CAP_LINES = 120            # findings kept per gate in the report
DUP_WINDOW = 6             # consecutive normalized lines forming a block
PY_COMPLEXITY_LIMIT = 15   # cyclomatic complexity of a Python function
C_COGNITIVE_LIMIT = 25     # cognitive complexity of a C or C++ function
BUILD_TIMEOUT_S = 1800
JOBS = 8
PY_LINT_RULES = "E,F,W,B,C4,PL,SIM,RET,ARG,TRY,PERF"
TIDY_LINT = "-*,bugprone-*,performance-*,misc-unused-*,misc-redundant-expression,readability-misleading-indentation"
TIDY_SECURITY = "-*,clang-analyzer-security.*,clang-analyzer-unix.*,clang-analyzer-core.*,cert-*"
TIDY_COMPLEXITY = "-*,readability-function-cognitive-complexity"

TOOLS = {
    "asyncnet": {
        "language": "python",
        "tree": "tornado/tornado-6.5.7",
        "excerpt": ["tornado/iostream.py", "tornado/http1connection.py",
                    "tornado/httputil.py", "tornado/simple_httpclient.py"],
        "tests": ["tornado/test/iostream_test.py", "tornado/test/http1connection_test.py",
                  "tornado/test/httputil_test.py", "tornado/test/simple_httpclient_test.py"],
    },
    "jsontool": {
        "language": "c",
        "tree": "jq/jq-1.8.2",
        "excerpt": ["src/execute.c", "src/jv.c", "src/jv_parse.c", "src/compile.c"],
        "flags": ["-std=gnu99", "-D_GNU_SOURCE", "-DHAVE_CONFIG_H", "-I.", "-Isrc",
                  "-Ivendor", "-Ivendor/oniguruma/src", "-Ivendor/decNumber"],
    },
    "buildtool": {
        "language": "cpp",
        "tree": "ninja/ninja-1.13.2/ninja-upstream",
        "excerpt": ["src/build.cc", "src/graph.cc", "src/deps_log.cc", "src/build_log.cc",
                    "src/manifest_parser.cc", "src/subprocess-posix.cc", "src/state.cc",
                    "src/disk_interface.cc"],
    },
}


def excerpt_files(root: Path, patterns: list[str]) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        found += [str(p.relative_to(root)) for p in sorted(root.glob(pattern)) if p.is_file()]
    return found


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], cwd: Path, env: dict | None = None, timeout: int = 900) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                              errors="replace", timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout} s"
    return proc.returncode, proc.stdout + proc.stderr


def build_env(work: Path) -> dict:
    return dict(os.environ, PATH=f"{GCC_BIN}:{os.environ['PATH']}", PYTHONPATH=str(work),
                PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0", PAGER="less", CC=f"{GCC_BIN}/gcc",
                CXX=f"{GCC_BIN}/g++")


def prepare_native(spec: dict, work: Path, env: dict) -> None:
    """Configure and compile what the analyzers need; the program's own tests are not used."""
    if spec["language"] == "c":
        steps = [["./configure", "--with-oniguruma=builtin", "--disable-docs", "--disable-shared",
                  "--disable-maintainer-mode"], ["make", f"-j{JOBS}"]]
    else:
        steps = [["cmake", "-S", ".", "-B", "build", "-DBUILD_TESTING=OFF", "-DCMAKE_BUILD_TYPE=Debug",
                  "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"]]
    for step in steps:
        code, out = run(step, work, env, BUILD_TIMEOUT_S)
        if code != 0:
            raise SystemExit(f"{step[0]} failed: {out[-400:]}")


def duplicates(work: Path, files: list[str]) -> list[str]:
    """Blocks of DUP_WINDOW consecutive normalized code lines seen more than once."""
    seen: dict[tuple[str, ...], list[str]] = defaultdict(list)
    comment = ("#", '"""', "'''", "//", "/*", "*")
    for rel in files:
        lines = (work / rel).read_text(encoding="utf-8", errors="replace").splitlines()
        code = [(i + 1, re.sub(r"\s+", " ", ln.strip())) for i, ln in enumerate(lines)]
        code = [(n, t) for n, t in code if len(t) > 1 and not t.startswith(comment)]
        for k in range(len(code) - DUP_WINDOW + 1):
            block = tuple(t for _, t in code[k:k + DUP_WINDOW])
            seen[block].append(f"{rel}:{code[k][0]}")
    return sorted(f"{len(w)}x {DUP_WINDOW}-line block at {', '.join(w[:4])}: {b[0][:60]}"
                  for b, w in seen.items() if len(w) > 1)


def tidy(checks: str, spec: dict, work: Path, files: list[str], env: dict, extra: list[str]) -> list[str]:
    def one(rel: str) -> str:
        if spec["language"] == "cpp":
            cmd = [str(VENV / "clang-tidy"), "-quiet", f"-checks={checks}", "-p", "build", *extra, rel]
        else:
            cmd = [str(VENV / "clang-tidy"), "-quiet", f"-checks={checks}", *extra, rel, "--", *spec["flags"]]
        return run(cmd, work, env, 900)[1]
    with ThreadPoolExecutor(JOBS) as pool:
        outs = list(pool.map(one, files))
    hits = set()
    prefix = str(work) + "/"
    for out in outs:
        for ln in out.splitlines():
            if re.search(r":\d+:\d+: (warning|error): ", ln):
                hits.add(ln.replace(prefix, ""))
    return sorted(hits)


def result(gate: str, magnitude: str, limit: str, outcome: str, work: Path, files: list[str]) -> dict:
    return {"contract_version": "1", "gate": gate, "magnitude": magnitude, "limit": limit,
            "result": outcome,
            "inputs": [{"path": rel, "sha256": sha256_of(work / rel)} for rel in files]}


def section(title: str, lines: list[str], report: list[str]) -> None:
    report.append(f"\n## {title}\n")
    report += lines[:CAP_LINES]
    if len(lines) > CAP_LINES:
        report.append(f"... {len(lines) - CAP_LINES} more lines omitted (cap {CAP_LINES})")


def static_python(work: Path, files: list[str], results: list, report: list) -> None:
    _, out = run([str(VENV / "ruff"), "check", "--isolated", "--no-cache", "--select", PY_LINT_RULES,
                  "--ignore", "E501", "--output-format", "concise", *files], work)
    hits = [ln for ln in out.splitlines() if re.match(r"^\S+:\d+:\d+: ", ln)]
    results.append(result("d-lint", f"{len(hits)} findings", "reported", "pass", work, files))
    section(f"d-lint: {len(hits)} findings", hits, report)
    _, out = run([str(VENV / "bandit"), "-q", "-f", "custom", "--msg-template",
                  "{relpath}:{line}: {test_id} {severity} {msg}", *files], work)
    hits = [ln for ln in out.splitlines() if re.match(r"^\S+:\d+: B\d+", ln)]
    results.append(result("d-security", f"{len(hits)} findings", "reported", "pass", work, files))
    section(f"d-security: {len(hits)} findings", hits, report)
    _, out = run([str(VENV / "ruff"), "check", "--isolated", "--no-cache", "--select", "C901", "--config",
                  f"lint.mccabe.max-complexity={PY_COMPLEXITY_LIMIT}", "--output-format", "concise", *files], work)
    hits = [ln for ln in out.splitlines() if re.match(r"^\S+:\d+:\d+: ", ln)]
    results.append(result("d-complexity", f"{len(hits)} functions above {PY_COMPLEXITY_LIMIT}", "reported",
                          "pass", work, files))
    section(f"d-complexity: {len(hits)} functions above {PY_COMPLEXITY_LIMIT}", hits, report)


def static_native(spec: dict, work: Path, files: list[str], env: dict, results: list, report: list) -> None:
    hits = tidy(TIDY_LINT, spec, work, files, env, [])
    results.append(result("d-lint", f"{len(hits)} findings", "reported", "pass", work, files))
    section(f"d-lint: {len(hits)} findings", hits, report)
    hits = tidy(TIDY_SECURITY, spec, work, files, env, [])
    results.append(result("d-security", f"{len(hits)} findings", "reported", "pass", work, files))
    section(f"d-security: {len(hits)} findings", hits, report)
    extra = ["-config={CheckOptions: {readability-function-cognitive-complexity.Threshold: "
             f"{C_COGNITIVE_LIMIT}}}}}"]
    hits = tidy(TIDY_COMPLEXITY, spec, work, files, env, extra)
    results.append(result("d-complexity", f"{len(hits)} functions above {C_COGNITIVE_LIMIT}", "reported",
                          "pass", work, files))
    section(f"d-complexity: {len(hits)} functions above cognitive {C_COGNITIVE_LIMIT}", hits, report)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True, choices=TOOLS)
    ap.add_argument("--excerpt", required=True, type=Path, help="folder with the excerpt files")
    ap.add_argument("--work", required=True, type=Path, help="scratch folder, recreated")
    ap.add_argument("--out", required=True, type=Path, help="folder for the report and results")
    args = ap.parse_args()
    spec = TOOLS[args.tool]
    if args.work.exists():
        shutil.rmtree(args.work)
    shutil.copytree(HERE / "sdist" / spec["tree"], args.work, symlinks=True)
    files = excerpt_files(args.excerpt, spec["excerpt"])
    if len(files) != len(excerpt_files(args.work, spec["excerpt"])):
        print("the excerpt does not hold every file of the tool's excerpt list", file=sys.stderr)
        return 2
    for rel in files:
        shutil.copy2(args.excerpt / rel, args.work / rel)
    args.out.mkdir(parents=True, exist_ok=True)
    env = build_env(args.work)
    report: list[str] = [f"# Domain gates report: {len(files)} files measured"]
    results: list[dict] = []

    if spec["language"] != "python":
        prepare_native(spec, args.work, env)

    if spec["language"] == "python":
        static_python(args.work, files, results, report)
    else:
        static_native(spec, args.work, files, env, results, report)

    hits = duplicates(args.work, files)
    results.append(result("d-duplicates", f"{len(hits)} repeated blocks", "reported", "pass", args.work, files))
    section(f"d-duplicates: {len(hits)} repeated blocks of {DUP_WINDOW} lines", hits, report)

    (args.out / "gates-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    for item in results:
        (args.out / f"{item['gate']}.json").write_text(json.dumps(item, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({r["gate"]: [r["result"], r["magnitude"]] for r in results}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
