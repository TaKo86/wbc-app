import { useState } from "react";
import { api } from "./api/client";
import type { FighterSubmission } from "./api/types";

export function AdminSubmissionsPage() {
  const [key, setKey] = useState("");
  const [submissions, setSubmissions] = useState<FighterSubmission[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editGym, setEditGym] = useState("");

  async function load() {
    setLoading(true);
    try { setSubmissions(await api.getSubmissions(key)); setMessage(""); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Unable to load submissions."); }
    finally { setLoading(false); }
  }

  async function action(work: () => Promise<unknown>) {
    try { await work(); await load(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Admin action failed."); }
  }

  function startEditing(submission: FighterSubmission) {
    setEditingId(submission.id);
    setEditName(submission.name);
    setEditGym(submission.gym_name || "");
  }

  return (
    <div className="form-page">
      <h1>Submission review</h1>
      <p className="page-muted">Review public fighter records before they enter the live database.</p>
      <div className="admin-login"><label>Admin key<input type="password" value={key} onChange={(e) => setKey(e.target.value)} /></label><button className="primary-action" onClick={load} disabled={!key || loading}>Load submissions</button></div>
      {message && <p className="form-message">{message}</p>}
      <div className="submission-list">
        {submissions.map((submission) => <article className="submission-card" key={submission.id}>
          <div><span className={`status status-${submission.status}`}>{submission.status}</span><h2>{submission.name}</h2><p>{submission.gender} · {submission.gym_name || "No gym listed"}</p><p>Amateur {submission.am_wins}-{submission.am_losses}-{submission.am_draws} · Pro {submission.pro_wins}-{submission.pro_losses}-{submission.pro_draws}</p>{submission.recent_fights.length > 0 && <p>Recent: {submission.recent_fights.map((fight) => `${fight.opponent_name} (${fight.result})`).join(" · ")}</p>}<p className="page-muted">Submitted by {submission.submitted_name} ({submission.submitted_email})</p></div>
          {editingId === submission.id ? <div className="submission-edit"><input value={editName} onChange={(e) => setEditName(e.target.value)} aria-label="Fighter name" /><input value={editGym} onChange={(e) => setEditGym(e.target.value)} aria-label="Gym name" /><button onClick={() => action(async () => { await api.updateSubmission(submission.id, key, { name: editName, gym_name: editGym || null }); setEditingId(null); })}>Save</button><button onClick={() => setEditingId(null)}>Cancel</button></div> : <div className="submission-actions"><button onClick={() => startEditing(submission)}>Edit</button><button onClick={() => action(() => api.approveSubmission(submission.id, key))} disabled={submission.status === "approved"}>Approve</button><button onClick={() => action(() => api.rejectSubmission(submission.id, key, "Needs correction or verification"))} disabled={submission.status === "rejected"}>Reject</button><button onClick={() => action(() => api.deleteSubmission(submission.id, key))}>Delete</button></div>}
        </article>)}
      </div>
    </div>
  );
}
