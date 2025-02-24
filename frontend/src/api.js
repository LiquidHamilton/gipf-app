import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000';

export const startGame = () => axios.post(`${API_URL}/start-game`);
export const getGameState = async () => {
    try {
        const response = await axios.get(`${API_URL}/game-state`);
        return response.data;
    } catch (error) {
        console.error("Error in getGameState API call:", error.response.data);  // Log error details
        throw error;  // Re-throw the error to be handled in the calling function
    }
};
export const makeMove = async (player_id, start, end) => {
    try {
        const response = await axios.post('http://localhost:5000/make-move', {
            player_id,
            start,
            end
        });
        return response.data;
    } catch (error) {
        console.error("Error in makeMove API call:", error.response.data);  // Log error details
        throw error;  // Re-throw the error to be handled in the calling function
    }
};
export const aiMove = (playerId) => axios.post(`${API_URL}/ai-move`, { player_id: playerId });
export const placeRing = (playerId, position) => axios.post(`${API_URL}/place-ring`, {
    player_id: playerId,
    position
});
export const aiPlaceRing = (playerId) => axios.post(`${API_URL}/ai-place-ring`, { player_id: playerId });