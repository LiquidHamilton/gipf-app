from models.game import Game
from models.move import Move
from models.player import Player
from models.board import Board

class Yinsh(Game):
    def __init__(self):
        self.board = Board()
        self.players = {
            1: Player(1),
            2: Player(2)
        }
        self.current_player = 1
        self.game_phase = "placing"
        self.markers = []
        self.turn_count = 0
        self.game_over = False

    def place_ring(self, player_id, position):
        """Place a ring for the player at the specified position."""
        if self.board.is_valid_position(position) and not self.board.get_piece(position):
            self.players[player_id].rings.append(position)
            self.board.place_piece(position, player_id)
            return True
        return False

    def move_ring(self, player_id, start, end):
        """Move a ring from start to end position."""
        if self.board.is_valid_position(start) and self.board.is_valid_position(end):
            if start in self.players[player_id].rings:
                self.players[player_id].rings.remove(start)
                self.players[player_id].rings.append(end)
                self.board.remove_piece(start)
                self.board.place_piece(end, player_id)
                self.flip_markers(start, end)
                return True
        return 

    def flip_markers(self, start, end, dry_run=False):
        """Flips markers between start and end position."""
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

        if not dry_run:
            for marker in flipped_markers:
                if marker in self.players[1].markers:
                    self.players[1].remove_marker(marker)
                    self.players[2].add_marker(marker)
                elif marker in self.players[2].markers:
                    self.players[2].remove_marker(marker)
                    self.players[1].add_marker(marker)
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
    
    def switch_turns(self):
        """Switch the current player."""
        self.current_player = 3 - self.current_player
        self.turn_count += 1
        if self.turn_count >= 10:
            self.game_phase = "playing"