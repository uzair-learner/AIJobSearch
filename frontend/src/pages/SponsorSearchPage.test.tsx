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
  searchSponsors.mockResolvedValue({ page: 1, pageSize: 25, totalRecords: 1, totalPages: 1, generatedAt: "", results: [] });
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
    employers: 0,
    occupations: 0,
    permCases: 0,
    currentJobs: 0,
    imports: 0,
    availableFiscalYears: [],
    availableStates: [],
    availableOccupations: [],
  });
  searchSponsors.mockResolvedValue({ page: 1, pageSize: 25, totalRecords: 0, totalPages: 1, generatedAt: "", results: [] });
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "Northwind" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await screen.findByText(/No PERM sponsorship data has been imported/i);
});

test("no match state is shown correctly", async () => {
  searchSponsors.mockResolvedValue({ page: 1, pageSize: 25, totalRecords: 0, totalPages: 1, generatedAt: "", results: [] });
  renderPage();
  fireEvent.change(await screen.findByPlaceholderText("Employer, occupation, SOC code, city, state, technology"), {
    target: { value: "unknown" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Search sponsors" }));
  await screen.findByText(/No sponsors matched these filters/i);
});

test("suggested demo search submits correctly", async () => {
  searchSponsors.mockResolvedValue({ page: 1, pageSize: 25, totalRecords: 1, totalPages: 1, generatedAt: "", results: [] });
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
