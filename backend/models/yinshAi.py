from models.AI import AI

class YinshAI(AI):
    def __init__(self, player_id):
        super().__init__(player_id)
   
    def get_possible_moves(self, game):
        """Generates all possible moves for the AI player"""
        possible_moves = []
        for ring in game.players[self.player_id].rings:
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 1), (0, -1)]:
                x, y = ring
                while True:
                    x += dx
                    y += dy
                    if not game.board.is_valid_position((x, y)):
                        break
                    if (x, y) in game.players[1].rings or (x, y) in game.players[2].rings:
                        break
                    possible_moves.append({
                        'start': ring,
                        'end': (x, y)
                    })
        print(f"AI possible moves: {possible_moves}")  # Debug statement
        return possible_moves
    
    def evaluate_moves(self, game, moves):
        """Evaluates and scores potential moves"""
        scored_moves = []
        for move in moves:
            score = self.evaluate_move(game, move)
            scored_moves.append({
                'move': move,
                'score': score
            })
        print(f"AI scored moves: {scored_moves}")  # Debug statement
        return scored_moves
    
    def evaluate_move(self, game, move):
        """Evaluates and scores a single move"""
        start, end = move['start'], move['end']
        score = 0

        # Defensive Play: Block opponent's potential winning moves
        opponent_id = 3 - self.player_id
        if game.check_potential_win(opponent_id, end):
            score += 100 # High score for blocking a win

        # Strategic Positioning: Prioritize central and strategic areas
        central_positions = [(5, 5), (5, 6), (6, 5), (6, 6)]
        if end in central_positions:
            score += 20 # Higher score for central positions

        # Balanced Aggression: Maximize future opportunities
        markers_to_flip = game.flip_markers(start, end, dry_run=True)
        score += len(markers_to_flip) * 10 # Moderate score for flipping markers

        # Avoiding immediate loss: Ensure the move doesn't lead to an immeidate loss
        if game.check_immediate_loss(self.player_id, end):
            score -= 100 # Lower score for risky moves

        return score

    def select_best_move(self, scored_moves):
        # Select the best move based on the scores
        selected_move = super().select_best_move(scored_moves)
        print(f"AI selected move: {selected_move}")  # Debug statement
        return selected_move

    def get_possible_positions(self, game):
        """Generates all possible ring placement positions for the AI player"""
        possible_positions = []
        for x in range(11):
            for y in range(11):
                if game.board.is_valid_position((x, y)) and not game.board.get_piece((x, y)):
                    possible_positions.append((x, y))
        return possible_positions
    
    def select_ring_placement(self, game):
        """Selects a ring placement for the AI during the initial phase."""
        possible_positions = self.get_possible_positions(game)
        if possible_positions:
            return possible_positions[0] # Update this for better reasoning
        return None