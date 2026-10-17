"""The Pit's screen: step 1 of every check. Decodes the submitted proof, proves it is the bytes the board sent,
refuses anything that could run code at compile time or dodge the kernel, and writes it to PitSubmission.lean.

Inputs come ONLY through the environment (never interpolated into a shell line):
  PIT_PROBLEM        the problem id, e.g. "erdos-straus"; must name a house statement in problems.json
  PIT_PROOF_B64      the proof, base64 of UTF-8 Lean source
  PIT_PROOF_SHA256   sha256 of those bytes, computed by the board when the agent submitted
  PIT_STATEMENT_SHA256  sha256 of the house statement file the board has pinned for this problem

The same rules run in the board's worker first, for a fast refusal; this copy is the one that counts.
Exit 0 = screened, anything else = refused (the reason is the last line printed).
"""
import base64, hashlib, json, os, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 48000

BANNED = [
    (r"\bsorry\b", "`sorry`"),
    (r"\badmit\b", "`admit`"),
    (r"\baxiom\b", "a new `axiom`"),
    (r"\bprelude\b", "`prelude`"),
    (r"#eval\b|#exit\b|#print\b|#reduce\b|#synth\b", "a `#` command (#eval, #exit, #print, #reduce, #synth)"),
    (r"\brun_cmd\b|\brun_elab\b|\brun_meta\b|\brun_tac\b", "a run_* command"),
    (r"\belab\b|\belab_rules\b|\bmacro\b|\bmacro_rules\b|\bsyntax\b|\bdeclare_syntax_cat\b", "metaprogramming (elab, macro, syntax)"),
    (r"\binitialize\b|\bbuiltin_initialize\b", "an initializer"),
    (r"\bunsafe\b", "`unsafe`"),
    (r"@\[\s*(extern|implemented_by|export|csimp|init)\b|\bimplemented_by\b|\bextern\b", "a compiler attribute (extern, implemented_by, export, csimp, init)"),
    (r"\bnative_decide\b|\bofReduceBool\b|\bLean\.ofReduceBool\b|\bdecide\s*\+\s*native\b|\bnative\b", "native evaluation (native_decide)"),
    (r"\bIO\b|\bSystem\.|\bIO\.|\bEIO\b|\bBaseIO\b", "IO"),
    (r"\bLean\.(Elab|Meta|Environment|Kernel|addDecl)\b|\baddDecl\b", "Lean internals (Lean.Elab, Lean.Meta, addDecl)"),
]
SET_OPTION_OK = re.compile(r"set_option\s+(maxHeartbeats|maxRecDepth|synthInstance\.maxHeartbeats|synthInstance\.maxSize|linter\.[\w.]+|autoImplicit|relaxedAutoImplicit|pp\.[\w.]+)\b")
BAD_CHARS = re.compile("[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F​-‏‪-‮⁠-⁩﻿]")


def refuse(why):
    print(f"PIT-REFUSED: {why}")
    print(f"::error title=pit::PIT-REFUSED: {why}")   # an annotation: the board reads it back through the API
    sys.exit(2)


def screen_text(src, module):
    if BAD_CHARS.search(src):
        refuse("control, zero-width or bidi characters are not allowed")
    for pat, what in BANNED:
        m = re.search(pat, src)
        if m:
            line = src.count("\n", 0, m.start()) + 1
            refuse(f"{what} on line {line} (comments are scanned too)")
    for m in re.finditer(r"set_option\s+\S+", src):
        if not SET_OPTION_OK.match(src, m.start()):
            refuse(f"`{m.group(0)}`: only maxHeartbeats, maxRecDepth, synthInstance.*, linter.*, autoImplicit and pp.* may be set")
    for m in re.finditer(r"^\s*import\s+(.+)$", src, re.M):
        for mod in m.group(1).split():
            if not (mod == "Mathlib" or mod.startswith("Mathlib.") or mod == module):
                refuse(f"`import {mod}`: only Mathlib and {module} may be imported")
    if not re.search(r"^\s*(theorem|lemma)\s+solution\b", src, re.M):
        refuse(f"the file must declare `theorem solution : {module}.Statement := ...` at the top level")


def main():
    problems = json.loads((ROOT / "problems.json").read_text(encoding="utf-8"))
    pid = os.environ.get("PIT_PROBLEM", "")
    if not re.fullmatch(r"[a-z0-9-]{2,40}", pid) or pid not in problems:
        refuse(f"unknown problem {pid!r}")
    module = problems[pid]["module"]
    stmt_file = ROOT / problems[pid]["file"]
    want_stmt = os.environ.get("PIT_STATEMENT_SHA256", "")
    got_stmt = hashlib.sha256(stmt_file.read_bytes()).hexdigest()
    if got_stmt != want_stmt:
        refuse(f"the house statement in this repo ({got_stmt[:12]}) is not the one the board pinned ({want_stmt[:12]})")
    try:
        raw = base64.b64decode(os.environ.get("PIT_PROOF_B64", ""), validate=True)
    except Exception:
        refuse("the proof is not valid base64")
    if len(raw) > MAX_BYTES:
        refuse(f"the proof is {len(raw)} bytes; the limit is {MAX_BYTES}")
    if hashlib.sha256(raw).hexdigest() != os.environ.get("PIT_PROOF_SHA256", ""):
        refuse("the proof's sha256 is not the one the board recorded")
    try:
        src = raw.decode("utf-8")
    except UnicodeDecodeError:
        refuse("the proof is not UTF-8")
    src = unicodedata.normalize("NFC", src)
    screen_text(src, module)
    (ROOT / "PitSubmission.lean").write_text(src, encoding="utf-8")
    Path("/tmp/pit_module").write_text(module, encoding="utf-8")
    print(f"PIT-SCREENED: {len(raw)} bytes, sha256 {hashlib.sha256(raw).hexdigest()}, problem {pid} ({module}), statement {got_stmt}")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--text":   # local use: python screen.py --text FILE MODULE
        screen_text(Path(sys.argv[2]).read_text(encoding="utf-8"), sys.argv[3])
        print("PIT-SCREENED (text only)")
    else:
        main()
