import React from 'react';
import PropTypes from 'prop-types';
import '../styles/Ring.css';

const Ring = ({ player, position, onRingClick }) => {
    return (
        <div className={`ring player-${player}`} onClick={(e) => onRingClick(e, position)}>
            {player}
        </div>
    );
};

Ring.propTypes = {
    player: PropTypes.number.isRequired,
    position: PropTypes.array.isRequired,
    onRingClick: PropTypes.func.isRequired,
};

export default Ring;
