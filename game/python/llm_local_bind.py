# llm_local_bind.py — minimal GPT4All bootstrap for Ren'Py
import os
import sys

_current = os.path.abspath(os.path.dirname(__file__))
_game_root = os.path.abspath(os.path.join(_current, os.pardir))

for path in (_current, _game_root):
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from gpt4all import GPT4All
except Exception as e:
    print(f"[HOLMES] ERROR: cannot import GPT4All — {e}")
    print("[HOLMES] Expected path:", os.path.join(_current, "gpt4all"))
    GPT4All = None

MODEL_NAME = "Llama-3.2-1B-Instruct-Q4_0.gguf"
MODEL_DIR = os.path.join(_current, "llm")
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)
DEFAULT_GENERATE_KWARGS = {
    "max_tokens": 128,
    "temp": 0.35,
    "top_p": 0.92,
    "repeat_penalty": 1.1,
    "n_batch": 4,
}

_model = None
if GPT4All is not None:
    try:
        _model = GPT4All(model_name=MODEL_NAME, model_path=MODEL_DIR, allow_download=False)
        print(f"[HOLMES] GPT4All model loaded successfully from: {MODEL_PATH}")
    except Exception as e:
        print(f"[HOLMES] ERROR while loading GPT4All model: {e}")

def generate_sync(prompt: str, **generate_kwargs):
    """
    Generate a response from the local GPT4All model using the prompt provided.
    Accepts optional keyword arguments for GPT4All.generate.
    """
    if _model is None:
        return "[Error] GPT4All not available or failed to load."

    try:
        params = DEFAULT_GENERATE_KWARGS.copy()
        params.update(generate_kwargs)
        raw_output = _model.generate(prompt, **params)
        if isinstance(raw_output, str):
            text_output = raw_output
        else:
            try:
                text_output = "".join(raw_output)
            except TypeError:
                text_output = str(raw_output)
        print(f"[HOLMES] GPT4All output: {text_output}")

        if not text_output:
            snippet = prompt[:120].replace("\n", " ") + ("..." if len(prompt) > 120 else "")
            print(f"[HOLMES] WARNING: GPT4All returned empty output for prompt: {snippet}")
            return "[Error] Local model produced no output."

        return text_output.strip()
    except Exception as e:
        print(f"[HOLMES] ERROR during inference: {e}")
        return f"[Error during inference: {e}]"

