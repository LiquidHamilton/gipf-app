from models.player import Player
from models.board import Board

class Game:
    def __init__(self, board_size):
        self.board = Board(board_size)
        self.players = {1: Player(1), 2: Player(2)}
        self.current_player = 1
        self.game_phase = "placing"
        self.game_over = False

    def switch_turns(self):
        """Switches the current player's turn"""
        self.current_player = 3 - self.current_player

    def check_game_over(self):
        """Checks if the game is over"""
        #Implement game-specific logic
        pass

    def get_game_state(self):
        """Returns the current game state"""
        return {
            "board": self.board.get_board_state(),
            "players": {
                player_id: { 
                    "rings": player.get_rings(),
                    "markers": player.get_markers()
                }
                for player_id, player in self.players.items()
            },
            "current_player": self.current_player,
            "game_phase": self.game_phase,
            "game_over": self.game_over
        }