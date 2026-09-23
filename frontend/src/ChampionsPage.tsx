import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { Champion } from "./api/types";
import { ChampionCard } from "./components/ChampionCard";

export function ChampionsPage() {
  const [champions, setChampions] = useState<Champion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getChampions()
      .then(setChampions)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading champions...</p>;
  if (error) return <p>Error loading champions: {error}</p>;

  return (
    <div>
      <h1>Champions</h1>
      <ul className="champion-grid">
        {champions.map((c) => (
          <ChampionCard key={c.title_id} champion={c} />
        ))}
      </ul>
    </div>
  );
}
