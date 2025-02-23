class Move:
    def __init__(self, start_pos, end_pos, player_id):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.player_id = player_id

    def execute(self, game):
        """Executes the move on the given game instance"""
        # Implement move execution logic specific to the game
        if self.is_valid(game):
            player = game.players[self.player_id]
            player.remove_ring(self.start_pos)
            player.add_ring(self.end_pos)
            player.add_marker(self.start_pos)
            game.board.place_piece(self.end_pos, self.player_id)
            game.switch_turns()
            return True
        return False
   
    def is_valid(self, game):
        """Validates the move"""
        if game.game_phase != "playing":
            return False
        if self.player_id != game.current_player:
            return False
        if not game.board.is_valid_position(self.start_pos) or not game.board.is_valid_position(self.end_pos):
            return False
        if game.board.get_piece(self.start_pos) != self.player_id or game.board.get_piece(self.end_pos) is not None:
            return False
        return True