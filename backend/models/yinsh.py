from models.game import Game
from models.move import Move

def offset_to_axial(row, col):
    """
    Converts odd-r offset coordinates to axial coordinates.
    Assumes an odd-r layout.
    """
    q = col - (row - (row & 1)) // 2
    r = row
    return (q, r)

def axial_to_offset(q, r):
    """
    Converts axial coordinates back to odd-r offset coordinates.
    For odd-r: row = r, col = q + (r - (r & 1)) // 2.
    """
    col = q + (r - (r & 1)) // 2
    return (r, col)

def axial_direction(direction):
    dq, dr = direction
    if dq != 0:
        dq = dq // abs(dq)
    if dr != 0:
        dr = dr // abs(dr)
    return (dq, dr)

class Yinsh(Game):
    def __init__(self):
        # Define the irregular board layout for YINSH.
        board_layout = [2, 3, 4, 5, 4, 5, 6, 5, 6, 5, 6, 5, 6, 5, 4, 5, 4, 3, 2]
        super().__init__(board_layout)
        self.game_phase = "placing"
        self.markers = []
        self.scored_rings = {1: [], 2: []}  # Track scored rings


    def place_ring(self, player_id, position):
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
        print(f"Player {player_id} rings after placement: {self.players[player_id].rings}")
        if len(self.players[1].rings) == 5 and len(self.players[2].rings) == 5:
            self.game_phase = "playing"
        return True

    def move_ring(self, player_id, start_pos, end_pos):
        print(f"Current game phase: {self.game_phase}")
        print(f"Current player: {self.current_player}")
        print(f"Player {player_id} rings: {self.players[player_id].rings}")
        if self.game_phase != "playing":
            print("Move failed: game phase is not 'playing'")
            return False
        if player_id != self.current_player:
            print(f"Move failed: not player {player_id}'s turn")
            return False
        if start_pos not in self.players[player_id].rings:
            print(f"Move failed: start position {start_pos} not in player {player_id}'s rings")
            return False
        if end_pos in self.players[1].rings or end_pos in self.players[2].rings:
            print(f"Move failed: end position {end_pos} occupied by a ring")
            return False

        # Update player's rings
        self.players[player_id].remove_ring(start_pos)
        self.players[player_id].add_ring(end_pos)
        self.players[player_id].add_marker(start_pos)
        
        # Update board grid:
        self.board.remove_piece(start_pos)
        self.board.place_piece(end_pos, player_id)
        
        self.flip_markers(start_pos, end_pos)
        # Check winner after move.
        winner = self.check_winner()
        if winner is not None:
            print(f"Game over! Player {winner} wins.")
            return True
        
        self.switch_turns()
        print(f"Move successful: {start_pos} -> {end_pos}")
        return True

    def flip_markers(self, start, end, dry_run=False):
        def axial_line(a, b):
            """Returns all axial coordinates between a and b (inclusive)."""
            n = max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[0] + a[1] - b[0] - b[1]))
            path = []
            for i in range(n + 1):
                t = i / max(n, 1)
                q = a[0] * (1 - t) + b[0] * t
                r = a[1] * (1 - t) + b[1] * t
                path.append((round(q), round(r)))
            return path

        start_axial = offset_to_axial(*start)
        end_axial = offset_to_axial(*end)
        path_axial = axial_line(start_axial, end_axial)
        
        flipped = []
        for axial in path_axial[1:]:  # Skip start position
            pos = axial_to_offset(*axial)
            if pos == start:
                continue
            # Check markers
            if pos in self.players[1].markers:
                flipped.append(pos)
                if not dry_run:
                    self.players[1].remove_marker(pos)
                    self.players[2].add_marker(pos)
            elif pos in self.players[2].markers:
                flipped.append(pos)
                if not dry_run:
                    self.players[2].remove_marker(pos)
                    self.players[1].add_marker(pos)
        return flipped

    def check_potential_win(self, player_id, position):
        opponent_id = 3 - player_id
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for x in range(len(self.board.grid)):
            for y in range(len(self.board.grid[x])):
                while self.board.is_valid_position((x, y)) and (self.board.get_piece((x, y)) == opponent_id or (x, y) == position):
                    x += 1
        return False

    def check_immediate_loss(self, player_id, position):
        opponent_id = 3 - player_id
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        return False

    def check_winner(self):
        directions = [
            # Horizontal (East/West)
            (0, 1), (0, -1),
            # Vertical (adjusted for odd-r offset)
            (1, 0), (-1, 0),
            # Diagonals (SE/NW and NE/SW)
            (1, 1), (-1, -1),
            (1, -1), (-1, 1)
        ]

        for player_id in [1, 2]:
            markers = set(self.players[player_id].markers)
            processed = set()
            sequences = []

            for (row, col) in markers:
                if (row, col) in processed:
                    continue
                    
                for d_row, d_col in directions:
                    sequence = []
                    for step in range(5):
                        current_row = row + d_row * step
                        current_col = col + d_col * step
                        # Adjust column for odd-r vertical moves
                        if d_row != 0 and current_row % 2 == 1 and d_col == 0:
                            current_col += (current_row - row) // 2
                        
                        if (current_row, current_col) not in markers:
                            break
                        sequence.append((current_row, current_col))
                    
                    if len(sequence) >= 5:
                        sequences.append(sequence)
                        processed.update(sequence)
                        break  # Only count each marker once

            # Handle first valid sequence only per turn
            if sequences:
                self.handle_sequence(player_id, sequences[0])
                if len(self.scored_rings[player_id]) >= 3:
                    return player_id

        return None

    def handle_sequence(self, player_id, sequence):
        # Remove only the markers in the sequence
        for pos in sequence:
            if pos in self.players[player_id].markers:
                self.players[player_id].remove_marker(pos)
        
        # Remove one ring only if available
        if self.players[player_id].rings:
            removed_ring = self.players[player_id].rings.pop()
            self.scored_rings[player_id].append(removed_ring)
            self.board.remove_piece(removed_ring)
            print(f"Player {player_id} scored 1 ring. Total scored: {len(self.scored_rings[player_id])}")
       
        # Check if the player has won
        if len(self.scored_rings[player_id]) >= 3:
            print(f"Player {player_id} WINS!")
