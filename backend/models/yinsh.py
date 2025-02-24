from models.game import Game
from models.move import Move

class Yinsh(Game):
    def __init__(self):
        super().__init__(board_size=11)  # 11x11 hexagonal board
        self.game_phase = "placing"
        self.markers = []

    def place_ring(self, player_id, position):
        """Places a ring during the initial placing phase."""
        if self.game_phase != "placing":
            return False
        if len(self.players[player_id].rings) >= 5:
            return False
        if not self.board.is_valid_position(position):
            return False
        if self.board.get_piece(position) is not None:
            return False
        self.board.place_piece(position, player_id)
        self.players[player_id].rings.append(position)
        if len(self.players[1].rings) == 5 and len(self.players[2].rings) == 5:
            self.game_phase = "playing"
        return True

    def move_ring(self, player_id, start_pos, end_pos):
        print(f"Current game phase: {self.game_phase}")  # Debug statement
        print(f"Current player: {self.current_player}")  # Debug statement
        print(f"Player {player_id} rings: {self.players[player_id].rings}")  # Debug statement


        if self.game_phase != "playing":
            print("Move failed: game phase is not 'playing'")  # Debug statement
            return False
        if player_id != self.current_player:
            print(f"Move failed: not player {player_id}'s turn")  # Debug statement
            return False
        if start_pos not in self.players[player_id].rings:
            print(f"Move failed: start position {start_pos} not in player {player_id}'s rings")  # Debug statement
            return False
        if end_pos in self.players[1].rings or end_pos in self.players[2].rings:
            print(f"Move failed: end position {end_pos} occupied by a ring")  # Debug statement
            return False
        self.players[player_id].remove_ring(start_pos)
        self.players[player_id].add_ring(end_pos)
        self.players[player_id].add_marker(start_pos)
        self.flip_markers(start_pos, end_pos)
        self.switch_turns()
        print(f"Move successful: {start_pos} -> {end_pos}")  # Debug statement
        return True

    def flip_markers(self, start, end, dry_run=False):
        """Flips markers between start and end position."""
        print(f"Flipping markers from {start} to {end}, dry_run={dry_run}")  # Debug statement


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

            if (x, y) in self.players[1].markers or (x, y) in self.players[2].markers:
                flipped_markers.append((x, y))

        print(f"Dry run mode: {dry_run}, Markers to flip: {flipped_markers}")  # Debug statement
        if not dry_run:
            for marker in flipped_markers:
                if marker in self.players[1].markers:
                    self.players[1].remove_marker(marker)
                    self.players[2].add_marker(marker)
                elif marker in self.players[2].markers:
                    self.players[2].remove_marker(marker)
                    self.players[1].add_marker(marker)
        print(f"Markers flipped: {flipped_markers}")  # Debug statement
        return flipped_markers
    
    def check_potential_win(self, player_id, position):
        """Checks if placing a ring at the given position blocks an opponent's win"""
        opponent_id = 3 - player_id
        directions = [(1,0), (0,1), (1,1), (1,-1)]

        for dx, dy in directions:
            count = 0
            x, y = position
            while self.board.is_valid_position((x, y)) and (self.board.get_piece((x, y)) == opponent_id or (x, y) == position):
                if (x, y) == position or self.board.get_piece((x, y)) == opponent_id:
                    count += 1
                x += dx
                y += dy
            if count >= 5:
                return True # This position can block an opponent's win
    
        return False
    
    def check_immediate_loss(self, player_id, position):
        """Checks if placing a ring at the given position leads to an immediate loss"""
        opponent_id = 3 - player_id
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 0
            x, y = position
            while self.board.is_valid_position((x, y)) and (self.board.get_piece((x, y)) == player_id or (x, y) == position):
                if (x, y) == position or self.board.get_piece((x, y)) == player_id:
                    count += 1
                x += dx
                y += dy
            if count >= 5:
                return True  # This move could lead to immediate loss for the AI player
        
        return 

    def check_winner(self):
        """Checks if a player has won the game"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        to_remove = []

        for x in range(self.board.size):
            for y in range(self.board.size):
                if (x, y) in self.players[1].markers or (x, y) in self.players[2].markers:
                    for dx, dy in directions:
                        sequence = [(x, y)]
                        for i in range(1, 5):
                            nx, ny = x + dx * i, y + dy * i
                            if not self.board.is_valid_position((nx, ny)):
                                break
                            if (nx, ny) in self.players[1].markers or (nx, ny) in self.players[2].markers:
                                sequence.append((nx, ny))
                            else:
                                break
                        if len(sequence) == 5:
                            to_remove.append(sequence)

        if to_remove:
            for sequence in to_remove:
                for pos in sequence:
                    self.players[1].remove_marker(pos)
                    self.players[2].remove_marker(pos)

            self.players[self.current_player].remove_ring(None)  # Remove one ring as a point

            if len(self.players[self.current_player].rings) == 2:  # 3 rings removed -> win
                self.game_over = True
                return self.current_player  # Return winner

        return None  