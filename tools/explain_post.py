"""Step 4 of explain.yml: take Claude's final message out of the action's execution file, scrub it, cut it short, and
post it as the run's summary and as ONE annotation starting `PIT-EXPLAIN:`, which the board reads back through the API.

Inputs come only through the environment:
  EXEC_FILE          path to claude-code-action's execution file (JSON: the session's messages, the last a "result")
  CLAUDE_CONCLUSION  the action's own success / failure
  SOURCE_RUN         html URL of the failed pit-check run
  SOURCE_TITLE       that run's title, "pit <submission id>"

The text is a stranger-influenced reading (the proof is untrusted), so: token-shaped strings and URLs are removed,
control characters are dropped, and it is cut to MAX characters. It never fails the job: no text means a plain
"no explanation" annotation, so the board stops waiting.
"""
import json, os, re, sys
from pathlib import Path

MAX = 700


def final_text(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return ""
    items = data if isinstance(data, list) else [data]
    for it in reversed(items):
        if isinstance(it, dict) and it.get("type") == "result" and isinstance(it.get("result"), str) and it["result"].strip():
            return it["result"]
    for it in reversed(items):   # fallback: the last assistant text block
        msg = it.get("message") if isinstance(it, dict) else None
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            parts = [c.get("text", "") for c in msg.get("content", []) if isinstance(c, dict) and c.get("type") == "text"]
            if any(p.strip() for p in parts):
                return "\n".join(parts)
    return ""


def scrub(t):
    t = re.sub(r"sk-ant-[A-Za-z0-9_\-]+|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]+|eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-.]+", "[removed]", t)
    t = re.sub(r"https?://\S+", "[link removed]", t)
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f​-‏‪-‮⁠-⁩﻿]", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    if len(t) > MAX:
        t = t[:MAX - 1].rsplit(" ", 1)[0] + "…"
    return t


def annotation_escape(t):
    # the message part of a workflow command: only %, CR and LF are escaped (title= is the property part)
    return t.replace("%", "%25").replace("\r", "").replace("\n", "%0A")


def main():
    text = scrub(final_text(os.environ.get("EXEC_FILE", "")))
    if not text:
        text = f"no explanation: the explainer came back {os.environ.get('CLAUDE_CONCLUSION') or 'empty'}. The checker's own verdict stands."
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## Why {os.environ.get('SOURCE_TITLE', 'this proof')} failed (Claude's reading, not the verdict)\n\n{text}\n\n"
                    f"Checker run: {os.environ.get('SOURCE_RUN', '')}\n")
    print(text)
    print(f"::notice title=pit-explain::PIT-EXPLAIN: {annotation_escape(text)}")


if __name__ == "__main__":
    main()
