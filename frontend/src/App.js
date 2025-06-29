import React, { useEffect, useState } from 'react';
import DynamicRenderer from './DynamicRenderer';
import StatusPanel from './StatusPanel';
import SettingsPanel from './SettingsPanel';
import ErrorDrawer from './ErrorDrawer';

export default function App() {
  const [spec, setSpec] = useState(null);
  const [status, setStatus] = useState({ backend: false, scanner: false });
  const [errors, setErrors] = useState({ backend: '', scanner: '' });
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    fetch('/api/ui-spec').then(r => r.json()).then(setSpec).catch(() => {});
  }, []);

  const checkStatus = () => {
    fetch('/api/healthz')
      .then(r => r.json())
      .then(() => {
        setStatus(s => ({ ...s, backend: true }));
        setErrors(e => ({ ...e, backend: '' }));
      })
      .catch(err => {
        setStatus(s => ({ ...s, backend: false }));
        setErrors(e => ({ ...e, backend: err.message }));
      });
    fetch('http://127.0.0.1:5001/healthz')
      .then(r => r.json())
      .then(() => {
        setStatus(s => ({ ...s, scanner: true }));
        setErrors(e => ({ ...e, scanner: '' }));
      })
      .catch(err => {
        setStatus(s => ({ ...s, scanner: false }));
        setErrors(e => ({ ...e, scanner: err.message }));
      });
  };

  useEffect(() => {
    checkStatus();
    const id = setInterval(checkStatus, 5000);
    return () => clearInterval(id);
  }, []);

  // theme: system preference
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const apply = () => {
      document.body.dataset.theme = mq.matches ? 'dark' : 'light';
    };
    apply();
    mq.addEventListener('change', apply);
    return () => mq.removeEventListener('change', apply);
  }, []);

  if (!spec) return <div>Waiting for backend/services...</div>;
  return (
    <div>
      <StatusPanel status={status} onRefresh={checkStatus} />
      <button onClick={() => setShowSettings(true)}>Settings</button>
      <SettingsPanel visible={showSettings} onClose={() => setShowSettings(false)} />
      <ErrorDrawer errors={errors} />
      <DynamicRenderer spec={spec} />
    </div>
  );
}
