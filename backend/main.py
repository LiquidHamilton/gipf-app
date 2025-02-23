from flask import Flask, request, jsonify
from flask_cors import CORS
from models.yinsh import Yinsh

app = Flask(__name__)
CORS(app) # Allow frontend to make requests

game = Yinsh() #Initialize game instance

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the GIPF-Series backend!"})

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
    start = tuple(data.get("start"))
    end = tuple(data.get("end"))

    if game.move_ring(player_id, start, end):
        return jsonify({"message": "Move successful"}), 200
    return jsonify({"error": "Invalid move"}), 400

@app.route('/check-winner', methods=['GET'])
def check_winner():
    """Checks if there is a winner."""
    winner = game.check_winner()
    if winner:
        return jsonify({"winner": winner}), 200
    return jsonify({"message": "No winner yet"}), 200

if __name__ == '__main__':
    app.run(debug=True)
