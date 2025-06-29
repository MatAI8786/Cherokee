import React from 'react';

export default function ErrorDrawer({ errors }) {
  const keys = Object.keys(errors).filter(k => errors[k]);
  if (keys.length === 0) return null;

  return (
    <div className="error-drawer">
      <h4>Errors</h4>
      {keys.map(k => (
        <div key={k} className="error-item">
          <strong>{k}</strong>: {errors[k]}
        </div>
      ))}
    </div>
  );
}
