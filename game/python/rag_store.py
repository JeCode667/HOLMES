# rag_store.py — RAG très simple (JSON + historique de dialogue)
#
# Chaque agent peut avoir un fichier JSON dans game/data/rag/<agent_id>.json
# au format :
# [
#   { "id": "xxx", "text": "....", "tags": ["...","..."] },
#   ...
# ]

import os
import json
import re

import agents as agents_mod

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_DATA_DIR = os.path.abspath(os.path.join(_BASE_DIR, "..", "data"))
_RAG_DIR = os.path.join(_DATA_DIR, "rag")

# cache RAG + historique
_RAG_CACHE: dict[str, list[dict]] = {}
_HISTORY: dict[str, list[dict]] = {}

_STOPWORDS = set([
    "the", "a", "an", "and", "or", "of", "in", "on", "to",
    "le", "la", "les", "un", "une", "des", "et", "de", "du", "en", "au", "aux"
])

def _tokenize(text: str) -> list[str]:
    text = text or ""
    tokens = re.findall(r"[a-zA-Zéèêàùïûç'-]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS]

def _load_kb(agent_id: str) -> list[dict]:
    if agent_id in _RAG_CACHE:
        return _RAG_CACHE[agent_id]

    agent = agents_mod.get_agent(agent_id)
    fname = agent.get("knowledge_file")
    if not fname:
        _RAG_CACHE[agent_id] = []
        return []

    path = os.path.join(_RAG_DIR, fname)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
        _RAG_CACHE[agent_id] = data
        return data
    except Exception as e:
        print(f"[HOLMES] WARNING: cannot load RAG for agent {agent_id} at {path}: {e}")
        _RAG_CACHE[agent_id] = []
        return []

def get_rag_context(agent_id: str, query: str, max_chunks: int = 3) -> str:
    """
    Sélectionne quelques passages pertinents en similarité lexicale simple.
    Suffisant pour guider un petit modèle local.
    """
    kb = _load_kb(agent_id)
    if not kb:
        return ""

    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return ""

    scored: list[tuple[int, str]] = []
    for entry in kb:
        text = entry.get("text", "")
        tags = " ".join(entry.get("tags", []))
        t_tokens = set(_tokenize(text + " " + tags))
        score = len(q_tokens & t_tokens)
        if score > 0:
            scored.append((score, text))

    if not scored:
        return ""

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [t for _, t in scored[:max_chunks]]
    return "\n\n".join(f"- {t}" for t in top)

def add_history(agent_id: str, player_input: str, response: str) -> None:
    if agent_id not in _HISTORY:
        _HISTORY[agent_id] = []
    _HISTORY[agent_id].append({
        "input": player_input,
        "response": response,
        "agent_name": agents_mod.get_name(agent_id),
    })

def get_history_context(agent_id: str, max_turns: int = 3) -> str:
    history = _HISTORY.get(agent_id, [])
    if not history:
        return ""

    last = history[-max_turns:]
    parts = []
    for h in last:
        parts.append(
            f"Earlier, the player said '{h['input']}', "
            f"{h['agent_name']} answered '{h['response']}'."
        )
    return "\n".join(parts)
