import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { TitleFight } from "./api/types";

export function ResultsPage() {
  const [results, setResults] = useState<TitleFight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getResults()
      .then(setResults)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="page-muted">Loading results...</p>;
  if (error) return <p className="page-muted">Error loading results: {error}</p>;
  if (results.length === 0) return <p className="page-muted">No results yet.</p>;

  return (
    <div>
      <h1>Results</h1>
      <ul>
        {results.map((r) => (
          <li key={r.id}>
            <strong>{r.winner.name}</strong>
            {r.opponent && ` def. ${r.opponent.name}`}
            {r.is_vacant_win && " (vacant title win)"}
            <br />
            {r.weight_class.name} — {r.level} ({r.scope})
            <br />
            {new Date(r.fight_date).toLocaleDateString()}
            {r.event && ` — ${r.event}`}
          </li>
        ))}
      </ul>
    </div>
  );
}
