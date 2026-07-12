import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <section className="hero">
      <div>
        <p className="eyebrow">VisaSponsor Jobs</p>
        <h1>Search historical PERM activity and current jobs without overstating sponsorship claims.</h1>
        <p className="lede">
          Explore historical green-card sponsorship evidence, current openings from sponsoring employers, and job
          postings that explicitly mention sponsorship language.
        </p>
        <div className="button-row">
          <Link to="/sponsors">Open sponsor search</Link>
          <Link to="/methodology" className="secondary-link">
            Review methodology
          </Link>
        </div>
      </div>
      <div className="hero-card panel">
        <h2>Important disclaimer</h2>
        <p>
          Results are based on historical and current public filing data. A previous filing does not guarantee that an
          employer or current position will provide immigration sponsorship.
        </p>
      </div>
    </section>
  );
}
