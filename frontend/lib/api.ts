import { AnalyzeRequest, AnalyzeResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export async function analyzeProperty(
  request: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    throw new Error(`분석 요청 실패: ${res.status}`);
  }

  return res.json();
}
