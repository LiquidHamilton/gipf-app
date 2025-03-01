import React from 'react';
import PropTypes from 'prop-types';
import '../styles/Ring.css';

const Ring = ({ player, position, onRingClick }) => {
  return (
    <div
      className={`ring player-${player}`}
      data-pos={`${position[0]}-${position[1]}`}
      onClick={(e) => onRingClick(e, position)}
    >
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
