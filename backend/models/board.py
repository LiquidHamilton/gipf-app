class Board:
    def __init__(self, row_lengths):
        self.row_lengths = row_lengths
        self.grid = self.initialize_board()

    def initialize_board(self):
        """Creates the board grid based on the provided row lengths."""
        return [[None for _ in range(length)] for length in self.row_lengths]
    
    def place_piece(self, position, piece):
        """Places a piece on the board."""
        if self.is_valid_position(position):
            row, col = position
            self.grid[row][col] = piece
            return True
        return False
    
    def remove_piece(self, position):
        """Removes a piece from the board."""
        if self.is_valid_position(position):
            row, col = position
            self.grid[row][col] = None
            return True
        return False
       
    def get_board_state(self):
        """Returns the current board grid."""
        return self.grid
    
    def get_piece(self, position):
        """Returns the piece at the given position."""
        if self.is_valid_position(position):
            row, col = position
            return self.grid[row][col]
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