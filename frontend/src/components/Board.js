import React, { useState, useEffect } from 'react';
import { startGame, getGameState, makeMove, aiMove, placeRing, aiPlaceRing } from '../api';
import Ring from './Ring';
import Marker from './Marker';
import '../styles/Board.css';

const Board = () => {
    const [gameState, setGameState] = useState(null);
    const [selectedRing, setSelectedRing] = useState(null);
    const cellWidth = 100;  // Adjust as needed
    const cellHeight = 40;  // Adjust as needed

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
                makeMove(gameState.current_player, selectedRing, position)
                    .then((updatedState) => {
                        console.log("Move made, updated state:", updatedState);
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
        console.log("handleMove called with:", gameState.current_player, start, end);  
        try {
            await makeMove(gameState.current_player, start, end);
            const newGameState = await getGameState();
            setGameState(newGameState);
        } catch (error) {
            console.error("Error making move:", error);
        }
    };

    const handleAiMove = async () => {
        try {
            await aiMove(gameState.current_player);
            const newGameState = await getGameState();
            setGameState(newGameState);
        } catch (error) {
            console.error("Error during AI move:", error);
        }
    };

    if (!gameState) return <div>Loading...</div>;

    const maxColumns = Math.max(...gameState.board.map(row => row.length));

    // Conversion function: compute pixel coordinates for an intersection.
    // Each row is centered horizontally (using rowOffset), and vertically staggered.
    const getIntersectionPosition = (row, col, boardLayout, cellWidth, cellHeight) => {
        const rowLength = boardLayout[row].length;
        const rowOffset = ((maxColumns - rowLength) * cellWidth) / 2;
        const x = rowOffset + col * cellWidth;
        const y = row * cellHeight * 0.75;
        return { x, y };
    };

    return (
        <div className="board-container">
            <div className="board">
                {gameState.board.map((row, rowIndex) => {
                    return (
                        <div
                            key={`row-${rowIndex}`}
                            className="board-row"
                            style={{ position: 'relative' }}
                        >
                            {row.map((cell, colIndex) => {
                                const pos = getIntersectionPosition(rowIndex, colIndex, gameState.board, cellWidth, cellHeight);
                                const markerHere = gameState.markers && gameState.markers.find(
                                    marker => marker.position[0] === rowIndex && marker.position[1] === colIndex
                                );
                                return (
                                    <div
                                        className="cell"
                                        key={`${rowIndex}-${colIndex}`}
                                        style={{
                                            width: `${cellWidth}px`,
                                            height: `${cellHeight}px`,
                                            left: `${pos.x}px`,
                                            top: `${pos.y}px`
                                        }}
                                        onClick={() => handleCellClick([rowIndex, colIndex])}
                                    >
                                        {cell && <Ring player={cell} position={[rowIndex, colIndex]} onRingClick={handleRingClick} />}
                                        {markerHere && <Marker player={markerHere.player} />}
                                    </div>
                                );
                            })}
                        </div>
                    );
                })}
            </div>
            {/* Optionally, add an SVG overlay here to draw board lines */}
        </div>
    );
};

export default Board;
