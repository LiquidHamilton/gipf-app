from models.AI import AI
import random

def offset_to_axial(row, col):
    q = col - (row - (row & 1)) // 2
    return (q, row)

def axial_to_offset(q, r):
    col = q + (r - (r & 1)) // 2
    return (r, col)

def axial_direction(direction):
    dq, dr = direction
    if dq != 0:
        dq = dq // abs(dq)
    if dr != 0:
        dr = dr // abs(dr)
    return (dq, dr)

class YinshAI(AI):
    def __init__(self, player_id):
        super().__init__(player_id)
        self.allowed_directions = [  # Precomputed directions
            (-1, 0), (1, 0), (-1, -1),
            (-1, 1), (1, -1), (1, 1)
        ]     
    
    def get_possible_moves(self, game):
        valid_moves = []
        for ring in game.players[self.player_id].rings:
            rx, ry = ring  # Cache start position
            for dx, dy in self.allowed_directions:
                x, y = rx, ry
                markers_passed = []
                while True:
                    x += dx
                    y += dy
                    if not game.board.is_valid_position((x, y)):
                        break
                    if game.board.get_piece((x, y)) is not None:
                        break
                    if (x, y) in game.players[1].markers + game.players[2].markers:
                        markers_passed.append((x, y))
                        continue
                    if markers_passed:
                        valid_moves.append({'start': ring, 'end': (x, y)})
                        break
                    else:
                        valid_moves.append({'start': ring, 'end': (x, y)})
        return valid_moves
    
    def evaluate_moves(self, game, moves):
        scored_moves = []
        for move in moves:
            score = self.evaluate_move(game, move)
            scored_moves.append({'move': move, 'score': score})
        return scored_moves
    
    def evaluate_move(self, game, move):
        start, end = move['start'], move['end']
        score = 0
        opponent_id = 3 - self.player_id
        start_axial = offset_to_axial(*start)
        end_axial = offset_to_axial(*end)
        direction = (end_axial[0] - start_axial[0], end_axial[1] - start_axial[1])
        # If vertical in axial terms (no change in q)
        if direction[0] == 0 and direction[1] != 0:
            score += 15
        if game.check_potential_win(opponent_id, end):
            score += 100
        central_positions = [(6, 2), (6, 3), (7, 2), (7, 3)]
        if end in central_positions:
            score += 20
        markers_to_flip = game.flip_markers(start, end, dry_run=True)
        score += len(markers_to_flip) * 10
        if game.check_immediate_loss(self.player_id, end):
            score -= 100
        return score

    def select_best_move(self, scored_moves):
        if scored_moves:
            best = max(scored_moves, key=lambda x: x['score'])
            print(f"AI selected move: {best}")
            return best['move']
        return None

    def get_possible_positions(self, game):
        possible_positions = []
        for row_index, row in enumerate(game.board.get_board_state()):
            for col_index in range(len(row)):
                if game.board.is_valid_position((row_index, col_index)) and not game.board.get_piece((row_index, col_index)):
                    possible_positions.append((row_index, col_index))
        return possible_positions

    def select_ring_placement(self, game):
        possible_positions = self.get_possible_positions(game)
        central_positions = [(6, 2), (6, 3), (7, 2), (7, 3)]
        best_position = None
        best_score = float('-inf')
        for pos in possible_positions:
            score = self.evaluate_placement(game, pos)
            score += random.random() * 20 - 10
            if pos in central_positions:
                score += 10
            if score > best_score:
                best_score = score
                best_position = pos
        if best_position is None:
            best_position = random.choice(possible_positions)
        return best_position

    def evaluate_placement(self, game, position):
        score = 0
        opponent_id = 3 - self.player_id
        if game.board.get_piece(position) == opponent_id:
            score -= 50
        if position in game.players[self.player_id].rings:
            score += 30
        central_positions = [(6,2), (6,3), (7,2), (7,3)]
        if position in central_positions:
            score += 20
        return score
