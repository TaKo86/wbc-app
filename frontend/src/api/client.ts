import type {
  Champion,
  DivisionRankings,
  Bout,
  TitleFight,
  News,
  Gender,
  TitleLevel,
  FighterSubmission,
  Fighter,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (body.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // Keep the HTTP status when the response is not JSON.
    }
    throw new Error(`API error ${res.status}: ${detail}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  getChampions: () => request<Champion[]>("/champions"),

  getRankings: (gender: Gender, level: TitleLevel) =>
    request<DivisionRankings[]>(`/rankings?gender=${gender}&level=${level}`),

  getRankingsByTitle: (titleId: number, gender: Gender, level: TitleLevel) =>
    request<DivisionRankings>(
      `/rankings/${titleId}?gender=${gender}&level=${level}`
    ),

  getBouts: () => request<Bout[]>("/bouts"),

  getResults: () => request<TitleFight[]>("/results"),

  getNews: () => request<News[]>("/news"),

  health: () => request<{ status: string }>("/health"),

  createSubmission: (payload: Omit<FighterSubmission, "id" | "status" | "admin_note" | "reviewed_at" | "created_at">) =>
    request<FighterSubmission>("/submissions", { method: "POST", body: JSON.stringify(payload) }),

  getSubmissions: (adminKey: string) =>
    request<FighterSubmission[]>("/submissions", { headers: { "X-Admin-Key": adminKey } }),

  updateSubmission: (id: number, adminKey: string, payload: Partial<FighterSubmission>) =>
    request<FighterSubmission>(`/submissions/${id}`, {
      method: "PATCH",
      headers: { "X-Admin-Key": adminKey },
      body: JSON.stringify(payload),
    }),

  approveSubmission: (id: number, adminKey: string) =>
    request<Fighter>(`/submissions/${id}/approve`, { method: "POST", headers: { "X-Admin-Key": adminKey } }),

  rejectSubmission: (id: number, adminKey: string, admin_note?: string) =>
    request<FighterSubmission>(`/submissions/${id}/reject`, {
      method: "POST",
      headers: { "X-Admin-Key": adminKey },
      body: JSON.stringify({ admin_note }),
    }),

  deleteSubmission: (id: number, adminKey: string) =>
    request<void>(`/submissions/${id}`, { method: "DELETE", headers: { "X-Admin-Key": adminKey } }),
};