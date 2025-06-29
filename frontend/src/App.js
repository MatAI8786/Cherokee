import React, { useEffect, useState } from 'react';
import DynamicRenderer from './DynamicRenderer';

export default function App() {
  const [spec, setSpec] = useState(null);

  useEffect(() => {
    fetch('/api/ui-spec').then(r => r.json()).then(setSpec);
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

  if (!spec) return null;
  return <DynamicRenderer spec={spec} />;
}
