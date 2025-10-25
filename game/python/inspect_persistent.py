"""
Script to safely load and inspect a Ren'Py persistent file.
Run from within Ren'Py with: $ python -m python.inspect_persistent
"""
import os
import sys
import pickle
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("inspect_persistent")

def safe_load(path: str) -> Dict[str, Any]:
    """Load a persistent file with error handling."""
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
            log.info(f"Successfully loaded {path}")
            return data
    except Exception as e:
        log.error(f"Error loading {path}: {e}")
        return {}

def inspect_object(obj: Any, path: str = "", max_depth: int = 3) -> None:
    """Recursively inspect an object's structure up to max_depth."""
    if max_depth <= 0:
        log.info(f"{path} = <max depth reached>")
        return
    
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else str(k)
            inspect_object(v, new_path, max_depth - 1)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            new_path = f"{path}[{i}]"
            inspect_object(v, new_path, max_depth - 1)
    else:
        log.info(f"{path} = {type(obj).__name__}({repr(obj)[:100]}{'...' if len(repr(obj)) > 100 else ''})")

def main():
    """Main inspection function."""
    saves_dir = os.path.join(os.path.dirname(__file__), "..", "saves")
    
    # Try both the main and backup files
    paths = [
        os.path.join(saves_dir, "persistent.bak"),
        os.path.join(saves_dir, "sync", "persistent.bak"),
    ]
    
    for path in paths:
        if os.path.exists(path):
            log.info(f"\nInspecting {path}:")
            data = safe_load(path)
            if data:
                inspect_object(data)
        else:
            log.warning(f"File not found: {path}")

if __name__ == "__main__":
    main()