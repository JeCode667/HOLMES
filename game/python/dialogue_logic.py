# dialogue_logic.py — GPT4All blocking inference (for debugging & testing)
import renpy.exports as renpy_exports
from python.llm_local_bind import generate_sync

SYSTEM_PROMPT = (
    "You are a historical dialogue evaluator for the game HOLMES. "
    "Judge whether the player's reply shows understanding of the scene and clues."
)

QWEN_CHAT_TEMPLATE = (
    "<|im_start|>system\n{system}\n<|im_end|>\n"
    "<|im_start|>user\n{user}\n<|im_end|>\n"
    "<|im_start|>assistant\n"
)

GENERATION_KWARGS = {
    "max_tokens": 120,
    "temp": 0.35,
    "top_p": 0.92,
    "repeat_penalty": 1.1,
    "n_batch": 4,
}

def process_input(player_text, target_id):
    """Run the local LLM and return (ok, feedback)."""
    text_value = (player_text or "").strip()
    if not text_value:
        feedback = "No input provided."
        renpy_exports.store._dialogue_feedback[0] = feedback
        return False, feedback

    user_prompt = (
        "You are a historical dialogue evaluator for the game HOLMES.\n"
        f"Context: Player interacts with '{target_id}'.\n\n"
        f"Player said: \"{text_value}\"\n\n"
        "Evaluate the answer:\n"
        "- If the response demonstrates understanding or mentions relevant clues, "
        "start with 'Good answer:' followed by a short justification.\n"
        "- Otherwise, start with 'Try again:' followed by a hint.\n"
    )

    final_prompt = QWEN_CHAT_TEMPLATE.format(system=SYSTEM_PROMPT, user=user_prompt)

    # Direct synchronous call to GPT4All
    try:
        out = generate_sync(final_prompt, **GENERATION_KWARGS)
    except Exception as e:
        feedback = f"[Error during inference: {e}]"
        renpy_exports.store._dialogue_feedback[0] = feedback
        return False, feedback

    feedback = out.strip() if out else "[No output from model.]"
    ok = feedback.lower().startswith("good answer")

    # Store feedback for UI access
    renpy_exports.store._dialogue_feedback[0] = feedback
    return ok, feedback


