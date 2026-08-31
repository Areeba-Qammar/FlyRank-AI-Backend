import { create } from "zustand";
import {
  Node,
  Edge,
  Connection,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
} from "reactflow";

type ExecutionLog = { nodeId: string; prompt: string; answer: "YES" | "NO" };

type FlowState = {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addNode: () => void;
  updateNodePrompt: (id: string, prompt: string) => void;
  saveToLocalStorage: () => void;
  loadFromLocalStorage: () => void;
  isRunning: boolean;
  executionLogs: ExecutionLog[];
  setRunning: (running: boolean) => void;
  setExecutionLogs: (logs: ExecutionLog[]) => void;
};

let idCounter = 1;

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [],
  edges: [],  isRunning: false,
  executionLogs: [],
  setRunning: (running) => set({ isRunning: running }),
  setExecutionLogs: (logs) => set({ executionLogs: logs }),

  onNodesChange: (changes) => {
    set({ nodes: applyNodeChanges(changes, get().nodes) });
  },

  onEdgesChange: (changes) => {
    set({ edges: applyEdgeChanges(changes, get().edges) });
  },

   onConnect: (connection) => {
    if (!connection.source || !connection.target) return;
    const isYes = connection.sourceHandle === "yes";
    const newEdge: Edge = {
      id: `e-${connection.source}-${connection.sourceHandle}-${connection.target}`,
      source: connection.source,
      target: connection.target,
      sourceHandle: connection.sourceHandle,
      targetHandle: connection.targetHandle,
      label: isYes ? "YES" : "NO",
      style: { stroke: isYes ? "#4ade80" : "#f87171", strokeWidth: 2 },
      animated: false,
    };
    set({ edges: addEdge(newEdge, get().edges) });
  },

  addNode: () => {
    const id = `node-${idCounter++}`;
    const newNode: Node = {
      id,
      type: "decision",
      position: { x: 100 + Math.random() * 300, y: 100 + Math.random() * 300 },
      data: { prompt: "", onPromptChange: get().updateNodePrompt },
    };
    set({ nodes: [...get().nodes, newNode] });
  },

  updateNodePrompt: (id, prompt) => {
    set({
      nodes: get().nodes.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, prompt } } : n
      ),
    });
  },

  saveToLocalStorage: () => {
    const { nodes, edges } = get();
    localStorage.setItem("be09-flow", JSON.stringify({ nodes, edges }));
  },

  loadFromLocalStorage: () => {
    const raw = localStorage.getItem("be09-flow");
    if (!raw) return;
    const { nodes, edges } = JSON.parse(raw);
    const restoredNodes = nodes.map((n: Node) => ({
      ...n,
      data: { ...n.data, onPromptChange: get().updateNodePrompt },
    }));
    set({ nodes: restoredNodes, edges });
  },
}));