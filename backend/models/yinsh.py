from models.game import Game
from models.move import Move

class Yinsh(Game):
    def __init__(self):
        super().__init__(board_size=11)  # 11x11 hexagonal board
        self.game_phase = "placing"
        self.markers = []

    def place_ring(self, player_id, position):
        if self.game_phase != "placing":
            return False
        if position in self.players[1].rings or position in self.players[2].rings:
            return False
        self.players[player_id].add_ring(position)
        self.board.place_piece(position, player_id)
        if len(self.players[1].rings) == 5 and len(self.players[2].rings) == 5:
            self.game_phase = "playing"
        return True

    def move_ring(self, player_id, start_pos, end_pos):
        move = Move(player_id, start_pos, end_pos)
        if move.execute(self):
            self.flip_markers(start_pos, end_pos)
            return True
        return False

    def flip_markers(self, start, end):
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

        # Flip markers in the list
        for marker in flipped_markers:
            if marker in self.players[1].markers:
                self.players[1].remove_marker(marker)
                self.players[2].add_marker(marker)
            elif marker in self.players[2].markers:
                self.players[2].remove_marker(marker)
                self.players[1].add_marker(marker)

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