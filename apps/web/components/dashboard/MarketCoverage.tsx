import { MarketCoverage } from "@/lib/api";
import { Card, SectionLabel } from "../ui";

const STATE_ORDER = ["limited", "moderate", "broad"] as const;
type CoverageState = (typeof STATE_ORDER)[number];

const STATE_LABELS: Record<CoverageState, string> = {
  limited: "LIMITED",
  moderate: "MODERATE",
  broad: "BROAD",
};

const STATE_COLORS: Record<CoverageState, string> = {
  limited: "text-yellow-400",
  moderate: "text-blue-400",
  broad: "text-emerald-400",
};

export function MarketCoverageSection({
  coverage,
}: {
  coverage: MarketCoverage | null;
}) {
  if (!coverage) return null;

  const state = (coverage.state ?? "limited") as CoverageState;
  const activeIndex = STATE_ORDER.indexOf(state);
  // Position: 0% → 50% → 100% mapped to 0% → 50% → 100% of the bar
  const dotLeft = `${(activeIndex / (STATE_ORDER.length - 1)) * 100}%`;

  const m = coverage.metrics;

  return (
    <section aria-labelledby="coverage-heading" className="space-y-4">
      <SectionLabel>Market Coverage</SectionLabel>
      <Card>
        <div className="flex flex-col md:flex-row gap-10 md:gap-16">
          {/* Left: state indicator */}
          <div className="flex-none space-y-6">
            <div>
              <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-[0.2em] mb-2">
                Coverage Level
              </p>
              <p
                id="coverage-heading"
                className={`text-4xl font-light uppercase tracking-widest ${STATE_COLORS[state]}`}
              >
                {STATE_LABELS[state]}
              </p>
            </div>

            {/* Scale bar */}
            <div className="relative w-56">
              <div className="h-px w-full bg-white/15 rounded-full" />
              {/* Dot */}
              <div
                className="absolute top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-white border-2 border-black shadow-md transition-all duration-700"
                style={{ left: dotLeft, transform: "translate(-50%, -50%)" }}
                aria-hidden="true"
              />
              {/* Labels below */}
              <div className="flex justify-between mt-3 text-[9px] font-medium text-gray-600 uppercase tracking-widest select-none">
                <span>Limited</span>
                <span>Moderate</span>
                <span>Broad</span>
              </div>
            </div>
          </div>

          {/* Right: metrics + note */}
          <div className="flex-1 space-y-5 text-sm text-gray-400">
            <div className="space-y-2">
              <MetricRow
                label="Active Sri Lankan IT roles"
                value={m?.total_sri_lankan_it_jobs ?? 0}
              />
              <MetricRow
                label="Sri Lankan jobs observed"
                value={m?.total_sri_lankan_jobs ?? 0}
              />
              <MetricRow
                label="Connected sources"
                value={m?.unique_sources ?? 0}
              />
            </div>

            <div className="border-t border-white/5 pt-4">
              <p className="text-xs text-gray-500 leading-relaxed italic">
                Coverage reflects the verified public employment sources
                currently connected to the platform. It does not represent the
                complete Sri Lankan IT labour market.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </section>
  );
}

function MetricRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-500 text-xs">{label}</span>
      <span className="text-white font-medium tabular-nums">{value}</span>
    </div>
  );
}
