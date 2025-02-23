import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000';

export const startGame = () => axios.post(`${API_URL}/start-game`);
export const getGameState = () => axios.get(`${API_URL}/game-state`);
export const makeMove = (playerId, start, end) => axios.post(`${API_URL}/make-move`, {
    player_id: playerId,
    start,
    end
});
export const aiMove = (playerId) => axios.post(`${API_URL}/ai-move`, { player_id: playerId });
export const placeRing = (playerId, position) => axios.post(`${API_URL}/place-ring`, {
    player_id: playerId,
    position
});
export const aiPlaceRing = (playerId) => axios.post(`${API_URL}/ai-place-ring`, { player_id: playerId });
