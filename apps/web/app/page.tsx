import { api } from "@/lib/api";
import { CountUp } from "@/components/CountUp";
import { DataFreshnessTag } from "@/components/DataFreshnessTag";
import { RoleDistributionChart } from "@/components/RoleDistributionChart";
import { SourceRegistryTable } from "@/components/SourceRegistryTable";
import { JobsTable } from "@/components/JobsTable";

export const dynamic = "force-dynamic";

export default async function Home() {
  // All data fetched server-side — no mock fallbacks
  const [summary, roles, sources, jobs, quality] = await Promise.all([
    api.getJobsSummary(),
    api.getRoleDistribution(),
    api.getSources(),
    api.getJobs(25),
    api.getDataQuality(),
  ]);

  const hasData = (summary?.data_available) ?? false;

  return (
    <div className="py-10 space-y-16">
      {/* ── HERO ─────────────────────────────────────────────── */}
      <section aria-labelledby="hero-heading" className="fade-up">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold text-blue-400 tracking-[0.2em] uppercase mb-4">
            Sri Lanka · IT Workforce Intelligence
          </p>
          <h1
            id="hero-heading"
            className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white leading-[1.08]"
          >
            Where industry demand
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-violet-400">
              meets talent supply.
            </span>
          </h1>
          <p className="mt-6 text-base text-gray-400 max-w-xl leading-relaxed">
            Continuously refreshed intelligence on IT job vacancies, role demand,
            and talent pipelines in Sri Lanka — computed from real data, never hardcoded.
          </p>

          {/* Freshness indicator */}
          <div className="mt-6 flex items-center gap-3">
            <DataFreshnessTag
              lastIngestedAt={summary?.last_ingested_at ?? null}
              source="Greenhouse"
            />
            {!hasData && (
              <span className="text-xs text-gray-600">
                Run the pipeline to populate live data.
              </span>
            )}
          </div>
        </div>
      </section>

      {/* ── KPI CARDS ────────────────────────────────────────── */}
      <section aria-label="Key market metrics" id="market">
        <SectionLabel>Market Snapshot</SectionLabel>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
          <KpiCard
            label="Active Vacancies"
            sublabel="Greenhouse · Live"
            delay="fade-up-1"
          >
            {hasData ? (
              <CountUp value={summary!.active_jobs} className="text-4xl font-light text-white" />
            ) : (
              <EmptyValue />
            )}
          </KpiCard>

          <KpiCard
            label="Total Ingested"
            sublabel="All boards combined"
            delay="fade-up-2"
          >
            {hasData ? (
              <CountUp value={summary!.total_jobs} className="text-4xl font-light text-white" />
            ) : (
              <EmptyValue />
            )}
          </KpiCard>

          <KpiCard
            label="Sri Lankan Postings"
            sublabel="Location-verified"
            delay="fade-up-3"
          >
            {hasData ? (
              <>
                <CountUp value={summary!.sri_lankan_jobs} className="text-4xl font-light text-white" />
                {summary!.sri_lankan_jobs === 0 && (
                  <p className="text-[10px] text-yellow-500/70 mt-1">
                    Current boards: Canonical + GitLab — add LK-specific boards for local coverage
                  </p>
                )}
              </>
            ) : (
              <EmptyValue />
            )}
          </KpiCard>

          <KpiCard
            label="Data Quality Score"
            sublabel="Validation pass rate"
            delay="fade-up-4"
          >
            {quality?.data_available ? (
              <>
                <CountUp
                  value={100 - (quality.unclassified_rate ?? 0) / 2}
                  suffix="%"
                  className="text-4xl font-light text-white"
                />
                <p className="text-[10px] text-gray-600 mt-1">
                  {quality.unclassified_count} unclassified roles
                </p>
              </>
            ) : (
              <EmptyValue />
            )}
          </KpiCard>
        </div>
      </section>

      {/* ── ROLE DISTRIBUTION ────────────────────────────────── */}
      <section aria-labelledby="roles-heading" id="roles">
        <div className="flex items-center justify-between mb-6">
          <div>
            <SectionLabel>Role Category Distribution</SectionLabel>
            <p className="text-xs text-gray-500 mt-1">
              Active job counts classified by IT role taxonomy (deterministic keyword matching v1)
            </p>
          </div>
          {quality?.data_available && (
            <span className="text-[10px] text-gray-600 font-mono hidden md:block">
              {quality.unclassified_rate}% unclassified — will improve in Phase 1C NLP
            </span>
          )}
        </div>

        <div className="glass rounded-2xl p-6 card-glow transition-all duration-300">
          {roles && roles.length > 0 ? (
            <RoleDistributionChart data={roles} />
          ) : (
            <EmptySection message="No role data yet. Run the pipeline to populate." />
          )}
        </div>
      </section>

      {/* ── LIVE JOB LISTINGS ────────────────────────────────── */}
      <section aria-labelledby="jobs-heading">
        <div className="flex items-center justify-between mb-6">
          <div>
            <SectionLabel>Live Job Listings</SectionLabel>
            <p className="text-xs text-gray-500 mt-1">
              Most recent 25 records from Silver layer · Source provenance preserved
            </p>
          </div>
          {hasData && (
            <DataFreshnessTag lastIngestedAt={summary!.last_ingested_at} source="Greenhouse" />
          )}
        </div>

        <div className="glass rounded-2xl p-6 card-glow transition-all duration-300">
          {jobs && jobs.length > 0 ? (
            <JobsTable jobs={jobs} />
          ) : (
            <EmptySection message="No job records available. Run the pipeline first." />
          )}
        </div>
      </section>

      {/* ── DATA SOURCES ─────────────────────────────────────── */}
      <section aria-labelledby="sources-heading" id="sources">
        <SectionLabel>Data Source Registry</SectionLabel>
        <p className="text-xs text-gray-500 mt-1 mb-6">
          All registered sources with integration status. Restricted sources are never scraped.
        </p>

        <div className="glass rounded-2xl p-6 card-glow transition-all duration-300">
          {sources && sources.length > 0 ? (
            <SourceRegistryTable sources={sources} />
          ) : (
            <EmptySection message="Source registry unavailable." />
          )}
        </div>
      </section>

      {/* ── DATA QUALITY ─────────────────────────────────────── */}
      {quality?.data_available && (
        <section aria-labelledby="quality-heading">
          <SectionLabel>Data Quality Metrics</SectionLabel>
          <p className="text-xs text-gray-500 mt-1 mb-6">
            Computed from the current Silver layer — not estimated.
          </p>

          <div className="glass rounded-2xl p-6 card-glow">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <QualityMetric
                label="Total Records"
                value={quality.total_records?.toLocaleString() ?? "—"}
              />
              <QualityMetric
                label="Missing Country"
                value={`${quality.null_country_count?.toLocaleString()} (${quality.null_country_rate}%)`}
                warn={(quality.null_country_rate ?? 0) > 50}
              />
              <QualityMetric
                label="Unclassified Roles"
                value={`${quality.unclassified_count?.toLocaleString()} (${quality.unclassified_rate}%)`}
                warn={(quality.unclassified_rate ?? 0) > 60}
              />
              <QualityMetric
                label="Last Ingestion"
                value={
                  quality.last_ingested_at
                    ? new Date(quality.last_ingested_at).toLocaleString()
                    : "—"
                }
              />
            </div>
          </div>
        </section>
      )}

      {/* ── METHODOLOGY ──────────────────────────────────────── */}
      <section aria-labelledby="methodology-heading" id="methodology">
        <SectionLabel>Methodology</SectionLabel>
        <div className="glass rounded-2xl p-8 card-glow space-y-4 text-sm text-gray-400 leading-relaxed">
          <p>
            <strong className="text-white">Zero fake data.</strong> Every metric shown derives from
            actual ingested records. If data is unavailable, components show explicit empty states —
            never fabricated values.
          </p>
          <p>
            <strong className="text-white">Medallion architecture.</strong> Raw data is preserved in
            the Bronze layer as immutable Parquet files. Normalized records conforming to the
            canonical <code className="text-blue-400 text-xs">JobContract</code> schema are written to Silver.
            Gold analytical datasets will aggregate from Silver (Phase 1C).
          </p>
          <p>
            <strong className="text-white">IT classification.</strong> Phase 1B uses deterministic
            keyword matching against a 14-category role taxonomy. Phase 1C will introduce NLP-assisted
            classification using job descriptions, reducing the current unclassified rate.
          </p>
          <p>
            <strong className="text-white">Sri Lanka detection.</strong> Location matching uses
            deterministic keyword signals (city names, country name, ISO code). Records with
            insufficient evidence are not classified as Sri Lankan.
          </p>
          <p>
            <strong className="text-white">Source provenance.</strong> Every record retains its
            original source, source job ID, ingestion timestamp, and first/last-seen timestamps —
            enabling future vacancy lifecycle analytics.
          </p>
        </div>
      </section>
    </div>
  );
}

