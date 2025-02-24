from flask import Flask, request, jsonify
from flask_cors import CORS
from models.yinsh import Yinsh
from models.yinshAi import YinshAI
from models.board import Board

app = Flask(__name__)
CORS(app) # Allow frontend to make requests

game = Yinsh() #Initialize game instance

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the GIPF-Series backend!"})

@app.route('/initialize_board', methods=['GET'])
def initalize_board():
    board_instance = Board()
    return jsonify(board_instance.board)

@app.route('/start-game', methods=['POST'])
def start_game():
    """Resets and starts a new game."""
    global game
    game = Yinsh()
    return jsonify({"message": "Game started"}), 200

@app.route('/game-state', methods=['GET'])
def get_game_state():
    """Returns the current board state."""
    state = game.get_game_state()
    return jsonify(state), 200

@app.route('/make-move', methods=['POST'])
def make_move():
    """Processes a player's move."""
    data = request.get_json()
    player_id = data.get("player_id")
    position = data.get("position")
    start = data.get("start")
    end = data.get("end")

    if game.game_phase == "placing" and position:
        if game.place_ring(player_id, tuple(position)):
            game.switch_turns()  # Switch turns after placing a ring
            return jsonify({"message": "Ring placed successfully"}), 200
        return jsonify({"error": "Invalid ring placement"}), 400
    elif game.game_phase == "moving" and start and end:
        if game.move_ring(player_id, tuple(start), tuple(end)):
            game.switch_turns()  # Switch turns after making a move
            return jsonify({"message": "Move successful"}), 200
        return jsonify({"error": "Invalid move"}), 400
    return jsonify({"error": "Invalid request"}), 400

@app.route('/check-winner', methods=['GET'])
def check_winner():
    """Checks if there is a winner."""
    winner = game.check_winner()
    if winner:
        return jsonify({"winner": winner}), 200
    return jsonify({"message": "No winner yet"}), 200

@app.route('/ai-move', methods=['POST'])
def ai_move():
    """AI makes a move."""
    data = request.get_json()
    player_id = data.get("player_id")

    ai = YinshAI(player_id)
    move = ai.make_move(game)

    if move and game.move_ring(player_id, move['start'], move['end']):
        game.switch_turns()  # Switch turns after AI makes a move
        return jsonify({"message": "Move successful"}), 200
    
    return jsonify({"error": "AI move failed"}), 400

@app.route('/place-ring', methods=['POST'])
def place_ring():
    """Places a ring for a player."""
    data = request.get_json()
    player_id = data.get("player_id")
    position = tuple(data.get("position"))

    if game.place_ring(player_id, position):
        game.switch_turns()
        return jsonify({"message": "Ring placed successfully"}), 200
    return jsonify({"error": "Invalid ring placement"}), 400

@app.route('/ai-place-ring', methods=['POST'])
def ai_place_ring():
    """AI places a ring during the initial placing phase."""
    data = request.get_json()
    player_id = data.get("player_id")

    ai = YinshAI(player_id)
    position = ai.select_ring_placement(game)

    if position and game.place_ring(player_id, position):
        game.switch_turns()
        return jsonify({
            "message": "Ring placed successfully",
            "position": position
        }), 200
    return jsonify({"error": "AI ring placement failed"}), 400



if __name__ == '__main__':
    app.run(debug=True)
