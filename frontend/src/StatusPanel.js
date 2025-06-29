import React from 'react';

export default function StatusPanel({ status, onRefresh }) {
  return (
    <div className="status-panel">
      <div>Backend: <span className={status.backend ? 'ok' : 'fail'}>{status.backend ? 'OK' : 'Down'}</span></div>
      <div>Scanner: <span className={status.scanner ? 'ok' : 'fail'}>{status.scanner ? 'OK' : 'Down'}</span></div>
      {onRefresh && <button onClick={onRefresh}>Refresh</button>}
    </div>
  );
}
