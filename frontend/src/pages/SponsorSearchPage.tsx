import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import SearchForm from "../components/SearchForm";
import SponsorTable from "../components/SponsorTable";
import SponsorCard from "../components/SponsorCard";
import Pagination from "../components/Pagination";
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import DataFreshnessBanner from "../components/DataFreshnessBanner";
import { getCaseStatuses, getDataFreshness, getFiscalYears, getProfessions, getStates } from "../api/metadataApi";
import { searchSponsors } from "../api/sponsorApi";
import type { SponsorSearchRequest } from "../types/sponsor";

const initialValues: SponsorSearchRequest = {
  searchText: "software",
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

export default function SponsorSearchPage() {
  const [filters, setFilters] = useState<SponsorSearchRequest>(initialValues);
  const [view, setView] = useState<"table" | "cards">("table");

  const fiscalYearsQuery = useQuery({ queryKey: ["fiscal-years"], queryFn: getFiscalYears });
  const professionsQuery = useQuery({ queryKey: ["professions"], queryFn: getProfessions });
  const statesQuery = useQuery({ queryKey: ["states"], queryFn: getStates });
  const statusesQuery = useQuery({ queryKey: ["case-statuses"], queryFn: getCaseStatuses });
  const freshnessQuery = useQuery({ queryKey: ["data-freshness"], queryFn: getDataFreshness });
  const searchQuery = useQuery({
    queryKey: ["sponsor-search", filters],
    queryFn: () => searchSponsors(filters),
  });

  const results = searchQuery.data?.results ?? [];
  const activeChips = useMemo(() => {
    const chips = [];
    if (filters.searchText) chips.push(`Search: ${filters.searchText}`);
    if (filters.fiscalYears.length) chips.push(`FY: ${filters.fiscalYears.join(", ")}`);
    if (filters.states.length) chips.push(`State: ${filters.states.join(", ")}`);
    if (filters.professionIds.length) chips.push(`Profession filter active`);
    chips.push(`Min filings: ${filters.minimumFilings}`);
    return chips;
  }, [filters]);

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
          defaultValues={filters}
          fiscalYears={fiscalYearsQuery.data ?? []}
          professions={professionsQuery.data ?? []}
          states={statesQuery.data ?? []}
          caseStatuses={statusesQuery.data ?? []}
          onSubmit={(values) => setFilters({ ...values, page: 1, pageSize: filters.pageSize })}
        />
      )}

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

      {searchQuery.isLoading ? <LoadingState label="Searching sponsor history..." /> : null}
      {searchQuery.isError ? <ErrorState message={(searchQuery.error as Error).message} /> : null}
      {!searchQuery.isLoading && !searchQuery.isError && results.length === 0 ? (
        <EmptyState message="No sponsors matched the current filters." />
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
            onChange={(page) => setFilters((current) => ({ ...current, page }))}
          />
        </>
      ) : null}
    </section>
  );
}
