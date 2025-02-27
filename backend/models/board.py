class Board:
    def __init__(self,size):
        self.size = size
        self.grid = self.initialize_board()

    def initialize_board(self):
        """Creates the starting board state"""
        return [[None for _ in range(self.size)] for _ in range(self.size)]
    
    def place_piece(self, position, piece):
        """Places a piece on the board"""
        if self.is_valid_position(position):
            self.grid[position[0]][position[1]] = piece
            return True
        return False
    
    def remove_piece(self, position):
        """Removes a piece from the board"""
        if self.is_valid_position(position):
            self.grid[position[0]][position[1]] = None
            return True
        return False
    
    def is_valid_position(self, position):
        """Checks if a position is valid on the board"""
        x, y = position
        return 0 <= x < self.size and 0 <= y < self.size
    
    def get_board_state(self):
        """Returns the current board state"""
        return self.grid
    
    def get_piece(self, position):
        """Returns the piece at a given position"""
        if self.is_valid_position(position):
            return self.grid[position[0]][position[1]]
        return None
