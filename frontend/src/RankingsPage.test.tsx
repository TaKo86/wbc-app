import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RankingsPage } from "./RankingsPage";
import { api } from "./api/client";
import type { DivisionRankings } from "./api/types";

vi.mock("./api/client", () => ({
  api: {
    getRankings: vi.fn(),
  },
}));

const fakeDivision: DivisionRankings = {
  weight_class: {
    id: 1,
    gender: "M",
    code: "LW",
    name: "Lightweight",
    kg_display: "61.25kg",
  },
  level: "Amateur",
  champion: null,
  contenders: [
    {
      rank: 1,
      fighter: {
        id: 1,
        name: "Contender One",
        gender: "M",
        gym: null,
        photo_url: null,
        record: { am: [3, 0, 0], pro: [0, 0, 0] },
      },
      requirement: null,
      flag: null,
    },
  ],
};

describe("RankingsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a loading state initially", () => {
    (api.getRankings as ReturnType<typeof vi.fn>).mockReturnValue(
      new Promise(() => {})
    );

    render(<RankingsPage />);

    expect(screen.getByText(/loading rankings/i)).toBeInTheDocument();
  });

  it("fetches with default gender/level and shows contenders", async () => {
    (api.getRankings as ReturnType<typeof vi.fn>).mockResolvedValue([
      fakeDivision,
    ]);

    render(<RankingsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Contender One/)).toBeInTheDocument();
    });

    expect(api.getRankings).toHaveBeenCalledWith("M", "Amateur");
    expect(screen.getByText(/title vacant/i)).toBeInTheDocument();
  });

  it("re-fetches when the level selector changes", async () => {
    (api.getRankings as ReturnType<typeof vi.fn>).mockResolvedValue([]);

    render(<RankingsPage />);

    await waitFor(() => {
      expect(api.getRankings).toHaveBeenCalledWith("M", "Amateur");
    });

    const user = userEvent.setup();
    const levelSelect = screen.getByLabelText(/level/i);
    await user.selectOptions(levelSelect, "Pro");

    await waitFor(() => {
      expect(api.getRankings).toHaveBeenCalledWith("M", "Pro");
    });
  });

  it("shows an error message if the API call fails", async () => {
    (api.getRankings as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("API error 422: Unprocessable Entity")
    );

    render(<RankingsPage />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/422/)).toBeInTheDocument();
  });

  it("shows an empty-state message when no divisions are returned", async () => {
    (api.getRankings as ReturnType<typeof vi.fn>).mockResolvedValue([]);

    render(<RankingsPage />);

    await waitFor(() => {
      expect(
        screen.getByText(/no weight classes found/i)
      ).toBeInTheDocument();
    });
  });
});
