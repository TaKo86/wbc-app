import { useState } from "react";
import "./App.css";
import { ChampionsPage } from "./ChampionsPage";
import { RankingsPage } from "./RankingsPage";
import { BoutsPage } from "./BoutsPage";
import { ResultsPage } from "./ResultsPage";
import { NewsPage } from "./NewsPage";
import { SubmitFighterPage } from "./SubmitFighterPage";
import { AdminSubmissionsPage } from "./AdminSubmissionsPage";

type Tab = "champions" | "rankings" | "bouts" | "results" | "news" | "submit" | "admin";

const TABS: { key: Tab; label: string }[] = [
  { key: "champions", label: "Champions" },
  { key: "rankings", label: "Rankings" },
  { key: "bouts", label: "Bouts" },
  { key: "results", label: "Results" },
  { key: "news", label: "News" },
  { key: "submit", label: "Submit fighter" },
  { key: "admin", label: "Admin review" },
];

function App() {
  const [tab, setTab] = useState<Tab>("champions");

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <img className="brand-logo" src="/wbc-logo.png" alt="WBC Muay Thai" />
          <div>
            <p className="eyebrow">Official organisation</p>
            <h1>Muay Thai New Zealand</h1>
          </div>
        </div>

        <nav className="tab-nav" aria-label="Main navigation">
          {TABS.map((t) => (
            <button
              key={t.key}
              type="button"
              className={tab === t.key ? "tab-button active" : "tab-button"}
              onClick={() => setTab(t.key)}
              disabled={tab === t.key}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="content-panel">
        {tab === "champions" && <ChampionsPage />}
        {tab === "rankings" && <RankingsPage />}
        {tab === "bouts" && <BoutsPage />}
        {tab === "results" && <ResultsPage />}
        {tab === "news" && <NewsPage />}
        {tab === "submit" && <SubmitFighterPage />}
        {tab === "admin" && <AdminSubmissionsPage />}
      </main>
    </div>
  );
}

export default App;
