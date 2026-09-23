import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { Bout } from "./api/types";

export function BoutsPage() {
  const [bouts, setBouts] = useState<Bout[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getBouts()
      .then(setBouts)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading bouts...</p>;
  if (error) return <p>Error loading bouts: {error}</p>;
  if (bouts.length === 0) return <p>No upcoming bouts scheduled.</p>;

  return (
    <div>
      <h1>Upcoming Bouts</h1>
      <ul>
        {bouts.map((b) => (
          <li key={b.id}>
            <strong>
              {b.fighter_a.name} vs {b.fighter_b.name}
            </strong>{" "}
            — {b.weight_class.name}
            {b.is_title_fight && " (Title Fight)"}
            <br />
            {new Date(b.scheduled_at).toLocaleString()}
            {b.city && ` — ${b.city}`}
            {" — "}
            {b.rounds} rounds — status: {b.status}
          </li>
        ))}
      </ul>
    </div>
  );
}
