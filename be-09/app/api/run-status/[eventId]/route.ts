import { NextRequest, NextResponse } from "next/server";
import { getResult } from "@/lib/inngest/results-store";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ eventId: string }> }
) {
  const { eventId } = await params;
  const result = getResult(eventId);

  if (!result) {
    return NextResponse.json({ status: "pending" });
  }

  return NextResponse.json({ status: "Completed", output: result });
}