// ── Shared sub-components ──────────────────────────────────

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-[0.18em]">
      {children}
    </h2>
  );
}

function KpiCard({
  label,
  sublabel,
  children,
  delay = "",
}: {
  label: string;
  sublabel: string;
  children: React.ReactNode;
  delay?: string;
}) {
  return (
    <div className={`glass rounded-2xl p-5 card-glow transition-all duration-300 fade-up ${delay} flex flex-col gap-3`}>
      <div>
        <p className="text-xs font-medium text-gray-400 leading-tight">{label}</p>
        <p className="text-[10px] text-gray-600 mt-0.5">{sublabel}</p>
      </div>
      <div className="mt-auto">{children}</div>
    </div>
  );
}

function EmptyValue() {
  return (
    <span className="text-4xl font-light text-gray-700">—</span>
  );
}

function EmptySection({ message }: { message: string }) {
  return (
    <div className="py-12 text-center">
      <p className="text-gray-600 text-sm">{message}</p>
    </div>
  );
}

function QualityMetric({
  label,
  value,
  warn = false,
}: {
  label: string;
  value: string;
  warn?: boolean;
}) {
  return (
    <div>
      <p className="text-[10px] text-gray-600 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-sm font-medium ${warn ? "text-yellow-400" : "text-white"}`}>{value}</p>
    </div>
  );
}
