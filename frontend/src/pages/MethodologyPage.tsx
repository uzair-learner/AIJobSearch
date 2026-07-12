export default function MethodologyPage() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Data Sources and Methodology</p>
          <h1>What the application does and does not claim.</h1>
        </div>
      </header>
      <div className="grid two">
        <article className="panel">
          <h2>Primary source</h2>
          <p>U.S. Department of Labor OFLC PERM public disclosure data is the primary sponsorship evidence source.</p>
          <p>The app distinguishes historical PERM activity from current job-level sponsorship language.</p>
        </article>
        <article className="panel">
          <h2>Important limitations</h2>
          <ul>
            <li>A PERM filing is not the same thing as a green-card approval.</li>
            <li>Historical sponsorship does not guarantee a current opening offers sponsorship.</li>
            <li>Rule-based scoring is explanatory, not legal advice.</li>
          </ul>
        </article>
      </div>
    </section>
  );
}
