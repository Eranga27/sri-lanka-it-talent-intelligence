import { test, expect } from "@playwright/test";

test.describe("Intelligence Dashboard E2E User Journey", () => {
  test.beforeEach(async ({ page }) => {
    // Intercept backend API calls with deterministic contract mocks to ensure reliable test execution
    await page.route("**/api/market/summary", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_sri_lankan_it_jobs: 20,
          total_sri_lankan_jobs: 38,
          total_jobs_observed: 941,
          connected_sources_count: 3,
          data_available: true,
          latest_ingestion_timestamp: "2026-08-14T11:42:46Z",
        }),
      });
    });

    await page.route("**/api/market/coverage", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          state: "limited",
          label: "LIMITED",
          explanation: "Initial public ATS sources active.",
          metrics: {
            total_sri_lankan_it_jobs: 20,
            total_sri_lankan_jobs: 38,
            unique_sources: 3,
          },
        }),
      });
    });

    await page.route("**/api/roles/demand", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { role_category: "Software Engineering", job_count: 12, job_percentage: 60.0 },
          { role_category: "Data & Analytics", job_count: 5, job_percentage: 25.0 },
          { role_category: "DevOps & Infrastructure", job_count: 3, job_percentage: 15.0 },
        ]),
      });
    });

    await page.route("**/api/skills/demand", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { skill_id: "python", skill_name: "Python", skill_category: "Programming", job_count: 10, job_percentage: 50.0 },
          { skill_id: "react", skill_name: "React", skill_category: "Frontend", job_count: 8, job_percentage: 40.0 },
          { skill_id: "docker", skill_name: "Docker", skill_category: "DevOps", job_count: 6, job_percentage: 30.0 },
          { skill_id: "aws", skill_name: "AWS", skill_category: "Cloud", job_count: 5, job_percentage: 25.0 },
        ]),
      });
    });

    await page.route("**/api/sources/", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { source_id: "greenhouse", name: "Greenhouse", status: "active", last_ingestion: "2026-08-14T11:42:46Z", job_count: 503 },
          { source_id: "workable", name: "Workable", status: "active", last_ingestion: "2026-08-14T11:42:46Z", job_count: 50 },
          { source_id: "lever", name: "Lever", status: "active", last_ingestion: "2026-08-14T11:42:46Z", job_count: 388 },
        ]),
      });
    });

    await page.goto("/");
  });

  test("1. Critical Journey & Hero rendering", async ({ page }) => {
    // Page title and H1
    await expect(page).toHaveTitle(/Sri Lanka IT Talent Intelligence/i);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible();
    await expect(heading).toContainText("Sri Lanka IT Talent Intelligence");

    // Live status badge in hero
    await expect(page.getByText(/LIVE DATA|LIMITED COVERAGE/i).first()).toBeVisible();
  });

  test("2. Market Overview section renders dynamic metrics", async ({ page }) => {
    const marketSection = page.locator("#market");
    await expect(marketSection).toBeVisible();

    // Verify KPI Cards load metric values
    await expect(page.getByText("Active IT Opportunities")).toBeVisible();
    await expect(page.getByText("Sri Lankan Jobs Observed")).toBeVisible();
    await expect(page.getByText("Connected Sources")).toBeVisible();

    // Values dynamically render from contract
    await expect(page.getByText("20")).toBeVisible();
    await expect(page.getByText("38")).toBeVisible();
  });

  test("3. Market Pulse section renders statement and timestamp", async ({ page }) => {
    await expect(page.getByText("Market Pulse")).toBeVisible();
    await expect(page.getByText("active IT roles observed")).toBeVisible();
  });

  test("4. Role Demand section renders categories and progress bars", async ({ page }) => {
    const rolesSection = page.locator("#roles");
    await expect(rolesSection).toBeVisible();

    await expect(page.getByText("Software Engineering")).toBeVisible();
    await expect(page.getByText("Data & Analytics")).toBeVisible();
    await expect(page.getByText("DevOps & Infrastructure")).toBeVisible();

    // Role count values
    await expect(page.getByText("12")).toBeVisible();
    await expect(page.getByText("60.0%")).toBeVisible();
  });

  test("5. Skill Demand section and Category filtering", async ({ page }) => {
    const skillsSection = page.locator("#skills");
    await expect(skillsSection).toBeVisible();

    // Category filter chips
    await expect(page.getByRole("button", { name: "All" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Frontend" })).toBeVisible();

    // Initial skills visible
    await expect(page.getByText("Python")).toBeVisible();
    await expect(page.getByText("React")).toBeVisible();

    // Click category chip "Frontend"
    await page.getByRole("button", { name: "Frontend" }).click();
    await expect(page.getByText("React")).toBeVisible();
    await expect(page.getByText("Python")).not.toBeVisible();
  });

  test("6. Market Coverage scale and disclaimer", async ({ page }) => {
    await expect(page.getByText("Market Coverage")).toBeVisible();
    await expect(page.getByText("LIMITED")).toBeVisible();
    await expect(page.getByText(/does not represent the complete Sri Lankan IT labour market/i)).toBeVisible();
  });

  test("7. Source Health registry section", async ({ page }) => {
    const sourcesSection = page.locator("#sources");
    await expect(sourcesSection).toBeVisible();

    await expect(page.getByText("Greenhouse")).toBeVisible();
    await expect(page.getByText("Workable")).toBeVisible();
    await expect(page.getByText("Lever")).toBeVisible();
  });

  test("8. Methodology documentation", async ({ page }) => {
    const methodSection = page.locator("#methodology");
    await expect(methodSection).toBeVisible();
    await expect(page.getByText(/Methodology & Scope/i)).toBeVisible();
    await expect(page.getByText(/Deterministic NLP/i)).toBeVisible();
  });

  test("9. Accessibility basics", async ({ page }) => {
    // Navigation accessibility
    const nav = page.getByRole("navigation", { name: "Main navigation" });
    await expect(nav).toBeVisible();

    // Check keyboard focusability on links
    const marketLink = page.getByRole("link", { name: "Market" });
    await marketLink.focus();
    await expect(marketLink).toBeFocused();
  });
});
