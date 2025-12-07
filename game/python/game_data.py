"""
GameData class for loading and managing game content from JSON.
"""
import json
import os
import renpy


class GameData:
    """Manages game content loaded from game_content.json"""
    
    def __init__(self, json_path=None):
        """Initialize and load game data from JSON file."""
        if json_path is None:
            # Use relative path from game directory for renpy.open_file
            json_path = "data/game_content.json"
        
        self.data = {}
        self.world_title = "Game World"
        self.world_image = "images/maps/world_map.png"
        self.primary_stage_id = None
        
        try:
            with renpy.open_file(json_path) as f:
                self.data = json.load(f)
            self._parse_data()
            print(f"[HOLMES] Successfully loaded game data from {json_path}")
        except Exception as e:
            print(f"[HOLMES] Warning: Could not load game_content.json: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_data(self):
        """Parse loaded JSON data and set up quick access properties."""
        world_map = self.data.get("world_map", {})
        self.world_title = world_map.get("title", "Game World")
        self.world_image = world_map.get("image", "images/maps/world_map.png")
        
        # Find primary stage (first with default_unlocked)
        stages = world_map.get("stages", [])
        for stage in stages:
            if stage.get("default_unlocked"):
                self.primary_stage_id = stage.get("id")
                break
        
        if not self.primary_stage_id and stages:
            self.primary_stage_id = stages[0].get("id")
    
    def resolve_area_id(self, area_id):
        """Resolve area identifier to actual area ID."""
        # This is a placeholder for more complex resolution logic
        return area_id
    
    def get_area(self, area_id):
        """Get area data by ID."""
        world_map = self.data.get("world_map", {})
        stages = world_map.get("stages", [])
        
        for stage in stages:
            areas = stage.get("areas", [])
            for area in areas:
                if area.get("id") == area_id:
                    return area
        return None
    
    def get_stage(self, stage_id):
        """Get stage data by ID."""
        world_map = self.data.get("world_map", {})
        stages = world_map.get("stages", [])
        
        for stage in stages:
            if stage.get("id") == stage_id:
                return stage
        return None
    
    def iter_stage_entries(self):
        """Iterate over all stage entries."""
        world_map = self.data.get("world_map", {})
        stages = world_map.get("stages", [])
        return iter(stages)
    
    def get_stage_areas(self, stage_id):
        """Get all areas for a stage."""
        stage = self.get_stage(stage_id)
        if stage:
            return stage.get("areas", [])
        return []
    
    def get_area_interactions(self, area_id):
        """Get all interactions for an area."""
        area = self.get_area(area_id)
        if area:
            return area.get("interactions", [])
        return []
    
    def get_interactions(self, area_id):
        """Alias for get_area_interactions."""
        return self.get_area_interactions(area_id)
    
    def get_area_stage(self, area_id):
        """Get the stage ID that contains a specific area."""
        world_map = self.data.get("world_map", {})
        stages = world_map.get("stages", [])
        
        for stage in stages:
            areas = stage.get("areas", [])
            for area in areas:
                if area.get("id") == area_id:
                    return stage.get("id")
        return None
    
    def get_interaction(self, interaction_id):
        """Get a specific interaction by ID from any area."""
        world_map = self.data.get("world_map", {})
        stages = world_map.get("stages", [])
        
        for stage in stages:
            areas = stage.get("areas", [])
            for area in areas:
                interactions = area.get("interactions", [])
                for interaction in interactions:
                    if interaction.get("id") == interaction_id:
                        return interaction
        return None
