"""The Pit's verdict: the last step. Writes a check file OUTSIDE the repo that imports the house statement and the
submission, states `theorem pit_verified : <Module>.Statement := solution`, and prints its axioms. GREEN only if
Lean accepts it with no errors, no `sorry` warning, and every axiom is one of propext, Classical.choice, Quot.sound.
The statement is the house's own file (hash-pinned in step 1), so a proof of anything else does not typecheck.
"""
import os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def main():
    module = Path("/tmp/pit_module").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"Pit\.[A-Za-z0-9]+", module):
        print(f"::error title=pit::PIT-RED: bad module name {module!r}"); sys.exit(1)
    d = Path("/tmp/pitcheck"); d.mkdir(exist_ok=True)
    chk = d / "Check.lean"
    chk.write_text(f"import {module}\nimport PitSubmission\n\ntheorem pit_verified : {module}.Statement := solution\n\n#print axioms pit_verified\n", encoding="utf-8")
    p = subprocess.run(["lake", "env", "lean", str(chk)], cwd=ROOT, capture_output=True, text=True, timeout=900)
    out = (p.stdout or "") + (p.stderr or "")
    print(out[-6000:])
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    def verdict(color, why):
        line = f"PIT-{color}: {why}"
        print(line)
        print(f"::{'notice' if color == 'GREEN' else 'error'} title=pit::{line}")   # the board reads this annotation back
        if summary:
            with open(summary, "a", encoding="utf-8") as f:
                f.write(f"## {line}\n\n```\n{out[-3000:]}\n```\n")
        sys.exit(0 if color == "GREEN" else 1)
    if p.returncode != 0 or re.search(r"(^|\s)error:", out):
        verdict("RED", "Lean refused the check file (the proof does not prove the house statement, or does not compile)")
    if "declaration uses 'sorry'" in out or "sorryAx" in out:
        verdict("RED", "the proof uses sorry")
    m = re.search(r"'pit_verified' depends on axioms: \[([^\]]*)\]", out)
    if m:
        axs = {a.strip() for a in m.group(1).replace("\n", " ").split(",") if a.strip()}
        bad = sorted(axs - ALLOWED)
        if bad:
            verdict("RED", f"the proof leans on axioms outside the house's three: {', '.join(bad)}")
        verdict("GREEN", f"Lean accepts it; axioms: {', '.join(sorted(axs))}")
    if "'pit_verified' does not depend on any axioms" in out:
        verdict("GREEN", "Lean accepts it; no axioms at all")
    verdict("RED", "no axiom report from Lean, so nothing is certified")


if __name__ == "__main__":
    main()
