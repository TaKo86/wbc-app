import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "./api/client";
import type { Gender, SubmissionFight } from "./api/types";

const initialForm = {
  submitted_name: "",
  submitted_email: "",
  name: "",
  gender: "M" as Gender,
  gym_name: "",
  recent_fights: Array.from({ length: 5 }, (_, index) => ({
    fight_number: index + 1,
    opponent_name: "",
    result: "Win" as SubmissionFight["result"],
  })),
  am_wins: 0,
  am_losses: 0,
  am_draws: 0,
  pro_wins: 0,
  pro_losses: 0,
  pro_draws: 0,
};

export function SubmitFighterPage() {
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  function update(field: keyof typeof form, value: string | number | SubmissionFight[]) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      await api.createSubmission({
        ...form,
        recent_fights: form.recent_fights.filter((fight) => fight.opponent_name.trim()),
      });
      setForm(initialForm);
      setMessage("Thanks. Your fighter record has been submitted for review.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to submit record.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="form-page">
      <h1>Submit a fighter record</h1>
      <p className="page-muted">Submit a new or updated fighter record for WBC Muay Thai NZ review.</p>
      <form className="fighter-form" onSubmit={submit}>
        <label>Your name<input required value={form.submitted_name} onChange={(e) => update("submitted_name", e.target.value)} /></label>
        <label>Your email<input required type="email" value={form.submitted_email} onChange={(e) => update("submitted_email", e.target.value)} /></label>
        <label>Fighter name<input required value={form.name} onChange={(e) => update("name", e.target.value)} /></label>
        <label>Gender<select value={form.gender} onChange={(e) => update("gender", e.target.value)}><option value="M">Male</option><option value="F">Female</option></select></label>
        <label>Gym<input value={form.gym_name} onChange={(e) => update("gym_name", e.target.value)} /></label>
        <fieldset><legend>Amateur record</legend><RecordInputs form={form} update={update} prefix="am" /></fieldset>
        <fieldset><legend>Professional record</legend><RecordInputs form={form} update={update} prefix="pro" /></fieldset>
        <fieldset><legend>Last five fights</legend><RecentFightInputs fights={form.recent_fights} update={(recent_fights) => update("recent_fights", recent_fights)} /></fieldset>
        <button className="primary-action" disabled={busy}>{busy ? "Submitting..." : "Submit for review"}</button>
      </form>
      {message && <p className="form-message">{message}</p>}
    </div>
  );
}

function RecordInputs({ form, update, prefix }: { form: typeof initialForm; update: (field: keyof typeof initialForm, value: string | number | SubmissionFight[]) => void; prefix: "am" | "pro" }) {
  return <div className="record-inputs">{(["wins", "losses", "draws"] as const).map((result) => <label key={result}>{result}<input type="number" min="0" value={form[`${prefix}_${result}`]} onChange={(e) => update(`${prefix}_${result}`, Number(e.target.value))} /></label>)}</div>;
}

function RecentFightInputs({ fights, update }: { fights: SubmissionFight[]; update: (fights: SubmissionFight[]) => void }) {
  return <div className="recent-fight-inputs">{fights.map((fight, index) => <div className="recent-fight-row" key={fight.fight_number}><span>#{index + 1}</span><input placeholder="Opponent name" value={fight.opponent_name} onChange={(e) => update(fights.map((item) => item.fight_number === fight.fight_number ? { ...item, opponent_name: e.target.value } : item))} /><select value={fight.result} onChange={(e) => update(fights.map((item) => item.fight_number === fight.fight_number ? { ...item, result: e.target.value as SubmissionFight["result"] } : item))}><option>Win</option><option>Loss</option><option>Decision win</option><option>Decision loss</option><option>TKO win</option><option>TKO loss</option><option>Draw</option><option>No contest</option></select></div>)}</div>;
}
