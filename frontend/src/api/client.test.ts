import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { api } from "./client";
import type { Champion, DivisionRankings } from "./types";

// Helper to build a fake fetch Response
function mockResponse(body: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    statusText: ok ? "OK" : "Error",
    json: async () => body,
  } as Response;
}

describe("api client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("getChampions calls the correct URL and returns parsed data", async () => {
    const fakeChampions: Champion[] = [
      {
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
        won_against: null,
        event: null,
        defences: 0,
      },
    ];

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      mockResponse(fakeChampions)
    );

    const result = await api.getChampions();

    expect(fetch).toHaveBeenCalledTimes(1);
    const [url] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toMatch(/\/champions$/);
    expect(result).toEqual(fakeChampions);
  });

  it("getRankings includes gender and level as query params", async () => {
    const fakeRankings: DivisionRankings[] = [];

    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      mockResponse(fakeRankings)
    );

    await api.getRankings("M", "Amateur");

    const [url] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toContain("gender=M");
    expect(url).toContain("level=Amateur");
  });

  it("throws a descriptive error when the response is not ok", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      mockResponse(null, false, 404)
    );

    await expect(api.getChampions()).rejects.toThrow(/404/);
  });

  it("getNews calls /news with no query params", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockResponse([]));

    await api.getNews();

    const [url] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toMatch(/\/news$/);
  });
});
