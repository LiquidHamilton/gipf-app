import React, { useState, useEffect } from 'react';
import { startGame, getGameState, makeMove, aiMove, placeRing, aiPlaceRing } from '../api';
import Ring from './Ring';
import Marker from './Marker';
import '../styles/Board.css';
import axios from 'axios';

const Board = () => {
    const [gameState, setGameState] = useState([]);

    useEffect(() => {
        const fetchBoard = async () => {
            try {
                const response = await axios.get('/initialize_board');
                console.log("Board state fetched: ", response.data); // Debugging message
                setGameState(response.data);
            } catch (error) {
                console.error("Error fetching the board state: ", error);
            }
        };

        fetchBoard();
    }, []);

    const renderBoard = () => {
        if (gameState.length === 0) {
            console.log("Game state is empty."); // Debugging message
            return <div>Loading...</div>;
        }

        console.log("Rendering board with state: ", gameState); // Debugging message

        return gameState.map((row, rowIndex) => (
            <div key={rowIndex} className="board-row">
                {row.map((cell, cellIndex) => (
                    <div key={cellIndex} className="board-cell">
                        {cell === 1 && <div className="ring">Ring</div>} {/* Adjust as needed */}
                    </div>
                ))}
            </div>
        ));
    
    };

    const handlePlaceRing = (position) => {
        placeRing(gameState.current_player, position).then(() => {
            getGameState().then(response => {
                setGameState(response.data);
                if (response.data.game_phase === 'placing') {
                    aiPlaceRing(3 - gameState.current_player).then(() => {
                        getGameState().then(response => setGameState(response.data));
                    });
                }
            });
        });
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
            {renderBoard()}
            <button onClick={handleAiMove}>AI Move</button>
        </div>
    );
};

export default Board;
