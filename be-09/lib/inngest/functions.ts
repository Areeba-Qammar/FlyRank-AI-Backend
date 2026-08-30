import { inngest } from "./client";
import { askYesNo } from "./llm";

type GraphNode = { id: string; prompt: string };
type GraphEdge = { source: string; sourceHandle: "yes" | "no"; target: string };
type RunFlowEvent = {
  data: {
    nodes: GraphNode[];
    edges: GraphEdge[];
    startNodeId: string;
  };
};

export const runDecisionFlow = inngest.createFunction(
  { id: "run-decision-flow", triggers: [{ event: "flow/run" }] },
  async ({ event, step }) => {
    const { nodes, edges, startNodeId } = event.data as RunFlowEvent["data"];
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const history: { nodeId: string; prompt: string; answer: "YES" | "NO" }[] = [];
    
    let currentId: string | undefined = startNodeId;
    let steps = 0;
    const MAX_STEPS = 50; // guard against an accidental cycle in the graph
    
    while (currentId && steps < MAX_STEPS) {
      const node = nodeMap.get(currentId);
      if (!node) break;
      
      const answer = await step.run(`decide-${node.id}`, async () => {
        return askYesNo(node.prompt);
      });
      
      history.push({ nodeId: node.id, prompt: node.prompt, answer });
      
      const nextEdge = edges.find(
        (e) => e.source === currentId && e.sourceHandle === answer.toLowerCase()
      );
      
      currentId = nextEdge?.target;
      steps++;
    }
    return { history, terminatedAt: currentId ?? null, totalSteps: steps };
  }
);