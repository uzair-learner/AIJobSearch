import { useForm } from "react-hook-form";
import FiscalYearSelect from "./FiscalYearSelect";
import ProfessionSelect from "./ProfessionSelect";
import StateSelect from "./StateSelect";
import type { SponsorSearchRequest } from "../types/sponsor";

type SearchFormProps = {
  defaultValues: SponsorSearchRequest;
  fiscalYears: Array<{ label: string; value: string | number; reportingPeriod: string | null }>;
  professions: Array<{ id: number; socCode: string; socTitle: string }>;
  states: string[];
  caseStatuses: string[];
  onSubmit: (values: SponsorSearchRequest) => void;
};

export default function SearchForm({
  defaultValues,
  fiscalYears,
  professions,
  states,
  caseStatuses,
  onSubmit,
}: SearchFormProps) {
  const { register, handleSubmit, setValue, watch } = useForm<SponsorSearchRequest>({
    defaultValues,
  });

  return (
    <form className="search-form panel" onSubmit={handleSubmit(onSubmit)}>
      <div className="grid two">
        <label>
          Search text
          <input
            {...register("searchText")}
            placeholder="Employer, occupation, SOC code, city, state, technology"
          />
        </label>
        <label>
          Case status
          <select {...register("caseStatuses.0")}>
            <option value="">All statuses</option>
            {caseStatuses
              .filter((status) => status !== "All statuses")
              .map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
          </select>
        </label>
      </div>

      <div className="grid four">
        <FiscalYearSelect
          options={fiscalYears}
          value={watch("fiscalYears")}
          onChange={(value) => setValue("fiscalYears", value)}
        />
        <ProfessionSelect
          options={professions}
          value={watch("professionIds")}
          onChange={(value) => setValue("professionIds", value)}
        />
        <StateSelect options={states} value={watch("states")} onChange={(value) => setValue("states", value)} />
        <label>
          Minimum filings
          <select {...register("minimumFilings", { valueAsNumber: true })}>
            <option value={1}>At least 1 filing</option>
            <option value={5}>At least 5 filings</option>
            <option value={10}>At least 10 filings</option>
            <option value={25}>At least 25 filings</option>
            <option value={50}>At least 50 filings</option>
          </select>
        </label>
      </div>

      <div className="grid four">
        <label>
          Sponsorship evidence
          <select {...register("evidenceType")}>
            <option value="all">All evidence levels</option>
            <option value="historical_perm">Historical PERM sponsor</option>
            <option value="historical_with_current_jobs">Historical sponsor with current openings</option>
            <option value="current_job_explicit">Current job explicitly mentions sponsorship</option>
            <option value="h1b_perm">H-1B and PERM sponsor</option>
          </select>
        </label>
        <label>
          Date recency
          <select {...register("dateRecency")}>
            <option value="all">All available history</option>
            <option value="current_fiscal_year">Current fiscal year</option>
            <option value="last_12_months">Last 12 months</option>
            <option value="last_3_fiscal_years">Last 3 fiscal years</option>
          </select>
        </label>
        <label>
          Sort by
          <select {...register("sortBy")}>
            <option value="recent_filings">Most recent sponsorship activity</option>
            <option value="highest_certified">Highest number of certified filings</option>
            <option value="highest_certification_rate">Highest certification rate</option>
            <option value="most_current_jobs">Most current job openings</option>
            <option value="most_sponsored_current_jobs">Most sponsored current jobs</option>
            <option value="highest_sponsorship_score">Highest sponsorship score</option>
            <option value="highest_average_salary">Highest average salary</option>
            <option value="employer_name">Employer name</option>
            <option value="newest_filing_date">Newest filing date</option>
          </select>
        </label>
        <label>
          Direction
          <select {...register("sortDirection")}>
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </label>
      </div>

      <div className="button-row">
        <button type="submit">Search sponsors</button>
      </div>
    </form>
  );
}
