import React, { useState, useEffect } from 'react';
import { startGame, getGameState, makeMove, aiMove, placeRing, aiPlaceRing } from '../api';
import Ring from './Ring';
import Marker from './Marker';
import '../styles/Board.css';

const Board = () => {
    const [gameState, setGameState] = useState(null);
    const [selectedRing, setSelectedRing] = useState(null);
    const cellWidth = 120;  // Adjust as needed
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
            await handleMove(selectedRing, position);
            setSelectedRing(null);
        } else if (gameState.game_phase === 'placing') {
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

    const animateAIMove = async (start, end) => {
        // Query the ring element by its data-pos (start position).
        const ringElement = document.querySelector(`.ring[data-pos="${start[0]}-${start[1]}"]`);
        if (ringElement) {
          // Compute the new pixel position for the destination.
          const pos = getIntersectionPosition(end[0], end[1], gameState.board, cellWidth, cellHeight);
          // Update the ring’s style so that the CSS transition animates it.
          ringElement.style.left = `${pos.x}px`;
          ringElement.style.top = `${pos.y}px`;
          
          // Optionally, update its data-pos attribute after the animation completes.
          await new Promise(resolve => setTimeout(resolve, 500)); // Match the 0.5s transition
          
          ringElement.setAttribute('data-pos', `${end[0]}-${end[1]}`);
        }
        
        // Finally, update the game state after the animation completes.
        const newGameState = await getGameState();
        setGameState(newGameState);
      };
      
      

    if (!gameState) return <div>Loading...</div>;

    const maxColumns = Math.max(...gameState.board.map(row => row.length));

    // Conversion function: compute pixel coordinates for an intersection.
    // Each row is centered horizontally and vertically staggered.
    const getIntersectionPosition = (row, col, boardLayout, cellWidth, cellHeight) => {
        const rowLength = boardLayout[row].length;
        const rowOffset = ((maxColumns - rowLength) * cellWidth) / 2;
        const x = rowOffset + col * cellWidth;
        const y = row * cellHeight * 0.75;
        return { x, y };
    };

    // Function to generate SVG lines overlay for board lines.
    const getBoardLines = (boardLayout, cellWidth, cellHeight) => {
        const lines = [];
        const intersectionPoints = [];
      
        // Calculate intersection points from the board layout.
        boardLayout.forEach((row, rowIndex) => {
          row.forEach((_, colIndex) => {
            const pos = getIntersectionPosition(rowIndex, colIndex, boardLayout, cellWidth, cellHeight);
            intersectionPoints.push({ x: pos.x, y: pos.y, row: rowIndex, col: colIndex });
          });
        });
      
        // Tolerance for grouping intersections (in pixels)
        const tol = 10; // You might adjust this value
      
        // Group points by vertical alignment using tolerance on x
        const verticalGroups = {};
        intersectionPoints.forEach(point => {
          // Instead of rounding, find an existing group key where the difference is within tolerance.
          let foundKey = null;
          Object.keys(verticalGroups).forEach(key => {
            if (Math.abs(point.x - key) < tol) {
              foundKey = key;
            }
          });
          if (foundKey !== null) {
            verticalGroups[foundKey].push(point);
          } else {
            verticalGroups[point.x] = [point];
          }
        });
      
        // Draw vertical lines: sort each group by y and connect consecutive points
        Object.values(verticalGroups).forEach(group => {
          group.sort((a, b) => a.y - b.y);
          for (let i = 0; i < group.length - 1; i++) {
            lines.push(
              <line
                key={`vert-${group[i].x}-${group[i].y}-${group[i+1].x}-${group[i+1].y}`}
                x1={group[i].x}
                y1={group[i].y}
                x2={group[i+1].x}
                y2={group[i+1].y}
                stroke="black"
                strokeWidth="2"
              />
            );
          }
        });
      
        // Also add diagonal lines (if still desired) using your previous logic:
        intersectionPoints.forEach(point => {
          intersectionPoints.forEach(neighbor => {
            const dx = Math.abs(neighbor.x - point.x);
            const dy = Math.abs(neighbor.y - point.y);
            // Diagonal connections (using cellWidth/2 and cellHeight*0.75 as before)
            if (dx === cellWidth / 2 && dy === cellHeight * 0.75) {
              lines.push(
                <line
                  key={`diag-${point.x}-${point.y}-${neighbor.x}-${neighbor.y}`}
                  x1={point.x}
                  y1={point.y}
                  x2={neighbor.x}
                  y2={neighbor.y}
                  stroke="black"
                  strokeWidth="2"
                />
              );
            }
          });
        });
      
        return lines;
      };
      

    

    return (
        <div className="board-container">
            <svg className="board-lines" width="100%" height="100%">
                {getBoardLines(gameState.board, cellWidth, cellHeight)}
            </svg>
            <div className="board">
                {gameState.board.map((row, rowIndex) => (
                    <div key={`row-${rowIndex}`} className="board-row" style={{ position: 'relative' }}>
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
                                        left: `${pos.x}px`,
                                        top: `${pos.y}px`,
                                        backgroundColor: "transparent",
                                        border: "none"
                                    }}
                                    onClick={() => handleCellClick([rowIndex, colIndex])}
                                >
                                    {cell && <Ring player={cell} position={[rowIndex, colIndex]} onRingClick={handleRingClick} />}
                                    {markerHere && <Marker player={markerHere.player} />}
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Board;
