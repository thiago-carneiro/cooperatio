#!/usr/bin/env python3
"""Run the static gates on the real trees, anonymize the reports, and record
which defects the anonymized report names by its lines."""
import importlib.util, json, os, pathlib, re, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("anonymize", HERE / "anonymize.py"); a = importlib.util.module_from_spec(s); s.loader.exec_module(a)
# Benchmark copy: the scratch folder of the run is read from the environment.
SCRATCH = pathlib.Path(os.environ.get("BENCHMARK_SCRATCH", "scratch")).resolve()
for tool in a.RULES:
    obj = HERE / "objects" / tool
    for variant in ("pristine", "seeded"):
        out = HERE / f"results-{variant}" / tool
        r = subprocess.run([sys.executable, "-B", str(HERE / "gates.py"), "--tool", tool, "--excerpt", str(obj / variant),
                            "--work", str(SCRATCH / f"{variant}-{tool}"), "--out", str(out)], capture_output=True, text=True)
        print(tool, variant, r.returncode, r.stdout.replace("\n", " ")[:230], r.stderr[-200:], flush=True)
        text = (out / "gates-report.md").read_text(encoding="utf-8")
        (out / "gates-report.raw.md").write_text(text, encoding="utf-8")
        text = text.replace(str(SCRATCH / f"{variant}-{tool}") + "/", "")
        (out / "gates-report.md").write_text(a.anon_tokens(tool, text), encoding="utf-8")
    report = (HERE / "results-seeded" / tool / "gates-report.md").read_text(encoding="utf-8")
    pristine = (HERE / "results-pristine" / tool / "gates-report.md").read_text(encoding="utf-8")
    sect, hits = "", []
    for ln in report.splitlines():
        if ln.startswith("## "):
            sect = ln[3:].split(":")[0]
        else:
            for m in re.finditer(r"([\w./-]+\.(?:py|c|cc)):(\d+)", ln):
                hits.append((sect, m.group(1), int(m.group(2))))
    key = json.loads((obj / "anon/answer-key.json").read_text(encoding="utf-8"))
    rows = [{"id": d["id"], "class": d["class"],
             "report_names_its_lines": sorted({h[0] for h in hits if h[1] == d["file"] and d["line_start"] <= h[2] <= d["line_end"]})}
            for d in key]
    (obj / "gates-detection.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    print(tool, "named:", sum(1 for r in rows if r["report_names_its_lines"]), "of", len(rows), flush=True)
