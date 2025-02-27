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
            if (!selectedRing) {
                setSelectedRing(position);
            } else {
                // Pass current_player from gameState and use the proper state setter
                makeMove(gameState.current_player, selectedRing, position)
                    .then((updatedState) => {
                        console.log("Move made, updated state:", updatedState);
                        // Fix: Set the game state directly
                        setGameState(updatedState);
                        setSelectedRing(null);
                    })
                    .catch((error) => console.error("Move failed:", error));
            }
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
        setGameState({...updatedState});
        console.log("After placing ring - Game State:", updatedState);
        if (updatedState.game_phase === 'placing') {
            await aiPlaceRing(3 - gameState.current_player);
            const aiUpdatedState = await getGameState();
            setGameState({...aiUpdatedState});
            console.log("After AI placing ring - Game State:", aiUpdatedState);
        }
    };

    const handleMove = async (start, end) => { 
        console.log("handleMove called with:", gameState.current_player, start, end);  
        try {
            await makeMove(gameState.current_player, start, end); // Send move to backend
            const newGameState = await getGameState(); // Fetch updated game state
            setGameState(newGameState); // Update React state
        } catch (error) {
            console.error("Error making move:", error);
        }
    };
    

    const handleAiMove = async () => {
        try {
            await aiMove(gameState.current_player); // Trigger AI move
            const newGameState = await getGameState(); // Fetch updated game state
            setGameState(newGameState); // Update React state
        } catch (error) {
            console.error("Error during AI move:", error);
        }
    };

    if (!gameState) return <div>Loading...</div>;

    return (
        <div className="board">
            {gameState.board.map((row, rowIndex) => (
                row.map((cell, colIndex) => {
                    // Look up a marker for this cell using the new structure
                    const markerHere = gameState.markers && gameState.markers.find(
                        marker => marker.position[0] === rowIndex && marker.position[1] === colIndex
                    );
                    return (
                        <div
                            className="cell"
                            key={`${rowIndex}-${colIndex}`}
                            onClick={() => handleCellClick([rowIndex, colIndex])}
                        >
                            {cell && <Ring player={cell} position={[rowIndex, colIndex]} onRingClick={handleRingClick} />}
                            {/* Render the Marker component only if a marker is found, passing the correct player for color */}
                            {markerHere && <Marker player={markerHere.player} />}
                        </div>
                    );
                })
            ))}
        </div>
    );
};


export default Board;
