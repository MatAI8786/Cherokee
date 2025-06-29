import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import GraphEditor from './components/GraphEditor';

const client = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={client}>
      <GraphEditor />
    </QueryClientProvider>
  );
}
