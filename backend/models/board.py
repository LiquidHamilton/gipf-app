class Board:
    def __init__(self):
        self.board = self.create_hexagonal_board()

    def create_hexagonal_board(self):
        """Create the hexagonal board layout."""
        return [
            [None, None, None, 1, 1, 1, 1, 1, None, None, None],
            [None, None, 1, 1, 1, 1, 1, 1, 1, None, None],
            [None, 1, 1, 1, 1, 1, 1, 1, 1, 1, None],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [None, 1, 1, 1, 1, 1, 1, 1, 1, 1, None],
            [None, None, 1, 1, 1, 1, 1, 1, 1, None, None],
            [None, None, None, 1, 1, 1, 1, 1, None, None, None]
        ]
    
    def place_piece(self, position, piece):
        """Places a piece on the board"""
        x, y = position
        if self.is_valid_position(position):
            self.board[x][y] = piece
            return True
        return False
    
    def remove_piece(self, position):
        """Removes a piece from the board"""
        x, y = position
        if self.is_valid_position(position):
            self.board[x][y] = 1
            return True
        return False
    
    def is_valid_position(self, position):
        """Checks if a position is valid on the board"""
        x, y = position
        return 0 <= x < len(self.board) and 0 <= y < len(self.board[x]) and self.board[x][y] == 1

    def get_board_state(self):
        """Returns the current board state"""
        return self.board
    
    def get_piece(self, position):
        """Returns the piece at a given position"""
        x, y = position
        if self.is_valid_position(position):
            return self.board[x][y]
        return None