import { NavLink, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SponsorSearchPage from "./pages/SponsorSearchPage";
import EmployerDetailPage from "./pages/EmployerDetailPage";
import CurrentJobsPage from "./pages/CurrentJobsPage";
import CompareEmployersPage from "./pages/CompareEmployersPage";
import MethodologyPage from "./pages/MethodologyPage";
import AdminImportsPage from "./pages/AdminImportsPage";
import SystemHealthPage from "./pages/SystemHealthPage";
import SavedSearchesPage from "./pages/SavedSearchesPage";

const links = [
  { to: "/", label: "Home" },
  { to: "/sponsors", label: "Sponsor Search" },
  { to: "/jobs", label: "Current Jobs" },
  { to: "/compare", label: "Compare" },
  { to: "/saved-searches", label: "Saved Searches" },
  { to: "/methodology", label: "Methodology" },
  { to: "/admin/imports", label: "Imports" },
  { to: "/health", label: "Health" },
];

export default function App() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="brand">
          <span className="brand-mark">VSJ</span>
          <div>
            <strong>VisaSponsor Jobs</strong>
            <p>Historical sponsorship evidence and current job signals</p>
          </div>
        </div>
        <nav>
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.to === "/"}>
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/sponsors" element={<SponsorSearchPage />} />
          <Route path="/employers/:employerId" element={<EmployerDetailPage />} />
          <Route path="/jobs" element={<CurrentJobsPage />} />
          <Route path="/compare" element={<CompareEmployersPage />} />
          <Route path="/saved-searches" element={<SavedSearchesPage />} />
          <Route path="/methodology" element={<MethodologyPage />} />
          <Route path="/admin/imports" element={<AdminImportsPage />} />
          <Route path="/health" element={<SystemHealthPage />} />
        </Routes>
      </main>
    </div>
  );
}
