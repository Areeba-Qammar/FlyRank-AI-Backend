"use client";

import { Handle, Position, NodeProps } from "reactflow";
import { useState } from "react";

export type DecisionNodeData = {
  prompt: string;
  onPromptChange: (id: string, prompt: string) => void;
};

export default function DecisionNode({ id, data }: NodeProps<DecisionNodeData>) {
  const [value, setValue] = useState(data.prompt);

  return (
    <div className="rounded-lg border-2 border-slate-600 bg-slate-900 text-white shadow-md w-64">
      <Handle type="target" position={Position.Top} />

      <div className="px-3 py-2 border-b border-slate-700 text-xs font-semibold text-slate-400">
        Decision Node
      </div>

      <div className="p-3">
        <textarea
          className="w-full bg-slate-800 rounded p-2 text-sm resize-none outline-none focus:ring-1 focus:ring-slate-500"
          rows={3}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={() => data.onPromptChange(id, value)}
          placeholder="Ask a yes/no question..."
        />
      </div>

      <div className="flex justify-between px-3 pb-2 text-xs">
        <span className="text-green-400">YES →</span>
        <span className="text-red-400">NO →</span>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        id="yes"
        style={{ left: "30%", background: "#4ade80" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="no"
        style={{ left: "70%", background: "#f87171" }}
      />
    </div>
  );
}