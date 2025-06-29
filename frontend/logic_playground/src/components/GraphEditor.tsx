import React, { useState } from 'react';
import ReactFlow, { MiniMap, Controls, Background, Node } from 'react-flow-renderer';

const initialNodes: Node[] = [];
const initialEdges: any[] = [];

export default function GraphEditor() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <ReactFlow nodes={nodes} edges={edges} onNodesChange={setNodes} onEdgesChange={setEdges}>
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
}
