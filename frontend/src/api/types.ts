// Types mirrored from backend/app/schemas.py — keep these in sync if the
// Pydantic schemas change.

export interface Gym {
  id: number;
  name: string;
  city: string | null;
}

export interface Record {
  am: [number, number, number]; // [wins, losses, draws]
  pro: [number, number, number];
}

export interface Fighter {
  id: number;
  name: string;
  gender: string; // "M" | "F"
  gym: Gym | null;
  photo_url: string | null;
  record: Record;
}

export interface FighterSubmission {
  id: number;
  submitted_name: string;
  submitted_email: string;
  name: string;
  gender: Gender;
  gym_name: string | null;
  recent_fights: SubmissionFight[];
  am_wins: number;
  am_losses: number;
  am_draws: number;
  pro_wins: number;
  pro_losses: number;
  pro_draws: number;
  status: "pending" | "approved" | "rejected";
  admin_note: string | null;
  reviewed_at: string | null;
  created_at: string;
}

export interface SubmissionFight {
  fight_number: number;
  opponent_name: string;
  result: "Win" | "Loss" | "Draw" | "No contest" | "Decision win" | "Decision loss" | "TKO win" | "TKO loss";
}

export interface WeightClass {
  id: number;
  gender: string; // "M" | "F"
  code: string;
  name: string;
  kg_display: string;
}

export interface Champion {
  title_id: number;
  level: string; // "World" | "Pro" | "Amateur"
  scope: string; // "New Zealand" | "Oceania" | "International" | "World"
  weight_class: WeightClass;
  fighter: Fighter;
  since: string; // ISO date string
  won_against: string | null;
  event: string | null;
  defences: number;
}

export interface RankingEntry {
  rank: number | null;
  fighter: Fighter;
  requirement: string | null;
  flag: string | null;
}

export interface DivisionRankings {
  weight_class: WeightClass;
  level: string; // "World" | "Pro" | "Amateur"
  champion: Champion | null;
  contenders: RankingEntry[];
}

export interface TitleFight {
  id: number;
  fight_date: string; // ISO date string
  weight_class: WeightClass;
  level: string;
  scope: string;
  winner: Fighter;
  opponent: Fighter | null;
  event: string | null;
  is_vacant_win: boolean;
}

export interface Bout {
  id: number;
  scheduled_at: string; // ISO datetime string
  weight_class: WeightClass;
  is_title_fight: boolean;
  fighter_a: Fighter;
  fighter_b: Fighter;
  rounds: number;
  city: string | null;
  status: string; // "scheduled" | "completed" | "cancelled"
}

export interface News {
  id: number;
  published_on: string; // ISO date string
  title: string;
  summary: string | null;
  url: string | null;
  source: string | null;
}

export type Gender = "M" | "F";
export type TitleLevel = "World" | "Pro" | "Amateur";