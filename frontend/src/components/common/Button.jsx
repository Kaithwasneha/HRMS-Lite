import React from 'react';
import './Button.css';

const Button = ({ 
  onClick, 
  children, 
  type = 'primary', 
  disabled = false, 
  loading = false 
}) => {
  return (
    <button
      className={`btn btn-${type}`}
      onClick={onClick}
      disabled={disabled || loading}
      type="button"
    >
      {loading ? (
        <span className="btn-loading">
          <span className="spinner"></span>
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;
