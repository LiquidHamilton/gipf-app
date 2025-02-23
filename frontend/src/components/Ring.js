import React from 'react';
import '../styles/Ring.css';

const Ring = ({ player }) => (
    <div className={`ring player-${player}`}></div>
);

export default Ring;