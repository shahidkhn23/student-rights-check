"""AI agent: the model decides which tools to call, the tools hold the facts.

Two tools, both backed by the tested, verified code:
  * check_document – runs the red-flag checks on the document the student attached
  * search_rights  – searches the 421 verified rules

Guardrail in code (not just in the prompt): every law reference (§ ..., Art. ...)
in the final answer must appear in a tool result. If not, the model gets one
chance to fix it; after that the agent returns the verified tool results instead.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request

from . import check
from .ask import RightsIndex, answer
from .llm import settings

SYSTEM = """You help students in Germany understand their rights and documents.
- Always use the tools. If a document is attached, call check_document. For questions, call search_rights.
- State legal facts ONLY from tool results. Never add laws, paragraphs, numbers or court cases yourself.
- If the tools return nothing useful, say you don't know and point to free help. Do not guess.
- General legal information only: never say what this person must do in their case or that they will win.
- If asked for a message to a landlord/employer, you may draft one, citing only rules from tool results.
- Answer in the student's language, simple and friendly. End with the free help from the tool results
  and this note: "General legal information, not legal advice for your case."
"""

TOOLS = [
    {"name": "check_document",
     "description": "Check the document the student attached for clauses that conflict with student rights. "
                    "Returns findings with the clause, the law and the source.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "search_rights",
     "description": "Search the verified knowledge base of student rights in Germany (housing, work, exams, "
                    "money, health insurance, contracts, data, discrimination). Use English or German keywords.",
     "input_schema": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]}},
]

LAW_REF = re.compile(r"(?:§+|Art\.)\s*\d+[a-z]?", re.I)


def to_chat_format(system: str, messages: list, tools: list) -> dict:
    """Convert the agent's tool-use conversation to the chat-completions format (used by most hosted models)."""
    out = [{"role": "system", "content": system}]
    for m in messages:
        c = m["content"]
        if isinstance(c, str):
            out.append({"role": m["role"], "content": c})
        elif m["role"] == "assistant":
            msg = {"role": "assistant",
                   "content": "".join(b.get("text", "") for b in c if b["type"] == "text") or None}
            calls = [{"id": b["id"], "type": "function",
                      "function": {"name": b["name"], "arguments": json.dumps(b.get("input", {}))}}
                     for b in c if b["type"] == "tool_use"]
            if calls:
                msg["tool_calls"] = calls
            out.append(msg)
        else:
            out += [{"role": "tool", "tool_call_id": b["tool_use_id"], "content": b["content"]} for b in c]
    return {"messages": out,
            "tools": [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                                         "parameters": t["input_schema"]}} for t in tools]}


def from_chat_format(message: dict) -> dict:
    """Convert an chat-style reply back to the agent's content blocks."""
    blocks = [{"type": "text", "text": message["content"]}] if message.get("content") else []
    for c in message.get("tool_calls") or []:
        blocks.append({"type": "tool_use", "id": c["id"], "name": c["function"]["name"],
                       "input": json.loads(c["function"].get("arguments") or "{}")})
    return {"content": blocks or [{"type": "text", "text": ""}]}


def llm_model(system: str, messages: list, tools: list) -> dict:
    """One call to any chat-completions compatible chat API (see llm.settings for the environment variables)."""
    cfg = settings()
    if not cfg:
        raise RuntimeError("LLM_API_KEY, LLM_BASE_URL and LLM_MODEL must be set")
    key, url, model = cfg
    payload = {"model": model, "max_tokens": 2000, "temperature": 0.2, **to_chat_format(system, messages, tools)}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "rightscheck/0.4"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return from_chat_format(json.loads(r.read())["choices"][0]["message"])


def _norm(ref: str) -> str:
    """'§ 551', '§\u00a0551' and '§§ 551' all become '§551'."""
    return re.sub(r"§+", "§", re.sub(r"\s+", "", ref)).lower()


def ungrounded_refs(text: str, sources: list[str]) -> list[str]:
    """Law references in the answer that appear in none of the sources (tool results, the document)."""
    allowed = {_norm(r) for r in LAW_REF.findall(" ".join(sources))}
    return [ref for ref in LAW_REF.findall(text) if _norm(ref) not in allowed]


def run_agent(message: str, document: str | None = None, model=None, max_steps: int = 6) -> dict:
    model = model or llm_model
    index = RightsIndex()
    trace, results = [], []

    def call_tool(name: str, args: dict) -> dict:
        if name == "check_document":
            return check(document) if document else {"error": "No document attached."}
        if name == "search_rights":
            return answer(args.get("question", ""), index)
        return {"error": f"Unknown tool {name}"}

    user = message if not document else f"{message}\n\n<document>\n{document[:15000]}\n</document>"
    messages = [{"role": "user", "content": user}]
    retried = False

    for _ in range(max_steps):
        resp = model(SYSTEM, messages, TOOLS)
        messages.append({"role": "assistant", "content": resp["content"]})
        calls = [b for b in resp["content"] if b["type"] == "tool_use"]

        if not calls:
            text = "".join(b.get("text", "") for b in resp["content"] if b["type"] == "text")
            # the contract's own section numbers (e.g. "§ 3 Kaution") are not invented law
            bad = ungrounded_refs(text, results + [document or ""])
            if bad:
                trace.append({"rejected": bad})
            if not bad:
                return {"answer": text, "trace": trace, "grounded": True}
            if not retried:
                retried = True
                messages.append({"role": "user", "content":
                                 f"You cited {', '.join(bad)}, which no tool returned. Remove anything not "
                                 "supported by the tool results and answer again."})
                continue
            return {"answer": fallback(results), "trace": trace, "grounded": False}

        tool_out = []
        for c in calls:
            out = call_tool(c["name"], c.get("input", {}))
            dumped = json.dumps(out, ensure_ascii=False)
            results.append(dumped)
            trace.append({"tool": c["name"], "input": c.get("input", {})})
            tool_out.append({"type": "tool_result", "tool_use_id": c["id"], "content": dumped})
        messages.append({"role": "user", "content": tool_out})

    return {"answer": fallback(results), "trace": trace, "grounded": False}


def fallback(results: list[str]) -> str:
    """Used when the model can't produce a grounded answer: show the verified tool results as they are."""
    if not results:
        return "I couldn't find verified information for this. Please ask a free advice service."
    return "I couldn't write a reliable summary, so here are the verified results:\n\n" + "\n\n".join(results)
