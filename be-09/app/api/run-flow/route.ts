import { NextRequest, NextResponse } from "next/server";
import { inngest } from "@/lib/inngest/client";

export async function POST(req: NextRequest) {
  const { nodes, edges, startNodeId } = await req.json();

  if (!startNodeId) {
    return NextResponse.json({ error: "startNodeId is required" }, { status: 400 });
  }

  await inngest.send({
    name: "flow/run",
    data: { nodes, edges, startNodeId },
  });

  return NextResponse.json({ status: "triggered" });
}