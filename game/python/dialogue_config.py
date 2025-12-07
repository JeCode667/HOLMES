"""
Dialogue configuration for LLM generation parameters.
"""


def get_agent_response_kwargs():
    """Get the generation parameters for agent responses."""
    return {
        "temp": 0.7,
        "top_k": 40,
        "top_p": 0.9,
        "min_p": 0.0,
        "repeat_penalty": 1.1,
        "repeat_last_n": 64,
        "n_batch": 128,
        "n_predict": 256,
        "streaming": False,
    }


def validate_config():
    """Validate the configuration. Can add checks here if needed."""
    kwargs = get_agent_response_kwargs()
    
    # Basic validation
    if kwargs.get("temp", 0) < 0 or kwargs.get("temp", 0) > 2:
        print("[HOLMES] Warning: temperature should be between 0 and 2")
    
    if kwargs.get("n_predict", 0) < 1:
        print("[HOLMES] Warning: n_predict should be positive")
    
    return True
