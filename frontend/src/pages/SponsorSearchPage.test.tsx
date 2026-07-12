import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";
import SponsorSearchPage from "./SponsorSearchPage";

const searchSponsors = vi.fn();
const getFiscalYears = vi.fn();
const getProfessions = vi.fn();
const getStates = vi.fn();
const getCaseStatuses = vi.fn();
const getDataFreshness = vi.fn();
const apiGet = vi.fn();

vi.mock("../api/sponsorApi", () => ({
  searchSponsors: (...args: unknown[]) => searchSponsors(...args),
}));

vi.mock("../api/metadataApi", () => ({
  getFiscalYears: () => getFiscalYears(),
  getProfessions: () => getProfessions(),
  getStates: () => getStates(),
  getCaseStatuses: () => getCaseStatuses(),
  getDataFreshness: () => getDataFreshness(),
}));

vi.mock("../api/client", async () => {
  const actual = await vi.importActual("../api/client");
  return {
    ...actual,
    apiGet: (...args: unknown[]) => apiGet(...args),
  };
});

function renderPage() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <SponsorSearchPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  getFiscalYears.mockResolvedValue([{ label: "All years", value: "all", reportingPeriod: null }]);
  getProfessions.mockResolvedValue([]);
  getStates.mockResolvedValue(["All states", "WA"]);
  getCaseStatuses.mockResolvedValue(["All statuses", "CERTIFIED"]);
  getDataFreshness.mockResolvedValue({
    latestGovernmentImport: null,
    reportingPeriod: null,
    latestCurrentJobsRetrieval: null,
    governmentDataLabel: "Latest imported government data",
  });
  apiGet.mockResolvedValue({
    databaseType: "sqlite",
    demoSeedEnabled: true,
    officialPermDataImported: false,
    employers: 3,
    occupations: 3,
    permCases: 5,
    currentJobs: 3,
    imports: 2,
    availableFiscalYears: [2026, 2025],
    availableStates: ["CA", "TX", "WA"],
    availableOccupations: [{ socCode: "15-1252", socTitle: "Software Developers" }],
  });
  searchSponsors.mockReset();
});

test("sponsor search does not run on initial load", async () => {
  renderPage();
  await screen.findByText("Enter a search term or select at least one filter.");
  expect(searchSponsors).not.toHaveBeenCalled();
});

test("search runs after form submission", async () => {
  searchSponsors.mockResolvedValue({
    page: 1,
    pageSize: 25,
    totalRecords: 1,
    totalPages: 1,
    resultView: "employers",
    totalMatchingEmployers: 1,
    totalMatchingPermCases: 2,
    generatedAt: "",
    results: [],
  });
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "Northwind" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await waitFor(() => expect(searchSponsors).toHaveBeenCalled());
});

test("clear filters resets the form", async () => {
  renderPage();
  const input = await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology");
  fireEvent.change(input, { target: { value: "Northwind" } });
  fireEvent.click(screen.getByRole("button", { name: "Clear Filters" }));
  await waitFor(() => expect(input).toHaveValue(""));
});

test("empty database state is shown correctly", async () => {
  apiGet.mockResolvedValueOnce({
    databaseType: "sqlite",
    demoSeedEnabled: false,
    officialPermDataImported: false,
    employers: 0,
    occupations: 0,
    permCases: 0,
    currentJobs: 0,
    imports: 0,
    availableFiscalYears: [],
    availableStates: [],
    availableOccupations: [],
  });
  searchSponsors.mockResolvedValue({
    page: 1,
    pageSize: 25,
    totalRecords: 0,
    totalPages: 1,
    resultView: "employers",
    totalMatchingEmployers: 0,
    totalMatchingPermCases: 0,
    generatedAt: "",
    results: [],
  });
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "Northwind" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await screen.findByText(/No PERM sponsorship data has been imported/i);
});

test("no match state is shown correctly", async () => {
  searchSponsors.mockResolvedValue({
    page: 1,
    pageSize: 25,
    totalRecords: 0,
    totalPages: 1,
    resultView: "employers",
    totalMatchingEmployers: 0,
    totalMatchingPermCases: 0,
    generatedAt: "",
    results: [],
  });
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "unknown" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await screen.findByText(/No sponsors matched these filters/i);
});

test("suggested demo search submits correctly", async () => {
  searchSponsors.mockResolvedValue({
    page: 1,
    pageSize: 25,
    totalRecords: 1,
    totalPages: 1,
    resultView: "employers",
    totalMatchingEmployers: 1,
    totalMatchingPermCases: 2,
    generatedAt: "",
    results: [],
  });
  renderPage();
  fireEvent.click(await screen.findByRole("button", { name: "Northwind" }));
  await waitFor(() =>
    expect(searchSponsors).toHaveBeenCalledWith(expect.objectContaining({ searchText: "Northwind" }))
  );
});

test("api errors display a useful message", async () => {
  searchSponsors.mockRejectedValue(new Error("The backend encountered an internal error."));
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "Northwind" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await screen.findByText("The backend encountered an internal error.");
});

