"""
Progression system for tracking player progress through the game.
"""
import renpy


class Progression:
    """Manages player progression and unlocked content."""
    
    def __init__(self):
        """Initialize progression system, loading from persistent storage."""
        self.data = {
            "unlocked_stages": [],
            "unlocked_areas": [],
            "completed_interactions": [],
        }
        
        # Load from Ren'Py persistent storage if available
        if hasattr(renpy.store, "persistent"):
            persistent = renpy.store.persistent
            if hasattr(persistent, "progression_data"):
                self.data.update(persistent.progression_data or {})
    
    def save(self):
        """Save progression data to persistent storage."""
        if hasattr(renpy.store, "persistent"):
            renpy.store.persistent.progression_data = self.data
    
    def unlock_stage(self, stage_id):
        """Unlock a stage."""
        if stage_id not in self.data.get("unlocked_stages", []):
            self.data.setdefault("unlocked_stages", []).append(stage_id)
            self.save()
    
    def unlock_area(self, area_id):
        """Unlock an area."""
        if area_id not in self.data.get("unlocked_areas", []):
            self.data.setdefault("unlocked_areas", []).append(area_id)
            self.save()
    
    def is_stage_unlocked(self, stage_id):
        """Check if a stage is unlocked."""
        return stage_id in self.data.get("unlocked_stages", [])
    
    def is_area_unlocked(self, area_id):
        """Check if an area is unlocked."""
        return area_id in self.data.get("unlocked_areas", [])
    
    def complete_interaction(self, interaction_id):
        """Mark an interaction as completed."""
        if interaction_id not in self.data.get("completed_interactions", []):
            self.data.setdefault("completed_interactions", []).append(interaction_id)
            self.save()
    
    def is_interaction_completed(self, interaction_id):
        """Check if an interaction is completed."""
        return interaction_id in self.data.get("completed_interactions", [])
