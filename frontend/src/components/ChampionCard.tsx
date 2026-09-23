import type { Champion } from "../api/types";
import { FighterPhoto } from "./FighterPhoto";

type ChampionCardProps = {
  champion: Champion;
};

export function ChampionCard({ champion }: ChampionCardProps) {
  const { fighter } = champion;

  return (
    <li>
      <FighterPhoto
        fighterId={fighter.id}
        name={fighter.name}
        photoUrl={fighter.photo_url}
      />
      <div className="champion-details">
        <span className="champion-division">{champion.weight_class.name}</span>
        <strong>{fighter.name}</strong>
        <span>{champion.level} · {champion.scope}</span>
        {champion.won_against && <span>{`won against ${champion.won_against}`}</span>}
        <span className="champion-meta">
          Since {new Date(champion.since).toLocaleDateString()}
          {champion.event && ` · ${champion.event}`}
        </span>
      </div>
    </li>
  );
}
