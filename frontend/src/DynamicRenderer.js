import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function ComponentFactory({ comp }) {
  switch (comp.type) {
    case 'TextInput':
      return <input placeholder={comp.placeholder} name={comp.bind || comp.id} />;
    case 'PasswordInput':
      return <input type="password" placeholder={comp.placeholder} name={comp.bind || comp.id} />;
    case 'Button':
      return <button>{comp.text}</button>;
    case 'Select':
    case 'Dropdown':
      return <select><option>{comp.placeholder}</option></select>;
    case 'Switch':
      return <label><input type="checkbox" /> {comp.label}</label>;
    case 'DatePicker':
      return <input type="date" />;
    case 'Chart':
      return <div className="chart-placeholder">{comp.id}</div>;
    case 'Table':
      return (
        <table>
          <thead>
            <tr>{comp.columns.map(c => <th key={c}>{c}</th>)}</tr>
          </thead>
          <tbody></tbody>
        </table>
      );
    case 'IconButton':
      return <button>{comp.icon}</button>;
    default:
      return null;
  }
}

function Page({ section }) {
  return (
    <div className="page" id={section.id}>
      {section.components && section.components.map(c => (
        <ComponentFactory key={c.id} comp={c} />
      ))}
    </div>
  );
}

export default function DynamicRenderer({ spec }) {
  const pages = spec.sections.filter(s => s.type === 'page');
  return (
    <Router>
      <nav>
        {pages.map(p => <Link key={p.id} to={`/${p.id}`}>{p.id}</Link>)}
      </nav>
      <Routes>
        {pages.map(p => <Route key={p.id} path={`/${p.id}`} element={<Page section={p} />} />)}
        <Route path="*" element={<div>Home</div>} />
      </Routes>
    </Router>
  );
}
