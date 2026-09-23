import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { Champion } from "./api/types";

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
      <ul>
        {champions.map((c) => (
          <li key={c.title_id}>
            <strong>{c.weight_class.name}</strong> ({c.level}, {c.scope}) —{" "}
            {c.fighter.name}
            {c.won_against && ` (won against ${c.won_against})`}
            {c.event && ` at ${c.event}`}
            {" — since "}
            {new Date(c.since).toLocaleDateString()}
          </li>
        ))}
      </ul>
    </div>
  );
}
