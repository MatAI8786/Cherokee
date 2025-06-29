import React, { useState, useEffect } from 'react';

export default function SettingsPanel({ visible, onClose }) {
  const [config, setConfig] = useState({});

  useEffect(() => {
    if (visible) {
      fetch('/api/config').then(r => r.json()).then(setConfig);
    }
  }, [visible]);

  const handleChange = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const save = () => {
    fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    }).then(r => r.json()).then(setConfig);
  };

  if (!visible) return null;

  return (
    <div className="settings-panel">
      <h3>Connections &amp; Settings</h3>
      {Object.entries(config).map(([k, v]) => (
        <div key={k} className="config-item">
          <label>{k}</label>
          <input value={v} onChange={e => handleChange(k, e.target.value)} />
        </div>
      ))}
      <button onClick={save}>Save</button>
      <button onClick={onClose}>Close</button>
    </div>
  );
}
