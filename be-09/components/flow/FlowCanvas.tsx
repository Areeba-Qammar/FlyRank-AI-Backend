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

async function pollRunStatus(eventId: string): Promise<any> {
  for (let i = 0; i < 150; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    const res = await fetch(`/api/run-status/${eventId}`);
    const data = await res.json();
    if (data.status === "Completed" || data.status === "Failed") {
      return data;
    }
  }
  return { status: "timeout" };
}

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
    isRunning,
    executionLogs,
    setRunning,
    setExecutionLogs,
  } = useFlowStore();
    const exportFlow = () => {
    const data = JSON.stringify({ nodes, edges }, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "flow.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  const importFlow = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(reader.result as string);
        const restoredNodes = parsed.nodes.map((n: any) => ({
          ...n,
          data: { ...n.data, onPromptChange: useFlowStore.getState().updateNodePrompt },
        }));
        useFlowStore.setState({ nodes: restoredNodes, edges: parsed.edges });
      } catch {
        alert("Invalid flow file.");
      }
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  useEffect(() => {
    loadFromLocalStorage();
  }, []);

  useEffect(() => {
    saveToLocalStorage();
  }, [nodes, edges]);

  const visitedNodeIds = new Set(executionLogs.map((l) => l.nodeId));

  const styledNodes = nodes.map((n) => ({
    ...n,
    style: visitedNodeIds.has(n.id)
      ? { boxShadow: "0 0 0 3px #4ade80" }
      : undefined,
  }));

  const runFlow = async () => {
    if (nodes.length === 0) return;
    setRunning(true);
    setExecutionLogs([]);

    const res = await fetch("/api/run-flow", {
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

    const { eventId } = await res.json();
    const result = await pollRunStatus(eventId);

    if (result.output?.history) {
      setExecutionLogs(result.output.history);
    }
    setRunning(false);
  };

  return (
    <div className="w-full h-screen bg-slate-950 flex">
      <div className="relative flex-1">
                <div className="absolute z-10 top-4 left-4 flex gap-2">
          <button
            onClick={addNode}
            className="bg-white text-black px-4 py-2 rounded-md text-sm font-medium shadow"
          >
            + Add Decision Node
          </button>
          <button
            onClick={runFlow}
            disabled={isRunning}
            className="bg-green-500 disabled:bg-green-900 disabled:text-green-500 text-black px-4 py-2 rounded-md text-sm font-medium shadow"
          >
            {isRunning ? "Running..." : "▶ Run Flow"}
          </button>
          <button
            onClick={exportFlow}
            className="bg-blue-500 text-white px-4 py-2 rounded-md text-sm font-medium shadow"
          >
            ⬇ Export
          </button>
          <label className="bg-slate-700 text-white px-4 py-2 rounded-md text-sm font-medium shadow cursor-pointer">
            ⬆ Import
            <input type="file" accept=".json" onChange={importFlow} className="hidden" />
          </label>
        </div>
        <ReactFlow
          nodes={styledNodes}
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

      <div className="w-80 bg-slate-900 border-l border-slate-700 p-4 overflow-y-auto text-white">
        <h2 className="text-sm font-semibold text-slate-400 mb-3">
          Execution Log
        </h2>
        {executionLogs.length === 0 && (
          <p className="text-xs text-slate-500">
            No run yet. Click "Run Flow" to execute.
          </p>
        )}
        {executionLogs.map((log, i) => (
          <div
            key={i}
            className="mb-3 p-2 rounded bg-slate-800 border border-slate-700"
          >
            <div className="text-xs text-slate-400 mb-1">Step {i + 1}</div>
            <div className="text-sm mb-1">{log.prompt}</div>
            <div
              className={`text-xs font-bold ${
                log.answer === "YES" ? "text-green-400" : "text-red-400"
              }`}
            >
              → {log.answer}
            </div>
          </div>
        ))}
      </div>
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