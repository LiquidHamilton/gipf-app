class Board:
    def __init__(self, row_lengths):
        self.row_lengths = row_lengths
        self.grid = self.initialize_board()
        self.markers_grid = self.initialize_board()  # Separate grid for markers

    def initialize_board(self):
        """Creates the board grid based on the provided row lengths."""
        return [[None for _ in range(length)] for length in self.row_lengths]
    
    def place_piece(self, position, piece):
        """Places a piece (ring or marker) on the board."""
        if self.is_valid_position(position):
            row, col = position
            self.grid[row][col] = piece
            return True
        return False
    
    def place_marker(self, position, player_id):
        """Places a marker on the board."""
        if self.is_valid_position(position):
            row, col = position
            self.markers_grid[row][col] = player_id
            return True
        return False
    
    def remove_piece(self, position):
        """Removes a piece (ring or marker) from the board."""
        if self.is_valid_position(position):
            row, col = position
            self.grid[row][col] = None
            return True
        return False
    
    def remove_marker(self, position):
        """Removes a marker from the board."""
        if self.is_valid_position(position):
            row, col = position
            self.markers_grid[row][col] = None
            return True
        return False
       
    def get_board_state(self):
        """Returns the current board grid."""
        return self.grid
    
    def get_markers_state(self):
        """Returns the current markers grid."""
        return self.markers_grid
    
    def get_piece(self, position):
        """Returns ring OR marker at position (None if both empty)"""
        if self.is_valid_position(position):
            row, col = position
            return self.grid[row][col] or self.markers_grid[row][col]
        return None
    
    def is_valid_position(self, position):
        """Checks if a position is valid on the board based on row lengths."""
        row, col = position
        if row < 0 or row >= len(self.row_lengths):
            return False
        # Handle odd-r offset column wrapping
        max_col = self.row_lengths[row] - 1
        if col < 0 or col > max_col:
            return False
        return True
    
    def get_ring(self, position):
        """Returns ring at position (None if empty)"""
        row, col = position
        return self.grid[row][col] if self.is_valid_position(position) else None

    def get_marker(self, position):
        """Returns marker at position (None if empty)"""
        row, col = position
        return self.markers_grid[row][col] if self.is_valid_position(position) else None