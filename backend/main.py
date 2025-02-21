from flask import Flask, jsonify
from flask_cors import CORS
from models.yinsh import Yinsh

app = Flask(__name__)
CORS(app) # Allow frontend to make requests

game = Yinsh() #Initialize game instance

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the GIPF-Series backend!"})

@app.route('/game-state')
def game_state():
    return jsonify(game.get_game_state())

if __name__ == '__main__':
    app.run(debug=True)
