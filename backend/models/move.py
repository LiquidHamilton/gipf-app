class Move:
    def __init__(self, start_pos, end_pos, player_id):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.player_id = player_id

    def execute(self, game):
        """Executes the move on the given game instance."""
        if self.is_valid(game):
            player = game.players[self.player_id]
            # Remove ring from start (update player and board)
            player.remove_ring(self.start_pos)
            game.board.remove_piece(self.start_pos)
            # Place ring at end (update player and board)
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
        if not self.is_valid(game):
            return False
        if game.game_phase != "playing":
            return False
        if self.player_id != game.current_player:
            return False
        if game.board.get_piece(self.start_pos) != self.player_id:
            return False
        
        return game.move_ring(self.player_id, self.start_pos, self.end_pos)
