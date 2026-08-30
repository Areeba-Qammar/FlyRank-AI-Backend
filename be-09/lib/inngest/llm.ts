import OpenAI from "openai";

const client = new OpenAI({
  baseURL: process.env.LLM_BASE_URL,
  apiKey: process.env.LLM_API_KEY,
  timeout: 30000,
  maxRetries: 0,
});

export async function askYesNo(prompt: string): Promise<"YES" | "NO"> {
  const res = await client.chat.completions.create({
    model: process.env.LLM_MODEL as string,
    temperature: 0,
    messages: [
      {
        role: "system",
        content:
          "You answer only with the single word YES or NO, in capital letters, with no punctuation, no explanation, and nothing else.",
      },
      { role: "user", content: prompt },
    ],
  });
  
  const raw = (res.choices[0].message?.content || "").trim().toUpperCase();
  if (raw.startsWith("YES")) return "YES";
  if (raw.startsWith("NO")) return "NO";
  
  // Model didn't follow instructions exactly — default to NO rather than crash.
  console.warn(`Unexpected model output, defaulting to NO: "${raw}"`);
  return "NO";
}