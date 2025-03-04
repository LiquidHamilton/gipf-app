class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.rings = []
        self.markers = []

    def add_ring(self, position):
        """Adds a ring to the player's collection"""
        self.rings.append(position)

    def remove_ring(self, position):
        if position in self.rings:
            self.rings.remove(position)
            return True
        print(f"Attempted to remove non-existent ring at {position}")
        return False

    def add_marker(self, position):
        """Adds a marker to the player's collection"""
        self.markers.append(position)

    def remove_marker(self, position):
        """Removes a marker from the player's collection"""
        self.markers.remove(position)

    def get_rings(self):
        """Returns the player's rings"""
        return self.rings
    
    def get_markers(self):
        """Returns the player's markers"""
        return self.markers