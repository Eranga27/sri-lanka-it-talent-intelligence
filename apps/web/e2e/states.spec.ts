import { test, expect } from "@playwright/test";

test.describe("Edge Cases, Error Handling & Empty States", () => {
  test("API Error state does not crash UI or expose raw stack traces", async ({ page }) => {
    // Intercept API with HTTP 500 error
    await page.route("**/api/market/summary", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Internal Server Error" }),
      });
    });

    await page.goto("/");

    // The page must render header and fallback gracefully
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.getByText(/Traceback|Python Error|Exception at/i)).not.toBeVisible();
  });

  test("Empty data state handles zero records gracefully", async ({ page }) => {
    // Mock zero data available
    await page.route("**/api/market/summary", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_sri_lankan_it_jobs: 0,
          total_sri_lankan_jobs: 0,
          total_jobs_observed: 0,
          connected_sources_count: 0,
          data_available: false,
        }),
      });
    });

    await page.route("**/api/roles/demand", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
    });

    await page.route("**/api/skills/demand", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
    });

    await page.goto("/");

    // Verify empty state container message appears
    await expect(page.getByText("No Sri Lankan IT data available yet.")).toBeVisible();
    await expect(page.getByText("python scripts/run_pipelines.py --layer all")).toBeVisible();
  });

  test("Responsive layout has no horizontal overflow on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto("/");

    // Check body scroll width equals viewport width
    const overflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });

    expect(overflow).toBe(false);
  });
});
