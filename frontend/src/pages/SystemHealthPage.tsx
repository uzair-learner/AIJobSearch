import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../api/client";
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";

export default function SystemHealthPage() {
  const query = useQuery({
    queryKey: ["health"],
    queryFn: () => apiGet<Record<string, unknown>>("/health"),
  });

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">System Health</p>
          <h1>Backend and data-ingestion status.</h1>
        </div>
      </header>
      {query.isLoading ? <LoadingState label="Checking API health..." /> : null}
      {query.isError ? <ErrorState message={(query.error as Error).message} /> : null}
      {query.data ? <pre className="panel code-block">{JSON.stringify(query.data, null, 2)}</pre> : null}
    </section>
  );
}
