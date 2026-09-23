import { useState } from "react";
import { ChampionsPage } from "./ChampionsPage";
import { RankingsPage } from "./RankingsPage";
import { BoutsPage } from "./BoutsPage";
import { ResultsPage } from "./ResultsPage";
import { NewsPage } from "./NewsPage";

type Tab = "champions" | "rankings" | "bouts" | "results" | "news";

const TABS: { key: Tab; label: string }[] = [
  { key: "champions", label: "Champions" },
  { key: "rankings", label: "Rankings" },
  { key: "bouts", label: "Bouts" },
  { key: "results", label: "Results" },
  { key: "news", label: "News" },
];

function App() {
  const [tab, setTab] = useState<Tab>("champions");

  return (
    <div>
      <nav>
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            disabled={tab === t.key}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main>
        {tab === "champions" && <ChampionsPage />}
        {tab === "rankings" && <RankingsPage />}
        {tab === "bouts" && <BoutsPage />}
        {tab === "results" && <ResultsPage />}
        {tab === "news" && <NewsPage />}
      </main>
    </div>
  );
}

export default App;
