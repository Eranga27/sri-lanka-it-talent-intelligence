"use client";
import { useState } from "react";
import { SkillDemandEntry } from "@/lib/api";
import { Card, SectionLabel, EmptySection } from "../ui";

const CATEGORIES = [
  "All",
  "Programming",
  "Frontend",
  "Backend",
  "Data",
  "Cloud",
  "DevOps",
  "AI / ML",
  "Cybersecurity",
  "Analytics / BI",
] as const;

export function SkillDemand({ skills }: { skills: SkillDemandEntry[] | null }) {
  const [filter, setFilter] = useState<string>("All");

  if (!skills || skills.length === 0) {
    return (
      <section aria-label="Technology Demand" className="space-y-4">
        <SectionLabel>Technology Demand</SectionLabel>
        <Card>
          <EmptySection message="No skill demand data yet." />
        </Card>
      </section>
    );
  }

  const filtered =
    filter === "All"
      ? skills
      : skills.filter((s) => s.skill_category === filter);

  const maxCount = Math.max(...skills.map((s) => s.job_count), 1);

  return (
    <section aria-labelledby="skills-heading" id="skills" className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <SectionLabel>Technology Demand</SectionLabel>
          <p className="text-xs text-gray-600 mt-1">
            From job description analysis · regex_boundary_match
          </p>
        </div>
      </div>

      {/* Category filter chips */}
      <div
        className="flex flex-wrap gap-2"
        role="group"
        aria-label="Filter skills by category"
      >
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            aria-pressed={filter === cat}
            className={`px-3 py-1 rounded-full text-[10px] uppercase tracking-wider font-medium transition-colors duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
              filter === cat
                ? "bg-white text-black"
                : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-gray-200"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <Card className="overflow-x-auto">
        {filtered.length === 0 ? (
          <EmptySection
            message={`No skills observed for category: ${filter}`}
          />
        ) : (
          <div role="list" aria-label="Technology demand ranking">
            {/* Header row */}
            <div className="flex items-center text-[10px] font-semibold text-gray-600 uppercase tracking-wider pb-3 mb-3 border-b border-white/5 px-2">
              <div className="w-7">#</div>
              <div className="w-44 shrink-0">Technology</div>
              <div className="flex-1">Demand</div>
            </div>

            {filtered.map((s, i) => {
              const barPct = (s.job_count / maxCount) * 100;
              return (
                <div
                  key={s.skill_id}
                  role="listitem"
                  className="group flex items-center py-2 px-2 rounded-lg hover:bg-white/[0.025] transition-colors relative"
                >
                  {/* Rank */}
                  <div className="w-7 text-xs text-gray-600 tabular-nums">
                    {i + 1}
                  </div>

                  {/* Skill name + category */}
                  <div className="w-44 shrink-0">
                    <span className="text-sm font-medium text-gray-100">
                      {s.skill_name}
                    </span>
                    <span className="block text-[10px] text-gray-600">
                      {s.skill_category}
                    </span>
                  </div>

                  {/* Bar + count */}
                  <div className="flex-1 flex items-center gap-3">
                    <div
                      className="h-1.5 flex-1 max-w-[240px] bg-white/5 rounded-full overflow-hidden"
                      aria-label={`${s.skill_name}: ${s.job_count} jobs`}
                    >
                      <div
                        className="h-full bg-indigo-500 rounded-full bar-grow"
                        style={
                          {
                            "--bar-pct": `${barPct}%`,
                            animationDelay: `${i * 30}ms`,
                          } as React.CSSProperties
                        }
                      />
                    </div>
                    <span className="text-sm text-white tabular-nums w-6 text-right">
                      {s.job_count}
                    </span>
                    <span className="text-[11px] text-gray-500 tabular-nums w-10 text-right">
                      {(s.job_percentage ?? 0).toFixed(1)}%
                    </span>
                  </div>

                  {/* Hover tooltip */}
                  <div
                    role="tooltip"
                    className="pointer-events-none absolute left-1/2 -top-12 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-[#1c1c1e] border border-white/10 rounded-lg shadow-2xl p-2.5 z-20 whitespace-nowrap text-xs"
                  >
                    <p className="text-white font-medium">{s.skill_name}</p>
                    <p className="text-gray-400 mt-0.5">
                      {s.job_count} job{s.job_count !== 1 ? "s" : ""} ·{" "}
                      {(s.job_percentage ?? 0).toFixed(1)}% of active IT roles
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </section>
  );
}
