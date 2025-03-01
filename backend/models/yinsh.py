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
        # ... existing validation checks ...

        # Update rings and markers
        self.players[player_id].remove_ring(start_pos)
        self.players[player_id].add_ring(end_pos)
        self.players[player_id].add_marker(start_pos)
        
        # Update board
        self.board.remove_piece(start_pos)
        self.board.place_piece(end_pos, player_id)
        
        # Flip markers
        self.flip_markers(start_pos, end_pos)
        
        # Check for winner
        winner = self.check_winner()
        if winner:
            self.game_over = True
            print(f"Player {winner} wins!")
            return True
        
        # Switch turns only if game is still ongoing
        if not self.game_over:
            self.switch_turns()
            print(f"Turn switched to Player {self.current_player}")
        
        return True

    def is_valid_move(self, start_pos, end_pos):
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Calculate direction components
        d_row = end_row - start_row
        d_col = end_col - start_col
        
        # Disallow horizontal moves (0 row change)
        if d_row == 0:
            return False

        # Calculate direction vector
        try:
            step_row = d_row // abs(d_row)
            step_col = d_col // abs(d_col) if d_col != 0 else 0
        except ZeroDivisionError:
            return False

        # Vertical movement specific validation
        if step_col == 0:  # Pure vertical move
            current_row, current_col = start_row, start_col
            for step in range(1, abs(d_row) + 1):
                current_row = start_row + step * step_row
                
                # Calculate column adjustment for odd-r offset
                if current_row % 2 != start_row % 2:  # Parity changed
                    current_col = start_col + (step_row > 0) * (step % 2)
                else:
                    current_col = start_col
                    
                # Skip check for final position
                if (current_row, current_col) == end_pos:
                    continue
                    
                if not self.board.is_valid_position((current_row, current_col)):
                    return False
                if self.board.get_piece((current_row, current_col)) is not None:
                    return False
            
            # Final position must match calculated end column
            final_col = current_col
            return end_col == final_col

        # Diagonal validation
        elif abs(d_row) == abs(d_col):
            current_row, current_col = start_row, start_col
            for step in range(1, abs(d_row)):
                current_row += step_row
                current_col += step_col
                
                # Adjust for odd-r offset in diagonal moves
                if current_row % 2 != start_row % 2:
                    current_col += step_col * (step % 2)
                
                if not self.board.is_valid_position((current_row, current_col)):
                    return False
                if self.board.get_piece((current_row, current_col)) is not None:
                    return False
            
            return True

        return False
    
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
            
        # Vertical must have 0 column change
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
        """
        Checks if a player has formed a winning sequence of five markers
        along any of the three primary axial directions (which, in an odd-r grid,
        capture vertical and diagonal connections).
        Converts each player's marker positions from offset (row, col) to axial (q, r)
        and then checks for sequences along (1,0), (0,1), and (-1,1).
        """
        # Primary axial directions for a hex grid (each direction covers its opposite)
        axial_directions = [
            (1, 0),    # East-West axis (horizontal in axial, but in odd-r this isn't a legal move, so won't trigger)
            (0, 1),    # Southeast-Northwest axis – corresponds to vertical movement
            (-1, 1)    # Southwest-Northeast axis – diagonal
        ]
        
        for player_id in [1, 2]:
            # Convert markers (offset coordinates) to axial coordinates.
            axialMarkers = { offset_to_axial(row, col) for (row, col) in self.players[player_id].markers }
            
            # For each marker, check along each allowed direction.
            for marker in axialMarkers:
                for d in axial_directions:
                    sequence = []
                    for step in range(5):
                        candidate = (marker[0] + d[0] * step, marker[1] + d[1] * step)
                        if candidate in axialMarkers:
                            sequence.append(candidate)
                        else:
                            break
                    if len(sequence) == 5:
                        # Convert the winning sequence back to offset coordinates.
                        winning_sequence = [axial_to_offset(q, r) for (q, r) in sequence]
                        self.handle_sequence(player_id, winning_sequence)
                        # Only declare a win if three rings have been scored.
                        if len(self.scored_rings[player_id]) >= 3:
                            return player_id
        return None




    def handle_sequence(self, player_id, sequence):
        """
        Given a winning sequence (in offset coordinates), remove those markers
        and remove a single ring from the player's board. A ring is removed only
        if the player has not yet scored the maximum (i.e. 3 rings removed).
        """
        print(f"Handling sequence for Player {player_id}: {sequence}")
        # Remove only the markers that form the winning sequence.
        for pos in sequence:
            if pos in self.players[player_id].markers:
                self.players[player_id].remove_marker(pos)
        
        # Remove one ring if available and if not already over-scored.
        if len(self.players[player_id].rings) > len(self.scored_rings[player_id]):
            removed_ring = self.players[player_id].rings.pop()
            self.scored_rings[player_id].append(removed_ring)
            self.board.remove_piece(removed_ring)
            print(f"Player {player_id} scored 1 ring. Total scored: {len(self.scored_rings[player_id])}")
        
        if len(self.scored_rings[player_id]) >= 3:
            print(f"Player {player_id} WINS!")

