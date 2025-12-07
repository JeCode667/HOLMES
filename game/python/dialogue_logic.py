
# dialogue_logic.py — couche mince au-dessus des agents + RAG
#
# API attendue par Ren'Py :
#   ok, feedback = process_input(player_text, target_id)
#   resp = get_character_response(character_agent, query, context="")
#
# Tous les détails (agents, RAG, historique) sont délégués à agents.py et rag_store.py.

import renpy.exports as renpy_exports # type: ignore

from llm_local_bind import generate_sync
import agents as agents_mod
import rag_store
import dialogue_config

# Template simple type "chat" (fonctionne avec des modèles instruct ou chat)
CHAT_TEMPLATE = (
    "<|im_start|>system\n{system}\n<|im_end|>\n"
    "<|im_start|>user\n{user}\n<|im_end|>\n"
    "<|im_start|>assistant\n"
)

# Utiliser la configuration centralisée
GENERATION_KWARGS = dialogue_config.get_agent_response_kwargs()

# Valider la configuration au démarrage
dialogue_config.validate_config()

# ---------------------------------------------------------------------
# Construction des prompts utilisateur selon le rôle
# ---------------------------------------------------------------------

def _build_user_prompt_field(agent_id: str, target_id: str, player_text: str) -> str:
    rag_ctx = rag_store.get_rag_context(agent_id, player_text)
    hist_ctx = rag_store.get_history_context(agent_id)

    ctx_parts = []
    if rag_ctx:
        ctx_parts.append("Relevant local facts:\n" + rag_ctx)
    if hist_ctx:
        ctx_parts.append("Earlier dialogue:\n" + hist_ctx)

    context_block = "\n\n".join(ctx_parts) if ctx_parts else "No additional context."

    return (
        f"Location or interaction id: '{target_id}'.\n"
        f"{context_block}\n\n"
        f"The player says to you:\n\"{player_text}\"\n\n"
        "Answer briefly (2–4 sentences), in character, from your limited perspective. "
        "You can hint at what the player should pay attention to, but do not break character."
    )

def _build_user_prompt_editor(agent_id: str, article_text: str) -> str:
    rag_ctx = rag_store.get_rag_context(agent_id, article_text)
    hist_ctx = rag_store.get_history_context(agent_id)

    ctx_parts = []
    if rag_ctx:
        ctx_parts.append("Guidelines for good revolutionary journalism:\n" + rag_ctx)
    if hist_ctx:
        ctx_parts.append("Previous drafts and your feedback:\n" + hist_ctx)

    context_block = "\n\n".join(ctx_parts) if ctx_parts else "No prior submissions."

    return (
        f"You are reviewing a draft article about recent events in Paris.\n"
        f"{context_block}\n\n"
        f"Article draft:\n\"\"\"\n{article_text}\n\"\"\"\n\n"
        "Evaluate this article. Start your answer with 'Good article:' if "
        "it is strong enough to publish and move to the next episode. "
        "Otherwise start with 'Try again:' and specify which angles, facts or "
        "voices are missing and where the journalist should investigate again."
    )

def _build_user_prompt_article_eval(agent_id: str, article_text: str) -> str:
    rag_ctx = rag_store.get_rag_context(agent_id, article_text)
    context_block = rag_ctx if rag_ctx else "No external context."

    return (
        f"Historical notes:\n{context_block}\n\n"
        f"Newspaper article:\n\"\"\"\n{article_text}\n\"\"\"\n\n"
        "Decide whether this article correctly explains the storming of the Bastille "
        "and its meaning for the beginning of the French Revolution. "
        "Start with 'Good answer:' if the article integrates both the spontaneous "
        "crowd action and the political/symbolic significance. Otherwise start with "
        "'Try again:' and explain what aspects are missing or oversimplified."
    )

# ---------------------------------------------------------------------
# API principale
# ---------------------------------------------------------------------

def process_input(player_text: str, target_id: str, character_agent: str | None = None):
    """
    Fonction appelée par Ren'Py.
    Renvoie (ok, feedback).
    - ok: bool (True si l'agent juge que la réponse est suffisante pour progresser),
    - feedback: texte affiché (réplique personnage ou rédacteur).
    """
    text_value = (player_text or "").strip()
    if not text_value:
        feedback = "No input provided."
        renpy_exports.store._dialogue_feedback[0] = feedback
        return False, feedback

    agent_id = agents_mod.resolve_agent_id(target_id, explicit_agent=character_agent)
    role = agents_mod.get_role(agent_id)
    system_prompt = agents_mod.get_system_prompt(agent_id)

    if role == "editor":
        user_prompt = _build_user_prompt_editor(agent_id, text_value)
    elif role == "article_evaluator":
        user_prompt = _build_user_prompt_article_eval(agent_id, text_value)
    else:
        user_prompt = _build_user_prompt_field(agent_id, target_id, text_value)

    prompt = CHAT_TEMPLATE.format(system=system_prompt, user=user_prompt)

    out = generate_sync(prompt, **GENERATION_KWARGS)
    feedback = (out or "").strip() or "[No output from model.]"

    fl = feedback.lower()
    if role == "editor":
        ok = fl.startswith("good article:")
    elif role == "article_evaluator":
        ok = fl.startswith("good answer:")
    else:
        # pour les personnages, tu peux choisir d'interpréter 'Good answer:' comme succès
        ok = fl.startswith("good answer:")

    # mémorisation dans historique (utile pour contexte RAG)
    rag_store.add_history(agent_id, text_value, feedback)

    renpy_exports.store._dialogue_feedback[0] = feedback
    return ok, feedback

def get_character_response(character_agent: str, query: str, context: str = "") -> str:
    """
    Réponse simple d'un agent (sans logique Good/Try again).
    Utile pour du dialogue pur non évaluatif.
    """
    agent_id = agents_mod.resolve_agent_id(target_id="", explicit_agent=character_agent)
    system_prompt = agents_mod.get_system_prompt(agent_id)

    rag_ctx = rag_store.get_rag_context(agent_id, query)
    hist_ctx = rag_store.get_history_context(agent_id)

    parts = []
    if context:
        parts.append("Scene context:\n" + context)
    if rag_ctx:
        parts.append("Relevant facts:\n" + rag_ctx)
    if hist_ctx:
        parts.append("Earlier dialogue:\n" + hist_ctx)

    context_block = "\n\n".join(parts) if parts else "No additional context."

    user_prompt = (
        f"{context_block}\n\n"
        f"The player says: \"{query}\"\n\n"
        f"Respond in character as {agents_mod.get_name(agent_id)}, briefly (2–4 sentences)."
    )

    prompt = CHAT_TEMPLATE.format(system=system_prompt, user=user_prompt)
    out = generate_sync(prompt, **GENERATION_KWARGS)
    response = (out or "").strip() or "[No response from model.]"

    rag_store.add_history(agent_id, query, response)
    return response
