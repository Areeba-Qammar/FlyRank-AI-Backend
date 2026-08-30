"use client";

import { useEffect } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";
import DecisionNode from "./DecisionNode";
import { useFlowStore } from "@/lib/flow-store";

const nodeTypes = { decision: DecisionNode };

function Canvas() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    saveToLocalStorage,
    loadFromLocalStorage,
  } = useFlowStore();

  useEffect(() => {
    loadFromLocalStorage();
  }, []);

  useEffect(() => {
    saveToLocalStorage();
  }, [nodes, edges]);

  return (
    <div className="w-full h-screen bg-slate-950">
            <div className="absolute z-10 top-4 left-4">
        <button
          onClick={addNode}
          className="bg-white text-black px-4 py-2 rounded-md text-sm font-medium shadow"
        >
          + Add Decision Node
        </button>
        <button
          onClick={async () => {
            if (nodes.length === 0) return;
            await fetch("/api/run-flow", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                nodes: nodes.map((n) => ({ id: n.id, prompt: n.data.prompt })),
                edges: edges.map((e) => ({
                  source: e.source,
                  sourceHandle: e.sourceHandle,
                  target: e.target,
                })),
                startNodeId: nodes[0].id,
              }),
            });
          }}
          className="bg-green-500 text-black px-4 py-2 rounded-md text-sm font-medium shadow ml-2"
        >
          ▶ Run Flow
        </button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

export default function FlowCanvas() {
  return (
    <ReactFlowProvider>
      <Canvas />
    </ReactFlowProvider>
  );
}