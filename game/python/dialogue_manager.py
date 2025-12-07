# dialogue_manager.py — gestion avancée du dialogue avec historique et navigation
#
# Fonctionnalités :
#   - Stockage de l'historique complet du dialogue (joueur -> agent -> propositions de réponse)
#   - Navigation entre les réponses avec précédent/suivant
#   - Génération des réponses de l'agent de manière asynchrone
#   - Gestion de l'état du dialogue (attente, affichage, navigation)

import renpy.exports as renpy_exports  # type: ignore
from typing import Optional, List, Dict, Any
import threading

from llm_local_bind import generate_sync
import agents as agents_mod
import dialogue_logic
import rag_store

# Structure pour un échange de dialogue
class DialogueExchange:
    """Représente un échange complet : question du joueur + réponse de l'agent + propositions de réponse"""
    def __init__(self, player_input: str, agent_id: str, agent_name: str):
        self.player_input = player_input
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_response = ""  # Réponse générée par l'agent
        self.player_options: List[str] = []  # Options de réponse proposées au joueur
        self.is_generating = True  # En attente de génération
        
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise l'échange pour stockage Ren'Py"""
        return {
            "player_input": self.player_input,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_response": self.agent_response,
            "player_options": self.player_options,
            "is_generating": self.is_generating,
        }


class DialogueManager:
    """Gestionnaire central du dialogue"""
    
    def __init__(self):
        self.dialogue_histories: Dict[str, List[DialogueExchange]] = {}  # Historique par agent_id
        self.current_agent_id: Optional[str] = None  # Agent actuel
        self.current_exchange_index = -1  # Index de l'échange actuel
        self.current_option_index = 0  # Index de l'option sélectionnée
        self.is_generating = False  # En train de générer une réponse d'agent
        
    def start_exchange(self, player_input: str, agent_id: str, target_id: str) -> Optional[DialogueExchange]:
        """
        Démarre un nouvel échange de dialogue.
        Lance la génération asynchrone de la réponse de l'agent.
        """
        text_value = (player_input or "").strip()
        if not text_value:
            return None
        
        # Changer d'agent si nécessaire
        if self.current_agent_id != agent_id:
            self.current_agent_id = agent_id
            # Initialiser l'historique pour cet agent si nécessaire
            if agent_id not in self.dialogue_histories:
                self.dialogue_histories[agent_id] = []
        
        agent_name = agents_mod.get_name(agent_id)
        exchange = DialogueExchange(text_value, agent_id, agent_name)
        
        # Ajouter à l'historique de cet agent
        self.dialogue_histories[agent_id].append(exchange)
        self.current_exchange_index = len(self.dialogue_histories[agent_id]) - 1
        self.current_option_index = 0
        
        # Lancer la génération de la réponse
        self._generate_agent_response_async(exchange, target_id)
        
        return exchange
        
    def _generate_agent_response_async(self, exchange: DialogueExchange, target_id: str):
        """
        Génère la réponse de l'agent dans un thread séparé pour ne pas bloquer.
        """
        def _generate():
            try:
                system_prompt = agents_mod.get_system_prompt(exchange.agent_id)
                user_prompt = dialogue_logic._build_user_prompt_field(
                    exchange.agent_id, 
                    target_id, 
                    exchange.player_input
                )
                
                prompt = dialogue_logic.CHAT_TEMPLATE.format(
                    system=system_prompt, 
                    user=user_prompt
                )
                
                # Génération synchrone du modèle
                response = generate_sync(prompt, **dialogue_logic.GENERATION_KWARGS)
                exchange.agent_response = (response or "").strip() or "[No response from model.]"
                
                # Génération des options de réponse (propositions pour le joueur)
                exchange.player_options = self._generate_player_options(
                    exchange.agent_id, 
                    exchange.player_input, 
                    exchange.agent_response,
                    target_id
                )
                
                # Mémoriser dans l'historique RAG
                rag_store.add_history(exchange.agent_id, exchange.player_input, exchange.agent_response)
                
            except Exception as e:
                exchange.agent_response = f"[Error: {str(e)}]"
                exchange.player_options = []
            finally:
                exchange.is_generating = False
                self.is_generating = False
        
        self.is_generating = True
        exchange.is_generating = True
        
        # Lancer dans un thread
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()
        
    def _generate_player_options(self, agent_id: str, player_input: str, agent_response: str, target_id: str) -> List[str]:
        """
        Génère 3-4 options de réponse pour le joueur basées sur le contexte.
        """
        system_prompt = (
            "You are a dialogue option generator for a visual novel. "
            "Generate 3 realistic and distinct response options that the player could say next. "
            "Each option should be 1 short sentence (5-10 words). "
            "Make options diverse: one could be inquisitive, one confrontational or curious, and one could be friendly or neutral. "
            "Format: Option 1: [text]\nOption 2: [text]\nOption 3: [text]"
        )
        
        user_prompt = (
            f"Previous context:\nPlayer asked: \"{player_input}\"\n"
            f"{agents_mod.get_name(agent_id)} responded: \"{agent_response}\"\n\n"
            "Generate 3 distinct response options the player could choose from."
        )
        
        prompt = dialogue_logic.CHAT_TEMPLATE.format(system=system_prompt, user=user_prompt)
        
        try:
            response = generate_sync(prompt, **{**dialogue_logic.GENERATION_KWARGS, "max_tokens": 100})
            options = self._parse_options(response)
            
            # Fallback options si la génération échoue
            if not options or len(options) < 2:
                options = [
                    "Tell me more about that.",
                    "What do you mean exactly?",
                    "I understand. What's next?",
                ]
            
            return options[:4]  # Max 4 options
            
        except Exception as e:
            print(f"[HOLMES] Error generating player options: {e}")
            return [
                "Tell me more about that.",
                "What do you mean exactly?",
                "I understand.",
            ]
    
    def _parse_options(self, text: str) -> List[str]:
        """Parse les options générées par le modèle"""
        options = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if line and (":" in line):
                # Format: "Option N: [text]"
                parts = line.split(":", 1)
                if len(parts) == 2:
                    option_text = parts[1].strip()
                    if option_text:
                        options.append(option_text)
        return options
    
    def get_current_exchange(self) -> Optional[DialogueExchange]:
        """Retourne l'échange actuel"""
        if not self.current_agent_id or self.current_agent_id not in self.dialogue_histories:
            return None
        
        history = self.dialogue_histories[self.current_agent_id]
        if self.current_exchange_index >= 0 and self.current_exchange_index < len(history):
            return history[self.current_exchange_index]
        return None
    
    def get_current_option(self) -> Optional[str]:
        """Retourne l'option actuellement sélectionnée"""
        exchange = self.get_current_exchange()
        if exchange and self.current_option_index < len(exchange.player_options):
            return exchange.player_options[self.current_option_index]
        return None
    
    def next_option(self) -> bool:
        """Passer à l'option suivante. Retourne True si mouvement effectué."""
        exchange = self.get_current_exchange()
        if not exchange or not exchange.player_options:
            return False
        
        if self.current_option_index < len(exchange.player_options) - 1:
            self.current_option_index += 1
            return True
        return False
    
    def prev_option(self) -> bool:
        """Passer à l'option précédente. Retourne True si mouvement effectué."""
        if self.current_option_index > 0:
            self.current_option_index -= 1
            return True
        return False
    
    def next_exchange(self) -> bool:
        """Naviguer vers l'échange suivant dans l'historique."""
        if not self.current_agent_id or self.current_agent_id not in self.dialogue_histories:
            return False
        
        history = self.dialogue_histories[self.current_agent_id]
        if self.current_exchange_index < len(history) - 1:
            self.current_exchange_index += 1
            self.current_option_index = 0
            return True
        return False
    
    def prev_exchange(self) -> bool:
        """Naviguer vers l'échange précédent dans l'historique."""
        if self.current_exchange_index > 0:
            self.current_exchange_index -= 1
            self.current_option_index = 0
            return True
        return False
    
    def select_current_option(self) -> str:
        """Sélectionne l'option actuelle et la retourne pour traitement"""
        option = self.get_current_option()
        if option:
            return option
        return ""
    
    def clear_dialogue(self, agent_id: Optional[str] = None):
        """Réinitialise le dialogue (pour un agent spécifique ou tous)"""
        if agent_id:
            # Effacer seulement pour cet agent
            if agent_id in self.dialogue_histories:
                self.dialogue_histories[agent_id] = []
            if self.current_agent_id == agent_id:
                self.current_exchange_index = -1
                self.current_option_index = 0
        else:
            # Effacer tout
            self.dialogue_histories = {}
            self.current_agent_id = None
            self.current_exchange_index = -1
            self.current_option_index = 0
        self.is_generating = False
    
    def get_history_summary(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retourne un résumé de l'historique pour affichage"""
        target_agent = agent_id or self.current_agent_id
        if not target_agent or target_agent not in self.dialogue_histories:
            return []
        return [exchange.to_dict() for exchange in self.dialogue_histories[target_agent]]
    
    def switch_agent(self, agent_id: str):
        """Switch to a different agent and load their history."""
        if agent_id != self.current_agent_id:
            self.current_agent_id = agent_id
            # Initialize history for this agent if needed
            if agent_id not in self.dialogue_histories:
                self.dialogue_histories[agent_id] = []
            # Set to most recent exchange for this agent
            history = self.dialogue_histories[agent_id]
            if history:
                self.current_exchange_index = len(history) - 1
            else:
                self.current_exchange_index = -1
            self.current_option_index = 0
    
    def is_viewing_past(self) -> bool:
        """Check if currently viewing a past exchange (not the most recent one)."""
        if not self.current_agent_id or self.current_agent_id not in self.dialogue_histories:
            return False
        history = self.dialogue_histories[self.current_agent_id]
        if not history:
            return False
        return self.current_exchange_index < len(history) - 1
    
    def get_history(self, agent_id: Optional[str] = None) -> List[DialogueExchange]:
        """Get the dialogue history for a specific agent."""
        target_agent = agent_id or self.current_agent_id
        if not target_agent or target_agent not in self.dialogue_histories:
            return []
        return self.dialogue_histories[target_agent]
    
    def clear_history(self, agent_id: Optional[str] = None):
        """Clear the history for a specific agent."""
        target_agent = agent_id or self.current_agent_id
        if target_agent and target_agent in self.dialogue_histories:
            self.dialogue_histories[target_agent] = []
            if self.current_agent_id == target_agent:
                self.current_exchange_index = -1
                self.current_option_index = 0


# Instance globale du gestionnaire
_dialogue_manager: Optional[DialogueManager] = None


def get_dialogue_manager() -> DialogueManager:
    """Retourne l'instance globale du gestionnaire de dialogue"""
    global _dialogue_manager
    if _dialogue_manager is None:
        _dialogue_manager = DialogueManager()
    return _dialogue_manager


def init_dialogue_manager():
    """Initialise le gestionnaire (appelé au démarrage du jeu)"""
    global _dialogue_manager
    _dialogue_manager = DialogueManager()


def start_dialogue_exchange(player_input: str, agent_id: str, target_id: str) -> Optional[DialogueExchange]:
    """API pour Ren'Py : démarre un nouvel échange de dialogue"""
    manager = get_dialogue_manager()
    return manager.start_exchange(player_input, agent_id, target_id)


def is_generating_response() -> bool:
    """Vérifie si une réponse est en cours de génération"""
    manager = get_dialogue_manager()
    return manager.is_generating


def get_current_exchange_dict() -> Dict[str, Any]:
    """Retourne l'échange actuel sous forme de dictionnaire"""
    manager = get_dialogue_manager()
    exchange = manager.get_current_exchange()
    if exchange:
        return exchange.to_dict()
    return {}


def get_current_option_text() -> str:
    """Retourne le texte de l'option actuellement sélectionnée"""
    manager = get_dialogue_manager()
    option = manager.get_current_option()
    return option or ""


def navigate_next_option() -> bool:
    """Navigation : option suivante"""
    manager = get_dialogue_manager()
    return manager.next_option()


def navigate_prev_option() -> bool:
    """Navigation : option précédente"""
    manager = get_dialogue_manager()
    return manager.prev_option()


def navigate_next_exchange() -> bool:
    """Navigation : échange suivant"""
    manager = get_dialogue_manager()
    return manager.next_exchange()


def navigate_prev_exchange() -> bool:
    """Navigation : échange précédent"""
    manager = get_dialogue_manager()
    return manager.prev_exchange()


def select_option_and_continue(player_input: str, agent_id: str, target_id: str):
    """Sélectionne l'option actuelle et démarre un nouvel échange"""
    manager = get_dialogue_manager()
    option = manager.select_current_option()
    if option:
        return start_dialogue_exchange(option, agent_id, target_id)
    return None


def clear_dialogue_state():
    """Réinitialise l'état du dialogue"""
    manager = get_dialogue_manager()
    manager.clear_dialogue()
