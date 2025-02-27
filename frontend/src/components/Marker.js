import React from 'react';
import PropTypes from 'prop-types';
import '../styles/Marker.css';

const Marker = ({ player }) => {
    return <div className={`marker player-${player}`} />;
};

Marker.propTypes = {
    player: PropTypes.number.isRequired,
};

export default Marker;
