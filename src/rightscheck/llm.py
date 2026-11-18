"""Optional AI layer: explains the verified findings in simple language.

Guardrails (this is what keeps the tool on the right side of the
Rechtsdienstleistungsgesetz and stops hallucinated law):
  * The model only receives facts from knowledge_base/laws.json, never asked to "know" the law.
  * It must not tell the user what to do in their specific case.
  * It must not cite any law that is not in the findings.
  * Every answer ends with the free-help list.

Works without any extra package (plain HTTPS call). If no API key is set,
the tool still works and returns the rule-based report.
"""

from __future__ import annotations

import json
import os
import urllib.request

SYSTEM_PROMPT = """You help international students in Germany understand documents.
You receive (1) a document and (2) a list of findings that were checked against German law by hand.

Rules you must follow:
- Explain each finding in simple, friendly English (B1 level). Short sentences.
- Use ONLY the legal facts given in the findings. Never add other laws, paragraphs, numbers or court cases.
- Give general legal information only. Never say what this person should do in their case,
  never say "you will win" or "this clause is definitely invalid for you".
  Say what the law generally says and that exceptions exist.
- If the user's language is given, answer in that language.
- Finish with: who can check it for free (from the free_help list) and the disclaimer, unchanged.
"""


ASK_PROMPT = """You help students in Germany understand their rights.
You receive a question and verified legal rules from a knowledge base.

Rules you must follow:
- Answer ONLY with the facts in the given rules. Never add other laws, numbers, deadlines or court cases.
- If the rules do not answer the question, say so and point to the free help. Do not guess.
- Give general legal information only, never a decision for the person's specific case.
- Simple, friendly language (B1 level), in the requested language. Short sentences.
- End with the free_help list and the disclaimer, unchanged.
"""


def settings() -> tuple[str, str, str] | None:
    """(api key, chat-completions URL, model) from the environment, or None if not configured.

    Works with any chat-completions compatible endpoint:
      LLM_API_KEY, LLM_BASE_URL (e.g. https://host/v1), LLM_MODEL
    """
    key, base, model = (os.getenv(n) for n in ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL"))
    if not (key and base and model):
        return None
    return key, base.rstrip("/") + "/chat/completions", model


def _call(system: str, user: str) -> str | None:
    cfg = settings()
    if not cfg:
        return None
    key, url, model = cfg
    payload = {
        "model": model,
        "max_tokens": 1500,
        "temperature": 0.2,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "rightscheck/0.4"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return data["choices"][0]["message"].get("content") or ""
    except Exception as e:  # network error, bad key ... fall back to the verified answer
        return f"(AI explanation unavailable: {e.__class__.__name__}. Showing the verified answer only.)"


def explain_answer(answer: dict, language: str = "English") -> str | None:
    return _call(ASK_PROMPT, f"Answer language: {language}\n\n<verified>\n"
                             f"{json.dumps(answer, ensure_ascii=False, indent=2)}\n</verified>")


def explain(document: str, report: dict, language: str = "English") -> str | None:
    return _call(SYSTEM_PROMPT, (
        f"Answer language: {language}\n\n"
        f"<document>\n{document[:15000]}\n</document>\n\n"
        f"<findings>\n{json.dumps(report, ensure_ascii=False, indent=2)}\n</findings>"))
