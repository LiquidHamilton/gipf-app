from models.AI import AI
import random

class YinshAI(AI):
    def __init__(self, player_id):
        super().__init__(player_id)
    
    def get_possible_moves(self, game):
        """Generates all possible moves for the AI player following movement rules."""
        possible_moves = []
        allowed_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 1), (0, -1)]
        for ring in game.players[self.player_id].rings:
            for dx, dy in allowed_directions:
                x, y = ring
                markers_encountered = False
                while True:
                    x += dx
                    y += dy
                    # Stop if out of board bounds
                    if not game.board.is_valid_position((x, y)):
                        break
                    # Cannot cross another ring.
                    if (x, y) in game.players[1].rings or (x, y) in game.players[2].rings:
                        break
                    # If cell has a marker, note that and continue looking.
                    if ((x, y) in game.players[1].markers or (x, y) in game.players[2].markers):
                        markers_encountered = True
                        continue
                    # At this point, the cell is empty.
                    if markers_encountered:
                        # Must stop at the first empty cell after a series of markers.
                        possible_moves.append({'start': ring, 'end': (x, y)})
                        break
                    else:
                        # If no markers encountered yet, every empty cell is a candidate.
                        possible_moves.append({'start': ring, 'end': (x, y)})
                        # Continue further to allow possibility of encountering markers later.
        #print(f"AI possible moves: {possible_moves}")
        # Optionally, you can filter out moves that fail validation using your Move class.
        valid_moves = []
        from models.move import Move  # Import here to avoid circular dependencies
        for move in possible_moves:
            candidate = Move(move['start'], move['end'], self.player_id)
            if candidate.is_valid(game):
                valid_moves.append(move)
        return valid_moves
    
    def evaluate_moves(self, game, moves):
        """Evaluates and scores potential moves."""
        scored_moves = []
        for move in moves:
            score = self.evaluate_move(game, move)
            scored_moves.append({'move': move, 'score': score})
        #print(f"AI scored moves: {scored_moves}")
        return scored_moves
    
    def evaluate_move(self, game, move):
        """Evaluates and scores a single move."""
        start, end = move['start'], move['end']
        score = 0
        opponent_id = 3 - self.player_id
        if game.check_potential_win(opponent_id, end):
            score += 100  # Defensive bonus for blocking opponent win
        # Central positioning bonus (if desired)
        central_positions = [(5, 5), (5, 6), (6, 5), (6, 6)]
        if end in central_positions:
            score += 20
        # Bonus for flipping markers
        markers_to_flip = game.flip_markers(start, end, dry_run=True)
        score += len(markers_to_flip) * 10
        if game.check_immediate_loss(self.player_id, end):
            score -= 100
        return score

    def select_best_move(self, scored_moves):
        """Selects the best move based on evaluated scores."""
        if scored_moves:
            best = max(scored_moves, key=lambda x: x['score'])
            print(f"AI selected move: {best}")
            return best['move']
        return None

    def get_possible_positions(self, game):
        """Generates all possible ring placement positions for the AI player."""
        possible_positions = []
        for x in range(11):
            for y in range(11):
                if game.board.is_valid_position((x, y)) and not game.board.get_piece((x, y)):
                    possible_positions.append((x, y))
        return possible_positions

    def select_ring_placement(self, game):
        """Selects a ring placement for the AI during the initial phase."""
        possible_positions = self.get_possible_positions(game)
        central_positions = [(5, 5), (5, 6), (6, 5), (6, 6)]
        central_positions_sorted = sorted(possible_positions, key=lambda pos: pos in central_positions, reverse=True)
        best_position = None
        best_score = float('-inf')
        for pos in central_positions_sorted:
            score = self.evaluate_placement(game, pos)
            if score > best_score:
                best_score = score
                best_position = pos
        if not best_position:
            remaining_positions = [pos for pos in possible_positions if pos not in central_positions]
            weighted_positions = remaining_positions.copy()
            weighted_positions.extend(central_positions_sorted)
            best_position = random.choice(weighted_positions)
        return best_position

    def evaluate_placement(self, game, position):
        """Evaluates the potential of a ring placement position."""
        score = 0
        opponent_id = 3 - self.player_id
        if game.board.get_piece(position) == opponent_id:
            score -= 50  # Penalty for placing near an opponent's ring
        if position in game.players[self.player_id].rings:
            score += 30  # Reward for proximity to own rings
        central_positions = [(5, 5), (5, 6), (6, 5), (6, 6)]
        if position in central_positions:
            score += 20
        return score
