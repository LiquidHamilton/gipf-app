from models.player import Player
from models.board import Board

class Game:
    def __init__(self, board_layout):
        # board_layout should be a list of row lengths
        self.board = Board(board_layout)
        self.players = {1: Player(1), 2: Player(2)}
        self.current_player = 1
        self.game_phase = "placing"
        self.game_over = False

    def switch_turns(self):
        """Switches the current player's turn"""
        self.current_player = 3 - self.current_player

    def check_game_over(self):
        """Checks if the game is over"""
        # Implement game-specific logic if needed.
        pass

    def get_game_state(self):
        # Create a list of marker objects with position and player info.
        markers = (
            [{"position": m, "player": 1} for m in self.players[1].get_markers()] +
            [{"position": m, "player": 2} for m in self.players[2].get_markers()]
        )

        return {
            "board": self.board.get_board_state(),
            "players": {
                player_id: { 
                    "rings": self.players[player_id].get_rings(),
                    "markers": self.players[player_id].get_markers()
                }
                for player_id in self.players
            },
            "markers": markers,  # Top-level markers array
            "current_player": self.current_player,
            "game_phase": self.game_phase,
            "game_over": self.game_over
        }
