"""
Dialogue helpers - Bridge between Ren'Py screens and dialogue manager.
Provides high-level functions for dialogue interaction in Ren'Py screens.
"""
import renpy
from dialogue_manager import DialogueManager

# Global dialogue manager instance
_dialogue_manager = None


def init_dialogue_system():
    """Initialize the dialogue system. Call this once at game start."""
    global _dialogue_manager
    _dialogue_manager = DialogueManager()


def get_dialogue_manager():
    """Get the global dialogue manager instance."""
    global _dialogue_manager
    if _dialogue_manager is None:
        init_dialogue_system()
    return _dialogue_manager


def dialogue_start_exchange(player_input, agent_id, target_id=None):
    """
    Start a new dialogue exchange.
    
    Args:
        player_input: The player's message
        agent_id: ID of the agent/character
        target_id: Optional target/interaction ID
    """
    manager = get_dialogue_manager()
    manager.start_exchange(player_input, agent_id, target_id)


def get_current_dialogue_exchange():
    """Get the current dialogue exchange data."""
    manager = get_dialogue_manager()
    return manager.get_current_exchange()


def get_current_dialogue_option():
    """Get the currently selected dialogue option."""
    manager = get_dialogue_manager()
    exchange = manager.get_current_exchange()
    if exchange and hasattr(exchange, 'player_options'):
        options = exchange.player_options
        index = manager.current_option_index
        if 0 <= index < len(options):
            return options[index]
    return ""


def get_current_option_index():
    """Get the index of the currently selected option."""
    manager = get_dialogue_manager()
    return manager.current_option_index


def get_total_dialogue_options():
    """Get the total number of dialogue options available."""
    manager = get_dialogue_manager()
    exchange = manager.get_current_exchange()
    if exchange and hasattr(exchange, 'player_options'):
        return len(exchange.player_options)
    return 0


def is_dialogue_generating():
    """Check if the dialogue system is currently generating a response."""
    manager = get_dialogue_manager()
    return manager.is_generating


def navigate_dialogue_next_option():
    """Navigate to the next dialogue option."""
    manager = get_dialogue_manager()
    manager.next_option()


def navigate_dialogue_prev_option():
    """Navigate to the previous dialogue option."""
    manager = get_dialogue_manager()
    manager.prev_option()


def navigate_dialogue_next_exchange():
    """Navigate to the next dialogue exchange in history."""
    manager = get_dialogue_manager()
    manager.next_exchange()


def navigate_dialogue_prev_exchange():
    """Navigate to the previous dialogue exchange in history."""
    manager = get_dialogue_manager()
    manager.prev_exchange()


def is_viewing_past_dialogue():
    """Check if the player is viewing past dialogue (not the current exchange)."""
    manager = get_dialogue_manager()
    return manager.is_viewing_past()


def dialogue_select_option(option_index):
    """
    Select a dialogue option and start a new exchange.
    
    Args:
        option_index: Index of the selected option
    """
    manager = get_dialogue_manager()
    exchange = manager.get_current_exchange()
    if exchange and hasattr(exchange, 'player_options'):
        options = exchange.player_options
        if 0 <= option_index < len(options):
            selected_text = options[option_index]
            manager.start_exchange(selected_text, manager.current_agent_id)


def resolve_agent_for_target(target_id):
    """
    Resolve the agent ID for a given target/interaction ID.
    
    Args:
        target_id: The target/interaction ID
        
    Returns:
        The agent ID associated with this target
    """
    # This is a simple implementation - you may need to enhance it
    # to look up the agent from game data
    if target_id:
        return target_id
    return "default_agent"


def switch_to_agent(agent_id):
    """
    Switch the current active agent.
    
    Args:
        agent_id: ID of the agent to switch to
    """
    manager = get_dialogue_manager()
    manager.switch_agent(agent_id)


def get_dialogue_history(agent_id=None):
    """
    Get the dialogue history for a specific agent or the current agent.
    
    Args:
        agent_id: Optional agent ID. If None, uses current agent.
        
    Returns:
        List of dialogue exchanges
    """
    manager = get_dialogue_manager()
    if agent_id is None:
        agent_id = manager.current_agent_id
    return manager.get_history(agent_id)


def clear_dialogue_history(agent_id=None):
    """
    Clear the dialogue history for a specific agent or the current agent.
    
    Args:
        agent_id: Optional agent ID. If None, uses current agent.
    """
    manager = get_dialogue_manager()
    if agent_id is None:
        agent_id = manager.current_agent_id
    manager.clear_history(agent_id)
