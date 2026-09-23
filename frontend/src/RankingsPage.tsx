import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { DivisionRankings, Gender, TitleLevel } from "./api/types";

const GENDERS: Gender[] = ["M", "F"];
const LEVELS: TitleLevel[] = ["World", "Pro", "Amateur"];

export function RankingsPage() {
  const [gender, setGender] = useState<Gender>("M");
  const [level, setLevel] = useState<TitleLevel>("Amateur");
  const [divisions, setDivisions] = useState<DivisionRankings[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .getRankings(gender, level)
      .then(setDivisions)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [gender, level]);

  return (
    <div>
      <h1>Rankings</h1>

      <div>
        <label>
          Gender:{" "}
          <select value={gender} onChange={(e) => setGender(e.target.value as Gender)}>
            {GENDERS.map((g) => (
              <option key={g} value={g}>
                {g === "M" ? "Male" : "Female"}
              </option>
            ))}
          </select>
        </label>{" "}
        <label>
          Level:{" "}
          <select value={level} onChange={(e) => setLevel(e.target.value as TitleLevel)}>
            {LEVELS.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && <p>Loading rankings...</p>}
      {error && <p>Error: {error}</p>}

      {!loading &&
        !error &&
        divisions.map((div) => (
          <section key={div.weight_class.id}>
            <h2>{div.weight_class.name}</h2>

            {div.champion ? (
              <p>
                Champion: <strong>{div.champion.fighter.name}</strong> (
                {div.champion.scope}) — since{" "}
                {new Date(div.champion.since).toLocaleDateString()}
              </p>
            ) : (
              <p>Title vacant</p>
            )}

            <ol>
              {div.contenders.map((c, i) => (
                <li key={c.fighter.id ?? i}>
                  {c.rank != null ? `#${c.rank} ` : ""}
                  {c.fighter.name}
                  {c.requirement && ` — ${c.requirement}`}
                  {c.flag && ` (${c.flag})`}
                </li>
              ))}
            </ol>
          </section>
        ))}

      {!loading && !error && divisions.length === 0 && (
        <p>No weight classes found for this gender/level combination.</p>
      )}
    </div>
  );
}
