class Yinsh:
    def __init__(self):
        self.board = self.initalize_board()
        self.rings = {1: [], 2: []} # Player 1 and 2 ring positions
        self.markers = []
        self.current_player = 1
        self.game_phase = "placing" # "placing" -> "playing"
        self.game_over = False

    def initalize_board(self):
        """Creates the starting board state"""
        board = [[None for _ in range (11)] for _ in range (11)] #11x11 hexoganal board
        return board
    
    def place_ring(self, player, position):
        """Places a ring on the board during inital phase"""
        if self.game_phase != "placing":
            return False # Cannot place rings after placement phase
        
        if position in self.rings[1] or position in self.rings[2]:
            return False # Position occupied
        
        self.rings[player].append(position)
        if len(self.rings[1]) == 5 and len(self.rings[2]) == 5:
            self.game_phase = "playing" # Transition to movement phase
        return True
    
    def move_ring(self, player, start_pos, end_pos):
        """moves a ring and places a marker"""
        if self.game_phase != "playing":
            return False
        if player != self.current_player:
            return False #Not the players turn
        if start_pos not in self.rings[player] or end_pos in self.rings[1] or end_pos in self.rings[2]:
            return False
        
        # Place a marker at the start position
        self.markers.append(start_pos)
        self.rings[player].remove(start_pos)
        self.rings[player].append(end_pos)

        # Flip any markers in the path (refine this later)
        self.flip_markers(start_pos, end_pos)

        # Switch turns
        self.current_player = 3 - player
        return True
    
    def flip_markers(self, start, end):
        """Flips markers between start and end position."""
        # Determine movement direction
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        # Normalize direction to get unit step
        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)

        x, y = start
        flipped_markers = []

        # Move along the path and flip markers
        while (x, y) != end:
            x += step_x
            y += step_y

            if (x,y) in self.markers:
                flipped_markers.append((x,y))
            elif (x,y) in self.rings[1] or (x,y) in self.rings[2]:
                break # Stop flipping if a ring is encountered

        # Flip markers in the list
        for marker in flipped_markers:
            if marker in self.markers:
                self.markers.remove(marker)
            else:
                self.markers.append(marker)
        
        return True

    def check_winner(self):
        """Checks if a player has won the game"""
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        to_remove = []

        for x in range(11):
            for y in range(11):
                if (x,y) in self.markers:
                    for dx, dy in directions:
                        sequence = [(x, y)]
                        for i in range(1,5):
                            nx, ny = x + dx * i, y + dy * i
                            if (nx, ny) in self.markers:
                                sequence.append((nx, ny))
                            else:
                                break
                        if len(sequence) == 5:
                            to_remove.append(sequence)
        if to_remove:
            for sequence in to_remove:
                for pos in sequence:
                    self.markers.remove(pos) # Remove markers from board
            self.rings[self.current_player].pop() # Remove one ring as a point

            if len(self.rings[self.current_player]) == 2: # 3 rings removed -> win
                self.game_over = True
                return self.current_player # Return winner
            
        return None # No winner yet
    
    def get_game_state(self):
        """Returns the current game state"""
        return {
            "board": self.board,
            "rings": self.rings,
            "markers": self.markers,
            "current_player": self.current_player,
            "game_phase": self.game_phase,
            "game_over": self.game_over
        }
    
