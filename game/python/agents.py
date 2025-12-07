# agents.py — définition des agents (personnages, rédacteur, évaluateur)
#
# Rôle : fournir un accès simple aux métadonnées d’agent et aux rôles,
# en s’appuyant sur game/data/agents.json

import os
import json

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_DATA_DIR = os.path.abspath(os.path.join(_BASE_DIR, "..", "data"))
_AGENTS_FILE = os.path.join(_DATA_DIR, "agents.json")

_AGENTS_CACHE = None

def _load_agents():
    global _AGENTS_CACHE
    if _AGENTS_CACHE is not None:
        return _AGENTS_CACHE

    try:
        with open(_AGENTS_FILE, "r", encoding="utf-8") as f:
            _AGENTS_CACHE = json.load(f)
    except Exception as e:
        print("[HOLMES] WARNING: cannot load agents.json, using minimal fallback.", e)
        _AGENTS_CACHE = {
            "default_field": {
                "name": "Parisian Witness",
                "role": "field",
                "personality": (
                    "You are an anonymous Parisian witness in July 1789. "
                    "You answer briefly about what you see around you."
                ),
                "knowledge_file": "default_field.json"
            }
        }
    return _AGENTS_CACHE

def get_agent(agent_id: str) -> dict:
    agents = _load_agents()

    agent = agents.get(agent_id)
    if agent is not None:
        return agent

    default_agent = agents.get("default_field")
    if default_agent is not None:
        return default_agent

    if agents:
        return next(iter(agents.values()))

    raise KeyError(f"No agents available to resolve '{agent_id}'")

def get_all_agents() -> dict:
    return _load_agents()

def get_role(agent_id: str) -> str:
    agent = get_agent(agent_id)
    return agent.get("role", "field")

def get_name(agent_id: str) -> str:
    agent = get_agent(agent_id)
    return agent.get("name", agent_id)

def get_system_prompt(agent_id: str) -> str:
    """Construit un prompt système simple en fonction du rôle et de la personnalité."""
    agent = get_agent(agent_id)
    personality = agent.get("personality", "")
    role = agent.get("role", "field")

    if role == "field":
        return (
            f"{personality}\n"
            "You are a historical character in Paris in July 1789. "
            "You speak briefly, in character, based on your own experience."
        )
    if role == "editor":
        return (
            f"{personality}\n"
            "You are the demanding editor-in-chief of a small political newspaper. "
            "You evaluate the journalist's article. Start with 'Good article:' if it "
            "is strong enough to publish and move to the next episode, otherwise start "
            "with 'Try again:' and give precise hints about missing viewpoints or facts."
        )
    if role == "article_evaluator":
        return (
            f"{personality}\n"
            "You are a rigorous historian of the French Revolution. You evaluate whether "
            "a newspaper article correctly explains the storming of the Bastille and its "
            "significance. Start with 'Good answer:' if the understanding is nuanced, "
            "otherwise start with 'Try again:' and explain what is missing."
        )
    return personality

# Mapping target_id -> agent_id
# Tu adaptes target_id pour qu’il corresponde à ce que tu utilises côté Ren’Py.
_TARGET_TO_AGENT = {
    # personnages terrain
    "bastille_worker": "bastille_worker",
    "bastille_soldier": "bastille_soldier",
    "palais_orator": "palais_orator",
    "palais_pamphleteer": "palais_pamphleteer",
    "faubourg_noble": "faubourg_noble",
    "faubourg_deputy": "faubourg_deputy",

    # rédaction / article
    "editor_office": "editor_in_chief",
    "article_submission": "article_evaluator",
}

def resolve_agent_id(target_id: str, explicit_agent: str | None = None) -> str:
    """
    Décide quel agent utiliser.
    - explicit_agent : prioritaire si non nul et existant.
    - sinon target_id -> agent via _TARGET_TO_AGENT.
    - sinon fallback 'default_field'.
    """
    agents = _load_agents()

    if explicit_agent and explicit_agent in agents:
        return explicit_agent

    if target_id in _TARGET_TO_AGENT:
        aid = _TARGET_TO_AGENT[target_id]
        if aid in agents:
            return aid

    if "default_field" in agents:
        return "default_field"
    # fallback extrême : premier agent
    return next(iter(agents.keys()))
