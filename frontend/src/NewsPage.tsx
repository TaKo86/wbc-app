import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { News } from "./api/types";

export function NewsPage() {
  const [news, setNews] = useState<News[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getNews()
      .then(setNews)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading news...</p>;
  if (error) return <p>Error loading news: {error}</p>;
  if (news.length === 0) return <p>No news yet.</p>;

  return (
    <div>
      <h1>News</h1>
      <ul>
        {news.map((n) => (
          <li key={n.id}>
            <strong>
              {n.url ? (
                <a href={n.url} target="_blank" rel="noopener noreferrer">
                  {n.title}
                </a>
              ) : (
                n.title
              )}
            </strong>
            <br />
            {new Date(n.published_on).toLocaleDateString()}
            {n.source && ` — ${n.source}`}
            {n.summary && <p>{n.summary}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
}
