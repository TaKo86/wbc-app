import type {
  Champion,
  DivisionRankings,
  Bout,
  TitleFight,
  News,
  Gender,
  TitleLevel,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
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
};