import { MarketSummary, MarketCoverage } from "@/lib/api";
import { Card, SectionLabel } from "../ui";
import { CountUp } from "./CountUp";

export function MarketOverview({ summary, coverage }: { summary: MarketSummary | null, coverage: MarketCoverage | null }) {
  if (!summary?.data_available) return null;

  return (
    <section aria-label="Market Overview" className="space-y-4">
      <SectionLabel>Market Overview</SectionLabel>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Observed IT Opportunities" sublabel="Active Sri Lankan IT jobs">
          <CountUp value={summary.total_sri_lankan_it_jobs || 0} className="text-3xl font-light text-white" />
        </KpiCard>
        <KpiCard label="Sri Lankan Jobs Observed" sublabel="All local vacancies">
          <CountUp value={summary.total_sri_lankan_jobs || 0} className="text-3xl font-light text-white" />
        </KpiCard>
        <KpiCard label="Connected Sources" sublabel="Active public integrations">
          <CountUp value={summary.unique_sources || 0} className="text-3xl font-light text-white" />
        </KpiCard>
        <KpiCard label="Market Coverage" sublabel="Integration scope">
          <span className="text-3xl font-light text-white uppercase tracking-wide">
            {coverage?.state || "LIMITED"}
          </span>
        </KpiCard>
      </div>
    </section>
  );
}

function KpiCard({ label, sublabel, children }: { label: string; sublabel: string; children: React.ReactNode }) {
  return (
    <Card className="flex flex-col gap-4 fade-up">
      <div>
        <p className="text-xs font-medium text-gray-400">{label}</p>
        <p className="text-[10px] text-gray-600 mt-1">{sublabel}</p>
      </div>
      <div className="mt-auto">{children}</div>
    </Card>
  );
}
