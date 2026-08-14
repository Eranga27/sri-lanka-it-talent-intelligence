import { api } from "@/lib/api";
import { Hero } from "@/components/dashboard/Hero";
import { MarketOverview } from "@/components/dashboard/MarketOverview";
import { MarketPulse } from "@/components/dashboard/MarketPulse";
import { RoleDemand } from "@/components/dashboard/RoleDemand";
import { SkillDemand } from "@/components/dashboard/SkillDemand";
import { MarketCoverageSection } from "@/components/dashboard/MarketCoverage";
import { SourceHealth } from "@/components/dashboard/SourceHealth";
import { Methodology } from "@/components/dashboard/Methodology";

export const dynamic = "force-dynamic";

export default async function Home() {
  // Fetch all dashboard data concurrently — no mock fallbacks
  const [summary, coverage, roles, skills, sources] = await Promise.all([
    api.getMarketSummary(),
    api.getMarketCoverage(),
    api.getRoleDemand(),
    api.getSkillDemand(),
    api.getSources(),
  ]);

  const hasData = summary?.data_available ?? false;

  return (
    <div className="py-10 space-y-20">
      {/* ── HERO ───────────────────────────────────────────────── */}
      <Hero coverage={coverage} />

      {/* ── MARKET OVERVIEW ────────────────────────────────────── */}
      <section id="market">
        {hasData ? (
          <MarketOverview summary={summary} coverage={coverage} />
        ) : (
          <EmptyDashboard />
        )}
      </section>

      {/* ── MARKET PULSE ───────────────────────────────────────── */}
      {hasData && <MarketPulse summary={summary} />}

      {/* ── ROLE + SKILL DEMAND ────────────────────────────────── */}
      {hasData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <RoleDemand roles={roles} />
          <SkillDemand skills={skills} />
        </div>
      )}

      {/* ── MARKET COVERAGE ────────────────────────────────────── */}
      {hasData && <MarketCoverageSection coverage={coverage} />}

      {/* ── DATA SOURCES ───────────────────────────────────────── */}
      <section id="sources">
        <SourceHealth sources={sources} />
      </section>

      {/* ── METHODOLOGY ────────────────────────────────────────── */}
      <Methodology />
    </div>
  );
}

function EmptyDashboard() {
  return (
    <div className="py-24 text-center border border-dashed border-white/10 rounded-2xl space-y-4">
      <h2 className="text-2xl font-light text-white">
        No Sri Lankan IT data available yet.
      </h2>
      <p className="text-gray-500 text-sm max-w-sm mx-auto">
        The platform is waiting for a successful source ingestion. Run the
        pipeline to populate the dashboard.
      </p>
      <pre className="inline-block text-xs text-gray-600 mt-4 bg-white/5 px-4 py-2 rounded-lg">
        python scripts/run_pipelines.py --layer all
      </pre>
    </div>
  );
}
