from __future__ import annotations

from typing import Any

from ollama_client import generate_json, generate_text

MAX_NOTE_CHARS = 65_000

EXTRACTION_PROMPT = '''You are FormulaForge AI, an exam-oriented formula extraction assistant.
Use ONLY the supplied study notes. Identify the subject and group formulas into concise topics.
Do not invent missing formulas. Remove duplicates. Preserve notation as plain Unicode/ASCII text.
Every variable must be formatted as a short string such as "F -> Force".
Important formulas are formulas repeated, emphasized, or central to the provided notes.

Return valid JSON only with this exact shape:
{
  "subject": "",
  "topics": [{"topic_name": "", "formulas": [{"formula": "", "meaning": "", "variables": [""], "use": ""}]}],
  "important_formulas": [{"formula": "", "meaning": "", "variables": [""], "use": ""}]
}
Use very short meanings and uses. Do not add prose outside JSON.

STUDY NOTES:
'''


def _clean_formula(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "formula": str(item.get("formula", "")).strip(),
        "meaning": str(item.get("meaning", "")).strip(),
        "variables": [str(variable).strip() for variable in item.get("variables", []) if str(variable).strip()],
        "use": str(item.get("use", "")).strip(),
    }


def normalize_sheet(payload: dict[str, Any]) -> dict[str, Any]:
    seen: set[str] = set()
    topics = []
    for topic in payload.get("topics", []):
        formulas = []
        for item in topic.get("formulas", []):
            formula = _clean_formula(item)
            key = formula["formula"].lower().replace(" ", "")
            if formula["formula"] and key not in seen:
                seen.add(key)
                formulas.append(formula)
        if formulas:
            topics.append({"topic_name": str(topic.get("topic_name", "General")).strip() or "General", "formulas": formulas})
    important = [_clean_formula(item) for item in payload.get("important_formulas", []) if item.get("formula")]
    return {"subject": str(payload.get("subject", "Study Notes")).strip() or "Study Notes", "topics": topics, "important_formulas": important}


def extract_formulas(notes: str) -> dict[str, Any]:
    if not notes.strip():
        raise ValueError("No readable text was found in the uploaded files.")
    payload = generate_json(EXTRACTION_PROMPT + notes[:MAX_NOTE_CHARS])
    result = normalize_sheet(payload)
    if not result["topics"]:
        raise ValueError("No formulas were found in these notes.")
    return result


def answer_from_notes(question: str, notes: str) -> str:
    prompt = f'''You are the FormulaForge study assistant. Answer ONLY from the uploaded notes below.
If the answer is not in the notes, say exactly: "I couldn't find that in the uploaded notes."
Keep the answer concise, exam-focused, and use bullets where helpful. Do not use outside knowledge.

UPLOADED NOTES:
{notes[:MAX_NOTE_CHARS]}

QUESTION: {question}
ANSWER:'''
    return generate_text(prompt)
