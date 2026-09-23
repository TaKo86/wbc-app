import { useState } from "react";

type FighterPhotoProps = {
  fighterId: number;
  name: string;
  photoUrl: string | null;
};

export function FighterPhoto({ fighterId, name, photoUrl }: FighterPhotoProps) {
  const [failed, setFailed] = useState(false);
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const src = photoUrl || `/champions/${fighterId}.jpg`;

  if (failed) {
    return (
      <div className="fighter-photo fighter-photo-fallback" aria-label={`${name} photo unavailable`}>
        {initials}
      </div>
    );
  }

  return (
    <img
      className="fighter-photo"
      src={src}
      alt={`${name}, champion`}
      onError={() => setFailed(true)}
    />
  );
}
