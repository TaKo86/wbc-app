import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ChampionsPage } from "./ChampionsPage";
import { api } from "./api/client";
import type { Champion } from "./api/types";

vi.mock("./api/client", () => ({
  api: {
    getChampions: vi.fn(),
  },
}));

const fakeChampion: Champion = {
  title_id: 1,
  level: "Amateur",
  scope: "New Zealand",
  weight_class: {
    id: 1,
    gender: "M",
    code: "LW",
    name: "Lightweight",
    kg_display: "61.25kg",
  },
  fighter: {
    id: 1,
    name: "Test Fighter",
    gender: "M",
    gym: null,
    photo_url: null,
    record: { am: [5, 1, 0], pro: [0, 0, 0] },
  },
  since: "2026-01-01",
  won_against: "Some Opponent",
  event: "Test Event",
  defences: 2,
};

describe("ChampionsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a loading state initially", () => {
    (api.getChampions as ReturnType<typeof vi.fn>).mockReturnValue(
      new Promise(() => {}) // never resolves — stays in loading
    );

    render(<ChampionsPage />);

    expect(screen.getByText(/loading champions/i)).toBeInTheDocument();
  });

  it("shows champion data once loaded", async () => {
    (api.getChampions as ReturnType<typeof vi.fn>).mockResolvedValue([
      fakeChampion,
    ]);

    render(<ChampionsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Test Fighter/)).toBeInTheDocument();
    });

    expect(screen.getByText(/Lightweight/)).toBeInTheDocument();
    expect(screen.getByText(/won against Some Opponent/)).toBeInTheDocument();
    expect(screen.getByText(/Test Event/)).toBeInTheDocument();
  });

  it("shows an error message if the API call fails", async () => {
    (api.getChampions as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("API error 500: Internal Server Error")
    );

    render(<ChampionsPage />);

    await waitFor(() => {
      expect(screen.getByText(/error loading champions/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/500/)).toBeInTheDocument();
  });

  it("renders nothing extra when the champions list is empty", async () => {
    (api.getChampions as ReturnType<typeof vi.fn>).mockResolvedValue([]);

    render(<ChampionsPage />);

    await waitFor(() => {
      expect(screen.queryByText(/loading champions/i)).not.toBeInTheDocument();
    });

    expect(screen.getByText(/champions/i)).toBeInTheDocument(); // the <h1>
    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
  });
});
