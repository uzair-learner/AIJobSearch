import { useState } from "react";
import { apiPostForm } from "../api/client";

export default function AdminImportsPage() {
  const [message, setMessage] = useState<string>("");

  async function handleSubmit(formData: FormData) {
    try {
      const fiscalYear = String(formData.get("fiscalYear") ?? "2026");
      const reportingPeriod = String(formData.get("reportingPeriod") ?? "Year to date");
      const file = formData.get("file") as File | null;
      if (!file) {
        setMessage("Choose a file first.");
        return;
      }
      const payload = new FormData();
      payload.set("file", file);
      const response = await apiPostForm(
        `/admin/imports/perm/upload?fiscalYear=${encodeURIComponent(fiscalYear)}&reportingPeriod=${encodeURIComponent(reportingPeriod)}`,
        payload,
        { "X-Admin-Token": import.meta.env.VITE_ADMIN_TOKEN ?? "change-me" }
      );
      setMessage(`Import queued: ${(response as { status?: string }).status ?? "unknown"}`);
    } catch (error) {
      setMessage((error as Error).message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Import Administration</p>
          <h1>Upload official PERM files with schema-aware processing.</h1>
        </div>
      </header>
      <form
        className="panel search-form"
        onSubmit={(event) => {
          event.preventDefault();
          handleSubmit(new FormData(event.currentTarget));
        }}
      >
        <div className="grid three">
          <label>
            Fiscal year
            <input name="fiscalYear" defaultValue="2026" />
          </label>
          <label>
            Reporting period
            <input name="reportingPeriod" defaultValue="Year to date" />
          </label>
          <label>
            File
            <input type="file" name="file" accept=".csv,.xlsx,.xls" />
          </label>
        </div>
        <div className="button-row">
          <button type="submit">Upload PERM file</button>
        </div>
        {message ? <p className="muted-text">{message}</p> : null}
      </form>
    </section>
  );
}
