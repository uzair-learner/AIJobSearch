import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import SearchForm from "../components/SearchForm";
import SponsorTable from "../components/SponsorTable";
import SponsorCard from "../components/SponsorCard";
import Pagination from "../components/Pagination";
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";
import DataFreshnessBanner from "../components/DataFreshnessBanner";
import { apiGet } from "../api/client";
import { getCaseStatuses, getDataFreshness, getFiscalYears, getProfessions, getStates } from "../api/metadataApi";
import { searchSponsors } from "../api/sponsorApi";
import type { DatabaseSummary, SponsorSearchRequest } from "../types/sponsor";

const initialValues: SponsorSearchRequest = {
  searchText: "",
  fiscalYears: [],
  professionIds: [],
  states: [],
  caseStatuses: [],
  minimumFilings: 1,
  evidenceType: "all",
  dateRecency: "all",
  page: 1,
  pageSize: 10,
  sortBy: "recent_filings",
  sortDirection: "desc",
};

const syntheticSuggestions = ["Software Developers", "Data Scientists", "Information Security Analysts", "Northwind", "Contoso", "Fabrikam", "WA", "TX", "CA"];

function hasMeaningfulSearch(filters: SponsorSearchRequest): boolean {
  return Boolean(
    filters.searchText.trim() ||
      filters.fiscalYears.length ||
      filters.professionIds.length ||
      filters.states.length ||
      filters.caseStatuses.length ||
      filters.minimumFilings > 1 ||
      filters.evidenceType !== "all" ||
      filters.dateRecency !== "all"
  );
}

