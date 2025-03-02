from models.game import Game
from models.move import Move

def offset_to_axial(row, col):
    q = col - (row - (row % 2)) // 2
    return (q, row)

def axial_to_offset(q, r):
    col = q + (r - (r % 2)) // 2
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

    def is_valid_placement(self, row, col):
        # Only allow vertical or diagonal placement
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if self.board.is_valid_position((new_row, new_col)) and self.board.get_piece((new_row, new_col)) is None:
                return True
        return False


    def move_ring(self, player_id, start_pos, end_pos):
        print(f"Move attempt by Player {player_id} from {start_pos} to {end_pos}")
        
        # Early exit if game is already over
        if self.game_over:
            print("Game over - move rejected")
            return False

        # Validate move first
        if not self.is_valid_move(start_pos, end_pos):
            print(f"Invalid move from {start_pos} to {end_pos}")
            return False

        # Remove ring from start
        self.players[player_id].remove_ring(start_pos)
        self.board.grid[start_pos[0]][start_pos[1]] = None
        
        # Place marker at start position
        self.players[player_id].add_marker(start_pos)
        self.board.markers_grid[start_pos[0]][start_pos[1]] = player_id
        
        # Place ring at end position
        self.players[player_id].add_ring(end_pos)
        self.board.grid[end_pos[0]][end_pos[1]] = player_id
        
        # Update board state
        self.board.remove_piece(start_pos)
        self.board.place_piece(end_pos, player_id)
        
        # Flip markers along the path
        self.flip_markers(start_pos, end_pos)
        
        # Check for winner AFTER updating state
        winner = self.check_winner()
        if winner:
            self.game_over = True
            print(f"Player {winner} wins!")
            return True  # Valid move that ended the game

        # Only switch turns if game isn't over
        if not self.game_over:
            self.switch_turns()
            print(f"Turn switched to Player {self.current_player}")

        return True

    def is_valid_move(self, start_pos, end_pos):
        # Convert to axial coordinates
        start_q, start_r = offset_to_axial(*start_pos)
        end_q, end_r = offset_to_axial(*end_pos)
        
        # Check valid axial direction
        dq, dr = end_q - start_q, end_r - start_r
        if not (dq == 0 or dr == 0 or abs(dq) == abs(dr)):
            return False  # Not a straight line in axial

        # Check path for rings
        steps = max(abs(dq), abs(dr))
        dir_q = dq // steps if dq != 0 else 0
        dir_r = dr // steps if dr != 0 else 0

        # Check path for obstacles
        markers_found = False
        for i in range(1, steps + 1):
            current_q = start_q + dir_q * i
            current_r = start_r + dir_r * i
            current_pos = axial_to_offset(current_q, current_r)
            
            # Position validity check
            if not self.board.is_valid_position(current_pos):
                return False
                
            # Ring collision check (markers are allowed)
            if self.board.get_ring(current_pos) is not None:
                return False

            # Track markers
            if self.board.get_marker(current_pos) is not None:
                markers_found = True
            elif markers_found:
                # Must stop after last marker
                return i == steps

        # Final position must be empty
        return self.board.get_ring(end_pos) is None
    
    def get_move_direction(self, start, end):
        """Returns normalized direction vector or None if invalid"""
        d_row = end[0] - start[0]
        d_col = end[1] - start[1]
        
        if d_row == 0 and d_col == 0:
            return None  # No movement
            
        try:
            step_row = d_row // abs(d_row)
            step_col = d_col // abs(d_col) if d_col != 0 else 0
        except ZeroDivisionError:
            return None
            
        # Vertical must have 0 column change in axial terms (odd-r adjusted)
        if step_col == 0:
            return (step_row, 0)
        # Diagonal must have 1:1 ratio
        elif abs(d_row) == abs(d_col):
            return (step_row, step_col)
        
        return None


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
        path = axial_line(start_axial, end_axial)
        
        flipped = []
        for axial in path[1:-1]:
            pos = axial_to_offset(*axial)
            # Check both players' markers and update board state
            if pos in self.players[1].markers:
                if not dry_run:
                    self.players[1].remove_marker(pos)
                    self.board.remove_marker(pos)
                    self.players[2].add_marker(pos)
                    self.board.place_marker(pos, 2)
                flipped.append(pos)
            elif pos in self.players[2].markers:
                if not dry_run:
                    self.players[2].remove_marker(pos)
                    self.board.remove_marker(pos)
                    self.players[1].add_marker(pos)
                    self.board.place_marker(pos, 1)
                flipped.append(pos)
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
        axial_directions = [
            (0, 1), (0, -1), (-1, 1), 
            (1, -1), (1, 1), (-1, -1)
        ]
        processed_sequences = set()

        # Check axial directions (diagonals)
        for player_id in [1, 2]:
            markers = self.players[player_id].markers
            axial_markers = {offset_to_axial(row, col) for (row, col) in markers}
            
            for marker in axial_markers:
                for d in axial_directions:
                    sequence = []
                    for step in range(-4, 5):
                        q = marker[0] + d[0] * step
                        r = marker[1] + d[1] * step
                        candidate = (q, r)
                        if candidate in axial_markers:
                            sequence.append(candidate)
                        else:
                            if len(sequence) >= 5:
                                break
                            sequence = []
                    
                    if len(sequence) >= 5:
                        sorted_seq = tuple(sorted(sequence[-5:]))
                        if sorted_seq not in processed_sequences:
                            processed_sequences.add(sorted_seq)
                            winning_sequence = [axial_to_offset(q, r) for (q, r) in sorted_seq]
                            if self.handle_sequence(player_id, winning_sequence):
                                return player_id

        # Check vertical lines in OFFSET coordinates (same column)
        for player_id in [1, 2]:
            markers = set(self.players[player_id].markers)
            for (row, col) in markers:
                # Check vertical down
                vertical = []
                current_row, current_col = row, col
                while (current_row, current_col) in markers:
                    vertical.append((current_row, current_col))
                    # Adjust column for odd-r offset when moving down
                    if current_row % 2 == 1:  # odd row
                        next_col = current_col
                    else:  # even row
                        next_col = current_col
                    current_row += 1
                    current_col = next_col

                # Check vertical up
                current_row, current_col = row - 1, col
                while (current_row, current_col) in markers:
                    vertical.insert(0, (current_row, current_col))
                    # Adjust column for odd-r offset when moving up
                    if current_row % 2 == 1:  # odd row
                        next_col = current_col
                    else:  # even row
                        next_col = current_col
                    current_row -= 1
                    current_col = next_col

                # Check for 5+ in a row
                if len(vertical) >= 5:
                    for i in range(len(vertical) - 4):
                        subsequence = vertical[i:i+5]
                        axial_subseq = tuple(sorted(offset_to_axial(r, c) for (r, c) in subsequence))
                        if axial_subseq not in processed_sequences:
                            processed_sequences.add(axial_subseq)
                            if self.handle_sequence(player_id, subsequence):
                                return player_id
        return None


    def handle_sequence(self, player_id, sequence):
        print(f"Handling sequence for Player {player_id}: {sequence}")
        
        # Remove only markers from the sequence
        for pos in sequence:
            if pos in self.players[player_id].markers:
                print(f"Removing marker at {pos}")
                self.players[player_id].remove_marker(pos)
                self.board.remove_marker(pos)
        
        # Remove one ring if available
        if len(self.players[player_id].rings) > 0:
            try:
                removed_ring = self.players[player_id].rings.pop()
                self.scored_rings[player_id].append(removed_ring)
                self.board.remove_piece(removed_ring)
                print(f"Player {player_id} scored a ring. Total: {len(self.scored_rings[player_id])}")
            except IndexError:
                print("No rings left to score")
        
        if len(self.scored_rings[player_id]) >= 3:
            self.game_over = True
            print(f"PLAYER {player_id} WINS!")
            return player_id
        return None

