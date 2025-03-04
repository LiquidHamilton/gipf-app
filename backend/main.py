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
    #print("Current game state:", state)
    return jsonify(state), 200

@app.route('/make-move', methods=['POST'])
def make_move():
    data = request.get_json()
    player_id = data.get("player_id")
    start = tuple(data.get("start"))
    end = tuple(data.get("end"))

    if player_id is None or start is None or end is None:
        return jsonify({"error": "Invalid request"}), 400

    # Process human move
    success = game.move_ring(player_id, start, end)
    if not success:
        return jsonify({"error": "Invalid move"}), 400

    # Get updated state after human move
    current_state = game.get_game_state()

    # Only proceed to AI move if game isn't over
    if current_state.get("game_over"):
        return jsonify(current_state), 200

    # Check if it's AI's turn
    if game.current_player != player_id:  # Human's turn ended, AI should move
        ai = YinshAI(game.current_player)
        ai_move = ai.make_move(game)
        if ai_move:
            ai_success = game.move_ring(game.current_player, ai_move['start'], ai_move['end'])
            if not ai_success:
                print("AI move failed but human move succeeded")
            
    # Always return the latest state
    final_state = game.get_game_state()
    return jsonify(final_state), 200



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
    
    state = game.get_game_state()
    #print("Updated game state after AI move:", state)  # Debug statement
    return jsonify(state), 200
    
@app.route('/place-ring', methods=['POST'])
def place_ring():
    """Places a ring for a player."""
    data = request.get_json()
    player_id = data.get("player_id")
    position = tuple(data.get("position"))

    if game.place_ring(player_id, position):
        current_state = game.get_game_state()
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