test("result summary and employer aggregation are displayed for software", async () => {
  searchSponsors.mockResolvedValue({
    page: 1,
    pageSize: 10,
    totalRecords: 1,
    totalPages: 1,
    resultView: "employers",
    totalMatchingEmployers: 1,
    totalMatchingPermCases: 2,
    generatedAt: "",
    results: [
      {
        employerId: 1,
        employerName: "Northwind Cloud",
        normalizedEmployerName: "NORTHWIND CLOUD",
        fiscalYear: 2026,
        numberOfPermFilings: 2,
        numberCertified: 2,
        numberDenied: 0,
        numberWithdrawn: 0,
        certificationRate: 100,
        primaryOccupation: "Software Developers",
        socCode: "15-1252",
        topJobTitle: "Staff Platform Engineer",
        worksiteCity: "Seattle",
        worksiteState: "WA",
        offeredWage: 160000,
        wageUnit: "Year",
        filingDate: "2026-07-04",
        decisionDate: "2026-07-10",
        caseStatus: "CERTIFIED",
        dataSource: "U.S. Department of Labor OFLC PERM disclosure data",
        dataUpdatedDate: "2026-07-02T00:00:00",
        currentJobCount: 1,
        currentSponsoredJobCount: 1,
        h1bSponsorshipHistory: true,
        sponsorshipConfidenceLevel: "Moderate recent PERM history",
        sponsorshipScore: 60,
        sponsorshipReasons: [],
        dataLimitations: [],
        matchingFilings: [
          {
            caseNumber: "DEMO-2025-0002",
            jobTitle: "Platform Engineer",
            socCode: "15-1252",
            occupation: "Software Developers",
            fiscalYear: 2025,
            caseStatus: "CERTIFIED",
            filingDate: "2025-01-18",
            decisionDate: "2025-06-12",
            worksiteCity: "Seattle",
            worksiteState: "WA",
            offeredWage: 160000,
            wageUnit: "Year",
            source: "synthetic_demo_fy2025.csv",
          },
          {
            caseNumber: "DEMO-2024-0001",
            jobTitle: "Senior Software Engineer",
            socCode: "15-1252",
            occupation: "Software Developers",
            fiscalYear: 2024,
            caseStatus: "CERTIFIED",
            filingDate: "2024-03-14",
            decisionDate: "2024-08-09",
            worksiteCity: "Seattle",
            worksiteState: "WA",
            offeredWage: 153500,
            wageUnit: "Year",
            source: "synthetic_demo_fy2024.csv",
          },
        ],
      },
    ],
  });
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "software" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await screen.findByText("1 employer matched, 2 PERM cases aggregated");
  await screen.findByText("Northwind Cloud");
  await screen.findByRole("button", { name: "View filings (2)" });
});

test("filing view shows separate matching records", async () => {
  searchSponsors
    .mockResolvedValueOnce({
      page: 1,
      pageSize: 10,
      totalRecords: 1,
      totalPages: 1,
      resultView: "employers",
      totalMatchingEmployers: 1,
      totalMatchingPermCases: 2,
      generatedAt: "",
      results: [
        {
          employerId: 1,
          employerName: "Northwind Cloud",
          normalizedEmployerName: "NORTHWIND CLOUD",
          fiscalYear: 2026,
          numberOfPermFilings: 2,
          numberCertified: 2,
          numberDenied: 0,
          numberWithdrawn: 0,
          certificationRate: 100,
          primaryOccupation: "Software Developers",
          socCode: "15-1252",
          topJobTitle: "Staff Platform Engineer",
          worksiteCity: "Seattle",
          worksiteState: "WA",
          offeredWage: 160000,
          wageUnit: "Year",
          filingDate: "2026-07-04",
          decisionDate: "2026-07-10",
          caseStatus: "CERTIFIED",
          dataSource: "U.S. Department of Labor OFLC PERM disclosure data",
          dataUpdatedDate: "2026-07-02T00:00:00",
          currentJobCount: 1,
          currentSponsoredJobCount: 1,
          h1bSponsorshipHistory: true,
          sponsorshipConfidenceLevel: "Moderate recent PERM history",
          sponsorshipScore: 60,
          sponsorshipReasons: [],
          dataLimitations: [],
          matchingFilings: [],
        },
      ],
    })
    .mockResolvedValueOnce({
      page: 1,
      pageSize: 10,
      totalRecords: 2,
      totalPages: 1,
      resultView: "filings",
      totalMatchingEmployers: 1,
      totalMatchingPermCases: 2,
      generatedAt: "",
      results: [
        {
          employerId: 1,
          employerName: "Northwind Cloud",
          caseNumber: "DEMO-2025-0002",
          jobTitle: "Platform Engineer",
          socCode: "15-1252",
          occupation: "Software Developers",
          fiscalYear: 2025,
          caseStatus: "CERTIFIED",
          filingDate: "2025-01-18",
          decisionDate: "2025-06-12",
          worksiteCity: "Seattle",
          worksiteState: "WA",
          offeredWage: 160000,
          wageUnit: "Year",
          source: "synthetic_demo_fy2025.csv",
        },
        {
          employerId: 1,
          employerName: "Northwind Cloud",
          caseNumber: "DEMO-2024-0001",
          jobTitle: "Senior Software Engineer",
          socCode: "15-1252",
          occupation: "Software Developers",
          fiscalYear: 2024,
          caseStatus: "CERTIFIED",
          filingDate: "2024-03-14",
          decisionDate: "2024-08-09",
          worksiteCity: "Seattle",
          worksiteState: "WA",
          offeredWage: 153500,
          wageUnit: "Year",
          source: "synthetic_demo_fy2024.csv",
        },
      ],
    });
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "software" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await screen.findByText("1 employer matched, 2 PERM cases aggregated");
  fireEvent.click(screen.getByRole("button", { name: "Filing view" }));
  await screen.findByText("DEMO-2025-0002");
  await screen.findByText("DEMO-2024-0001");
});
