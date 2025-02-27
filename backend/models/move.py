class Move:
    def __init__(self, start_pos, end_pos, player_id):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.player_id = player_id

    def execute(self, game):
        """Executes the move on the given game instance"""
        if self.is_valid(game):
            player = game.players[self.player_id]
            # Remove ring from start position (update player and board)
            player.remove_ring(self.start_pos)
            game.board.remove_piece(self.start_pos)
            # Place ring at end position (update player and board)
            player.add_ring(self.end_pos)
            game.board.place_piece(self.end_pos, self.player_id)
            # Drop a marker where the ring started
            player.add_marker(self.start_pos)
            # Flip markers along the path, if applicable
            game.flip_markers(self.start_pos, self.end_pos)
            game.switch_turns()
            return True
        return False

    def is_valid(self, game):
        """Validates the move according to basic conditions and path rules"""
        if game.game_phase != "playing":
            return False
        if self.player_id != game.current_player:
            return False
        # The starting cell must contain the player's ring, and the end cell must be empty.
        if game.board.get_piece(self.start_pos) != self.player_id:
            return False
        if game.board.get_piece(self.end_pos) is not None:
            return False
        # Check that the movement path obeys the game rules.
        if not self.is_valid_path(game):
            return False
        return True

    def is_valid_path(self, game):
        """
        Validates that the move from start_pos to end_pos follows these rules:
          1. The move is in a straight line (allowed directions).
          2. The ring may skip any number of empty spaces initially.
          3. If markers are encountered, the ring must stop on the first empty cell immediately following the last marker.
          4. The ring cannot cross over any other ring.
          5. The ring cannot end on a space that contains a marker or ring.
        """
        sx, sy = self.start_pos
        ex, ey = self.end_pos
        dx = ex - sx
        dy = ey - sy

        # Must move somewhere
        if dx == 0 and dy == 0:
            return False

        # Normalize to get the step (allowed directions: diagonal, horizontal, vertical)
        step_x = (dx // abs(dx)) if dx != 0 else 0
        step_y = (dy // abs(dy)) if dy != 0 else 0
        allowed_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 1), (0, -1)]
        if (step_x, step_y) not in allowed_directions:
            return False

        # Traverse the path from the cell immediately after start_pos
        x, y = sx + step_x, sy + step_y
        markers_encountered = False

        while (x, y) != (ex, ey):
            # If a ring is encountered anywhere along the path, the move is invalid.
            if game.board.get_piece((x, y)) is not None:
                return False

            # Check if this cell contains a marker (from either player)
            cell_has_marker = ((x, y) in game.players[1].markers or (x, y) in game.players[2].markers)
            if cell_has_marker:
                markers_encountered = True
            else:
                # If we've already encountered markers and now hit an empty cell...
                if markers_encountered:
                    # This empty cell must be the final destination.
                    if (x, y) != (ex, ey):
                        return False
                    break
            x += step_x
            y += step_y

        # Final check: the end cell must be empty of both rings and markers.
        if game.board.get_piece(self.end_pos) is not None:
            return False
        if (self.end_pos in game.players[1].markers or self.end_pos in game.players[2].markers):
            return False

        return True