export default function SponsorSearchPage() {
  const [formFilters, setFormFilters] = useState<SponsorSearchRequest>(initialValues);
  const [submittedFilters, setSubmittedFilters] = useState<SponsorSearchRequest | null>(null);
  const [view, setView] = useState<"table" | "cards">("table");
  const [validationMessage, setValidationMessage] = useState<string>("");
  const [clearSignal, setClearSignal] = useState(0);

  const fiscalYearsQuery = useQuery({ queryKey: ["fiscal-years"], queryFn: getFiscalYears });
  const professionsQuery = useQuery({ queryKey: ["professions"], queryFn: getProfessions });
  const statesQuery = useQuery({ queryKey: ["states"], queryFn: getStates });
  const statusesQuery = useQuery({ queryKey: ["case-statuses"], queryFn: getCaseStatuses });
  const freshnessQuery = useQuery({ queryKey: ["data-freshness"], queryFn: getDataFreshness });
  const databaseSummaryQuery = useQuery({
    queryKey: ["database-summary"],
    queryFn: () => apiGet<DatabaseSummary>("/health/database-summary"),
  });
  const searchQuery = useQuery({
    queryKey: ["sponsor-search", submittedFilters],
    queryFn: () => searchSponsors(submittedFilters!),
    enabled: submittedFilters !== null,
  });

  const results = searchQuery.data?.results ?? [];
  const activeChips = useMemo(() => {
    const chips = [];
    if (submittedFilters?.searchText) chips.push(`Search: ${submittedFilters.searchText}`);
    if (submittedFilters?.fiscalYears.length) chips.push(`FY: ${submittedFilters.fiscalYears.join(", ")}`);
    if (submittedFilters?.states.length) chips.push(`State: ${submittedFilters.states.join(", ")}`);
    if (submittedFilters?.professionIds.length) chips.push(`Profession filter active`);
    if (submittedFilters) chips.push(`Min filings: ${submittedFilters.minimumFilings}`);
    return chips;
  }, [submittedFilters]);

  function submitFilters(values: SponsorSearchRequest) {
    const next = {
      ...values,
      searchText: values.searchText.trim(),
      fiscalYears: values.fiscalYears.filter((value) => value !== null && value !== undefined),
      professionIds: values.professionIds.filter((value) => value !== null && value !== undefined),
      states: values.states.filter(Boolean),
      caseStatuses: values.caseStatuses.filter(Boolean),
      page: 1,
      pageSize: formFilters.pageSize,
    };
    setFormFilters(next);
    if (!hasMeaningfulSearch(next)) {
      setValidationMessage("Enter a search term or select at least one filter.");
      setSubmittedFilters(null);
      return;
    }
    setValidationMessage("");
    setSubmittedFilters(next);
  }

  function clearFilters() {
    setFormFilters(initialValues);
    setSubmittedFilters(null);
    setValidationMessage("");
    setClearSignal((value) => value + 1);
  }

  function runSuggestion(suggestion: string) {
    const next = { ...initialValues, searchText: suggestion };
    setFormFilters(next);
    setSubmittedFilters(next);
    setValidationMessage("");
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Green Card Sponsor Search</p>
          <h1>Identify historical sponsorship evidence without overstating current availability.</h1>
        </div>
        <div className="view-toggle">
          <button className={view === "table" ? "active" : ""} onClick={() => setView("table")}>
            Table
          </button>
          <button className={view === "cards" ? "active" : ""} onClick={() => setView("cards")}>
            Cards
          </button>
        </div>
      </header>

      <DataFreshnessBanner {...freshnessQuery.data} />

      {fiscalYearsQuery.isLoading || professionsQuery.isLoading || statesQuery.isLoading || statusesQuery.isLoading ? (
        <LoadingState label="Loading metadata..." />
      ) : (
        <SearchForm
          defaultValues={formFilters}
          fiscalYears={fiscalYearsQuery.data ?? []}
          professions={professionsQuery.data ?? []}
          states={statesQuery.data ?? []}
          caseStatuses={statusesQuery.data ?? []}
          onSubmit={submitFilters}
          onClear={clearFilters}
          clearSignal={clearSignal}
        />
      )}

      {databaseSummaryQuery.data?.demoSeedEnabled ? (
        <section className="panel">
          <strong>Synthetic demo searches</strong>
          <p className="muted-text">These suggestions query synthetic demonstration records, not official government data.</p>
          <div className="chip-row">
            {syntheticSuggestions.map((suggestion) => (
              <button key={suggestion} type="button" className="secondary chip-button" onClick={() => runSuggestion(suggestion)}>
                {suggestion}
              </button>
            ))}
          </div>
        </section>
      ) : null}

      <div className="chip-row">
        {activeChips.map((chip) => (
          <span className="chip" key={chip}>
            {chip}
          </span>
        ))}
      </div>

      <section className="panel disclaimer">
        Results are based on historical and current public filing data. A previous filing does not guarantee that an
        employer or current position will provide immigration sponsorship.
      </section>

      {validationMessage ? <ErrorState message={validationMessage} /> : null}
      {searchQuery.isLoading ? <LoadingState label="Searching sponsor history..." /> : null}
      {searchQuery.isError ? <ErrorState message={(searchQuery.error as Error).message} /> : null}
      {!submittedFilters && !validationMessage ? (
        <section className="panel muted">Enter a search term or select at least one filter.</section>
      ) : null}
      {submittedFilters && !searchQuery.isLoading && !searchQuery.isError && databaseSummaryQuery.data?.permCases === 0 ? (
        <section className="panel muted">
          No PERM sponsorship data has been imported. Import an official Department of Labor PERM disclosure file or enable demonstration data.{" "}
          <Link to="/admin/imports">Open Imports</Link>
        </section>
      ) : null}
      {submittedFilters &&
      !searchQuery.isLoading &&
      !searchQuery.isError &&
      databaseSummaryQuery.data &&
      databaseSummaryQuery.data.permCases > 0 &&
      results.length === 0 ? (
        <section className="panel muted">
          <p>No sponsors matched these filters. Try a broader employer name, occupation, location, fiscal year, or clear some filters.</p>
          <p>
            Employers: {databaseSummaryQuery.data.employers} | PERM cases: {databaseSummaryQuery.data.permCases} | Fiscal years:{" "}
            {databaseSummaryQuery.data.availableFiscalYears.join(", ") || "None"} | Demo mode: {databaseSummaryQuery.data.demoSeedEnabled ? "Enabled" : "Disabled"}
          </p>
        </section>
      ) : null}

      {!searchQuery.isLoading && !searchQuery.isError && results.length > 0 ? (
        <>
          {view === "table" ? (
            <SponsorTable sponsors={results} />
          ) : (
            <div className="card-grid">
              {results.map((sponsor) => (
                <SponsorCard key={sponsor.employerId} sponsor={sponsor} />
              ))}
            </div>
          )}
          <Pagination
            page={searchQuery.data?.page ?? 1}
            totalPages={searchQuery.data?.totalPages ?? 1}
            onChange={(page) =>
              setSubmittedFilters((current) => (current ? { ...current, page } : current))
            }
          />
        </>
      ) : null}
    </section>
  );
}
