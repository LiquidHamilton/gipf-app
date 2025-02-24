import React, { useState, useEffect } from 'react';
import { startGame, getGameState, makeMove, aiMove, placeRing, aiPlaceRing } from '../api';
import Ring from './Ring';
import Marker from './Marker';
import '../styles/Board.css';

const Board = () => {
    const [gameState, setGameState] = useState(null);

    useEffect(() => {
        startGame().then(() => {
            getGameState().then(response => {
                setGameState(response.data);
            });
        });
    }, []);

    const handlePlaceRing = (position) => {
        placeRing(gameState.current_player, position).then(() => {
            getGameState().then(response => {
                console.log("After Placing Ring - Game State:", response.data);  // Add console log
                setGameState(response.data);
                if (response.data.game_phase === 'placing') {
                    aiPlaceRing(3 - gameState.current_player).then(() => {
                        getGameState().then(response => {
                            console.log("After AI Placing Ring - Game State:", response.data);  // Add console log
                            setGameState(response.data);
                        }).catch(error => console.error("Error getting game state after AI placing ring:", error));  // Add error log
                    }).catch(error => console.error("Error in AI placing ring:", error));  // Add error log
                }
            }).catch(error => console.error("Error getting game state after placing ring:", error));  // Add error log
        }).catch(error => console.error("Error placing ring:", error));  // Add error log
    };

    const handleMove = (start, end) => {
        makeMove(gameState.current_player, start, end).then(() => {
            getGameState().then(response => setGameState(response.data));
        });
    };

    const handleAiMove = () => {
        aiMove(gameState.current_player).then(() => {
            getGameState().then(response => setGameState(response.data));
        });
    };

    if (!gameState) return <div>Loading...</div>;

    return (
        <div className="board">
            {gameState.board.map((row, rowIndex) => (
                row.map((cell, colIndex) => (
                    <div
                        className="cell"
                        key={`${rowIndex}-${colIndex}`}
                        onClick={() => gameState.game_phase === 'placing' ? handlePlaceRing([rowIndex, colIndex]) : null}
                    >
                        {cell && <Ring player={cell} />}
                        {gameState.markers && gameState.markers.some(marker => marker[0] === rowIndex && marker[1] === colIndex) && <Marker />}
                    </div>
                ))
            ))}
            <button onClick={handleAiMove}>AI Move</button>
        </div>
    );
};

export default Board;
