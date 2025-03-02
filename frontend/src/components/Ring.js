import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import '../styles/Ring.css';

const Ring = ({ player, position, onRingClick, style }) => {
  const ringRef = useRef(null);

  // Optional: update element styles whenever style prop changes.
  useEffect(() => {
    if (ringRef.current && style) {
      Object.assign(ringRef.current.style, style);
    }
  }, [style]);

  return (
    <div
      ref={ringRef}
      className={`ring player-${player}`}
      data-pos={`${position[0]}-${position[1]}`}
      onClick={(e) => onRingClick(e, position)}
      style={style}
    >
      {player}
    </div>
  );
};

Ring.propTypes = {
  player: PropTypes.number.isRequired,
  position: PropTypes.array.isRequired,
  onRingClick: PropTypes.func.isRequired,
  style: PropTypes.object,
};

Ring.defaultProps = {
  style: {},
};

export default Ring;
