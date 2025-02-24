import React, { useState, useEffect } from 'react';
import { startGame, getGameState, makeMove, aiMove, placeRing, aiPlaceRing } from '../api';
import Ring from './Ring';
import Marker from './Marker';
import '../styles/Board.css';

const Board = () => {
    const [gameState, setGameState] = useState(null);
    const [selectedRing, setSelectedRing] = useState(null);

    useEffect(() => {
        const initializeGame = async () => {
            await startGame();
            const initialState = await getGameState();
            setGameState(initialState);
            console.log("Game started:", initialState);
        };
        initializeGame();
    }, []);

    useEffect(() => {
        console.log("Game state updated:", gameState);
    }, [gameState]);

    const handleRingClick = (e, position) => {
        e.stopPropagation();
        console.log("Ring clicked at:", position);
        if (gameState.game_phase === 'playing') {
            console.log("Selected ring for moving:", position);
            setSelectedRing(position);
        }
    };

    const handleCellClick = async (position) => {
        console.log("Cell clicked at:", position);
        if (selectedRing && gameState.game_phase === 'playing') {
            console.log("Move ring from:", selectedRing, "to:", position);
            await handleMove(selectedRing, position);
            setSelectedRing(null);
        } else if (gameState.game_phase === 'placing') {
            console.log("Place ring at:", position);
            await handlePlaceRing(position);
        }
    };

    const handlePlaceRing = async (position) => {
        await placeRing(gameState.current_player, position);
        const updatedState = await getGameState();
        setGameState(updatedState);
        console.log("After placing ring - Game State:", updatedState);
        if (updatedState.game_phase === 'placing') {
            await aiPlaceRing(3 - gameState.current_player);
            const aiUpdatedState = await getGameState();
            setGameState(aiUpdatedState);
            console.log("After AI placing ring - Game State:", aiUpdatedState);
        }
    };

    const handleMove = async (start, end) => {
        const payload = {
            player_id: gameState.current_player,
            start,
            end
        };

        console.log("Sending move request with payload:", payload);

        await makeMove(gameState.current_player, start, end);
        const updatedState = await getGameState();
        console.log("After moving ring - Game State:", updatedState);
        setGameState(updatedState);
    };

    const handleAiMove = async () => {
        await aiMove(gameState.current_player);
        const updatedState = await getGameState();
        setGameState(updatedState);
    };

    if (!gameState) return <div>Loading...</div>;

    return (
        <div className="board">
            {gameState.board.map((row, rowIndex) => (
                row.map((cell, colIndex) => (
                    <div
                        className="cell"
                        key={`${rowIndex}-${colIndex}-${gameState.board[rowIndex][colIndex]}`} // Ensure unique key
                        onClick={() => handleCellClick([rowIndex, colIndex])}
                    >
                        {cell && <Ring player={cell} position={[rowIndex, colIndex]} onRingClick={handleRingClick} />}
                        {gameState.markers && gameState.markers.some(marker => marker[0] === rowIndex && marker[1] === colIndex) && <Marker />}
                    </div>
                ))
            ))}
            <button onClick={handleAiMove}>AI Move</button>
        </div>
    );
};

export default Board;
